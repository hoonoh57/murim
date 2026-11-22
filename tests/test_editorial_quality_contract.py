"""Creative production authority and historical-vs-Wuxia skill isolation."""
import unittest
from src.core.skills import build_full_system_prompt, load_all_skills_raw
from src.critics.council import CouncilAgent
from src.core.models import Scenario
from src.agents.director import DirectorAgent
from src.agents.writer import WriterAgent
from src.agents.art_direction import ArtDirectionAgent
from src.agents.imaging import ImagingAgent
from src.agents.camera import CameraAgent
from src.agents.video import VideoAgent
from src.agents.audio import AudioAgent
from src.agents.marketing import MarketingAgent
from unittest.mock import patch


class EditorialQualityContractTests(unittest.TestCase):
    def test_default_legacy_skill_aggregate_excludes_cultural_skills(self):
        self.assertEqual(set(load_all_skills_raw()),{"transcendent","story","prompt","sync"})

    def test_historical_writer_does_not_inherit_wuxia_template(self):
        s = build_full_system_prompt("writer", content_mode="historical_art")
        self.assertIn("사료 기반 영화적 역사서사", s)
        self.assertIn("시청자의 귀한 시간을", s)
        self.assertNotIn("천마혈영검법", s)
        self.assertNotIn("15비트 구조를 반드시", s)

    def test_reviewer_prompts_are_not_unbounded_rewriters(self):
        p = build_full_system_prompt("council", content_mode="historical_art")
        self.assertIn("외부 Gemini", p)
        self.assertIn("증거", p)
        self.assertIn("독립", p)

    def test_historical_writer_uses_historical_council(self):
        w=WriterAgent(is_mock=True, content_mode="historical_art")
        self.assertIn("사료",w.council.personas[0])
        self.assertNotIn("천마",w.system_prompt)

    def test_missing_skill_is_not_silently_ignored(self):
        with patch("src.core.skills.SKILLS_DIR","/nonexistent-creative-skill-source"):
            with self.assertRaises(FileNotFoundError):
                build_full_system_prompt("writer", content_mode="historical_art")

    def test_cultural_art_roles_do_not_apply_wuxia_generation_shortcuts(self):
        art=ArtDirectionAgent(is_mock=True, content_mode="historical_art")
        self.assertIn("미장센",art.system_prompt)
        with self.assertRaises(ValueError): art.design_style_guide("세한도 작품")
        with self.assertRaises(ValueError): art.get_emotional_palette("정")
        camera=CameraAgent(is_mock=True, content_mode="historical_art")
        with self.assertRaises(ValueError): camera.plan_camera_angles([])
        imaging=ImagingAgent(is_mock=True, content_mode="historical_art")
        with self.assertRaises(ValueError): imaging.generate("painting of the artifact")
        with self.assertRaises(ValueError): imaging.get_negative_prompt()
        with self.assertRaises(ValueError): imaging.revise_prompt("artifact",[])
        video=VideoAgent(is_mock=True, content_mode="historical_art")
        with self.assertRaises(ValueError): video.generate_from_image("dummy.png","generic zoom")
        with self.assertRaises(ValueError): video.generate_with_sync("dummy.png","generic zoom")
        audio=AudioAgent(is_mock=True, content_mode="historical_art")
        with self.assertRaises(ValueError): audio.validate_narration_length("확정 원고",12.0)
        with self.assertRaises(ValueError): audio.tts("확정 원고")
        with self.assertRaises(ValueError): audio.generate_bgm("중후한")
        with self.assertRaises(ValueError): audio.generate_sfx("긴장")
        marketing=MarketingAgent(is_mock=True, content_mode="historical_art")
        from src.core.models import Scenario
        with self.assertRaises(ValueError):
            marketing.generate_assets(Scenario(title="세한도",synopsis="",script="",scenes=[],sound_guide={}))

    def test_unknown_content_mode_fails_closed(self):
        with self.assertRaises(ValueError):
            build_full_system_prompt("writer", content_mode="guess")
        with self.assertRaises(ValueError):
            build_full_system_prompt("unknown", content_mode="historical_art")

    def test_mock_council_cannot_grant_approval(self):
        sample=Scenario(title="Revised", synopsis="artifact", script="text", scenes=[], sound_guide={})
        result=CouncilAgent(is_mock=True,content_mode="historical_art").evaluate(sample)
        self.assertEqual(result.final_score,0.0)
        self.assertTrue(all(c.score==0.0 for c in result.critiques))
        self.assertEqual(len(result.critiques),6)

    def test_missing_verified_project_cannot_start_production(self):
        director=DirectorAgent(is_mock=False)
        result=director.orchestrate_episode("topic","events",{})
        self.assertIsNone(result)

if __name__=="__main__":
    unittest.main()
