# 운영 데이터 백업 및 복원 가이드

**Scholaria 프로덕션 백업·복원 실전 운영 가이드**

> 📚 **관련 문서**:
> - [DEPLOYMENT.md](DEPLOYMENT.md) - 프로덕션 배포 가이드
> - [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - 관리 패널 운영
> - `scripts/backup.sh`, `scripts/restore.sh`, `scripts/backup-scheduler.sh` - 백업/복원 자동화
> - `scripts/test-backup-restore.sh` - 백업 무결성 테스트

> 🎯 **목적**: 운영자가 백업·복원·리허설을 독립적으로 수행할 수 있는 완전한 절차 제공.

## 백업 대상

### 데이터베이스 & 저장소
- **PostgreSQL**: 사용자, 토픽, 컨텍스트, 청크
- **Redis**: 세션, 캐시, Celery 큐
- **Qdrant**: 벡터 임베딩 & 인덱스

## 백업 주기

| 유형 | 주기 | 보존 기간 | 용도 |
|------|------|-----------|------|
| 일일 | 매일 02:00 | 7일 | 빠른 복원 |
| 주간 | 일요일 03:00 | 30일 | 중기 보호 |
| 월간 | 1일 04:00 | 365일 | 장기 보호 |

## 백업 실행

### 프로덕션 환경별 절차

#### Docker Compose 환경
```bash
# 1. 환경 변수 설정 (.env)
export BACKUP_DIR=/var/backups/scholaria
export RETENTION_DAYS=7

# 2. 수동 백업 (권장)
./scripts/backup.sh

# 3. 백업 확인
ls -lh ${BACKUP_DIR}/scholaria_backup_*/
cat ${BACKUP_DIR}/scholaria_backup_*/backup_manifest.json

# 4. 무결성 검증
cd ${BACKUP_DIR}/scholaria_backup_*/
sha256sum -c SHA256SUMS
```

#### 자동 백업 스케줄링 (cron)
```bash
# 1. cron 잡 설치 (root 권한 필요)
./scripts/backup-scheduler.sh install-cron

# 2. 스케줄 확인
./scripts/backup-scheduler.sh status

# 3. 수동 실행 (테스트)
./scripts/backup-scheduler.sh daily

# 4. 헬스 체크
./scripts/backup-scheduler.sh health-check
```

#### 컨테이너 내부에서 실행 (베어메탈 불가 시)
```bash
# 백업 스크립트를 컨테이너에 복사 후 실행
docker compose -f docker-compose.prod.yml exec postgres bash -c "
  export BACKUP_DIR=/backup
  export POSTGRES_PASSWORD=\$POSTGRES_PASSWORD
  /scripts/backup.sh
"

# 백업 파일을 호스트로 복사 (최신 백업 자동 탐색)
LATEST_BACKUP=$(docker compose -f docker-compose.prod.yml exec postgres ls -t /backup | head -n 1)
docker cp "postgres:/backup/${LATEST_BACKUP}" ./backups/
```

## 복원 절차

### 사전 점검 (복원 전 필수)
```bash
# 1. 최신 백업 확인
ls -lht ${BACKUP_DIR}/scholaria_backup_*/ | head -5

# 2. 백업 무결성 검증
./scripts/restore.sh --dry-run latest

# 3. 디스크 공간 확인 (PostgreSQL 덤프의 2배 이상 권장)
df -h /var/lib/postgresql

# 4. 서비스 중단 계획 수립 (복원 중 다운타임 발생)
```

### 전체 복원 (프로덕션)
```bash
# 1. 서비스 중단 (자동으로 진행되지만 사전 공지 권장)
docker compose -f docker-compose.prod.yml stop backend celery-worker

# 2. 복원 실행 (확인 프롬프트 응답 필요)
./scripts/restore.sh latest

# 3. 데이터 무결성 검증
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres -d scholaria -c "SELECT COUNT(*) FROM topics;"
docker compose -f docker-compose.prod.yml exec redis redis-cli DBSIZE

# 4. 서비스 재시작
docker compose -f docker-compose.prod.yml up -d

# 5. 헬스 체크
curl -f http://localhost:8001/health
```

### 선택적 복원 (컴포넌트별)
```bash
# PostgreSQL만 복원 (Redis/Qdrant 유지)
./scripts/restore.sh --component postgres latest

# Redis만 복원 (세션 캐시 초기화)
./scripts/restore.sh --component redis latest

# Qdrant만 복원 (벡터 인덱스 재구성)
./scripts/restore.sh --component qdrant latest
```

### 특정 시점 복원 (PITR)
```bash
# 1. 백업 목록 조회
ls -lh ${BACKUP_DIR}/scholaria_backup_*/

# 2. 특정 백업 선택
./scripts/restore.sh ${BACKUP_DIR}/scholaria_backup_20241001_020000

# 3. 강제 복원 (프롬프트 생략)
./scripts/restore.sh --force ${BACKUP_DIR}/scholaria_backup_20241001_020000
```

### 드라이런 모드 (테스트)
```bash
# 복원 시뮬레이션 (실제 변경 없음)
./scripts/restore.sh --dry-run latest

# 출력 예:
# [DRY RUN] Would restore PostgreSQL from: postgres_20241001_020000.sql.custom
# [DRY RUN] Would restore Redis from: redis_20241001_020000.rdb.gz
# [DRY RUN] Would restore Qdrant from: qdrant_20241001_020000/qdrant_snapshot.tar.gz
```

## 재해 복구 시나리오

### 시나리오 1: PostgreSQL 데이터 손상
**증상**: 애플리케이션 에러, SQL 쿼리 실패, 트랜잭션 롤백 반복

**복구 절차**:
```bash
# 1. 에러 로그 확인
docker compose -f docker-compose.prod.yml logs postgres | tail -100

# 2. 서비스 중단
docker compose -f docker-compose.prod.yml stop backend celery-worker

# 3. PostgreSQL만 복원
./scripts/restore.sh --component postgres latest

# 4. 스키마 검증
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres -d scholaria -c "\dt"
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres -d scholaria -c "SELECT COUNT(*) FROM topics;" -c "SELECT COUNT(*) FROM context_items;"

# 5. 마이그레이션 확인 (Alembic)
docker compose -f docker-compose.prod.yml exec backend alembic current
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 6. 서비스 재시작
docker compose -f docker-compose.prod.yml up -d

# 7. 애플리케이션 검증
curl -f http://localhost:8001/api/topics | jq '.[0]'
```

**예상 다운타임**: 중형 DB 기준 10-30분

---

### 시나리오 2: Redis 캐시 손실
**증상**: 세션 만료, 캐시 미스율 100%, Celery 태스크 유실

**복구 절차**:
```bash
# 1. Redis 상태 확인
docker compose -f docker-compose.prod.yml exec redis redis-cli INFO | grep "used_memory"

# 2. Celery 워커 중단 (태스크 큐 보존)
docker compose -f docker-compose.prod.yml stop celery-worker

# 3. Redis 복원
./scripts/restore.sh --component redis latest

# 4. 캐시 검증
docker compose -f docker-compose.prod.yml exec redis redis-cli DBSIZE
docker compose -f docker-compose.prod.yml exec redis redis-cli --scan --pattern "embedding_cache:*" | wc -l

# 5. Celery 워커 재시작
docker compose -f docker-compose.prod.yml up -d celery-worker

# 6. 태스크 큐 확인
docker compose -f docker-compose.prod.yml exec celery-worker celery -A backend.celery_app inspect active
```

**예상 다운타임**: 5-10분 (세션 재로그인 필요)

---

### 시나리오 3: Qdrant 벡터 인덱스 파손
**증상**: 검색 결과 공백, RAG 응답 품질 저하, Qdrant API 에러

**복구 절차**:
```bash
# 1. Qdrant 컬렉션 상태 확인
curl -s http://localhost:6333/collections/scholaria_documents | jq '.result.vectors_count'

# 2. Qdrant 복원
./scripts/restore.sh --component qdrant latest

# 3. 벡터 개수 검증
curl -s http://localhost:6333/collections/scholaria_documents | jq '.result'

# 4. 검색 테스트
curl -X POST http://localhost:8001/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "테스트 쿼리", "topic_slug": "test"}'
```

**예상 다운타임**: 없음 (검색 품질만 영향)

---

### 시나리오 4: 전체 인프라 장애 (서버 손실)
**전제 조건**: 백업이 오프사이트 (S3, NAS 등)에 존재

**복구 절차**:
```bash
# 1. 새 서버 프로비저닝 (Ubuntu 22.04+)
# 2. Docker 설치
curl -fsSL https://get.docker.com | sh

# 3. 저장소 클론 및 환경 설정
git clone https://github.com/your-org/scholaria.git
cd scholaria
cp .env.prod.example .env.prod
vim .env.prod  # SECRET_KEY, JWT_SECRET_KEY, OPENAI_API_KEY 설정

# 4. 백업 다운로드
mkdir -p /var/backups/scholaria
rsync -avz backup-server:/backup/scholaria_backup_latest/ /var/backups/scholaria/

# 5. Docker Compose 시작 (빈 DB로 초기화)
docker compose -f docker-compose.prod.yml up -d postgres redis qdrant

# 6. 전체 복원
export BACKUP_DIR=/var/backups/scholaria
./scripts/restore.sh --force latest

# 7. 애플리케이션 시작
docker compose -f docker-compose.prod.yml up -d

# 8. 전체 헬스 체크
./scripts/backup-scheduler.sh health-check
curl -f http://localhost:8001/health
curl -f http://localhost:6333/health
```

**예상 복구 시간**: 1-2시간 (인프라 프로비저닝 포함)

---

### 시나리오 5: 의도하지 않은 데이터 삭제
**증상**: 토픽/컨텍스트 항목 누락, 사용자 신고

**복구 절차**:
```bash
# 1. 삭제 시점 추정 (애플리케이션 로그 확인)
docker compose -f docker-compose.prod.yml logs backend | grep "DELETE"

# 2. 삭제 직전 백업 선택
ls -lh ${BACKUP_DIR}/scholaria_backup_*/ | grep "$(date -d '2 hours ago' +%Y%m%d)"

# 3. 임시 환경에서 복원 (프로덕션 영향 없음)
docker compose -f docker-compose.dev.yml up -d
export BACKUP_DIR=/var/backups/scholaria
./scripts/restore.sh --force ${BACKUP_DIR}/scholaria_backup_20241008_100000

# 4. 데이터 추출
docker compose -f docker-compose.dev.yml exec postgres pg_dump -U postgres -d scholaria -t topics -t context_items > /tmp/deleted_data.sql

# 5. 프로덕션에 선택적 복원
docker compose -f docker-compose.prod.yml exec -T postgres psql -U postgres -d scholaria < /tmp/deleted_data.sql
```

**예상 다운타임**: 없음 (병렬 환경 활용)

## 환경 변수

백업 동작은 `.env`에서 설정:

```bash
BACKUP_DAILY_RETENTION=7
BACKUP_WEEKLY_RETENTION=30
BACKUP_MONTHLY_RETENTION=365
BACKUP_NOTIFY_EMAIL=admin@example.com
BACKUP_NOTIFY_WEBHOOK=https://hooks.slack.com/...
```

## 모니터링

### 헬스 체크
```bash
./scripts/backup-scheduler.sh health-check
```

헬스 체크 항목:
- 백업 디렉토리 접근
- 최근 백업 존재 여부
- 디스크 공간
- 스크립트 실행 권한

### 알림
- **이메일**: 백업 성공/실패
- **웹훅**: Slack/Discord 통합
- **로그**: `/var/log/scholaria/backup-*.log`

## 보안

- 백업 무결성: SHA256 체크섬
- 접근 권한: 최소 권한 원칙
- 암호화: 전송 중/저장 시 (옵션)
- 감사 로그: 모든 백업/복원 기록

## 복구 리허설 (정기 훈련)

### 목적
- 백업 무결성 검증
- 복구 절차 숙지
- RTO/RPO 측정

### 리허설 절차
```bash
# 1. 테스트 환경 준비 (프로덕션과 격리)
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d

# 2. 자동화 리허설 스크립트 실행
./scripts/test-backup-restore.sh

# 출력 예:
# [OK] Backup created: /backup/scholaria_backup_20241008_140000
# [OK] Restore completed: PostgreSQL, Redis, Qdrant
# [OK] Data integrity verified:
#      - PostgreSQL: 25 topics, 150 context_items
#      - Redis: 320 keys
#      - Qdrant: 1500 vectors in scholaria_documents
# [OK] All checks passed in 3m 25s

# 3. 수동 검증 (샘플 데이터 확인)
docker compose -f docker-compose.dev.yml exec postgres psql -U postgres -d scholaria -c "SELECT * FROM topics LIMIT 5;"

# 4. 테스트 환경 정리
docker compose -f docker-compose.dev.yml down -v
```

### 리허설 주기 권장
- **월간**: 전체 복원 리허설 (프로덕션 백업 활용)
- **분기**: 재해 복구 시나리오 실행 (새 서버 구성 포함)
- **반기**: 오프사이트 백업 복원 테스트

---

## 트러블슈팅

### 백업 실패

#### 증상 1: "Disk full" 에러
```bash
# 디스크 사용량 확인
df -h ${BACKUP_DIR}

# 해결: 오래된 백업 수동 삭제
find ${BACKUP_DIR} -type d -name "scholaria_backup_*" -mtime +30 -exec rm -rf {} \;

# 또는 보존 기간 단축
export DAILY_RETENTION=3
./scripts/backup-scheduler.sh daily
```

#### 증상 2: PostgreSQL 연결 실패
```bash
# PostgreSQL 상태 확인
docker compose ps postgres
docker compose logs postgres | tail -50

# 해결: 컨테이너 재시작
docker compose restart postgres
docker compose exec postgres pg_isready -U postgres
```

#### 증상 3: Qdrant 스냅샷 생성 실패
```bash
# Qdrant 컬렉션 확인
curl -s http://localhost:6333/collections | jq '.'

# 해결: Qdrant 재시작 후 재시도
docker compose restart qdrant
sleep 10
./scripts/backup.sh
```

---

### 복원 실패

#### 증상 1: "Checksum mismatch" 에러
```bash
# 백업 무결성 재검증
cd ${BACKUP_DIR}/scholaria_backup_YYYYMMDD_HHMMSS
sha256sum -c SHA256SUMS

# 해결: 이전 백업 선택
./scripts/restore.sh $(ls -dt ${BACKUP_DIR}/scholaria_backup_* | sed -n 2p)
```

#### 증상 2: PostgreSQL 복원 중 "role does not exist" 에러
```bash
# 사용자 생성
docker compose exec postgres psql -U postgres -c "CREATE ROLE scholaria WITH LOGIN PASSWORD 'your-secure-password';"

# 재시도
./scripts/restore.sh --component postgres latest
```

#### 증상 3: Redis 복원 후 키 없음
```bash
# Redis 재시작 후 RDB 로드 확인
docker compose restart redis
docker compose logs redis | grep "DB loaded"

# 수동 복원
docker compose stop redis
docker cp ${BACKUP_DIR}/scholaria_backup_latest/redis_*.rdb.gz /tmp/
gunzip /tmp/redis_*.rdb.gz
docker cp /tmp/redis_*.rdb redis:/data/dump.rdb
docker compose start redis
```

---

## 오프사이트 백업 (선택)

### AWS S3 동기화
```bash
# 1. AWS CLI 설치 및 인증
aws configure

# 2. 백업 업로드 (cron 추가 권장)
aws s3 sync ${BACKUP_DIR}/ s3://scholaria-backups/prod/ \
  --exclude "*" \
  --include "scholaria_backup_*" \
  --storage-class STANDARD_IA

# 3. 복원 시 다운로드
aws s3 sync s3://scholaria-backups/prod/scholaria_backup_YYYYMMDD_HHMMSS/ \
  ${BACKUP_DIR}/scholaria_backup_YYYYMMDD_HHMMSS/
```

### rsync (NAS/원격 서버)
```bash
# 백업 서버로 전송 (cron 추가)
rsync -avz --delete \
  ${BACKUP_DIR}/ \
  backup-server:/mnt/backups/scholaria/

# 복원 시 다운로드
rsync -avz \
  backup-server:/mnt/backups/scholaria/scholaria_backup_YYYYMMDD_HHMMSS/ \
  ${BACKUP_DIR}/
```

---

## 참조

- **백업 스크립트**: `scripts/backup.sh`
- **복원 스크립트**: `scripts/restore.sh`
- **스케줄러**: `scripts/backup-scheduler.sh`
- **리허설 자동화**: `scripts/test-backup-restore.sh`
- **배포 가이드**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **관리 가이드**: [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
