# Murim 제품 코딩 선행 설계 심사 및 Alpha 입증 게이트 v1.0

2026-11-24 KST | 사용자 확정 최우선 계약 | 기준 HEAD b4dbd111466122c54fa6018dc2205ef85d3eda8b
**DESIGN_HOLD / PRODUCT_CODING_FROZEN / COMPETITIVE_ALPHA_NOT_PROVEN**
이 계약이 이전 handoff의 M1-B 즉시 코딩 계획보다 우선한다. 기존 소스/테스트/원본은 보존한다. 신규 제품 기능, M1-B/C, UI, 실행기, 자동 평가 코딩은 보류한다. 조사, 설계, 권리 범위의 기존 도구/기존 실행기 활용, 독립 원고/자산 비교 실험, 비실행 계약 및 증거 기록만 허용. 신설 제품 코드로 벤치마크를 통과시키는 순환 논리 금지. 이미 구현된 M1-A의 27개 테스트와 M0 부분 16개 결과는 과거 국소 실행 증거이지 설계 승인 아님.

## 1. 설계 감사 판정
5축 소유권, 능력 기반 교체, 품질 캐스케이드, 전문 스킬/Champion–Challenger, 단순 UI 방향은 문서화되어 있다. 하지만 생성 역량이 실제로 존재하는지, 전문가 수준의 품질, 평가자의 실제 신뢰도, 경쟁 제품 대비 유의미한 우위, 지속 가능한 비용, 기술 한계 및 실패 경로가 미실증이다. 따라서 구조 방향은 유지하되 상세 설계와 검증을 먼저 한다. 100년 수명, 모든 미래 기술의 완전 호환, 최고 품질 및 시장 성공은 보장 가능한 속성이 아니다. 변경 가능한 전문 기술과 장기 안정 계약, 측정 가능한 복구·교체·이전 증거를 목표로 한다.

기존 M1-A는 점수와 필수 검사/해시 형식의 순수 구조 검증만 수행한다. 정수 점수/target 및 평가자 ID 차이만으로 전문 평가의 타당성, 독립성, 불확실성, 실제 원고/영상 증거, 비교우위를 표현/보장하지 못한다. 후속 설계에서 객관 검사, 의미 평가, 사람 선호, 비교 효과, 증거 인증을 구분하고 그 계약을 검토한 뒤에만 코드 변경 여부를 결정한다. 점수 중심 계약에 창작을 억지로 끼워 맞추지 않는다.

## 2. 모든 단위 능력의 필수 설계 질문
capability마다 독립 dossier를 작성하고 기준 날짜/버전/적용 시장·장르·길이·권한·장비를 기록한다.
1) 고객이 얻을 결과와 가장 어려운 실패는 무엇인가? 사용자가 해야 할 기술 조작을 어떻게 제거하는가?
2) 현재 최상위 실제 경쟁 제품·전문가 방식·최신 논문/원저자 구현에서 이미 기본 제공하는 것은 무엇인가? 홍보 주장과 관측 결과를 구분한다.
3) 기존 기술 Adopt/Compose로 어떤 품질을 달성할 수 있고, 무엇이 실제 한계인가? 구현·라이선스·API·한국어·자원·권리·비용·장기 유지·외부 의존/장애를 확인한다.
4) 최고 품질을 생성하는 전문 방법론(상태/입력/산출물/핵심 제어/창작 대안/실패 복구)은 무엇인가? 구체적인 기술을 비교하여 선택하고 검증 불능 기능을 제외하거나 설계를 바꾼다. 품질 판정만 설계하고 생성 로직은 LLM에게 맡기는 방식 금지.
5) 경쟁 앱/강한 단일 모델/기존 방식/적용 가능한 전문 인간 작업보다 어떤 Alpha를 제공하는가? 동등 조건의 실제 결과와 비용·시간·사용자 노력으로 반증할 수 있어야 한다.
6) 외부 평가자가 실제 무엇을 관측하고 어떤 오류를 낼 수 있는가? 독립성·사람 보정·편향·반례·증거 인증·불확실성·통합 품질 검증을 어떻게 수행하는가?
7) 요구를 못 맞추면 어떤 다른 기술/전략으로 바꾸고 어느 상위 계약을 수정하는가? 유효한 대안이 없으면 HOLD, 목표 하향/강제 진행/무한 개선 금지.
8) 5축 owner, versioned capability/input/output/evidence/schema, parent/child/dependency, 스킬 및 engine pin, 권한/자원·실패/취소/UNKNOWN/재시작/rollback, 이력과 단순 UI에 미치는 영향은 무엇인가? 새 기능 때문에 공통 코드에 feature-specific 변경 금지.

