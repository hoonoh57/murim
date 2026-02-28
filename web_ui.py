import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from src.relay.relay_client import RelaySession
from src.relay.relay_automator import RelayAutomator
from src.api.ai_clients import GeminiFreeClient

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use a fixed key from .env for session persistence across restarts
app.secret_key = os.getenv("FLASK_SECRET_KEY", "murim_factory_stable_secret_dev_key")

# 세션별 RelaySession 저장 (메모리 + 파일)
sessions_store: dict = {}
SESSIONS_DIR = "sessions"

def save_session_to_file(sid: str, relay: RelaySession):
    """세션을 JSON 파일로 저장"""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)
    
    filepath = os.path.join(SESSIONS_DIR, f"{sid}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(relay.to_dict(), f, ensure_ascii=False, indent=2)

def load_all_sessions():
    """서버 시작 시 저장된 세션들을 메모리로 로드"""
    if not os.path.exists(SESSIONS_DIR):
        return
    
    # 오래된 세션 정리 (7일 초과)
    cleanup_old_sessions(days=7)
    
    count = 0
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            sid = filename[:-5]
            filepath = os.path.join(SESSIONS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions_store[sid] = RelaySession.from_dict(data)
                    count += 1
            except Exception as e:
                print(f"Error loading session {filename}: {e}")
    print(f"Loaded {count} sessions from disk.")

def cleanup_old_sessions(days: int = 7):
    """지정한 일수보다 오래된 세션 파일 삭제"""
    if not os.path.exists(SESSIONS_DIR):
        return
    
    import time
    now = time.time()
    cutoff = now - (days * 86400)
    
    removed = 0
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SESSIONS_DIR, filename)
            if os.path.getmtime(filepath) < cutoff:
                try:
                    os.remove(filepath)
                    removed += 1
                except Exception as e:
                    print(f"Failed to remove old session {filename}: {e}")
    
    if removed > 0:
        print(f"Cleaned up {removed} sessions older than {days} days.")

def get_session() -> RelaySession:
    sid = session.get("sid")
    if sid and sid in sessions_store:
        return sessions_store[sid]
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start_episode():
    """에피소드 제작 시작 → Round 1 배치 프롬프트 생성"""
    data = request.json
    topic = data.get("topic", "").strip()
    events = data.get("events", "").strip()
    
    if not topic:
        return jsonify({"error": "주제를 입력해 주세요."}), 400
    
    # 새 세션 생성
    sid = str(uuid.uuid4())
    session["sid"] = sid
    
    relay = RelaySession(topic=topic, events=events or "자동 생성")
    sessions_store[sid] = relay
    
    batch_text = relay.start_round1()
    save_session_to_file(sid, relay)
    
    return jsonify({
        "round": 1,
        "batch_prompt": batch_text,
        "messages": relay.messages
    })


@app.route("/api/submit_response", methods=["POST"])
def submit_response():
    """사용자가 Claude 응답을 붙여넣으면 파싱 후 다음 라운드 진행"""
    relay = get_session()
    sid = session.get("sid")
    if not relay:
        return jsonify({"error": "세션이 없습니다. 새로 시작해 주세요."}), 400
    
    data = request.json
    raw_response = data.get("response", "").strip()
    
    if not raw_response:
        return jsonify({"error": "응답을 입력해 주세요."}), 400
    
    current = relay.current_round
    response_data = {}
    
    if current == 1:
        # Round 1 응답 처리 → Round 2 프롬프트 생성
        result = relay.process_round1_response(raw_response)
        if not result["success"]:
            return jsonify({
                "error": result.get("error", "파싱 실패"),
                "messages": relay.messages,
                "hint": "JSON 형식이 포함된 응답인지 확인해 주세요."
            }), 422
        
        batch_text = relay.start_round2()
        response_data = {
            "round": 2,
            "batch_prompt": batch_text,
            "messages": relay.messages,
            "scenario_preview": relay.scenario_json
        }
    
    elif current == 2:
        # Round 2 응답 처리 → Round 3 프롬프트 생성
        result = relay.process_round2_response(raw_response)
        
        if result.get("killed"):
            response_data = {
                "round": -1,
                "status": "killed",
                "messages": relay.messages,
                "summary": relay.get_summary()
            }
        else:
            batch_text = relay.start_round3()
            response_data = {
                "round": 3,
                "batch_prompt": batch_text,
                "messages": relay.messages,
                "needs_rework": result.get("needs_rework", False),
                "council_result": relay.council_json
            }
    
    elif current == 3:
        # Round 3 응답 처리
        result = relay.process_round3_response(raw_response)
        
        if result.get("reworked"):
            # Rework 완료 → Round 2로 복귀
            batch_text = relay.start_round2()
            response_data = {
                "round": 2,
                "batch_prompt": batch_text,
                "messages": relay.messages,
                "reworked": True
            }
        else:
            # 제작 완료
            response_data = {
                "round": 99,
                "status": "completed",
                "messages": relay.messages,
                "summary": relay.get_summary()
            }
    
    if response_data:
        save_session_to_file(sid, relay)
        return jsonify(response_data)
        
    return jsonify({"error": "알 수 없는 상태"}), 400


@app.route("/api/force_go", methods=["POST"])
def force_go():
    """REWORK 판정이지만 강제로 GO 진행"""
    relay = get_session()
    sid = session.get("sid")
    if not relay:
        return jsonify({"error": "세션이 없습니다."}), 400
    
    batch_text = relay.start_round3(force_go=True)
    save_session_to_file(sid, relay)
    
    return jsonify({
        "round": 3,
        "batch_prompt": batch_text,
        "messages": relay.messages
    })


@app.route("/api/auto_run", methods=["POST"])
def auto_run():
    """Gemini API를 사용하여 전체 제작 과정 자동 수행"""
    topic = request.json.get("topic", "").strip()
    events = request.json.get("events", "").strip()
    
    if not topic:
        return jsonify({"error": "주제를 입력해 주세요."}), 400
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"error": "GOOGLE_API_KEY가 서버에 설정되어 있지 않습니다."}), 500
        
    # 세션 생성
    sid = str(uuid.uuid4())
    session["sid"] = sid
    relay = RelaySession(topic=topic, events=events or "자동 생성")
    sessions_store[sid] = relay
    
    # 자동화 실행
    client = GeminiFreeClient(api_key=api_key)
    automator = RelayAutomator(relay, client)
    
    try:
        summary = automator.run_all()
        save_session_to_file(sid, relay)
        return jsonify({
            "status": "completed",
            "messages": relay.messages,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": f"자동화 중 오류 발생: {str(e)}"}), 500


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """현재 세션 요약 정보"""
    relay = get_session()
    if not relay:
        return jsonify({"error": "세션이 없습니다."}), 400
    return jsonify(relay.get_summary())


@app.route("/api/download", methods=["GET"])
def download_result():
    """제작 결과 JSON 파일 다운로드"""
    from flask import Response
    from datetime import datetime
    
    relay = get_session()
    if not relay:
        return jsonify({"error": "세션이 없습니다."}), 400
    
    summary = relay.get_summary()
    filename = f"murim_episode_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    json_str = json.dumps(summary, ensure_ascii=False, indent=2)
    
    return Response(
        json_str,
        mimetype="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/json; charset=utf-8"
        }
    )


if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    load_all_sessions()
    
    print("\n" + "=" * 50)
    print("  MURIM AI FACTORY — Human Relay UI")
    print("  http://localhost:8080")
    print("=" * 50 + "\n")
    app.run(host="0.0.0.0", port=8080, debug=True)
