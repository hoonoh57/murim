# -*- coding: utf-8 -*-
import json, os, subprocess, asyncio, re, glob, sys

def find_episode():
    eps = [d for d in os.listdir("outputs") if d.startswith("ep")]
    return os.path.join("outputs", eps[0]) if eps else None

EPISODE_DIR = find_episode()
if not EPISODE_DIR:
    print("No episode found!")
    sys.exit(1)

OUTPUT_FILE = os.path.join(EPISODE_DIR, "final_video.mp4")
TEMP_DIR = os.path.join(EPISODE_DIR, "temp_render")
os.makedirs(TEMP_DIR, exist_ok=True)
WIDTH, HEIGHT, FPS = 1920, 1080, 30
VOICE = "ko-KR-InJoonNeural"

print("=" * 60)
print("  MURIM AI FACTORY - Episode Renderer")
print("  Episode:", EPISODE_DIR)
print("=" * 60)
sys.stdout.flush()

print("\n[Phase 1] Parsing scenario...")
with open(os.path.join(EPISODE_DIR, "scenario.json"), "r", encoding="utf-8") as fp:
    data = json.load(fp)

scenes = data.get("scenes", [])
script = data.get("script", "")
print("  Title:", data.get("title", ""))
print("  Scenes:", len(scenes))
sys.stdout.flush()

blocks = [b.strip() for b in script.strip().split("\n\n") if b.strip()]
chunk = max(1, len(blocks) // max(1, len(scenes)))

scene_data = []
for i, sc in enumerate(scenes):
    sid = sc.get("id", "S{:02d}".format(i + 1))
    start = i * chunk
    end = start + chunk if i < len(scenes) - 1 else len(blocks)
    text = " ".join(blocks[start:end])
    tr = sc.get("time_range", "0:00-0:10")
    parts = tr.split("-")
    try:
        p0 = parts[0].strip().split(":")
        p1 = parts[1].strip().split(":")
        dur = max(5, min((int(p1[0]) * 60 + int(p1[1])) - (int(p0[0]) * 60 + int(p0[1])), 45))
    except Exception:
        dur = 10
    scene_data.append({"sid": sid, "text": text[:400], "dur": dur, "desc": sc.get("description", "")[:50]})

for s in scene_data:
    print("  {}: {}... ({}s)".format(s["sid"], s["desc"], s["dur"]))
sys.stdout.flush()

print("\n[Phase 2] Generating TTS narration...")
sys.stdout.flush()

async def gen_tts():
    import edge_tts
    for s in scene_data:
        out = os.path.join(TEMP_DIR, "{}_narration.mp3".format(s["sid"]))
        if os.path.exists(out):
            print("  [TTS] {} exists, skip".format(s["sid"]))
            continue
        txt = s["text"] if s["text"].strip() else "..."
        print("  [TTS] {}: {}...".format(s["sid"], txt[:40]))
        sys.stdout.flush()
        c = edge_tts.Communicate(txt, VOICE)
        await c.save(out)
        print("  [TTS] {} done".format(s["sid"]))
        sys.stdout.flush()

asyncio.run(gen_tts())

print("\n[Phase 3] Creating Ken Burns video clips...")
sys.stdout.flush()

def get_dur(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path], capture_output=True)
    out = r.stdout.decode("utf-8", errors="ignore")
    try:
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return 10.0


imgs_dir = os.path.join(EPISODE_DIR, "images")
for idx, s in enumerate(scene_data):
    sid = s["sid"]
    clip = os.path.join(TEMP_DIR, "{}_clip.mp4".format(sid))
    if os.path.exists(clip):
        print("  [Video] {} exists, skip".format(sid))
        continue
    matches = glob.glob(os.path.join(imgs_dir, "{}_*".format(sid)))
    if not matches:
        print("  [Video] {} no image!".format(sid))
        continue
    narr = os.path.join(TEMP_DIR, "{}_narration.mp3".format(sid))
    dur = get_dur(narr) + 1.0 if os.path.exists(narr) else s["dur"]
    dur = max(5, min(dur, 45))
    d = int(dur * FPS)
    zooms = [
        "zoompan=z='min(zoom+0.001,1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={}:s={}x{}:fps={}".format(d, WIDTH, HEIGHT, FPS),
        "zoompan=z='min(zoom+0.0008,1.3)':x='if(eq(on,1),0,x+1.5)':y='ih/4':d={}:s={}x{}:fps={}".format(d, WIDTH, HEIGHT, FPS),
        "zoompan=z='min(zoom+0.0015,1.5)':x='iw/4':y='ih/4':d={}:s={}x{}:fps={}".format(d, WIDTH, HEIGHT, FPS),
        "zoompan=z='if(eq(on,1),1.5,max(zoom-0.001,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={}:s={}x{}:fps={}".format(d, WIDTH, HEIGHT, FPS),
        "zoompan=z='min(zoom+0.002,1.6)':x='iw/2-(iw/zoom/2)':y='ih/3':d={}:s={}x{}:fps={}".format(d, WIDTH, HEIGHT, FPS),
        "zoompan=z='min(zoom+0.001,1.3)':x='if(eq(on,1),iw/3,x-1)':y='ih/3':d={}:s={}x{}:fps={}".format(d, WIDTH, HEIGHT, FPS),
    ]
    vf = zooms[idx % len(zooms)]
    print("  [Video] {}: Ken Burns ({:.1f}s)...".format(sid, dur))
    sys.stdout.flush()
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", matches[0], "-vf", vf, "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), clip], capture_output=True)
    print("  [Video] {} done".format(sid))
    sys.stdout.flush()

print("\n[Phase 4] Merging scenes...")
sys.stdout.flush()
merged = []
for s in scene_data:
    sid = s["sid"]
    clip = os.path.join(TEMP_DIR, "{}_clip.mp4".format(sid))
    narr = os.path.join(TEMP_DIR, "{}_narration.mp3".format(sid))
    out = os.path.join(TEMP_DIR, "{}_merged.mp4".format(sid))
    if os.path.exists(out):
        merged.append(out)
        print("  [Merge] {} exists, skip".format(sid))
        continue
    if not os.path.exists(clip):
        continue
    if os.path.exists(narr):
        subprocess.run(["ffmpeg", "-y", "-i", clip, "-i", narr, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], capture_output=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-i", clip, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-c:v", "copy", "-c:a", "aac", "-shortest", "-t", str(s["dur"]), out], capture_output=True)
    if os.path.exists(out):
        merged.append(out)
        print("  [Merge] {} done".format(sid))
    sys.stdout.flush()

print("\n[Phase 5] Final concat ({} scenes)...".format(len(merged)))
sys.stdout.flush()
listf = os.path.join(TEMP_DIR, "concat_list.txt")
with open(listf, "w", encoding="utf-8") as fp:
    for m in merged:
            fp.write("file '{}'\n".format(os.path.abspath(m).replace("\\", "/")))
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf, "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", OUTPUT_FILE], capture_output=True)

if os.path.exists(OUTPUT_FILE):
    dur = get_dur(OUTPUT_FILE)
    sz = os.path.getsize(OUTPUT_FILE) / 1024 / 1024
    print("\n" + "=" * 60)
    print("  COMPLETE!")
    print("  File:", OUTPUT_FILE)
    print("  Duration: {:.1f}s | Size: {:.1f}MB".format(dur, sz))
    print("=" * 60)
else:
    print("  ERROR: final video not created!")
