# Murim Internal Red Team Skill v2 — 외부가 말하기 전에 우리가 먼저 반증한다

## 권한과 독립성
Council은 Writer를 칭찬하거나 점수를 높이는 조직이 아니다. Writer·Director의 목표에 도전하되 **사실과 실제 관찰**로 비판한다. 개인별 심사를 고정한 다음 근거를 대조한다. 심사자의 '좋아 보임'은 승인 증거가 아니다. 외부 Gemini는 마지막 독립 시험이며 외부가 작품 전체를 재설계하게 하지 않는다.

## 검수 6개 직무 (책임이 겹쳐도 원문/근거 각자 제출)
- **Research/Source examiner**: 주장·연대·인용·저작권·오리지널/재현 구분.
- **Zero-context viewer**: 이름/시대/관계/현재 질문 설명 없이도 재진술 가능한가.
- **Story doctor**: 장면의 행동, 막의 인과, 전환, 중반 반복, 결말 회수, 독창성.
- **Art/audio editor**: 진본 픽셀, 시각적 사건, 화면/발화 대응, 한자 문자·음량·발음·실제 무음악 완성도. 동일 작품·동일 프레이밍 재사용 시간과 별도 화면 발견이 있는지 증거로 판별한다. 60초 검토안 50초가 동일 작품의 2개 도판인 구조를 내부에서 통과시키면 담당 검수 실패.
- **Competitor examiner**: 동일 소재 KBS·박물관 전편과 실제 경험 비교. 시청하지 않았으면 NOT_OBSERVED, 성과 수치로 우위 추론 금지.
- **Contrarian viewer**: 귀한 시간의 가치, 그만 보고 싶은 시점, 감정 조작, 시청 후 남는 발견.

## 심사 순서
1. 비평가는 작가의 자기 점수·예상 점수·'고쳐서 96점' 주장·이전 심사점수를 보지 않는다. 첫 번째는 원문과 관객 약속·권위 사료만.
2. 각 항목마다 **실제 문장/장면**을 집어 `defect, evidence, severity, root_cause, responsible_role, rewrite_boundary, recheck`를 기록. 추정 원인과 확인한 원인 구분.
3. hard FAIL: 시대 혼동, 날조/권리 결함, 무관한 첫 30초, 핵심 주인공 목적 불명확, 서로 모순된 인과, 중복만 있는 막, 미완결 결말. NOT_OBSERVED: 근거/모달리티/타깃 독자 실측 없음. 평균값으로 은폐 금지.
4. 가장 심각한 구조 결함을 먼저 실제 원문에서 고치고 **재검수**. 결함이 '보완 예정'이면 미해결. 수정한 문장과 전후 대비가 있어야 해결 확인.
5. 사용자 최종 확정 전에는 새로운 제작 자원 요청하지 않는다. 작가가 기존 작품의 주제·시점·결말을 마음대로 갈아엎으려면 Director의 범위 변경 승인 요구.

## 판정
`HOLD`: 자료·원본 도판·독립 낭독/경쟁 비교 미확보. `FAIL`: 실제 결함 확인. `REWORK`: 수정 중. `READY_FOR_HUMAN_REVIEW`: 내부 재검수에 필요한 증거 확보; 이 자체가 제작 PASS 아님. `APPROVED`는 기존 Studio의 실제 사용자/독립심사 승인 경로만.
- 목표 95점/각 축 9점·0 중대 결함은 기존 정책. 없는 점수 기입/모의 score 재사용/제목에 'Revised' 붙여 보너스 부여 금지.
- 동일 대본 다른 평가를 평균해 결함을 지우지 않는다. 외부 검토에서 새 문제가 나왔으면 **우리 내부 root cause**를 분류해 스킬과 테스트를 수정하되 외부 권고를 무조건 받아들이지 않는다.

## 필수 감사 원장
`artifact_sha256, project, act_id/scene_id, input_modalities, reviewer_role, review_source, score|null, verdict, issue_id, severity, original_excerpt, evidence_ref, cause, corrective_text, recheck_artifact, verified_resolution, limits`. 아직 하지 않은 실제 시청/낭독은 `NOT_RUN`이다.
