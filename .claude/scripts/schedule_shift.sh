#!/bin/bash
# schedule_shift.sh -- Schedules cascading transition warnings before a hard stop.
# Deploys 30-minute, 15-minute, and 5-minute alerts using the macOS `at` daemon.
#
# Usage: ./schedule_shift.sh "15:00" "Dad Duty" "Time to transition to James and John."
# Requires: macOS with `atrun` enabled (sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_TIME="${1:?Usage: schedule_shift.sh HH:MM CONTEXT ACTION}"
CONTEXT="${2:?Missing context name (e.g., 'Dad Duty')}"
ACTION="${3:?Missing action description}"

# Validate time format
if ! echo "$TARGET_TIME" | grep -qE '^[0-9]{1,2}:[0-9]{2}$'; then
    echo "ERROR: Time must be in HH:MM format. Got: $TARGET_TIME"
    exit 1
fi

# Parse hours and minutes
IFS=':' read -r HOUR MIN <<< "$TARGET_TIME"

# Calculate warning times
calc_time() {
    local h=$HOUR m=$MIN offset=$1
    m=$((m - offset))
    while [ $m -lt 0 ]; do
        m=$((m + 60))
        h=$((h - 1))
    done
    printf "%02d:%02d" $h $m
}

T30=$(calc_time 30)
T15=$(calc_time 15)
T05=$(calc_time 5)

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: use `at` daemon for precise scheduling
    echo "${SCRIPT_DIR}/transition_alert.sh '30 Min to ${CONTEXT}' 'Save your work. ${ACTION}'" | at "$T30" 2>/dev/null
    echo "${SCRIPT_DIR}/transition_alert.sh '15 Min to ${CONTEXT}' 'Wrap up the task. Energy check. ${ACTION}'" | at "$T15" 2>/dev/null
    echo "${SCRIPT_DIR}/transition_alert.sh '5 Min to ${CONTEXT}' 'HARD STOP. Shutting down active work state.'" | at "$T05" 2>/dev/null

    echo "Scheduled transition alerts for ${CONTEXT}:"
    echo "  30-min warning at ${T30}"
    echo "  15-min warning at ${T15}"
    echo "   5-min warning at ${T05}"
    echo "  Hard stop at ${TARGET_TIME}"
else
    # Linux/CI: log the schedule (no `at` daemon assumed)
    echo "SCHEDULE (${CONTEXT} at ${TARGET_TIME}):"
    echo "  ${T30} -- 30-min warning"
    echo "  ${T15} -- 15-min warning"
    echo "  ${T05} --  5-min warning"
    echo "  NOTE: macOS at daemon required for live alerts."
fi
