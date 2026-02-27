import os
import json
import time

class MockHelper:
    @staticmethod
    def get_mock_path(category, filename):
        path = f"assets/mocks/{category}/{filename}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(f"Mock {category} content for {filename}")
        return path

class ScenarioEngine:
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock
        from src.core.prompts import SYSTEM_PROMPT
        self.system_prompt = SYSTEM_PROMPT

    def generate_episode(self, topic, events):
        if self.is_mock:
            print(f"[MOCK] Generating scenario for: {topic}")
            time.sleep(1)
            return {
                "title": f"MOCK EPISODE: {topic}",
                "script": "천마의 기억이 요동친다. (Mock Script)",
                "scenes": [
                    {"id": "S01", "desc": "Moonlit cliff", "image_prompt": "cinematic cliff", "video_prompt": "Slow zoom on cliff"}
                ]
            }
        # Real API logic here
        return {"status": "success"}

class ImageGenerator:
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock

    def generate(self, prompt, char_ref=None):
        if self.is_mock:
            print(f"[MOCK] Generating image: {prompt[:30]}...")
            return MockHelper.get_mock_path("images", "mock_image.png")
        return "storage_url"

class VideoGenerator:
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock

    def generate_from_image(self, image_url, prompt):
        if self.is_mock:
            print(f"[MOCK] Generating video from: {image_url}")
            return MockHelper.get_mock_path("videos", "mock_video.mp4")
        return "video_url"

class AudioGenerator:
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock

    def tts(self, text, lang="ko"):
        if self.is_mock:
            print(f"[MOCK] Generating TTS ({lang}): {text[:20]}...")
            return MockHelper.get_mock_path("audio", f"mock_tts_{lang}.mp3")
        return "audio_path"
