"""
WAN 2.2 vs LTX-2 비디오 품질 비교 실행기
사용법: python compare_videos.py
"""

from src.pipeline.video_comparator import VideoComparator

EPISODE_DIR = r"outputs\ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846"

def main():
    comparator = VideoComparator(EPISODE_DIR)

    # S01 한 장면만 먼저 테스트 (두 모델 비교)
    print("Phase 1: S01 테스트 생성")
    comparator.run_comparison(
        scenes=["S01"],
        models=["wan22", "ltx2"],
        width=512,
        height=320,
        frames=41,
    )

    # 결과 확인 후 전체 장면 생성
    # print("Phase 2: 전체 장면 생성")
    # comparator.run_comparison(
    #     scenes=None,  # 전체
    #     models=["wan22", "ltx2"],
    #     width=512,
    #     height=320,
    #     frames=41,
    # )

if __name__ == "__main__":
    main()
