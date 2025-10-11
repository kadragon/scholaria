# Deployment Guide

**Scholaria RAG System (FastAPI) 프로덕션 배포 완전 가이드**

> 📚 **관련 문서**:
> - [README.md](../README.md) - 프로젝트 개요 & 개발 환경 설정
> - [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - 관리 패널 사용법
> - [backup-strategy.md](backup-strategy.md) - 백업/복원 전략
> - [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) - 기술 스택 선택 배경
> - `.env.example` - 프로덕션 환경 변수 전체 목록

## Prerequisites

Before deploying Scholaria, ensure you have the following:

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.13+ (for development/management)
- **uv** package manager for Python dependency management
- **OpenAI API Key** for embeddings and chat completions
- **Minimum 4GB RAM** and **20GB disk space**
- **HTTPS/SSL certificate** for production (recommended)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd scholaria

# Install dependencies (for management commands)
(cd backend && uv sync)
```

### 2. Environment Configuration

Create a `.env` file from the example:

```bash
# Copy the environment template
cp .env.example .env

# Edit with your production values
nano .env
```

### 3. Start Services (Production)

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check service status
docker compose -f docker-compose.prod.yml ps
```

### 4. Initialize Database

```bash
# Run database migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create admin user (interactive Python shell)
docker compose -f docker-compose.prod.yml exec backend python -c "
from backend.models.user import User
from backend.auth.utils import pwd_context
from backend.models.base import SessionLocal

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@example.com',
    password=pwd_context.hash('your-secure-password'),
    is_active=True,
    is_staff=True,
    is_superuser=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

### 5. Verify Deployment

```bash
# Check service health
curl http://localhost/health

# Check API endpoints
curl http://localhost/api/topics/

# Access API documentation
open http://localhost/docs

# Access admin panel
open http://localhost/admin

# Access observability dashboards
open http://localhost:16686  # Jaeger UI
open http://localhost:9090   # Prometheus UI
open http://localhost:3001   # Grafana UI (admin/admin)
```

## Production Setup

### Docker Compose Services

`docker-compose.prod.yml`이 다음 서비스들을 제공:

**핵심 서비스:**
- **backend**: FastAPI (uvicorn ASGI)
- **celery-worker**: 비동기 작업 처리 (임베딩, 문서 수집)
- **admin-frontend**: Refine 관리 패널 (nginx 정적 서빙)
- **nginx**: 리버스 프록시 & 로드 밸런서
- **PostgreSQL 16**: 메인 데이터베이스
- **Redis 7**: 캐시 & Celery 브로커
- **Qdrant**: 벡터 데이터베이스

**볼륨:**
- `postgres_data`: DB 영속성
- `redis_data`: 캐시 영속성
- `qdrant_data`: 벡터 저장소

### 아키텍처

```
Internet → Nginx (80/443) → FastAPI Backend (8001)
                          → Admin Frontend (정적)

FastAPI → PostgreSQL (5432)
       → Redis (6379) ← Celery Worker
       → Qdrant (6333)
       → OpenAI API
```

## Environment Variables

> 📋 **참고**: 전체 환경 변수 목록은 `.env.example` 파일을 참조하세요.

### 필수 변수 (JWT & Auth)

```bash
# JWT Configuration (REQUIRED)
JWT_SECRET_KEY=your-very-long-random-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24
```

**Generate a secure JWT secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Database Configuration

```bash
# PostgreSQL
DATABASE_URL=postgresql://postgres:secure-password@postgres:5432/scholaria
# 또는 개별 설정
DB_ENGINE=postgresql
DB_NAME=scholaria
DB_USER=postgres
DB_PASSWORD=your-secure-database-password  # 필수
DB_HOST=postgres
DB_PORT=5432
```

> ⚠️ **중요**: `DB_PASSWORD`는 기본값 없음. 모든 환경에서 명시적 설정 필요.

### AI 및 서비스 설정

```bash
# OpenAI (필수)
OPENAI_API_KEY=sk-your-openai-api-key-here

# 임베딩 & 채팅 모델 (옵션, 기본값 사용 가능)
OPENAI_EMBEDDING_MODEL=text-embedding-3-large  # 기본값
OPENAI_CHAT_MODEL=gpt-4o-mini                   # 기본값
OPENAI_EMBEDDING_DIM=3072                       # 기본값
OPENAI_CHAT_TEMPERATURE=0.3                     # 기본값
OPENAI_CHAT_MAX_TOKENS=1000                     # 기본값
```

### 벡터 DB & 캐시

```bash
# Redis (Celery 브로커 & 캐시)
REDIS_URL=redis://redis:6379/0

# Qdrant (벡터 검색)
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=context_items  # 기본값
```

### CORS 및 성능

```bash
# CORS (프로덕션 필수)
FASTAPI_ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# RAG 검색 파라미터 (옵션)
RAG_SEARCH_LIMIT=15           # 초기 검색 결과 수
RAG_RERANK_TOP_K=7            # 리랭킹 후 최종 결과 수
```



### 프로덕션 .env 예시

```bash
DEBUG=False
JWT_SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(32))">
DATABASE_URL=postgresql://postgres:secure-pw@postgres:5432/scholaria
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=sk-xxx
QDRANT_URL=http://qdrant:6333
FASTAPI_ALLOWED_ORIGINS=https://yourdomain.com

