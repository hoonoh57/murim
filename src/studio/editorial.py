"""Project-scoped immutable pre-production plan, review and approval ledger."""
import json
import os
import re
import uuid
import xml.etree.ElementTree as ET
from .workspace import (ID, LOCK, safe, hash_bytes, state, xml_bytes, validate, track, scenes)

FIELDS = ('purpose','audience','policy','story','facts','visual','audio','ending')
AXES = ('viewer_value','narrative','historical_evidence','visual_design','audio_design','coherence')
SCENE_FIELDS = ('id','title','frames','narration','visual','motion','sound','facts','subtitle')
KNOWN = [
    ('GEMINI-01','1842년 간찰을 1844년 책 도착 장면에 배치한 역사 연대 오류'),
    ('GEMINI-02','반복 정지화면과 시각적 변화 부족'),
    ('GEMINI-03','SAPI 기계음 내레이션'),
    ('GEMINI-04','미완결 결말')]
GUIDE = {
    'purpose':'작품의 중심 질문과 시청 보상', 'audience':'목표 시청자와 진입 장벽',
    'policy':'제작 방침·차별화·금지사항', 'story':'전체 시나리오 및 서사 구조',
    'facts':'사료·사실과 재연의 구분 및 출처', 'visual':'미술·영상·첫 3초 연출 방침',
    'audio':'성우·음향·발화 및 자막 방침', 'ending':'결말과 여운'}
MAX_TEXT=250000

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')

def key(value):
    return hash_bytes(canonical(value))

def string(value, limit=MAX_TEXT, empty=False, label='내용'):
    if not isinstance(value,str): raise ValueError(label+' 항목이 없거나 문장이 아닙니다.')
    if len(value)>limit: raise ValueError(label+' 길이 초과: '+str(len(value))+' / '+str(limit)+'자')
    if not empty and not value.strip(): raise ValueError(label+' 항목이 비어 있습니다.')
    return value

def relay_object(raw):
    """Accept a whole human-relayed answer, preserving prose outside the machine block."""
    raw=string(raw,1200000)
    try: obj=json.loads(raw)
    except json.JSONDecodeError:
        blocks=re.findall(r"```(?:json|murim)[ \t]*\r?\n(.*?)\r?\n```",raw,re.S|re.I)
        if len(blocks)!=1: raise ValueError('응답 전체를 받았지만 제작 정보가 없습니다. 응답 정리 요청을 복사해 AI에게 전달하고 새 답변 전체를 붙여 넣으세요.')
        try: obj=json.loads(blocks[0])
        except json.JSONDecodeError as exc: raise ValueError('AI 응답이 불완전합니다. 응답 정리 요청으로 다시 받아 주세요.') from exc
    if not isinstance(obj,dict): raise ValueError('AI 응답 형식이 올바르지 않습니다.')
    return obj

def baseline(store,pid):
    doc,rev=store.load(pid)
    # Original timeline is the first immutable revision, not the last edited draft.
    original=store.revisions(pid)[0].name[9:73]
    doc,_=store.load(pid,original)
    s=state(doc)
    plan={k:'' for k in FIELDS}
    plan['scenes']=[]
    registered={a['id']:a for a in s['assets']}
    for r in s['scenes']:
        t=r['tracks']
        def source(kind):
            a=registered.get(t.get(kind,{}).get('asset'))
            return ' / '.join(a.get(k,'') for k in ('label','source','rights')) if a else ''
        visual=' / '.join(x for x in (source('image'),t.get('image',{}).get('text',''),source('video'),t.get('effect',{}).get('camera','')) if x)
        sound=' / '.join(x for x in (source('voice'),source('bgm'),source('sfx')) if x)
        plan['scenes'].append(dict(id=r['id'],title=r['title'],frames=r['frames'],
            narration=t.get('voice',{}).get('text',''),visual=visual,
            motion=t.get('video',{}).get('text',''),sound=sound,facts=source('image'),
            subtitle=t.get('subtitle',{}).get('text','')))
    plan['story']='\n\n'.join(r['title']+'\n'+r['narration'] for r in plan['scenes'])
    known=doc.get('baseline')=='8a9f3c33d62e'
    return dict(plan=plan,source_revision=original,known_failed=known,
        prior_summary='사용자 전달 Gemini 평가 38.5/100; 기록된 요약이며 원문 아님' if known else '',
        issues=[dict(id=i,description=d,origin='prior-summary') for i,d in KNOWN] if known else [])

