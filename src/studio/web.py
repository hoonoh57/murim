"""Studio blueprint for existing local Murim Web UI. All writes are explicit, revisioned operations."""
import copy
import json
import os
import re
import secrets
import shutil
import threading
import uuid
from pathlib import Path
from flask import Blueprint, abort, jsonify, render_template, request, send_file
from .workspace import (Store, LOCK, ID, MAX_FILE, assets, asset_path, digest, safe, patch,
                        get_scene, track, register_asset, xml_bytes, state, validate, read_xml, voice_key)
from .render import render, executables, media_info
from .voice import synthesize
from .comfy import store_graph,listed_graphs,generate,MAX_GRAPH

ROOT=Path(__file__).resolve().parents[2]
store=Store(ROOT)
BP=Blueprint('studio',__name__,url_prefix='/studio')
TOKEN=secrets.token_urlsafe(32)
JOB_LOCK=threading.Lock()


@BP.before_request
def local_only():
    if request.remote_addr not in ('127.0.0.1','::1') or request.host.split(':')[0] not in ('localhost','127.0.0.1'):
        abort(403)
    if request.method!='GET':
        if not secrets.compare_digest(request.headers.get('X-Murim-Studio',''),TOKEN):abort(403)
        if request.content_length is None or request.content_length>MAX_FILE+65536:abort(413)


@BP.errorhandler(ValueError)
@BP.errorhandler(OSError)
@BP.errorhandler(RuntimeError)
@BP.errorhandler(KeyError)
@BP.errorhandler(TypeError)
def error(e):return jsonify(error=str(e)[:1000]),400


def data():
    d=request.get_json()
    if not isinstance(d,dict):raise ValueError('JSON object required')
    return d


def current(pid,revision):
    d,h=store.load(pid)
    if revision!=h:raise ValueError('Revision conflict; reload current project')
    return d,h


def brief(pid,**more):return jsonify(dict(store.describe(pid),**more))


@BP.get('/')
def index():return render_template('studio.html',studio_token=TOKEN)


@BP.get('/api/projects')
def projects():
    return jsonify(projects=store.list_projects(),runs=store.runs())


@BP.post('/api/projects')
def create_project():
    d=data()
    if 'run' in d:pid=store.import_run(str(d['run']))
    else:pid=store.create(str(d.get('title','새 작품')).strip()[:120])
    return brief(pid)


@BP.get('/api/project/<pid>')
def project(pid):return brief(pid)


@BP.get('/api/project/<pid>/xml')
def xml(pid):
    d,h=store.load(pid)
    from flask import Response
    return Response(xml_bytes(d),mimetype='application/xml',headers={'Content-Disposition':'attachment; filename="project.mvml.xml"'})


@BP.post('/api/project/<pid>/patch')
def edit(pid):
    x=data()
    with LOCK:
        d,h=current(pid,x.get('revision'));n,dirty=patch(d,x.get('ops'))
        if x.get('preview') is True:return jsonify(state=state(n),dirty=dirty,revision=h)
        store.save(pid,n,h);return brief(pid,dirty=dirty)


@BP.post('/api/project/<pid>/restore')
def restore(pid):
    x=data()
    with LOCK:
        d,h=current(pid,x.get('revision'));old,_=store.load(pid,x.get('target'));store.save(pid,old,h)
        return brief(pid)


@BP.post('/api/project/<pid>/asset')
def add_asset(pid):
    f=request.files.get('file');kind=request.form.get('kind');source=request.form.get('source','').strip();rights=request.form.get('rights','').strip()
    ext=Path(f.filename or '').suffix.lower() if f else ''
    allowed={'image':{'.jpg','.jpeg','.png','.webp'},'video':{'.mp4','.mov','.webm'},'audio':{'.wav','.mp3','.m4a','.flac'}}
    if not f or ext not in allowed.get(kind,set()) or not source or not rights:raise ValueError('Media file, kind, source and rights required')
    with LOCK:
        d,h=current(pid,request.form.get('revision'));base=store.folder(pid)
        stage=safe(base,'imports/'+uuid.uuid4().hex[:12],directory=True,create=True);p=stage/('media'+ext)
        f.save(p)
        if p.stat().st_size>MAX_FILE:raise ValueError('Media exceeds 256 MB')
        _,fp=executables(store.root); info=media_info(fp,p,kind)
        aid=register_asset(d,store.root,p,kind,Path(f.filename).name,source,rights);store.save(pid,d,h)
        return brief(pid,imported=aid,media_info=info)


@BP.get('/api/project/<pid>/asset/<aid>')
def get_asset(pid,aid):
    d,_=store.load(pid);a=assets(d).get(aid)
    if a is None:abort(404)
    # URLs can only resolve registered media, never arbitrary workspace files.
    return send_file(asset_path(store.root,a),conditional=True)


@BP.post('/api/project/<pid>/voice')
def voice(pid):
    x=data()
    if not JOB_LOCK.acquire(False):raise ValueError('Another production job is running')
    try:
        d,h=current(pid,x.get('revision'));r=synthesize(store,pid,d,x.get('scene'),x.get('rights_confirmed'));store.save(pid,d,h)
        return brief(pid,voice_result=r)
    finally:JOB_LOCK.release()


@BP.post('/api/project/<pid>/render')
def render_project(pid):
    x=data()
    if not JOB_LOCK.acquire(False):raise ValueError('Another production job is running')
    try:
        d,h=current(pid,x.get('revision'));r=render(store,pid,d,h,x.get('scene'));return jsonify(r)
    finally:JOB_LOCK.release()


