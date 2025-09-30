#!/bin/bash

# Scholaria Backup Scheduler
# This script manages scheduled backups with different frequencies

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup.sh"
LOG_DIR="${LOG_DIR:-/var/log/scholaria}"
BACKUP_DIR="${BACKUP_DIR:-/backup}"

# Backup types and retention
DAILY_RETENTION="${DAILY_RETENTION:-7}"
WEEKLY_RETENTION="${WEEKLY_RETENTION:-30}"
MONTHLY_RETENTION="${MONTHLY_RETENTION:-365}"

# Notification settings
NOTIFY_EMAIL="${NOTIFY_EMAIL:-}"
NOTIFY_WEBHOOK="${NOTIFY_WEBHOOK:-}"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    send_notification "ERROR" "$1"
    exit 1
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Email notification
    if [ -n "${NOTIFY_EMAIL}" ] && command -v mail &> /dev/null; then
        echo "Scholaria Backup ${status} at ${timestamp}: ${message}" | mail -s "Scholaria Backup ${status}" "${NOTIFY_EMAIL}"
    fi

    # Webhook notification
    if [ -n "${NOTIFY_WEBHOOK}" ] && command -v curl &> /dev/null; then
        curl -X POST "${NOTIFY_WEBHOOK}" \
            -H "Content-Type: application/json" \
            -d "{\"status\": \"${status}\", \"message\": \"${message}\", \"timestamp\": \"${timestamp}\"}" \
            > /dev/null 2>&1 || true
    fi
}

# Setup log directory
setup_logging() {
    mkdir -p "${LOG_DIR}"

    # Log rotation setup
    cat > "/tmp/scholaria-backup-logrotate" << EOF
${LOG_DIR}/backup-*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

    # Install logrotate config if running as root
    if [ "$(id -u)" -eq 0 ] && [ -d "/etc/logrotate.d" ]; then
        cp "/tmp/scholaria-backup-logrotate" "/etc/logrotate.d/scholaria-backup"
    fi
}

# Cleanup old backups based on type
cleanup_backups() {
    local backup_type="$1"
    local retention_days="$2"

    log "Cleaning up ${backup_type} backups older than ${retention_days} days..."

    # Find and remove old backups
    find "${BACKUP_DIR}" -maxdepth 1 -type d -name "scholaria_backup_*" -mtime +${retention_days} | while read backup_dir; do
        # Check if this backup matches the type
        local backup_name=$(basename "${backup_dir}")
        local backup_date=$(echo "${backup_name}" | sed 's/scholaria_backup_\([0-9]\{8\}\)_.*/\1/')

        case "${backup_type}" in
            "daily")
                # Daily backups: remove all older than retention
                log "Removing old daily backup: ${backup_dir}"
                rm -rf "${backup_dir}"
                ;;
            "weekly")
                # Weekly backups: keep only Sunday backups
                local day_of_week=$(date -d "${backup_date}" +%u 2>/dev/null || echo "0")
                if [ "${day_of_week}" = "7" ]; then  # Sunday
                    if [ $(find "${backup_dir}" -mtime +${retention_days} | wc -l) -gt 0 ]; then
                        log "Removing old weekly backup: ${backup_dir}"
                        rm -rf "${backup_dir}"
                    fi
                fi
                ;;
            "monthly")
                # Monthly backups: keep only first of month backups
                local day_of_month=$(date -d "${backup_date}" +%d 2>/dev/null || echo "0")
                if [ "${day_of_month}" = "01" ]; then  # First of month
                    if [ $(find "${backup_dir}" -mtime +${retention_days} | wc -l) -gt 0 ]; then
                        log "Removing old monthly backup: ${backup_dir}"
                        rm -rf "${backup_dir}"
                    fi
                fi
                ;;
        esac
    done
}

