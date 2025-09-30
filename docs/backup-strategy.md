# Scholaria 데이터베이스 백업 전략

## 개요

Scholaria 시스템의 데이터 안전성과 비즈니스 연속성을 보장하기 위한 포괄적인 백업 및 복원 전략입니다.

## 백업 대상

### 1. PostgreSQL 데이터베이스
- **데이터**: 사용자 데이터, 토픽, 컨텍스트, 청크, 관리자 설정
- **스키마**: 테이블 구조, 인덱스, 제약조건
- **메타데이터**: 권한, 함수, 트리거

### 2. Redis 캐시
- **세션 데이터**: 사용자 세션 정보
- **캐시 데이터**: 임시 처리 결과, API 응답 캐시
- **Celery 작업**: 백그라운드 작업 큐

### 3. Qdrant 벡터 데이터베이스
- **벡터 임베딩**: 문서 및 청크 벡터 데이터
- **컬렉션 메타데이터**: 인덱스 설정, 컬렉션 구성
- **벡터 검색 인덱스**: 검색 성능 최적화 데이터

## 백업 유형 및 주기

### 1. 일일 백업 (Daily Backup)
- **주기**: 매일 오전 2시 실행
- **보존 기간**: 7일
- **용도**: 일상적인 데이터 보호, 빠른 복원

### 2. 주간 백업 (Weekly Backup)
- **주기**: 매주 일요일 오전 3시 실행
- **보존 기간**: 30일 (약 4주)
- **용도**: 중기 데이터 보호, 월간 복원 지점

### 3. 월간 백업 (Monthly Backup)
- **주기**: 매월 1일 오전 4시 실행
- **보존 기간**: 365일 (1년)
- **용도**: 장기 데이터 보호, 연간 복원 지점

## 백업 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PostgreSQL    │───▶│  Backup Scripts  │───▶│  Backup Volume  │
└─────────────────┘    │                  │    └─────────────────┘
                       │  - backup.sh     │
┌─────────────────┐    │  - restore.sh    │    ┌─────────────────┐
│     Redis       │───▶│  - scheduler.sh  │───▶│   Log Volume    │
└─────────────────┘    │                  │    └─────────────────┘
                       │  Docker Container │
┌─────────────────┐    │  (Alpine Linux)  │    ┌─────────────────┐
│     Qdrant      │───▶│                  │───▶│  Notifications  │
└─────────────────┘    └──────────────────┘    │  (Email/Webhook)│
                                               └─────────────────┘
```

## 백업 파일 구조

```
/backup/
├── scholaria_backup_20240301_020000/
│   ├── backup_manifest.json          # 백업 메타데이터
│   ├── SHA256SUMS                     # 체크섬 파일
│   ├── postgres_20240301_020000.sql.custom  # PostgreSQL 커스텀 포맷
│   ├── postgres_20240301_020000.sql.gz      # PostgreSQL SQL 덤프
│   ├── redis_20240301_020000.rdb.gz         # Redis RDB 파일
│   └── qdrant_20240301_020000/
│       └── qdrant_snapshot.tar.gz           # Qdrant 스냅샷
├── scholaria_backup_20240302_020000/
└── ...
```

## 백업 스크립트

### 1. `backup.sh`
주요 백업 스크립트로 다음 기능을 제공:
- PostgreSQL 덤프 (커스텀 포맷 및 SQL 포맷)
- Redis RDB 파일 백업
- Qdrant 스냅샷 생성
- 백업 무결성 검증
- 메타데이터 및 체크섬 생성

### 2. `restore.sh`
복원 스크립트로 다음 기능을 제공:
- 선택적 복원 (특정 컴포넌트만)
- 백업 무결성 검증
- 드라이 런 모드
- 안전한 복원 절차

### 3. `backup-scheduler.sh`
스케줄링 및 관리 스크립트:
- 자동화된 백업 실행
- 헬스 체크
- 알림 발송
- 상태 모니터링

## Docker 환경 설정

### 백업 서비스 활성화
```bash
# 백업 서비스와 함께 시작
docker-compose --profile backup up -d

# 수동 백업 실행
docker-compose exec backup /scripts/backup.sh

# 복원 실행
docker-compose exec backup /scripts/restore.sh latest

# 상태 확인
docker-compose exec backup /scripts/backup-scheduler.sh status
```

### 환경 변수 설정
```bash
# .env 파일에 추가
BACKUP_DAILY_RETENTION=7
BACKUP_WEEKLY_RETENTION=30
BACKUP_MONTHLY_RETENTION=365
BACKUP_NOTIFY_EMAIL=admin@example.com
BACKUP_NOTIFY_WEBHOOK=https://hooks.slack.com/...
```

## 복원 절차

### 1. 전체 시스템 복원
```bash
# 최신 백업에서 전체 복원
./scripts/restore.sh latest

