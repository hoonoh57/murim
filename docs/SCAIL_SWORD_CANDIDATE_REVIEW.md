# SCAIL-2 검술 입력 후보 실프레임 검증 게이트

**상태: 검증 대기. 두 후보 모두 SCAIL 입력으로 승인하지 않음.**

## 입력 기준과 실험 목표

SCAIL-2에서 참조 이미지가 외형을 제공하고, driving video가 시간에 따른 인물 동작을 제공합니다. 사람의 포즈 모방만으로 손잡이·검날·검 방향의 일관성은 보장되지 않습니다.

이전 실패 실험 `murim_sword_driving_2s.mp4`는 역광, 실루엣, 검과 손의 형상 소실이 있어 **재사용 금지**입니다. 기존 최초 성공 사례 `SCAIL2_FULL_00001`는 변경·삭제하지 않습니다.

## 후보 원본 (실제 프레임 확인 전에는 미승인)

| 코드 | 영상 페이지 | 제한 |
| --- | --- | --- |
| pexels-6536346 | https://www.pexels.com/video/a-person-is-practicing-fencing-alone-6536346/ | 단일 펜싱 선수로 공개 설명; 무협 검술과 달라 찌르기 동작 실험 후보로만 사용 |
| pexels-5973868 | https://www.pexels.com/video/a-woman-practicing-her-fencing-skill-5973868/ | 펜싱 움직임; 잘 보이는 구간을 실측하기 전까지 후보 |

제공: Pexels. https://www.pexels.com/license/

`E:\comfyui-scail\PREVIEW-SWORD-CANDIDATES.cmd`를 한 번 실행하면 공식 Pexels 원본을 `samples\sword-candidate-review`에 별도로 다운로드하고 (원본 SHA256 기록) FFmpeg로 **1초 간격 최대 16프레임 4×4 연락표(contact sheet)** 를 만듭니다. 결과는 `pexels-<id>-contact-sheet.png`와 `preview-report.json`; 오류는 `logs\preview-sword-candidates.log`입니다. CMD는 결과를 확인할 수 있도록 자동으로 닫지 않으며, 입력 폴더·기존 워크플로·모델은 변경하지 않습니다.

## 수동 WYSIWYG 승인 게이트

- [ ] 실제 검날 또는 연습검의 전체 길이가 2초 이상 화면에서 구별된다
- [ ] 손-검 손잡이 접촉이 2초 전후 프레임에서 유지된다
- [ ] 한 사람의 동작만 있으며 장면전환·방해물·차폐가 없다
- [ ] 몸 전체가 충분히 밝고 인물과 배경 분리가 선명하다
- [ ] 최소 2초 연속 **명확한** 찌르기/베기/막기 중 하나가 확인된다
- [ ] 동작에 따라 몸의 자세가 변하며 정지 포즈나 춤만 반복하지 않는다
- [ ] 라이선스, 출처 및 원본 SHA256이 기록됐다

**모든 항목 확인 전에는 새 SCAIL 워크플로를 구성·실행하지 않습니다.** 후보가 부적합하면 모두 탈락시키고 다른 실촬영 소스로 교체합니다. 펜싱 동작 PASS를 무협 검술 품질 PASS로 혼동하지 않습니다.
