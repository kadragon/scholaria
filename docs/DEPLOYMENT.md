# Deployment Guide

This guide provides comprehensive instructions for deploying the **Scholaria RAG System** (FastAPI) in production environments.

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
uv sync
```

### 2. Environment Configuration

Create a `.env` file from the production example:

```bash
# Copy the production environment template
cp .env.prod.example .env.prod

# Edit with your production values
nano .env.prod
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
```

## Production Setup

### Docker Compose Services

The `docker-compose.prod.yml` provides a complete production setup:

**Core Services**:
- **backend**: FastAPI application (uvicorn)
- **celery-worker**: Background task processing for async operations (embeddings, ingestion)
- **admin-frontend**: Refine Admin Panel (nginx-served static files)
- **nginx**: Reverse proxy & load balancer
- **PostgreSQL 16**: Primary database
- **Redis 7**: Cache and Celery broker
- **Qdrant**: Vector database for embeddings

**Volumes**:
- `postgres_data`: Database persistence
- `redis_data`: Cache persistence
- `qdrant_data`: Vector database storage

### Architecture

```
Internet → Nginx (80/443) → FastAPI Backend (8001)
                         → Admin Frontend (static files)

FastAPI → PostgreSQL (5432)
       → Redis (6379) ← Celery Worker (async tasks)
       → Qdrant (6333)
       → OpenAI API

Celery Worker → PostgreSQL (5432)
             → Qdrant (6333)
             → OpenAI API (embeddings)
```

## Environment Variables

### Required Variables (JWT & Auth)

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
# Database
DATABASE_URL=postgresql://postgres:secure-password@postgres:5432/scholaria
DB_ENGINE=postgresql
DB_NAME=scholaria
DB_USER=postgres
DB_PASSWORD=your-secure-database-password
DB_HOST=postgres
DB_PORT=5432
```

### OpenAI Configuration

```bash
# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_DIM=3072
OPENAI_CHAT_TEMPERATURE=0.3
OPENAI_CHAT_MAX_TOKENS=1000
```

### Service URLs

```bash
# Redis
REDIS_URL=redis://redis:6379/0

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=context_items
```

### CORS Configuration (Production)

```bash
# Frontend domains that can access the API
FASTAPI_ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

### Optional Performance Tuning

```bash
# RAG Search Parameters
RAG_SEARCH_LIMIT=15
RAG_RERANK_TOP_K=7

# File Upload
FILE_VALIDATION_MAX_SIZE=10485760  # 10MB
```

### Example Production .env File

```bash
# Production Configuration
DEBUG=False

# JWT (REQUIRED)
JWT_SECRET_KEY=your-generated-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24

# Database
DATABASE_URL=postgresql://postgres:secure-db-password@postgres:5432/scholaria
DB_PASSWORD=secure-db-password

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_DIM=3072

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION_NAME=context_items

# CORS (add your production domains)
FASTAPI_ALLOWED_ORIGINS=https://yourdomain.com

# Performance
RAG_SEARCH_LIMIT=15
RAG_RERANK_TOP_K=7
```

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

### Database Backup

```bash
# Automated backup script (included)
./scripts/backup.sh

# Manual backup
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres scholaria > backup_$(date +%Y%m%d).sql

# Restore from backup
docker compose -f docker-compose.prod.yml exec -i postgres psql -U postgres scholaria < backup.sql
```

## Security

### Essential Security Measures

1. **JWT Secret Key**: Generate and store securely
   ```bash
   # Never use default values in production!
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Database Security**:
   - Use strong passwords (minimum 20 characters)
   - Restrict database access to application only
   - Enable SSL connections in production

3. **API Keys**:
   - Store OpenAI API keys in environment variables only
   - Never commit secrets to version control
   - Rotate keys regularly (quarterly recommended)

4. **Network Security**:
   - Use HTTPS for all external traffic
   - Configure firewall to restrict internal service access
   - Only expose nginx port (80/443) externally

5. **CORS Configuration**:
   - Set `FASTAPI_ALLOWED_ORIGINS` to your specific domains
   - Never use `*` (allow all) in production

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

## Local Development with Docker

For local testing with production-like environment:

```bash
# Use development compose file
docker compose -f docker-compose.dev.yml up -d

# Apply migrations
docker compose -f docker-compose.dev.yml exec backend alembic upgrade head

# View logs
docker compose -f docker-compose.dev.yml logs -f backend
```

## Support

For support or additional help, refer to:
- [README.md](../README.md) - Quick start guide
- [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) - Technical decisions
- [TESTING_STRATEGY.md](TESTING_STRATEGY.md) - Testing approach
- Project issue tracker
