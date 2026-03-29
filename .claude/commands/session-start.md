# /session-start -- EEF Boot Sequence

You are executing the Active EEF session boot sequence. Follow these steps exactly.

## Step 1: Detect Time & Infer Mode
Run `date '+%H:%M %p'` to get the current time. Infer the likely context:
- Before 1:00 PM --> `morning-shop` (CVHS teaching)
- 1:00 PM to 4:00 PM --> transition window (could be any mode -- ask user)
- After 4:00 PM --> `afternoon-family` or `deep-work`

Store the current time as SESSION_TIME (HH:MM format).

## Step 2: Confirm Mode & Hard Stops
Present to the user:
```
SESSION BOOT
------------
Detected time: [SESSION_TIME]
Inferred mode: [morning-shop / afternoon-family / deep-work]

Default hard stops:
  - Leave shop: 2:45 PM
  - Relieve childcare: 3:15 PM
```

Ask: "Confirm mode and hard stops, or override?"

Wait for user response. Store the confirmed values as:
- CONFIRMED_MODE (e.g., "morning-shop")
- CONFIRMED_STOPS (e.g., "Leave shop 2:45 PM, Relieve childcare 3:15 PM")

## Step 3: Initialize Run Log
Run `bash .claude/scripts/run-log-init.sh "CONFIRMED_MODE" "SESSION_TIME" "CONFIRMED_STOPS"`
substituting the actual confirmed values from Step 2.

This fills in {DATE}, {MODE}, {TIME}, and {HARD_STOPS} in the template.
If the run-log already exists, the script returns RUN_LOG_EXISTS (tokens already filled
from a prior session-start today -- proceed to Step 4).

## Step 4: Check Yesterday's Carryover
List files in `logs/` matching `run-log-*.md`. Sort by date. Find the most recent
file BEFORE today. If one exists, read its `## End-of-Day Summary` and `## Carryover`
sections. Extract:
- Any incomplete tasks (lines containing "TODO", "pending", "incomplete", or "[ ]")
- Any items flagged for follow-up

Append these to today's run-log under `## Carryover`. Report count to user.

## Step 5: Check Morning Briefing
If `memory/morning_briefing.md` exists and is not the default placeholder, read and
display its contents to the user. This was prepared by the Night Shift script overnight.

## Step 6: Schedule Transition Alerts
Once mode is confirmed, if there are hard stops applicable to the current mode:
- On macOS, run `.claude/scripts/schedule_shift.sh` for each hard stop.
  Example: `bash .claude/scripts/schedule_shift.sh "14:45" "Leave Shop" "Save state and head out."`
- On other platforms, log the schedule to the run-log for manual reference.

## Step 7: Activate Context
Report to the user:
```
EEF active.
Mode:      [CONFIRMED_MODE]
Session:   [SESSION_TIME]
Next stop: [first hard stop time] ([context])
Carryover: [N items from yesterday]
```