## 3. 코딩 허가 게이트 D0–D5 (제품 품질 G1–G4와 별도)
D0 문제/시장 기준: 사용 시나리오, target audience, 기존 전문 작업과 직접 경쟁 앱의 기능·품질 기준, 차별화 가설. 강한 비교군 포함. 문서 조회만으로 완료 아님.
D1 기술 실현성: 실제 사용할 기술 후보와 독립 공개 evidence, 필요한 API/입출력/라이선스, 실제 환경·권리·비용·한계, 실패 복구/대체 전략. 가장 위험한 가정을 기존 도구로 먼저 실증한다.
D2 전문 생산 설계: 실제 생성 및 수정 방법, 상태/계층/통합·전문 스킬·대안 생성/독창성 보호/근거 입력, 구체적 산출물 및 모달리티, 검증 계약, 사용자 개입 최소화. 단순 'LLM이 알아서' 금지.
D3 평가 설계: 별도 evaluator 검증, 인간 전문 평가/관객 보정 표본, 실제 관측, 고정 독립 비교군/fixture·척도·실험 예산·표본 설계·사전 margin/불확실성 규칙, 실패율 및 하위 꼬리. 평가자 반복 호출로 점수 상승을 취득 금지. 결과에 맞춰 기준 변경 금지.
D4 사전 실물 실증: 신규 제품 코딩 없이 기존 도구/API/원저자 구현/기존 LLM 인터페이스/격리 환경으로 대표 산출물을 만든다. 동일 brief, 비교군, 독립 평가 및 전문가/관객 보정, 실제 비용·시간·조작·실패 포함. 반증 가능한 핵심 Alpha와 필수 품질, 실제 환경 타당성의 관측 증거 확보. 실험 절차상의 수동 조작은 실험 한계로 기록하며 최종 자동화 사용성 증거로 세지 않는다. 접근이 막히면 NOT_RUN/HOLD, 공개 예시를 자체 실행으로 둔갑 금지.
D5 구조/통합 설계 심사: 모든 D0–D4 evidence 및 known risk, 인터페이스/버전/보안·저장·의존성·교체/복구·통합 품질과 회귀 계획, 경쟁 앱 기준의 누락 기능 분석. 독립 설계 반대심사에서 blocker 0, 타당한 완화책과 검증 기준, 근거 연결이 확인되면 개발 LLM이 DESIGN_OK를 기록한다. 평가자 명의/수치 위조 금지. 필수 증거 미확보는 DESIGN_HOLD. 제품 구현이 없어서만 검증 가능한 성질(실제 host hash, 최종 UI, 대규모 runtime)은 구현 인수 조건으로 분명히 분리; 이를 사전 완료라 하지 않는다.

전체 프로그램의 기능 경계 및 핵심 설계 가정은 전체 설계 감사 대상이다. 모든 단위의 D0–D5 심사 상태를 관리하고 미승인 단위 코드 금지. 사용자 요청의 전체 설계 OK 전까지 신규 제품 코딩 전체 보류. 정상적으로 개발 LLM이 비교·결함 보완·설계 심사를 담당하며 사용자에게 기술 선택을 맡기지 않는다. 실제 외부 평가자/전문가/경쟁 앱/권한 미확보는 blocker로 기록. 실제 사람의 참여/유료 서비스/외부 자산 전송 권한을 임의로 가정하지 않는다. 기존 작품 G1–G4와 게시 승인 유지. 설계 OK는 시장 성공 보증이나 완성 제품 PASS가 아니다.

## 4. 단위 능력별 초기 설계 결함/검증 매트릭스
아래는 초기 inventory 및 반증 계획이며 전수 상세 설계 완료/채택 아님. 모든 행 DESIGN_HOLD. 연구 출처와 적용 조건은 별도 dossier에서 갱신한다.

