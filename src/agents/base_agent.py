import os
import json
from anthropic import Anthropic
from src.evolution.skill_tracker import EvolutionLog, DraftPractice
from pydantic import BaseModel

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, agent_type: str, is_mock: bool = True):
        self.agent_type = agent_type
        self.is_mock = is_mock
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.client = Anthropic(api_key=self.api_key) if not is_mock and self.api_key else None
        
        # Deferred import to prevent circular dependency
        from src.critics.council import CouncilAgent
        self.council = CouncilAgent(is_mock=is_mock)
        
        # Evolution Tracking
        self.log_file = f"outputs/evolution/{self.agent_type}_evolution.json"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.log = self._load_log()
        self.log.agent_id = f"Agent_{self.agent_type.upper()}"

    def _load_log(self) -> EvolutionLog:
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return EvolutionLog(**data)
        return EvolutionLog(agent_id=f"Agent_{self.agent_type.upper()}")

    def save_log(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.log.model_dump(), f, indent=4, ensure_ascii=False)

    def get_level(self) -> int:
        return self.log.current_level

    @abstractmethod
    def self_practice(self, focus: str):
        """Must be implemented by subclasses"""
        pass

    def calculate_xp(self, score_v1: float, score_v2: float) -> int:
        level = self.get_level()
        base_xp = int(score_v2 * 20)
        improvement_bonus = max(0, int((score_v2 - score_v1) * 50))
        difficulty_factor = max(0.3, 1.0 - (level * 0.1))
        
        total = int((base_xp + improvement_bonus) * difficulty_factor)
        return total

    def add_experience(self, practice: DraftPractice, score_v1: float, score_v2: float):
        gained_xp = self.calculate_xp(score_v1, score_v2)
        self.log.add_practice(practice, gained_xp)
        self.save_log()

    def _generate_reflection(self, scenario, score_v1: float, score_v2: float):
        """AI 또는 MOCK을 사용하여 수련 결과에 대한 자기 성찰을 생성합니다."""
        if self.is_mock:
            return f"{self.agent_type} 분야 수련을 완료했습니다. 점수 향상: {score_v1:.1f} -> {score_v2:.1f}. 다음 수련에서는 고도화된 스킬을 연마하겠습니다."
            
        prompt = f"""
        당신은 {self.agent_type} 분야에서 자가 수련 중인 에이전트입니다.
        이번 수련의 결과는 다음과 같습니다:
        - 초기 점수: {score_v1:.1f}
        - 최종 점수: {score_v2:.1f}
        
        비평 위원회의 피드백을 통해 본인이 무엇을 배웠고 어떤 점이 개선되었는지, 
        그리고 다음 수련에서는 무엇에 집중할지 1-2문장으로 한국어로 성찰하세요.
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
