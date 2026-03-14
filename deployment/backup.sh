#!/bin/bash

# Automated EDA - Backup Script
# Run this with cron for automatic backups: 0 2 * * * /path/to/backup.sh

BACKUP_DIR="/backups/automated-eda"
DATABASE_NAME="automated_eda"
CONTAINER_NAME="automated_eda_postgres"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql"

echo "Starting database backup at $(date)"

# Backup PostgreSQL database
docker-compose exec -T postgres pg_dump -U postgres "$DATABASE_NAME" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "Backup completed: ${BACKUP_FILE}.gz"

# Remove old backups (older than RETENTION_DAYS)
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

echo "Cleanup completed - removed backups older than $RETENTION_DAYS days"

# Upload to cloud storage (optional - uncomment and configure)
# aws s3 cp "${BACKUP_FILE}.gz" s3://your-bucket/backups/
# echo "Uploaded to S3"

echo "Backup finished at $(date)"
