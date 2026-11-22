"""Invoked only by Studio with the existing local GPT-SoVITS runtime."""
import json
import os
import sys
from pathlib import Path

os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
root=Path.cwd().resolve()
job=Path(sys.argv[1]).resolve()
request=json.loads(job.read_text(encoding='utf-8'))
import yaml
import torch
import numpy as np
from scipy.io.wavfile import write
sys.path.insert(0,str(root/'GPT_SoVITS'))
from TTS_infer_pack.TTS import TTS,TTS_Config
source=root/'GPT_SoVITS/configs/tts_infer.yaml'
configs=yaml.safe_load(source.read_text(encoding='utf-8'))
cfg=dict(configs['v2'])
# Bind the known matching v2 pair, not the invalid custom weights from the old setup.
for key,rel in {
    't2s_weights_path':'GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt',
    'vits_weights_path':'GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s2G2333k.pth',
    'bert_base_path':'GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large',
    'cnhuhbert_base_path':'GPT_SoVITS/pretrained_models/chinese-hubert-base'
}.items():
    p=(root/rel).resolve()
    if not p.is_relative_to(root) or not p.exists(): raise FileNotFoundError(str(p))
    cfg[key]=str(p)
cfg.update(device='cuda' if torch.cuda.is_available() else 'cpu',version='v2')
cfg['is_half']=cfg['device']=='cuda';configs['custom']=cfg
config=job.with_name('resolved_tts.yaml');config.write_text(yaml.safe_dump(configs,allow_unicode=True),encoding='utf-8')
ref=root/'refs/narrator_ref_7s.wav'
if not ref.is_file(): raise FileNotFoundError(str(ref))
pipe=TTS(TTS_Config(str(config)))
params=dict(text=request['text'],text_lang='ko',ref_audio_path=str(ref),
            prompt_text=request['prompt_text'],prompt_lang='ko',top_k=10,top_p=.8,
            temperature=request['temperature'],text_split_method='cut0',batch_size=1,
            split_bucket=False,speed_factor=request['speed'],fragment_interval=.3,
            parallel_infer=False,streaming_mode=False,return_fragment=False,
            repetition_penalty=1.35,sample_steps=32,seed=42)
sr,audio=next(pipe.run(params)); samples=np.asarray(audio); values=samples.astype(np.float64)
if np.issubdtype(samples.dtype,np.integer): values/=max(abs(np.iinfo(samples.dtype).min),np.iinfo(samples.dtype).max)
if not np.isfinite(values).all() or len(values)/sr<.35 or np.sqrt(np.mean(values**2))<.002 or np.max(np.abs(values))<.02: raise RuntimeError('Silent or invalid synthesis')
write(str(job.with_name('voice.wav')),sr,np.clip(values*32767,-32768,32767).astype(np.int16))
print('[PASS] actual waveform synthesized; audition required')
