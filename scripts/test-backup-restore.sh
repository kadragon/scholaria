#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup.sh"
RESTORE_SCRIPT="${SCRIPT_DIR}/restore.sh"
BACKUP_DIR="${BACKUP_DIR:-/tmp/scholaria_backup_test}"
TEST_ENV="${TEST_ENV:-dev}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error_exit() {
    log "ERROR: $1"
    cleanup_test_env
    exit 1
}

cleanup_test_env() {
    log "Cleaning up test environment..."
    if [ "${TEST_ENV}" = "dev" ]; then
        docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v > /dev/null 2>&1 || true
    fi
    rm -rf "${BACKUP_DIR}"
}

setup_test_env() {
    log "Setting up test environment..."

    if [ "${TEST_ENV}" = "dev" ]; then
        docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
        docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres redis qdrant

        log "Waiting for services to be ready..."
        for i in {1..30}; do
            if docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1 && \
               docker compose exec -T redis redis-cli ping > /dev/null 2>&1 && \
               curl -sf http://localhost:6333/health > /dev/null 2>&1; then
                log "All services ready"
                return 0
            fi
            sleep 2
        done
        error_exit "Services failed to start"
    fi
}

seed_test_data() {
    log "Seeding test data..."

    docker compose exec -T postgres psql -U postgres -d scholaria > /dev/null 2>&1 <<'EOF' || error_exit "Failed to seed PostgreSQL data"
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS context_items (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO topics (name, slug, description) VALUES
    ('Test Topic 1', 'test-topic-1', 'Test description 1'),
    ('Test Topic 2', 'test-topic-2', 'Test description 2'),
    ('Test Topic 3', 'test-topic-3', 'Test description 3');

INSERT INTO context_items (topic_id, title, content)
SELECT t.id, 'Context Item ' || i, 'Test content ' || i
FROM topics t, generate_series(1, 10) i;

EOF

    docker compose exec -T redis redis-cli > /dev/null 2>&1 <<'EOF' || error_exit "Failed to seed Redis data"
SET test:key1 "value1"
SET test:key2 "value2"
SET test:key3 "value3"
SADD test:set member1 member2 member3
HSET test:hash field1 "hash_value1" field2 "hash_value2"
EOF

    curl -X PUT "http://localhost:6333/collections/scholaria_documents" \
        -H "Content-Type: application/json" \
        -d '{
            "vectors": {
                "size": 1536,
                "distance": "Cosine"
            }
        }' > /dev/null 2>&1 || error_exit "Failed to create Qdrant collection"

    curl -X PUT "http://localhost:6333/collections/scholaria_documents/points" \
        -H "Content-Type: application/json" \
        -d '{
            "points": [
                {"id": 1, "vector": [0.1, 0.2, 0.3], "payload": {"text": "test doc 1"}},
                {"id": 2, "vector": [0.4, 0.5, 0.6], "payload": {"text": "test doc 2"}},
                {"id": 3, "vector": [0.7, 0.8, 0.9], "payload": {"text": "test doc 3"}}
            ]
        }' > /dev/null 2>&1 || error_exit "Failed to insert Qdrant vectors"

    log "Test data seeded successfully"
}

