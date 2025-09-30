#!/bin/bash

# Scholaria Database Restore Script
# This script restores backups created by backup.sh

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backup}"
DRY_RUN="${DRY_RUN:-false}"

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

# Print usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS] BACKUP_PATH

Restore Scholaria database from backup.

ARGUMENTS:
    BACKUP_PATH     Path to backup directory or auto-discover with 'latest'

OPTIONS:
    -h, --help              Show this help message
    -d, --dry-run          Show what would be restored without making changes
    -c, --component COMP   Restore only specific component (postgres|redis|qdrant|all)
    --skip-verification    Skip backup integrity verification
    --force               Force restore without confirmation prompts

EXAMPLES:
    $0 latest                                   # Restore from latest backup
    $0 /backup/scholaria_backup_20240301_120000 # Restore from specific backup
    $0 --component postgres latest              # Restore only PostgreSQL
    $0 --dry-run latest                         # Show what would be restored

ENVIRONMENT VARIABLES:
    BACKUP_DIR              Directory containing backups (default: /backup)
    DRY_RUN                 Set to 'true' for dry run mode
    DB_HOST, DB_NAME, etc.  Database connection parameters

EOF
}

# Find latest backup
find_latest_backup() {
    local latest_backup
    latest_backup=$(find "${BACKUP_DIR}" -maxdepth 1 -type d -name "scholaria_backup_*" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

    if [ -z "${latest_backup}" ]; then
        error_exit "No backups found in ${BACKUP_DIR}"
    fi

    echo "${latest_backup}"
}

# Validate backup directory
validate_backup() {
    local backup_path="$1"
    local skip_verification="$2"

    if [ ! -d "${backup_path}" ]; then
        error_exit "Backup directory does not exist: ${backup_path}"
    fi

    local manifest_file="${backup_path}/backup_manifest.json"
    if [ ! -f "${manifest_file}" ]; then
        error_exit "Backup manifest not found: ${manifest_file}"
    fi

    if [ "${skip_verification}" = "false" ]; then
        log "Verifying backup integrity..."

        local checksum_file="${backup_path}/SHA256SUMS"
        if [ ! -f "${checksum_file}" ]; then
            error_exit "Checksum file not found: ${checksum_file}"
        fi

        cd "${backup_path}"
        if ! sha256sum -c SHA256SUMS > /dev/null 2>&1; then
            error_exit "Backup integrity verification failed"
        fi
        cd - > /dev/null

        log "Backup integrity verification passed"
    fi
}

# Show backup information
show_backup_info() {
    local backup_path="$1"
    local manifest_file="${backup_path}/backup_manifest.json"

    log "Backup Information:"
    log "==================="

    if command -v jq &> /dev/null; then
        log "Backup Date: $(jq -r '.backup_date' "${manifest_file}")"
        log "Backup Type: $(jq -r '.backup_type' "${manifest_file}")"
        log "Components:"
        jq -r '.components | to_entries[] | "  - \(.key)"' "${manifest_file}" | while read line; do
            log "$line"
        done
    else
        log "Path: ${backup_path}"
        log "Manifest: ${manifest_file}"
    fi

    local backup_size=$(du -sh "${backup_path}" | cut -f1)
    log "Total Size: ${backup_size}"
    log "==================="
}

# Stop services before restore
stop_services() {
    local component="$1"

    if [ "${DRY_RUN}" = "true" ]; then
        log "[DRY RUN] Would stop services for component: ${component}"
        return
    fi

    log "Stopping services for component: ${component}"

    case "${component}" in
        "postgres"|"all")
            if command -v docker &> /dev/null; then
                docker-compose stop web celery-worker celery-beat || true
            fi
            ;;
        "redis"|"all")
            if command -v docker &> /dev/null; then
                docker-compose stop celery-worker celery-beat || true
            fi
            ;;
    esac
}

# Start services after restore
start_services() {
    local component="$1"

    if [ "${DRY_RUN}" = "true" ]; then
        log "[DRY RUN] Would start services for component: ${component}"
        return
    fi

    log "Starting services for component: ${component}"

    case "${component}" in
        "postgres"|"redis"|"all")
            if command -v docker &> /dev/null; then
                docker-compose up -d web celery-worker celery-beat || true
            fi
            ;;
    esac
}

