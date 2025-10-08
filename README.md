# Scholaria - School Integrated RAG System

✅ **FastAPI 전용 시스템** - TDD-driven Retrieval-Augmented Generation system for schools.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) package manager

### Development Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services (Docker):**
   ```bash
   docker compose up -d
   ```

4. **Run migrations:**
   ```bash
   uv run alembic upgrade head
   ```

5. **Run tests:**
   ```bash
   uv run pytest backend/tests/
   ```

6. **Start development server:**
   ```bash
   # 로컬 개발 (빠른 iteration)
   uv run uvicorn backend.main:app --reload --port 8001

   # 또는 Docker 개발 환경
   docker compose up -d
   ```

   Access:
   - API Docs: http://localhost:8001/docs
   - Admin Panel: http://localhost:5173 (Docker) or http://localhost:8001/admin
   - Health Check: http://localhost:8001/health
   - Flower (Celery): http://localhost:5555

## 🛠️ Development Commands

### Code Quality
```bash
# Lint and format code
uv run ruff check --fix .
uv run ruff format .

# Type checking
uv run mypy .

# Run all checks
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest backend/tests/
```

### Testing
```bash
# All tests
uv run pytest backend/tests/

# With coverage
uv run pytest backend/tests/ --cov=backend --cov-report=html

# Specific test file
uv run pytest backend/tests/test_auth.py -v
```

### Database
```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Pre-commit
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## ✅ Project Status

**FastAPI migration complete | Core functionality verified**

- ✅ FastAPI + SQLAlchemy backend
- ✅ Refine Admin Panel (React + shadcn/ui)
- ✅ Full ingestion pipeline with PDF/Markdown/FAQ support
- ✅ Vector search and RAG API endpoints
- ✅ JWT authentication system
- ✅ Production Docker deployment ready

See [TASKS.md](docs/agents/TASKS.md) for detailed progress tracking.

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy + Alembic
- **Admin UI**: Refine + React 18 + TypeScript + shadcn/ui
- **Database**: PostgreSQL + Qdrant (vector DB)
- **Queue**: Celery + Redis
- **Monitoring**: Flower (Celery dashboard)
- **Parsing**: Docling for PDF processing
- **AI**: OpenAI GPT + Sentence Transformers
- **Auth**: JWT (python-jose + passlib)

### Project Structure
```
scholaria/
├── backend/          # FastAPI application
│   ├── auth/         # Authentication utilities
│   ├── dependencies/ # FastAPI dependencies
│   ├── ingestion/    # Document processing
│   ├── models/       # SQLAlchemy models
│   ├── retrieval/    # RAG & vector search
│   ├── routers/      # API endpoints
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── tests/        # Test suite
├── frontend/         # Refine Admin Panel
├── alembic/          # Database migrations
├── nginx/            # Nginx configuration
├── scripts/          # Deployment & utility scripts
└── docs/             # Documentation
```

## 🔐 Authentication

The system uses JWT-based authentication. Required environment variables:

```bash
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24
```

**Admin user creation:**
```python
# Use backend/models/user.py
from backend.models.user import User
from backend.auth.utils import pwd_context
from backend.models.base import SessionLocal

db = SessionLocal()
admin = User(
    username="admin",
    email="admin@example.com",
    password=pwd_context.hash("your-password"),
    is_active=True,
    is_staff=True,
    is_superuser=True
)
db.add(admin)
db.commit()
```

## 🐳 Docker Deployment

### Development (기본)
```bash
# 개발용 환경 (hot reload, volume mount)
docker compose up -d

# 마이그레이션
docker compose exec backend alembic upgrade head
```

Access:
- Backend API: http://localhost:8001
- Frontend: http://localhost:5173
- Flower: http://localhost:5555

### Production
```bash
# 프로덕션 설정 복사
cp .env.example .env
# .env 파일 수정 (JWT_SECRET_KEY, DB_PASSWORD 등 필수)

# 프로덕션 환경 실행
docker compose -f docker-compose.prod.yml up -d

# 마이그레이션
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

Access:
- API: http://localhost/api (via nginx)
- Admin: http://localhost/admin
- Docs: http://localhost/docs

## 🧪 Testing Strategy

Following strict TDD principles:
1. Write failing tests first (Red)
2. Implement minimal code to pass (Green)
3. Refactor and improve (Refactor)

Test organization:
- `backend/tests/` - FastAPI unit & integration tests
- `backend/tests/admin/` - Admin API tests
- Core tests verified: auth (12/12), admin (31/31)

## 📚 Documentation

### 개발자 가이드
- [Architecture Decisions](docs/ARCHITECTURE_DECISIONS.md) - 주요 기술 결정 (Django→FastAPI 이유 등)
- [Contributing Guidelines](docs/CONTRIBUTING.md) - 개발 워크플로우 & 브랜치 전략
- [Testing Strategy](docs/TESTING_STRATEGY.md) - TDD 원칙 & 테스트 실행 방법

### 운영 가이드
- [Deployment Guide](docs/DEPLOYMENT.md) - **프로덕션 배포 완전 가이드** (환경 설정, DB 초기화, 모니터링)
- [Backup Strategy](docs/BACKUP_STRATEGY.md) - 백업/복원 전략 & 스크립트 사용법

### 사용자 가이드
- [Admin Guide](docs/ADMIN_GUIDE.md) - 관리 패널 사용법 (컨텍스트 업로드, 토픽 관리)
- [User Guide](docs/USER_GUIDE.md) - 학생/엔드유저용 시스템 사용 가이드

> 💡 **빠른 참조**: 프로덕션 배포는 [DEPLOYMENT.md](docs/DEPLOYMENT.md) → 환경 변수는 `.env.prod.example` 참조

## 🔧 Environment Variables

**필수 설정** (상세 설명은 `.env.example` & `.env.prod.example` 참조):

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/scholaria

# OpenAI (필수)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# JWT Authentication (프로덕션 필수)
JWT_SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(32))">
JWT_ALGORITHM=HS256

# Vector DB
QDRANT_URL=http://localhost:6333

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS (프로덕션)
FASTAPI_ALLOWED_ORIGINS=https://yourdomain.com
```

> 🔒 **보안**: `JWT_SECRET_KEY`는 반드시 생성 필요. 프로덕션 환경 설정 상세는 [DEPLOYMENT.md](docs/DEPLOYMENT.md#environment-variables) 참조.

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## 📄 License

This project is proprietary and confidential.