def plan_check(p,complete=True):
    if not isinstance(p,dict) or set(p)!=set(FIELDS)|{'scenes'}: raise ValueError('제작안 필드 불일치')
    for k in FIELDS: string(p[k],40000,empty=not complete,label=GUIDE[k])
    rows=p['scenes']
    if not isinstance(rows,list) or not 1<=len(rows)<=200: raise ValueError('장면 1~200개 필요')
    ids=set()
    for number,r in enumerate(rows,1):
        if not isinstance(r,dict) or set(r)!=set(SCENE_FIELDS): raise ValueError('장면 필드 불일치')
        if not isinstance(r['id'],str) or not ID.fullmatch(r['id']) or r['id'] in ids: raise ValueError('장면 ID 오류')
        ids.add(r['id'])
        if type(r['frames']) is not int or not 24<=r['frames']<=1440: raise ValueError('장면 길이 1~60초 필요')
        for k in ('title','narration','visual','sound','facts','subtitle'): string(r[k],160 if k=='title' else 4000,empty=not complete or k in ('narration','subtitle'),label=f'{number}번 장면 {k}')
        string(r['motion'],4000,empty=True,label=f'{number}번 장면 동작')
    if sum(r['frames'] for r in rows)>24*3600: raise ValueError('전체 1시간 초과')
    if len(canonical(p))>900000: raise ValueError('제작안 용량 초과')
    return p

def plan_payload(v,data,relay=None):
    plan=plan_check(data.get('plan'),complete=relay is not None); rev=key(plan)
    if any(p['revision']==rev for p in v['versions']): raise ValueError('같은 제작안은 다시 제출할 수 없습니다. 실제 내용을 수정하세요.')
    payload=dict(revision=rev,plan=plan,note=string(data.get('note'),10000,label='원본 대비 수정 근거'),parent=v['latest']['revision'])
    if relay is not None:
        payload.update(raw_response=relay[0],instruction=data['instruction'])
        if v['prior_raw'] and not v['prior_indexed']:
            descriptions=relay[1].get('prior_issues')
            if not isinstance(descriptions,list) or not 1<=len(descriptions)<=100: raise ValueError('AI가 기존 비평의 전체 결함 목록을 정리하지 않았습니다.')
            payload['prior_issues']=[dict(id='PRIOR-%03d'%(j+1),description=string(x,4000,label='기존 비평 문제'),origin='human-relayed-ai-extraction') for j,x in enumerate(descriptions)]
    return payload

def relay_plan_payload(v,raw,instruction):
    relay=relay_object(raw)
    if relay.get('parent')!=v['latest']['revision']: raise ValueError('현재 버전에 대한 수정 응답이 아닙니다. 현재 수정 요청을 다시 복사하세요.')
    return plan_payload(v,dict(plan=relay.get('plan'),note=relay.get('note'),instruction=instruction),(raw,relay))

