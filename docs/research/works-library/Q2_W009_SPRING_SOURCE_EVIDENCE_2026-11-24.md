# Q2 / A02 W009 Spring — 원저자 제작 기록 분석 및 관측 경계

2026-11-24 KST | 기준 main d617aa86108f4c6ffe0856103c21839be43fcc38 | PARTIAL_SOURCE_RESEARCH / NOT_OBSERVED (영상) / A02 NOT_QUALIFIED

기존 GEMINI_VIDEO_ANALYSIS_PILOT.md, VIDEO_ANALYSIS_PROMPT_V1.md 및 MURIM_COMPETITIVE_WORKS_LIBRARY.md의 합격 조건 불변. 연구자의 대체 경로 선택은 원저자 텍스트 기록 분석이며 Gemini 영상 분석 결과 또는 canonical video-analysis JSON 반환으로 대체하지 않는다.

## 원천 및 실행 증거
- W009: Spring, Blender Animation Studio, Andy Goralczyk 감독, 2019-04-04, 7:44, 대사 없는 3D 판타지. 공식 발표 https://www.blender.org/press/spring-open-movie/ 및 권리 안내 https://studio.blender.org/projects/spring/pages/about/ 의 검색 제공 본문 확인. CC BY 4.0, 로고/상표 및 별도 표시 제외. 귀속 © Blender Foundation | cloud.blender.org/spring. 영상 https://www.youtube.com/watch?v=WhWc3b3KhnY.
- Wikimedia Commons https://commons.wikimedia.org/wiki/File:Spring_-_Blender_Open_Movie.webm 의 검색 제공 본문: 7:44, 2048x858, VP9/Opus, 77.99 MB, CC BY 4.0. 격리 컨테이너 curl로 공개 파일 redirect 접근 시도 결과 exit 6 (Could not resolve host: commons.wikimedia.org). 파일 미수신, 프레임 추출/음향 청취 NOT_RUN. 전체 시간축 미관측; duration 464000ms는 출처 표기 분량이며 media probe 실측 아님.
- 연결된 실행 도구 및 plugin 검색(Gemini Google AI Studio video understanding)에서 Gemini 직접 영상 이해 호출 수단 미발견. 미승인 API/계정/비용 호출 없음. 실제 provider request ID, model/version, tokens, latency, cost, raw response 모두 미확보. 추가 플러그인이 존재할 가능성은 배제하지 않음.
- Blender 공식 페이지 직접 열기 일부 402 또는 cache miss; 아래 B01/B02는 원저자 페이지 본문 직접 열람, B03~B06은 검색이 제공한 원출처 텍스트만 확인. 첨부 이미지/영상 자체 열람과 구분. 자료 저자의 진술이며 독립 실험 증거 아님.

## 실제 제작 기록 → 창작/생산 원리 후보

