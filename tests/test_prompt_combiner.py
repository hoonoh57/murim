"""
테스트: PromptCombiner - 프롬프트 결합 및 도구별 포맷 검증
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline.prompt_combiner import PromptCombiner, TOOL_TEMPLATES


class TestPromptCombiner:
    """PromptCombiner 기능 검증"""

    @pytest.fixture(scope="class")
    def ep_dir(self):
        """테스트 에피소드 디렉토리"""
        ep_path = "outputs/ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846"
        if not os.path.isdir(ep_path):
            pytest.skip(f"테스트 에피소드 없음: {ep_path}")
        return ep_path

    @pytest.fixture(scope="class")
    def combiner(self, ep_dir):
        """PromptCombiner 인스턴스"""
        return PromptCombiner(ep_dir)

    def test_load_prompts(self, combiner):
        """프롬프트 파일 로드 검증"""
        assert combiner.image_prompts, "image_prompts.json 로드 실패"
        assert combiner.video_prompts, "video_prompts.json 로드 실패"
        assert combiner.audio_guide, "audio_guide.json 로드 실패"

    def test_scene_count(self, combiner):
        """장면 개수 확인"""
        count = combiner.get_scene_count()
        assert count == 6, f"6장면이어야 함, 실제: {count}"

    def test_get_all_scenes(self, combiner):
        """전체 장면 프롬프트 결합"""
        scenes = combiner.get_all_scenes()
        assert len(scenes) == 6, f"6개 장면 기대, 실제: {len(scenes)}"
        
        # S01 장면 검증
        s01 = next((s for s in scenes if s['scene_id'] == 'S01'), None)
        assert s01 is not None, "S01 장면 없음"
        assert 'image_prompt' in s01, "S01에 image_prompt 없음"
        assert 'motion_prompt' in s01, "S01에 motion_prompt 없음"
        assert 'duration_sec' in s01, "S01에 duration_sec 없음"

    def test_available_tools(self):
        """지원 도구 확인"""
        tools = PromptCombiner.get_available_tools()
        assert len(tools) == 5, f"5개 도구 기대, 실제: {len(tools)}"
        
        expected = {'kling', 'runway', 'pika', 'veo', 'haiper'}
        assert set(tools.keys()) == expected, f"도구 이름 불일치"
        
        # 각 도구의 필수 필드 확인
        for tool_key, tool_info in tools.items():
            assert 'name' in tool_info, f"{tool_key}: name 필드 없음"
            assert 'url' in tool_info, f"{tool_key}: url 필드 없음"
            assert 'free' in tool_info, f"{tool_key}: free 필드 없음"
            assert 'max_sec' in tool_info, f"{tool_key}: max_sec 필드 없음"

    def test_format_for_tool_kling(self, combiner):
        """Kling 도구용 프롬프트 포맷"""
        result = combiner.format_for_tool('S01', 'kling')
        assert result['tool'] == 'Kling AI', "도구명 불일치"
        assert 'prompt' in result, "prompt 필드 없음"
        assert result['duration'] <= 10, "지속시간 제약(10초) 위반"
        assert result['format'] == 'image_to_video', "format 불일치"

    def test_format_for_tool_veo(self, combiner):
        """Veo 도구용 프롬프트 포맷 (text_to_video)"""
        result = combiner.format_for_tool('S01', 'veo')
        assert result['tool'] == 'Google Veo (via AI Studio)'
        # Veo는 text_to_video이므로 image_prompt 내용이 포함되어야 함
        assert len(result['prompt']) > 200, "프롬프트에 image 정보 포함되어야 함"
        assert result['format'] == 'text_to_video', "Veo는 text_to_video 방식"

    def test_format_all_tools(self, combiner):
        """모든 도구의 모든 장면 포맷 검증"""
        tools = list(TOOL_TEMPLATES.keys())
        scenes = combiner.get_all_scenes()
        
        for tool_key in tools:
            for scene in scenes:
                result = combiner.format_for_tool(scene['scene_id'], tool_key)
                assert 'tool' in result, f"{tool_key}/{scene['scene_id']}: tool 필드 없음"
                assert 'prompt' in result, f"{tool_key}/{scene['scene_id']}: prompt 필드 없음"
                assert result['duration'] > 0, f"{tool_key}/{scene['scene_id']}: duration이 0"

    def test_generate_test_sheet(self, combiner):
        """테스트 시트 생성"""
        sheet = combiner.generate_test_sheet()
        assert 'scene_count' in sheet, "scene_count 필드 없음"
        assert 'tool_count' in sheet, "tool_count 필드 없음"
        assert 'tests' in sheet, "tests 필드 없음"
        
        assert sheet['scene_count'] == 6, f"6개 장면 기대, 실제: {sheet['scene_count']}"
        assert sheet['tool_count'] == 5, f"5개 도구 기대, 실제: {sheet['tool_count']}"
        assert len(sheet['tests']) == 30, f"30개 테스트(6 scenes x 5 tools) 기대"
        
        # 각 테스트 항목 구조 확인
        for test in sheet['tests']:
            assert 'scene_id' in test, "test에 scene_id 없음"
            assert 'tool' in test, "test에 tool 없음"
            assert 'prompt' in test, "test에 prompt 없음"
            assert 'result' in test, "test에 result 없음 (초기값: None)"

    def test_audio_guide_structure(self, combiner):
        """오디오 가이드 구조"""
        audio = combiner.audio_guide
        if audio:
            # BGM
            if 'bgm' in audio:
                assert 'mood' in audio['bgm'], "BGM: mood 필드 없음"
                assert 'instruments' in audio['bgm'], "BGM: instruments 필드 없음"
            
            # SFX 리스트
            if 'sfx' in audio:
                assert isinstance(audio['sfx'], list), "SFX는 리스트여야 함"
                if len(audio['sfx']) > 0:
                    assert 'timestamp' in audio['sfx'][0], "SFX: timestamp 필드 없음"
                    assert 'effect' in audio['sfx'][0], "SFX: effect 필드 없음"


class TestPromptCombinerPerformance:
    """성능 및 대용량 테스트"""

    @pytest.fixture(scope="class")
    def ep_dir(self):
        ep_path = "outputs/ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846"
        if not os.path.isdir(ep_path):
            pytest.skip(f"테스트 에피소드 없음: {ep_path}")
        return ep_path

    @pytest.fixture(scope="class")
    def combiner(self, ep_dir):
        return PromptCombiner(ep_dir)

    def test_load_time(self, combiner):
        """로드 시간 측정 (< 1초)"""
        import time
        start = time.time()
        combiner.get_all_scenes()
        elapsed = time.time() - start
        assert elapsed < 1.0, f"로드 시간 너무 오래 걸림: {elapsed:.2f}초"

    def test_format_time(self, combiner):
        """포맷 시간 측정 (전체 < 100ms)"""
        import time
        tools = list(TOOL_TEMPLATES.keys())
        scenes = combiner.get_all_scenes()
        
        start = time.time()
        for tool_key in tools:
            for scene in scenes:
                combiner.format_for_tool(scene['scene_id'], tool_key)
        elapsed = time.time() - start
        
        avg_per_test = elapsed / (len(tools) * len(scenes)) * 1000
        assert avg_per_test < 10, f"평균 포맷 시간: {avg_per_test:.2f}ms (목표: < 10ms)"


class TestPromptCombinerExportFormats:
    """출력 포맷 검증"""

    @pytest.fixture(scope="class")
    def ep_dir(self):
        ep_path = "outputs/ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846"
        if not os.path.isdir(ep_path):
            pytest.skip(f"테스트 에피소드 없음: {ep_path}")
        return ep_path

    @pytest.fixture(scope="class")
    def combiner(self, ep_dir):
        return PromptCombiner(ep_dir)

    def test_json_serializable(self, combiner):
        """JSON 직렬화 가능 여부"""
        scenes = combiner.get_all_scenes()
        try:
            json_str = json.dumps(scenes, ensure_ascii=False, indent=2)
            assert len(json_str) > 0, "JSON 변환 실패"
        except TypeError as e:
            pytest.fail(f"JSON 직렬화 불가: {e}")

    def test_test_sheet_json_serializable(self, combiner):
        """테스트 시트 JSON 직렬화"""
        sheet = combiner.generate_test_sheet()
        try:
            json_str = json.dumps(sheet, ensure_ascii=False, indent=2)
            assert len(json_str) > 0, "JSON 변환 실패"
            # 파일로 저장 시뮬레이션
            saved_data = json.loads(json_str)
            assert saved_data['scene_count'] == sheet['scene_count']
        except Exception as e:
            pytest.fail(f"테스트 시트 JSON 변환 실패: {e}")


if __name__ == "__main__":
    # CLI 실행: python -m pytest tests/test_prompt_combiner.py -v
    pytest.main([__file__, "-v", "--tb=short"])
