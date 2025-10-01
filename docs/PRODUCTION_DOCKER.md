# Production Docker Deployment Guide

This guide covers the production deployment of Scholaria using Docker Compose with optimized configurations for security, performance, and reliability.

## Architecture Overview

The production deployment consists of:

- **Backend Application**: FastAPI application served via Uvicorn workers
- **Celery Worker**: Background task processing for document ingestion
- **Celery Beat**: Scheduled task management
- **PostgreSQL**: Primary database with optimized settings
- **Redis**: Cache and message broker with persistence
- **Qdrant**: Vector database for semantic search
- **MinIO**: S3-compatible object storage
- **Nginx**: Reverse proxy with SSL support (optional)

## Quick Start

### 1. Environment Setup

```bash
# Copy production environment template
cp .env.prod.example .env.prod

# Edit with your production values
nano .env.prod
```

### 2. Deploy

```bash
# Make deploy script executable
chmod +x scripts/deploy.sh

# Run production deployment
./scripts/deploy.sh deploy
```

### 3. Access Application

- **Web Interface**: http://your-domain:8000
- **Admin Interface**: http://your-domain:8000/admin
- **API Documentation**: http://your-domain:8000/api/docs/
- **Health Check**: http://your-domain:8000/health/

## Production Configuration Files

### Core Files

- `docker-compose.prod.yml` - Production service definitions
- `Dockerfile.prod` - Multi-stage production build
- `.env.prod` - Production environment variables
- `backend/config.py` - FastAPI settings module (env-driven)
- `nginx/nginx.conf` - Nginx reverse proxy configuration

### Support Scripts

- `scripts/deploy.sh` - Deployment automation
- `scripts/postgres-init.sql` - Database initialization

## Environment Variables

### Required Variables

```bash
SECRET_KEY=your-application-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
POSTGRES_DB=scholaria_prod
POSTGRES_USER=scholaria_user
POSTGRES_PASSWORD=your-secure-password
OPENAI_API_KEY=your-openai-api-key
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key
```

### Optional Security Variables

```bash
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
USE_X_FORWARDED_HOST=True
USE_X_FORWARDED_PORT=True
```

## Service Configuration

### Web Application

- **Runtime**: Python 3.13 with Gunicorn WSGI server
- **Workers**: 4 sync workers with auto-restart
- **Resources**: 2GB memory limit, 1 CPU limit
- **Health Check**: HTTP health endpoint monitoring
- **Security**: Non-root user, read-only filesystem

### Database (PostgreSQL)

- **Version**: PostgreSQL 16 with Alpine Linux
- **Authentication**: SCRAM-SHA-256 for enhanced security
- **Resources**: 2GB memory limit, connection pooling
- **Persistence**: Named volume with backup support
- **Health Check**: Connection validation

### Cache & Message Broker (Redis)

- **Version**: Redis 7 with Alpine Linux
- **Persistence**: AOF enabled for durability
- **Memory**: 1GB limit with LRU eviction
- **Health Check**: PING command monitoring

### Vector Database (Qdrant)

- **Version**: Qdrant v1.7.4 with stability optimizations
- **Resources**: 4GB memory, 2 CPU for search performance
- **Persistence**: Named volume for vector collections
- **Health Check**: HTTP API health endpoint

### Object Storage (MinIO)

- **Version**: MinIO with fixed release tag
- **Resources**: 1GB memory limit
- **Persistence**: Named volume for file storage
- **Security**: Custom access keys, console access control

## Security Features

### Application Security

- **Secret Management**: Environment-based secret injection
- **User Permissions**: Non-root container execution
- **Input Validation**: File type and size restrictions
- **Rate Limiting**: API endpoint throttling
- **CORS & Security**: FastAPI CORS middleware configured via `FASTAPI_ALLOWED_ORIGINS`

### Network Security

- **Isolated Network**: Custom bridge network for services
- **Internal Communication**: Service-to-service communication
- **Nginx Security Headers**: XSS, Content-Type, Frame-Options
- **SSL/TLS Support**: HTTPS configuration ready

### Data Security

- **Database Encryption**: SCRAM-SHA-256 authentication
- **Password Hashing**: JWT secrets and hashing handled via `backend/auth/utils.py`
- **Session Security**: Secure cookie settings
- **Audit Logging**: Comprehensive application logging

## Performance Optimizations

### Application Layer

