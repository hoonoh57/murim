# Murim 외부 독립 작품 심사 프롬프트 v1
2026-11-22 KST. 권위 평가 기준: docs/VIEWER_VALUE_GATE_V1.json (v1.0). 기존 4-GATE/Council을 강화하며 별도 품질 승인 우회로가 아니다.

## 실행 계약 (제작 시스템용; 심사 모델에는 필요한 심사 내용만 전달)
- 동일 artifact hash의 실제 렌더 영상과 음성, 익명 ID, 장면 타임코드, 별도 사실·권리 검증 자료. 1차 심사 전 제작 의도, 작가, AI 사용 비용, 사용자 이전 비평, 내부 점수, 다른 심사 결과, 목표 총점, 개선 기대치를 숨긴다. 사실 확인은 시청자 첫인상 답변 후 separate evidence pass로 수행한다. 실제 전후 영상 A/B 비교는 순서 무작위, 버전 명칭 비공개, 등가 조건.
- Gemini 동영상 지원 공식 문서 https://ai.google.dev/gemini-api/docs/video-understanding ; Claude 이미지 입력 공식 문서 https://platform.claude.com/docs/en/build-with-claude/vision . 선택한 모델/계정의 실제 video/audio/image 지원, 샘플링/길이 제한, 요금, 데이터 보존, 자산 전송 권리 확인. 프레임+대본만이면 모션/음성/싱크의 판단 불가를 명시하고 null 처리. LLM은 3초 반응을 추정할 뿐 실제 시청자의 이탈률이 아니다. API/video modal evidence 미지원이면 해당 영역 미심사.
- 현재 src/api/ai_clients.py의 GeminiFreeClient.generate_response(prompt: str)는 text-only 인터페이스. ScenarioEngine의 Anthropic client는 시나리오 생성 목적. 그대로 호출하는 것이 MP4 심사 구현은 아님. 향후 ReviewAdapter를 기존 provider 경계에서 선택적 추가하는 후보; 기존 키 로그와 키 사용 정책(키 prefix 출력 및 한도 우회 가능성) 검토 후 실연결. 인증/외부 전송/비용 명시 승인, 없는 연결 mock 금지, 원본 동영상 공개 게시 금지.
- 1차 평가는 별도 독립 세션에서 수행, 원문 응답 append-only 보존. 2차는 동일 평가 결과에 근거한 수정안 작성. 재제작 후 새 독립 심사 실시; 수정안의 예상 점수는 실제 점수로 기록하지 않는다.
- 총점은 시스템이 rubric weight로 계산. 검증 대상 독립 리뷰어별 total>=95, 모든 축>=9/10은 내부 목표이며 사용자/실제 관객/전문 감수와 별개. 여러 리뷰 평균으로 중대 결함을 은폐하지 않는다. 근거 없는 결함은 재확인하며 상충 의견은 Council 근거 심사, 원문 보존. 중요한 미평가 또는 관찰 자료 부족 HOLD, 확인된 hard defect FAIL. 심사 모델 자체 점수는 실제 사용자 유지율이나 시장성 입증 아님. 기준/모델 바꿔 합격점 얻기, 같은 파일 반복 제출로 유리한 점수 선택 금지. 각 승인된 재제작 라운드 최대 3회 또는 사전 승인 비용 한도, 정체/미달이면 HOLD/FAIL 및 원인 재설계(기존 gate rework limit 준수). 무제한 재생성 금지.
- 외부 심사 기능이 unavailable이면 NOT_RUN, manual import 후보. 현재 실제 외부 LLM 심사 미실행. v0.1 MP4 실제 FAIL 기준점; v0.2 HTML은 실제 MP4 아님, 자산/음성/렌더 미완료. 우선 v0.1로 평가 기준 점검 가능하되 신규 영상 제작 대체 금지.

## Prompt A — 독립 시청자 평가 (1차)
당신은 이 한국어 영상의 제작에 관여하지 않은 독립 비평가입니다. 역사나 미술을 공부하려고 찾아온 사람이 아니라, 유튜브에서 즐겁게 시간을 보내고 싶은 시청자(45~69세 우선 연구군, 연령별 선호 단정 금지)의 관점과 전문 영상 비평 관점을 구분해 평가하십시오. 영상 제작 노력, 예산, 도구가 무엇인지 추정하여 가점을 주지 마십시오.

핵심 질문: 수많은 영상 대신 왜 이 작품에 내 시간을 써야 하는가?