class Editorial:
    def __init__(self,store,pid):
        self.store,self.pid=store,pid
    def events(self):
        base=self.store.folder(self.pid)
        if not (base/'preproduction').exists(): return []
        base=safe(base,'preproduction',directory=True)
        out=[]
        for p in sorted(base.glob('*.json')):
            m=re.fullmatch(r'(\d{8})-([0-9a-f]{64})\.json',p.name)
            if not m or int(m.group(1))!=len(out)+1: raise ValueError('제작안 이력 순서 오류')
            p=safe(base,p.name); raw=p.read_bytes()
            if hash_bytes(raw)!=m.group(2): raise ValueError('제작안 이력 무결성 오류')
            e=json.loads(raw)
            if e.get('previous')!=(out[-1]['hash'] if out else ''): raise ValueError('제작안 이력 연결 오류')
            out.append(dict(e,hash=m.group(2)))
        return out
    def append(self,events,kind,data):
        base=safe(self.store.folder(self.pid),'preproduction',directory=True,create=True)
        raw=canonical(dict(kind=kind,data=data,previous=events[-1]['hash'] if events else ''))
        h=hash_bytes(raw)
        path=base/('%08d-%s.json'%(len(events)+1,h))
        temp=base/('pending-'+uuid.uuid4().hex)
        with temp.open('xb') as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        temp.rename(path)
    def view(self,events=None):
        events=self.events() if events is None else events
        orig=events[0]['data'] if events else baseline(self.store,self.pid)
        plans=[dict(revision=key(orig['plan']),plan=orig['plan'],note='기존 원본 (미승인)',original=True)]
        all_issues={i['id']:i for i in orig['issues']}
        issues=dict(all_issues)
        raw_prior=None; prior_indexed=False; review=None; approved=None; feedback=[]; pending_reply=None
        for e in events[1:]:
            d=e['data']
            if e['kind']=='prior_capture':
                raw_prior=d['raw']
            elif e['kind']=='prior_review':
                raw_prior=d['raw']; prior_indexed=True
                all_issues.update({i['id']:i for i in d['issues']}); issues=dict(all_issues)
            elif e['kind']=='relay_rejected':
                pending_reply=d
            elif e['kind']=='plan':
                plans.append(dict(d,original=False)); review=None; approved=None; pending_reply=None
                if d.get('prior_issues'):
                    all_issues.update({i['id']:i for i in d['prior_issues']}); prior_indexed=True
                issues=dict(all_issues) # Revised plans must recheck prior resolved issues too.
            elif e['kind']=='review':
                review=d
                plans[-1]['review']=d
                # Only a passing re-review of the specific issue closes it. Raw evidence is retained.
                for i in d['closed']: issues.pop(i,None)
                all_issues.update({i['id']:i for i in d['issues']})
                issues.update({i['id']:i for i in d['issues']})
            elif e['kind']=='approval':
                approved=d; plans[-1]['approval']=d
            elif e['kind']=='feedback':
                feedback.append(d); all_issues.update({i['id']:i for i in d['issues']}); issues.update({i['id']:i for i in d['issues']}); approved=None
        latest=plans[-1]
        try: plan_check(latest['plan']); ready=not latest['original']
        except ValueError: ready=False
        ok=bool(approved and review and review['pass'] and not issues and approved['revision']==latest['revision'])
        doc,mvrev=self.store.load(self.pid)
        if ok:
            ok=doc.get('editorial-plan')==latest['revision'] and signature(doc)==signature_plan(latest['plan'])
        return dict(token=events[-1]['hash'] if events else '', original=orig, versions=plans,
            latest=latest,issues=list(issues.values()),prior_raw=raw_prior,prior_indexed=prior_indexed,all_issues=list(all_issues.values()),review=review,feedback=feedback,pending_reply=pending_reply,
            approved=ok,approval=approved,mvml_revision=mvrev,ready=ready,
            status='APPROVED' if ok else 'HOLD' if approved else 'REWORK_REQUIRED' if review and (issues or not review['pass']) else 'APPROVAL_REQUIRED' if review else 'HOLD')
    def mutate(self,token,action,data):
        with LOCK:
            ev=self.events(); v=self.view(ev)
            if token!=v['token']: raise ValueError('제작안 리비전 충돌: 다시 읽으세요')
            if action=='prior_capture':
                if v['prior_raw'] is not None or v['review'] is not None: raise ValueError('기존 비평 원문은 이미 등록되었습니다.')
                payload=dict(raw=string(data.get('raw')))
            elif action=='prior_review':
                if v['prior_raw'] is not None or any(e['kind']=='review' for e in ev): raise ValueError('기존 비평은 재심사 전에 1회 등록')
                raw=string(data.get('raw')); descriptions=data.get('issues')
                if not isinstance(descriptions,list) or not descriptions or len(descriptions)>100: raise ValueError('원문에서 확인한 문제 목록 필요')
                payload=dict(raw=raw,issues=[dict(id='PRIOR-%03d'%(j+1),description=string(x,4000),origin='human-relayed') for j,x in enumerate(descriptions)])
            elif action=='feedback':
                raw=string(data.get('raw')); source=data.get('source'); descriptions=data.get('issues')
                if not isinstance(source,dict) or not ID.fullmatch(str(source.get('render',''))) or not re.fullmatch(r'[0-9a-f]{64}',str(source.get('sha256',''))) or not re.fullmatch(r'[0-9a-f]{64}',str(source.get('revision',''))): raise ValueError('실제 렌더 증거 필요')
                if not isinstance(descriptions,list) or not descriptions or len(descriptions)>100: raise ValueError('구조적 결함 목록 필요')
                if any(f['source']['render']==source['render'] and f['raw']==raw for f in v['feedback']): raise ValueError('이미 등록된 제작 후 비평')
                prefix='POST-'+key([source,raw])[:12]
                payload=dict(raw=raw,source=source,issues=[dict(id=prefix+'-%03d'%(j+1),description=string(x,4000),origin='actual-render-feedback') for j,x in enumerate(descriptions)])
            elif action=='plan':
                payload=plan_payload(v,data)
            elif action in ('relay_plan','relay_receive'):
                raw=string(data.get('raw'),1200000,label='AI 답변')
                instruction=string(data.get('instruction',''),10000,empty=True,label='감독 지시')
                try:
                    payload=relay_plan_payload(v,raw,instruction)
                    action='plan'
                except ValueError as exc:
                    if action=='relay_plan': raise
                    # Preserve the actual answer independently from the production plan.
                    # No valid revision, score, or approval is created by a rejected answer.
                    payload=dict(raw=raw,instruction=instruction,parent=v['latest']['revision'],error=str(exc))
                    action='relay_rejected'
                    if v.get('pending_reply')==payload: return v
            elif action=='review':
                if v['latest']['original'] or v['review'] is not None: raise ValueError('수정 제작안마다 독립 심사 1회; 재시도는 새 수정본에서')
                plan_check(v['latest']['plan'])
                if (v['original']['known_failed'] or v['prior_raw']) and not v['prior_indexed']: raise ValueError('기존 Gemini 비평 원문 및 문제 목록을 먼저 등록하세요')
                raw=string(data.get('raw'),1200000); reviewer=string(data.get('reviewer'),200)
                r=relay_object(raw)
                if not isinstance(r,dict) or r.get('revision')!=v['latest']['revision']: raise ValueError('심사 대상 제작안 해시 불일치')
                scores=r.get('scores')
                if not isinstance(scores,dict) or set(scores)!=set(AXES): raise ValueError('6개 사전 제작 심사 축 필요')
                for x in scores.values():
                    if x is not None and (type(x) not in (int,float) or not 0<=x<=10): raise ValueError('심사 점수 범위 오류')
                string(r.get('evidence'),40000)
                faults=r.get('issues'); res=r.get('resolutions')
                if not isinstance(faults,list) or len(faults)>100 or not isinstance(res,list): raise ValueError('문제 및 재검증 목록 필요')
                known={i['id'] for i in v['issues']}; closed=[]; seen=set()
                for x in res:
                    if not isinstance(x,dict) or x.get('id') not in known or x['id'] in seen or type(x.get('resolved')) is not bool: raise ValueError('재검증 문제 ID 오류')
                    seen.add(x['id']); string(x.get('evidence'),10000)
                    if x['resolved']: closed.append(x['id'])
                if seen!=known: raise ValueError('모든 기존 문제를 명시적으로 재검증하세요')
                new=[dict(id=v['latest']['revision'][:12]+'-%03d'%(j+1),description=string(x,4000),origin='external-review') for j,x in enumerate(faults)]
                complete=all(x is not None for x in scores.values())
                total=sum(scores.values())/len(AXES)*10 if complete else None
                passed=bool(complete and total>=95 and min(scores.values())>=9 and not new and set(closed)==known and r.get('verdict')=='PASS')
                # A rejected revision may not close old issues; carry them forward for the next review.
                payload=dict(revision=v['latest']['revision'],raw=raw,reviewer=reviewer,scores=scores,total=total,issues=new,closed=closed if passed else [],resolutions=res,evidence=r['evidence'],pass_=passed)
                payload['pass']=payload.pop('pass_')
            elif action=='approval':
                if v['approved'] or not v['review'] or not v['review']['pass'] or v['issues'] or data.get('confirmed') is not True:
                    raise ValueError('독립 재심사 통과 및 모든 결함 해소·인간 승인 필요')
                if data.get('mvml_revision')!=v['mvml_revision']: raise ValueError('M-VML 리비전 충돌')
                approver=string(data.get('approver'),200)
                plan_check(v['latest']['plan'])
                doc,h=self.store.load(self.pid)
                compiled=materialize(doc,v['latest'])
                if len(xml_bytes(compiled))>1000000: raise ValueError('승인 타임라인 용량 초과')
                target=self.store.save(self.pid,compiled,h)
                payload=dict(revision=v['latest']['revision'],mvml_revision=target,reviewer=approver)
            else: raise ValueError('Unknown pre-production action')
            if not ev:
                self.append(ev,'original',v['original']); ev=self.events()
            self.append(ev,action,payload)
            return self.view()
    def require(self,doc=None):
        v=self.view()
        if not v['approved']: raise ValueError('제작 보류: 00 사전 제작에서 수정안 재심사·인간 승인을 완료하세요')
        if doc is not None and (doc.get('editorial-plan')!=v['latest']['revision'] or signature(doc)!=signature_plan(v['latest']['plan'])):
            raise ValueError('승인된 시나리오 변경은 사전 제작에서 새 수정본으로 재심사하세요')
        return v

def signature(doc):
    return [(s.get('id'),s.get('title'),int(s.get('frames')),track(s,'voice').text or '' if track(s,'voice') is not None else '') for s in scenes(doc)]

def signature_plan(p):
    return [(s['id'],s['title'],s['frames'],s['narration']) for s in p['scenes']]

def materialize(doc,version):
    # Fresh production slots from the actual approved screenplay. Previous M-VML and all
    # registered bytes remain intact; rejected audio/video/old baseline clips are not auto-bound.
    doc=ET.fromstring(xml_bytes(doc))
    doc.set('editorial-plan',version['revision'])
    tl=doc.find('timeline'); tl.clear()
    for r in version['plan']['scenes']:
        s=ET.SubElement(tl,'scene',id=r['id'],title=r['title'],frames=str(r['frames']))
        ET.SubElement(s,'track',kind='image').text=r['visual']
        if r['motion'].strip(): ET.SubElement(s,'track',kind='video').text=r['motion']
        ET.SubElement(s,'track',kind='voice',speed='0.92',temperature='0.65',gain='0').text=r['narration']
        ET.SubElement(s,'track',kind='subtitle',mode='plain').text=r['subtitle']
    return validate(doc)
