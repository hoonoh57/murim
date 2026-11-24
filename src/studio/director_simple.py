"""GPT-style Murim director UI: human-relayed images, immutable storyboard decisions.

This is a facade over the established editorial and M-VML engines. It never
weakens G1/G2 approval and never reports a generated video without media.
"""
import json
import os
import re
import secrets
import uuid
from pathlib import Path

from flask import Blueprint, abort, jsonify, render_template, request

from .editorial import Editorial
from .web import TOKEN, store, JOB_LOCK
from .workspace import LOCK, MAX_FILE, assets, get_scene, hash_bytes, patch, safe, state, track

BP = Blueprint("director_simple", __name__, url_prefix="/studio/simple")
ROLES = {"character", "style", "prop", "location", "scene"}
META_RE = re.compile(r"^(\d{8})-([a-f0-9]{64})\.json$")


@BP.before_request
def local_only():
    if request.remote_addr not in ("127.0.0.1", "::1") or request.host.split(":")[0] not in ("localhost", "127.0.0.1"):
        abort(403)
    if request.method != "GET":
        if not secrets.compare_digest(request.headers.get("X-Murim-Studio", ""), TOKEN):
            abort(403)
        if request.content_length is None or request.content_length > MAX_FILE + 65536:
            abort(413)


@BP.errorhandler(ValueError)
@BP.errorhandler(OSError)
@BP.errorhandler(RuntimeError)
@BP.errorhandler(KeyError)
@BP.errorhandler(TypeError)
def error(exc):
    return jsonify(error=str(exc)[:1000]), 400


def payload():
    obj = request.get_json(silent=True)
    if not isinstance(obj, dict):
        raise ValueError("JSON object required")
    return obj


def default_book():
    return {"archived": False, "candidates": [], "selected": {}, "confirmed": False,
            "editorial_revision": "", "confirmed_by": "", "vml_revision": ""}


def read_book(pid):
    folder = store.folder(pid)
    base = folder / "director"
    if not base.exists():
        return default_book(), "", 0
    base = safe(folder, "director", directory=True)
    files = sorted((p for p in base.iterdir() if META_RE.fullmatch(p.name) and p.is_file() and not p.is_symlink()))
    if not files:
        return default_book(), "", 0
    for i, p in enumerate(files, 1):
        match = META_RE.fullmatch(p.name)
        if int(match.group(1)) != i:
            raise ValueError("Director revision sequence corrupted")
    last = files[-1]
    raw = safe(base, last.name).read_bytes()
    sha = hash_bytes(raw)
    if len(raw) > 1_000_000 or sha != META_RE.fullmatch(last.name).group(2):
        raise ValueError("Director revision integrity error")
    doc = json.loads(raw)
    if not isinstance(doc, dict) or set(doc) != set(default_book()):
        raise ValueError("Director state schema mismatch")
    return doc, sha, len(files)


