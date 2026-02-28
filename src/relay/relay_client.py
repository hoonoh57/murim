"""
Human-Relay 클라이언트
- 배치 빌더/파서를 사용하여 웹 UI와 에이전트 시스템을 연결
- 라운드별 상태 관리
"""

import json
from typing import Dict, Optional, List
from src.relay.batch_builder import BatchBuilder, BatchRequest
from src.relay.batch_parser import BatchParser, ParsedResponse
from src.core.models import Scenario, Scene, Critique, ProductionResult


class RelaySession:
    """하나의 에피소드 제작 세션을 관리합니다."""
    
    def __init__(self, topic: str, events: str):
        self.topic = topic
        self.events = events
        self.builder = BatchBuilder()
        self.parser = BatchParser()
        
        # 라운드별 결과 저장소
        self.round_results: Dict[int, Dict[str, ParsedResponse]] = {}
        self.current_round = 0
        
        # 에이전트별 결과 캐시
        self.scenario_json: Optional[dict] = None
        self.council_json: Optional[dict] = None
        self.style_guide_json: Optional[dict] = None
        self.camera_plans_json: Optional[dict] = None
        self.imaging_json: Optional[dict] = None
        self.video_json: Optional[dict] = None
        self.audio_json: Optional[dict] = None
        self.marketing_json: Optional[dict] = None
        
        # 상태
        self.status = "initialized"  # initialized, round1, round2, round3, completed
        self.rework_count = 0
        self.max_reworks = 2
        self.messages: List[str] = []  # UI 표시용 로그 메시지

    def start_round1(self) -> str:
        """Round 1 배치 프롬프트를 생성합니다."""
        self.current_round = 1
        self.status = "round1"
        self.messages.append("📝 Round 1: 시나리오 생성 요청 준비 중...")
        
        requests = self.builder.build_round1(self.topic, self.events)
        batch_text = self.builder.format_batch(requests, round_num=1)
        
        self.messages.append(f"✅ Round 1 배치 프롬프트 생성 완료 (요청 {len(requests)}개)")
        return batch_text

    def process_round1_response(self, raw_response: str) -> dict:
        """Round 1 응답을 파싱하고 시나리오를 추출합니다."""
        results = self.parser.parse(raw_response)
        self.round_results[1] = results
        
        # WriterAgent 응답 추출
        writer_resp = self.parser.get_by_owner(results, "Writer")
        if writer_resp and writer_resp.parsed_json:
            self.scenario_json = writer_resp.parsed_json
            self.messages.append(
                f"✅ 시나리오 수신: \"{self.scenario_json.get('title', 'N/A')}\""
            )
            return {"success": True, "scenario": self.scenario_json}
        
        # JSON 파싱 실패 시 전체 응답에서 JSON 추출 시도
        json_obj = self.parser.extract_json(raw_response)
        if json_obj:
            self.scenario_json = json_obj
            self.messages.append(
                f"✅ 시나리오 수신 (직접 파싱): \"{self.scenario_json.get('title', 'N/A')}\""
            )
            return {"success": True, "scenario": self.scenario_json}
        
        self.messages.append("❌ Round 1 응답 파싱 실패. 형식을 확인해 주세요.")
        return {"success": False, "error": "파싱 실패"}

    def start_round2(self) -> str:
        """Round 2 배치 프롬프트를 생성합니다."""
        if not self.scenario_json:
            return "오류: 시나리오가 없습니다. Round 1을 먼저 완료하세요."
        
        self.current_round = 2
        self.status = "round2"
        self.messages.append("📝 Round 2: 평가 + 기획 요청 준비 중...")
        
        requests = self.builder.build_round2(self.scenario_json)
        batch_text = self.builder.format_batch(requests, round_num=2)
        
        self.messages.append(f"✅ Round 2 배치 프롬프트 생성 완료 (요청 {len(requests)}개)")
        return batch_text

    def process_round2_response(self, raw_response: str) -> dict:
        """Round 2 응답을 파싱합니다."""
        results = self.parser.parse(raw_response)
        self.round_results[2] = results
        
        # Council 응답
        council_resp = self.parser.get_by_owner(results, "Council")
        if council_resp and council_resp.parsed_json:
            self.council_json = council_resp.parsed_json
            avg = self.council_json.get("average_score", 0)
            verdict = self.council_json.get("verdict", "N/A")
            self.messages.append(f"⚖️ 평가 완료: 평균 {avg}점 → {verdict}")
        
        # ArtDirection 응답
        art_resp = self.parser.get_by_owner(results, "ArtDirection")
        if art_resp and art_resp.parsed_json:
            self.style_guide_json = art_resp.parsed_json
            self.messages.append(
                f"🎨 스타일 가이드: {self.style_guide_json.get('style', 'N/A')}"
            )
        
        # Camera 응답
        camera_resp = self.parser.get_by_owner(results, "Camera")
        if camera_resp and camera_resp.parsed_json:
            self.camera_plans_json = camera_resp.parsed_json
            plans_count = len(self.camera_plans_json.get("camera_plans", []))
            self.messages.append(f"🎬 카메라 계획: {plans_count}개 장면")
        
        # REWORK 판단
        needs_rework = False
        if self.council_json:
            verdict = self.council_json.get("verdict", "").upper()
            avg_score = self.council_json.get("average_score", 0)
            if verdict == "REWORK" or (avg_score < 7.5 and verdict != "GO"):
                needs_rework = True
            if verdict == "KILL" or avg_score < 6.0:
                self.messages.append("💀 KILL 판정: 품질 미달로 제작 중단 권고")
                self.status = "killed"
                return {"success": True, "needs_rework": False, "killed": True}
        
        return {
            "success": True, 
            "needs_rework": needs_rework,
            "can_rework": self.rework_count < self.max_reworks,
            "killed": False
        }

    def start_round3(self, force_go: bool = False) -> str:
        """Round 3 배치 프롬프트를 생성합니다."""
        self.current_round = 3
        self.status = "round3"
        
        needs_rework = False
        if not force_go and self.council_json:
            verdict = self.council_json.get("verdict", "").upper()
            avg_score = self.council_json.get("average_score", 0)
            if verdict == "REWORK" or avg_score < 7.5:
                needs_rework = True
                self.rework_count += 1
        
        if needs_rework:
            self.messages.append(
                f"🔄 REWORK 요청 ({self.rework_count}/{self.max_reworks}): "
                f"시나리오 수정 프롬프트 생성 중..."
            )
        else:
            self.messages.append("🚀 GO 판정: 리소스 제작 프롬프트 생성 중...")
        
        requests = self.builder.build_round3(
            scenario_json=self.scenario_json,
            council_json=self.council_json or {},
            style_guide_json=self.style_guide_json or {},
            camera_plans_json=self.camera_plans_json or {},
            needs_rework=needs_rework
        )
        batch_text = self.builder.format_batch(requests, round_num=3)
        
        self.messages.append(f"✅ Round 3 배치 프롬프트 생성 완료 (요청 {len(requests)}개)")
        return batch_text

    def process_round3_response(self, raw_response: str) -> dict:
        """Round 3 응답을 파싱합니다."""
        results = self.parser.parse(raw_response)
        self.round_results[3] = results
        
        # Rework 경로인 경우: WriterAgent의 수정본 수신 확인
        writer_resp = self.parser.get_by_owner(results, "Writer")
        if writer_resp and writer_resp.parsed_json:
            self.scenario_json = writer_resp.parsed_json
            self.messages.append(
                f"📝 수정 시나리오 수신: \"{self.scenario_json.get('title', 'N/A')}\""
            )
            # Rework 성공 → 다시 평가(Round 2) 단계로 상태 변경
            self.status = "round2"
            # start_round2()에서 2로 재조정되지만, 여기서 미리 맞춰둠 (정합성)
            self.current_round = 2
            return {"success": True, "reworked": True}
        
        # GO 경로: 리소스 결과 수집
        imaging_resp = self.parser.get_by_owner(results, "Imaging")
        if imaging_resp and imaging_resp.parsed_json:
            self.imaging_json = imaging_resp.parsed_json
            count = len(self.imaging_json.get("enhanced_prompts", []))
            self.messages.append(f"🖼️ 이미지 프롬프트: {count}개 장면")
        
        video_resp = self.parser.get_by_owner(results, "Video")
        if video_resp and video_resp.parsed_json:
            self.video_json = video_resp.parsed_json
            count = len(self.video_json.get("motion_plans", []))
            self.messages.append(f"🎥 비디오 모션 플랜: {count}개 장면")
        
        audio_resp = self.parser.get_by_owner(results, "Audio")
        if audio_resp and audio_resp.parsed_json:
            self.audio_json = audio_resp.parsed_json
            self.messages.append(f"🔊 사운드스케이프: 수신 완료")
        
        marketing_resp = self.parser.get_by_owner(results, "Marketing")
        if marketing_resp and marketing_resp.parsed_json:
            self.marketing_json = marketing_resp.parsed_json
            yt_title = self.marketing_json.get("youtube_title", "N/A")
            self.messages.append(f"📢 마케팅: \"{yt_title}\"")
        
        self.status = "completed"
        self.messages.append("🎉 전체 제작 파이프라인 완료!")
        return {"success": True, "reworked": False}

    def get_summary(self) -> dict:
        """최종 제작 결과 요약을 반환합니다."""
        return {
            "status": self.status,
            "topic": self.topic,
            "events": self.events,
            "scenario": self.scenario_json,
            "council": self.council_json,
            "style_guide": self.style_guide_json,
            "camera_plans": self.camera_plans_json,
            "imaging": self.imaging_json,
            "video": self.video_json,
            "audio": self.audio_json,
            "marketing": self.marketing_json,
            "messages": self.messages,
            "rework_count": self.rework_count,
            "current_round": self.current_round
        }

    def to_dict(self) -> dict:
        """세션 상태 전체를 딕셔너리로 변환 (저장용)"""
        data = self.get_summary()
        
        # round_results 직렬화
        serialized_results = {}
        for round_num, results in self.round_results.items():
            serialized_results[str(round_num)] = {
                res_id: resp.to_dict() for res_id, resp in results.items()
            }
        data["round_results"] = serialized_results
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'RelaySession':
        """딕셔너리로부터 세션 복구"""
        session = cls(topic=data.get("topic", ""), events=data.get("events", ""))
        session.status = data.get("status", "initialized")
        session.current_round = data.get("current_round", 0)
        session.rework_count = data.get("rework_count", 0)
        session.messages = data.get("messages", [])
        
        session.scenario_json = data.get("scenario")
        session.council_json = data.get("council")
        session.style_guide_json = data.get("style_guide")
        session.camera_plans_json = data.get("camera_plans")
        session.imaging_json = data.get("imaging")
        session.video_json = data.get("video")
        session.audio_json = data.get("audio")
        session.marketing_json = data.get("marketing")
        
        # round_results 복구
        raw_results = data.get("round_results", {})
        for round_str, results_dict in raw_results.items():
            round_num = int(round_str)
            session.round_results[round_num] = {
                res_id: ParsedResponse.from_dict(resp_data) 
                for res_id, resp_data in results_dict.items()
            }
        
        return session
