import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from PIL import Image

# Import the actual renderer, never exercise a real remote download in tests.
path=Path(__file__).resolve().parent/'render_sehando_intro.py'
if not path.is_file(): path=Path(__file__).resolve().parents[1]/'scripts/render_sehando_intro.py'
spec=importlib.util.spec_from_file_location('renderer',path)
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

class SourceCacheTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.asset={'id':'ART:DETAIL@1','url':'https://upload.wikimedia.org/example.jpg','source':'https://commons.wikimedia.org/wiki/File:Example.jpg','rights':'fixture ONLY','expected-width':'640','expected-height':'400'}
        self.src=self.root/'fixture.jpg'; Image.new('RGB',(640,400),'white').save(self.src)
    def test_import_reuse_offline(self):
        with patch.object(r,'download',side_effect=AssertionError('network must not run')):
            p,rec=r.cache_asset(self.root,self.asset,self.src)
            p2,rec2=r.cache_asset(self.root,self.asset)
        self.assertEqual(p,p2); self.assertEqual(rec,rec2); self.assertEqual(r.sha(self.src),r.sha(p)); self.assertIn('USER_SUPPLIED',rec['retrieval'])
    def test_no_wikimedia_retry(self):
        with patch.object(r,'urlopen',side_effect=AssertionError('no Wikimedia download')):
            with self.assertRaisesRegex(ValueError,'Source not cached'): r.cache_asset(self.root,self.asset,allow_download=True)
    def test_tampering_rejected(self):
        p,_=r.cache_asset(self.root,self.asset,self.src)
        Image.new('RGB',(640,400),'red').save(p)
        with self.assertRaisesRegex(ValueError,'identity/hash mismatch'): r.cache_asset(self.root,self.asset)
    def test_wrong_dimensions(self):
        Image.new('RGB',(600,400),'white').save(self.src)
        with self.assertRaisesRegex(ValueError,'dimensions differ'): r.cache_asset(self.root,self.asset,self.src)
        self.assertFalse((self.root/'outputs/sehando/intro/source-cache'/r.asset_key(self.asset)).exists())
    def test_existing_immutable_entry(self):
        p,_=r.cache_asset(self.root,self.asset,self.src); old=r.sha(p)
        Image.new('RGB',(640,400),'red').save(self.src)
        with self.assertRaisesRegex(ValueError,'Different import'): r.cache_asset(self.root,self.asset,self.src)
        self.assertEqual(old,r.sha(p))
    def test_successful_museum_download_cached(self):
        a=dict(self.asset,id='ART:LETTER@1',url='https://www.museum.go.kr/test.jpg')
        with patch.object(r,'download',side_effect=lambda a,p:p.write_bytes(self.src.read_bytes())) as m:
            _,rec=r.cache_asset(self.root,a,allow_download=True); r.cache_asset(self.root,a)
        self.assertEqual(m.call_count,1); self.assertEqual(rec['retrieval'],'SOURCE_URL_BYTES_RETRIEVED')
    def test_429_no_retry_and_no_partial_asset(self):
        a=dict(self.asset,id='ART:LETTER@1',url='https://www.museum.go.kr/test.jpg')
        with patch.object(r,'urlopen',side_effect=HTTPError(a['url'],429,'rate limited',{'Retry-After':'120'},None)) as m:
            with self.assertRaisesRegex(RuntimeError,'Retry-After=120'): r.cache_asset(self.root,a,allow_download=True)
        self.assertEqual(m.call_count,1); self.assertFalse((self.root/'outputs/sehando/intro/source-cache'/r.asset_key(a)).exists())
    def test_unsafe_cache_link_rejected(self):
        cache=self.root/'outputs'; target=self.root/'foreign'; target.mkdir()
        try: cache.symlink_to(target,target_is_directory=True)
        except (OSError,NotImplementedError): self.skipTest('symlink unavailable')
        with self.assertRaisesRegex(ValueError,'Unsafe output path'): r.cache_asset(self.root,self.asset,self.src)
if __name__=='__main__': unittest.main()
