# Progress: 운영 데이터 백업/복원 가이드

## Summary
PostgreSQL, Redis, Qdrant 백업·복원 절차를 문서화하고 자동화 리허설 스크립트 작성 완료.

## Goal & Approach
**목표**: 운영자가 독립적으로 백업·복원·리허설을 수행할 수 있는 실전 가이드 제공
**접근**: 기존 `BACKUP_STRATEGY.md` 확장 + 리허설 자동화 스크립트 추가

## Completed Steps

### Step 1: BACKUP_STRATEGY.md 확장
- **프로덕션 환경별 절차** 추가 (Docker Compose, 베어메탈, 컨테이너 내부 실행)
- **재해 복구 시나리오 5가지** 상세 작성:
  1. PostgreSQL 데이터 손상 (예상 다운타임 10-30분)
  2. Redis 캐시 손실 (예상 다운타임 5-10분)
  3. Qdrant 벡터 인덱스 파손 (다운타임 없음)
  4. 전체 인프라 장애 (복구 시간 1-2시간)
  5. 의도하지 않은 데이터 삭제 (병렬 환경 활용, 다운타임 없음)
- **복구 리허설 절차** 추가 (월간/분기/반기 주기 권장)
- **트러블슈팅 섹션** 추가 (백업 실패 3가지, 복원 실패 3가지 케이스)
- **오프사이트 백업** 절차 추가 (AWS S3, rsync)

### Step 2: test-backup-restore.sh 작성
- **기능**:
  - Docker Compose dev 환경 자동 구성
  - 테스트 데이터 시딩 (PostgreSQL 테이블, Redis 키, Qdrant 벡터)
  - 백업 실행 → 데이터 삭제 → 복원 → 무결성 검증
  - 베이스라인 vs 복원 데이터 비교 (row count, key count, vector count)
- **옵션**:
  - `--keep-env`: 테스트 환경 유지 (수동 검증용)
  - `--backup-dir DIR`: 백업 디렉토리 커스터마이징
- **에러 핸들링**: 실패 시 자동 정리 및 명확한 에러 메시지

## Current Failures
없음 (문서 검증 및 스크립트 dry-run 필요)

## Decision Log
1. **기존 스크립트 수정 금지** → 프로덕션 안정성 유지, 문서/자동화만 추가
2. **BACKUP_STRATEGY.md 확장** → 새 문서 생성 대신 기존 개요를 실전 가이드로 변환
3. **리허설 스크립트 dev 환경 타겟** → 프로덕션 백업 활용하되 격리된 환경에서 검증
4. **무결성 검증 단순화** → row/key/vector count 비교로 빠른 피드백 루프 제공

## Next Step
- **Validation**: 스크립트 실행 및 문서 peer review
- **AGENTS.md 반영**: 복구 리허설 주기 및 트러블슈팅 패턴 추가
- **커밋**: `[Structural] docs: 운영 백업/복원 가이드 확장 및 리허설 자동화 [backup-restore-guide]`
