# Murim AI Content Factory 🏯

AI 기술을 활용한 정통무협 유튜브 콘텐츠의 완전 자동화 제작 시스템입니다.

## 🚀 개요
이 프로젝트는 시나리오 작성, 이미지 및 영상 생성, 성우 더빙, 그리고 최종 영상 편집까지의 전 과정을 멀티 에이전트 시스템을 통해 자동화하는 것을 목표로 합니다.

## 🛠 주요 기능
- **멀티 에이전트 파이프라인**: 작가, 비평위원회, 감독 에이전트 간의 협업
- **캐릭터 일관성 유지**: Midjourney --cref 및 --oref 기반 비주얼 생성
- **다국어 자동 확장**: 하나의 대본으로 5개국어 이상의 나레이션 및 자막 자동 생성
- **GATE 검증 시스템**: 제작 단계별 휴먼-인-더-루프(Human-in-the-loop) 품질 검증

## 📦 설치 방법
1. 저장소 클론:
   ```bash
   git clone https://github.com/hoonoh57/murim.git
   cd murim
   ```
2. 환경 설정:
   ```bash
   cp .env.example .env
   # .env 파일에 API 키 입력
   ```
3. 라이브러리 설치:
   ```bash
   pip install -e .
   ```

## 🎮 실행 방법
```bash
python main.py
```

## 🗺 로드맵
- **Phase 0**: 인프라 및 리포 정리 (진행 중)
- **Phase 1**: 에이전트 기반 오케스트레이션 구현
- **Phase 2**: 실제 시나리오 및 영상 제작 (GATE 검증)
- **Phase 3**: 다국어 채널 업로드 및 마케팅 자동화