# Run backup with logging
run_backup() {
    local backup_type="$1"
    local log_file="${LOG_DIR}/backup-${backup_type}-$(date +%Y%m%d).log"

    log "Starting ${backup_type} backup..."

    # Set retention for this backup type
    case "${backup_type}" in
        "daily")
            export RETENTION_DAYS="${DAILY_RETENTION}"
            ;;
        "weekly")
            export RETENTION_DAYS="${WEEKLY_RETENTION}"
            ;;
        "monthly")
            export RETENTION_DAYS="${MONTHLY_RETENTION}"
            ;;
    esac

    # Run backup and capture output
    if "${BACKUP_SCRIPT}" >> "${log_file}" 2>&1; then
        local backup_size=$(tail -n 5 "${log_file}" | grep "Total backup size:" | cut -d':' -f2 | xargs || echo "unknown")
        log "${backup_type} backup completed successfully (${backup_size})"
        send_notification "SUCCESS" "${backup_type} backup completed (${backup_size})"

        # Cleanup old backups
        cleanup_backups "${backup_type}" "${RETENTION_DAYS}"
    else
        local error_msg="$(tail -n 10 "${log_file}" | grep ERROR | tail -n 1 || echo "Backup failed - check log: ${log_file}")"
        error_exit "${backup_type} backup failed: ${error_msg}"
    fi
}

# Install cron jobs
install_cron() {
    local cron_user="${1:-root}"

    log "Installing cron jobs for user: ${cron_user}"

    # Create cron entries
    local cron_entries=$(cat << EOF
# Scholaria Database Backup Schedule
# Daily backup at 2 AM
0 2 * * * ${SCRIPT_DIR}/backup-scheduler.sh daily >> ${LOG_DIR}/scheduler.log 2>&1

# Weekly backup on Sunday at 3 AM
0 3 * * 0 ${SCRIPT_DIR}/backup-scheduler.sh weekly >> ${LOG_DIR}/scheduler.log 2>&1

# Monthly backup on 1st day at 4 AM
0 4 1 * * ${SCRIPT_DIR}/backup-scheduler.sh monthly >> ${LOG_DIR}/scheduler.log 2>&1

# Health check every 6 hours
0 */6 * * * ${SCRIPT_DIR}/backup-scheduler.sh health-check >> ${LOG_DIR}/scheduler.log 2>&1
EOF
)

    # Install cron jobs
    if command -v crontab &> /dev/null; then
        (crontab -u "${cron_user}" -l 2>/dev/null | grep -v "Scholaria Database Backup" || true; echo "${cron_entries}") | crontab -u "${cron_user}" -
        log "Cron jobs installed successfully"
    else
        log "WARNING: crontab not available. Manual cron setup required:"
        echo "${cron_entries}"
    fi
}

# Remove cron jobs
remove_cron() {
    local cron_user="${1:-root}"

    log "Removing cron jobs for user: ${cron_user}"

    if command -v crontab &> /dev/null; then
        crontab -u "${cron_user}" -l 2>/dev/null | grep -v "Scholaria Database Backup" | grep -v "${SCRIPT_DIR}/backup-scheduler.sh" | crontab -u "${cron_user}" -
        log "Cron jobs removed successfully"
    else
        log "WARNING: crontab not available. Manual cron cleanup required"
    fi
}

