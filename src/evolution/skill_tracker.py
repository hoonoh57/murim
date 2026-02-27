from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.models import Scenario

class DraftPractice(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    topic: str
    focus_point: str  # 이번 습작에서 집중한 부분 (예: 내공 묘사, 대사 톤 등)
    scenario: Scenario
    self_reflection: str # 작가 스스로의 회고
    evolution_step: int # 진화 단계 레벨

class EvolutionLog(BaseModel):
    writer_id: str = "Heavenly_Writer_01"
    current_level: int = 1
    total_practices: int = 0
    experiences: List[str] = [] # 습득한 기술/노하우 목록
    practice_history: List[DraftPractice] = []
