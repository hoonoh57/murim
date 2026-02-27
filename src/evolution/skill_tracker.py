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
    agent_id: str = "Agent_01"
    current_level: int = 1
    total_practices: int = 0
    total_xp: int = 0
    experiences: List[str] = [] # 습득한 기술/노하우 목록
    practice_history: List[DraftPractice] = []

    def check_level_up(self):
        # 레벨업 공식: 레벨 * 500 XP 필요
        needed_xp = self.current_level * 500
        if self.total_xp >= needed_xp:
            self.current_level += 1
            msg = f"✨ LEVEL UP! {self.agent_id}: {self.current_level-1} -> {self.current_level} ✨"
            self.experiences.append(f"Level {self.current_level} 달성")
            print("\n" + "*"*30)
            print(msg)
            print("*"*30 + "\n")
