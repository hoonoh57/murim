import copy
import json
import tempfile
import unittest
from pathlib import Path
from src.studio.comfy import parse_graph, bind_inputs, output_video, store_graph, get_graph, listed_graphs
from src.studio.workspace import Store

GRAPH={'1':{'class_type':'LoadImage','inputs':{'image':'old.png'}},'2':{'class_type':'LoadAudio','inputs':{'audio':'old.wav'}},'3':{'class_type':'TextEncode','inputs':{'text':'old'}},'4':{'class_type':'SaveVideo','inputs':{'video':['3',0],'filename_prefix':'old'}}}
MAP={'image':{'node':'1','field':'image'},'audio':{'node':'2','field':'audio'},'motion':{'node':'3','field':'text'},'output':'4'}
class Workflow(unittest.TestCase):
    def test_graph_validation(self):
        self.assertEqual(parse_graph(json.dumps(GRAPH).encode()),GRAPH)
        for g in ({'nodes':[]},{'1':{'class_type':'Shell','inputs':{}}},{'1':{'class_type':'X','inputs':{'p':'https://example.com/file'}}},{'1':{'class_type':'X','inputs':{'x':['missing',0]}}}):
            with self.assertRaises(ValueError):parse_graph(json.dumps(g).encode())
    def test_binding_no_mutation(self):
        g=bind_inputs(GRAPH,MAP,'image.png','audio.wav','hello');self.assertEqual(g['1']['inputs']['image'],'image.png');self.assertEqual(g['2']['inputs']['audio'],'audio.wav');self.assertEqual(g['3']['inputs']['text'],'hello');self.assertEqual(GRAPH['3']['inputs']['text'],'old')
    def test_wrong_mapping_prevents_execution(self):
        m=copy.deepcopy(MAP);m['audio']=m['image']
        with self.assertRaises(ValueError):bind_inputs(GRAPH,m,'i.png','a.wav','hello')
        with self.assertRaises(ValueError):bind_inputs(GRAPH,MAP,'i.png',None,'hello')
    def test_saved_video_selection(self):
        item={'filename':'actual.mp4','type':'output','subfolder':''};h={'outputs':{'4':{'gifs':[item]}}};self.assertEqual(output_video(h,'4'),item)
        with self.assertRaises(ValueError):output_video(h,'3')
        h['outputs']['4']['gifs'].append(item)
        with self.assertRaises(ValueError):output_video(h,'4')
    def test_trusted_immutable_registration(self):
        with tempfile.TemporaryDirectory() as t:
            store=Store(Path(t));pid=store.create('test');raw=json.dumps(GRAPH).encode()
            with self.assertRaises(ValueError):store_graph(store,pid,raw,False)
            r=store_graph(store,pid,raw,True);self.assertEqual(get_graph(store,pid,r['id']),GRAPH);self.assertEqual(len(listed_graphs(store,pid)),1)
if __name__=='__main__':unittest.main()
