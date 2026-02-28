"""
PromptCombiner - 이미지/비디오/오디오 프롬프트를 결합하여
외부 도구(Kling, Runway, Veo, Pika 등)에서 사용할 수 있는 프롬프트를 생성합니다.
"""

import os
import json
from typing import Dict, List, Optional


# 무료/저비용 도구별 프롬프트 포맷 템플릿
TOOL_TEMPLATES = {
    'comfyui_wan22': {
        'name': 'ComfyUI WAN 2.2 5B (Local)',
        'url': 'http://127.0.0.1:8188',
        'free_tier': True,
        'max_duration': 5,
        'format': 'image_to_video',
        'prompt_template': '{motion_prompt}. Cinematic wuxia, {style_note}.',
        'notes': '로컬 GPU. 무료. 고품질 모션. VRAM 8GB: 512x320/41f 권장.'
    },
    'comfyui_ltx2': {
        'name': 'ComfyUI LTX-2 Distilled (Local)',
        'url': 'http://127.0.0.1:8188',
        'free_tier': True,
        'max_duration': 20,
        'format': 'image_to_video_audio',
        'prompt_template': '{motion_prompt}. {style_note}. Cinematic martial arts scene.',
        'notes': '로컬 GPU. 무료. 오디오 동시 생성. 빠른 속도. VRAM 8GB: FP8 Distilled 사용.'
    },
    'kling': {
        'name': 'Kling AI',
        'url': 'https://klingai.com',
        'free_tier': True,
        'max_duration': 10,
        'format': 'image_to_video',
        'prompt_template': '{motion_prompt}. Style: cinematic wuxia, {style_note}. Duration: {duration}s.',
        'notes': '무료 10초 클립. 이미지 업로드 후 프롬프트 입력.'
    },
    'runway': {
        'name': 'Runway Gen-3',
        'url': 'https://runwayml.com',
        'free_tier': True,
        'max_duration': 10,
        'format': 'image_to_video',
        'prompt_template': '{motion_prompt}. Cinematic, {style_note}.',
        'notes': '무료 크레딧 125초 제공. Gen-3 Alpha Turbo 사용.'
    },
    'pika': {
        'name': 'Pika',
        'url': 'https://pika.art',
        'free_tier': True,
        'max_duration': 4,
        'format': 'image_to_video',
        'prompt_template': '{motion_prompt}',
        'notes': '무료 일일 크레딧. 4초 클립.'
    },
    'veo': {
        'name': 'Google Veo (via AI Studio)',
        'url': 'https://aistudio.google.com',
        'free_tier': True,
        'max_duration': 8,
        'format': 'text_to_video',
        'prompt_template': '{image_prompt}. {motion_prompt}. Cinematic wuxia style.',
        'notes': 'Google AI Studio에서 무료 사용. Veo 2 모델.'
    },
    'haiper': {
        'name': 'Haiper',
        'url': 'https://haiper.ai',
        'free_tier': True,
        'max_duration': 6,
        'format': 'image_to_video',
        'prompt_template': '{motion_prompt}. {style_note}.',
        'notes': '무료 일일 크레딧. 2-6초 클립.'
    }
}


class PromptCombiner:
    """에피소드 프롬프트를 외부 도구용으로 결합/포맷합니다."""

    def __init__(self, episode_dir: str):
        self.episode_dir = episode_dir
        self.image_prompts = self._load_json('prompts/image_prompts.json')
        self.video_prompts = self._load_json('prompts/video_prompts.json')
        self.audio_guide = self._load_json('prompts/audio_guide.json')
        self.scenario = self._load_json('scenario.json')

    def _load_json(self, relative_path: str) -> dict:
        path = os.path.join(self.episode_dir, relative_path)
        if not os.path.isfile(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_scene_count(self) -> int:
        prompts = self.image_prompts.get('enhanced_prompts', [])
        return len(prompts)

    def get_combined_scene(self, scene_id: str) -> dict:
        """특정 장면의 이미지+비디오+오디오 프롬프트를 결합"""
        result = {'scene_id': scene_id}

        # 이미지 프롬프트
        for p in self.image_prompts.get('enhanced_prompts', []):
            if p.get('scene_id') == scene_id:
                result['image_prompt'] = p.get('prompt', '')
                break

        # 비디오 프롬프트
        for p in self.video_prompts.get('motion_plans', []):
            if p.get('scene_id') == scene_id:
                result['motion_prompt'] = p.get('motion_prompt', '')
                result['duration_sec'] = p.get('duration_sec', 5)
                result['transition'] = p.get('transition', '')
                break

        return result

    def get_all_scenes(self) -> List[dict]:
        """모든 장면의 결합 프롬프트 반환"""
        scenes = []
        for p in self.image_prompts.get('enhanced_prompts', []):
            sid = p.get('scene_id', 'unknown')
            scenes.append(self.get_combined_scene(sid))
        return scenes

    def format_for_tool(self, scene_id: str, tool_key: str) -> dict:
        """특정 도구용으로 프롬프트를 포맷"""
        if tool_key not in TOOL_TEMPLATES:
            return {'error': f'Unknown tool: {tool_key}'}

        tool = TOOL_TEMPLATES[tool_key]
        scene = self.get_combined_scene(scene_id)

        duration = min(scene.get('duration_sec', 5), tool['max_duration'])
        style_note = 'dark atmosphere, volumetric lighting'

        prompt = tool['prompt_template'].format(
            image_prompt=scene.get('image_prompt', ''),
            motion_prompt=scene.get('motion_prompt', ''),
            style_note=style_note,
            duration=duration
        )

        return {
            'tool': tool['name'],
            'url': tool['url'],
            'scene_id': scene_id,
            'prompt': prompt,
            'duration': duration,
            'format': tool['format'],
            'notes': tool['notes']
        }

    def generate_test_sheet(self) -> dict:
        """전체 장면 x 전체 도구 테스트 시트 생성"""
        scenes = self.get_all_scenes()
        tools = list(TOOL_TEMPLATES.keys())

        sheet = {
            'episode_dir': self.episode_dir,
            'scene_count': len(scenes),
            'tool_count': len(tools),
            'tools': {k: {'name': v['name'], 'url': v['url'], 'free': v['free_tier']} for k, v in TOOL_TEMPLATES.items()},
            'tests': []
        }

        for scene in scenes:
            sid = scene['scene_id']
            for tool_key in tools:
                formatted = self.format_for_tool(sid, tool_key)
                sheet['tests'].append({
                    'scene_id': sid,
                    'tool': tool_key,
                    'tool_name': formatted['tool'],
                    'prompt': formatted['prompt'],
                    'duration': formatted['duration'],
                    'result': None,
                    'quality_score': None,
                    'cost': 'free',
                    'notes': ''
                })

        return sheet

    @staticmethod
    def get_available_tools() -> dict:
        return {k: {'name': v['name'], 'url': v['url'], 'free': v['free_tier'], 'max_sec': v['max_duration'], 'notes': v['notes']} for k, v in TOOL_TEMPLATES.items()}
