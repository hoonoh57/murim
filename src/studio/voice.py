"""Local-only TTS adapter. No auto install or mock/SAPI fallback."""
import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from .workspace import safe, digest, register_asset, voice_key, track, get_scene
from .render import executables, media_info

REF_TEXT='안녕하세요. 오늘은 단순히 줄거리를 훑는게 아니라, 한편의 이야기가 어떻게 첫 순간부터 우리를 완벽하게 사로잡는'


def synthesize(store,pid,doc,sid,rights_confirmed):
    if rights_confirmed is not True: raise ValueError('Confirm reference voice use rights before synthesis')
    s=get_scene(doc,sid);t=track(s,'voice')
    if t is None or not (t.text or '').strip(): raise ValueError('Enter spoken text first')
    engine=Path(os.environ.get('MURIM_SOVITS_ROOT','E:/GPT-SoVITS')).resolve()
    exe=engine/'runtime/python.exe';ref=engine/'refs/narrator_ref_7s.wav';worker=store.root/'scripts/studio_sovits_worker.py'
    if not all(p.is_file() for p in (exe,ref,worker)): raise ValueError('Existing GPT-SoVITS runtime/reference not found')
    stage=safe(store.folder(pid),'voice-jobs/'+uuid.uuid4().hex[:12],directory=True,create=True)
    job=dict(text=t.text,prompt_text=REF_TEXT,speed=float(t.get('speed','0.92')),temperature=float(t.get('temperature','0.65')),reference_sha256=digest(ref),worker_sha256=digest(worker),model='GPT-SoVITS-v2')
    request=stage/'request.json';request.write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
    with (stage/'engine.log').open('xb') as log:
        p=subprocess.run([str(exe),str(worker),str(request)],cwd=engine,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
    if p.returncode:raise RuntimeError('GPT-SoVITS inference failed; inspect '+str(stage/'engine.log'))
    wav=safe(stage,'voice.wav');_,fp=executables(store.root);info=media_info(fp,wav,'audio')
    aid=register_asset(doc,store.root,wav,'audio',sid+' · GPT-SoVITS v2',f'Local GPT-SoVITS v2; reference SHA256 {job["reference_sha256"]}; job {stage.name}','사용자가 참조 음성 사용권 확인; 청취 및 게시 심사 별도')
    t.set('asset',aid);t.set('profile','narrator-v2');t.set('origin','SOVITS_V2');t.set('bound',voice_key(t));t.set('in','0')
    v=track(s,'video')
    if v is not None and v.get('lip-bound'):v.attrib.pop('asset',None);v.attrib.pop('lip-bound',None)
    return dict(asset=aid,seconds=info['duration'],fits=info['duration']+int(t.get('offset','0'))/24<=int(s.get('frames'))/24,job=stage.name)