1. 실제 받은 영상/오디오/프레임/대본, 관찰한 시간 범위와 샘플링 한계부터 적으십시오. 제공받지 않은 음성·움직임·출처, 실제 유지율은 추측하지 마십시오.
2. 0~3초 첫인상, 3~15초, 15~30초, 30~60초를 구분하여 시청할 이유와 이탈하고 싶어지는 이유를 기록하십시오. 화면과 음성의 실제 특징을 타임코드로 지목하십시오. 실제 시청자가 이탈했다고 주장하지 마십시오.
3. 배경지식 없이 알게 된 중심 사건, 다음 사건에 대해 생긴 궁금증, 새롭게 발견한 사실을 자유롭게 표현하십시오. 왜 관심이 생기지 않았는지도 적으십시오.
4. V01 소재의 매력(10), V02 첫인상/선택(15), V03 시각적 독창성(15), V04 서사 몰입(15), V05 청각 이해(10), V06 역사적 진실성(10), V07 지적 발견(10), V08 영상/음향 조화(5), V09 기술 완성도(5), V10 여운/재방문(5)을 각각 0~10점으로 평정하십시오. 괄호는 가중 배점, 점수 기준은 0 부재, 3 심각한 결함, 5 평범하여 선택 이유 부족, 7 양호하나 뚜렷한 우위 없음, 9 비교 증거가 뒷받침하는 차별성과 매력, 10 비교작 대비 매우 뛰어난 결과와 충분한 증거. 판단 자료가 없으면 null/NOT_OBSERVED. 비교작을 보지 못했다면 그 한계를 적으십시오. 다른 영상보다 뛰어나다고 단정하지 마십시오.
5. 원작 오인, 핵심 사실 오류, 권리 미확인, 필수 내레이션 누락, 심각한 화면/음성 결함, 연속성 문제의 실제 증거를 확인하십시오. 미확인은 명시하고 보류. 실제 출처 없이 진본 여부를 단정하지 마십시오.

출력은 JSON 객체: artifact_id, observed_modalities, observed_time_ranges, sampling_limitations, viewer_first_impression, reason_to_watch, reason_to_leave, story_recall, new_discovery, assessments[{axis_id,score:null|number,status,evidence:[{start_seconds,end_seconds,observation}],limitations}], hard_defects[{code,status,evidence}], comparator_observations, critical_issues_ranked, verdict_recommendation. 가짜 점수/가짜 관찰 금지. 모델의 시청 의향은 가설로만 표시. 사실 검증 자료는 별도 질의에서 확인.

## Prompt B — 목표 수준에 근접하기 위한 처방 (2차, 평가 고정 후)
앞의 독립 심사 결과를 변경하거나 점수를 재작성하지 마십시오. 기존 내부 목표는 95/100, 모든 축 9/10 이상, 중대한 결함 0입니다. 현재 결과의 구체적 문제를 해당 목표에 근접시키는 실행 가능한 개선안을 제시하십시오. 품질이 부족하면 구조 전체를 교체할 수도 있으나 검증된 사실과 권리, 기존 원고의 핵심은 유지하십시오.
- 문제마다 axis_id, issue_id, shot_id, 시작/끝 타임코드, 관찰 근거, 원인(검증된 원인/가설 구분), 심각도, responsible_role, action_patch, 필요한 source/asset/voice/camera/timeline ID, 선행 조건, 비용/도구 의존성(확인되지 않았으면 unknown), before/after 시청자 가치 가설, 동일 조건 재검증 방법과 합격 기준을 제안하십시오.
- 추상적 권고('화질 개선', '더 영화적으로', '더 흥미롭게')만 금지. 화면 재설계, 정확한 내레이션 수정, 자산 대체 필요조건, 컷 길이/전환, 음향의 실제 구체적 변경을 제안하십시오. M-VML 원본을 임의로 덮어쓰지 말고 수정 패치 제안만. AI가 생성한 원작 대용물, 근거 없는 역사적 사건, 교훈/공포/선정적 낚시, 저품질 자산 확대를 해결책으로 사용하지 마십시오.
- 가장 큰 가치 개선과 최소한의 변경부터 순위화. 목표 미달 시 변경할 다음 전략 또는 제작 중단/재설계 기준을 명시. 실제 재렌더 없이 점수 상승 보장 금지.
- 출력 JSON: artifact_id, assessment_ref, rework_items[], dependencies[], recheck_plan[], expected_value_hypotheses[], blockers[], stop_conditions[]. 예상 점수는 실제 심사 점수와 혼동 금지.

## 재검증과 증거
실제 재제작 artifact SHA256과 변경 전후 M-VML/asset 버전, 리뷰 provider/model/version, 입력 모달리티, request/prompt revision, raw response, normalized result, verifier, 비용, 권리/사실/기술 검증 결과를 남긴다. 실제 관객 A/B 및 전문 감수는 독립된 gate 상태. 결과물 목표 출력은 기존 Murim outputs/sehando/intro/<revision>/<run-id>/, review sidecar는 동일 run 하위에 저장하도록 향후 구현. 대화 파일/원격 Git 저장 여부를 Windows 파일 작성과 혼동하지 않는다.
