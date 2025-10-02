# 백업 전략

**Scholaria 데이터 백업 및 재해 복구 전략**

> 📚 **관련 문서**:
> - [DEPLOYMENT.md](DEPLOYMENT.md) - 프로덕션 배포 가이드
> - [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - 관리 패널 운영
> - `scripts/backup.sh`, `scripts/restore.sh` - 실제 백업/복원 스크립트

> ⚠️ **참고**: 이 문서는 백업 전략 개요 제공. 실제 실행은 위 스크립트 참조.

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

### 수동 백업
```bash
# PostgreSQL
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres scholaria > backup_$(date +%Y%m%d).sql

# 자동 스크립트 (권장)
./scripts/backup.sh
```

### 자동 백업 활성화
```bash
# 백업 서비스와 함께 시작
docker compose --profile backup up -d

# 상태 확인
docker compose exec backup /scripts/backup-scheduler.sh status
```

## 복원 절차

### 전체 복원
```bash
./scripts/restore.sh latest
```

### 선택적 복원
```bash
# PostgreSQL만
./scripts/restore.sh --component postgres latest

# 드라이런 (테스트)
./scripts/restore.sh --dry-run latest
```

## 재해 복구 시나리오

### DB 오류
1. 서비스 중단
2. 최신 백업 확인
3. `./scripts/restore.sh --component postgres latest`
4. 데이터 무결성 확인
5. 서비스 재시작

### 전체 장애
1. 새 환경 구성
2. Docker 환경 복원
3. `./scripts/restore.sh latest`
4. 서비스 검증

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

## 문제 해결

### 백업 실패
```bash
# 로그 확인
tail -f /var/log/scholaria/backup-daily-$(date +%Y%m%d).log

# 디스크 공간
df -h /backup

# 권한 확인
ls -la /backup
```

### 복원 실패
```bash
# 백업 무결성 검증
cd /backup/scholaria_backup_YYYYMMDD_HHMMSS
sha256sum -c SHA256SUMS

# 서비스 상태
docker compose ps
```

---

**참조:**
**참조:**
- 백업 스크립트: `scripts/backup.sh`
- 복원 스크립트: `scripts/restore.sh`
- 스케줄러: `scripts/backup-scheduler.sh`
- 배포 가이드: [DEPLOYMENT.md](DEPLOYMENT.md)
