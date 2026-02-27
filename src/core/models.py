from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    id: str
    time_range: str
    description: str
    camera: str
    emotion: str
    image_prompt: str
    video_prompt: str

class Critique(BaseModel):
    persona: str
    score: int = Field(ge=0, le=10)
    comment: str
    suggestions: List[str]

class Scenario(BaseModel):
    title: str
    synopsis: str
    script: str
    scenes: List[Scene]
    sound_guide: Dict[str, str]
    critiques: Optional[List[Critique]] = None
    final_score: Optional[float] = None
    assets: Optional[Dict] = None

class EpisodeRequest(BaseModel):
    topic: str
    events: str
    version: int = 1

class ProductionResult(BaseModel):
    scenario: Scenario
    image_paths: List[str] = []
    video_paths: List[str] = []
    audio_path: Optional[str] = None
    marketing_meta: Optional[Dict] = None
    status: str = "success"
