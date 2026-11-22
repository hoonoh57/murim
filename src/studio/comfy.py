"""Explicitly trusted local ComfyUI API graph adapter; M-VML never contains executable graph code.
The user selects an already tested graph and exact scalar input/output bindings.
No arbitrary remote URL, model installation, auto workflow substitution or shell invocation.
"""
import copy
import json
import mimetypes
import re
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from .workspace import safe, digest, hash_bytes, assets, asset_path, get_scene, track, register_asset, MAX_FILE
from .render import executables,media_info

MAX_GRAPH=2*1024*1024
BASE='http://127.0.0.1:8188'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise ValueError('ComfyUI redirects not permitted')

class LocalClient:
    def __init__(self):self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    def json(self,path,payload=None):
        req=urllib.request.Request(BASE+'/'+path,data=None if payload is None else json.dumps(payload).encode('utf-8'),headers={'Content-Type':'application/json'})
        with self.opener.open(req,timeout=25) as r:
            data=r.read(32*1024*1024+1)
        if len(data)>32*1024*1024:raise ValueError('ComfyUI response too large')
        return json.loads(data)
    def upload(self,path):
        path=Path(path);name='murim_'+uuid.uuid4().hex+path.suffix.lower();boundary=uuid.uuid4().hex
        if path.stat().st_size>MAX_FILE:raise ValueError('Uploaded file too large')
        typ=mimetypes.guess_type(name)[0] or 'application/octet-stream'
        data=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\nContent-Type: {typ}\r\n\r\n').encode()+path.read_bytes()+f'\r\n--{boundary}--\r\n'.encode()
        req=urllib.request.Request(BASE+'/upload/image',data=data,headers={'Content-Type':'multipart/form-data; boundary='+boundary},method='POST')
        with self.opener.open(req,timeout=120) as r:result=json.loads(r.read(65537))
        filename=result.get('name','');sub=result.get('subfolder','')
        if not filename or Path(filename).name!=filename or any(c in filename for c in ('/', '\\', ':')) or sub:raise ValueError('Unexpected ComfyUI upload location')
        return filename
    def queue(self,graph):
        # Do not contend for the existing GPU or disturb unrelated queue jobs.
        q=self.json('queue')
        if q.get('queue_running') or q.get('queue_pending'):raise ValueError('ComfyUI queue occupied; finish existing jobs first')
        result=self.json('prompt',{'prompt':graph,'client_id':uuid.uuid4().hex})
        pid=result.get('prompt_id','')
        if result.get('error') or result.get('node_errors') or not re.fullmatch(r'[a-fA-F0-9-]{16,64}',pid):raise ValueError('ComfyUI graph rejected: '+str(result)[:500])
        return pid
    def wait(self,pid,timeout=1800):
        start=time.monotonic()
        while time.monotonic()-start<timeout:
            r=self.json('history/'+pid).get(pid)
            if r:
                status=r.get('status',{})
                if status.get('status_str')=='error':raise RuntimeError('ComfyUI failed: '+str(status.get('messages',''))[-700:])
                if status.get('completed') is False:time.sleep(3);continue
                if r.get('outputs'):return r
                raise ValueError('ComfyUI returned no outputs')
            time.sleep(3)
        raise TimeoutError('ComfyUI timeout; job may still exist in its own queue. No retry submitted.')
    def fetch_video(self,item,dest):
        if item.get('type')!='output':raise ValueError('Only saved ComfyUI outputs are accepted')
        filename=item.get('filename','');sub=item.get('subfolder','')
        if not re.fullmatch(r'[^/\\:\r\n]+\.(mp4|webm|mov)',filename,re.I) or not isinstance(sub,str) or '\\' in sub or ':' in sub or sub.startswith('/') or '..' in Path(sub).parts:raise ValueError('Invalid output path')
        q=urllib.parse.urlencode({'filename':filename,'subfolder':sub,'type':'output'})
        with self.opener.open(BASE+'/view?'+q,timeout=180) as r,Path(dest).open('xb') as f:
            n=0
            while True:
                chunk=r.read(1024*1024)
                if not chunk:break
                n+=len(chunk)
                if n>MAX_FILE:raise ValueError('Output exceeds 256 MB limit')
                f.write(chunk)


