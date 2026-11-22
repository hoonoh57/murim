"""Pre-production gate contract tests; no external model or GPU required."""
import copy
import json
import tempfile
import unittest
from src.studio.workspace import Store, patch, track, scenes, new_doc
from src.studio.editorial import Editorial, AXES, FIELDS, signature, signature_plan

class EditorialTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=Store(self.tmp.name); self.pid=self.store.create('test')
        self.e=Editorial(self.store,self.pid)
    def tearDown(self): self.tmp.cleanup()
    def mutate(self,action,**data):
        return self.e.mutate(self.e.view()['token'],action,data)
    def plan(self,change='first'):
        p=copy.deepcopy(self.e.view()['latest']['plan'])
        for k in FIELDS: p[k]='설계 '+k+' '+change
        for s in p['scenes']:
            s.update(title='장면 '+change,narration='실제 '+change,visual='이미지 '+change,sound='성우 '+change,facts='사료 '+change,subtitle='실제 '+change)
        return p
    def review(self,score=10,issues=None,resolve=True):
        v=self.e.view()
        r=dict(revision=v['latest']['revision'],scores={k:score for k in AXES},evidence='축별 증거',
            issues=issues or [],resolutions=[dict(id=i['id'],resolved=resolve,evidence='수정된 장면과 근거') for i in v['issues']],verdict='PASS')
        return self.mutate('review',raw=json.dumps(r),reviewer='fixture independent')
    def approve(self):
        return self.mutate('approval',confirmed=True,approver='fixture human',mvml_revision=self.e.view()['mvml_revision'])
    def test_unapproved_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'제작 보류'):self.e.require()
        with self.assertRaises(ValueError):self.approve()
    def test_incomplete_draft_can_save_not_review(self):
        p=self.plan();p['policy']=''
        self.assertFalse(self.mutate('plan',plan=p,note='draft')['ready'])
        with self.assertRaises(ValueError):self.review()
    def test_failed_revision_cannot_retry_or_approve(self):
        p=self.plan();self.mutate('plan',plan=p,note='v1')
        self.assertFalse(self.review(3,['기계음 방침 불량'])['review']['pass'])
        with self.assertRaises(ValueError):self.approve()
        with self.assertRaises(ValueError):self.review()
        with self.assertRaises(ValueError):self.mutate('plan',plan=p,note='same')
        self.mutate('plan',plan=self.plan('second'),note='v2')
        self.assertFalse(self.review(resolve=False)['review']['pass'])
        self.assertEqual(len(self.e.view()['issues']),1)
    def test_prior_review_and_all_issues_must_be_resolved(self):
        self.mutate('prior_review',raw='원문',issues=['역사 오류'])
        self.mutate('plan',plan=self.plan(),note='v1')
        self.assertFalse(self.review(resolve=False)['review']['pass'])
        self.mutate('plan',plan=self.plan('second'),note='v2')
        self.assertTrue(self.review()['review']['pass'])
        self.assertTrue(self.approve()['approved'])
        self.assertEqual(len(self.e.view()['versions']),3)
        self.assertEqual(self.e.view()['prior_raw'],'원문')
    def test_approved_scenario_materialized_and_protected(self):
        p=self.plan();self.mutate('plan',plan=p,note='v1');self.review();v=self.approve()
        d,h=self.store.load(self.pid);self.assertEqual(signature(d),signature_plan(p))
        self.assertEqual(d.get('editorial-plan'),v['latest']['revision'])
        self.assertIsNone(track(scenes(d)[0],'voice').get('asset'))
        self.e.require(d)
        sid=p['scenes'][0]['id']
        candidate,_=patch(d,[dict(op='set',scene=sid,track='subtitle',values={'mode':'fade'})])
        self.e.require(candidate)
        changed,_=patch(d,[dict(op='set',scene=sid,track='voice',values={'text':'다른 시나리오'})])
        with self.assertRaises(ValueError):self.e.require(changed)
        self.mutate('plan',plan=self.plan('second'),note='reopen')
        with self.assertRaises(ValueError):self.e.require()
        old,_=self.store.load(self.pid,h);self.assertEqual(signature(old),signature_plan(p))
    def test_known_failed_original_requires_raw_review(self):
        pid='d'*12; original=new_doc('failed baseline'); original.set('baseline','8a9f3c33d62e')
        self.store.save(pid,original); self.e=Editorial(self.store,pid)
        self.assertEqual(len(self.e.view()['issues']),4)
        self.mutate('plan',plan=self.plan(),note='v1')
        with self.assertRaisesRegex(ValueError,'기존 Gemini'):self.review()
        self.mutate('prior_review',raw='원문',issues=['추가 문제'])
        self.assertTrue(self.review()['review']['pass'])
        self.assertTrue(self.approve()['approved'])
        self.mutate('plan',plan=self.plan('second'),note='new version')
        self.assertEqual(len(self.e.view()['issues']),5)
        self.assertFalse(self.review(resolve=False)['review']['pass'])
    def test_actual_render_feedback_reopens_gate(self):
        self.mutate('plan',plan=self.plan(),note='v1');self.review();self.approve()
        source=dict(render='a'*12,sha256='b'*64,revision='c'*64,editorial_plan=self.e.view()['latest']['revision'])
        self.assertFalse(self.mutate('feedback',raw='실제 영상 비평',issues=['서사 결함'],source=source)['approved'])
        with self.assertRaises(ValueError):self.e.require()
        with self.assertRaises(ValueError):self.approve()
        with self.assertRaises(ValueError):self.review()
        self.mutate('plan',plan=self.plan('second'),note='rework')
        self.assertTrue(self.review()['review']['pass'])
        self.assertTrue(self.approve()['approved'])
        self.assertEqual(self.e.view()['feedback'][0]['source'],source)
    def test_plain_critique_capture_and_relay_plan(self):
        raw='Gemini 원문\n| 항목 | 문제 |\n| 서사 | 결말 미완성 |'
        self.mutate('prior_capture',raw=raw)
        self.assertEqual(self.e.view()['prior_raw'],raw)
        self.assertFalse(self.e.view()['prior_indexed'])
        v=self.e.view()
        response={'parent':v['latest']['revision'],'plan':self.plan(),'note':'결말 개편','prior_issues':['결말 미완성']}
        whole='사람이 읽는 변경 설명\n```json\n'+json.dumps(response,ensure_ascii=False)+'\n```'
        updated=self.mutate('relay_plan',raw=whole,instruction='결말을 완성해 줘')
        self.assertTrue(updated['prior_indexed'])
        self.assertEqual(updated['latest']['raw_response'],whole)
        self.assertEqual(updated['latest']['instruction'],'결말을 완성해 줘')
        self.assertEqual(len(updated['issues']),1)
        self.assertFalse(updated['approved'])
        with self.assertRaises(ValueError): self.mutate('relay_plan',raw=whole)
    def test_capture_without_extraction_blocks_review(self):
        self.mutate('prior_capture',raw='원문 비평')
        self.mutate('plan',plan=self.plan(),note='기존 방식')
        with self.assertRaisesRegex(ValueError,'문제 목록'):self.review()
    def test_whole_review_answer_kept_and_resolutions_visible(self):
        self.mutate('prior_review',raw='원문',issues=['결함'])
        self.mutate('plan',plan=self.plan(),note='v1')
        v=self.e.view()
        r=dict(revision=v['latest']['revision'],scores={k:10 for k in AXES},evidence='대본 근거',
            issues=[],resolutions=[dict(id=v['issues'][0]['id'],resolved=True,evidence='수정된 문장')],verdict='PASS')
        whole='사람이 읽는 독립 평가\n```json\n'+json.dumps(r,ensure_ascii=False)+'\n```'
        result=self.mutate('review',raw=whole,reviewer='fixture')
        self.assertEqual(result['review']['raw'],whole)
        self.assertEqual(result['review']['resolutions'],r['resolutions'])
        self.assertTrue(result['review']['pass'])
        self.assertFalse(result['approved'])
    def test_unstructured_response_cannot_become_plan(self):
        before=self.e.view()['token']
        with self.assertRaises(ValueError):self.mutate('relay_plan',raw='예상 96점 / 앞으로 개선할 계획')
        self.assertEqual(self.e.view()['token'],before)
        self.assertFalse(self.e.view()['approved'])

    def test_receive_plain_answer_preserves_without_approving(self):
        raw='예상 96점. 향후 개선할 계획입니다.'
        result=self.mutate('relay_receive',raw=raw,instruction='개선해줘')
        self.assertEqual(result['pending_reply']['raw'],raw)
        self.assertEqual(len(result['versions']),1)
        self.assertFalse(result['approved'])
        self.assertEqual(self.e.view()['pending_reply']['raw'],raw)
        self.assertEqual(self.mutate('relay_receive',raw=raw,instruction='개선해줘')['token'],result['token'])
    def test_receive_missing_field_reports_specific_and_then_recovers(self):
        self.mutate('prior_capture',raw='기존 결말 오류')
        p=self.plan();p['purpose']=''
        packet=dict(parent=self.e.view()['latest']['revision'],plan=p,note='실제 변경',prior_issues=['결말 오류'])
        result=self.mutate('relay_receive',raw=json.dumps(packet),instruction='개선')
        self.assertIn('작품의 중심 질문',result['pending_reply']['error'])
        self.assertEqual(len(result['versions']),1)
        packet['plan']=self.plan()
        whole='수정 답변\n```json\n'+json.dumps(packet,ensure_ascii=False)+'\n```'
        result=self.mutate('relay_receive',raw=whole,instruction='개선')
        self.assertIsNone(result['pending_reply'])
        self.assertEqual(len(result['versions']),2)
        self.assertTrue(result['prior_indexed'])
        self.assertFalse(result['approved'])
        self.assertIsNotNone(next(e for e in self.e.events() if e['kind']=='relay_rejected'))
    def test_stale_token_and_unknown_review(self):
        self.mutate('plan',plan=self.plan(),note='v1')
        with self.assertRaises(ValueError):self.e.mutate('','plan',{'plan':self.plan('v2'),'note':'stale'})
        with self.assertRaises(ValueError):self.mutate('review',raw=json.dumps({'revision':'wrong'}),reviewer='fixture')
    def test_null_and_low_axis_do_not_pass(self):
        self.mutate('plan',plan=self.plan(),note='v1')
        self.assertFalse(self.review(score=None)['review']['pass'])
        self.mutate('plan',plan=self.plan('second'),note='v2')
        self.assertFalse(self.review(score=9)['review']['pass'])

if __name__=='__main__':unittest.main()
