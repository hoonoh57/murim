import os
import json
import random
from typing import List
from anthropic import Anthropic
from src.core.models import Scenario, Critique
from src.core.constants import COUNCIL_PERSONAS

class CouncilAgent:
    def __init__(self, is_mock: bool = True):
        self.is_mock = is_mock
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.client = Anthropic(api_key=self.api_key) if not is_mock and self.api_key else None
        self.personas = COUNCIL_PERSONAS

    def evaluate(self, scenario: Scenario) -> Scenario:
        print(f"[Council] Evaluating scenario: {scenario.title}")
        critiques = []
        total_score = 0
        
        for persona in self.personas:
            if self.is_mock:
                # 수련 루프에서 점수 변화를 시뮬레이션하기 위해 'Revised' 키워드가 있으면 높은 점수 부여
                # 현실성을 위해 소량의 랜덤 변동(±0.2) 추가
                base_score = 8.5 if "Revised" in scenario.title else 7.8
                score = base_score + random.uniform(-0.2, 0.2)
                critique = Critique(
                    persona=persona,
                    score=score,
                    comment=f"{persona} 입장에서 본 의견입니다. (Mock)",
                    suggestions=["내공 묘사를 더 비장하게", "첫 장면 훅을 더 강하게"]
                )
            else:
                print(f"[Council] {persona} 비평 중...")
                prompt = f"당신은 '{persona}'입니다. 다음 무협 시나리오를 비평하고 0~10점의 점수와 의견을 JSON 형식으로 작성해주세요.\n시나리오 제목: {scenario.title}\n대본: {scenario.script}"
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    system=f"당신은 무협 시나리오 비평가 {persona}입니다. 반드시 {{\"score\": 8, \"comment\": \"...\", \"suggestions\": [\"...\", \"...\"]}} 형식의 JSON으로만 답하세요.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                try:
                    content = response.content[0].text
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    res_json = json.loads(content)
                    critique = Critique(
                        persona=persona,
                        score=res_json.get("score", 7),
                        comment=res_json.get("comment", ""),
                        suggestions=res_json.get("suggestions", [])
                    )
                except Exception as e:
                    print(f"[Council Error] {persona} 비평 실패: {e}")
                    critique = Critique(persona=persona, score=7, comment="비평 오류", suggestions=[])
            
            critiques.append(critique)
            total_score += critique.score
        
        scenario.critiques = critiques
        scenario.final_score = total_score / len(self.personas)
        
        # Verdict Logic
        verdict = "REWORK"
        if scenario.final_score >= 7.5:
            verdict = "GO"
        elif scenario.final_score < 6.0:
            verdict = "KILL"
        
        print(f"[Council] Final Average Score: {scenario.final_score:.1f} -> Verdict: {verdict}")
        
        # Save results
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
