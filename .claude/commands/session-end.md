# /session-end -- EEF Wrap-Up Protocol

You are executing the Active EEF session wrap-up. Follow these steps exactly.

## Step 1: Capture Session Changes
Run `git diff --stat` and `git status` to see all file changes made this session.
Summarize what was created, modified, or deleted.

## Step 2: Identify Open Threads
Review the conversation history for this session. List:
- Any tasks that were started but not completed
- Any decisions that need follow-up
- Any items the user mentioned but did not act on

## Step 3: Update Memory Files
For each domain touched during this session, update the relevant memory file:
- School items --> `memory/cvhs/active_curriculum.md`
- LLC items --> `memory/llc/active_projects.md`
- Family items --> `memory/dad/boys_routines.md` or `memory/dad/stacie_sync.md`

Only update files that were actually relevant to this session's work.

## Step 4: Write Run-Log Summary
Append to today's `logs/run-log-YYYY-MM-DD.md` under `## End-of-Day Summary`:
- Mode used
- Duration (session start to now)
- 3-5 bullet points of what was accomplished
- Open threads carried forward
- Energy assessment (high-output session? suggest lighter start tomorrow?)

## Step 5: Transition Reminder
Check the current time against hard stops:
- If a hard stop is approaching within 30 minutes, trigger a transition warning.
- If the user is in morning-shop mode, remind about afternoon transition.
- If the user is in deep-work mode, remind about the 90-minute energy rule.

## Step 6: Confirm Flush
Report the summary to the user, then state:
"Session logged. Context can be released. Next session starts clean."
