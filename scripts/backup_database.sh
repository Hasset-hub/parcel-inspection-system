#!/bin/bash

# Backup script for parcel_system database
BACKUP_DIR=~/projects/parcel-inspection-system/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/parcel_system_${TIMESTAMP}.sql"

echo "Starting backup..."
pg_dump -h localhost -U parcel_admin parcel_system > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    gzip "$BACKUP_FILE"
    echo "Compressed: ${BACKUP_FILE}.gz"

    # Keep only last 7 backups
    ls -t ${BACKUP_DIR}/parcel_system_*.sql.gz | tail -n +8 | xargs rm -f
    echo "Old backups cleaned up"
else
    echo "Backup failed!"
    exit 1
fi
