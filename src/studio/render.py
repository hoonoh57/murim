"""Selected scene render and content-keyed reuse. No model fallback."""
import json
import math
import os
import re
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from .workspace import (FPS, AUDIO, assets, asset_path, digest, hash_bytes, safe, scenes,
                        track, scene_fingerprint, state, xml_bytes)

W,H=1920,1080


def executables(root):
    # Reuse installed project-independent binaries before requiring PATH changes.
    locations=[Path(os.environ.get('MURIM_FFMPEG_DIR','E:/GPT-SoVITS'))]
    local=os.environ.get('LOCALAPPDATA')
    if local:
        locations.extend(sorted(Path(local).glob('Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin'),reverse=True))
    for folder in locations:
        pair=[folder/(n+'.exe') for n in ('ffmpeg','ffprobe')]
        if all(p.is_file() for p in pair):
            # Prefer current PATH if it has both executables.
            break
    else: pair=[]
    ff,fp=shutil.which('ffmpeg'),shutil.which('ffprobe')
    if ff and fp: return ff,fp
    # Prefer WinGet's newer installation when PATH is absent.
    for folder in reversed(locations):
        candidate=[folder/(n+'.exe') for n in ('ffmpeg','ffprobe')]
        if all(p.is_file() for p in candidate): return tuple(str(p) for p in candidate)
    raise ValueError('FFmpeg/ffprobe not found in PATH or existing installations')


def run(args,timeout=900):
    r=subprocess.run([str(a) for a in args],capture_output=True,timeout=timeout)
    if r.returncode: raise RuntimeError(Path(str(args[0])).name+': '+r.stderr.decode('utf-8','replace')[-1000:])
    return r.stdout


def probe(fp,p): return json.loads(run([fp,'-v','error','-show_streams','-show_format','-of','json',p],30))


def media_info(fp,p,kind):
    if kind=='image':
        from PIL import Image
        with Image.open(p) as im:
            if im.format not in ('JPEG','PNG','WEBP') or max(im.size)>16000: raise ValueError('Unsupported image')
            im.load(); return dict(width=im.width,height=im.height)
    info=probe(fp,p); ss=info.get('streams',[])
    if not any(x.get('codec_type')==kind for x in ss): raise ValueError('Missing '+kind+' stream')
    d=float(info['format']['duration'])
    if not math.isfinite(d) or not 0<d<=3600: raise ValueError('Invalid duration')
    return dict(duration=d)