# Observability (OpenTelemetry)
OTEL_ENABLED=true
OTEL_TRACES_SAMPLER_ARG=0.1  # 10% sampling for production
PROMETHEUS_METRICS_ENABLED=true
```

> 🔒 **보안**: `JWT_SECRET_KEY`, `DB_PASSWORD`, `OPENAI_API_KEY`는 반드시 프로덕션 환경에서 설정 필요. 기본값 사용 금지.

상세 환경 변수 설명은 `.env.example` 참조.

## Observability

Scholaria includes comprehensive observability with OpenTelemetry, Jaeger, Prometheus, and Grafana:

### Services

```yaml
# docker-compose.yml includes:
- jaeger:16686     # Trace visualization UI
- prometheus:9090  # Metrics scraping & UI
- grafana:3001     # Dashboard UI (login: admin/admin)
```

### Configuration

```bash
# Enable/disable observability
OTEL_ENABLED=true

# Trace sampling (reduce overhead in production)
OTEL_TRACES_SAMPLER_ARG=0.1  # 10% of traces (recommended for prod)
OTEL_TRACES_SAMPLER_ARG=1.0  # 100% of traces (dev/testing)

# Metrics endpoint
PROMETHEUS_METRICS_ENABLED=true  # Exposes /metrics
```

### Access Dashboards

```bash
# Jaeger: View distributed traces
open http://localhost:16686

# Prometheus: Query metrics
open http://localhost:9090

# Grafana: Pre-configured RAG dashboard
open http://localhost:3001  # Login: admin/admin
# Navigate to: Dashboards → Scholaria RAG Pipeline
```

### Performance Impact

- **Overhead**: ~4% latency increase with 100% sampling
- **Recommended**: Use 10% sampling (`OTEL_TRACES_SAMPLER_ARG=0.1`) in production
- **Disable**: Set `OTEL_ENABLED=false` to completely disable instrumentation

### Troubleshooting

See `docs/OBSERVABILITY.md` for:
- Detailed configuration reference
- Dashboard usage guide
- Performance tuning
- Common issues and solutions

## Database Management

### Migrations

```bash
# Create new migration
docker compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Rollback last migration
docker compose -f docker-compose.prod.yml exec backend alembic downgrade -1

# View migration history
docker compose -f docker-compose.prod.yml exec backend alembic history
```

### 데이터베이스 백업

```bash
# 자동 백업 (스크립트 사용)
./scripts/backup.sh

# 수동 백업
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres scholaria > backup_$(date +%Y%m%d).sql

# 복원
docker compose -f docker-compose.prod.yml exec -i postgres psql -U postgres scholaria < backup.sql
```

> 📦 **백업 전략**: 상세 백업/복원 절차는 `scripts/backup.sh`, `scripts/restore.sh` 참조. 일일/주간/월간 백업 스케줄 지원.

## Security

### 필수 보안 조치

1. **JWT Secret**: 프로덕션에서 반드시 생성
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **데이터베이스 보안**:
   - 강력한 패스워드 사용 (20자 이상)
   - 프로덕션에서 SSL 연결 활성화

3. **API Keys**:
   - 환경 변수로만 관리
   - 정기 로테이션 (분기별 권장)

4. **Flower Dashboard**:
   - `FLOWER_USER`, `FLOWER_PASSWORD` 강력한 값 설정
   - 외부 접근 차단 (nginx proxy 또는 방화벽)

5. **네트워크**:
   - HTTPS 필수
   - nginx 포트(80/443)만 외부 노출

6. **CORS**: `FASTAPI_ALLOWED_ORIGINS`에 실제 도메인만 설정 (와일드카드 금지)

### SSL/TLS Configuration

Configure SSL in nginx (example with Let's Encrypt):

```nginx
# nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location /api/ {
        proxy_pass http://backend:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://backend:8001;
    }

    location /admin/ {
        proxy_pass http://admin-frontend:80/;
    }
}
```

## Monitoring

### Service Health Checks

```bash
# Check all services
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Check specific service
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs celery-worker
docker compose -f docker-compose.prod.yml logs postgres

