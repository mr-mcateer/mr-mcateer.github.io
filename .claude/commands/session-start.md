# /session-start -- EEF Boot Sequence

You are executing the Active EEF session boot sequence. Follow these steps exactly.

## Step 1: Detect Time & Infer Mode
Run `date` to get the current time. Infer the likely context:
- Before 1:00 PM --> `morning-shop` (CVHS teaching)
- 1:00 PM to 4:00 PM --> transition window (could be any mode)
- After 4:00 PM --> `afternoon-family` or `deep-work`

## Step 2: Initialize Run Log
Run `bash .claude/scripts/run-log-init.sh` to create today's run-log from template.
Read the output to confirm creation or existence.

## Step 3: Check Yesterday's Carryover
Find the most recent previous run-log in `logs/`. If one exists, read it and extract:
- Any incomplete tasks
- Any items flagged for follow-up
List these as "Carryover Items" in today's run-log.

## Step 4: Check Morning Briefing
If `memory/morning_briefing.md` exists, read and display it. This was prepared by
the Night Shift script overnight.

## Step 5: Confirm Mode & Hard Stops
Present to the user:
```
SESSION BOOT
------------
Detected time: [HH:MM]
Inferred mode: [morning-shop / afternoon-family / deep-work]

Default hard stops:
  - Leave shop: 2:45 PM
  - Relieve childcare: 3:15 PM

Carryover: [N items from yesterday]
```

Ask: "Confirm mode and hard stops, or override?"

## Step 6: Schedule Transition Alerts
Once mode is confirmed, if there are hard stops applicable to the current mode:
- Log the hard stops in today's run-log under the `## Mode` section.
- On macOS, run `.claude/scripts/schedule_shift.sh` for each hard stop.
- On other platforms, log the schedule to the run-log for manual reference.

## Step 7: Activate Context
- Update today's run-log with session start time, confirmed mode, and hard stops.
- Report: "EEF active. Mode: [mode]. Next hard stop: [time] ([context])."
