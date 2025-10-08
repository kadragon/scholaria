# Research: 운영 데이터 백업/복원 가이드

## Goal
PostgreSQL, Redis, Qdrant 백업·복원 절차를 수립하고 운영 가이드 문서화.

## Scope
- 기존 백업 스크립트 (`backup.sh`, `restore.sh`, `backup-scheduler.sh`) 분석
- Docker Compose 인프라 (prod/dev 환경) 파악
- `BACKUP_STRATEGY.md` 문서 검토 및 개선 필요 사항 도출

## Related Files/Flows
- `scripts/backup.sh` — PostgreSQL (pg_dump), Redis (RDB), Qdrant (snapshot API) 백업
- `scripts/restore.sh` — 컴포넌트별/전체 복원, dry-run, 무결성 검증
- `scripts/backup-scheduler.sh` — cron 스케줄링 (daily/weekly/monthly), 헬스 체크, 알림
- `docs/BACKUP_STRATEGY.md` — 기존 전략 문서 (개요 제공)
- `docker-compose.yml`, `docker-compose.prod.yml` — 볼륨, 서비스 구성

## Hypotheses
1. 기존 스크립트는 백업·복원 기능을 **완전히 구현**했으나, **운영 가이드는 개요 수준**만 제공.
2. 실제 운영 시나리오 (재해 복구, 부분 복원, 프로덕션 절차) 상세 문서 필요.
3. 복구 리허설 절차 및 자동화 테스트가 부재.

## Evidence
- `backup.sh`:
  - PostgreSQL: custom + plain SQL 이중 백업, 압축, 무결성 체크섬
  - Redis: BGSAVE → RDB 복사 + 압축
  - Qdrant: HTTP 스냅샷 API + 압축
  - Manifest JSON 생성, 보존 정책 적용
- `restore.sh`:
  - latest 자동 탐색, 컴포넌트별 복원 옵션
  - dry-run, 무결성 검증, 서비스 중지/재시작
  - 확인 프롬프트 (force 옵션 시 자동)
- `backup-scheduler.sh`:
  - cron 통합 (daily 02:00, weekly Sun 03:00, monthly 1일 04:00)
  - 보존 기간 (daily 7d, weekly 30d, monthly 365d)
  - 헬스 체크 (디스크 공간, 최신 백업 연령, 권한)
  - 이메일/웹훅 알림
- `BACKUP_STRATEGY.md`:
  - 주기·보존 정책 개요, 간단한 명령 예제, 환경 변수 목록
  - **실전 복구 시나리오, 리허설 절차, 자동화 검증 방법 미비**

## Assumptions/Open Qs
- ✅ 스크립트는 프로덕션 준비 완료 (무결성 검증, 로그, 알림 포함).
- ❓ 복구 리허설 자동화 (실제 복원 후 무결성 테스트) 필요 여부?
- ❓ 오프사이트 백업 전송 (S3, rsync 등) 절차 추가 여부?
- ❓ 프로덕션 환경에서 백업 서비스 프로파일 활성화 여부?

## Sub-agent Findings
(없음)

## Risks
- **데이터 손실**: 복구 절차 오류 시 프로덕션 데이터 유실 위험.
- **다운타임**: 복원 중 서비스 중단 (PostgreSQL 최대 수십 분).
- **디스크 공간**: 백업 볼륨 부족 시 실패.

## Next
→ **PLAN.md** 작성: 운영 가이드 구조 설계 및 검증 계획 수립.
