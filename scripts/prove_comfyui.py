# -*- coding: utf-8 -*-
"""One-shot, real ComfyUI WAN 2.2 I2V proof. No scheduler, mocks, or cloud API."""
import argparse
import copy
import json
import math
import mimetypes
import os
from pathlib import Path
import struct
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import uuid
import zlib

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "workflows" / "wan22_5b_api.json"
DEFAULT_OUTPUT = ROOT / "outputs" / "p1_comfyui"
PROMPT = (
    "Cinematic wuxia scene in ancient East Asia: a lone martial artist in a "
    "dark robe stands before misty mountains. Wind moves his robe and pine "
    "branches. Gentle cinematic camera push forward, natural continuous motion."
)


QUALITY_PROMPT = (
    "One continuous cinematic shot of the exact same wuxia character shown in "
    "the reference image. Preserve the character's face, clothing, colors, "
    "composition, and original visual style. The character blinks naturally, "
    "breathes softly, and gently turns their head while a faint breeze moves "
    "the hair and fabric. Subtle believable movement, stable camera, clear "
    "facial structure, detailed textures; no cuts, no morphing or new people."
)


class ProofError(Exception):
    pass


def loopback_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1")
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise ProofError("[URL_DENIED] Only local http://127.0.0.1:8188 is allowed")
    try:
        if parsed.port is None:
            raise ProofError("[URL_DENIED] An explicit local port is required")
    except ValueError as exc:
        raise ProofError("[URL_DENIED] Invalid ComfyUI port") from exc
    return value.rstrip("/")


class LocalAPI:
    def __init__(self, base_url):
        self.base = loopback_url(base_url)

    def request(self, endpoint, data=None, content_type="application/json", timeout=20):
        if not endpoint.startswith("/") or endpoint.startswith("//"):
            raise ProofError("[API_PATH] Invalid API path")
        payload = None
        if data is not None:
            payload = data if isinstance(data, bytes) else json.dumps(data).encode("utf-8")
        req = Request(
            self.base + endpoint,
            data=payload,
            headers={"Content-Type": content_type} if payload is not None else {},
            method="POST" if payload is not None else "GET",
        )
        try:
            return urlopen(req, timeout=timeout)
        except HTTPError as exc:
            body = exc.read(2048).decode("utf-8", errors="replace")
            raise ProofError("[COMFY_HTTP] {} {} {}".format(
                exc.code, endpoint, body)) from exc
        except (URLError, OSError) as exc:
            raise ProofError("[COMFY_CONNECTION] {}: {}".format(endpoint, exc)) from exc

    def json(self, endpoint, data=None):
        with self.request(endpoint, data=data) as response:
            return json.load(response)

    def upload(self, image):
        image = Path(image)
        if image.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            raise ProofError("[IMAGE_TYPE] Use a PNG, JPG, or WebP image")
        if not image.is_file() or not 0 < image.stat().st_size <= 20 * 1024 * 1024:
            raise ProofError("[IMAGE_SIZE] Image must be nonempty and <=20 MiB")
        boundary = "murim" + uuid.uuid4().hex
        filename = ("murim_p1_" + uuid.uuid4().hex[:12] + image.suffix.lower())
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        body = (
            ("--{}\r\nContent-Disposition: form-data; name=\"image\"; "
             "filename=\"{}\"\r\nContent-Type: {}\r\n\r\n").format(
                boundary, filename, mime).encode("ascii")
            + image.read_bytes()
            + ("\r\n--{}--\r\n".format(boundary)).encode("ascii")
        )
        with self.request("/upload/image", data=body,
                          content_type="multipart/form-data; boundary=" + boundary,
                          timeout=60) as response:
            result = json.load(response)
        name = result.get("name")
        if not isinstance(name, str) or not name:
            raise ProofError("[UPLOAD_FAIL] ComfyUI did not return an image name")
        return name


