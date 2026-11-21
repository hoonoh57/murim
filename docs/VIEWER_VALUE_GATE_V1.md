# Murim 시청 가치 심사 기준 v1 — Viewer Value Gate

2026-11-22 KST. 사용자 실제 v0.1 영상 평가가 정상적인 기준점임을 명시. 출력 가능성을 시험한 영상과 품질 목표에 맞춰 제작한 작품을 구분한다. **“왜 이 주제에 내 시간을 써야 하는가?”** 를 최상위 질문으로 삼는다. 기존 4-GATE를 대체하거나 자동화 단계 수를 늘리지 않는다. 기존 G1/G2/G3/G4에서 동일 평가축을 사용하고, 증거가 없는 항목은 HOLD한다.

## 평가 계약
- 10개 평가축과 배점, 판정, 책임, 개선 방법은 `docs/VIEWER_VALUE_GATE_V1.json` 참조. 가중합 = Σ(배점×0~10 점수/10). 95/100 이상 및 모든 축 ≥9/10은 기존의 높은 내부 목표. 유튜브 공식 추천 문턱, 시장 성공 보장, 실제 유지율로 표현하지 않는다. 0점은 확인된 부재, 미평가는 null/NOT_EVALUATED. 예: 5=평범, 7=좋지만 선택해야 할 뚜렷한 이유 없음, 9=경쟁작 대비 매력과 차별점이 독립 심사로 확인. 더 세부적인 평정은 근거 타임코드/관찰의 강도에 따름. 자체 평가/독립 LLM/실제 관객 점수를 혼합하지 말고 별도 기록. 고정 기준을 점수에 맞추어 완화 금지.
- 원작 오인, 핵심 역사 오류, 권리 미확인, 필요한 음성 누락, 심각한 영상·음향/연속성 결함은 하드 FAIL. 판정할 원본/영상/음향/권리 증거가 없으면 HOLD (미완료); 알려진 결함이 있으면 FAIL. 점수 평균으로 상쇄하지 않는다. 필수 항목 누락에서 출력 성공을 작품성 PASS로 승격하지 않는다. 사람 최종 승인 전 게시 불가.
- 모든 평가 기록은 work/revision, shotID 및 timecode, rubric axis ID, reviewer type/anonymous ID, score or null, evidence, defect class, proposed correction, responsible role, recheck artifact/version을 포함. 시청자 의견은 자연어 원문 유지. 정량 평가 미실시 시 가짜점수 금지. 모델 점수와 관객 행동을 별도 보존.
- 단계: G1 소재 선택 이유/인물 선택/원전 깊이 → G2 3개 첫 화면 후보와 발화·카메라 의도 → G3 실제 이미지/음성 소스 개별 검수, 10~15초 통합 시험 → 실제 60초 통합 렌더와 TV/모바일/무화면 청취 → G4 패키징·권리·사용자 승인. 각 실패는 해당 책임 영역으로 돌려보내고 수정 전후를 동일 시나리오/조건에서 비교. 새 결과를 만들었다는 사실이 개선 증거가 아니다. 품질 승인되지 않은 설정은 Skill Registry에 성공 사례로 등록 금지.
- 실제 관객 탐색 표본 목표 12~20명, 우선 역사 관심 높음/낮음 분산 및 기기 분산. 제목/썸네일 선택, 무음악 첫 3초, 15초 및 60초 자발 시청 중단/이유, 자유 재진술, 새 사실/여운/다음 영상 선택 기록. 강제 완주나 유도 질문, 모델 평가를 관객 의견으로 치환 금지. 12명 기준의 기존 탐색 운영 목표(핵심 사건 설명 10명, 자발 완주 9명)는 통계적 시장 합격 아님. 경쟁작 KBS 세한, 박물관 영상, 인접 채널 길이/장르 유사 콘텐츠 실제 비교는 아직 NOT_RUN; 조회수만으로 우위 단정 금지.

## v0.1 실패를 재현 가능한 개선 과제로 변환
- 실제 사용자: 첫 3초 익숙한 어두운 AI 화풍, 주제·대사·화질의 붕어빵 느낌. 시청자 관점 첫인상/미술 실패. 전체 패널 유지율 측정 아님.
- 확인된 실제 이전 파일: 60초 720p 출력, 일부 원본 445x142, 진본 없음, 실제 내레이션 없음. 구체적 개선: 독립 고해상도 원본과 원작 도판 사용, 소스 대비 크롭 후 유효 해상도 검사(최종 1080p에 실제 픽셀 부족이면 생산 자산 부적격), 텍스트 명료화, 실제 낭독, 카메라를 정보 발견에 연결, 무의미한 확대 반복 제거. 원고·이전 실패 영상·실험 코드 보존.
- 알려진 실패 분류 PRODUCT_DEFECT (creative execution); 실제 원본 다운로드 차단 ENVIRONMENT_ISSUE, 권리·음성·미실험 영역 HOLD. v0.1의 baseline은 FAIL, 총점 미측정. v0.2의 품질 자체평가/관객평가도 미측정.

