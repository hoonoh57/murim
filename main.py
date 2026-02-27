import os
import sys
from src.api.ai_clients import ScenarioEngine, ImageGenerator, VideoGenerator, AudioGenerator

def main():
    print("\n" + "="*50)
    print("   MURIM AI CONTENT FACTORY - INTERACTIVE MODE")
    print("="*50)
    
    # 설정 초기화
    scenario_engine = ScenarioEngine(is_mock=True)
    img_gen = ImageGenerator(is_mock=True)
    vid_gen = VideoGenerator(is_mock=True)
    audio_gen = AudioGenerator(is_mock=True)

    # UI: 사용자 입력 받기
    print("\n[STEP 1] 에피소드 기획")
    topic = input("에피소드 주제를 입력하세요 (예: 천마의 회귀): ")
    events = input("주요 사건들을 입력하세요 (예: 경맥 돌파, 혈귀와 대면): ")

    # 1. 시나리오 생성 및 출력
    print("\n" + "-"*30)
    print("AI 시나리오 생성 중...")
    episode = scenario_engine.generate_episode(topic, events)
    
    print("\n[AI 생성 결과]")
    print(f"▶ 제목: {episode['title']}")
    print(f"▶ 대본: {episode['script']}")
    print(f"▶ 씬(Scene) 정보:")
    for scene in episode['scenes']:
        print(f"   - {scene['id']}: {scene['desc']}")
        print(f"     * Image Prompt: {scene['image_prompt']}")
        print(f"     * Video Prompt: {scene['video_prompt']}")
    print("-"*30)

    # UI: 작업 진행 여부 확인 (Human-in-the-loop)
    choice = input("\n이 시나리오로 작업을 계속 진행할까요? (y/n): ").lower()
    if choice != 'y':
        print("작업을 중단합니다. 다시 실행해 주세요.")
        return

    # 2. 이미지 및 영상 생성 시뮬레이션
    print("\n[STEP 2] 비주얼 리소스 생성")
    for scene in episode['scenes']:
        print(f"\n--- {scene['id']} 생성 중 ---")
        img_path = img_gen.generate(scene['image_prompt'])
        vid_path = vid_gen.generate_from_image(img_path, scene['video_prompt'])
        print(f"-> 완료: {vid_path}")
    
    # 3. 음성 생성
    print("\n[STEP 3] 오디오 생성")
    audio_path = audio_gen.tts(episode['script'])
    print(f"-> 완료: {audio_path}")

    print("\n" + "="*50)
    print("   [SUCCESS] 모든 리소스 생성 완료!")
    print(f"   위치: {os.path.abspath('assets/mocks/')}")
    print("="*50)
    print("\nTip: 실제 API 연결 시에도 이 인터페이스를 통해 '수동 검증'이 가능합니다.")

if __name__ == "__main__":
    main()
