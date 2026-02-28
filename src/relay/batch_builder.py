"""
배치 프롬프트 빌더
- GATE별 의존성을 고려하여 라운드를 분리
- 각 요청에 REQ-ID와 Owner를 명기
- Claude가 파싱하기 쉬운 구조화된 형식으로 출력
"""

import json
from typing import Dict, List, Optional
from src.core.models import Scenario, Scene
from src.core.prompts import SYSTEM_PROMPT
from src.core.constants import COUNCIL_PERSONAS


class BatchRequest:
    """단일 AI 요청 단위"""
    def __init__(self, req_id: str, owner: str, gate: str, 
                 system_msg: str, user_msg: str, 
                 response_format: str = "text"):
        self.req_id = req_id
        self.owner = owner
        self.gate = gate
        self.system_msg = system_msg
        self.user_msg = user_msg
        self.response_format = response_format  # "json" or "text"


class BatchBuilder:
    """라운드별 배치 프롬프트를 생성합니다."""

    def build_round1(self, topic: str, events: str) -> List[BatchRequest]:
        """
        Round 1: 시나리오 생성 (WriterAgent만)
        의존성 없음 — 1개 요청
        """
        requests = []

        # REQ-001: Writer 시나리오 생성
        requests.append(BatchRequest(
            req_id="REQ-001",
            owner="WriterAgent",
            gate="GATE1-scenario",
            system_msg=SYSTEM_PROMPT,
            user_msg=(
                f"[에피소드 요청]\n"
                f"주제: {topic}\n"
                f"주요 사건: {events}\n\n"
                f"위 내용을 바탕으로 시나리오를 작성해주세요.\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"title": "제목", "script": "전체 나레이션 대본", '
                f'"scenes": [{{"id": "S01", "time_range": "0:00-0:30", '
                f'"description": "장면 설명", "camera": "카메라 지시", '
                f'"emotion": "감정톤", "image_prompt": "영문 이미지 프롬프트", '
                f'"video_prompt": "영문 비디오 프롬프트"}}], '
                f'"sound_guide": {{"bgm": "BGM 무드", "fx": "효과음 설명"}}}}'
            ),
            response_format="json"
        ))

        return requests

    def build_round2(self, scenario_json: dict) -> List[BatchRequest]:
        """
        Round 2: 시나리오 평가 + 아트/카메라 기획 (병렬 가능)
        의존성: Round 1의 시나리오 결과
        """
        requests = []
        title = scenario_json.get("title", "")
        script = scenario_json.get("script", "")
        scenes_str = json.dumps(scenario_json.get("scenes", []), ensure_ascii=False, indent=2)

        # REQ-002: Council 평가 (6인 비평위원회)
        persona_list = "\n".join([f"  {i+1}. {p}" for i, p in enumerate(COUNCIL_PERSONAS)])

        requests.append(BatchRequest(
            req_id="REQ-002",
            owner="CouncilAgent",
            gate="GATE1-review",
            system_msg=(
                f"당신은 무협 시나리오 품질 평가 위원회입니다. "
                f"6명의 서로 다른 관점의 평가자가 각각 점수와 의견을 제시합니다."
            ),
            user_msg=(
                f"다음 시나리오를 평가하세요.\n\n"
                f"제목: {title}\n"
                f"대본:\n{script}\n\n"
                f"평가자 목록:\n{persona_list}\n\n"
                f"각 평가자별로 0~10점 점수, 코멘트, 개선 제안을 작성하세요.\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"critiques": [{{"persona": "이름", "score": 8.5, '
                f'"comment": "코멘트", "suggestions": ["제안1", "제안2"]}}], '
                f'"average_score": 8.0, "verdict": "GO 또는 REWORK 또는 KILL"}}'
            ),
            response_format="json"
        ))

        # REQ-003: ArtDirection 스타일 가이드
        requests.append(BatchRequest(
            req_id="REQ-003",
            owner="ArtDirectionAgent",
            gate="GATE2-style",
            system_msg="당신은 무협 콘텐츠의 미술 감독입니다. 시나리오의 세계관과 감정에 맞는 비주얼 스타일을 설계합니다.",
            user_msg=(
                f"다음 시나리오에 맞는 아트 스타일 가이드를 작성하세요.\n\n"
                f"제목: {title}\n"
                f"대본 요약:\n{script[:500]}\n\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"style": "스타일명 (예: Dark Wuxia)", '
                f'"palette": ["#hexcode1", "#hexcode2", "#hexcode3"], '
                f'"mood": "전체 분위기 한 줄", '
                f'"texture": "질감/재질 설명", '
                f'"reference": "참고 작품 또는 스타일"}}'
            ),
            response_format="json"
        ))

        # REQ-004: Camera 앵글 계획
        requests.append(BatchRequest(
            req_id="REQ-004",
            owner="CameraAgent",
            gate="GATE2-camera",
            system_msg="당신은 무협 영상의 촬영 감독입니다. 각 장면의 감정과 액션에 최적화된 카메라 기법을 설계합니다.",
            user_msg=(
                f"다음 장면들의 카메라 앵글과 움직임을 계획하세요.\n\n"
                f"장면 목록:\n{scenes_str}\n\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"camera_plans": [{{"scene_id": "S01", "angle": "카메라 앵글명", '
                f'"movement": "카메라 움직임", "composition": "구도 설명", '
                f'"transition": "장면 전환 기법"}}]}}'
            ),
            response_format="json"
        ))

        return requests

    def build_round3(self, scenario_json: dict, council_json: dict,
                     style_guide_json: dict, camera_plans_json: dict,
                     needs_rework: bool = False) -> List[BatchRequest]:
        """
        Round 3: 
        - 만약 REWORK이면 → 수정 시나리오 요청 1개
        - 만약 GO이면 → 리소스 제작 프롬프트 (Imaging/Video/Audio/Marketing)
        """
        requests = []
        title = scenario_json.get("title", "")
        script = scenario_json.get("script", "")
        scenes = scenario_json.get("scenes", [])

        if needs_rework:
            # 시나리오 재작성 요청
            critiques_summary = json.dumps(
                council_json.get("critiques", []), ensure_ascii=False, indent=2
            )
            requests.append(BatchRequest(
                req_id="REQ-005R",
                owner="WriterAgent",
                gate="GATE1-rework",
                system_msg=SYSTEM_PROMPT,
                user_msg=(
                    f"다음은 당신이 작성한 시나리오에 대한 6인 비평위원회의 평가입니다.\n\n"
                    f"원본 제목: {title}\n"
                    f"원본 대본:\n{script}\n\n"
                    f"비평:\n{critiques_summary}\n\n"
                    f"비평을 적극 반영하여 시나리오를 수정하고, "
                    f"Round 1과 동일한 JSON 형식으로 다시 작성해주세요."
                ),
                response_format="json"
            ))
            return requests

        # GO 경로: 리소스 제작 프롬프트들
        style_name = style_guide_json.get("style", "Traditional Wuxia")
        palette = style_guide_json.get("palette", [])
        palette_str = ", ".join(palette) if palette else "#2D1B1B, #DAA520"
        camera_plans = camera_plans_json.get("camera_plans", [])

        # REQ-005: Imaging 프롬프트 강화
        scene_prompts = []
        for s in scenes:
            scene_prompts.append(
                f"Scene {s.get('id', '?')}: {s.get('image_prompt', s.get('description', ''))}"
            )
        scene_prompts_str = "\n".join(scene_prompts)

        requests.append(BatchRequest(
            req_id="REQ-005",
            owner="ImagingAgent",
            gate="GATE3-imaging",
            system_msg="당신은 AI 이미지 프롬프트 전문가입니다. Midjourney/DALL-E용 고품질 영문 프롬프트를 작성합니다.",
            user_msg=(
                f"다음 장면들의 이미지 프롬프트를 고품질로 확장하세요.\n\n"
                f"스타일: {style_name}\n"
                f"색상 팔레트: {palette_str}\n\n"
                f"원본 프롬프트:\n{scene_prompts_str}\n\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"enhanced_prompts": [{{"scene_id": "S01", '
                f'"prompt": "enhanced english prompt with style and lighting details"}}]}}'
            ),
            response_format="json"
        ))

        # REQ-006: Video 모션 지시
        requests.append(BatchRequest(
            req_id="REQ-006",
            owner="VideoAgent",
            gate="GATE3-video",
            system_msg="당신은 AI 영상 연출가입니다. 각 장면의 모션, 카메라 움직임, 전환 효과를 설계합니다.",
            user_msg=(
                f"다음 장면들의 비디오 모션 지시서를 작성하세요.\n\n"
                f"장면 목록:\n{json.dumps(scenes, ensure_ascii=False, indent=2)}\n\n"
                f"카메라 계획:\n{json.dumps(camera_plans, ensure_ascii=False, indent=2)}\n\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"motion_plans": [{{"scene_id": "S01", '
                f'"motion_prompt": "english motion description", '
                f'"duration_sec": 5, "transition": "cut/fade/zoom"}}]}}'
            ),
            response_format="json"
        ))

        # REQ-007: Audio 사운드스케이프
        sound_guide = scenario_json.get("sound_guide", {})
        requests.append(BatchRequest(
            req_id="REQ-007",
            owner="AudioAgent",
            gate="GATE3-audio",
            system_msg="당신은 무협 콘텐츠의 사운드 디자이너입니다. BGM, 효과음, TTS 가이드를 설계합니다.",
            user_msg=(
                f"다음 시나리오의 사운드스케이프를 설계하세요.\n\n"
                f"제목: {title}\n"
                f"대본:\n{script[:800]}\n"
                f"기존 사운드 가이드: {json.dumps(sound_guide, ensure_ascii=False)}\n\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"bgm": {{"mood": "무드 설명", "tempo": "BPM", "instruments": ["악기1"]}}, '
                f'"sfx": [{{"timestamp": "0:05", "effect": "효과음 설명"}}], '
                f'"tts_guide": {{"voice_style": "음성 스타일", "pace": "빠르기", "emotion": "감정톤"}}}}'
            ),
            response_format="json"
        ))

        # REQ-008: Marketing 에셋
        requests.append(BatchRequest(
            req_id="REQ-008",
            owner="MarketingAgent",
            gate="GATE4-marketing",
            system_msg="당신은 유튜브 무협 콘텐츠 마케팅 전문가입니다. 조회수와 구독을 극대화하는 에셋을 설계합니다.",
            user_msg=(
                f"다음 에피소드의 마케팅 에셋을 작성하세요.\n\n"
                f"제목: {title}\n"
                f"시놉시스:\n{script[:300]}\n\n"
                f"반드시 아래 JSON 형식으로만 답하세요:\n"
                f'{{"youtube_title": "클릭 유도 제목", '
                f'"thumbnail_text": "썸네일 텍스트 (15자 이내)", '
                f'"description": "영상 설명 (300자)", '
                f'"tags": ["태그1", "태그2"], '
                f'"hook_line": "시작 5초 후킹 멘트"}}'
            ),
            response_format="json"
        ))

        return requests

    def format_batch(self, requests: List[BatchRequest], round_num: int) -> str:
        """배치 요청 리스트를 하나의 복사 가능한 텍스트로 포맷합니다."""
        lines = []
        lines.append(f"===== MURIM AI FACTORY — BATCH REQUEST (Round {round_num}) =====")
        lines.append(f"총 요청 수: {len(requests)}개")
        lines.append(f"")
        lines.append(f"### [중요 지시: 반드시 준수할 것] ###")
        lines.append(f"1. 아래 모든 요청에 대해 순서대로 각각 답변해 주세요.")
        lines.append(f"2. 각 답변의 시작과 끝에 지정된 구분자를 '토씨 하나 틀리지 않고' 정확히 사용하세요.")
        lines.append(f"3. 구분자 예시 (REQ-001에 대한 답변일 경우):")
        lines.append(f"   ---[RES-001 | WriterAgent]---")
        lines.append(f"   {{ ... JSON 데이터 ... }}")
        lines.append(f"   ---[END RES-001]---")
        lines.append(f"4. 위 구분자가 없으면 시스템이 답변을 인식하지 못합니다.")
        lines.append(f"")

        for req in requests:
            lines.append(f"---[{req.req_id} | {req.owner} | {req.gate}]---")
            if req.system_msg:
                lines.append(f"[시스템 지시]\n{req.system_msg}")
                lines.append(f"")
            lines.append(f"[요청]\n{req.user_msg}")
            lines.append(f"---[END {req.req_id}]---")
            lines.append(f"")

        lines.append(f"===== END BATCH REQUEST =====")
        lines.append(f"")
        lines.append(f"[응답 형식 가이드]")
        lines.append(f"아래 형식들을 답변에 그대로 포함시켜 주세요:")
        for req in requests:
            res_id = req.req_id.split('-')[1]
            lines.append(f"---[RES-{res_id} | {req.owner}]---")
            lines.append(f"(이곳에 {req.response_format.upper()} 응답 작성)")
            lines.append(f"---[END RES-{res_id}]---")
            lines.append(f"")

        return "\n".join(lines)