@BP.get('/api/project/<pid>/renders')
def renders(pid):
    folder=store.folder(pid);base=folder/'renders'
    if not base.exists():return jsonify(renders=[])
    base=safe(folder,'renders',directory=True);result=[]
    for p in sorted(base.iterdir(),key=lambda p:p.stat().st_mtime,reverse=True):
        if ID.fullmatch(p.name) and p.is_dir() and not p.is_symlink() and (p/'receipt.json').is_file():
            try:result.append(json.loads(safe(p,'receipt.json').read_text(encoding='utf-8')))
            except (OSError,ValueError):continue
    return jsonify(renders=result[:150])


@BP.get('/api/project/<pid>/render/<rid>')
def rendered(pid,rid):
    if not ID.fullmatch(rid):abort(404)
    base=safe(store.folder(pid),'renders/'+rid,directory=True);rec=json.loads(safe(base,'receipt.json').read_text(encoding='utf-8'));p=safe(base,'intro.mp4')
    if digest(p)!=rec.get('sha256'):raise ValueError('Render integrity error')
    return send_file(p,mimetype='video/mp4',conditional=True)


@BP.get('/api/project/<pid>/baseline')
def baseline(pid):
    d,h=store.load(pid);run=d.get('baseline','')
    if not ID.fullmatch(run):abort(404)
    base=safe(store.root,'outputs/sehando/intro/v0.2/'+run,directory=True);r=json.loads(safe(base,'receipt.json').read_text(encoding='utf-8'));p=safe(base,'intro.mp4')
    if digest(p)!=r['video_sha256']:raise ValueError('Baseline integrity error')
    return send_file(p,mimetype='video/mp4',conditional=True)


@BP.get('/api/project/<pid>/prompt/<sid>')
def relay_prompt(pid,sid):
    d,h=store.load(pid);s=get_scene(d,sid);context=next(x for x in state(d)['scenes'] if x['id']==sid)
    opts=[a for a in state(d)['assets'] if a['id'] in {t.get('asset') for t in s}]
    mode=request.args.get('mode','patch')
    if mode=='patch':
        text='현재 선택 장면만 수정하는 JSON 배열을 제안. 외부 파일/코드/URL/명령 실행 금지. 허용: set(scene,track,values), remove(scene,track), scene(scene,title,frames). track=image(asset,text),video(asset,text,in),effect(camera,amount,text),voice(text,speed,temperature,gain,offset,in),subtitle(text,mode,size,color,offset,end),bgm/sfx(asset,gain,offset,in,text). 카메라 static/push/pull/pan-right/pan-left, 자막 plain/fade/reveal. 시간은 24fps 정수 프레임. 등록된 asset ID만 허용. 미확인 사실 창작 금지. JSON 배열만 응답.\n'
    else:text='선택 장면의 고해상도 이미지 또는 영상 후보 제작. 기존 원작/생성 재현 구분, 역사 고증, 색채·구도·움직임·캐릭터 일관성 고려. 원화의 내용과 글자 생성/변조 금지. 1920×1080 이상의 이미지 또는 장면 길이에 맞는 영상; 출처/사용권 명시. 아래 미디어 참조는 사용자가 명시적으로 첨부.\n'
    return jsonify(prompt=text+json.dumps({'scene':context,'selected_assets':opts},ensure_ascii=False,indent=2),revision=h)


@BP.post('/api/project/<pid>/review')
def review(pid):
    x=data();rid=x.get('render','');raw=x.get('text','')
    if not ID.fullmatch(rid) or not isinstance(raw,str) or not 1<=len(raw)<=100000:raise ValueError('Select rendered artifact and enter review')
    base=safe(store.folder(pid),'renders/'+rid,directory=True);r=json.loads(safe(base,'receipt.json').read_text(encoding='utf-8'));p=safe(base,'intro.mp4')
    if digest(p)!=r['sha256']:raise ValueError('Render integrity error')
    folder=safe(store.folder(pid),'reviews',directory=True,create=True);name=uuid.uuid4().hex[:12]+'.json'
    with (folder/name).open('x',encoding='utf-8') as f:json.dump({'render':rid,'sha256':r['sha256'],'revision':r['revision'],'reviewer':'human-relayed','raw':raw,'status':'UNADJUDICATED'},f,ensure_ascii=False,indent=2)
    return jsonify(saved=name)


@BP.get('/api/project/<pid>/workflows')
def workflows(pid):return jsonify(workflows=listed_graphs(store,pid))


@BP.post('/api/project/<pid>/workflows')
def register_workflow(pid):
    f=request.files.get('file')
    if not f or Path(f.filename or '').suffix.lower()!='.json':raise ValueError('Select trusted API-form JSON')
    with LOCK:
        current(pid,request.form.get('revision'))
        return jsonify(store_graph(store,pid,f.stream.read(MAX_GRAPH+1),request.form.get('trusted')=='yes'))


@BP.post('/api/project/<pid>/comfy')
def generate_comfy(pid):
    x=data()
    if not JOB_LOCK.acquire(False):raise ValueError('Another production job is running')
    try:
        d,h=current(pid,x.get('revision'));r=generate(store,pid,d,x.get('scene'),x.get('workflow'),x.get('mapping'),x.get('confirmed'));store.save(pid,d,h)
        return brief(pid,comfy_result=r)
    finally:JOB_LOCK.release()