| 단위 capability (열린 예시) | 강한 기준/기술 후보 | 미해결 한계·사전 증거 |
|---|---|---|
| 목표·관객·기획/리서치 | 전문 개발 lab/기관 원전, 검색·사료 검증, Runway Agent | 실제 의도 회복·새로운 관점·근거/권리/시장 포지션. 모호한 brief/수정 의도/사료 충돌에서 정확한 완성 기획; 질문 수와 오류 비교 |
| 시나리오·각본 | DOC/DOME/StoryWriter/Storyteller/CritiCS, Sudowrite/Novelcrafter, 전문 작가 | 고정 구조·장편 기억·대사·독창성·평가 타당성. 별도 screenplay review 및 실제 독립 원고 비교 |
| 스토리보드·프리비즈 | LTX Studio, Higgsfield, Runway, DramaAgent | 원고 의미/동선/카메라/시각적 보상/연속성, 실제 컷 및 animatic 시간. 자연어 변경의 downstream 효과 |
| 캐릭터·장소·소품·이미지 | 참조 conditioning, 재사용 Elements, LoRA/편집/다각도 자산 | identity/의상/검-손/공간·권리·표정·시각적 개성. 여러 각도·조명·쇼트의 blind contact sheet와 실제 영상 연결. 모델 이름만으로 품질 추정 금지 |
| 동작·영상·멀티쇼트 | 현재 로컬 ComfyUI, WAN/LTX/SCAIL 후보, 상용 엔진, DramaAgent, VBench-2.0 | RTX4070 Laptop 8GB 실환경, 검/손 접촉/칼날/자세/물리/카메라/시공간 연결. 권한 범위 실물 30–60초와 어려운 쇼트, 전체 실패/재생성 횟수·비용. 단일 MP4 성공은 품질 PASS 아님 |
| 한국어 음성/연기/립싱크 | 기존 GPT-SoVITS 후보 및 실제 상용 TTS/음성 연기 비교 | 원어민 독립 청취, 발음/인물 voice/감정/억양/동기화, 실제 ASR·phoneme 및 지연 검증, 음성 이용 권리. 기술 정확도와 연기 품질 분리 |
| 음악·효과·믹싱 | 실제 편집/음향 도구, EBU R128 계측 및 배포별 프로필 | 대사 가림/과잉 음악/공간감/권리. 원본 stem/무음악 비교/실제 믹스 청취·LUFS/true peak; 방송용 수치를 모든 채널에 강제 금지 |
| 편집·자막·합성 | 기존 FFmpeg, OpenTimelineIO 편집 교환, 전문 NLE, CutCraft 연구 후보 | 원고/장면 의미·컷 리듬·공간 연결·음향/자막 동기·export. 동일 영상/음성 자산으로 실제 편집본 독립 비교 및 round-trip |
| 최종 작품·배포 준비·관객 | 실제 경쟁작/전문 작품/타깃 관객, YouTube retention 등 실제 관측 | 1회 LLM 칭찬과 시장 성과를 구분. 블라인드 전편 시청, 이해/선호/기억, 실제 반복 사용·비용·타깃 시장 파일럿. 게시/결제 별도 승인 |
| 공통 runtime·스킬·데이터·보안 | Temporal/LangGraph 등 기존 도구, Agent Skills/JSON Schema/OTIO | 일반 엔진 재발명 금지. 기존 도구로 중첩/부분 재작업/실패/재연결/데이터 이동 시뮬레이션, 실제 교체·격리·500 manifest·migration/backup/rollback의 구현 후 시험 계획 |
| 자연어 UI·기계검증 | 실제 대화형 경쟁 앱/일반 접근성·사용성 평가 | 비전문가의 동일 brief→실제 작품→수정→결과의 성공률, 기술 조작 수, 시간, 재사용 의사. 무인가 동작/가짜 상태 금지, 진단의 read-only 연결 및 증거 추적 |

단위 품질의 합이 전체 작품 품질은 아니다. 통합 설계에서 의도/서사/캐릭터/장소/소품/시간축/권리/미학/청각 상태를 revision 및 dependency로 결속하고 장면/시퀀스/전편의 통합 반증을 포함. 국소 최적화가 전체를 훼손하면 부모 실패로 반환하며 변경 승인과 원본 보존. 실제 경쟁우위는 전체 E2E의 사용자 노력·품질·비용 비교에서 판정한다.

## 5. 외부 평가와 시장 Alpha의 분리
외부 LLM 극찬은 발견 신호일 뿐 품질 인증/시장 상위 진입의 충분조건이 아니다. LLM이 인간을 대체해 평가할 수 있는 축과 그렇지 못한 축을 먼저 실측. 평가 프로토콜은 동일 작품 순서 반전, 길이/문체/출처 표시 편향, 자기/동계열 평가, 모의 오류 탐지, 인간 간 불일치, 거짓 PASS율, 보정 및 보류를 포함. 선호/근거 없는 칭찬은 집계하지 않는다. 같은 LLM의 재호출을 독립 평가자로 세지 않는다. 모든 검증이 통과해도 입증 범위(장르/길이/모델/비교군/표본/비용)를 명기한다.
Alpha 후보: 전문 수준의 실제 산출물 + 적은 사용자 기술 개입 + 지속적으로 교체 가능한 엔진과 재현 가능한 targeted repair + 합리적 비용의 결합. 기능 보유는 Alpha 아님. 전문 사용자/관객/경쟁 제품과 비교해 우위가 입증되어야 한다. 전문 작품 평가, 비교 제품 우위, 유료 시장 검증(자발적 채택/반복 사용/경제성)은 서로 별도. 현재 모두 미실증.

