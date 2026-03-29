#!/bin/bash
# run-log-init.sh -- Create today's run log from template if it doesn't exist.
# Called by the /session-start command.
#
# Usage: bash run-log-init.sh [MODE] [TIME] [HARD_STOPS]
# If MODE/TIME/HARD_STOPS are omitted, placeholders remain for session-start to fill.

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)" || exit 1
TODAY=$(date +%Y-%m-%d) || { echo "ERROR: date command failed"; exit 1; }
LOG_FILE="${REPO_ROOT}/logs/run-log-${TODAY}.md"
TEMPLATE="${REPO_ROOT}/logs/run-log-template.md"

MODE="${1:-}"
TIME="${2:-}"
HARD_STOPS="${3:-}"

if [ -f "$LOG_FILE" ]; then
    echo "RUN_LOG_EXISTS=${LOG_FILE}"
else
    if [ -f "$TEMPLATE" ]; then
        sed_cmd="s|{DATE}|${TODAY}|g"
        [ -n "$MODE" ] && sed_cmd="${sed_cmd};s|{MODE}|${MODE}|g"
        [ -n "$TIME" ] && sed_cmd="${sed_cmd};s|{TIME}|${TIME}|g"
        [ -n "$HARD_STOPS" ] && sed_cmd="${sed_cmd};s|{HARD_STOPS}|${HARD_STOPS}|g"
        sed "$sed_cmd" "$TEMPLATE" > "$LOG_FILE"
        echo "RUN_LOG_CREATED=${LOG_FILE}"
    else
        echo "ERROR: Template not found at ${TEMPLATE}"
        exit 1
    fi
fi
