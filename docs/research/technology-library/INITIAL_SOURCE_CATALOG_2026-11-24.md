# 최신 제작기술 연구 초기 자료원 및 우선 후보

2026-11-24 조회 | SOURCE_CATALOG_ONLY | 실제 강의 전편 관측/재현/벤치마크 NOT_RUN
공개 공식 자료와 연구 원출처 중심. 최신 버전 단정이 아니라 조회 당시 확인한 발표/자료 후보이며 원본 릴리스와 요청 시점 상태를 다시 확인한다.

| ID | 출처/자료 | 확인한 내용 또는 조사 대상 | 상태 |
|---|---|---|---|
| T001 | [LTX-2.5 in ComfyUI: The Upgrade Guide](https://www.youtube.com/watch?v=Sl0jn8ucDqE) | 실제 LTX-2.5 업그레이드 강의. 노드·가중치·설정·실제 출력 조건 추출 우선 | VIDEO_DISCOVERED |
| T002 | [LTX-2 공식 releases](https://github.com/Lightricks/LTX-2/releases), [공식 changelog](https://github.com/Lightricks/LTX-2/blob/main/CHANGELOG.md) | inference, sampler/커널 등 변경과 버전별 결과 차이·호환 확인 | DOCUMENT_DISCOVERED |
| T003 | [ComfyUI 공식 releases](https://github.com/Comfy-Org/ComfyUI/releases), [공식 workflow templates](https://comfy.org/workflows) | 2026-11-18 release 기록 발견. 노드/메모리/호환 및 template 재사용 조사 | DOCUMENT_DISCOVERED |
| T004 | [Runway Academy](https://academy.runwayml.com/), [Workflows](https://help.runwayml.com/hc/en-us/articles/45763528999699-Introduction-to-Workflows) | 실제 단편·카메라·캐릭터·반복 제작 교육. LLM/영상/오디오·편집 노드 조합 | DOCUMENT_DISCOVERED |
| T005 | [Runway changelog](https://runway.com/changelog), [Agent 공식 가이드](https://help.runwayml.com/hc/en-us/articles/51601639579667-Creating-with-Runway-Agent) | 업데이트 및 자동 멀티쇼트/모델 선택/편집 제공 범위 비교 | DOCUMENT_DISCOVERED |
| T006 | [Google Flow 2026-11-12 신규 도구](https://blog.google/innovation-and-ai/models-and-research/google-labs/new-google-flow-tools/) | 동일 인물의 나이 변화, 한 take에서 여러 각도 등 발표 기능. 정체성/연기 유지 실증 필요 | PUBLISHER_CLAIM_ONLY |
| T007 | [Google Flow/Flow Music 2026-11-19 제작 사례](https://blog.google/innovation-and-ai/models-and-research/google-labs/flow-and-flow-music-session-artists/) | 음악 및 영상 전문가의 맞춤 도구/워크플로 연구 | DOCUMENT_DISCOVERED |
| T008 | [Blender Studio](https://studio.blender.org/welcome/) | 실제 전문 CG 제작·애니메이션/Grease Pencil 기법. 2026-11-17 기술 글 발견 | DOCUMENT_DISCOVERED |
| T009 | [NVIDIA ComfyUI creator workflows](https://developer.nvidia.com/blog/how-to-build-run-and-scale-high-quality-creator-workflows-in-comfyui/) | RTX 로컬 워크플로, 모델·리소스 최적화. 사용자 8GB 환경 실증 필요 | PUBLISHER_CLAIM_ONLY |
| T010 | [CamPilot](https://arxiv.org/abs/2609.10943), [Stable Cinemetrics](https://arxiv.org/abs/2509.26555) | 카메라 전문 제어/영화적 평가 연구. 논문 주장과 실제 우리 품질 분리 | RESEARCH_CANDIDATE |
| T011 | [CineRecon](https://arxiv.org/abs/2610.16577) | 참조 영상의 편집 가능한 3D 동적 장면 복원 평가 연구 | RESEARCH_CANDIDATE |

정기 자료원 후보: 위 원출처와 GitHub 공식 release API https://docs.github.com/en/rest/releases/releases , Hugging Face model cards https://huggingface.co/docs/hub/model-cards , arXiv 공개 논문, 공식 교육 채널 및 전문 기관. 음성/한국어 연기·음악/효과·편집/합성·각본/시장 분야는 추가 원저자 자료원 조사 필요. 출처별 접근/라이선스 및 최신성·변경 확인 정책 검증 전 자동 수집 금지.
최초 Gemini 기술 강의 실증: T001 실제 영상 입력 및 [공통 프롬프트](TECHNOLOGY_ANALYSIS_PROMPT_V1.md) + [JSON 계약](technology-analysis-candidate-v1.schema.json), T002/T003 공식 버전·워크플로와 대조, 실제 관측 가능 범위/정밀 설정·누락/claim·비용 확인. 현재 URL/공식 자료 검색만 완료, 영상 전편 분석 및 기술 재현 결과 0. 기존 로컬 설치 변경/계정 연결/유료 호출/원문 복제 없음. W009 작품 분석 실증과 서로 다른 prompt/schema 사용.