def parse_graph(raw):
    if len(raw)>MAX_GRAPH:raise ValueError('API graph exceeds 2 MB')
    graph=json.loads(raw.decode('utf-8-sig'))
    if not isinstance(graph,dict) or not 1<=len(graph)<=300:raise ValueError('Expected ComfyUI API format, not UI workflow format')
    for k,node in graph.items():
        if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,64}',k) or not isinstance(node,dict) or not isinstance(node.get('class_type'),str) or not isinstance(node.get('inputs'),dict):raise ValueError('Expected API graph with node IDs, class_type and inputs')
        # This is not a sandbox for installed custom nodes: graph is supplied only by the local trusted user.
        if re.search(r'(^|[ _-])(shell|exec|pythoncode|httprequest|webhook|uploadto)([ _-]|$)',node['class_type'],re.I):raise ValueError('Execution/network control nodes are outside Studio scope')
        for key,v in node['inputs'].items():
            if isinstance(v,str) and re.match(r'^https?://',v,re.I):raise ValueError('External URL inputs are outside local workflow scope')
            if isinstance(v,list) and (len(v)!=2 or not isinstance(v[0],str) or v[0] not in graph or not isinstance(v[1],int)):raise ValueError('Unsupported connection input')
    return graph


def describe_graph(graph):
    return [{'id':k,'class_type':n['class_type'],'title':str(n.get('_meta',{}).get('title',''))[:100],
             'fields':[x for x,v in n['inputs'].items() if isinstance(v,str)]} for k,n in graph.items()]


def store_graph(store,pid,raw,trusted):
    if trusted is not True:raise ValueError('Confirm this is your trusted, already tested local API workflow')
    graph=parse_graph(raw); normalized=json.dumps(graph,ensure_ascii=False,sort_keys=True).encode('utf-8');gid=hash_bytes(normalized)
    folder=safe(store.folder(pid),'workflows',directory=True,create=True);p=folder/(gid+'.json')
    if not p.exists():
        with p.open('xb') as f:f.write(normalized)
    elif digest(safe(folder,p.name))!=gid:raise ValueError('Workflow hash mismatch')
    return dict(id=gid,nodes=describe_graph(graph))


def get_graph(store,pid,gid):
    if not isinstance(gid,str) or not re.fullmatch(r'[a-f0-9]{64}',gid):raise ValueError('Invalid workflow ID')
    p=safe(store.folder(pid),'workflows/'+gid+'.json');raw=p.read_bytes()
    if hash_bytes(raw)!=gid:raise ValueError('Workflow integrity mismatch')
    return parse_graph(raw)


def listed_graphs(store,pid):
    folder=store.folder(pid)/'workflows'
    if not folder.exists():return []
    folder=safe(store.folder(pid),'workflows',directory=True);out=[]
    for p in sorted(folder.iterdir()):
        if re.fullmatch(r'[a-f0-9]{64}\.json',p.name) and not p.is_symlink():
            graph=get_graph(store,pid,p.stem);out.append(dict(id=p.stem,nodes=describe_graph(graph)))
    return out


def resolve_binding(graph,binding,required):
    if not binding:
        if required:raise ValueError('Required workflow input mapping is missing')
        return None
    if not isinstance(binding,dict) or set(binding)!={'node','field'}:raise ValueError('Invalid binding')
    node=graph.get(binding['node']);field=binding['field']
    if node is None or not isinstance(node['inputs'].get(field),str):raise ValueError('Binding must be an existing scalar text input')
    return node['inputs'],field


