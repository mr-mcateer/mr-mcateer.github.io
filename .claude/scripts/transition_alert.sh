#!/bin/bash
# transition_alert.sh -- Multi-sensory, screen-hijacking alert for state transitions.
# Uses auditory cues, text-to-speech, and an AppleScript modal that blocks window focus.
#
# Usage: ./transition_alert.sh "30 Minutes to Dad Duty" "Wrap up shop dry runs."
# Requires: macOS with Accessibility permissions granted to Claude/Terminal.

TITLE="${1:-Transition Alert}"
MESSAGE="${2:-Time to switch contexts.}"

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: Full multi-sensory interrupt

    # 1. Auditory interrupt: pierces the hyper-focus bubble
    afplay /System/Library/Sounds/Glass.aiff &

    # 2. Voice announcement
    say "Attention. ${TITLE}." &

    # 3. Visual interrupt: system modal that blocks window focus until acknowledged
    osascript -e "
    tell application \"System Events\"
        activate
        display dialog \"${MESSAGE}\" with title \"${TITLE}\" buttons {\"Acknowledge & Save State\"} default button \"Acknowledge & Save State\" with icon caution
    end tell
    "
else
    # Linux/CI fallback: terminal-only alert
    echo ""
    echo "============================================"
    echo "  TRANSITION ALERT: ${TITLE}"
    echo "--------------------------------------------"
    echo "  ${MESSAGE}"
    echo "============================================"
    echo ""
    # Attempt bell character for terminal notification
    printf '\a'
fi
