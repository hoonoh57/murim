"""Render the existing M-VML v0.2 using source images and an installed Korean voice.
No remote execution, model installation, paid API, or publication. Review candidate only.
"""
import argparse, hashlib, json, os, re, shutil, stat, subprocess, sys, uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

W, H, FPS = 1920, 1080, 24
ROOT = Path(__file__).resolve().parents[1]
XML = ROOT / 'experiments/mvml_intro_lab/review_v02/intro.mvml.xml'
ALLOWED = {'upload.wikimedia.org', 'www.museum.go.kr'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def plan(xml):
    data = xml.read_bytes()
    if len(data) > 100000 or re.search(rb'<!\s*(DOCTYPE|ENTITY)', data, re.I):
        raise ValueError('Unsafe XML')
    doc = ET.fromstring(data)
    if doc.tag != 'mvml' or doc.get('version') != '0.2-review' or doc.get('duration') != '60':
        raise ValueError('Expected v0.2-review, 60 seconds')
    reg = {}
    for a in doc.findall('./registry/asset'):
        key = a.get('id', '')
        u = urlsplit(a.get('url', ''))
        if not re.fullmatch(r'ART:[A-Z]+@1', key) or key in reg or u.scheme != 'https' or u.hostname not in ALLOWED or u.username or u.password or not a.get('source') or not a.get('rights'):
            raise ValueError('Invalid source asset: ' + key)
        reg[key] = dict(a.attrib)
    shots, ids, pos = [], set(), 0
    for s in doc.findall('./sequence/shot'):
        key, d, aid = s.get('id', ''), int(s.get('seconds', 0)), s.get('asset')
        line = (s.text or '').strip()
        if not re.fullmatch(r'S[0-9]{2}', key) or key in ids or aid not in reg or not 1 <= d <= 20 or not line or s.get('framing') not in ('whole','right'):
            raise ValueError('Invalid shot: ' + key)
        ids.add(key); shots.append(dict(id=key, start=pos, seconds=d, asset=aid, framing=s.get('framing'), heading=s.get('heading',''), text=line, cue=s.get('cue',''))); pos += d
    if pos != 60 or not shots: raise ValueError('Timeline must be exactly 60 seconds')
    return reg, shots

def safe_output(root):
    root = root.resolve(); p = root
    for part in ('outputs','sehando','intro','v0.2'):
        p = p / part
        if p.exists() or p.is_symlink():
            if p.is_symlink() or not p.is_dir() or getattr(p.lstat(), 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
                raise ValueError('Unsafe output path: ' + str(p))
        else: p.mkdir()
        if not p.resolve().is_relative_to(root): raise ValueError('Output escapes project')
    p = p / uuid.uuid4().hex[:12]; p.mkdir(); return p

def run(args):
    p = subprocess.run([str(x) for x in args], capture_output=True, check=False)
    if p.returncode: raise RuntimeError(Path(str(args[0])).name + ': ' + p.stderr.decode('utf-8','replace')[-1200:])
    return p.stdout

def probe(ffprobe, p):
    return json.loads(run([ffprobe,'-v','error','-show_streams','-show_format','-of','json',p]))

def acquire(asset, p):
    from PIL import Image
    request = Request(asset['url'], headers={'User-Agent':'MurimResearch/1.0 (source image retrieval for private evaluation)'})
    with urlopen(request, timeout=30) as r:
        if urlsplit(r.geturl()).hostname not in ALLOWED: raise ValueError('Unexpected source host')
        data = r.read(25*1024*1024+1)
    if len(data)>25*1024*1024: raise ValueError('Source exceeds byte budget')
    p.write_bytes(data)
    with Image.open(p) as im:
        im.load(); w,h=im.size
        if im.format not in ('JPEG','PNG') or min(w,h)<240: raise ValueError('Invalid source image')
    if asset.get('expected-width') and (w,h)!=(int(asset['expected-width']),int(asset['expected-height'])):
        raise ValueError('High-resolution source dimensions differ')
    return dict(asset, file=p.name, sha256=sha(p), width=w, height=h, retrieval='SOURCE_URL_BYTES_VERIFIED', approval='REVIEW_ONLY')

def korean_voice():
    if os.name!='nt': raise RuntimeError('Windows Korean SAPI voice required; no silent fallback')
    script="Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.GetInstalledVoices() | Where-Object {$_.Enabled -and $_.VoiceInfo.Culture.Name -like 'ko-*'} | ForEach-Object {$_.VoiceInfo.Name}; $s.Dispose()"
    out=run(['powershell.exe','-NoProfile','-NonInteractive','-Command','[Console]::OutputEncoding=[Text.Encoding]::UTF8; '+script]).decode('utf-8-sig').strip().splitlines()
    if not out: raise RuntimeError('No installed Korean SAPI voice; use --voice-dir with S01.wav ...')
    return out[0]

def speak(text, voice, path):
    t=path.with_suffix('.txt'); t.write_text(text,encoding='utf-8')
    script="Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SelectVoice($env:MURIM_SAPI_VOICE); $s.Rate=-1; $s.SetOutputToWaveFile($env:MURIM_SAPI_OUT); $s.Speak([IO.File]::ReadAllText($env:MURIM_SAPI_TEXT,[Text.Encoding]::UTF8)); $s.Dispose()"
    env=dict(os.environ,MURIM_SAPI_VOICE=voice,MURIM_SAPI_OUT=str(path),MURIM_SAPI_TEXT=str(t))
    subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],env=env,check=True,capture_output=True)

