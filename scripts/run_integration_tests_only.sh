#!/bin/bash

# Run Docker Integration Tests Only
# Assumes Docker Compose services are already running

set -e

echo "🧪 Running Docker Integration Tests..."

# Check if services are running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ Docker services are not running. Please run: docker-compose up -d"
    exit 1
fi

echo "✅ Docker services detected"

# Set environment variable and run tests
export DOCKER_INTEGRATION_TESTS=true

echo "📋 Running integration tests..."
uv run python -m pytest rag/tests/test_docker_integration.py -v --tb=short

echo "✅ Integration tests completed!"