# 특정 백업에서 복원
./scripts/restore.sh /backup/scholaria_backup_20240301_020000
```

### 2. 선택적 복원
```bash
# PostgreSQL만 복원
./scripts/restore.sh --component postgres latest

# Redis만 복원
./scripts/restore.sh --component redis latest

# Qdrant만 복원
./scripts/restore.sh --component qdrant latest
```

### 3. 드라이 런 모드
```bash
# 실제 복원 없이 테스트
./scripts/restore.sh --dry-run latest
```

## 모니터링 및 알림

### 1. 헬스 체크
- 백업 디렉토리 접근성
- 최근 백업 존재 여부
- 디스크 공간 확인
- 스크립트 실행 가능성

### 2. 알림 시스템
- **이메일**: 백업 성공/실패 알림
- **웹훅**: Slack, Discord 등 통합
- **로그**: 상세한 실행 로그 기록

### 3. 상태 모니터링
```bash
# 백업 시스템 상태 확인
./scripts/backup-scheduler.sh status

# 헬스 체크 실행
./scripts/backup-scheduler.sh health-check
```

## 보안 고려사항

### 1. 접근 권한
- 백업 파일 암호화 (필요시)
- 최소 권한 원칙 적용
- 네트워크 격리

### 2. 데이터 보호
- 백업 무결성 검증 (SHA256)
- 전송 중 암호화
- 저장 시 암호화 (옵션)

### 3. 감사 로그
- 모든 백업/복원 작업 로깅
- 접근 기록 유지
- 이상 행위 모니터링

## 재해 복구 시나리오

### 1. 데이터베이스 오류
1. 서비스 중단
2. 최신 백업 확인
3. 선택적 복원 실행
4. 데이터 무결성 확인
5. 서비스 재시작

### 2. 전체 시스템 장애
1. 새로운 환경 구성
2. Docker 환경 복원
3. 전체 백업 복원
4. 서비스 검증
5. DNS 변경 (필요시)

### 3. 부분 데이터 손실
1. 문제 범위 확인
2. 백업 시점 선택
3. 선택적 복원
4. 데이터 병합 (필요시)
5. 테스트 및 검증

## 성능 최적화

### 1. 백업 최적화
- 증분 백업 고려 (향후)
- 압축률 최적화
- 병렬 처리 활용

### 2. 저장소 최적화
- 자동 정리 정책
- 압축 전략
- 중복 제거

### 3. 네트워크 최적화
- 대역폭 제한
- 압축 전송
- 재시도 메커니즘

## 테스트 및 검증

### 1. 백업 테스트
```bash
# 정기적인 백업 테스트 (월 1회 권장)
./scripts/backup.sh
./scripts/restore.sh --dry-run latest
```

### 2. 복원 테스트
```bash
# 테스트 환경에서 복원 검증
# 1. 테스트 환경 구성
# 2. 프로덕션 백업 복원
# 3. 데이터 무결성 확인
# 4. 기능 테스트 실행
```

### 3. 재해 복구 드릴
- 분기별 재해 복구 시뮬레이션
- RTO/RPO 목표 달성도 측정
- 절차 개선 사항 도출

## 문제 해결

### 일반적인 문제

#### 1. 백업 실패
```bash
# 로그 확인
tail -f /var/log/scholaria/backup-daily-$(date +%Y%m%d).log

# 디스크 공간 확인
df -h /backup

# 권한 확인
ls -la /backup
```

#### 2. 복원 실패
```bash
# 백업 무결성 확인
cd /backup/scholaria_backup_YYYYMMDD_HHMMSS
sha256sum -c SHA256SUMS

# 서비스 상태 확인
docker-compose ps
```

#### 3. 네트워크 연결 문제
```bash
# 데이터베이스 연결 테스트
pg_isready -h postgres -p 5432

# Redis 연결 테스트
redis-cli -h redis ping

# Qdrant 연결 테스트
curl http://qdrant:6333/health
```

## 연락처 및 지원

문제 발생 시 다음 절차를 따르세요:

1. **즉시 대응**: 로그 확인 및 기본 문제 해결
2. **에스컬레이션**: 복잡한 문제 시 개발팀 연락
3. **문서화**: 모든 문제 및 해결 과정 기록

---

*이 문서는 Scholaria 백업 시스템의 종합 가이드입니다. 정기적으로 업데이트하고 팀과 공유하시기 바랍니다.*
