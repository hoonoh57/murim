import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from src.relay.relay_client import RelaySession

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use a fixed key from .env for session persistence across restarts
app.secret_key = os.getenv("FLASK_SECRET_KEY", "murim_factory_stable_secret_dev_key")

# 세션별 RelaySession 저장 (단순 구현: 메모리 저장)
sessions_store: dict = {}


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
    
    return jsonify({
        "round": 1,
        "batch_prompt": batch_text,
        "messages": relay.messages
    })


@app.route("/api/submit_response", methods=["POST"])
def submit_response():
    """사용자가 Claude 응답을 붙여넣으면 파싱 후 다음 라운드 진행"""
    relay = get_session()
    if not relay:
        return jsonify({"error": "세션이 없습니다. 새로 시작해 주세요."}), 400
    
    data = request.json
    raw_response = data.get("response", "").strip()
    
    if not raw_response:
        return jsonify({"error": "응답을 입력해 주세요."}), 400
    
    current = relay.current_round
    
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
        return jsonify({
            "round": 2,
            "batch_prompt": batch_text,
            "messages": relay.messages,
            "scenario_preview": relay.scenario_json
        })
    
    elif current == 2:
        # Round 2 응답 처리 → Round 3 프롬프트 생성
        result = relay.process_round2_response(raw_response)
        
        if result.get("killed"):
            return jsonify({
                "round": -1,
                "status": "killed",
                "messages": relay.messages,
                "summary": relay.get_summary()
            })
        
        batch_text = relay.start_round3()
        return jsonify({
            "round": 3,
            "batch_prompt": batch_text,
            "messages": relay.messages,
            "needs_rework": result.get("needs_rework", False),
            "council_result": relay.council_json
        })
    
    elif current == 3:
        # Round 3 응답 처리
        result = relay.process_round3_response(raw_response)
        
        if result.get("reworked"):
            # Rework 완료 → Round 2로 복귀
            batch_text = relay.start_round2()
            return jsonify({
                "round": 2,
                "batch_prompt": batch_text,
                "messages": relay.messages,
                "reworked": True
            })
        
        # 제작 완료
        return jsonify({
            "round": 99,
            "status": "completed",
            "messages": relay.messages,
            "summary": relay.get_summary()
        })
    
    return jsonify({"error": "알 수 없는 상태"}), 400


@app.route("/api/force_go", methods=["POST"])
def force_go():
    """REWORK 판정이지만 강제로 GO 진행"""
    relay = get_session()
    if not relay:
        return jsonify({"error": "세션이 없습니다."}), 400
    
    batch_text = relay.start_round3(force_go=True)
    return jsonify({
        "round": 3,
        "batch_prompt": batch_text,
        "messages": relay.messages
    })


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """현재 세션 요약 정보"""
    relay = get_session()
    if not relay:
        return jsonify({"error": "세션이 없습니다."}), 400
    return jsonify(relay.get_summary())


if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    print("\n" + "=" * 50)
    print("  MURIM AI FACTORY — Human Relay UI")
    print("  http://localhost:8080")
    print("=" * 50 + "\n")
    app.run(host="0.0.0.0", port=8080, debug=True)
