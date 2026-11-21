import unittest
from pathlib import Path
from intro_lab import compile_vml

class CompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml=Path(__file__).with_name('intro.mvml.xml').read_text(encoding='utf-8')
    def test_valid_deterministic(self):
        p=compile_vml(self.xml)
        self.assertEqual((p['seconds'],len(p['shots'])),(60,8))
        self.assertEqual(p,compile_vml(self.xml))
    def reject(self,a,b):
        self.assertIn(a,self.xml)
        with self.assertRaises(ValueError):compile_vml(self.xml.replace(a,b,1))
    def test_missing_id(self):self.reject('camera="CAM:push@1"','camera="CAM:none@1"')
    def test_hash(self):self.reject('e4bed6727e4dc96b1b27cdca2e98eca848121d8ced57a1f43eaab949c3ffec72','0'*64)
    def test_type(self):self.reject('camera="CAM:push@1"','camera="IMG:street@1"')
    def test_duration(self):self.reject('seconds="7"','seconds="6"')
    def test_path_escape(self):self.reject('assets/street.jpg','assets/../../secret.jpg')
    def test_duplicate_shot(self):self.reject('id="S02"','id="S01"')
    def test_unsafe_xml(self):
        with self.assertRaises(ValueError):compile_vml('<!DOCTYPE foo>'+self.xml)

if __name__=='__main__':unittest.main()
