"""M-VML Studio document and immutable revisions. No executable instructions in XML."""
import hashlib
import json
import math
import os
import re
import shutil
import stat
import threading
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

FPS = 24
TRACKS = ('image', 'video', 'effect', 'voice', 'subtitle', 'bgm', 'sfx')
AUDIO = ('voice', 'bgm', 'sfx')
ASSET_KIND = {'image':'image','video':'video','voice':'audio','bgm':'audio','sfx':'audio'}
CAMERAS = ('static','push','pull','pan-right','pan-left')
SUB_EFFECTS = ('plain','fade','reveal')
ID = re.compile(r'[a-f0-9]{12}')
LOCK = threading.RLock()
MAX_FILE = 256 * 1024 * 1024


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def safe(root, relative, *, directory=False, create=False):
    """Only regular files/directories below the explicitly selected root; no reparse traversal."""
    root = Path(root).resolve()
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(p in ('..', '.') or ':' in p for p in rel.parts):
        raise ValueError('Unsafe relative path')
    p = root
    for i, name in enumerate(rel.parts):
        p = p / name
        is_dir = i < len(rel.parts)-1 or directory
        if p.is_symlink(): raise ValueError('Link forbidden')
        if p.exists():
            if getattr(p.lstat(),'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0):
                raise ValueError('Reparse point forbidden')
            if is_dir != p.is_dir(): raise ValueError('Path kind mismatch')
            if not is_dir and not p.is_file(): raise ValueError('File required')
        elif is_dir and create:
            p.mkdir()
        elif not is_dir and create:
            pass
        else:
            raise FileNotFoundError(str(rel))
        if not p.resolve().is_relative_to(root): raise ValueError('Path escapes workspace')
    return p


def xml_bytes(doc):
    return ET.tostring(doc,encoding='utf-8',xml_declaration=True)


def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_xml(path):
    data = path.read_bytes()
    if len(data)>1_000_000 or re.search(rb'<!\s*(DOCTYPE|ENTITY)',data,re.I): raise ValueError('Unsafe XML')
    return ET.fromstring(data)


def numeric(v, low, high, integer=False):
    if isinstance(v,bool): raise ValueError('Numeric value required')
    n = int(v) if integer else float(v)
    if not math.isfinite(n) or not low<=n<=high or (integer and float(v)!=n): raise ValueError('Out of range')
    return str(n)


def new_scene(frames=144, title='새 장면'):
    s=ET.Element('scene',id=uuid.uuid4().hex[:12],frames=str(frames),title=title)
    return s


def new_doc(title):
    d=ET.Element('mvml',version='studio-1',title=title,fps='24',status='DRAFT')
    ET.SubElement(d,'assets'); ET.SubElement(d,'timeline').append(new_scene())
    return d


def assets(doc): return {a.get('id'):a for a in doc.find('assets')}


def scenes(doc): return list(doc.find('timeline'))


def get_scene(doc, sid):
    s=next((x for x in scenes(doc) if x.get('id')==sid),None)
    if s is None: raise ValueError('Unknown scene')
    return s


def track(s, kind): return s.find("track[@kind='%s']" % kind)


def asset_path(root, a, verify=True):
    p=safe(root,a.get('path'))
    if not p.is_relative_to(Path(root).resolve()/'outputs'): raise ValueError('Only outputs assets allowed')
    if verify and digest(p)!=a.get('sha256'): raise ValueError('Asset hash mismatch: '+a.get('id',''))
    return p


def register_asset(doc, root, p, kind, label, source, rights):
    if kind not in ('image','video','audio') or not source.strip() or not rights.strip(): raise ValueError('Asset provenance required')
    root=Path(root).resolve(); p=Path(p).resolve()
    rel=p.relative_to(root).as_posix()
    p=safe(root,rel)
    if not p.is_relative_to(root/'outputs'): raise ValueError('Only output assets permitted')
    h=digest(p)
    # Same bytes but differing provenance are distinct immutable records.
    aid='A'+hash_bytes(json.dumps([h,kind,source,rights],ensure_ascii=False).encode())[:24]
    existing=assets(doc).get(aid)
    if existing is None:
        ET.SubElement(doc.find('assets'),'asset',id=aid,kind=kind,path=rel,sha256=h,label=label[:160],source=source[:1000],rights=rights[:1000])
    return aid


def validate(doc):
    if doc.tag!='mvml' or doc.get('version')!='studio-1' or doc.get('fps')!='24' or not 1<=len(doc.get('title',''))<=120: raise ValueError('Invalid M-VML header')
    if [x.tag for x in doc]!=['assets','timeline']: raise ValueError('Invalid M-VML sections')
    aa=assets(doc)
    if len(aa)!=len(doc.find('assets')): raise ValueError('Duplicate assets')
    for a in aa.values():
        if a.tag!='asset' or not re.fullmatch(r'A[0-9a-f]{24}',a.get('id','')) or a.get('kind') not in ('image','video','audio') or not re.fullmatch(r'[0-9a-f]{64}',a.get('sha256','')): raise ValueError('Invalid asset')
    ss=scenes(doc)
    if not 1<=len(ss)<=200 or len({s.get('id') for s in ss})!=len(ss): raise ValueError('Invalid scene list')
    total=0
    for s in ss:
        if s.tag!='scene' or not ID.fullmatch(s.get('id','')) or len(s.get('title',''))>160: raise ValueError('Invalid scene')
        frames=int(numeric(s.get('frames'),24,1440,True)); total+=frames
        kinds=[t.get('kind') for t in s]
        if any(k not in TRACKS for k in kinds) or len(kinds)!=len(set(kinds)): raise ValueError('Duplicate/unknown track')
        for t in s:
            if t.tag!='track' or len(t): raise ValueError('Invalid track')
            k=t.get('kind'); aid=t.get('asset','')
            if aid and (aid not in aa or ASSET_KIND.get(k)!=aa[aid].get('kind')): raise ValueError('Asset kind mismatch')
            if len(t.text or '')>4000: raise ValueError('Track text too long')
            if k in AUDIO:
                numeric(t.get('gain','0' if k=='voice' else '-18'),-60,6)
                numeric(t.get('offset','0'),0,frames-1,True)
                numeric(t.get('in','0'),0,144000,True)
            if k=='video': numeric(t.get('in','0'),0,144000,True)
            if k=='voice':
                numeric(t.get('speed','0.92'),0.75,1.25); numeric(t.get('temperature','0.65'),0.2,1.2)
                if aid and t.get('bound')!=voice_key(t): raise ValueError('Stale voice binding')
            if k=='effect' and t.get('camera','static') not in CAMERAS: raise ValueError('Unknown camera')
            if k=='effect': numeric(t.get('amount','0.12'),0,0.4)
            if k=='subtitle':
                if t.get('mode','plain') not in SUB_EFFECTS: raise ValueError('Unknown subtitle effect')
                numeric(t.get('size','48'),30,72,True)
                if not re.fullmatch(r'#[0-9a-fA-F]{6}',t.get('color','#ffffff')): raise ValueError('Invalid subtitle color')
                begin=int(numeric(t.get('offset','0'),0,frames-1,True))
                end=int(numeric(t.get('end',str(frames)),1,frames,True))
                if end<=begin: raise ValueError('Subtitle timing invalid')
    if total>24*3600: raise ValueError('Timeline exceeds one hour')
    return doc


def voice_key(t):
    if t is None: return ''
    return hash_bytes(json.dumps([t.text or '',t.get('speed','0.92'),t.get('temperature','0.65'),t.get('profile','narrator-v2')],ensure_ascii=False).encode())


def patch(doc, ops):
    """Typed patch contract; no paths, code, arbitrary XML attributes or whole-document replacements."""
    if not isinstance(ops,list) or not 1<=len(ops)<=30: raise ValueError('1–30 operations required')
    d=ET.fromstring(xml_bytes(doc)); before={s.get('id'):ET.tostring(s) for s in scenes(d)}
    for op in ops:
        if not isinstance(op,dict): raise ValueError('Object required')
        action=op.get('op')
        if action=='add_scene':
            if set(op)-{'op','frames','title','after'}: raise ValueError('Unknown field')
            s=new_scene(int(numeric(op.get('frames',144),24,1440,True)),str(op.get('title','새 장면'))[:160])
            tl=d.find('timeline'); after=op.get('after')
            tl.insert(list(tl).index(get_scene(d,after))+1,s) if after else tl.append(s)
            continue
        if not ID.fullmatch(str(op.get('scene',''))): raise ValueError('Scene id required')
        s=get_scene(d,op['scene'])
        if action=='delete_scene':
            if set(op)!={'op','scene'}: raise ValueError('Unknown field')
            d.find('timeline').remove(s); continue
        if action=='move_scene':
            if set(op)!={'op','scene','index'}: raise ValueError('Unknown field')
            tl=d.find('timeline'); index=int(numeric(op['index'],0,len(tl)-1,True)); tl.remove(s); tl.insert(index,s); continue
        if action=='scene':
            if set(op)-{'op','scene','title','frames'}: raise ValueError('Unknown field')
            if 'title' in op: s.set('title',str(op['title'])[:160])
            if 'frames' in op: s.set('frames',numeric(op['frames'],24,1440,True))
            continue
        k=op.get('track')
        if k not in TRACKS: raise ValueError('Unknown track')
        t=track(s,k)
        if action=='remove':
            if set(op)!={'op','scene','track'}: raise ValueError('Unknown field')
            if t is not None: s.remove(t)
            if k in ('voice','image'):
                vv=track(s,'video')
                if vv is not None and vv.get('lip-bound'): vv.attrib.pop('asset',None);vv.attrib.pop('lip-bound',None)
            continue
        if action!='set' or set(op)!={'op','scene','track','values'} or not isinstance(op['values'],dict): raise ValueError('Unknown operation')
        v=op['values']; allowed={
            'image':{'asset','text'}, 'video':{'asset','text','in','lip_sync'}, 'effect':{'camera','amount','text'},
            'voice':{'asset','text','gain','offset','in','speed','temperature'},
            'subtitle':{'text','mode','size','color','offset','end'}, 'bgm':{'asset','gain','offset','in','text'},'sfx':{'asset','gain','offset','in','text'}}[k]
        if set(v)-allowed: raise ValueError('Unknown track field')
        if t is None: t=ET.SubElement(s,'track',kind=k)
        oldkey=voice_key(t) if k=='voice' else ''
        oldasset=t.get('asset',''); oldtext=t.text or ''
        for name,value in v.items():
            if not isinstance(value,(str,int,float)) or isinstance(value,bool): raise ValueError('Invalid track value')
            if name=='text': t.text=str(value)
            elif name=='lip_sync':
                if value not in ('yes','no'): raise ValueError('lip_sync must be yes/no')
            else: t.set(name,str(value))
        if k=='voice':
            if 'asset' in v and v['asset'] and v['asset']!=oldasset:
                t.set('profile','manual'); t.set('bound',voice_key(t)); t.set('origin','MANUAL_IMPORT')
                vid=track(s,'video')
                if vid is not None and vid.get('lip-bound'): vid.attrib.pop('asset',None);vid.attrib.pop('lip-bound',None)
            elif oldkey!=voice_key(t) or ('asset' in v and not v['asset'] and oldasset):
                audio=t.get('asset'); t.attrib.pop('asset',None); t.attrib.pop('bound',None)
                if 'text' in v:
                    # Subtitle text follows the script only if it previously matched. No fake word timing.
                    sub=track(s,'subtitle'); old_scene=get_scene(doc,op['scene']); old_voice=track(old_scene,'voice')
                    if sub is not None and old_voice is not None and (sub.text or '')==(old_voice.text or ''): sub.text=t.text
                vid=track(s,'video')
                if vid is not None and vid.get('lip-bound'):
                    vid.attrib.pop('asset',None);vid.attrib.pop('lip-bound',None)
        if k=='video':
            if 'text' in v and t.text!=oldtext and 'asset' not in v:
                t.attrib.pop('asset',None);t.attrib.pop('lip-bound',None)
            if v.get('lip_sync')=='yes':
                vt=track(s,'voice');it=track(s,'image')
                if not t.get('asset') or vt is None or not vt.get('asset'): raise ValueError('Lip-sync binding requires selected real video and voice')
                t.set('lip-bound',hash_bytes(json.dumps([t.get('asset'),vt.get('asset'),it.get('asset') if it is not None else '',t.text or ''],ensure_ascii=False).encode()))
            elif v.get('lip_sync')=='no' or ('asset' in v and v['asset']!=oldasset): t.attrib.pop('lip-bound',None)
        if k=='image' and 'asset' in v and v['asset']!=oldasset:
            vid=track(s,'video')
            if vid is not None and vid.get('lip-bound'): vid.attrib.pop('asset',None);vid.attrib.pop('lip-bound',None)
    validate(d)
    after={s.get('id'):ET.tostring(s) for s in scenes(d)}
    return d,sorted(k for k in before.keys()|after.keys() if before.get(k)!=after.get(k))


def state(doc):
    validate(doc); aa=assets(doc); result=[]; cursor=0
    for s in scenes(doc):
        n=int(s.get('frames')); tt={t.get('kind'):dict(t.attrib,text=t.text or '') for t in s}
        pending=[]
        if not any(tt.get(k,{}).get('asset') for k in ('image','video')): pending.append('visual')
        if tt.get('voice',{}).get('text') and not tt['voice'].get('asset'): pending.append('voice')
        if tt.get('video',{}).get('text') and not tt['video'].get('asset'): pending.append('motion')
        result.append(dict(id=s.get('id'),title=s.get('title',''),start=cursor,frames=n,tracks=tt,pending=pending));cursor+=n
    return dict(title=doc.get('title'),fps=FPS,frames=cursor,scenes=result,assets=[{k:v for k,v in a.attrib.items() if k!='path'} for a in aa.values()])


class Store:
    def __init__(self, root): self.root=Path(root).resolve()
    def folder(self,pid,create=False):
        if not ID.fullmatch(pid): raise ValueError('Invalid project id')
        return safe(self.root,'outputs/studio/'+pid,directory=True,create=create)
    def revisions(self,pid):
        base=self.folder(pid); return sorted(p for p in base.glob('*.mvml.xml') if re.fullmatch(r'\d{8}-[a-f0-9]{64}\.mvml\.xml',p.name) and p.is_file() and not p.is_symlink())
    def load(self,pid,rev=None):
        rr=self.revisions(pid)
        if not rr: raise ValueError('No revisions')
        p=rr[-1] if rev is None else next((p for p in rr if p.name[9:73]==rev),None)
        if p is None: raise ValueError('Unknown revision')
        p=safe(self.folder(pid),p.name); raw=p.read_bytes(); h=hash_bytes(raw)
        if h!=p.name[9:73]: raise ValueError('Revision hash mismatch')
        return validate(read_xml(p)),h
    def save(self,pid,doc,expected=None):
        with LOCK:
            folder=self.folder(pid,True); rr=self.revisions(pid)
            if rr:
                _,head=self.load(pid)
                if expected!=head: raise ValueError('Revision conflict: reload current document')
            elif expected is not None: raise ValueError('Revision conflict')
            validate(doc); data=xml_bytes(doc); h=hash_bytes(data)
            if rr and h==head: return h
            n=int(rr[-1].name[:8])+1 if rr else 1
            p=folder/f'{n:08d}-{h}.mvml.xml'; tmp=folder/('pending-'+uuid.uuid4().hex)
            with tmp.open('xb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
            tmp.rename(p); return h
    def create(self,title):
        pid=uuid.uuid4().hex[:12]; doc=new_doc(title); self.save(pid,doc); return pid
    def describe(self,pid):
        d,h=self.load(pid); return dict(state(d),id=pid,revision=h,revisions=[p.name[9:73] for p in self.revisions(pid)])
    def list_projects(self):
        p=self.root/'outputs/studio'
        if not p.exists(): return []
        p=safe(self.root,'outputs/studio',directory=True)
        result=[]
        for q in sorted(p.iterdir()):
            if ID.fullmatch(q.name) and q.is_dir() and not q.is_symlink():
                try:
                    d,h=self.load(q.name); result.append(dict(id=q.name,title=d.get('title'),revision=h))
                except (ValueError,OSError): continue
        return result
    def runs(self):
        p=self.root/'outputs/sehando/intro/v0.2'
        if not p.exists(): return []
        p=safe(self.root,'outputs/sehando/intro/v0.2',directory=True)
        return [q.name for q in sorted(p.iterdir()) if ID.fullmatch(q.name) and not q.is_symlink() and (q/'receipt.json').is_file() and (q/'intro.mp4').is_file()]
    def import_run(self,run):
        if not ID.fullmatch(run): raise ValueError('Invalid run')
        with LOCK:
            base=safe(self.root,'outputs/sehando/intro/v0.2/'+run,directory=True)
            rec=json.loads(safe(base,'receipt.json').read_text(encoding='utf-8'))
            if digest(safe(base,'intro.mp4'))!=rec['video_sha256'] or digest(safe(base,'source.mvml.xml'))!=rec['source_sha256']: raise ValueError('Original receipt hash mismatch')
            src=read_xml(safe(base,'source.mvml.xml'))
            if src.get('version')!='0.2-review': raise ValueError('Unsupported import')
            d=new_doc('세한도 · '+run); d.set('baseline',run); tl=d.find('timeline'); tl.clear()
            index={}
            for key,a in rec['assets'].items():
                p=safe(base,a['file'])
                if digest(p)!=a['sha256']: raise ValueError('Original image hash mismatch')
                index[key]=register_asset(d,self.root,p,'image',a['label'],a['source'],a['rights'])
            for row in rec['shots']:
                sid=row['id']; n=int(row['seconds'])*FPS
                if not re.fullmatch(r'S\d{2}',sid): raise ValueError('Invalid original shot')
                s=new_scene(n,row.get('heading') or sid); s.set('original-id',sid); tl.append(s)
                ET.SubElement(s,'track',kind='image',asset=index[row['asset']],framing=row['framing'])
                ET.SubElement(s,'track',kind='effect',camera='static',amount='0')
                voice=safe(base,sid+'.wav')
                if digest(voice)!=row['voice_sha256']: raise ValueError('Original voice hash mismatch')
                aid=register_asset(d,self.root,voice,'audio',sid+' 기존 SAPI','v0.2 original run '+run,'기존 평가용 음성; 게시 승인 미확인')
                t=ET.SubElement(s,'track',kind='voice',asset=aid,profile='legacy-sapi',origin='V02_SAPI',gain='0');t.text=row['text'];t.set('bound',voice_key(t))
                ET.SubElement(s,'track',kind='subtitle',mode='plain',size='39',color='#242a25').text=row['text']
                # Retain immutable original per-scene output for exact unchanged clips.
                clip=safe(base,sid+'.mp4'); s.set('baseline-clip',clip.relative_to(self.root).as_posix());s.set('baseline-sha',digest(clip));s.set('baseline-state',scene_fingerprint(s))
            pid=uuid.uuid4().hex[:12];self.save(pid,d);return pid


def scene_fingerprint(s):
    # The baseline comparison excludes only provenance markers, not editable fields.
    c=ET.fromstring(ET.tostring(s));
    for k in ('baseline-state','baseline-clip','baseline-sha'): c.attrib.pop(k,None)
    return hash_bytes(ET.tostring(c,encoding='utf-8'))
