#!/bin/bash

# Docker Compose Integration Testing Script
# This script starts all Docker services and runs integration tests

set -e  # Exit on any error

echo "🐳 Starting Docker Compose Integration Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if docker-compose is available
if docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
else
    print_error "Neither 'docker compose' nor 'docker-compose' is available in PATH."
    exit 1
fi

print_status "Stopping any existing containers..."
"${COMPOSE_CMD[@]}" down -v 2>/dev/null || true

print_status "Starting Docker Compose services..."
"${COMPOSE_CMD[@]}" up -d

# Function to wait for services to be ready
wait_for_services() {
    local max_attempts=30
    local delay=2
    local required_services=("postgres" "redis" "qdrant")
    local optional_services=("frontend" "flower" "celery-worker")

    print_status "Waiting for required services to be ready..."

    # Wait for required services
    for service in "${required_services[@]}"; do
        print_status "Waiting for $service..."
        local attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if "${COMPOSE_CMD[@]}" ps "$service" | grep -q "Up" && check_service_health "$service"; then
                print_success "$service is ready"
                break
            fi

            attempt=$((attempt + 1))
            if [ $attempt -eq $max_attempts ]; then
                print_error "$service failed to become ready after $((max_attempts * delay)) seconds"
                "${COMPOSE_CMD[@]}" logs "$service"
                exit 1
            fi
            sleep $delay
        done
    done

    # Check optional services (don't fail if they're not available)
    for service in "${optional_services[@]}"; do
        if "${COMPOSE_CMD[@]}" ps "$service" | grep -q "Up" && check_service_health "$service"; then
            print_success "$service is ready"
        else
            print_warning "$service is not available (optional)"
        fi
    done
}

# Function to check specific service health
check_service_health() {
    local service=$1
    case $service in
        "postgres")
            "${COMPOSE_CMD[@]}" exec -T postgres pg_isready -h localhost > /dev/null 2>&1
            ;;
        "redis")
            "${COMPOSE_CMD[@]}" exec -T redis redis-cli ping > /dev/null 2>&1
            ;;
        "qdrant")
            curl -s http://localhost:6333/health > /dev/null 2>&1
            ;;
        *)
            return 0  # Unknown service, assume healthy if running
            ;;
    esac
}

wait_for_services

# Final check of all services
print_status "Final service health check..."

services=("postgres" "redis" "qdrant" "frontend" "flower" "celery-worker")
all_healthy=true

for service in "${services[@]}"; do
    if "${COMPOSE_CMD[@]}" ps "$service" | grep -q "Up"; then
        print_success "$service is running"
    else
        print_error "$service is not running"
        all_healthy=false
    fi
done

if [ "$all_healthy" = false ]; then
    print_error "Some services are not running. Check ${COMPOSE_CMD[*]} logs for details."
    "${COMPOSE_CMD[@]}" logs
    exit 1
fi

print_status "Running database migrations..."
export DOCKER_INTEGRATION_TESTS=true
(cd backend && uv run alembic -c ../alembic.ini upgrade head)

print_status "Running Docker integration tests..."

# Run the integration tests with detailed output
if (cd backend && uv run pytest tests/test_rag_endpoint.py tests/test_rag_streaming.py -v --tb=short); then
    print_success "All integration tests passed! ✅"
    test_result=0
else
    print_error "Some integration tests failed! ❌"
    test_result=1
fi

print_status "Test run completed. Keeping services running for manual testing..."
print_warning "Services are still running. You can:"
print_warning "  - Access Qdrant Dashboard: http://localhost:6333/dashboard"
print_warning "  - Access Flower: http://localhost:5555"
print_warning "  - Access Frontend (Refine): http://localhost:5173"
print_warning "  - Stop services: ${COMPOSE_CMD[*]} down"

exit $test_result
