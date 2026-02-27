from src.agents.director import DirectorAgent
from src.agents.writer import WriterAgent
from src.critics.council import CouncilAgent
from src.api.ai_clients import ImageGenerator, VideoGenerator, AudioGenerator

def main():
    print("\n" + "="*50)
    print("   MURIM AI FACTORY - AGENT ORCHESTRATION")
    print("="*50)
    
    try:
        # 에이전트 초기화
        import os
        from dotenv import load_dotenv
        load_dotenv()
        is_mock = os.getenv("IS_MOCK", "true").lower() == "true"
        
        director = DirectorAgent(is_mock=is_mock)
        writer = WriterAgent(is_mock=is_mock)
        img_gen = ImageGenerator(is_mock=is_mock)
        vid_gen = VideoGenerator(is_mock=is_mock)
        audio_gen = AudioGenerator(is_mock=is_mock)

        agents = {"writer": writer, "director": director} # 추후 확장

        # 메뉴 선택
        print("\n[메뉴 선택]")
        print(" 1. 정식 에피소드 제작 (Production)")
        print(" 2. 작가 자가 습작 및 진화 (Training/習作)")
        print(" 3. 시스템 밸런스 체크 (Balance Check)")
        mode = input("\n번호를 선택하세요: ")

        if mode == "3":
            report = director.check_balance(agents)
            print(f"\n[Balance Report] Gap: {report['gap']}, Balanced: {report['balanced']}")
            for target in report['training_targets']:
                print(f" -> Training required for: {target['agent']} (Priority: {target['priority']})")
            return

        if mode == "2":
            print("\n" + "-"*30)
            print("   WRITER SELF-EVOLUTION MODE")
            print("-"*30)
            focus = input("이번 습작의 집중 포인트를 입력하세요: ") or "정통 무협의 분위기"
            result = writer.self_practice(focus)
            print(f"\n{result}")
            return

        # 1. 정식 제작 (Director Orchestration)
        print(f"\n[STEP 1] 에피소드 기획 (Director: {is_mock})")
        topic = input("주제: ") or "천마의 회귀"
        events = input("요약: ") or "1화: 회귀와 첫 번째 경맥 돌파"
        
        scenario = director.orchestrate_episode(topic, events, agents)
        
        if not scenario:
            print("제작이 중단되었습니다.")
            return

        # 3. 비주얼 및 오디오 생성 (기존 로직 유지, 추후 에이전트로 전환)
        print("\n[STEP 3] 리소스 제작")
        choice = input("\n리소스를 제작할까요? (y/n): ").lower()
        if choice != 'y': return

        for scene in scenario.scenes:
            print(f"\n--- {scene.id} 제작 ---")
            img_path = img_gen.generate(scene.image_prompt)
            vid_path = vid_gen.generate_from_image(img_path, scene.video_prompt)
        
        audio_path = audio_gen.tts(scenario.script)
        print(f"-> 오디오 경로: {audio_path}")

        print("\n" + "="*50)
        print("   [SUCCESS] 에피소드 제작 완료!")
        print("="*50)

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
