import os
import json
from anthropic import Anthropic
from src.critics.council import CouncilAgent
from src.evolution.skill_tracker import EvolutionLog, DraftPractice
from src.api.ai_clients import ScenarioEngine
from pydantic import BaseModel

class BaseAgent:
    def __init__(self, agent_type: str, is_mock: bool = True):
        self.agent_type = agent_type
        self.is_mock = is_mock
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.client = Anthropic(api_key=self.api_key) if not is_mock and self.api_key else None
        self.council = CouncilAgent(is_mock=is_mock)
        
        # Evolution Tracking
        self.log_file = f"outputs/evolution/{self.agent_type}_evolution.json"
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.log = self._load_log()

    def _load_log(self) -> EvolutionLog:
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return EvolutionLog(**data)
        return EvolutionLog(writer_id=f"Agent_{self.agent_type}")

    def save_log(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.log.model_dump(), f, indent=4, ensure_ascii=False)

    def get_level(self) -> int:
        return self.log.current_level

    def self_practice(self, focus: str):
        """Must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement self_practice")

    def calculate_xp(self, score_v1: float, score_v2: float) -> int:
        """
        기본 XP: score_v2 * 20
        개선 보너스: (score_v2 - score_v1) * 50 (마이너스면 0)
        난이도 보정: level이 높을수록 XP 획득 어려움
        """
        level = self.get_level()
        base_xp = int(score_v2 * 20)
        improvement_bonus = max(0, int((score_v2 - score_v1) * 50))
        difficulty_factor = max(0.3, 1.0 - (level * 0.1))
        
        total = int((base_xp + improvement_bonus) * difficulty_factor)
        return total

    def add_experience(self, practice: DraftPractice, score_v1: float, score_v2: float):
        gained_xp = self.calculate_xp(score_v1, score_v2)
        # EvolutionLog의 add_practice는 이제 인자가 달라졌으므로 수정 필여할 수 있음
        # 여기서는 log 객체에 직접 반영
        self.log.practice_history.append(practice)
        self.log.total_practices += 1
        self.log.total_xp += gained_xp
        print(f"[{self.agent_type.upper()} EVOLUTION] XP Gained: +{gained_xp} (Total: {self.log.total_xp})")
        self.log.check_level_up()
        self.save_log()
