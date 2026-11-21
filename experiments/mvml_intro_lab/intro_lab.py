"""M-VML pilot: compile ID references, render local reference animatic, edit via loopback UI."""
from pathlib import Path
import argparse, hashlib, json, re, secrets, shutil, subprocess, time, uuid, wave, math, array, os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
W,H,FPS=1280,720,24

def safe_file(name):
    p=Path(name); f=(ROOT/p).resolve()
    if p.is_absolute() or '..' in p.parts or not f.is_relative_to(ROOT) or not f.is_file(): raise ValueError('Missing/unsafe file: '+name)
    return f

def compile_vml(xml):
    if len(xml)>100000 or re.search(r'<!\s*(DOCTYPE|ENTITY)',xml,re.I): raise ValueError('Unsafe XML')
    r=ET.fromstring(xml)
    if r.tag!='mvml' or r.get('version')!='0.1' or tuple(r.get(k) for k in ('width','height','fps'))!=('1280','720','24') or [e.tag for e in r]!=['registry','sequence']: raise ValueError('Expected M-VML 0.1 / 720p24')
    kinds={'asset':'IMG','camera':'CAM','style':'STYLE','theme':'THEME','character':'CHAR'}; reg={}
    for e in r[0]:
        id=e.get('id',''); a=dict(e.attrib,type=e.tag)
        if e.tag not in kinds or not re.fullmatch(kinds[e.tag]+r':[A-Za-z0-9_]+@[1-9][0-9]*',id) or id in reg: raise ValueError('Invalid/duplicate ID: '+id)
        if e.tag=='asset':
            if a.get('kind')!='concept' or not a.get('origin') or not a.get('display_label') or len(a['display_label'])>60 or not re.fullmatch(r'assets/[a-z]+\.jpg',a.get('file','')): raise ValueError('Concept asset provenance/path required')
            if hashlib.sha256(safe_file(a['file']).read_bytes()).hexdigest()!=a.get('sha256'): raise ValueError('Asset hash mismatch: '+id)
        if e.tag=='camera' and (not 1<=float(a['zoom'])<=1.25 or a.get('anchor') not in ('center','right')): raise ValueError('Invalid camera')
        reg[id]=a
    def ref(id,kind):
        if id not in reg or reg[id]['type']!=kind: raise ValueError('Unresolved/wrong type: '+str(id))
        return reg[id]
    for a in reg.values():
        if a['type']=='character': ref(a.get('image'),'asset')
    seq=r[1]; style=ref(seq.get('style'),'style');theme=ref(seq.get('theme'),'theme'); shots=[];cursor=0;seen=set()
    for e in seq:
        id=e.get('id','');d=int(e.get('seconds','0'));title=e.get('title','').strip(); caption=e.findtext('caption','').strip()
        if e.tag!='shot' or not re.fullmatch(r'[A-Za-z0-9_-]{1,24}',id) or id in seen or not 1<=d<=20 or e.get('truth')!='staging' or not 0<len(title)<=40 or not 0<len(caption)<=130: raise ValueError('Invalid shot: '+id)
        seen.add(id);shots.append(dict(id=id,start=cursor,seconds=d,title=title,caption=caption,image=ref(e.get('image'),'asset'),camera=ref(e.get('camera'),'camera'),character=ref(e.get('character'),'character') if e.get('character') else None,truth='staging'));cursor+=d
    if cursor!=60: raise ValueError('Expected exactly 60 seconds; got '+str(cursor))
    return dict(work=r.get('work'),seconds=cursor,fps=FPS,width=W,height=H,style=style,theme=theme,registry=reg,shots=shots,source_sha256=hashlib.sha256(xml.encode()).hexdigest())

def font():
    for s in [os.getenv('MURIM_FONT'),'/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc','/usr/share/fonts/truetype/nanum/NanumSquareR.ttf','C:/Windows/Fonts/malgun.ttf']:
        if s and Path(s).is_file():return s
    raise ValueError('Set MURIM_FONT to an installed Korean font')

