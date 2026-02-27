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