def make_test_png(path):
    """Small locally generated test source, to avoid requiring user assets."""
    width, height = 512, 320
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # PNG filter None
        for x in range(width):
            ridge = 173 + int(22 * math.sin(x / 38.0) + 12 * math.cos(x / 71.0))
            if y < ridge:
                color = (max(0, 100 - y // 7), 125 - y // 8, 145 - y // 10)
            else:
                shade = min(65, 10 + (y - ridge) // 2)
                color = (shade, shade + 13, shade + 15)
            raw.extend(color)

    def chunk(name, data):
        return (struct.pack(">I", len(data)) + name + data
                + struct.pack(">I", zlib.crc32(name + data) & 0xffffffff))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + chunk(b"IEND", b""))
    with Path(path).open("xb") as output:
        output.write(png)


def quality_resolution(image_path):
    """Choose a portrait/landscape resolution for an 8-GB-class GPU.

    Quality mode requires a genuine PNG so an incorrectly named JPEG is not
    silently uploaded with PNG MIME type and the aspect ratio is reliable.
    No image conversion, overwriting, or Pillow dependency is needed.
    """
    image_path = Path(image_path)
    if image_path.suffix.lower() != ".png":
        raise ProofError("[QUALITY_IMAGE] Provide a genuine PNG reference image")
    with image_path.open("rb") as stream:
        header = stream.read(24)
    if (len(header) != 24 or not header.startswith(b"\x89PNG\r\n\x1a\n")
            or header[12:16] != b"IHDR"):
        raise ProofError("[QUALITY_IMAGE] File is not a genuine PNG (possibly JPEG with .png extension)")
    width, height = struct.unpack(">II", header[16:24])
    if not (64 <= width <= 16384 and 64 <= height <= 16384):
        raise ProofError("[QUALITY_IMAGE] Invalid PNG dimensions")
    return (576, 768) if height > width else (832, 480)


def load_workflow():
    try:
        workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ProofError("[WORKFLOW_INVALID] Cannot load WAN API JSON: {}".format(exc)) from exc
    required = {
        "3": "KSampler",
        "6": "CLIPTextEncode",
        "7": "CLIPTextEncode",
        "37": "UNETLoader",
        "38": "CLIPLoader",
        "39": "VAELoader",
        "55": "Wan22ImageToVideoLatent",
        "56": "LoadImage",
        "57": "CreateVideo",
        "58": "SaveVideo",
    }
    for node_id, class_name in required.items():
        if workflow.get(node_id, {}).get("class_type") != class_name:
            raise ProofError("[WORKFLOW_INVALID] Node {} must be {}".format(node_id, class_name))
    return workflow


def preflight(api, workflow):
    stats = api.json("/system_stats")
    if not isinstance(stats, dict):
        raise ProofError("[SERVER_INVALID] /system_stats returned an invalid response")
    info = api.json("/object_info")
    if not isinstance(info, dict):
        raise ProofError("[SERVER_INVALID] /object_info returned an invalid response")
    missing_nodes = sorted({
        node["class_type"] for node in workflow.values()
        if node["class_type"] not in info
    })
    if missing_nodes:
        raise ProofError("[NODE_MISSING] {}".format(", ".join(missing_nodes)))
    missing_models = []
    for node_id, field in (("37", "unet_name"), ("38", "clip_name"), ("39", "vae_name")):
        node = workflow[node_id]
        filename = node["inputs"][field]
        definition = info[node["class_type"]]["input"]["required"][field]
        choices = definition[0] if isinstance(definition, list) and definition else None
        if isinstance(choices, list) and filename not in choices:
            missing_models.append("{}: {}".format(node["class_type"], filename))
    if missing_models:
        raise ProofError("[MODEL_MISSING] {}".format("; ".join(missing_models)))
    return stats


def build_workflow(template, image_name, steps=8, frames=17,
                   width=512, height=320, prompt=PROMPT, label="proof"):
    if frames < 5 or frames > 41 or (frames - 1) % 4:
        raise ProofError("[FRAMES] Use 5..41 frames in increments of 4")
    if not 1 <= steps <= 30:
        raise ProofError("[STEPS] Use 1..30 sampling steps")
    if (width % 32 or height % 32 or not 256 <= width <= 1024
            or not 256 <= height <= 1024):
        raise ProofError("[RESOLUTION] Dimensions must be multiples of 32 within 256..1024")
    if label not in ("proof", "quality"):
        raise ProofError("[OUTPUT_LABEL] Invalid output label")
    workflow = copy.deepcopy(template)
    workflow["56"]["inputs"]["image"] = image_name
    workflow["6"]["inputs"]["text"] = prompt
    workflow["3"]["inputs"]["seed"] = 20261121
    workflow["3"]["inputs"]["steps"] = steps
    workflow["55"]["inputs"]["width"] = width
    workflow["55"]["inputs"]["height"] = height
    workflow["55"]["inputs"]["length"] = frames
    workflow["58"]["inputs"]["filename_prefix"] = ("murim_p1/" + label + "_"
                                                   + uuid.uuid4().hex[:12])
    return workflow


def locate_video(history):
    outputs = history.get("outputs", {})
    if not isinstance(outputs, dict):
        return None
    ordered = ([outputs["58"]] if "58" in outputs else []) + [
        value for key, value in outputs.items() if key != "58"
    ]
    for output in ordered:
        if not isinstance(output, dict):
            continue
        for part in (output, output.get("ui", {})):
            if not isinstance(part, dict):
                continue
            for key in ("videos", "gifs", "images", "files"):
                items = part.get(key, [])
                if not isinstance(items, list):
                    continue
                for entry in items:
                    if (isinstance(entry, dict)
                            and str(entry.get("filename", "")).lower().endswith(
                                (".mp4", ".webm", ".mov"))):
                        return entry
    return None


def await_video(api, prompt_id, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        history = api.json("/history/" + prompt_id)
        record = history.get(prompt_id) if isinstance(history, dict) else None
        if isinstance(record, dict):
            status = record.get("status", {})
            if isinstance(status, dict) and (status.get("status_str") == "error"
                                              or status.get("completed") is False):
                raise ProofError("[RENDER_FAIL] ComfyUI history reports an execution error: {}".format(
                    str(status.get("messages", []))[:1000]))
            video = locate_video(record)
            if video:
                return video
            raise ProofError("[OUTPUT_MISSING] Prompt finished but no video output was recorded")
        time.sleep(3)
    raise ProofError("[RENDER_TIMEOUT] Queued prompt may still be running in ComfyUI; "
                     "inspect its queue/history before retrying")


def save_video(api, entry, output_dir):
    name = entry["filename"]
    if not isinstance(name, str) or not name or "/" in name or "\\" in name:
        raise ProofError("[OUTPUT_PATH] Invalid returned filename")
    subfolder = entry.get("subfolder", "")
    kind = entry.get("type", "output")
    if not isinstance(subfolder, str) or ".." in subfolder.replace("\\", "/").split("/"):
        raise ProofError("[OUTPUT_PATH] Invalid returned subfolder")
    if kind != "output":
        raise ProofError("[OUTPUT_PATH] Only permanent ComfyUI outputs are accepted")
    query = urlencode({"filename": name, "subfolder": subfolder, "type": "output"})
    destination = Path(output_dir) / ("p1_" + uuid.uuid4().hex[:12] + "_" + name)
    # Exclusive creation; never overwrite or remove pre-existing local files.
    created = False
    try:
        with destination.open("xb") as out:
            created = True
            with api.request("/view?" + query, timeout=120) as response:
                total = 0
                while True:
                    piece = response.read(1024 * 1024)
                    if not piece:
                        break
                    total += len(piece)
                    if total > 250 * 1024 * 1024:
                        raise ProofError("[OUTPUT_SIZE] Video exceeds 250 MiB safety limit")
                    out.write(piece)
        with destination.open("rb") as f:
            header = f.read(16)
        valid_mp4 = len(header) >= 12 and header[4:8] == b"ftyp"
        valid_webm = header.startswith(b"\x1a\x45\xdf\xa3")
        if not ((name.lower().endswith((".mp4", ".mov")) and valid_mp4)
                or (name.lower().endswith(".webm") and valid_webm)):
            raise ProofError("[OUTPUT_INVALID] Downloaded data is not an MP4/MOV/WebM video")
        return destination
    except Exception:
        # Cleanup is limited to this invocation's newly created file.
        if created and destination.exists():
            destination.unlink()
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description="One-time ComfyUI WAN 2.2 real video proof")
    parser.add_argument("--url", default="http://127.0.0.1:8188")
    parser.add_argument("--image", help="Optional local PNG/JPG/WebP reference image")
    parser.add_argument("--timeout", type=int, default=900, help="Wait up to N seconds for render")
    parser.add_argument("--probe-only", action="store_true", help="Check models and nodes, do not queue")
    parser.add_argument("--quality", action="store_true", help="Real PNG reference, 20+ steps and 8-GB-friendly video")
    args = parser.parse_args(argv)
    if not 10 <= args.timeout <= 3600:
        raise ProofError("[TIMEOUT] Use 10..3600 seconds")
    if args.quality and not args.image:
        raise ProofError("[QUALITY_REFERENCE_REQUIRED] Use --quality --image PATH_TO_REAL_PNG")
    workflow = load_workflow()
    api = LocalAPI(args.url)
    preflight(api, workflow)
    if args.probe_only:
        print("[PASS] ComfyUI WAN 2.2 nodes and models ready; no render queued")
        return 0
    output_dir = DEFAULT_OUTPUT
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.image:
        image_path = Path(args.image).resolve(strict=True)
    else:
        image_path = output_dir / ("source_" + uuid.uuid4().hex[:12] + ".png")
        make_test_png(image_path)
    dimensions = quality_resolution(image_path) if args.quality else None
    image_name = api.upload(image_path)
    if args.quality:
        prompt = build_workflow(
            workflow, image_name, steps=24, frames=33,
            width=dimensions[0], height=dimensions[1],
            prompt=QUALITY_PROMPT, label="quality")
    else:
        print("[SMOKE_ONLY] Synthetic landscape proves the pipeline, NOT image quality")
        prompt = build_workflow(workflow, image_name)
    response = api.json("/prompt", {"prompt": prompt, "client_id": uuid.uuid4().hex})
    prompt_id = response.get("prompt_id", "") if isinstance(response, dict) else ""
    if not isinstance(prompt_id, str) or not prompt_id:
        raise ProofError("[QUEUE_FAIL] ComfyUI did not return prompt_id: {}".format(str(response)[:500]))
    print("[RUNNING] ComfyUI queued one WAN 2.2 scene: " + prompt_id, flush=True)
    entry = await_video(api, prompt_id, args.timeout)
    video = save_video(api, entry, output_dir)
    print("[PASS] Real ComfyUI video downloaded: {} ({} bytes)".format(
        video, video.stat().st_size))
    if args.quality:
        print("[REVIEW_REQUIRED] File creation verified; visual quality needs human review")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ProofError, OSError, ValueError, KeyError) as error:
        print("[FAIL] {}".format(error), file=sys.stderr)
        sys.exit(1)