# Health check
health_check() {
    log "Running backup system health check..."

    local issues=()

    # Check backup directory
    if [ ! -d "${BACKUP_DIR}" ]; then
        issues+=("Backup directory does not exist: ${BACKUP_DIR}")
    elif [ ! -w "${BACKUP_DIR}" ]; then
        issues+=("Backup directory is not writable: ${BACKUP_DIR}")
    fi

    # Check backup script
    if [ ! -f "${BACKUP_SCRIPT}" ]; then
        issues+=("Backup script not found: ${BACKUP_SCRIPT}")
    elif [ ! -x "${BACKUP_SCRIPT}" ]; then
        issues+=("Backup script is not executable: ${BACKUP_SCRIPT}")
    fi

    # Check log directory
    if [ ! -d "${LOG_DIR}" ]; then
        issues+=("Log directory does not exist: ${LOG_DIR}")
    elif [ ! -w "${LOG_DIR}" ]; then
        issues+=("Log directory is not writable: ${LOG_DIR}")
    fi

    # Check recent backup
    local latest_backup=$(find "${BACKUP_DIR}" -maxdepth 1 -type d -name "scholaria_backup_*" -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || echo "")
    if [ -z "${latest_backup}" ]; then
        issues+=("No backups found in backup directory")
    else
        local backup_age=$(find "${latest_backup}" -mtime +2 2>/dev/null | wc -l)
        if [ "${backup_age}" -gt 0 ]; then
            issues+=("Latest backup is older than 2 days: ${latest_backup}")
        fi
    fi

    # Check disk space
    local available_space=$(df "${BACKUP_DIR}" | awk 'NR==2 {print $4}')
    local required_space=1048576  # 1GB in KB
    if [ "${available_space}" -lt "${required_space}" ]; then
        issues+=("Low disk space in backup directory: $(df -h "${BACKUP_DIR}" | awk 'NR==2 {print $4}') available")
    fi

    # Report results
    if [ ${#issues[@]} -eq 0 ]; then
        log "Health check passed - backup system is healthy"
        send_notification "INFO" "Backup system health check passed"
    else
        local issue_list=$(printf '%s\n' "${issues[@]}")
        log "Health check failed - issues found:"
        echo "${issue_list}"
        send_notification "WARNING" "Backup system health check failed: ${issue_list}"
    fi
}

# Show status
show_status() {
    log "Backup System Status"
    log "==================="
    log "Backup Directory: ${BACKUP_DIR}"
    log "Log Directory: ${LOG_DIR}"
    log "Backup Script: ${BACKUP_SCRIPT}"
    echo

    # Show recent backups
    log "Recent Backups:"
    find "${BACKUP_DIR}" -maxdepth 1 -type d -name "scholaria_backup_*" -printf '%T+ %p\n' 2>/dev/null | sort -r | head -10 | while read timestamp path; do
        local backup_name=$(basename "${path}")
        local backup_size=$(du -sh "${path}" 2>/dev/null | cut -f1 || echo "unknown")
        log "  ${timestamp} ${backup_name} (${backup_size})"
    done
    echo

    # Show cron jobs
    log "Scheduled Jobs:"
    crontab -l 2>/dev/null | grep -A 5 -B 1 "Scholaria Database Backup" || log "  No cron jobs found"
    echo

    # Show disk usage
    log "Disk Usage:"
    df -h "${BACKUP_DIR}" | tail -1 | awk '{printf "  Backup Directory: %s used, %s available (%s used)\n", $3, $4, $5}'
    df -h "${LOG_DIR}" | tail -1 | awk '{printf "  Log Directory: %s used, %s available (%s used)\n", $3, $4, $5}'
}

# Main function
main() {
    local action="${1:-help}"

    # Setup logging
    setup_logging

    case "${action}" in
        "daily"|"weekly"|"monthly")
            run_backup "${action}"
            ;;
        "install-cron")
            install_cron "${2:-root}"
            ;;
        "remove-cron")
            remove_cron "${2:-root}"
            ;;
        "health-check")
            health_check
            ;;
        "status")
            show_status
            ;;
        "help"|"-h"|"--help")
            cat << EOF
Usage: $0 [ACTION] [OPTIONS]

ACTIONS:
    daily               Run daily backup
    weekly              Run weekly backup
    monthly             Run monthly backup
    install-cron [USER] Install cron jobs (default user: root)
    remove-cron [USER]  Remove cron jobs (default user: root)
    health-check        Check backup system health
    status              Show backup system status
    help                Show this help message

ENVIRONMENT VARIABLES:
    BACKUP_DIR          Backup directory (default: /backup)
    LOG_DIR             Log directory (default: /var/log/scholaria)
    DAILY_RETENTION     Daily backup retention days (default: 7)
    WEEKLY_RETENTION    Weekly backup retention days (default: 30)
    MONTHLY_RETENTION   Monthly backup retention days (default: 365)
    NOTIFY_EMAIL        Email for notifications
    NOTIFY_WEBHOOK      Webhook URL for notifications

EXAMPLES:
    $0 daily                    # Run daily backup
    $0 install-cron             # Install cron jobs as root
    $0 install-cron backup      # Install cron jobs as backup user
    $0 health-check             # Check system health
    $0 status                   # Show system status

EOF
            ;;
        *)
            error_exit "Unknown action: ${action}. Use '$0 help' for usage information."
            ;;
    esac
}

# Run main function
main "$@"
