import os
import json
from typing import List
from anthropic import Anthropic
from src.core.models import Scenario, Critique
from src.core.constants import COUNCIL_PERSONAS, HISTORICAL_ART_PERSONAS
from src.core.skills import build_full_system_prompt

class CouncilAgent:
    def __init__(self, is_mock: bool = True, content_mode: str = "wuxia"):
        self.is_mock = is_mock
        self.content_mode = content_mode
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.client = Anthropic(api_key=self.api_key) if not is_mock and self.api_key else None
        self.personas = HISTORICAL_ART_PERSONAS if content_mode == 'historical_art' else COUNCIL_PERSONAS

    def evaluate(self, scenario: Scenario) -> Scenario:
        print(f"[Council] Evaluating scenario: {scenario.title}")
        critiques = []
        total_score = 0
        
        for persona in self.personas:
            if not self.is_mock and self.client is None:
                critique = Critique(persona=persona,score=0.0,
                                  comment="NOT_EVALUATED: no configured independent reviewer",
                                  suggestions=[])
            elif self.is_mock:
                # Never convert synthetic rehearsal into an approval score.
                critique = Critique(
                    persona=persona, score=0.0,
                    comment="NOT_EVALUATED: mock response, no real source or viewer review",
                    suggestions=[]
                )
            else:
                print(f"[Council] {persona} 비평 중...")
                prompt = (f"당신은 '{persona}'입니다. 다음 원고의 결함을 실제 문장으로 반증하세요.\n"
                          f"제목: {scenario.title}\n대본: {scenario.script}\n"
                          "해당 장면, 결함, 검증 가능한 근거, 미확인 항목, 담당자를 명시하세요. "
                          "시청하지 않은 영상/확인하지 않은 사료는 관찰했다고 꾸미지 마세요.")
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=(build_full_system_prompt("council", self.content_mode) if self.content_mode == "historical_art" else f"당신은 무협 시나리오 비평가 {persona}입니다.") +
                           "\n독립 근거가 없으면 score=0. 점수는 승인권이 아님. JSON: " +
                           '{"score": 0, "comment": "실제 근거와 미확인 사항", "suggestions": ["증거가 있는 결함과 최소 수정 범위"]}',
                    messages=[{"role": "user", "content": prompt}]
                )
                
                try:
                    content = response.content[0].text
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    res_json = json.loads(content)
                    critique = Critique(
                        persona=persona,
                        score=res_json["score"] if type(res_json.get("score")) in (int,float) and 0<=res_json["score"]<=10 and res_json.get("comment") else 0.0,
                        comment=res_json.get("comment", "NOT_EVALUATED"),
                        suggestions=res_json.get("suggestions", [])
                    )
                except Exception as e:
                    print(f"[Council Error] {persona} 비평 실패: {e}")
                    critique = Critique(persona=persona, score=0.0, comment="NOT_EVALUATED: 비평 오류", suggestions=[])
            
            critiques.append(critique)
            total_score += critique.score
        
        scenario.critiques = critiques
        scenario.final_score = total_score / len(self.personas)
        
        # The Council may identify defects but cannot authorize production.
        verdict = "NOT_EVALUATED" if self.is_mock else "INDEPENDENT_AND_HUMAN_REVIEW_REQUIRED"
        
        print(f"[Council] Final Average Score: {scenario.final_score:.1f} -> Verdict: {verdict}")
        
        # Review records are diagnostic only; never a source of production approval.
        self._save_critique_to_file(scenario)
        
        return scenario

    def _save_critique_to_file(self, scenario: Scenario):
        from datetime import datetime
        dir_path = "outputs/critiques"
        os.makedirs(dir_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{dir_path}/critique_{timestamp}.json"
        
        save_data = {
            "title": scenario.title,
            "final_score": scenario.final_score,
            "critiques": [c.model_dump() for c in scenario.critiques]
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4, ensure_ascii=False)
        print(f"[Council] Critique archived to {file_path}")