# Restore PostgreSQL database
restore_postgres() {
    local backup_path="$1"
    local manifest_file="${backup_path}/backup_manifest.json"

    log "Restoring PostgreSQL database..."

    # Find backup files
    local custom_backup=""
    local sql_backup=""

    if command -v jq &> /dev/null; then
        # Use jq to parse manifest
        custom_backup=$(jq -r '.components.postgresql.files[] | select(endswith(".custom"))' "${manifest_file}" 2>/dev/null | head -n1)
        sql_backup=$(jq -r '.components.postgresql.files[] | select(endswith(".sql.gz"))' "${manifest_file}" 2>/dev/null | head -n1)
    else
        # Fallback: find files by pattern
        custom_backup=$(find "${backup_path}" -name "postgres_*.sql.custom" -type f | head -n1)
        sql_backup=$(find "${backup_path}" -name "postgres_*.sql.gz" -type f | head -n1)
    fi

    if [ -z "${custom_backup}" ] && [ -z "${sql_backup}" ]; then
        error_exit "No PostgreSQL backup files found"
    fi

    if [ "${DRY_RUN}" = "true" ]; then
        log "[DRY RUN] Would restore PostgreSQL from: ${custom_backup:-$sql_backup}"
        return
    fi

    # Prefer custom format for faster restore
    if [ -n "${custom_backup}" ] && [ -f "${backup_path}/${custom_backup}" ]; then
        log "Restoring from custom format backup: ${custom_backup}"

        # Drop existing database and recreate
        PGPASSWORD="${POSTGRES_PASSWORD}" dropdb -h "${DB_HOST}" -U "${DB_USER}" --if-exists "${DB_NAME}" || error_exit "Failed to drop database"
        PGPASSWORD="${POSTGRES_PASSWORD}" createdb -h "${DB_HOST}" -U "${DB_USER}" "${DB_NAME}" || error_exit "Failed to create database"

        # Restore from custom format
        PGPASSWORD="${POSTGRES_PASSWORD}" pg_restore \
            -h "${DB_HOST}" \
            -U "${DB_USER}" \
            -d "${DB_NAME}" \
            --verbose \
            --clean \
            --if-exists \
            --no-owner \
            --no-privileges \
            "${backup_path}/${custom_backup}" || error_exit "PostgreSQL restore failed"

    elif [ -n "${sql_backup}" ] && [ -f "${backup_path}/${sql_backup}" ]; then
        log "Restoring from SQL backup: ${sql_backup}"

        # Restore from compressed SQL
        gunzip -c "${backup_path}/${sql_backup}" | PGPASSWORD="${POSTGRES_PASSWORD}" psql \
            -h "${DB_HOST}" \
            -U "${DB_USER}" \
            -d postgres \
            --quiet || error_exit "PostgreSQL restore failed"
    else
        error_exit "PostgreSQL backup file not found"
    fi

    log "PostgreSQL restore completed"
}

# Restore Redis data
restore_redis() {
    local backup_path="$1"
    local manifest_file="${backup_path}/backup_manifest.json"

    log "Restoring Redis data..."

    # Find Redis backup file
    local redis_backup=""

    if command -v jq &> /dev/null; then
        redis_backup=$(jq -r '.components.redis.files[0]' "${manifest_file}" 2>/dev/null)
    else
        redis_backup=$(find "${backup_path}" -name "redis_*.rdb.gz" -type f | head -n1 | xargs basename)
    fi

    if [ -z "${redis_backup}" ] || [ ! -f "${backup_path}/${redis_backup}" ]; then
        error_exit "Redis backup file not found: ${redis_backup}"
    fi

    if [ "${DRY_RUN}" = "true" ]; then
        log "[DRY RUN] Would restore Redis from: ${redis_backup}"
        return
    fi

    # Stop Redis before restore
    if command -v docker &> /dev/null; then
        local redis_container=$(docker ps --filter "name=redis" --format "{{.Names}}" | head -n1)
        if [ -n "${redis_container}" ]; then
            docker-compose stop redis

            # Extract and copy RDB file
            local temp_rdb="/tmp/dump.rdb"
            gunzip -c "${backup_path}/${redis_backup}" > "${temp_rdb}"

            # Copy to Redis data volume
            docker-compose up -d redis
            sleep 5  # Wait for Redis to start
            docker-compose stop redis
            docker cp "${temp_rdb}" "${redis_container}:/data/dump.rdb"
            rm "${temp_rdb}"

            # Start Redis
            docker-compose up -d redis
        else
            error_exit "Redis container not found"
        fi
    else
        # Local Redis restore
        systemctl stop redis-server || error_exit "Failed to stop Redis"
        gunzip -c "${backup_path}/${redis_backup}" > "/var/lib/redis/dump.rdb"
        chown redis:redis "/var/lib/redis/dump.rdb"
        systemctl start redis-server || error_exit "Failed to start Redis"
    fi

    log "Redis restore completed"
}

