import os
import unittest
from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import EvolutionLog, DraftPractice
from src.core.models import Scenario

class MockAgent(BaseAgent):
    def self_practice(self, focus: str):
        # Test implementation
        score_v1 = 7.0
        score_v2 = 8.0
        practice = DraftPractice(
            topic="Test",
            focus_point=focus,
            scenario=Scenario(title="Test", synopsis="Test", script="Test", scenes=[], sound_guide={}),
            self_reflection="Test reflection",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)

class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        # Use a temporary log file for testing
        self.agent = MockAgent(agent_type="test_agent", is_mock=True)
        self.agent.log_file = "outputs/evolution/test_agent_evolution.json"
        if os.path.exists(self.agent.log_file):
            os.remove(self.agent.log_file)
        self.agent.log = EvolutionLog(agent_id="Agent_TEST")

    def test_xp_calculation(self):
        # Level 1, score 8.0, improvement 1.0
        # base_xp = 8 * 20 = 160
        # improvement_bonus = (8-7)*50 = 50
        # total = (160 + 50) * (1.0 - 1*0.1) = 210 * 0.9 = 189
        xp = self.agent.calculate_xp(7.0, 8.0)
        self.assertEqual(xp, 189)

    def test_level_up(self):
        self.agent.log.total_xp = 450
        self.agent.log.current_level = 1
        
        # Adding 100 XP should trigger level up (needed 500)
        practice = DraftPractice(
            topic="Test", focus_point="Test", 
            scenario=Scenario(title="T", synopsis="T", script="T", scenes=[], sound_guide={}),
            self_reflection="R", evolution_step=1
        )
        # We manually add practice with high XP
        self.agent.log.add_practice(practice, 100)
        self.assertEqual(self.agent.log.current_level, 2)

    def test_abc_enforcement(self):
        # Trying to instantiate a class without self_practice should raise TypeError
        with self.assertRaises(TypeError):
            class IncompleteAgent(BaseAgent):
                pass
            IncompleteAgent(agent_type="fail", is_mock=True)

    def tearDown(self):
        if os.path.exists(self.agent.log_file):
            os.remove(self.agent.log_file)

if __name__ == "__main__":
    unittest.main()
