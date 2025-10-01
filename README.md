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

3. **Start services:**
   ```bash
   docker-compose up -d
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
   # FastAPI backend
   uv run uvicorn backend.main:app --reload --port 8001

   # Or using Docker
   docker compose -f docker-compose.dev.yml up
   ```

   Access:
   - API Docs: http://localhost:8001/docs
   - Admin Panel: http://localhost:8001/admin
   - Health Check: http://localhost:8001/health

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

### Development
```bash
docker compose -f docker-compose.dev.yml up
```

### Production
```bash
# Copy and configure environment
cp .env.prod.example .env.prod

# Start services
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

Access:
- API: http://localhost/api
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

- [Architecture Decisions](docs/ARCHITECTURE_DECISIONS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Strategy](docs/TESTING_STRATEGY.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)
- [User Guide](docs/USER_GUIDE.md)
- [Admin Guide](docs/ADMIN_GUIDE.md)

## 🔧 Environment Variables

Key configuration (see `.env.example` for full list):

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/scholaria

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=context_items

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# CORS (production)
FASTAPI_ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## 📄 License

This project is proprietary and confidential.
