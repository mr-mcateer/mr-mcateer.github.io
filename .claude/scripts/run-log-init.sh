#!/bin/bash
# run-log-init.sh -- Create today's run log from template if it doesn't exist.
# Called by the /session-start command.

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="${REPO_ROOT}/logs/run-log-${TODAY}.md"
TEMPLATE="${REPO_ROOT}/logs/run-log-template.md"

if [ -f "$LOG_FILE" ]; then
    echo "RUN_LOG_EXISTS=${LOG_FILE}"
else
    if [ -f "$TEMPLATE" ]; then
        sed "s/{DATE}/${TODAY}/g" "$TEMPLATE" > "$LOG_FILE"
        echo "RUN_LOG_CREATED=${LOG_FILE}"
    else
        echo "ERROR: Template not found at ${TEMPLATE}"
        exit 1
    fi
fi
