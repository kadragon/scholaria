#!/bin/bash

# Scholaria Database Backup Script
# This script creates comprehensive backups of PostgreSQL, Redis, and Qdrant data

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backup}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PREFIX="scholaria_backup_${TIMESTAMP}"

# Database connection settings
DB_HOST="${DB_HOST:-postgres}"
DB_NAME="${DB_NAME:-scholaria}"
DB_USER="${DB_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"

# Redis settings
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Qdrant settings
QDRANT_HOST="${QDRANT_HOST:-qdrant}"
QDRANT_PORT="${QDRANT_PORT:-6333}"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Create backup directory
create_backup_dir() {
    local backup_path="${BACKUP_DIR}/${BACKUP_PREFIX}"
    mkdir -p "${backup_path}"
    echo "${backup_path}"
}

# Backup PostgreSQL database
backup_postgres() {
    local backup_path="$1"
    local pg_backup_file="${backup_path}/postgres_${BACKUP_PREFIX}.sql"

    log "Starting PostgreSQL backup..."

    # Create SQL dump
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
        -h "${DB_HOST}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=custom \
        --file="${pg_backup_file}.custom" || error_exit "PostgreSQL backup failed"

    # Also create plain SQL for easier inspection/manual recovery
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
        -h "${DB_HOST}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --verbose \
        --clean \
        --if-exists \
        --create \
        > "${pg_backup_file}" || error_exit "PostgreSQL plain SQL backup failed"

    # Compress the plain SQL file
    gzip "${pg_backup_file}"

    log "PostgreSQL backup completed: ${pg_backup_file}.custom and ${pg_backup_file}.gz"
}

# Backup Redis data
backup_redis() {
    local backup_path="$1"
    local redis_backup_file="${backup_path}/redis_${BACKUP_PREFIX}.rdb"

    log "Starting Redis backup..."

    # Trigger Redis BGSAVE
    redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" BGSAVE > /dev/null

    # Wait for background save to complete
    while [ "$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" LASTSAVE)" = "$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" LASTSAVE)" ]; do
        sleep 1
    done

    # Copy the RDB file from Redis container
    if command -v docker &> /dev/null; then
        # If running in Docker environment
        local redis_container=$(docker ps --filter "name=redis" --format "{{.Names}}" | head -n1)
        if [ -n "${redis_container}" ]; then
            docker cp "${redis_container}:/data/dump.rdb" "${redis_backup_file}" || error_exit "Redis backup copy failed"
        else
            error_exit "Redis container not found"
        fi
    else
        # If Redis is running locally
        cp "/var/lib/redis/dump.rdb" "${redis_backup_file}" || error_exit "Redis backup copy failed"
    fi

    # Compress the RDB file
    gzip "${redis_backup_file}"

    log "Redis backup completed: ${redis_backup_file}.gz"
}

# Backup Qdrant data
backup_qdrant() {
    local backup_path="$1"
    local qdrant_backup_dir="${backup_path}/qdrant_${BACKUP_PREFIX}"

    log "Starting Qdrant backup..."

    # Create Qdrant snapshot via API
    local snapshot_name="backup_${TIMESTAMP}"
    curl -X POST "http://${QDRANT_HOST}:${QDRANT_PORT}/snapshots" \
        -H "Content-Type: application/json" \
        -d "{\"snapshot_name\": \"${snapshot_name}\"}" || error_exit "Qdrant snapshot creation failed"

    # Wait a moment for snapshot to be created
    sleep 5

    # Download the snapshot
    mkdir -p "${qdrant_backup_dir}"
    curl -X GET "http://${QDRANT_HOST}:${QDRANT_PORT}/snapshots/${snapshot_name}" \
        --output "${qdrant_backup_dir}/qdrant_snapshot.tar" || error_exit "Qdrant snapshot download failed"

    # Compress the snapshot
    gzip "${qdrant_backup_dir}/qdrant_snapshot.tar"

    log "Qdrant backup completed: ${qdrant_backup_dir}/qdrant_snapshot.tar.gz"
}

# Create backup manifest
create_manifest() {
    local backup_path="$1"
    local manifest_file="${backup_path}/backup_manifest.json"

    cat > "${manifest_file}" << EOF
{
    "backup_timestamp": "${TIMESTAMP}",
    "backup_date": "$(date -Iseconds)",
    "backup_type": "full",
    "components": {
        "postgresql": {
            "database": "${DB_NAME}",
            "files": [
                "postgres_${BACKUP_PREFIX}.sql.custom",
                "postgres_${BACKUP_PREFIX}.sql.gz"
            ]
        },
        "redis": {
            "files": [
                "redis_${BACKUP_PREFIX}.rdb.gz"
            ]
        },
        "qdrant": {
            "files": [
                "qdrant_${BACKUP_PREFIX}/qdrant_snapshot.tar.gz"
            ]
        }
    },
    "retention_policy": {
        "retention_days": ${RETENTION_DAYS}
    }
}
EOF

    log "Backup manifest created: ${manifest_file}"
}

# Calculate checksums
create_checksums() {
    local backup_path="$1"
    local checksum_file="${backup_path}/SHA256SUMS"

    cd "${backup_path}"
    find . -type f -not -name "SHA256SUMS" -exec sha256sum {} \; > "${checksum_file}"
    cd - > /dev/null

    log "Checksums created: ${checksum_file}"
}

# Clean up old backups
cleanup_old_backups() {
    log "Cleaning up backups older than ${RETENTION_DAYS} days..."

    find "${BACKUP_DIR}" -maxdepth 1 -type d -name "scholaria_backup_*" -mtime +${RETENTION_DAYS} -exec rm -rf {} \;

    log "Old backup cleanup completed"
}

# Verify backup integrity
verify_backup() {
    local backup_path="$1"

    log "Verifying backup integrity..."

    # Verify checksums
    cd "${backup_path}"
    if sha256sum -c SHA256SUMS > /dev/null 2>&1; then
        log "Backup integrity verification PASSED"
    else
        error_exit "Backup integrity verification FAILED"
    fi
    cd - > /dev/null
}

# Main backup function
main() {
    log "Starting Scholaria backup process..."

    # Create backup directory
    local backup_path
    backup_path=$(create_backup_dir)

    # Perform backups
    backup_postgres "${backup_path}"
    backup_redis "${backup_path}"
    backup_qdrant "${backup_path}"

    # Create manifest and checksums
    create_manifest "${backup_path}"
    create_checksums "${backup_path}"

    # Verify backup
    verify_backup "${backup_path}"

    # Clean up old backups
    cleanup_old_backups

    log "Backup process completed successfully: ${backup_path}"

    # Output backup size
    local backup_size=$(du -sh "${backup_path}" | cut -f1)
    log "Total backup size: ${backup_size}"
}

# Run main function
main "$@"
