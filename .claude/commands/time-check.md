# /time-check -- On-Demand Time & Energy Status

You are executing an EEF time and energy status check.

## Step 1: Current Time
Run `date` to get the current time.

## Step 2: Session Duration
Read today's run-log at `logs/run-log-YYYY-MM-DD.md` (use today's date).
Find the session start time. Calculate elapsed time since session start.

## Step 3: Hard Stop Countdown
Read the hard stops from the run-log's `## Mode` section. Calculate time
remaining to each hard stop.

## Step 4: Energy Assessment
- If elapsed session time > 90 minutes and mode is `deep-work`:
  "ENERGY WARNING: You have been in deep work for [N] minutes. Take a break NOW."
- If elapsed session time > 60 minutes:
  "Energy note: [N] minutes in. Consider a stretch or water break."
- Otherwise: report elapsed time only.

## Step 5: Report
Format the status as a compact block:

```
TIME CHECK
----------
Now:          [HH:MM]
Mode:         [current mode]
Session:      [elapsed] minutes
Next stop:    [hard stop context] in [remaining] minutes ([HH:MM])
Energy:       [green/yellow/red based on elapsed time]
```

Do not add commentary. Just the status block.
