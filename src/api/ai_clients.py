import os
import json
import time
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class MockHelper:
    @staticmethod
    def get_mock_path(category, filename):
        path = f"assets/mocks/{category}/{filename}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(f"Mock {category} content for {filename}")
        return path

class GeminiFreeClient:
    """Google Gemini 무료 API (Generative AI SDK) 클라이언트"""
    
    def __init__(self, api_key=None, model_name="gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("[WARNING] GOOGLE_API_KEY가 없습니다. Mock 모드로 동작하거나 오류가 발생할 수 있습니다.")
        
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, prompt: str) -> str:
        """배치 프롬프트에 대한 응답을 생성합니다."""
        if not self.api_key:
            return "---[RES-001 | WriterAgent]---\n{\"title\": \"Mock\", \"script\": \"Key missing\"}\n---[END RES-001]---"

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[Gemini ERROR] {e}")
            return f"Error: {e}"

class ScenarioEngine:
# ... (rest of the existing file)
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.client = Anthropic(api_key=self.api_key) if not is_mock and self.api_key else None
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
                    {
                        "id": "S01", 
                        "time_range": "0:00-0:30",
                        "description": "Moonlit cliff", 
                        "camera": "Wide shot",
                        "emotion": "Brave",
                        "image_prompt": "cinematic cliff", 
                        "video_prompt": "Slow zoom on cliff"
                    }
                ]
            }
        
        # Real API Call
        print(f"[API] Calling Anthropic ({self.model}) for: {topic}")
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": f"주제: {topic}\n주요사건: {events}\n위 내용을 바탕으로 JSON 형식으로 시나리오를 작성해줘."}
            ]
        )
        
        # Parse JSON from response
        try:
            # Claude 3 often wraps JSON in quotes or markdown blocks, but we'll try to parse it directly
            content = message.content[0].text
            # Basic cleanup if it's wrapped in ```json ... ```
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception as e:
            print(f"[ERROR] Failed to parse AI response: {e}")
            return {"error": str(e)}

class ImageGenerator:
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock
        self.api_key = api_key or os.getenv("MIDJOURNEY_PROXY_API_KEY")

    def generate(self, prompt, char_ref=None):
        if self.is_mock:
            print(f"[MOCK] Generating image: {prompt[:30]}...")
            return MockHelper.get_mock_path("images", "mock_image.png")
        # MJ API integration would go here
        return "storage_url"

class VideoGenerator:
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock
        self.api_key = api_key or os.getenv("XAI_API_KEY")

    def generate_from_image(self, image_url, prompt):
        if self.is_mock:
            print(f"[MOCK] Generating video from: {image_url}")
            return MockHelper.get_mock_path("videos", "mock_video.mp4")
        # Grok API integration would go here
        return "video_url"

class AudioGenerator:
    def __init__(self, api_key=None, is_mock=True):
        self.is_mock = is_mock
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")

    def tts(self, text, lang="ko"):
        if self.is_mock:
            print(f"[MOCK] Generating TTS ({lang}): {text[:20]}...")
            return MockHelper.get_mock_path("audio", f"mock_tts_{lang}.mp3")
        # ElevenLabs API integration would go here
        return "audio_path"
