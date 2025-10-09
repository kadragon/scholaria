# Plan: 운영 데이터 백업/복원 가이드

## Objective
운영자를 위한 **실전 백업·복원 가이드** 작성 및 복구 리허설 절차 수립.

## Constraints
- 기존 스크립트 (`backup.sh`, `restore.sh`, `backup-scheduler.sh`) 수정 금지 (프로덕션 안정성 유지).
- 문서는 **`BACKUP_STRATEGY.md` 개선**으로 진행 (기존 개요 → 실전 운영 가이드).
- 복구 리허설은 **자동화 스크립트 추가** (`scripts/test-backup-restore.sh`).

## Target Files & Changes
1. **`docs/BACKUP_STRATEGY.md`** — 확장·개선
   - **추가**: 프로덕션 환경별 절차 (Docker, 베어메탈), 상세 복구 시나리오, 리허설 가이드, 트러블슈팅
   - **유지**: 기존 개요, 주기·보존 정책, 환경 변수
2. **`scripts/test-backup-restore.sh`** — 신규 작성
   - 백업 생성 → 복원 → 무결성 검증 (PostgreSQL row count, Redis key count, Qdrant collection)
   - CI/CD 통합 가능 (선택적)

## Test/Validation Cases
### 문서 검증
- [ ] 신규 운영자가 가이드만으로 백업·복원 수행 가능한지 확인 (peer review)
- [ ] 모든 시나리오 (DB 오류, 전체 장애, 부분 복원) 커버
- [ ] 코드 블록에 실행 가능한 명령어 포함

### 스크립트 검증
- [ ] `test-backup-restore.sh` 실행 → 백업 생성 성공
- [ ] 복원 후 데이터 무결성 (PostgreSQL 스키마/레코드, Redis 키, Qdrant 벡터 개수) 검증
- [ ] dry-run 옵션 동작 확인
- [ ] 실패 시 적절한 에러 메시지 출력

## Steps
1. **[Structural]** `BACKUP_STRATEGY.md` 확장
   - 프로덕션 환경별 절차, 복구 시나리오, 리허설 가이드 추가
2. **[Behavioral]** `test-backup-restore.sh` 작성
   - 백업·복원·검증 자동화 스크립트
3. **[Structural]** `PROGRESS.md` 갱신

## Rollback
- Git revert 가능 (문서·스크립트만 변경).
- 기존 스크립트 미수정으로 프로덕션 리스크 없음.

## Review Hotspots
- `BACKUP_STRATEGY.md` 복구 시나리오 정확성 (PostgreSQL 드롭/재생성, Qdrant 스냅샷 업로드).
- `test-backup-restore.sh` 무결성 검증 로직 (실패 케이스 탐지 가능 여부).

## Status
- [ ] Step 1: `BACKUP_STRATEGY.md` 확장
- [ ] Step 2: `test-backup-restore.sh` 작성
- [ ] Step 3: 검증 및 `PROGRESS.md` 갱신