capture_baseline() {
    log "Capturing baseline metrics..."

    BASELINE_PG_TOPICS=$(docker compose exec -T postgres psql -U postgres -d scholaria -t -c "SELECT COUNT(*) FROM topics;" 2>/dev/null | xargs || echo "0")
    BASELINE_PG_CONTEXTS=$(docker compose exec -T postgres psql -U postgres -d scholaria -t -c "SELECT COUNT(*) FROM context_items;" 2>/dev/null | xargs || echo "0")
    BASELINE_REDIS_KEYS=$(docker compose exec -T redis redis-cli DBSIZE 2>/dev/null | xargs || echo "0")
    BASELINE_QDRANT_VECTORS=$(curl -sf http://localhost:6333/collections/scholaria_documents 2>/dev/null | jq -r '.result.vectors_count // 0')

    log "Baseline: PG Topics=${BASELINE_PG_TOPICS}, PG Contexts=${BASELINE_PG_CONTEXTS}, Redis Keys=${BASELINE_REDIS_KEYS}, Qdrant Vectors=${BASELINE_QDRANT_VECTORS}"
}

run_backup() {
    log "Running backup..."

    export BACKUP_DIR="${BACKUP_DIR}"
    export RETENTION_DAYS=7

    if ! "${BACKUP_SCRIPT}"; then
        error_exit "Backup failed"
    fi

    BACKUP_PATH=$(find "${BACKUP_DIR}" -maxdepth 1 -type d -name "scholaria_backup_*" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

    if [ -z "${BACKUP_PATH}" ]; then
        error_exit "Backup directory not found"
    fi

    log "Backup created: ${BACKUP_PATH}"
    echo "${BACKUP_PATH}"
}

wipe_data() {
    log "Wiping data to simulate disaster..."

    docker compose exec -T postgres psql -U postgres -d scholaria -c "DROP TABLE IF EXISTS context_items, topics CASCADE;" > /dev/null 2>&1 || true
    docker compose exec -T redis redis-cli FLUSHDB > /dev/null 2>&1 || true
    curl -X DELETE "http://localhost:6333/collections/scholaria_documents" > /dev/null 2>&1 || true

    log "Data wiped"
}

run_restore() {
    local backup_path="$1"

    log "Running restore from ${backup_path}..."

    export BACKUP_DIR="${BACKUP_DIR}"

    if ! "${RESTORE_SCRIPT}" --force "${backup_path}"; then
        error_exit "Restore failed"
    fi

    log "Restore completed"
}

verify_integrity() {
    log "Verifying data integrity..."

    sleep 5

    RESTORED_PG_TOPICS=$(docker compose exec -T postgres psql -U postgres -d scholaria -t -c "SELECT COUNT(*) FROM topics;" 2>/dev/null | xargs || echo "0")
    RESTORED_PG_CONTEXTS=$(docker compose exec -T postgres psql -U postgres -d scholaria -t -c "SELECT COUNT(*) FROM context_items;" 2>/dev/null | xargs || echo "0")
    RESTORED_REDIS_KEYS=$(docker compose exec -T redis redis-cli DBSIZE 2>/dev/null | xargs || echo "0")
    RESTORED_QDRANT_VECTORS=$(curl -sf http://localhost:6333/collections/scholaria_documents 2>/dev/null | jq -r '.result.vectors_count // 0')

    log "Restored: PG Topics=${RESTORED_PG_TOPICS}, PG Contexts=${RESTORED_PG_CONTEXTS}, Redis Keys=${RESTORED_REDIS_KEYS}, Qdrant Vectors=${RESTORED_QDRANT_VECTORS}"

    local all_passed=true

    if [ "${RESTORED_PG_TOPICS}" != "${BASELINE_PG_TOPICS}" ]; then
        log "FAIL: PostgreSQL topics count mismatch (expected ${BASELINE_PG_TOPICS}, got ${RESTORED_PG_TOPICS})"
        all_passed=false
    fi

    if [ "${RESTORED_PG_CONTEXTS}" != "${BASELINE_PG_CONTEXTS}" ]; then
        log "FAIL: PostgreSQL context_items count mismatch (expected ${BASELINE_PG_CONTEXTS}, got ${RESTORED_PG_CONTEXTS})"
        all_passed=false
    fi

    if [ "${RESTORED_REDIS_KEYS}" != "${BASELINE_REDIS_KEYS}" ]; then
        log "FAIL: Redis keys count mismatch (expected ${BASELINE_REDIS_KEYS}, got ${RESTORED_REDIS_KEYS})"
        all_passed=false
    fi

    if [ "${RESTORED_QDRANT_VECTORS}" != "${BASELINE_QDRANT_VECTORS}" ]; then
        log "FAIL: Qdrant vectors count mismatch (expected ${BASELINE_QDRANT_VECTORS}, got ${RESTORED_QDRANT_VECTORS})"
        all_passed=false
    fi

    if [ "${all_passed}" = true ]; then
        log "All integrity checks PASSED"
        return 0
    else
        error_exit "Integrity verification FAILED"
    fi
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Test backup and restore functionality with integrity verification.

OPTIONS:
    -h, --help          Show this help message
    --keep-env          Keep test environment after completion
    --backup-dir DIR    Custom backup directory (default: /tmp/scholaria_backup_test)

EXAMPLES:
    $0                  # Run full test cycle
    $0 --keep-env       # Run test and keep environment for inspection

EOF
}

main() {
    local keep_env=false
    local start_time=$(date +%s)

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            --keep-env)
                keep_env=true
                shift
                ;;
            --backup-dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    log "Starting backup-restore test cycle..."

    trap 'error_exit "Test interrupted"' INT TERM

    setup_test_env
    seed_test_data
    capture_baseline

    backup_path=$(run_backup)

    wipe_data

    run_restore "${backup_path}"

    verify_integrity

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log "Test cycle completed successfully in ${duration}s"

    if [ "${keep_env}" = false ]; then
        cleanup_test_env
    else
        log "Test environment kept for inspection (use 'docker compose -f docker-compose.dev.yml down -v' to clean up)"
    fi

    log "All checks PASSED"
}

main "$@"