# Check Celery worker status
docker compose -f docker-compose.prod.yml exec celery-worker celery -A backend.celery_app inspect active
```

### Application Health

```bash
# FastAPI health endpoint
curl http://localhost/health

# API endpoints
curl http://localhost/api/topics/

# Check database connection
docker compose -f docker-compose.prod.yml exec backend python -c "from backend.models.base import SessionLocal; db = SessionLocal(); print('DB OK')"
```

### Performance Metrics

Monitor these key metrics:
- **Response time**: API endpoints < 3 seconds
- **Memory usage**: Backend container < 2GB
- **Disk usage**: Monitor postgres_data volume growth
- **Database connections**: PostgreSQL connection pool usage
- **Vector search**: Qdrant query latency

## Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check Docker status
docker system info

# Validate compose file
docker compose -f docker-compose.prod.yml config

# Check logs
docker compose -f docker-compose.prod.yml logs
```

#### 2. JWT Authentication Errors

```bash
# Verify JWT_SECRET_KEY is set
docker compose -f docker-compose.prod.yml exec backend env | grep JWT

# Test login endpoint
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your-password"
```

#### 3. Database Connection Errors

```bash
# Check PostgreSQL status
docker compose -f docker-compose.prod.yml exec postgres pg_isready

# Test connection
docker compose -f docker-compose.prod.yml exec postgres psql -U postgres -d scholaria -c "SELECT 1;"
```

#### 4. CORS Errors

```bash
# Check CORS configuration
docker compose -f docker-compose.prod.yml exec backend env | grep CORS

# Update FASTAPI_ALLOWED_ORIGINS in .env.prod
```

#### 5. OpenAI API Issues

```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check rate limits in logs
docker compose -f docker-compose.prod.yml logs backend | grep "rate limit"
```

### Recovery Procedures

```bash
# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# Rebuild and restart
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Restore database from backup
docker compose -f docker-compose.prod.yml exec -i postgres psql -U postgres scholaria < backup.sql
```

## Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review logs for errors
   - Check disk space usage
   - Monitor API performance

2. **Monthly**:
   - Update system packages
   - Review security logs
   - Backup database

3. **Quarterly**:
   - Update Docker images
   - Rotate JWT secret keys
   - Performance optimization review

### Updates and Upgrades

```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Apply updates
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Local Development

### Option 1: Docker Development Environment (권장)

전체 스택을 Docker로 실행 (hot reload 지원):

```bash
# 개발 환경 실행
docker compose up -d

# 로그 확인
docker compose logs -f backend

# 마이그레이션
docker compose exec backend alembic upgrade head
```

Access:
- Backend: http://localhost:8001
- Frontend: http://localhost:5173
- Flower: http://localhost:5555

### Option 2: 로컬 실행 (빠른 iteration)

인프라만 Docker, 앱은 로컬 실행:

```bash
# 인프라만 실행
docker compose up -d postgres redis qdrant

# Backend 로컬 실행
(cd backend && uv run uvicorn backend.main:app --reload --port 8001)

# Celery worker 로컬 실행
(cd backend && uv run celery -A backend.celery_app worker --loglevel=info)
```

## 추가 참조

**운영 관련:**
- [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md) - 백업 스크립트 & 재해 복구
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - 관리 패널 운영 가이드

**개발 관련:**
- [README.md](../README.md) - 개발 환경 설정
- [TESTING_STRATEGY.md](TESTING_STRATEGY.md) - 테스트 전략
- [CONTRIBUTING.md](CONTRIBUTING.md) - 개발 워크플로우

**기술 배경:**
- [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) - FastAPI 선택 이유 등