def font():
    for name in [os.environ.get('MURIM_FONT'), 'C:/Windows/Fonts/batang.ttc','C:/Windows/Fonts/malgun.ttf','/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if name and Path(name).is_file(): return name
    raise ValueError('Install/select a Korean font via MURIM_FONT')


def make_plate(s,a,p,out):
    """2x source-native canvas. No upscaling the source to fill the viewport."""
    from PIL import Image, ImageDraw
    with Image.open(p) as im:
        im=im.convert('RGB'); t=track(s,'image')
        if t.get('framing')=='right': im=im.crop((int(im.width*.61),0,im.width,int(im.height*.63)))
        # At most 2x output pixels. FFmpeg's zoom is capped below by native pixels.
        im.thumbnail((W*2-160,H*2-300),Image.Resampling.LANCZOS)
        plate=Image.new('RGB',(W*2,H*2),'#f6f2e9'); plate.paste(im,((plate.width-im.width)//2,(plate.height-im.height)//2-60)); plate.save(out)
        return im.size


def overlay(s,doc,out):
    from PIL import Image,ImageDraw,ImageFont
    im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im); f=font(); t=track(s,'subtitle');
    # Title and source attribution are static, subtitle animation is separate.
    title=s.get('title',''); v=track(s,'video'); i=track(s,'image'); a=assets(doc).get(v.get('asset')) if v is not None and v.get('asset') else assets(doc).get(i.get('asset')) if i is not None else None
    if title:
        d.rectangle((48,35,1872,100),fill=(15,15,15,150));d.text((72,46),title[:70],font=ImageFont.truetype(f,38),fill='white')
    if a is not None:
        label=a.get('label','')+' · '+a.get('source','')
        d.rectangle((48,875,1872,929),fill=(15,15,15,180));d.text((70,885),label[:100],font=ImageFont.truetype(f,24),fill='white')
    im.save(out)
    sub=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(sub)
    if t is not None and (t.text or '').strip():
        ff=ImageFont.truetype(f,int(t.get('size','48'))); lines=[]; line=''
        for word in t.text.split():
            nxt=(line+' '+word).strip()
            if line and d.textlength(nxt,font=ff)>1700: lines.append(line); line=word
            else: line=nxt
        if line: lines.append(line)
        if len(lines)>3 or any(d.textlength(x,font=ff)>1700 for x in lines): raise ValueError('Subtitle exceeds safe region; shorten text or use more scenes')
        color=t.get('color','#ffffff'); rgb=tuple(int(color[i:i+2],16) for i in (1,3,5)); light=sum(rgb)<270
        d.rectangle((65,940-len(lines)*int(t.get('size','48'))//2,1855,1060),fill=(250,247,238,220) if light else (15,15,15,190))
        for k,l in enumerate(lines):
            d.text((W//2,987+(k-(len(lines)-1)/2)*(int(t.get('size','48'))+5)),l,font=ff,fill=t.get('color','#ffffff'),stroke_width=1,stroke_fill='#f5efd9' if light else '#242424',anchor='mm')
    target=out.with_name('subtitle.png');sub.save(target);return target


def fingerprint(root,doc,s,ff):
    aa=assets(doc); paths={}
    for t in s:
        aid=t.get('asset','')
        if aid: paths[aid]=asset_path(root,aa[aid])
    key=hash_bytes(json.dumps([scene_fingerprint(s),{aid:aa[aid].get('sha256') for aid in sorted(paths)},digest(Path(__file__)),digest(Path(__file__).with_name('workspace.py')),str(ff),digest(Path(font()))],sort_keys=True).encode())
    return key,paths


def validate_clip(fp,p,frames):
    info=probe(fp,p); v=next((x for x in info['streams'] if x.get('codec_type')=='video'),None); a=next((x for x in info['streams'] if x.get('codec_type')=='audio'),None)
    if not v or not a or (v.get('width'),v.get('height'),int(v.get('nb_frames',0)))!=(W,H,frames) or abs(float(info['format']['duration'])-frames/FPS)>.15: raise ValueError('Rendered clip timing or stream mismatch')


def render_scene(store,pid,doc,s,ff,fp):
    root=store.root; n=int(s.get('frames')); dur=n/FPS; cache=safe(store.folder(pid),'cache',directory=True,create=True)
    key,paths=fingerprint(root,doc,s,ff)
    if s.get('baseline-state')==scene_fingerprint(s) and s.get('baseline-clip'):
        p=safe(root,s.get('baseline-clip'))
        if digest(p)!=s.get('baseline-sha'): raise ValueError('Original clip changed')
        validate_clip(fp,p,n); return p,'ORIGINAL_REUSED'
    target=cache/(key+'.mp4'); receipt=cache/(key+'.json')
    if target.exists() or receipt.exists():
        p=safe(cache,target.name); r=json.loads(safe(cache,receipt.name).read_text(encoding='utf-8'))
        if r.get('sha256')!=digest(p): raise ValueError('Cache hash mismatch')
        validate_clip(fp,p,n);return p,'CACHE_REUSED'
    stage=safe(cache,'job-'+uuid.uuid4().hex[:12],directory=True,create=True); plate=stage/'plate.png'; over=stage/'overlay.png'; sub=overlay(s,doc,over)
    v=track(s,'video'); i=track(s,'image'); e=track(s,'effect'); st=track(s,'subtitle'); vol=[]
    args=[ff,'-v','error','-nostdin','-threads','2'];filters=[]
    camera=e.get('camera','static') if e is not None else 'static'; amount=float(e.get('amount','0.12')) if e is not None else 0
    if v is not None and (v.text or '').strip() and not v.get('asset'): raise ValueError('Motion video pending; import actual video or remove motion track')
    if v is not None and v.get('asset'):
        p=paths[v.get('asset')]; start=int(v.get('in','0'))/FPS
        if media_info(fp,p,'video')['duration']+0.02 < start+dur: raise ValueError('Video shorter than selected scene; adjust its length')
        if camera!='static': raise ValueError('Camera motion on video not supported in this revision; use baked video motion')
        args+=['-ss',str(start),'-i',p];filters.append(f'[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,trim=duration={dur},setpts=PTS-STARTPTS[base]')
    elif i is not None and i.get('asset'):
        make_plate(s,assets(doc)[i.get('asset')],paths[i.get('asset')],plate);args+=['-i',plate]
        # Zoompan works on the 2x native canvas. Bound output crop to >= output size.
        u=f'on/{max(1,n-1)}'; z={'static':'1','push':f'1+{amount}*{u}','pull':f'1+{amount}*(1-{u})','pan-right':f'1+{amount}','pan-left':f'1+{amount}'}[camera]
        x={'pan-right':f'(iw-iw/zoom)*{u}','pan-left':f'(iw-iw/zoom)*(1-{u})'}.get(camera,'(iw-iw/zoom)/2')
        filters.append(f"[0:v]zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':d={n}:s={W}x{H}:fps={FPS},setsar=1[base]")
    else: raise ValueError('Scene has no ready visual asset')
    args+=['-i',over,'-loop','1','-framerate',str(FPS),'-i',sub]; filters.append('[base][1:v]overlay=0:0[decor]')
    begin=int(st.get('offset','0'))/FPS if st is not None else 0; end=int(st.get('end',str(n)))/FPS if st is not None else dur;mode=st.get('mode','plain') if st is not None else 'plain'
    # Real fade or rising reveal. Subtitles remain separate from original images.
    if mode=='fade': filters.append(f'[2:v]format=rgba,fade=t=in:st={begin}:d={min(.4,(end-begin)/2)}:alpha=1[sub]'); subname='sub'
    else: subname='2:v'
    y=f"'if(lt(t,{begin+0.4}),max(0,36*(1-(t-{begin})/0.4)),0)'" if mode=='reveal' else '0'
    filters.append(f"[decor][{subname}]overlay=0:{y}:enable='between(t,{begin},{end-1/FPS/2})',format=yuv420p[v]")
    input_no=3
    for k in AUDIO:
        t=track(s,k)
        if t is None: continue
        if not t.get('asset'):
            if k=='voice' and (t.text or '').strip(): raise ValueError('Narration is pending: generate/import it first')
            continue
        p=paths[t.get('asset')]; info=media_info(fp,p,'audio'); offset=int(t.get('offset','0'))/FPS; start=int(t.get('in','0'))/FPS
        if info['duration']<=start: raise ValueError('Audio trim exceeds duration')
        if k=='voice' and (t.text or '').strip() and info['duration']-start+offset>dur+.03: raise ValueError('Narration exceeds scene duration: extend scene, do not truncate')
        gain=float(t.get('gain','0' if k=='voice' else '-18'));args+=['-ss',str(start),'-i',p]
        if k=='voice':
            check=subprocess.run([ff,'-hide_banner','-i',str(p),'-af','volumedetect','-f','null','-'],capture_output=True,timeout=60).stderr.decode('utf-8','replace')
            peak=re.search(r'max_volume:\s*(-?[\d.]+) dB',check)
            if not peak or float(peak.group(1))<-45: raise ValueError('Silent or invalid narration')
        filters.append(f'[{input_no}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,adelay={round(offset*1000)}:all=1,apad,atrim=duration={dur}[a{input_no}]');vol.append(f'[a{input_no}]');input_no+=1
    if vol: filters.append(''.join(vol)+f'amix=inputs={len(vol)}:normalize=0,alimiter=limit=0.95,atrim=duration={dur}[a]')
    else:
        args+=['-f','lavfi','-i','anullsrc=r=48000:cl=stereo'];filters.append(f'[{input_no}:a]atrim=duration={dur}[a]')
    tmp=stage/'clip.mp4'
    args+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-t',str(dur),'-frames:v',str(n),'-c:v','libx264','-threads','2','-preset','fast','-crf','18','-c:a','aac','-ar','48000','-ac','2','-b:a','192k','-movflags','+faststart',tmp]
    run(args);validate_clip(fp,tmp,n);h=digest(tmp)
    # Cache entries are create-only; requests are serialized by the caller.
    tmp.rename(target); receipt.write_text(json.dumps({'sha256':h,'key':key,'frames':n}),encoding='utf-8');return target,'RENDERED'


def render(store,pid,doc,revision,scene_id=None):
    ff,fp=executables(store.root); ss=scenes(doc)
    if scene_id is not None:
        ss=[s for s in ss if s.get('id')==scene_id]
        if len(ss)!=1: raise ValueError('Unknown selected scene')
    out=safe(store.folder(pid),'renders/'+uuid.uuid4().hex[:12],directory=True,create=True)
    (out/'source.mvml.xml').write_bytes(xml_bytes(doc)); records=[]
    for j,s in enumerate(ss):
        p,status=render_scene(store,pid,doc,s,ff,fp); dest=out/f'part-{j:04d}.mp4'
        shutil.copyfile(p,dest); records.append(dict(scene=s.get('id'),status=status,sha256=digest(dest),file=dest.name))
    # Normalize audio/video first using concat demuxer only when codec parameters are same;
    # concat filter re-encodes timeline to support legacy mono and current stereo clips.
    result=out/'intro.mp4'; frames=sum(int(s.get('frames')) for s in ss)
    if len(records)==1: shutil.copyfile(out/records[0]['file'],result)
    else:
        args=[ff,'-v','error','-nostdin'];fc=[];pairs=[]
        for j,(s,r) in enumerate(zip(ss,records)):
            args+=['-i',out/r['file']]; d=int(s.get('frames'))/FPS
            fc+= [f'[{j}:v]fps={FPS},setsar=1,trim=duration={d},setpts=PTS-STARTPTS[v{j}]',f'[{j}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={d},asetpts=PTS-STARTPTS[a{j}]'];pairs.append(f'[v{j}][a{j}]')
        fc.append(''.join(pairs)+f'concat=n={len(ss)}:v=1:a=1[v][a]')
        run(args+['-filter_complex_threads','2','-filter_complex',';'.join(fc),'-map','[v]','-map','[a]','-frames:v',str(frames),'-t',str(frames/FPS),'-c:v','libx264','-threads','2','-preset','fast','-crf','18','-c:a','aac','-ar','48000','-ac','2','-movflags','+faststart',result])
    validate_clip(fp,result,frames)
    receipt=dict(id=out.name,revision=revision,scene=scene_id,frames=frames,sha256=digest(result),clips=records,status='DRAFT_RENDERED_QUALITY_NOT_APPROVED')
    (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');return receipt
