import os
import traceback
from dotenv import load_dotenv

from src.agents.director import DirectorAgent
from src.agents.writer import WriterAgent
from src.agents.imaging import ImagingAgent
from src.agents.video import VideoAgent
from src.agents.audio import AudioAgent
from src.agents.camera import CameraAgent
from src.agents.art_direction import ArtDirectionAgent
from src.agents.marketing import MarketingAgent

from src.critics.council import CouncilAgent
from src.api.ai_clients import ImageGenerator, VideoGenerator, AudioGenerator
from src.core.models import EpisodeRequest

def main():
    print("\n" + "="*50)
    print("   MURIM AI FACTORY - AGENT ORCHESTRATION")
    print("="*50)
    
    try:
        load_dotenv()
        is_mock = os.getenv("IS_MOCK", "true").lower() == "true"
        
        director = DirectorAgent(is_mock=is_mock)
        writer = WriterAgent(is_mock=is_mock)
        imaging = ImagingAgent(is_mock=is_mock)
        video = VideoAgent(is_mock=is_mock)
        audio = AudioAgent(is_mock=is_mock)
        camera = CameraAgent(is_mock=is_mock)
        art_dir = ArtDirectionAgent(is_mock=is_mock)
        marketing = MarketingAgent(is_mock=is_mock)

        agents = {
            "director": director,
            "writer": writer,
            "imaging": imaging,
            "video": video,
            "audio": audio,
            "camera": camera,
            "art_direction": art_dir,
            "marketing": marketing
        }

        # 메뉴 선택
        print("\n[메뉴 선택]")
        print(" 1. 정식 에피소드 제작 (Production)")
        print(" 2. 작가 자가 습작 및 진화 (Training/習作)")
        print(" 3. 시스템 밸런스 체크 및 자동 훈련 (Balance & Auto-Train)")
        mode = input("\n번호를 선택하세요: ")

        if mode == "3":
            report = director.check_balance(agents)
            print(f"\n[Balance Report] Gap: {report['gap']}, Balanced: {report['balanced']}")
            for target in report['training_targets']:
                print(f" -> Training required for: {target['agent']} (Priority: {target['priority']})")
            
            if not report['balanced']:
                do_train = input("\n부족한 에이전트를 자동 습작 시킬까요? (y/n): ").lower()
                if do_train == 'y':
                    director.auto_train(report, agents)
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
        print(f"\n[STEP 1] 에피소드 제작 개시 (Director: {is_mock})")
        topic = input("주제: ") or "천마의 회귀"
        events = input("요약: ") or "1화: 회귀와 첫 번째 경맥 돌파"
        
        scenario = director.orchestrate_episode(topic, events, agents)
        
        if scenario:
            print("\n" + "="*50)
            print(f"   [SUCCESS] '{scenario.title}' 제작 및 배포 완료!")
            print("="*50)
        else:
            print("\n[FAIL] 제작 진행 중 중단되었습니다.")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