def save_book(pid, book, expected):
    old, head, index = read_book(pid)
    if expected != head:
        raise ValueError("Director state revision conflict; reload project")
    if set(book) != set(default_book()) or not isinstance(book["candidates"], list) or not isinstance(book["selected"], dict):
        raise ValueError("Invalid Director state")
    raw = json.dumps(book, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > 1_000_000:
        raise ValueError("Director state too large")
    sha = hash_bytes(raw)
    if sha == head:
        return head
    base = safe(store.folder(pid), "director", directory=True, create=True)
    path = base / ("%08d-%s.json" % (index + 1, sha))
    tmp = base / ("pending-" + uuid.uuid4().hex)
    with tmp.open("xb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    tmp.rename(path)
    return sha


def available(pid):
    d, revision = store.load(pid)
    book, token, _ = read_book(pid)
    editorial = Editorial(store, pid).view()
    signature_ok = editorial["approved"]
    ready = bool(
        signature_ok and book["confirmed"] and
        book["editorial_revision"] == editorial["latest"]["revision"]
    )
    if ready:
        aa = assets(d)
        for scene in editorial["latest"]["plan"]["scenes"]:
            cid = book["selected"].get("scene:" + scene["id"])
            candidate = next((x for x in book["candidates"] if x["id"] == cid), None)
            ref = track(get_scene(d, scene["id"]), "image")
            if not candidate or candidate["asset"] not in aa or ref is None or ref.get("asset") != candidate["asset"]:
                ready = False
                break
    return d, revision, book, token, editorial, ready


def require_editorial(pid, doc, book, editorial):
    if book["archived"]:
        raise ValueError("Archived projects are read-only; restore first")
    Editorial(store, pid).require(doc)
    if book["editorial_revision"] and book["editorial_revision"] != editorial["latest"]["revision"]:
        raise ValueError("Scenario approval changed. Reset storyboard selections for the newly approved plan")


def validate_slot(role, scene, editorial):
    if role not in ROLES:
        raise ValueError("Unknown asset role")
    if role == "scene":
        valid = {x["id"] for x in editorial["latest"]["plan"]["scenes"]}
        if scene not in valid:
            raise ValueError("Select a scenario scene")
        return "scene:" + scene
    if scene not in (None, ""):
        raise ValueError("Global asset role cannot carry a scene")
    return role


@BP.get("/")
def index():
    return render_template("director_simple.html", studio_token=TOKEN)


@BP.get("/api/projects")
def projects():
    result = []
    for p in store.list_projects():
        book, _, _ = read_book(p["id"])
        result.append(dict(p, archived=book["archived"]))
    return jsonify(projects=result)


@BP.post("/api/projects")
def create():
    x = payload()
    title = str(x.get("title", "")).strip()
    if not 1 <= len(title) <= 120:
        raise ValueError("Enter a project title (1–120 characters)")
    with LOCK:
        pid = store.create(title)
        return jsonify(store.describe(pid)), 201


@BP.get("/api/project/<pid>")
def view(pid):
    with LOCK:
        d, revision, book, token, editorial, ready = available(pid)
        overview = store.describe(pid)
        return jsonify(project=overview, director=book, director_token=token,
                       editorial={"approved": editorial["approved"], "status": editorial["status"],
                                  "plan_revision": editorial["latest"]["revision"],
                                  "scenes": editorial["latest"]["plan"]["scenes"],
                                  "issues": editorial["issues"][:30]},
                       storyboard_ready=ready)


@BP.post("/api/project/<pid>/project-action")
def project_action(pid):
    x = payload()
    action = x.get("action")
    with LOCK:
        d, revision, book, token, _, _ = available(pid)
        if x.get("director_token") != token:
            raise ValueError("Director revision conflict")
        if action == "rename":
            if book["archived"]:
                raise ValueError("Restore before editing")
            title = str(x.get("title", "")).strip()
            if not 1 <= len(title) <= 120:
                raise ValueError("Invalid project title")
            if x.get("revision") != revision:
                raise ValueError("M-VML revision conflict")
            d.set("title", title)
            store.save(pid, d, revision)
        elif action in ("archive", "restore"):
            book = dict(book, archived=action == "archive")
            save_book(pid, book, token)
        else:
            raise ValueError("Unknown project operation")
        return jsonify(ok=True)


@BP.get("/api/project/<pid>/relay")
def relay(pid):
    d, _, book, _, editorial, ready = available(pid)
    mode = request.args.get("mode", "storyboard")
    plan = editorial["latest"]["plan"]
    if mode == "scenario":
        text = ("당신은 Murim Studio의 시나리오 작가입니다. 다음 기획을 바탕으로 사람이 감수할 완결된 작품 원문을 작성하세요. "
                "이 대화의 승인 절차를 외부 심사나 실제 제작 PASS로 주장하지 마세요. "
                "장면마다 사건, 인간의 선택, 공간, 소품, 시각적 새 발견과 검술 물리동작을 명시하세요.\n\n")
        text += json.dumps({"project": d.get("title"), "current_plan": plan}, ensure_ascii=False, indent=2)
    elif mode == "storyboard":
        require_editorial(pid, d, book, editorial)
        text = ("승인된 시나리오를 절대 변경하지 말고 GPT 이미지 생성 모델로 캐릭터, 화풍, 소품, 장소와 "
                "각 장면 스토리보드의 후보 이미지를 제작하세요. 얼굴/의상/검/공간의 일관성을 유지하세요. "
                "이미지에는 자막과 텍스트를 넣지 마세요. 사용자가 후보를 선택하기 전에는 어떠한 영상도 제작하지 마세요.\n\n")
        text += json.dumps({"approved_revision": editorial["latest"]["revision"], "scenes": plan["scenes"]}, ensure_ascii=False, indent=2)
    elif mode == "motion":
        if not ready:
            raise ValueError("Storyboard must be confirmed first")
        sid = request.args.get("scene", "")
        shot = next((s for s in plan["scenes"] if s["id"] == sid), None)
        if not shot:
            raise ValueError("Unknown scene")
        aa = assets(d)
        cid = book["selected"]["scene:" + sid]
        item = next(c for c in book["candidates"] if c["id"] == cid)
        text = ("청명의 확정된 캐릭터·소품·장소 이미지와 선택된 장면 스토리보드를 기준으로 "
                "8초 내외 무협 동작의 시작-중간1..N-종료 키프레임을 설계하세요. "
                "모든 키프레임에서 얼굴·복장·검의 손잡이/칼날/그립을 유지하세요. "
                "실제로 실행되지 않은 AI 이미지나 영상을 생성했다고 말하지 마세요.\n\n")
        text += json.dumps({"scene": shot, "approved_image": {"asset": item["asset"], "label": aa[item["asset"]].get("label")},
                            "fps": 24, "mode": "HUMAN_RELAY_UNVALIDATED"}, ensure_ascii=False, indent=2)
    else:
        raise ValueError("Unknown relay mode")
    return jsonify(prompt=text)


@BP.post("/api/project/<pid>/candidate")
def candidate(pid):
    x = payload()
    with LOCK:
        d, _, book, token, editorial, _ = available(pid)
        require_editorial(pid, d, book, editorial)
        if x.get("director_token") != token:
            raise ValueError("Director revision conflict")
        slot = validate_slot(x.get("role"), x.get("scene"), editorial)
        aid = x.get("asset")
        obj = assets(d).get(aid)
        if obj is None or obj.get("kind") != "image":
            raise ValueError("Registered image asset required")
        entry = {"id": uuid.uuid4().hex[:12], "asset": aid, "slot": slot,
                 "label": str(x.get("label", ""))[:160]}
        copy = dict(book, candidates=list(book["candidates"]) + [entry],
                    confirmed=False, confirmed_by="", vml_revision="",
                    editorial_revision=editorial["latest"]["revision"])
        new_token = save_book(pid, copy, token)
        return jsonify(candidate=entry, director_token=new_token)


@BP.post("/api/project/<pid>/select")
def select(pid):
    x = payload()
    with LOCK:
        d, _, book, token, editorial, _ = available(pid)
        require_editorial(pid, d, book, editorial)
        if x.get("director_token") != token:
            raise ValueError("Director revision conflict")
        cid = x.get("candidate")
        entry = next((c for c in book["candidates"] if c["id"] == cid), None)
        if entry is None:
            raise ValueError("Unknown candidate")
        selection = dict(book["selected"])
        selection[entry["slot"]] = cid
        copy = dict(book, selected=selection, confirmed=False, confirmed_by="", vml_revision="")
        new_token = save_book(pid, copy, token)
        return jsonify(director_token=new_token)


@BP.post("/api/project/<pid>/confirm")
def confirm(pid):
    x = payload()
    if not JOB_LOCK.acquire(False):
        raise ValueError("Production job is running")
    try:
        with LOCK:
            d, revision, book, token, editorial, ready = available(pid)
            require_editorial(pid, d, book, editorial)
            if x.get("director_token") != token or x.get("revision") != revision:
                raise ValueError("Revision conflict")
            if x.get("confirmed") is not True or not str(x.get("approver", "")).strip():
                raise ValueError("Human storyboard selection and approval required")
            required = ["character", "style"] + ["scene:" + s["id"] for s in editorial["latest"]["plan"]["scenes"]]
            if any(not book["selected"].get(slot) for slot in required):
                raise ValueError("Select character, style and one storyboard image for every scene")
            candidates = {c["id"]: c for c in book["candidates"]}
            aa = assets(d)
            ops = []
            for s in editorial["latest"]["plan"]["scenes"]:
                slot = "scene:" + s["id"]
                c = candidates.get(book["selected"][slot])
                if c is None or c["slot"] != slot or c["asset"] not in aa:
                    raise ValueError("Selected storyboard image missing")
                ops.append({"op": "set", "scene": s["id"], "track": "image",
                            "values": {"asset": c["asset"]}})
            for slot in ("character", "style"):
                c = candidates.get(book["selected"][slot])
                if c is None or c["slot"] != slot or c["asset"] not in aa:
                    raise ValueError("Selected master image missing")
            if len(ops) > 30:
                raise ValueError("Split storyboard confirmation into supported scene batches")
            edited, dirty = patch(d, ops)
            Editorial(store, pid).require(edited)
            new_revision = store.save(pid, edited, revision)
            copy = dict(book, confirmed=True, confirmed_by=str(x["approver"]).strip()[:200],
                        vml_revision=new_revision)
            new_token = save_book(pid, copy, token)
            return jsonify(confirmed=True, vml_revision=new_revision,
                           director_token=new_token, dirty=dirty)
    finally:
        JOB_LOCK.release()


@BP.get("/api/project/<pid>/production")
def production(pid):
    d, revision, book, token, editorial, ready = available(pid)
    if not ready:
        raise ValueError("Scenario and storyboard must be approved before production")
    aa = assets(d)
    rows = []
    for scene in editorial["latest"]["plan"]["scenes"]:
        cid = book["selected"]["scene:" + scene["id"]]
        c = next(x for x in book["candidates"] if x["id"] == cid)
        t = track(get_scene(d, scene["id"]), "video")
        rows.append({"id": scene["id"], "title": scene["title"], "seconds": scene["frames"] / 24,
                     "reference_asset": c["asset"], "label": aa[c["asset"]].get("label"),
                     "video_asset": t.get("asset", "") if t is not None else "",
                     "status": "CANDIDATE_REQUIRES_VIEWING" if t is not None and t.get("asset") else "HUMAN_RELAY_REQUIRED"})
    return jsonify(state="HUMAN_RELAY_UNTIL_WORKFLOW_VALIDATED", vml_revision=revision, shots=rows)


@BP.post("/api/project/<pid>/attach-video")
def attach_video(pid):
    x = payload()
    if not JOB_LOCK.acquire(False):
        raise ValueError("Production job running")
    try:
        with LOCK:
            d, revision, book, token, editorial, ready = available(pid)
            if not ready:
                raise ValueError("Storyboard no longer approved")
            if x.get("revision") != revision:
                raise ValueError("M-VML revision conflict")
            sid = x.get("scene")
            get_scene(d, sid)
            aid = x.get("asset")
            a = assets(d).get(aid)
            if a is None or a.get("kind") != "video":
                raise ValueError("Registered real video asset required")
            updated, dirty = patch(d, [{"op": "set", "scene": sid, "track": "video",
                                         "values": {"asset": aid}}])
            Editorial(store, pid).require(updated)
            rev = store.save(pid, updated, revision)
            return jsonify(revision=rev, dirty=dirty, status="CANDIDATE_REQUIRES_VIEWING")
    finally:
        JOB_LOCK.release()
