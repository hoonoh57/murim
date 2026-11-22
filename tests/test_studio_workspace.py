import io
import json
import math
import tempfile
import unittest
import wave
from pathlib import Path
import struct
from PIL import Image
from src.studio.workspace import Store, patch, state, track, get_scene, register_asset, safe, digest, voice_key, assets, new_doc
from src.studio.render import render, executables, media_info
import xml.etree.ElementTree as ET

class Studio(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.store=Store(self.root);self.pid=self.store.create('Fixture');self.doc,self.rev=self.store.load(self.pid);self.sid=state(self.doc)['scenes'][0]['id']
    def change(self,*ops):
        return patch(self.doc,list(ops))
    def test_revision_cas_restore(self):
        d,dirty=self.change(dict(op='scene',scene=self.sid,title='changed'));r=self.store.save(self.pid,d,self.rev);self.assertNotEqual(r,self.rev);self.assertEqual(dirty,[self.sid]);self.assertRaisesRegex(ValueError,'Revision conflict',self.store.save,self.pid,d,self.rev);old,_=self.store.load(self.pid,self.rev);self.assertEqual(self.store.save(self.pid,old,r),self.rev)
    def test_select_changes_only_one_scene(self):
        d,_=self.change(dict(op='add_scene',after=self.sid));d2,dirty=patch(d,[dict(op='set',scene=self.sid,track='subtitle',values={'text':'test','mode':'fade'})]);self.assertEqual(dirty,[self.sid]);self.assertEqual(state(d2)['scenes'][1],state(d)['scenes'][1]);self.assertEqual(state(d2)['frames'],288)
    def test_reject_invalid(self):
        for op in [dict(op='set',scene=self.sid,track='effect',values={'camera':'exec'}),dict(op='set',scene=self.sid,track='image',values={'path':'../../secrets'}),dict(op='set',scene=self.sid,track='image',values={'asset':'not-registered'}),dict(op='delete_scene',scene=self.sid)]:
            with self.assertRaises(ValueError):self.change(op)
    def image(self):
        p=safe(self.root,'outputs/test.jpg',create=True);Image.new('RGB',(2200,1500),'#8b8574').save(p);return register_asset(self.doc,self.root,p,'image','fixture','test','test only')
    def audio(self):
        p=safe(self.root,'outputs/test.wav',create=True)
        with wave.open(str(p),'wb') as w:
            w.setparams((1,2,16000,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<h',int(3000*math.sin(i*.17))) for i in range(10000)))
        return register_asset(self.doc,self.root,p,'audio','fixture','test','test only')
    def test_voice_changes_invalidate(self):
        a=self.audio();d,_=self.change(dict(op='set',scene=self.sid,track='voice',values={'asset':a,'text':'old'}),dict(op='set',scene=self.sid,track='subtitle',values={'text':'old'}));d2,_=patch(d,[dict(op='set',scene=self.sid,track='voice',values={'text':'new'})]);s=get_scene(d2,self.sid);self.assertFalse(track(s,'voice').get('asset'));self.assertEqual(track(s,'subtitle').text,'new');self.assertIn('voice',state(d2)['scenes'][0]['pending'])
    def test_asset_tamper(self):
        a=self.image();from src.studio.workspace import asset_path;path=asset_path(self.root,assets(self.doc)[a]);path.write_bytes(b'x');self.assertRaisesRegex(ValueError,'hash mismatch',asset_path,self.root,assets(self.doc)[a])
    def test_traversal(self):
        self.assertRaises(ValueError,safe,self.root,'../x')
        (self.root/'foreign').mkdir();(self.root/'link').symlink_to(self.root/'foreign',target_is_directory=True);self.assertRaises(ValueError,safe,self.root,'link',directory=True)
    def test_real_render_and_reuse(self):
        # Synthetic image and tone are technical fixtures only and never product quality evidence.
        a=self.image();snd=self.audio();d,_=self.change(dict(op='scene',scene=self.sid,frames=24),dict(op='set',scene=self.sid,track='image',values={'asset':a}),dict(op='set',scene=self.sid,track='voice',values={'text':'test','asset':snd}),dict(op='set',scene=self.sid,track='subtitle',values={'text':'One shot','mode':'fade'}),dict(op='set',scene=self.sid,track='effect',values={'camera':'push','amount':.12}),dict(op='add_scene',after=self.sid,frames=24));other=state(d)['scenes'][1]['id'];d,_=patch(d,[dict(op='set',scene=other,track='image',values={'asset':a}),dict(op='set',scene=other,track='bgm',values={'asset':snd,'gain':-20})]);r=self.store.save(self.pid,d,self.rev);first=render(self.store,self.pid,d,r);self.assertEqual(first['frames'],48);d2,dirty=patch(d,[dict(op='set',scene=self.sid,track='subtitle',values={'text':'Edited','mode':'reveal'})]);r2=self.store.save(self.pid,d2,r);second=render(self.store,self.pid,d2,r2);self.assertEqual(dirty,[self.sid]);self.assertEqual(second['clips'][1]['status'],'CACHE_REUSED');self.assertEqual(first['clips'][1]['sha256'],second['clips'][1]['sha256']);self.assertNotEqual(first['clips'][0]['sha256'],second['clips'][0]['sha256']);self.assertNotEqual(first['sha256'],second['sha256'])
    def test_stale_voice_blocks_render(self):
        a=self.image();d,_=self.change(dict(op='scene',scene=self.sid,frames=24),dict(op='set',scene=self.sid,track='image',values={'asset':a}),dict(op='set',scene=self.sid,track='voice',values={'text':'pending'}));r=self.store.save(self.pid,d,self.rev)
        with self.assertRaisesRegex(ValueError,'Narration is pending'):render(self.store,self.pid,d,r,self.sid)
if __name__=='__main__':unittest.main()