## 6. 현행 연구 근거 (2026-11-24 조회)
- DOC https://aclanthology.org/2023.acl-long.190/ ; Re3 https://aclanthology.org/2022.emnlp-main.296/ ; DOME https://aclanthology.org/2025.naacl-long.63/ ; StoryWriter https://arxiv.org/abs/2506.16445 ; STORYTELLER https://aclanthology.org/2025.findings-acl.1071/ ; CritiCS https://aclanthology.org/2024.emnlp-main.1046/ ; IS-CoT https://aclanthology.org/2026.acl-long.911/ . 서사 연구의 성능은 원 논문 실험에 한정, 한국어 전문 각본/우리 환경 전이 미실증.
- DramaAgent https://aclanthology.org/2026.aacl-long.163/ (2026년 11월 학술 공개): 계층적 story planning, 지속 인물 상태, scene-wise generation, targeted repair가 이미 제안됨. 우리 5축/다중 agent 자체를 독점 Alpha라 주장 금지.
- LitBench https://aclanthology.org/2026.eacl-long.362/ : 논문 내 최강 범용 judge 인간 선호 일치 73%, 특화 reward model 78% (https://arxiv.org/abs/2507.00769). 창작 평가의 한계. https://aclanthology.org/2026.aacl-long.203/ 인간 창작 평가의 여러 양상을 어느 LLM도 모두 재현하지 못함. https://arxiv.org/abs/2306.05685 위치/장문/자기 선호 편향. https://doi.org/10.1126/sciadv.adn5290 AI 보조 단편 개별 창의성/집단 다양성 trade-off.
- VBench-2.0 https://vchitect.github.io/VBench-2.0-project/ ; EBU R128 https://tech.ebu.ch/publications/r128 ; OTIO https://opentimelineio.readthedocs.io/en/latest/ ; CutCraft https://arxiv.org/abs/2609.08275 (preprint); 실제 clip/편집/한국어 음성 적용 미검증. YouTube retention https://support.google.com/youtube/answer/9314415 는 관객 행동의 일부이지 작품성/매출 보장 아님.
- 경쟁 앱 공식 문서: https://docs.sudowrite.com/using-sudowrite/1ow1qkGqof9rtcyGnrWUBS/what-is-story-bible/jmWepHcQdJetNrE991fjJC ; https://www.novelcrafter.com/courses/ultimate-beginners-guide/writing-a-complete-scene ; https://help.runwayml.com/hc/en-us/articles/51601639579667-Creating-with-Runway-Agent ; https://help.runwayml.com/hc/en-us/articles/53907039424915-Using-Agent-Skills ; https://ltx.io/blog/how-to-build-a-complete-pre-visualization-pipeline ; https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-cinema-studio . 이미 Story Bible/개요/장면/재작성, 대화형 multi-shot, skill, pre-viz, camera/actor/element reuse가 존재. 실제 동일 결과 비교 NOT_RUN.

### 5.1 실제 독자 시장 실증

[실제 관객 검증 계약](MURIM_AUDIENCE_VALIDATION_CONTRACT.md)을 D3/D4 및 시장 검증의 구체적 기준으로 적용. 독자 행동·댓글·노출을 함께 분석하고 소설/영상/앱 시장성 별도. 문피아 AI 직접 생성물 금지 준수, 허용 채널 또는 동의한 한국어 독자 평가단. 실제 실증 NOT_RUN. 설계 동결 유지.

### 5.2 압축 실물 작품을 통한 단위 기술 실증

[제작기술 시장 실증 계약](MURIM_SHORT_FORM_MARKET_VALIDATION.md)을 D1~D4의 대표 실험 계획에 적용. 신규 제품 코드 없이 기존 기술로 짧은 난제 및 완결형 단편 애니메이션/숏드라마의 실물 품질과 실제 관객 반응 확인. 의심 기술을 독립 대조하여 개선하고 통합 품질 재검증. 실제 관객/게시/시장 증거 미확보 시 HOLD, 조회·이탈 단독으로 기술 원인 판정 금지. 권한 및 모든 설계 동결 유지.

