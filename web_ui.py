import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session, send_file
from dotenv import load_dotenv
from src.relay.relay_client import RelaySession
from src.relay.relay_automator import RelayAutomator
from src.api.ai_clients import GeminiFreeClient
from src.pipeline.image_manager import ImageManager
from src.pipeline.prompt_combiner import PromptCombiner

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use a fixed key from .env for session persistence across restarts
app.secret_key = os.getenv("FLASK_SECRET_KEY", "murim_factory_stable_secret_dev_key")

# 세션별 RelaySession 저장 (메모리 + 파일)
sessions_store: dict = {}
SESSIONS_DIR = "sessions"
OUTPUTS_DIR  = "outputs"   # ✅ [NEW] 구조화 출력 디렉토리


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
        result = relay.process_round3_response(raw_response)
        
        if result.get("reworked"):
            batch_text = relay.start_round2()
            response_data = {
                "round": 2,
                "batch_prompt": batch_text,
                "messages": relay.messages,
                "reworked": True
            }
        else:
            # ✅ [NEW] 파이프라인 완료 → outputs/ 폴더에 구조화 자동 저장
            output_dir = relay.save_to_outputs(OUTPUTS_DIR)
            response_data = {
                "round": 99,
                "status": "completed",
                "messages": relay.messages,
                "summary": relay.get_summary(),
                "output_dir": output_dir  # UI에 저장 경로 전달
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
        
    api_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY")
    if not api_keys:
        return jsonify({"error": "GOOGLE_API_KEY 또는 GOOGLE_API_KEYS가 서버에 설정되어 있지 않습니다."}), 500
        
    sid = str(uuid.uuid4())
    session["sid"] = sid
    relay = RelaySession(topic=topic, events=events or "자동 생성")
    sessions_store[sid] = relay
    
    client = GeminiFreeClient(api_keys=api_keys)
    automator = RelayAutomator(relay, client)
    
    try:
        summary = automator.run_all()
        # ✅ [NEW] 자동 제작 완료 → outputs/ 폴더에 구조화 자동 저장
        output_dir = relay.save_to_outputs(OUTPUTS_DIR)
        save_session_to_file(sid, relay)
        return jsonify({
            "status": "completed",
            "messages": relay.messages,
            "summary": relay.get_summary(),
            "output_dir": output_dir  # UI에 저장 경로 전달
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
    """
    제작 결과 JSON 파일 다운로드.
    outputs/ 폴더에 저장된 episode.json을 우선 서빙하고,
    없으면 메모리 요약을 동적으로 반환합니다.
    """
    from flask import Response
    from datetime import datetime as dt
    
    relay = get_session()
    if not relay:
        return jsonify({"error": "세션이 없습니다."}), 400
    
    # ✅ [NEW] outputs 폴더의 파일이 있으면 그것을 서빙
    if relay.output_dir and os.path.isfile(os.path.join(relay.output_dir, "episode.json")):
        return send_file(
            os.path.join(relay.output_dir, "episode.json"),
            mimetype="application/json",
            as_attachment=True,
            download_name=f"episode_{os.path.basename(relay.output_dir)}.json"
        )
    
    # Fallback: 메모리 요약 동적 직렬화
    summary = relay.get_summary()
    filename = f"murim_episode_{dt.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_str = json.dumps(summary, ensure_ascii=False, indent=2)
    
    return Response(
        json_str,
        mimetype="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/json; charset=utf-8"
        }
    )


# ✅ [NEW] outputs 디렉토리 에피소드 목록 API
@app.route("/api/outputs", methods=["GET"])
def list_outputs():
    """outputs/ 폴더에 저장된 에피소드 목록 반환"""
    if not os.path.exists(OUTPUTS_DIR):
        return jsonify({"episodes": []})
    
    episodes = []
    for dir_name in sorted(os.listdir(OUTPUTS_DIR), reverse=True):
        dir_path = os.path.join(OUTPUTS_DIR, dir_name)
        if not os.path.isdir(dir_path) or not dir_name.startswith("ep"):
            continue
        
        ep_info = {"dir": dir_name, "files": []}
        episode_file = os.path.join(dir_path, "episode.json")
        if os.path.isfile(episode_file):
            try:
                with open(episode_file, "r", encoding="utf-8") as f:
                    ep_data = json.load(f)
                ep_info["topic"] = ep_data.get("topic", "")
                ep_info["status"] = ep_data.get("status", "")
                title = (ep_data.get("scenario") or {}).get("title", "")
                ep_info["title"] = title
            except Exception:
                pass
        
        # 저장된 파일 목록
        for root, _, files in os.walk(dir_path):
            for fname in files:
                rel = os.path.relpath(os.path.join(root, fname), dir_path)
                ep_info["files"].append(rel)
        
        episodes.append(ep_info)
    
    return jsonify({"episodes": episodes})


# ✅ [NEW] outputs 에피소드 개별 파일 서빙 API
@app.route("/api/outputs/<ep_dir>/<path:filepath>", methods=["GET"])
def serve_output_file(ep_dir: str, filepath: str):
    """outputs/{ep_dir}/{filepath} 파일을 직접 서빙합니다."""
    # 경로 탈출 방지 (보안)
    safe_dir = os.path.basename(ep_dir)
    full_path = os.path.realpath(os.path.join(OUTPUTS_DIR, safe_dir, filepath))
    outputs_root = os.path.realpath(OUTPUTS_DIR)
    
    if not full_path.startswith(outputs_root):
        return jsonify({"error": "잘못된 경로"}), 400
    
    if not os.path.isfile(full_path):
        return jsonify({"error": "파일을 찾을 수 없습니다."}), 404
    
    return send_file(full_path, as_attachment=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Phase 4: 에셋 관리 API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route("/assets")
def assets_page():
    return render_template("assets.html")


def _find_episode_dir(ep_name):
    """에피소드 디렉토리를 여러 위치에서 탐색"""
    for base in [OUTPUTS_DIR, os.path.join(OUTPUTS_DIR, "episodes")]:
        path = os.path.join(base, ep_name)
        if os.path.isdir(path):
            return path
    return None


@app.route("/api/asset/episodes")
def asset_episodes():
    episodes = []
    for base in [OUTPUTS_DIR, os.path.join(OUTPUTS_DIR, "episodes")]:
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base), reverse=True):
            if d.startswith("ep") and os.path.isdir(os.path.join(base, d)):
                if d not in [e["dir"] for e in episodes]:
                    episodes.append({"dir": d, "path": os.path.join(base, d)})
    return jsonify({"episodes": episodes})


@app.route("/api/asset/manifest")
def asset_manifest():
    ep = request.args.get("ep", "")
    ep_dir = _find_episode_dir(ep)
    if not ep_dir:
        return jsonify({"error": "에피소드 없음"}), 404
    mgr = ImageManager(ep_dir)
    manifest = mgr.scan_images()
    return jsonify(manifest)


@app.route("/api/asset/coverage")
def asset_coverage():
    ep = request.args.get("ep", "")
    ep_dir = _find_episode_dir(ep)
    if not ep_dir:
        return jsonify({"error": "에피소드 없음"}), 404
    mgr = ImageManager(ep_dir)
    mgr.scan_images()
    return jsonify(mgr.get_coverage_report())


@app.route("/api/asset/image")
def asset_image():
    ep = request.args.get("ep", "")
    filename = request.args.get("file", "")
    ep_dir = _find_episode_dir(ep)
    if not ep_dir or not filename:
        return "Not found", 404
    filepath = os.path.join(ep_dir, "images", filename)
    if not os.path.isfile(filepath):
        return "Not found", 404
    return send_file(filepath)


@app.route("/api/asset/select", methods=["POST"])
def asset_select():
    data = request.json
    ep_dir = _find_episode_dir(data.get("ep", ""))
    if not ep_dir:
        return jsonify({"error": "에피소드 없음"}), 404
    mgr = ImageManager(ep_dir)
    mgr.scan_images()
    ok = mgr.select_image(data.get("scene_id", ""), data.get("file", ""))
    return jsonify({"success": ok})


@app.route("/api/asset/score", methods=["POST"])
def asset_score():
    data = request.json
    ep_dir = _find_episode_dir(data.get("ep", ""))
    if not ep_dir:
        return jsonify({"error": "에피소드 없음"}), 404
    mgr = ImageManager(ep_dir)
    mgr.scan_images()
    ok = mgr.set_quality_score(data.get("scene_id", ""), data.get("file", ""), data.get("score", 0), data.get("notes", ""))
    return jsonify({"success": ok})


@app.route("/api/asset/upload", methods=["POST"])
def asset_upload():
    ep = request.form.get("ep", "")
    ep_dir = _find_episode_dir(ep)
    if not ep_dir:
        return jsonify({"error": "에피소드 없음"}), 404
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "파일 없음"}), 400
    images_dir = os.path.join(ep_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    filepath = os.path.join(images_dir, f.filename)
    f.save(filepath)
    mgr = ImageManager(ep_dir)
    mgr.scan_images()
    return jsonify({"success": True, "file": f.filename})


@app.route("/api/asset/prompts")
def asset_prompts():
    ep = request.args.get("ep", "")
    ep_dir = _find_episode_dir(ep)
    if not ep_dir:
        return jsonify({"error": "에피소드 없음"}), 404
    combiner = PromptCombiner(ep_dir)
    return jsonify({
        "scenes": combiner.get_all_scenes(),
        "tools": combiner.get_available_tools(),
        "audio": combiner.audio_guide
    })


@app.route("/api/asset/test_sheet")
def asset_test_sheet():
    ep = request.args.get("ep", "")
    ep_dir = _find_episode_dir(ep)
    if not ep_dir:
        return jsonify({"error": "에피소드 없음"}), 404
    combiner = PromptCombiner(ep_dir)
    sheet = combiner.generate_test_sheet()
    return jsonify(sheet)


if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR,  exist_ok=True)  # ✅ [NEW] outputs 폴더 보장
    load_all_sessions()
    
    print("\n" + "=" * 50)
    print("  MURIM AI FACTORY — Human Relay UI")
    print("  http://localhost:8080")
    print("=" * 50 + "\n")
    app.run(host="0.0.0.0", port=8080, debug=True)
