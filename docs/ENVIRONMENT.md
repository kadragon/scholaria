# Environment Configuration Guide

This guide covers environment variable configuration for the Scholaria RAG system.

## Quick Setup

### 1. Copy Environment Template
```bash
# For development
cp .env.example .env

# For production
cp .env.prod.example .env.prod
```

### 2. Update Required Variables
Edit your `.env` file and update these critical variables:

```bash
# Generate a new secret key
python -c 'import secrets; print(secrets.token_urlsafe(50))'

# Get OpenAI API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_actual_api_key_here

# Set secure database password
DB_PASSWORD=your_secure_password_here
```

### 3. Validate Configuration
```bash
# Run diagnostics
uv run ruff check .
uv run mypy .
uv run pytest backend/tests -q
```

## Environment Variables Reference

### 🔒 Security Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | Development key | Application secret used for cryptographic signing |
| `DEBUG` | No | `True` | Enable/disable debug mode |
| `ALLOWED_HOSTS` | Production | `[]` | Comma-separated list of allowed hosts |

### 🔐 Authentication (JWT)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | Yes | Development key | JWT signing key - generate with `python -c 'import secrets; print(secrets.token_urlsafe(32))'` |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_HOURS` | No | `24` | JWT token expiration time in hours |

### 🤖 AI Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | None | OpenAI API key for embeddings and chat |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-large` | Embedding model name |
| `OPENAI_EMBEDDING_DIM` | No | `3072` | Embedding dimensions |
| `OPENAI_CHAT_MODEL` | No | `gpt-4o-mini` | Chat completion model |
| `OPENAI_CHAT_TEMPERATURE` | No | `0.3` | Chat model temperature |
| `OPENAI_CHAT_MAX_TOKENS` | No | `1000` | Max tokens for chat responses |

### 🗄️ Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_ENGINE` | No | `postgresql` | Database engine |
| `DB_NAME` | No | `scholaria` | Database name |
| `DB_USER` | No | `postgres` | Database username |
| `DB_PASSWORD` | Production | `postgres` | Database password |
| `DB_HOST` | No | `localhost` | Database host |
| `DB_PORT` | No | `5432` | Database port |

### 🔍 Vector Database (Qdrant)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QDRANT_HOST` | No | `localhost` | Qdrant server host |
| `QDRANT_PORT` | No | `6333` | Qdrant server port |
| `QDRANT_COLLECTION_NAME` | No | `scholaria_documents` | Collection name for documents |

### 📦 Object Storage (MinIO)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MINIO_ENDPOINT` | No | `localhost:9000` | MinIO server endpoint |
| `MINIO_ACCESS_KEY` | No | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | No | `minioadmin` | MinIO secret key |
| `MINIO_BUCKET_NAME` | No | `scholaria-docs` | Storage bucket name |
| `MINIO_SECURE` | No | `False` | Use HTTPS for MinIO |

### 🚀 Performance & Caching

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL |
| `LLAMAINDEX_CACHE_ENABLED` | No | `false` | Enable embedding cache |
| `LLAMAINDEX_CACHE_DIR` | No | `storage/llamaindex_cache` | Cache directory |
| `LLAMAINDEX_CACHE_NAMESPACE` | No | `scholaria-default` | Cache namespace |
| `RAG_SEARCH_LIMIT` | No | `10` | Max search results |
| `RAG_RERANK_TOP_K` | No | `5` | Top results after reranking |

### 🌍 Localization

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TIME_ZONE` | No | `Asia/Seoul` | Server timezone |
| `LANGUAGE_CODE` | No | `ko-kr` | Default language code |

### 📁 File Processing

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FILE_VALIDATION_MAX_SIZE` | No | `10485760` | Max file size in bytes (10MB) |

## Environment-Specific Configurations

### Development Environment
```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_HOST=localhost
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
MINIO_ENDPOINT=localhost:9000
```

### Docker Compose Environment
```bash
DEBUG=False
DB_HOST=postgres
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
MINIO_ENDPOINT=minio:9000
```

### Production Environment
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key
OPENAI_API_KEY=your-production-api-key
DB_PASSWORD=your-secure-db-password
MINIO_ACCESS_KEY=your-production-minio-key
MINIO_SECRET_KEY=your-production-minio-secret
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

## Security Best Practices

### 🔐 Secrets Management
- Never commit `.env` files to version control
- Use strong, unique passwords for all services
- Rotate API keys regularly
- Use environment-specific API keys

### 🛡️ Production Security
- Set `DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS with proper SSL settings
- Enable security headers
- Use secure database connections

### 📋 Environment Validation
```bash
# Validate configuration before deployment
uv run ruff check .
uv run mypy .
uv run pytest backend/tests -q
```

## Troubleshooting

### Common Issues

**Missing OpenAI API Key**
```
Error: OPENAI_API_KEY environment variable is required
```
Solution: Set your OpenAI API key in the `.env` file.

**Database Connection Failed**
```
Error: Database connection failed
```
Solution: Check database credentials and ensure PostgreSQL is running.

**Redis Connection Failed**
```
Error: Redis connection failed
```
Solution: Ensure Redis server is running on the configured URL.

### Environment Validation Command
```bash
# Combined validation (lint + type + tests)
uv run ruff check . && uv run mypy . && uv run pytest backend/tests -q
```

This command will check:
- ✅ Required environment variables
- ⚠️ Security settings
- 🔌 Service connectivity
- 📋 Configuration summary

## File Structure

```
scholaria/
├── .env                    # Your local environment (not in git)
├── .env.example           # Development template
├── .env.prod.example      # Production template
└── docs/
    └── ENVIRONMENT.md     # This documentation
```
