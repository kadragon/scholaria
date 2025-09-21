#!/bin/bash
# Production deployment script for Scholaria RAG System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    if [ ! -f ".env.prod" ]; then
        log_error ".env.prod file not found. Copy .env.prod.example and configure it."
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Build and start services
deploy() {
    log_info "Starting production deployment..."

    # Load environment variables
    export $(cat .env.prod | grep -v '^#' | xargs)

    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose -f docker-compose.prod.yml pull

    # Build application image
    log_info "Building application image..."
    docker-compose -f docker-compose.prod.yml build --no-cache web

    # Start infrastructure services first
    log_info "Starting infrastructure services..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis qdrant minio

    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30

    # Run database migrations
    log_info "Running database migrations..."
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate --noinput

    # Collect static files
    log_info "Collecting static files..."
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput

    # Create superuser if it doesn't exist
    log_info "Ensuring superuser exists..."
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@scholaria.local', 'changeme123')
    print('Superuser created: admin / changeme123')
else:
    print('Superuser already exists')
"

    # Start all services
    log_info "Starting all services..."
    docker-compose -f docker-compose.prod.yml up -d

    # Check service health
    log_info "Checking service health..."
    sleep 10
    docker-compose -f docker-compose.prod.yml ps

    log_info "Deployment completed successfully!"
    log_warn "Remember to:"
    log_warn "1. Change the default superuser password"
    log_warn "2. Configure SSL certificates for production"
    log_warn "3. Set up regular database backups"
    log_warn "4. Monitor application logs"
}

# Update deployment
update() {
    log_info "Updating production deployment..."

    # Load environment variables
    export $(cat .env.prod | grep -v '^#' | xargs)

    # Pull latest images
    docker-compose -f docker-compose.prod.yml pull

    # Rebuild application
    docker-compose -f docker-compose.prod.yml build --no-cache web

    # Run migrations
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate --noinput

    # Collect static files
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput

    # Restart services with zero downtime
    docker-compose -f docker-compose.prod.yml up -d --force-recreate web celery-worker celery-beat

    log_info "Update completed successfully!"
}

# Backup database
backup() {
    log_info "Creating database backup..."

    export $(cat .env.prod | grep -v '^#' | xargs)

    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"

    docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > "backups/$BACKUP_FILE"

    log_info "Database backup created: backups/$BACKUP_FILE"
}

# Show logs
logs() {
    log_info "Showing application logs..."
    docker-compose -f docker-compose.prod.yml logs -f web celery-worker
}

# Health check
health() {
    log_info "Checking service health..."

    services=("web" "celery-worker" "postgres" "redis" "qdrant" "minio")

    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
            log_info "$service: ✓ Running"
        else
            log_error "$service: ✗ Not running"
        fi
    done
}

# Main script
case "$1" in
    deploy)
        check_prerequisites
        deploy
        ;;
    update)
        update
        ;;
    backup)
        mkdir -p backups
        backup
        ;;
    logs)
        logs
        ;;
    health)
        health
        ;;
    *)
        echo "Usage: $0 {deploy|update|backup|logs|health}"
        echo ""
        echo "  deploy  - Full production deployment"
        echo "  update  - Update existing deployment"
        echo "  backup  - Create database backup"
        echo "  logs    - Show application logs"
        echo "  health  - Check service health"
        exit 1
        ;;
esac