def bind_inputs(graph,mapping,image_name,audio_name,motion):
    if not isinstance(mapping,dict) or set(mapping)!={'image','audio','motion','output'}:raise ValueError('Explicit mapping required')
    g=copy.deepcopy(graph);seen=set()
    for kind,required,value in (('image',True,image_name),('audio',bool(audio_name),audio_name),('motion',bool(motion),motion)):
        b=resolve_binding(g,mapping[kind],required)
        if b:
            ident=(mapping[kind]['node'],mapping[kind]['field'])
            if ident in seen:raise ValueError('Two roles cannot bind the same input')
            seen.add(ident)
            if value is None:raise ValueError('Audio binding requires an actual voice asset')
            b[0][b[1]]=value
    out=mapping['output']
    if not isinstance(out,str) or out not in g:raise ValueError('Choose saved video output node')
    if 'filename_prefix' in g[out]['inputs']:
        if not isinstance(g[out]['inputs']['filename_prefix'],str):raise ValueError('Output filename prefix must be scalar')
        g[out]['inputs']['filename_prefix']='murim_studio_'+hash_bytes(json.dumps([image_name,audio_name,motion]).encode())[:16]
    return g


def output_video(history,out):
    row=history.get('outputs',{}).get(out,{})
    candidates=[]
    for key in ('videos','gifs','images'):
        v=row.get(key,[])
        if not isinstance(v,list):continue
        candidates.extend(x for x in v if isinstance(x,dict) and x.get('type')=='output' and re.search(r'\.(mp4|webm|mov)$',x.get('filename',''),re.I))
    if len(candidates)!=1:raise ValueError('Selected output must contain exactly one saved video; no guessing among results')
    return candidates[0]


def generate(store,pid,doc,sid,workflow,mapping,confirmed,client=None):
    if confirmed is not True:raise ValueError('Confirm local graph execution')
    graph=get_graph(store,pid,workflow);s=get_scene(doc,sid);i=track(s,'image');v=track(s,'voice');vt=track(s,'video');aa=assets(doc)
    if i is None or not i.get('asset'):raise ValueError('Select an actual image first')
    motion=(vt.text or '') if vt is not None else ''
    audio_binding=bool(mapping.get('audio'))
    if audio_binding and (v is None or not v.get('asset')):raise ValueError('Lip-sync requires actual selected voice output')
    if audio_binding and (int(v.get('offset','0')) or int(v.get('in','0'))):raise ValueError('Lip-sync requires untrimmed voice at scene start')
    img=asset_path(store.root,aa[i.get('asset')]);wav=asset_path(store.root,aa[v.get('asset')]) if audio_binding else None
    # Validate explicit roles before uploading or submitting work.
    bind_inputs(graph,mapping,'image.png','audio.wav' if wav is not None else None,motion)
    client=client or LocalClient();known=client.json('object_info')
    missing=sorted({n['class_type'] for n in graph.values()}-set(known))
    if missing:raise ValueError('Installed ComfyUI nodes missing: '+', '.join(missing)[:300])
    job=safe(store.folder(pid),'comfy-jobs/'+uuid.uuid4().hex[:12],directory=True,create=True)
    image_name=client.upload(img);audio_name=client.upload(wav) if wav is not None else None
    g=bind_inputs(graph,mapping,image_name,audio_name,motion)
    request=dict(workflow=workflow,mapping=mapping,scene=sid,image_sha256=digest(img),voice_sha256=digest(wav) if wav else None,graph=g)
    (job/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2),encoding='utf-8')
    prompt_id=client.queue(g);(job/'submitted.json').write_text(json.dumps({'prompt_id':prompt_id}),encoding='utf-8')
    hist=client.wait(prompt_id);item=output_video(hist,mapping['output']);target=job/('video'+Path(item['filename']).suffix.lower());client.fetch_video(item,target)
    _,fp=executables(store.root);info=media_info(fp,target,'video');h=digest(target)
    result=dict(prompt_id=prompt_id,workflow=workflow,sha256=h,seconds=info['duration'],job=job.name,source_image=i.get('asset'),source_voice=v.get('asset') if audio_binding else None,status='CANDIDATE_REQUIRES_VIEWING')
    (job/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    aid=register_asset(doc,store.root,target,'video','ComfyUI '+sid+' · '+job.name,'Local ComfyUI workflow '+workflow+'; prompt '+prompt_id,'사용자 등록 로컬 워크플로; 출력 검수 및 권리 확인 필요')
    result['asset']=aid;result['fits']=info['duration']+.02>=int(s.get('frames'))/24
    return result
