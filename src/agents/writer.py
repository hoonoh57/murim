import os
import json
from typing import List
from src.core.models import Scenario, Scene, EpisodeRequest
from src.api.ai_clients import ScenarioEngine

class WriterAgent:
    def __init__(self, is_mock: bool = True):
        self.engine = ScenarioEngine(is_mock=is_mock)
        
    def write_scenario(self, request: EpisodeRequest) -> Scenario:
        print(f"[Writer] Writing scenario for topic: {request.topic}")
        raw_data = self.engine.generate_episode(request.topic, request.events)
        
        if "error" in raw_data:
            print(f"[ERROR] WriterAgent failed: {raw_data['error']}")
            return Scenario(title="Error", synopsis="", script="", scenes=[], sound_guide={})

        # Correctly parse scenes as Scene objects
        scenes_data = raw_data.get("scenes", [])
        parsed_scenes = [Scene(**s) for s in scenes_data]
        
        return Scenario(
            title=raw_data.get("title", request.topic),
            synopsis=request.events,
            script=raw_data.get("script", ""),
            scenes=parsed_scenes,
            sound_guide=raw_data.get("sound_guide", {"bgm": "Epic Wuxia", "fx": "Sword Clashing"})
        )
