# Gemini 영상 분석 도입 사전 실증 — 설계 후보

2026-11-24 | DESIGN_HOLD / NOT_RUN
공식 근거: https://ai.google.dev/gemini-api/docs/video-understanding ; https://ai.google.dev/gemini-api/docs/structured-output ; https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/video-understanding .
공개 YouTube URL 영상 입력(Preview), 시청각 분석·타임스탬프, 구조화 JSON 출력 지원을 확인. 기본 정적 샘플링 1 FPS, 빠른 쇼트/동작 누락 가능; endpoint/model에 따라 구간 지정·fps·길이·context·요금·제한 다름. 실제 사용 모델, 설정, 지원 여부 및 비용을 요청 시점에 확인. 전체 영상 시간축 분석과 프레임 단위 완전 관측은 다르다. JSON 문법 적합과 사실 정확성은 별개. Gemini 웹 앱에서 가능한 기능이 모든 API 조합에서 동일하다고 가정하지 않음.

## 첫 실증 W009
Spring - Blender Open Movie: https://www.youtube.com/watch?v=WhWc3b3KhnY ; 제작사 작품/CC BY 4.0 안내 https://studio.blender.org/projects/spring/pages/about/ . 제작자/원본 링크/귀속 및 이용 범위를 기록. 원본 URL은 확인했으나 실제 영상 분석/파일 열람은 아직 하지 않았다. 외부 API 이용 및 계정·비용 권한 확인 전 호출 안 함.

## 세 번의 분석
A 전체 맥락/시간축: 원본 전체 구조와 의미 장면·관측 범위 및 누락 후보. 장편은 겹치는 시간 구간으로 분할하고 전체 서사 일관성 재평가.
B 정밀: 실제 시각·음향 근거를 재확인. 필요한 구간에 지원되는 높은 샘플링/해상도 또는 권리 확보된 영상의 기존 분석 도구 적용. 구간 경계 중복/공백/절대 시간축, 프레임 정밀도 별도 확인. 기술 원인 단정 금지.
C 독립 검증: 분석자와 다른 평가자/직접 감상/기존 제작 자료를 사용하여 근거 위치, 누락, 오인, 반례를 검증. 실제 인간 관객 데이터는 별도 수집; 같은 모델의 재호출은 독립 인간 평가가 아니다. 시장 신호/원리의 인과 검증은 상중하 코호트와 실물 비교가 필요.

## 데이터 흐름 및 수용
1. 입력 작업/작품 ID, 원본 판본/URL·권리, duration 및 요청 범위, 요청 prompt/schema digest, provider/model/settings, 실제 요청 ID/응답·오류/비용·시간 등 신뢰된 실행 envelope는 Manager/Bridge가 기록. 모델이 제공한 자기 주장으로 대체 금지.
2. 응답은 candidate staging에 보존하고 canonical JSON Schema(현재 선언적 초안) 검사, ID 참조/중복/시간 경계/coverage 연속·누락/실제 duration·원본 판본/모달리티/증거 정밀도/권리/출력 절단을 별도 검사. null과 미관측 상태는 성공이 아님. MODEL_OUTPUT_INVALID / PARTIAL / NOT_OBSERVED / VERIFIED_OBSERVATION 구분. 자동 수정으로 잘못된 관측을 사실로 만들어내지 않음.
3. 시장 자료는 별도 권위 출처의 관측으로 저장. 작품별 감상 분석, 시장 관측, cross-work pattern 후보 및 독립 검증을 분리. 평가 rubric 버전/관측자/권리 및 provenance 결속. 미검증 후보는 작가용 검증 지식 pack에 승격하지 않는다.
4. 실제 평가 기준: 장면 경계/증거 정확도, 누락/환각, 의미 분석의 전문성, 원리 추출 유용성, 비교 일관성, 권리/안전, JSON 수용률, 시간/비용. 원본 직접 관측으로 만든 독립 reference와 비교. 고정 기준/표본을 파일럿 이후 본실험 전에 확정. 저비용 모델과 고품질 모델·기타 영상 이해 기술 비교, 필요 시 대체. 실제 후보가 기존 분석보다 낫지 않으면 재설계.
5. 5축: Gemini는 video analysis capability의 교체 가능한 Add-on, Core/Bridge/Manager에 vendor 전용 코드 금지. Bridge 실행, Manager 승인·증거 결속/검사 orchestration/승격, JSON 저장 전용. 분석 raw 결과와 검증된 library revision 분리. 제품 runtime/DB/loader/API 코드 구현 금지.

## 현재
프롬프트와 선언형 후보 schema 작성, 공식 기능 및 W009 URL 확인. 실제 Gemini 호출, 응답, canonical schema validator/semantic 검증, 실제 비교 및 DB 저장은 NOT_RUN. 첫 결과로 포맷·정밀도·비용을 검증하고 개선하기 전 대량 수집 금지. KNOWLEDGE_HOLD / DESIGN_HOLD / PRODUCT_CODING_FROZEN.
