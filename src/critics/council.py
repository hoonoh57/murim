import os
import json
from typing import List
from anthropic import Anthropic
from src.core.models import Scenario, Critique

class CouncilAgent:
    def __init__(self, is_mock: bool = True):
        self.is_mock = is_mock
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.client = Anthropic(api_key=self.api_key) if not is_mock and self.api_key else None
        self.personas = [
            "정통무협 마니아 (고증 중시)",
            "영상 연출가 (비주얼 중시)",
            "대본 작가 (서사 구조 중시)",
            "속도형 시청자 (도파민/자극 중시)",
            "글로벌 팬 (보편적 정서 중시)",
            "전략 마케터 (조회수/바이럴 중시)"
        ]

    def evaluate(self, scenario: Scenario) -> Scenario:
        print(f"[Council] Evaluating scenario: {scenario.title}")
        critiques = []
        total_score = 0
        
        for persona in self.personas:
            if self.is_mock:
                score = 8
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
