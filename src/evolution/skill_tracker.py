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
    total_xp: int = 0
    experiences: List[str] = [] # 습득한 기술/노하우 목록
    practice_history: List[DraftPractice] = []

    def add_practice(self, practice: DraftPractice, score: float):
        self.practice_history.append(practice)
        self.total_practices += 1
        
        # XP 계산: 평점 기반 (평점 * 20)
        # 예: 8.5점 -> 170 XP
        gained_xp = int(score * 20)
        self.total_xp += gained_xp
        print(f"[Evolution] Score: {score:.1f} -> XP gained: +{gained_xp} (Total: {self.total_xp})")
        
        self.check_level_up()

    def check_level_up(self):
        # 레벨업 공식: 레벨 * 500 XP 필요
        needed_xp = self.current_level * 500
        if self.total_xp >= needed_xp:
            self.current_level += 1
            msg = f"✨ LEVEL UP! {self.current_level-1} -> {self.current_level} ✨"
            self.experiences.append(f"Level {self.current_level} 달성")
            print("\n" + "*"*30)
            print(msg)
            print("*"*30 + "\n")