| ID | 출처와 확인된 내용 | 적용 후보 | 한계 및 반증 |
|---|---|---|---|
| B01 | David Revoy, 2017-10-09, [Spring Preproduction](https://www.davidrevoy.com/article337/spring-preproduction), 직접 본문: 원고를 읽고 첫 주에 인물/주요 환경 디자인, 복잡한 액션의 컬러 스토리보드 착수 | 전문 미술/프리비즈는 원고의 서사 기능을 입력으로 삼고 난제 쇼트를 앞당겨 검토 | 실제 이미지 및 애니매틱 미관측, 다른 제작 방식과의 비교 없음 |
| B02 | David Revoy, 2019-04-04, [Concept art](https://www.davidrevoy.com/article712/spring-open-movie-character-design-and-concept-art), 직접 본문: 제작 착수 직전 기상 도입부 삭제, 관련 콘셉트 아트는 존재 | 제작 준비비 매몰비용으로 장면 존치 정당화 금지, 서사 기능과 전체 구조 우선, 제외 revision 보존 | 삭제의 정확한 이유/관객 선호 효과 미확인. 삭제 전후 실제 비교 NOT_RUN. B01의 초기 기록과 B02의 최종 기록은 시점이 다름 |
| B03 | Blender Studio, 2018-03-21, [Log 07](https://studio.blender.org/blog/spring-weekly-2018-03-16/), 원출처 검색 본문: 감독 편집 변경으로 당시 영화 길이 2분 감소, 개 동작 테스트로 rig 문제와 캐릭터 표현 탐색 | 최종 제작 이전 저비용 구조/동작 검토 | 당시 편집 길이와 최종판 동일하다고 단정 금지, 삭제한 구간/효과 미확인 |
| B04 | Blender Studio, 2018-05-07, [Log 09](https://studio.blender.org/blog/spring-weekly-2018-05-03/), 원출처 검색 본문: 쇼트 제작 전 애니메이션 테스트, 자산 통합 테스트 렌더에서 파티클/렌더 문제 노출 | 난제별 먼저 실증하고 통과한 설정만 통합. 검/손/정체성 사례는 Murim의 별도 적용 가설 | 원본 영상/실행 설정/장비/비용/개선폭 미관측 |
| B05 | Blender Studio, 2019-07-15, [Open Content Overview](https://studio.blender.org/blog/spring-spring-open-content-overview/), 원출처 검색 본문: 단계별 스토리보드~렌더 기록, 선정 쇼트 20개 animation/lighting bundle | 실패 원인/수정 revision/비교 결과를 지식의 근거로 보존 | 20개 파일 미다운로드, 실제 재현/속도/비용 미확인; 20은 편집 반복 횟수가 아님 |
| B06 | Blender Studio, 2018-01-23, [Log 01](https://studio.blender.org/blog/spring-weekly-2017-01-19/), 원출처 검색 본문: 이야기 및 쇼트 수정, 임시 음악·소리, 제작 추적과 pose library 협업 | 수정 가능한 저비용 통합 편집과 성능 일관성 도구 | 실제 산출물 및 비교 실험 없음 |

## 후보 Knowledge Pack 및 평가 반례
위 원리는 생산 과정에서 발견한 가설이며 장면별 작품성·실제 관객 감정·상업성·인과 효과를 입증하지 않는다. 창작자에게 제공하는 연구용 비실행 pack 후보: (1) 원고의 사건과 인물 선택을 미술/동작 의도에 연결, (2) 핵심 서사 기능 기준으로 도입/반복 장면 재검토, (3) 대표 난제의 최소 실물 및 실패를 먼저 관측, (4) 각 단계의 원본 revision 및 실제 개선 evidence 추적. 원작 캐릭터/사건/구도 복제 금지. 비교 실험 시 동일 독자적 brief와 모델/예산에서 pack 미사용 및 강한 일반 전문 지침 대비 블라인드 원고/프리비즈 평가; 합격선/독립 표본 미확정, 실제 실험 NOT_RUN. 검증된 작가 지식으로 승격 금지.

Q4 후보 참조 반례:
- R05: 제작 전 삭제된 집에서의 기상 장면을 최종 영상에 등장한다고 주장 → FAIL(판본 혼동; B01/B02).
- R06: 선정 쇼트 20개를 애니매틱 수정 20회라고 해석 → FAIL(단위 혼동; B05).
- R07: 2분 편집 단축으로 관객 만족도가 상승했다고 확정 → FAIL(인과/실측 부재; B03).
- R08: 접근 실패한 영상의 특정 시간대 음향/장면/시청자 감정을 직접 관측이라고 기록 → FAIL(미관측 증거 위조).
독립 평가기/실제 시험 NOT_RUN. 관객 심리·시장·순위·수익 데이터 추가 안 함.

## 판정 및 다음
공개 제작 원자료 분석 경계 완료(직접 본문 2건, 검색 제공 제작 원문 4건); W009 영상/음향 전체 NOT_OBSERVED, Gemini NOT_CONNECTED / NOT_RUN, JSON schema 실응답 검증 NOT_RUN. A02 NOT_QUALIFIED / KNOWLEDGE_HOLD, 기술·시장/5축/전체 설계 판정 불변. ENVIRONMENT_ISSUE: 영상 다운로드 DNS 및 Gemini 호출 연결/권한 미확보. 반복 호출 대신 Q3 기술 원저자 자료 실증으로 이동. Q2 재개 조건: 승인된 실제 영상 파일/연결 및 독립 참조 관측, 동일 판본의 시간축·시청각 검증, 상중하/반례 자료 및 실제 pack 기여도 비교. 제품 코드/테스트/UI/DB 변경, Windows 실행, 비용, 외부 게시/전송 없음.
