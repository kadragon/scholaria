# Deployment Guide

This guide provides comprehensive instructions for deploying the **Scholaria RAG System** in production environments.

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

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your production values
nano .env
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run database migrations
uv run python manage.py migrate

# Create admin user
uv run python manage.py createsuperuser

# Load initial data (optional)
uv run python manage.py loaddata fixtures/initial_topics.json
```

### 5. Verify Deployment

```bash
# Check service health
curl http://localhost:8000/api/topics/

# Access admin interface
open http://localhost:8000/admin/

# View API documentation
open http://localhost:8000/api/docs/
```

## Production Setup

Review infrastructure prerequisites, configure secrets, and plan monitoring before promoting Scholaria to production.

## Docker Compose

The included `docker-compose.yml` provides a complete production setup:

### Services
- **PostgreSQL 16**: Primary database
- **Redis 7**: Cache and Celery broker
- **Qdrant**: Vector database for embeddings
- **MinIO**: S3-compatible object storage
- **Unstructured API**: Document processing service

### Volumes
- `postgres_data`: Database persistence
- `redis_data`: Cache persistence
- `qdrant_data`: Vector database storage
- `minio_data`: File storage

## Production Considerations

1. **Reverse Proxy**: Use **Nginx** or **Apache** as a reverse proxy
2. **SSL/TLS**: Configure HTTPS with Let's Encrypt or commercial certificates
3. **Domain**: Set up proper domain and DNS configuration
4. **Firewall**: Restrict access to internal services (Redis, PostgreSQL, etc.)
5. **Backups**: Implement regular database and file storage backups

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-long-random-secret-key` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings/chat | `sk-...` |
| `DB_PASSWORD` | PostgreSQL password | `secure-password` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `secure-secret` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `scholaria` |
| `DB_USER` | Database user | `postgres` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_URL` | Complete Redis URL | `redis://localhost:6379/0` |
| `QDRANT_HOST` | Qdrant host | `localhost` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `QDRANT_COLLECTION_NAME` | Vector collection name | `scholaria_documents` |
| `MINIO_ENDPOINT` | MinIO endpoint | `localhost:9000` |
| `MINIO_BUCKET_NAME` | Storage bucket name | `scholaria-docs` |
| `MINIO_SECURE` | Use HTTPS for MinIO | `False` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-large` |
| `OPENAI_CHAT_MODEL` | Chat model | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_DIM` | Embedding dimensions | `3072` |
| `OPENAI_CHAT_TEMPERATURE` | Chat temperature | `0.3` |
| `OPENAI_CHAT_MAX_TOKENS` | Max response tokens | `1000` |
| `LLAMAINDEX_CACHE_ENABLED` | Enable embedding cache | `true` |
| `LLAMAINDEX_CACHE_DIR` | Cache directory | `storage/llamaindex_cache` |
| `RAG_SEARCH_LIMIT` | Search result limit | `10` |
| `RAG_RERANK_TOP_K` | Reranking top-k | `5` |
| `FILE_VALIDATION_MAX_SIZE` | Max file size (bytes) | `10485760` |

Docling-powered PDF parsing runs entirely in-process, so no external service or
environment variables are required for document conversion.

### Example .env File

```bash
# Production Configuration
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here

# Database
DB_PASSWORD=your-secure-database-password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4o-mini

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key
MINIO_SECURE=False

# Performance
LLAMAINDEX_CACHE_ENABLED=true
RAG_SEARCH_LIMIT=15
RAG_RERANK_TOP_K=7
```

## Database Setup

### Initial Migration

```bash
# Create and apply migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Create superuser for admin access
uv run python manage.py createsuperuser
```

### Database Backup

```bash
# Backup database
docker exec scholaria_postgres_1 pg_dump -U postgres scholaria > backup.sql

# Restore database
docker exec -i scholaria_postgres_1 psql -U postgres scholaria < backup.sql
```

### Collection Reset (Development)

```bash
# Reset Qdrant collection (if needed)
./scripts/qdrant-reset.sh
```

## Security

### Essential Security Measures

