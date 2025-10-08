# Task Summary: 운영 데이터 백업/복원 가이드

## 목표
PostgreSQL, Redis, Qdrant 백업·복원 절차 수립 및 운영 가이드 문서화

## 핵심 변경
1. **`docs/BACKUP_STRATEGY.md`** 확장
   - 프로덕션 환경별 절차 (Docker, 베어메탈, 컨테이너 내부 실행)
   - 재해 복구 시나리오 5가지 (PostgreSQL 손상, Redis 손실, Qdrant 파손, 전체 장애, 데이터 삭제)
   - 복구 리허설 가이드 (월간/분기/반기 주기)
   - 트러블슈팅 (백업 실패 3가지, 복원 실패 3가지)
   - 오프사이트 백업 (AWS S3, rsync)

2. **`scripts/test-backup-restore.sh`** 신규
   - 자동화 리허설: 백업 → 복원 → 무결성 검증
   - 무결성 검증: PostgreSQL row count, Redis key count, Qdrant vector count
   - 옵션: `--keep-env`, `--backup-dir`

## 테스트
- 문서 검증: 신규 운영자가 가이드만으로 복원 수행 가능 여부 (peer review 권장)
- 스크립트 검증: `./scripts/test-backup-restore.sh` 실행 성공 (dev 환경)

## 커밋
- SHA: `06c0218`
- Type: [Structural]
- Message: "운영 백업/복원 가이드 확장 및 리허설 자동화"

## 영향 범위
- **문서**: `BACKUP_STRATEGY.md` 확장 (기존 개요 → 실전 가이드)
- **스크립트**: `test-backup-restore.sh` 추가 (기존 스크립트 미수정)
- **위험**: 없음 (프로덕션 코드/설정 미변경)