def overlay(s,p):
    from PIL import Image,ImageDraw,ImageFont
    im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im);f=font();title=ImageFont.truetype(f,44);small=ImageFont.truetype(f,22);sub=ImageFont.truetype(f,32)
    for y in range(490,H):d.line((0,y,W,y),fill=(12,14,18,round(205*((y-490)/(H-490))**.8)))
    for y in range(145):d.line((0,y,W,y),fill=(12,14,18,round(195*(1-y/145))))
    d.text((48,34),s['title'],font=title,fill='#f7ecd9',stroke_width=1,stroke_fill='#26221d')
    label=s['image']['display_label']
    d.rounded_rectangle((45,91,60+int(d.textlength(label,font=small)),125),radius=4,fill=(18,20,22,220));d.text((52,94),label,font=small,fill='#f5e7d1')
    lines=[];line=''
    for word in s['caption'].split():
        candidate=(line+' '+word).strip()
        if d.textlength(candidate,font=sub)>1120 and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    for i,line in enumerate(lines):d.text((W//2,650-(len(lines)-1-i)*43),line,anchor='mm',font=sub,fill='white',stroke_width=1,stroke_fill='#302b25')
    im.save(p)

def music(p):
    sr=24000;samples=array.array('h');chords=[(110,164.81,220),(98,146.83,196),(82.41,123.47,164.81),(110,146.83,196),(130.81,164.81,261.63),(110,164.81,220)]
    for n in range(sr*60):
        t=n/sr;k=min(5,int(t/10));u=t-k*10;env=min(1,u/2,(10-u)/2)*min(1,t/2,(60-t)/3)
        v=sum(math.sin(2*math.pi*f*t)+.18*math.sin(4*math.pi*f*t) for f in chords[k])/3
        samples.append(int(32767*.095*env*v*(.85+.15*math.sin(2*math.pi*.13*t))))
    with wave.open(str(p),'wb') as f:f.setparams((1,2,sr,0,'NONE','not compressed'));f.writeframes(samples.tobytes())

def render(xml):
    plan=compile_vml(xml);ff=shutil.which('ffmpeg');probe=shutil.which('ffprobe')
    if not ff or not probe:raise ValueError('FFmpeg/ffprobe required on PATH')
    out=ROOT/'renders'/uuid.uuid4().hex[:12];out.mkdir(parents=True);start=time.monotonic();parts=[]
    (out/'source.mvml.xml').write_text(xml,encoding='utf-8');(out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
    def run(args):subprocess.run([ff,'-hide_banner','-loglevel','error']+args,check=True,stderr=subprocess.PIPE)
    for s in plan['shots']:
        n=s['seconds']*FPS;p=out/(s['id']+'.png');part=out/(s['id']+'.mp4');overlay(s,p);z=float(s['camera']['zoom']);x='iw-iw/zoom' if s['camera']['anchor']=='right' else 'iw/2-iw/zoom/2'
        filt=f'[0:v]scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,zoompan=z=1+{z-1:.6f}*on/{n-1}:x={x}:y=ih/2-ih/zoom/2:d={n}:s={W}x{H}:fps={FPS}[bg];[bg][1:v]overlay=0:0,format=yuv420p'
        run(['-threads','2','-i',str(safe_file(s['image']['file'])),'-i',str(p),'-filter_complex_threads','2','-filter_complex',filt,'-frames:v',str(n),'-c:v','libx264','-threads','2','-preset','ultrafast','-crf','20','-an',str(part)]);parts.append(part.name)
    c=out/'parts.txt';c.write_text(''.join("file '"+n+"'\n" for n in parts),encoding='utf-8');m=out/'music.wav';music(m);result=out/'intro.mp4'
    run(['-f','concat','-safe','1','-i',str(c),'-i',str(m),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','128k','-t','60','-movflags','+faststart',str(result)])
    info=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-of','json',str(result)]));v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio')
    if abs(float(info['format']['duration'])-60)>.05 or (v['width'],v['height'],int(v['nb_frames']))!=(W,H,1440):raise ValueError('Output duration/frame mismatch')
    receipt=dict(source_sha256=plan['source_sha256'],video=result.relative_to(ROOT).as_posix(),duration=float(info['format']['duration']),frames=1440,size=[W,H],video_codec=v['codec_name'],audio_codec=a['codec_name'],elapsed_seconds=round(time.monotonic()-start,2),sha256=hashlib.sha256(result.read_bytes()).hexdigest(),status='REFERENCE_ANIMATIC_RENDERED',limitations=['No narration','No ComfyUI generation','Character identity unverified','All imagery concept reenactment'])
    (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');return receipt

def serve():
    token=secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        def reply(self,data,typ,status=200):
            self.send_response(status);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def obj(self,x,status=200):self.reply(json.dumps(x,ensure_ascii=False).encode(),'application/json; charset=utf-8',status)
        def do_GET(self):
            try:
                p=self.path.split('?')[0]
                if p=='/':self.reply(safe_file('studio.html').read_text(encoding='utf-8').replace('__TOKEN__',token).encode(),'text/html; charset=utf-8')
                elif p=='/intro.mvml.xml':self.reply(safe_file(p[1:]).read_bytes(),'application/xml; charset=utf-8')
                elif p=='/sample.json':self.reply(safe_file(p[1:]).read_bytes(),'application/json; charset=utf-8')
                elif re.fullmatch(r'/assets/[a-z]+\.jpg',p):self.reply(safe_file(p[1:]).read_bytes(),'image/jpeg')
                elif re.fullmatch(r'/renders/[a-f0-9]{12}/intro\.mp4',p):self.reply(safe_file(p[1:]).read_bytes(),'video/mp4')
                else:self.obj({'error':'not found'},404)
            except (OSError,ValueError):self.obj({'error':'not found'},404)
        def do_POST(self):
            if self.headers.get('X-Murim-Token')!=token or self.path not in ('/compile','/render'):self.obj({'error':'forbidden'},403);return
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<=100000:raise ValueError('Request size')
                xml=self.rfile.read(n).decode('utf-8');self.obj(compile_vml(xml) if self.path=='/compile' else render(xml))
            except Exception as e:self.obj({'error':str(e)[:500]},400)
    print('[PASS] Studio http://127.0.0.1:8769',flush=True);ThreadingHTTPServer(('127.0.0.1',8769),Handler).serve_forever()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--compile',action='store_true');a=p.parse_args()
    if a.render or a.compile:
        xml=safe_file('intro.mvml.xml').read_text(encoding='utf-8');print(json.dumps(render(xml) if a.render else compile_vml(xml),ensure_ascii=False))
    else:serve()