## 실제 v0.2 재제작 시안
`experiments/mvml_intro_lab/review_v02/intro.mvml.xml`에 7컷/60초/248자(공백 포함, 각 컷 trim 합계) 재편집 원고와 3개 첫 화면 A 필묵/여백, B 실물, C 제목 글씨, 원작 기반 밝은 종이 팔레트 등록. XML은 편집 명세이며 기존 0.1 compiler에서 호환 실행된 것이 아니다. `review.html`은 같은 XML의 평가용 브라우저 export이며 사용자 PC의 인터넷에서 원본 도판을 직접 불러오는 형태. export JSON은 점수와 댓글, 재생 위치를 기록, 개인 점수 목표 충족도 작품 승인 아님. 출력 영상 생성이나 기존 Studio 통합 기능 구현 아님. 리뷰 원본 XML과 embedded XML 동일한 Git blob 증거. 실제 자산 미확보 시 재생 차단 표시; 개별 원본 접근 가능한 컷 비교만. 선택적으로 Windows 브라우저의 localService 한국어 TTS가 설치되어 있으면 미리듣기(실제 성우, 녹음, 싱크 검증 아님; 컷 전환시 중단 가능). 기본은 무음 시안. 브라우저 WYSIWYG 실행, voice 및 원격 이미지 로딩 NOT_VERIFIED. Node JS 구문 검사 PASS / XML 참조와 지속시간 검사 PASS. 사용자에게 이 시안을 최종 영상으로 제시하지 않는다.
- 정확한 출처: 국립중앙박물관 증10000 공식 소장품 https://www.museum.go.kr/MUSEUM/contents/M0502000000.do?relicId=36516218&schM=view&searchId=search (공공누리 1유형 표시, 공식 실물 썸네일 1000px은 production master 아님). Wikimedia Commons Sehando.jpg 12424×3325, 그림 부분 6533×2652 https://commons.wikimedia.org/wiki/File:Sehando_-_detail.jpg (PD-Art 표시 및 지역별 사진 관련 제한 확인 필요); 간찰 https://www.museum.go.kr/MUSEUM/contents/M0502000000.do?relicId=87704&schM=view&searchId=search (1842-10-03 실제 문서, 1844 책/현장 아님). 근거 https://www.museum.go.kr/MUSEUM/contents/M0202030000.do?exhiSpThemId=570115&listType=list&menuId=past&schM=view . 1944년 후지쓰카 학술 기록/손재형 실제 사진 등 추가 고해상도/권리 확인 자산은 아직 확보 대상. 지금 1944년 장면에 사용한 도판은 현재 소장품 자료이며 그 해 촬영 아님.
- 브라우저 표시 가능 여부와 원본 바이트/권리 등록 분리. 컨테이너 DNS 및 download 오류로 원본 확보 실패. AI 유사 그림, 이전 저품질 이미지, 저해상도 썸네일을 production master로 fallback하지 않는다. 최종 파일은 기존 Murim `outputs/sehando/intro/<revision>/<run-id>/`에 실제 영상/receipt/asset-manifest 저장하는 목표 유지; 실제 Windows 연결/자산전송/GPU 및 output 연동 NOT_VERIFIED. 반복 ZIP 수동 설치 요구하지 않는다.

## 다음 한 단계
기존 승인 작업공간에서 실제 고해상도 도판과 사용권/해시 등록, 실제 한국어 낭독 확보 → 3가지 첫 화면(동일 음성) 및 10~15초 비교 결과를 평가표로 심사 → 통과 후 동일 60초 원고를 실제 1080p 이상으로 렌더/청취/블라인드 평가. 재현 영상과 인물 일관성은 필요한 경우에 한해 검증된 조건화 사용. **현재 v0.2는 SOURCE_FIRST_REVIEW_PREVIEW / ASSET_BYTES_BLOCKED / AUDIO_NOT_RUN / MP4_NOT_RENDERED / QUALITY_HOLD.** 목표를 넘었다고 주장하지 않는다.
