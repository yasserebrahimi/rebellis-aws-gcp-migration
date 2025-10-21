#!/bin/bash
log_info "redis-cli not found; skipping Redis backup"
return
fi


local redis_rdb="${BACKUP_DIR}/${BACKUP_PREFIX}_redis.rdb"
# Try to trigger a save and copy the RDB if a local server
if redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -n "${REDIS_DB}" ping >/dev/null 2>&1; then
redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -n "${REDIS_DB}" BGSAVE || true
sleep 2
# Try common dump locations
for rdb in /var/lib/redis/dump.rdb /data/dump.rdb; do
if [[ -f "$rdb" ]]; then
cp "$rdb" "$redis_rdb" && break
fi
done
# Fallback: use --rdb export (works when permitted)
if [[ ! -f "$redis_rdb" ]]; then
redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" --rdb "$redis_rdb" || true
fi
if [[ -f "$redis_rdb" ]]; then
gzip -f "$redis_rdb"
log_success "Redis backup complete: ${redis_rdb}.gz"
else
log_info "Redis backup not produced (permissions/paths)"
fi
else
log_info "Redis not reachable; skipping"
fi
}


package_meta() {
log_info "Creating checksum and manifest..."
local manifest="${BACKUP_DIR}/${BACKUP_PREFIX}_manifest.txt"
{
echo "ENVIRONMENT=${ENVIRONMENT}"
echo "TIMESTAMP=${TIMESTAMP}"
echo "DB_HOST=${DB_HOST}"
echo "DB_NAME=${DB_NAME}"
echo "REDIS_HOST=${REDIS_HOST}"
} > "$manifest"


(cd "$BACKUP_DIR" && sha256sum ${BACKUP_PREFIX}_* 2>/dev/null || shasum -a 256 ${BACKUP_PREFIX}_* 2>/dev/null || true) > "${manifest}.sha256" || true
}


upload_s3() {
if [[ -n "${S3_BUCKET}" ]]; then
if ! command -v aws >/dev/null 2>&1; then
log_error "aws CLI not found but S3_BUCKET is set"
fi
log_info "Uploading backups to s3://${S3_BUCKET}/${ENVIRONMENT}/ ..."
aws s3 cp "${BACKUP_DIR}" "s3://${S3_BUCKET}/${ENVIRONMENT}/" --recursive --exclude "*" --include "${BACKUP_PREFIX}_*"
log_success "Uploaded to S3"
fi
}


rotate_local() {
log_info "Rotating local backups keeping ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -mtime +"${RETENTION_DAYS}" -name 'rebellis_backup_*' -print -delete || true
}


main() {
backup_database
backup_redis
package_meta
upload_s3
rotate_local
log_success "Backup completed"
}


main "$@"