# Restore Qdrant data
restore_qdrant() {
    local backup_path="$1"
    local manifest_file="${backup_path}/backup_manifest.json"

    log "Restoring Qdrant data..."

    # Find Qdrant backup
    local qdrant_snapshot=""

    if command -v jq &> /dev/null; then
        qdrant_snapshot=$(jq -r '.components.qdrant.files[0]' "${manifest_file}" 2>/dev/null)
    else
        qdrant_snapshot=$(find "${backup_path}" -name "qdrant_snapshot.tar.gz" -type f | head -n1)
    fi

    if [ -z "${qdrant_snapshot}" ]; then
        error_exit "Qdrant backup file not found"
    fi

    local qdrant_file="${backup_path}/${qdrant_snapshot}"
    if [[ "${qdrant_snapshot}" == /* ]]; then
        qdrant_file="${qdrant_snapshot}"  # Already absolute path
    fi

    if [ ! -f "${qdrant_file}" ]; then
        error_exit "Qdrant backup file not found: ${qdrant_file}"
    fi

    if [ "${DRY_RUN}" = "true" ]; then
        log "[DRY RUN] Would restore Qdrant from: ${qdrant_file}"
        return
    fi

    # Extract snapshot
    local temp_dir="/tmp/qdrant_restore_$$"
    mkdir -p "${temp_dir}"
    gunzip -c "${qdrant_file}" > "${temp_dir}/snapshot.tar"

    # Upload snapshot to Qdrant
    curl -X POST "http://${QDRANT_HOST}:${QDRANT_PORT}/snapshots/upload" \
        -H "Content-Type: application/octet-stream" \
        --data-binary "@${temp_dir}/snapshot.tar" || error_exit "Qdrant snapshot upload failed"

    # Clean up
    rm -rf "${temp_dir}"

    log "Qdrant restore completed"
}

# Confirm restore operation
confirm_restore() {
    local backup_path="$1"
    local component="$2"
    local force="$3"

    if [ "${force}" = "true" ] || [ "${DRY_RUN}" = "true" ]; then
        return
    fi

    echo
    log "WARNING: This will OVERWRITE existing data!"
    log "Backup: ${backup_path}"
    log "Component: ${component}"
    echo
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm

    if [ "${confirm}" != "yes" ]; then
        log "Restore cancelled by user"
        exit 1
    fi
}

# Main restore function
main() {
    local backup_path=""
    local component="all"
    local skip_verification="false"
    local force="false"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -c|--component)
                component="$2"
                shift 2
                ;;
            --skip-verification)
                skip_verification="true"
                shift
                ;;
            --force)
                force="true"
                shift
                ;;
            -*)
                error_exit "Unknown option: $1"
                ;;
            *)
                if [ -z "${backup_path}" ]; then
                    backup_path="$1"
                else
                    error_exit "Too many arguments"
                fi
                shift
                ;;
        esac
    done

    # Validate arguments
    if [ -z "${backup_path}" ]; then
        error_exit "Backup path is required. Use 'latest' for most recent backup or provide specific path."
    fi

    if [[ ! "${component}" =~ ^(postgres|redis|qdrant|all)$ ]]; then
        error_exit "Invalid component. Must be one of: postgres, redis, qdrant, all"
    fi

    # Find backup path
    if [ "${backup_path}" = "latest" ]; then
        backup_path=$(find_latest_backup)
        log "Using latest backup: ${backup_path}"
    fi

    # Validate backup
    validate_backup "${backup_path}" "${skip_verification}"

    # Show backup information
    show_backup_info "${backup_path}"

    # Confirm restore
    confirm_restore "${backup_path}" "${component}" "${force}"

    log "Starting restore process..."

    # Stop relevant services
    stop_services "${component}"

    # Perform restore based on component
    case "${component}" in
        "postgres")
            restore_postgres "${backup_path}"
            ;;
        "redis")
            restore_redis "${backup_path}"
            ;;
        "qdrant")
            restore_qdrant "${backup_path}"
            ;;
        "all")
            restore_postgres "${backup_path}"
            restore_redis "${backup_path}"
            restore_qdrant "${backup_path}"
            ;;
    esac

    # Start services
    start_services "${component}"

    if [ "${DRY_RUN}" = "true" ]; then
        log "[DRY RUN] Restore simulation completed"
    else
        log "Restore process completed successfully"
    fi
}

# Run main function
main "$@"
