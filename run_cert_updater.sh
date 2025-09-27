#!/bin/bash
# run_cert_updater.sh - Wrapper script for cron

SCRIPT_DIR="/home/fmndkn/python/cert_updater"
STATUS_FILE="$SCRIPT_DIR/last_run.status"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Started" > "$STATUS_FILE"

CONFIG_FILE="$SCRIPT_DIR/config.ini"
LOG_FILE="$SCRIPT_DIR/cron.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== $TIMESTAMP - Starting SSL Certificate Update ===" >> "$LOG_FILE"

cd "$SCRIPT_DIR"

# Активация виртуального окружения (если используется)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated" >> "$LOG_FILE"
fi

# Запуск скрипта
/usr/bin/python3 cert_updater.py -c "$CONFIG_FILE" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ $EXIT_CODE -eq 0 ]; then
    echo "=== $TIMESTAMP - Update completed successfully ===" >> "$LOG_FILE"
else
    echo "=== $TIMESTAMP - Update failed with exit code $EXIT_CODE ===" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Finished" >> "$STATUS_FILE"