def frame(s,a,src,target):
    from PIL import Image,ImageDraw,ImageFont
    font=Path(os.getenv('MURIM_FONT','C:/Windows/Fonts/batang.ttc'))
    if not font.is_file(): font=Path('C:/Windows/Fonts/malgun.ttf')
    if not font.is_file(): raise ValueError('Korean font required (MURIM_FONT)')
    f=lambda n: ImageFont.truetype(str(font),n)
    paper=Image.new('RGB',(W,H),'#f6f2e9'); d=ImageDraw.Draw(paper)
    with Image.open(src) as im:
        im=im.convert('RGB')
        if s['framing']=='right': im=im.crop((int(im.width*.61),0,im.width,int(im.height*.63)))
        native=im.size; im.thumbnail((1760,770),Image.Resampling.LANCZOS)
        x=(W-im.width)//2; y=94+(780-im.height)//2
        paper.paste(im,(x,y)); d.rectangle((x-1,y-1,x+im.width,y+im.height),outline='#c8c0af')
    if s['heading']: d.text((80,35),s['heading'],font=f(42),fill='#283a34')
    d.text((80,886),a['label'],font=f(28),fill='#564e43')
    credit='출처: Wikimedia Commons (PD-Art 표기)' if 'wikimedia' in a['url'] else '출처: 국립중앙박물관 · 공공누리 제1유형'
    d.text((1840,886),credit,font=f(24),fill='#564e43',anchor='ra')
    lines=[]; line=''
    for word in s['text'].split():
        nxt=(line+' '+word).strip()
        if line and d.textlength(nxt,font=f(39))>1700: lines.append(line); line=word
        else: line=nxt
    if line: lines.append(line)
    if len(lines)>2: raise ValueError('Subtitle exceeds two lines')
    for i,l in enumerate(lines): d.text((W//2,970+i*48-(len(lines)-1)*24),l,font=f(39),fill='#242a25',anchor='mm')
    paper.save(target); return {'crop_native':list(native),'display_pixels':list(im.size),'upscaled':False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--plan-only',action='store_true'); ap.add_argument('--voice-dir',type=Path); args=ap.parse_args()
    reg,shots=plan(XML)
    if args.plan_only:
        print('[PASS] M-VML 7-cut 60-second plan validated' if len(shots)==7 else '[PASS] M-VML 60-second plan validated'); return
    from PIL import Image
    ff,fp=shutil.which('ffmpeg'),shutil.which('ffprobe')
    if not ff or not fp: raise RuntimeError('FFmpeg and ffprobe must already be available')
    voice='USER_WAV' if args.voice_dir else korean_voice()
    out=safe_output(ROOT); print('OUTPUT: '+str(out),flush=True)
    try:
        shutil.copyfile(XML,out/'source.mvml.xml'); assets={}; parts=[]
        for aid in sorted({s['asset'] for s in shots}):
            p=out/(aid.split(':')[1].split('@')[0].lower()+'.jpg'); assets[aid]=acquire(reg[aid],p)
        (out/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2),encoding='utf-8')
        for s in shots:
            p=out/(s['id']+'.wav'); png=out/(s['id']+'.png'); mp4=out/(s['id']+'.mp4')
            if args.voice_dir: shutil.copyfile(args.voice_dir/p.name,p)
            else: speak(s['text'],voice,p)
            dur=float(probe(fp,p)['format']['duration'])
            if not 0.4<=dur<=s['seconds']-.15: raise ValueError('Narration does not fit shot '+s['id']+': '+str(dur))
            a=assets[s['asset']]; geom=frame(s,a,out/a['file'],png); s.update(geometry=geom,voice_seconds=dur,voice_sha256=sha(p))
            run([ff,'-v','error','-loop','1','-framerate',str(FPS),'-i',png,'-i',p,'-af','adelay=150:all=1,apad','-t',str(s['seconds']),'-vf','format=yuv420p','-c:v','libx264','-preset','fast','-crf','17','-c:a','aac','-ar','48000','-ac','1','-b:a','128k','-movflags','+faststart',mp4]); parts.append(mp4.name)
        (out/'concat.txt').write_text(''.join("file '"+n+"'\n" for n in parts),encoding='utf-8')
        temp=out/'candidate.tmp.mp4'; result=out/'intro.mp4'
        run([ff,'-v','error','-f','concat','-safe','1','-i',out/'concat.txt','-c','copy','-movflags','+faststart',temp]); info=probe(fp,temp)
        v=next(x for x in info['streams'] if x['codec_type']=='video'); a=next(x for x in info['streams'] if x['codec_type']=='audio')
        if (v['width'],v['height'],int(v['nb_frames']))!=(W,H,1440) or abs(float(info['format']['duration'])-60)>.15: raise ValueError('Output format/duration mismatch')
        temp.rename(result)
        rec={'status':'REVIEW_CANDIDATE_NOT_APPROVED','video_sha256':sha(result),'source_sha256':sha(out/'source.mvml.xml'),'duration':float(info['format']['duration']),'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'voice':voice,'assets':assets,'shots':shots,'limitations':['SAPI/user WAV audition pending','static source-first visual treatment','rights and source authenticity review pending','actual audience and external review NOT_RUN']}
        (out/'receipt.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8'); print('[PASS] Rendered review candidate: '+str(result))
    except Exception as e:
        (out/'failure.json').write_text(json.dumps({'status':'BLOCKED_OR_FAILED','error':str(e)[:1500]},ensure_ascii=False),encoding='utf-8'); raise

if __name__=='__main__':
    try: main()
    except Exception as exc: print('[FAIL] '+str(exc),file=sys.stderr); sys.exit(1)