- **Static File Serving**: Nginx static file handling
- **Cache Middleware**: Full-page caching for anonymous users
- **Database Connections**: Connection pooling and reuse
- **Task Queue**: Async processing for heavy operations

### Database Optimizations

- **Connection Pooling**: Optimized connection limits
- **Query Optimization**: Indexed fields and efficient queries
- **Memory Configuration**: Tuned PostgreSQL settings
- **Backup Strategy**: Automated backup scripts

### Caching Strategy

- **Application Cache**: Redis for session and view caching
- **Static Assets**: Long-term browser caching
- **API Responses**: Conditional caching for read operations
- **Vector Search**: Qdrant internal optimizations

## Monitoring & Health Checks

### Health Check Endpoints

- **Application**: `/health/` - Database and cache connectivity
- **Services**: Docker health check for all services
- **Nginx**: Service availability monitoring
- **Database**: PostgreSQL connection validation

### Logging Configuration

- **Application Logs**: Structured JSON logging to files
- **Error Tracking**: Email notifications for critical errors
- **Access Logs**: Nginx request logging
- **Rotation**: Automatic log rotation and cleanup

### Resource Monitoring

- **Memory Limits**: Enforced container memory limits
- **CPU Limits**: Controlled CPU resource allocation
- **Disk Usage**: Volume usage monitoring
- **Network Traffic**: Service communication tracking

## Backup & Recovery

### Database Backup

```bash
# Create database backup
./scripts/deploy.sh backup

# Restore from backup
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB < backup_file.sql
```

### File Storage Backup

```bash
# Backup MinIO data
docker-compose -f docker-compose.prod.yml exec minio mc mirror /data /backup/minio

# Backup uploaded files
docker cp $(docker-compose -f docker-compose.prod.yml ps -q web):/app/uploads ./backup/uploads
```

### Configuration Backup

```bash
# Backup environment and configuration
cp .env.prod backup/
cp -r nginx/ backup/
cp docker-compose.prod.yml backup/
```

## Deployment Commands

### Initial Deployment

```bash
./scripts/deploy.sh deploy
```

### Update Deployment

```bash
./scripts/deploy.sh update
```

### Service Management

```bash
# Check service health
./scripts/deploy.sh health

# View logs
./scripts/deploy.sh logs

# Manual service restart
docker-compose -f docker-compose.prod.yml restart web celery-worker
```

## SSL/HTTPS Configuration

### Nginx with SSL

1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `nginx/ssl/` directory
3. Uncomment HTTPS server block in `nginx/nginx.conf`
4. Update environment variables:

```bash
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

### Load Balancer SSL

For cloud deployments behind load balancer:

```bash
USE_X_FORWARDED_HOST=True
USE_X_FORWARDED_PORT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

## Scaling Considerations

### Horizontal Scaling

- **Celery Workers**: Scale worker containers based on load
- **Database**: Read replicas for read-heavy workloads
- **Load Balancing**: Multiple web containers behind load balancer
- **Storage**: Distributed MinIO setup for high availability

### Vertical Scaling

- **Memory**: Increase container memory limits
- **CPU**: Adjust CPU limits and worker counts
- **Storage**: Expand volume sizes for data growth
- **Network**: Optimize network configuration

## Troubleshooting

### Common Issues

1. **Service Not Starting**: Check environment variables and logs
2. **Database Connection**: Verify PostgreSQL health and credentials
3. **File Uploads**: Check MinIO configuration and permissions
4. **Search Issues**: Validate Qdrant service and collection setup

### Debug Commands

```bash
# Check service logs
docker-compose -f docker-compose.prod.yml logs service-name

# Access service shell
docker-compose -f docker-compose.prod.yml exec service-name sh

# Check service status
docker-compose -f docker-compose.prod.yml ps

# Monitor resource usage
docker stats
```

### Performance Debugging

```bash
# Database performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM pg_stat_activity;"

# Redis performance
docker-compose -f docker-compose.prod.yml exec redis redis-cli info stats

# Application performance
curl -f http://localhost:8000/health/
```

## Security Best Practices

1. **Change Default Passwords**: Update all default credentials
2. **Restrict Network Access**: Use firewall rules for production
3. **Regular Updates**: Keep container images updated
4. **Monitor Logs**: Set up log monitoring and alerting
5. **Backup Regularly**: Implement automated backup procedures
6. **SSL Certificates**: Use valid SSL certificates for HTTPS
7. **Environment Isolation**: Separate development and production environments
