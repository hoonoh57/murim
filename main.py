import sys
from src.core.models import EpisodeRequest
from src.agents.writer import WriterAgent
from src.critics.council import CouncilAgent
from src.api.ai_clients import ImageGenerator, VideoGenerator, AudioGenerator

def main():
    print("\n" + "="*50)
    print("   MURIM AI FACTORY - AGENT ORCHESTRATION")
    print("="*50)
    
    try:
        # 에이전트 초기화
        # IS_MOCK 상태 확인 (기본 True)
        import os
        from dotenv import load_dotenv
        load_dotenv()
        is_mock = os.getenv("IS_MOCK", "true").lower() == "true"
        
        writer = WriterAgent(is_mock=is_mock)
        council = CouncilAgent(is_mock=is_mock)
        img_gen = ImageGenerator(is_mock=is_mock)
        vid_gen = VideoGenerator(is_mock=is_mock)
        audio_gen = AudioGenerator(is_mock=is_mock)

        # 메뉴 선택
        print("\n[메뉴 선택]")
        print(" 1. 정식 에피소드 제작 (Production)")
        print(" 2. 작가 자가 습작 및 진화 (Training/習作)")
        mode = input("\n번호를 선택하세요: ")

        if mode == "2":
            print("\n" + "-"*30)
            print("   WRITER SELF-EVOLUTION MODE")
            print("-"*30)
            focus = input("이번 습작의 집중 포인트를 입력하세요 (예: 비장한 대사, 내공 묘사): ") or "정통 무협의 분위기"
            result = writer.self_practice(focus)
            print(f"\n{result}")
            return

        # 1. 시나리오 생성 (Writer Agent)
        print(f"\n[STEP 1] 에피소드 기획 및 집필 (Mock: {is_mock})")
        topic = input("주제: ") or "천마의 회귀"
        events = input("요약: ") or "1화: 회귀와 첫 번째 경맥 돌파"
        
        request = EpisodeRequest(topic=topic, events=events)
        scenario = writer.write_scenario(request)
        
        if scenario.title == "Error":
            print("시나리오 생성 중 오류가 발생했습니다. 프로그램을 종료합니다.")
            return

        # 2. 비평 (Council Agent)
        print("\n[STEP 2] 6인 비평위원회 평가")
        scenario = council.evaluate(scenario)
        
        print("\n" + "-"*30)
        print(f"⭐ 최종 평점: {scenario.final_score:.1f}/10")
        
        verdict = "REWORK"
        if scenario.final_score >= 7.5: verdict = "GO (제작 승인)"
        elif scenario.final_score < 6.0: verdict = "KILL (폐기)"
        else: verdict = "REWORK (보완 필요)"
        
        print(f"📢 위원회 판정: {verdict}")
        print("-"*30)
        
        for cr in scenario.critiques:
            print(f" - [{cr.persona}] {cr.score}점: {cr.comment}")

        if "GO" not in verdict:
            print("\n판정 결과에 따라 작업을 중단합니다.")
            return

        choice = input("\n이대로 제작을 진행할까요? (y/n): ").lower()
        if choice != 'y': return

        # 3. 비주얼 및 오디오 생성
        print("\n[STEP 3] 리소스 제작")
        for scene in scenario.scenes:
            print(f"\n--- {scene.id} 제작: {scene.description} ---")
            img_path = img_gen.generate(scene.image_prompt)
            vid_path = vid_gen.generate_from_image(img_path, scene.video_prompt)
            print(f"-> 비디오 경로: {vid_path}")
        
        audio_path = audio_gen.tts(scenario.script)
        print(f"-> 오디오 경로: {audio_path}")

        print("\n" + "="*50)
        print("   [SUCCESS] 에이전트 협업 완료!")
        print("="*50)

    except Exception as e:
        print(f"\n[CRITICAL ERROR] 시스템 가동 중 예상치 못한 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
