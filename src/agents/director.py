from typing import List, Dict
from src.agents.base_agent import BaseAgent
from src.core.models import EpisodeRequest, Scenario
from src.evolution.skill_tracker import DraftPractice, EvolutionLog

class DirectorAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="director", is_mock=is_mock)
        
    def check_balance(self, agents: Dict[str, BaseAgent]) -> dict:
        """전 에이전트 레벨 조회 -> 편차 분석 -> 훈련 명령 생성"""
        print("\n[Director] Checking ecosystem balance...")
        levels = {name: agent.get_level() for name, agent in agents.items()}
        
        max_lv = max(levels.values())
        min_lv = min(levels.values())
        gap = max_lv - min_lv
        avg = sum(levels.values()) / len(levels)
        
        training_targets = []
        for name, lv in levels.items():
            if lv < avg - 0.5:
                training_targets.append({
                    "agent": name,
                    "current_level": lv,
                    "priority": "HIGH" if lv == min_lv else "MEDIUM"
                })
        
        report = {
            "levels": levels,
            "gap": gap,
            "balanced": (gap <= 1),
            "training_targets": training_targets
        }
        return report

    def auto_train(self, report: dict, agents: Dict[str, BaseAgent]):
        """밸런스 보고서에 따른 자동 훈련 실행"""
        if not report["training_targets"]:
            print("[Director] All agents are balanced. No auto-training needed.")
            return

        print(f"[Director] Auto-training initiated for {len(report['training_targets'])} agents.")
        for target in report["training_targets"]:
            agent_name = target["agent"]
            agent = agents.get(agent_name)
            if agent:
                print(f" -> Training {agent_name} (Priority: {target['priority']})")
                agent.self_practice(focus="Ecosystem Balance Optimization")

    def orchestrate_episode(self, topic: str, events: str, agents: Dict[str, BaseAgent]):
        """전체 파이프라인 조율 (기획 -> 비평 -> 수정 -> 리소스 제작 -> 마케팅)"""
        from src.core.models import ProductionResult
        print(f"\n[Director] Starting orchestration for: {topic}")
        
        # 0. 에이전트 확보
        writer = agents.get("writer")
        art_dir = agents.get("art_direction")
        camera = agents.get("camera")
        imaging = agents.get("imaging")
        video = agents.get("video")
        audio = agents.get("audio")
        marketing = agents.get("marketing")

        if not writer: 
            print("[Director] Error: WriterAgent not found.")
            return None
        
        # 1. 시나리오 생성 및 품질 관리 (Writer + Council)
        print("\n[GATE 1] Scenario Generation & Review")
        scenario = writer.write_scenario(EpisodeRequest(topic=topic, events=events))
        
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            attempts += 1
            print(f"\n[Director] Quality Review - Attempt {attempts}/{max_attempts}")
            scenario = writer.council.evaluate(scenario)
            
            if scenario.final_score >= 7.5:
                print(f"[Director] Quality approved ({scenario.final_score:.1f}).")
                break
            
            if attempts < max_attempts:
                print(f"[Director] Quality ({scenario.final_score:.1f}) below threshold (7.5). Ordering REWORK.")
                scenario = writer.revise_scenario(scenario, scenario.critiques)
            else:
                print(f"[Director] Maximum rework attempts reached. Current Score: {scenario.final_score:.1f}")

        if scenario.final_score < 6.0:
            print("[Director] KILL: Final quality unacceptable. Production cancelled.")
            return None

        # 2. 프로덕션 기획 (Art Direction, Camera)
        print("\n[GATE 2] Production Planning")
        style_guide = None
        camera_plans = []
        
        if art_dir:
            style_guide = art_dir.design_style_guide(scenario.synopsis)
            print(f" -> Style Guide Color: {style_guide.get('palette')}")
        
        if camera:
            camera_plans = camera.plan_camera_angles(scenario.scenes)
            print(f" -> Camera Planning completed for {len(camera_plans)} scenes.")

        # 3. 리소스 제작 (Imaging, Video, Audio)
        print("\n[GATE 3] Resource Production")
        image_paths = []
        video_paths = []
        audio_path = None
        
        if imaging and video:
            for i, scene in enumerate(scenario.scenes):
                print(f" -> Processing {scene.id}...")
                plan = camera_plans[i] if i < len(camera_plans) else None
                img_path = imaging.generate(scene.image_prompt, style_guide=style_guide)
                vid_path = video.generate_from_image(img_path, scene.video_prompt, camera_plan=plan)
                image_paths.append(img_path)
                video_paths.append(vid_path)
        
        if audio:
            audio_path = audio.tts(scenario.script)
            print(f" -> Final Audio created at: {audio_path}")

        # 4. 마케팅 (Marketing)
        print("\n[GATE 4] Marketing & Distribution")
        marketing_meta = None
        if marketing:
            marketing_meta = marketing.generate_assets(scenario)
            print(f" -> Marketing Bundle: {marketing_meta.get('title')}")

        # 5. 결과 정리
        scenario.assets = {
            "images": image_paths,
            "videos": video_paths,
            "audio": audio_path
        }
        
        result = ProductionResult(
            scenario=scenario,
            image_paths=image_paths,
            video_paths=video_paths,
            audio_path=audio_path,
            marketing_meta=marketing_meta
        )

        print(f"\n[Director] Episode '{scenario.title}' processing complete!")
        return result

    def self_practice(self, focus: str):
        print(f"[Director] Self-practice: Optimizing orchestration rules for {focus}")
        # 감독 보너스는 오케스트레이션 성공률 등으로 계산 가능하나, 현재는 시뮬레이션
        score_v1 = 7.0 + (self.log.current_level * 0.1)
        score_v2 = min(9.5, score_v1 + 0.5)
        
        practice = DraftPractice(
            topic="Orchestration Optimization",
            focus_point=focus,
            scenario=Scenario(title="N/A", synopsis="N/A", script="N/A", scenes=[], sound_guide={}),
            self_reflection=f"감독 레벨 {self.log.current_level} 수련 완료. 조율 로직 최적화.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        return "Director self-optimization complete."
