# Auto Healing MVP 검증 보고서

## 실행 정보

- 실행일: 2026-10-30
- 환경: Windows 로컬 Python 3.13.15
- 검증 명령: `py -m unittest discover -s tests -v`
- 결과: 26건 실행, 실패 0건, 오류 0건
- 외부 LLM: 사용하지 않음

## 정상 서비스

| 항목 | 결과 |
|---|---|
| `/health` | `status=ok` |
| 정상 `/coach` | `status=ok` |
| 응답 질문 수 | 3개 |
| 외부 네트워크 호출 | 없음 |

## 장애 실험

| 장애 | 탐지·분류 | 복구 | 독립 검증 | 시도 | 결과 |
|---|---|---|---|---:|---|
| HTTP 429 | PASS | 백오프 후 대체 응답 | PASS | 3 | recovered / degraded |
| 타임아웃 | PASS | 백오프 후 대체 응답 | PASS | 3 | recovered / degraded |
| 연결 실패 | PASS | 백오프 후 대체 응답 | PASS | 3 | recovered / degraded |
| HTTP 5xx | PASS | 백오프 후 대체 응답 | PASS | 3 | recovered / degraded |
| 원인 불명 | PASS | 자동 복구하지 않음 | 에스컬레이션 | 0 | escalated |

실험 요약은 `artifacts/experiments/metrics.json`에 저장했다. 모든 장애 주입은 `mock-llm` 대상에 한정된다.

## 안전 통제

- 최대 재시도: 3회
- 백오프 정책: 1초, 2초, 4초
- 의존 서비스 요청 타임아웃: 5초
- 전체 워크플로 타임아웃 계약: 30초
- 회로 차단: 3회 실패 시 OPEN
- 회로 재개: 30초 냉각 후 헬스체크와 사람 승인 필요
- 원인 불명 장애: 자동 변경 금지, Notification payload 생성
- 민감정보: token·purchase_note 필터 테스트 통과

## Docker 검증

- `docker compose config`: PASS
- `docker compose build`: BLOCKED
- 차단 원인: Docker Desktop Linux engine daemon이 실행 중이지 않아 Docker API에 연결할 수 없음
- 영향: 로컬 Python 서버와 전체 unittest 검증은 완료했으나 컨테이너 실행 증거는 아직 없음

## 남은 제한

- 실제 Docker 컨테이너 실행은 Docker daemon을 시작한 뒤 재검증해야 한다.
- Notification은 외부 메시징 서비스로 전송하지 않고 로컬 payload와 구조화 로그로 검증한다.
- MTTD·MTTR의 정밀한 실험값은 컨테이너 환경에서 최종 데모를 재실행한 뒤 갱신한다.