1. **SECRET_KEY**: Generate a strong, unique Django secret key
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Database Security**:
   - Use strong passwords for database accounts
   - Restrict database access to application hosts only
   - Enable SSL connections in production

3. **API Keys**:
   - Store OpenAI API keys securely
   - Use environment variables, never commit to code
   - Rotate keys regularly

4. **Network Security**:
   - Use HTTPS for all external traffic
   - Implement proper firewall rules
   - Restrict internal service access

5. **File Upload Security**:
   - File validation enabled by default
   - Maximum file size limits enforced
   - Malicious file detection active

### SSL/TLS Configuration

For production, configure SSL/TLS termination:

```nginx
# Nginx configuration example
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Service Health Checks

```bash
# Check all services
docker-compose ps

# View service logs
docker-compose logs -f

# Check specific service
docker-compose logs postgres
docker-compose logs redis
docker-compose logs qdrant
docker-compose logs minio
```

### Application Health

```bash
# Check API health
curl http://localhost:8000/api/topics/

# Check admin interface
curl http://localhost:8000/admin/login/

# Check database connection
uv run python manage.py dbshell --command "SELECT 1;"
```

### Log Monitoring

Important log locations:
- **Django logs**: Application stdout/stderr
- **PostgreSQL logs**: Container logs
- **Redis logs**: Container logs
- **Qdrant logs**: Container logs

### Performance Monitoring

Monitor these metrics:
- **Response time**: API endpoints < 3 seconds
- **Memory usage**: Keep under 80% of available RAM
- **Disk usage**: Monitor volume growth
- **Database connections**: Monitor connection pool usage

## Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check Docker status
docker system info

# Check compose file syntax
docker-compose config

# Check logs for errors
docker-compose logs
```

#### 2. Database Connection Errors

```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Test connection
docker-compose exec postgres psql -U postgres -d scholaria -c "SELECT 1;"

# Check environment variables
echo $DB_HOST $DB_PORT $DB_USER
```

#### 3. OpenAI API Issues

```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check rate limits in logs
docker-compose logs | grep "rate limit"
```

#### 4. Qdrant Connection Issues

```bash
# Check Qdrant status
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections
```

#### 5. MinIO Access Issues

```bash
# Check MinIO health
curl http://localhost:9000/minio/health/ready

# Access MinIO console
open http://localhost:9001
```

### Recovery Procedures

#### Service Recovery

```bash
# Restart specific service
docker-compose restart postgres

# Restart all services
docker-compose restart

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

#### Data Recovery

```bash
# Restore database from backup
docker-compose exec -i postgres psql -U postgres scholaria < backup.sql

# Reset Qdrant collection
./scripts/qdrant-reset.sh
uv run python manage.py shell -c "from rag.retrieval.qdrant import QdrantService; QdrantService().reset_collection()"
```

### Performance Optimization

#### Database Optimization

```bash
# Analyze database performance
uv run python manage.py dbshell -c "ANALYZE;"

# Check slow queries
docker-compose logs postgres | grep "slow query"
```

#### Cache Optimization

```bash
# Monitor Redis memory usage
docker-compose exec redis redis-cli info memory

# Clear cache if needed
docker-compose exec redis redis-cli flushall
```

## Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review logs for errors
   - Check disk space usage
   - Monitor API performance

2. **Monthly**:
   - Update system packages
   - Rotate log files
   - Review security settings

3. **Quarterly**:
   - Update Docker images
   - Review and rotate API keys
   - Performance optimization review

### Updates and Upgrades

```bash
# Update Docker images
docker-compose pull

# Restart with new images
docker-compose down
docker-compose up -d

# Run migrations after updates
uv run python manage.py migrate
```

### Backup Strategy

Implement regular backups:

```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker exec scholaria_postgres_1 pg_dump -U postgres scholaria > "backups/db_$DATE.sql"

# MinIO data backup
docker run --rm -v minio_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/minio_$DATE.tar.gz /data

# Qdrant data backup
docker run --rm -v qdrant_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/qdrant_$DATE.tar.gz /data
```

For support or additional help, refer to the project documentation or open an issue in the repository.
