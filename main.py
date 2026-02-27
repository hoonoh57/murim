from src.core.models import EpisodeRequest
from src.agents.writer import WriterAgent, CouncilAgent
from src.api.ai_clients import ImageGenerator, VideoGenerator, AudioGenerator

def main():
    print("\n" + "="*50)
    print("   MURIM AI FACTORY - AGENT ORCHESTRATION")
    print("="*50)
    
    # 에이전트 초기화
    writer = WriterAgent(is_mock=True)
    council = CouncilAgent()
    img_gen = ImageGenerator(is_mock=True)
    vid_gen = VideoGenerator(is_mock=True)
    audio_gen = AudioGenerator(is_mock=True)

    # 1. 시나리오 생성 (Writer Agent)
    print("\n[STEP 1] 에피소드 기획 및 집필")
    topic = input("주제: ") or "천마의 회귀"
    events = input("요약: ") or "1화: 회귀와 첫 번째 경맥 돌파"
    
    request = EpisodeRequest(topic=topic, events=events)
    scenario = writer.write_scenario(request)
    
    # 2. 비평 (Council Agent)
    print("\n[STEP 2] 6인 비평위원회 평가")
    scenario = council.evaluate(scenario)
    
    print("\n[비평 결과 요약]")
    print(f"⭐ 최종 평점: {scenario.final_score:.1f}/10")
    for cr in scenario.critiques[:3]: # 상위 3개만 표시
        print(f" - [{cr['persona']}] {cr['score']}점: {cr['comment']}")

    choice = input("\n이대로 제작을 진행할까요? (y/n): ").lower()
    if choice != 'y': return

    # 3. 비주얼 및 오디오 생성
    print("\n[STEP 3] 리소스 제작")
    for scene in scenario.scenes:
        print(f"\n--- {scene.id} 제작 ---")
        img_path = img_gen.generate(scene.image_prompt)
        vid_path = vid_gen.generate_from_image(img_path, scene.video_prompt)
    
    audio_path = audio_gen.tts(scenario.script)

    print("\n" + "="*50)
    print("   [SUCCESS] 에이전트 협업 완료!")
    print("="*50)

if __name__ == "__main__":
    main()