### 5.3 경쟁작 지식 베이스 선행 심사

[경쟁작 라이브러리](MURIM_COMPETITIVE_WORKS_LIBRARY.md)는 D0의 비교 모집단/시장 언어, D2의 전문 제작 입력, D3의 평가 기준/반례, D4의 실제 지식 적용 효과 검증에 필수. 상·중·하의 실제 작품과 관측 및 근거를 비교하고 해당 작가 pack을 사전 확정. 원천 후보만 확보한 상태에서는 KNOWLEDGE_HOLD. 제품 코드 동결 유지.

### 5.4 최신 기술 정보의 설계 선행 입력

[기술 연구 라이브러리](MURIM_TECHNOLOGY_INTELLIGENCE_CONTRACT.md)에서 최신 공식 릴리스/교육·실제 워크플로·원저자 연구/실패 근거를 확인하고 D0~D4에 활용한다. 기술 후보의 출처/실제 재현/목표 환경 비교 및 최신성/권리/호환 검증 분리. Gemini 강의 분석 후보 및 표준 데이터 준비, 실증 미실행. 전체 D0~D5 OK 전 제품 코딩 금지.

### 5.5 제작 이전의 시장 기회 선별

[시장 기회 계약](MURIM_MARKET_OPPORTUNITY_CONTRACT.md)은 D0 시장 선택/경쟁 공백, D1~D2 실현성·제작 차별성, D3 후보 선정 기준 보정, D4 독자·시청자/수익 경로 실증, D5 통합 심사의 필수 입력. 연구 우선순위와 실제 투자 순위 구분, 초기 수동 후보는 제작 HOLD. 검증되지 않은 기술/수익률로 투자 승인 금지. 설계 동결 유지.

### 5.6 시장·소재 선정 자체의 선행 품질 게이트

[시장 선행 검증 계약](MURIM_PREPRODUCTION_MARKET_GATE.md)의 MARKET-M0~M6를 D0~D4 및 D5에 연결. 실제 유사 신규 창작자/경제성·수익 자격/콘셉트 비교·검증 원가·보수적 손익·선별 모델 독립 비교를 먼저 실증. 미달 원인별 보완 또는 투자 후보 제외. 수동 연구 순위/100점 가중치 폐기. 실제 작품 pilot은 선행 검증 외부 확인이며 무계획 실패 제작의 수단 금지. 코드 동결 유지.

### 5.7 공정별 엄격한 심사와 집중 실행

[통합 심사 계약](MURIM_ASSURANCE_AND_COMMITTED_EXECUTION_CONTRACT.md) 및 [공정별 원장](research/assurance/STAGE_ACCEPTANCE_REGISTER.md) 적용. 모든 D0~D5의 필수 요구-판정-실제 증거 추적, 평가기 독립 검증, 미달 보완/종료조건, 합격된 baseline 및 변경 조건을 설계에 반영. 초기 공정 15행 전체 NOT_QUALIFIED, 수치 보정/실물 독립 검증 전 설계 OK 금지.

## 6.1 분야별 상세 생산 설계 보완 (2026-11-25)

- [A07 영상 제작 로직·기반기술 비교 및 목표 설계](research/assurance/A07_VIDEO_PRODUCTION_DESIGN_2026-11-25.md): 실제 현재 adapter와 원저자 소스의 V1~V6 GAP, 다중 조건/시간축, typed recipe, preview/refine, 국소 수정, 비동기 실행 및 불확실 상태 복구, 5축 책임의 D2 상세 설계 입력. 이후 구현 설계 시 적용하며 D1/D3/D4/D5 검증 및 전체 승인 전 코딩 금지. 기존 계약 및 품질 하한 불변.

## 7. 다음 작업
제품 코딩 재개 금지. [시나리오 전문 생산 상세 설계 심사](skills/screenplay-master/references/production-design-review.md)를 첫 대상 dossier로 발전. 각본 고위험 가정·평가자 보정·권리 확보 전문 원고/경쟁 앱/강한 LLM 대비 기존 도구로 실증할 수 있는 경로를 조사한다. 이어 모든 단위에 동일 절차를 적용하고 전체 설계 심사 완료 전 M1-B를 시작하지 않는다. 현 상태 DESIGN_HOLD, 전체 REMEDIATION_REQUIRED.
