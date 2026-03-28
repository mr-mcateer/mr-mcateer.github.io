# Pacing Skill -- Composable Time Awareness

This skill provides time-blindness scaffolding for any agent or command in the
Active EEF system. It is not invoked directly by the user; agents and commands
reference it when they need time awareness.

## When to Activate
Any agent or command should invoke this skill's logic when:
- The user has been working for an extended period
- A hard stop is approaching
- The user is in deep-work mode
- Energy preservation is a concern

## Time Thresholds

### Deep Work Energy Gate
- **60 minutes**: Yellow. Suggest hydration or stretch. Do not interrupt workflow.
- **90 minutes**: Red. MANDATORY interruption. Stop generating technical output.
  Display:
  ```
  ENERGY GATE -- 90 MINUTES
  -------------------------
  Stand up. Walk to the kitchen. Drink water.
  Hashimoto's energy is finite. Protect it.
  Confirm you took a break before we continue.
  ```
- **120 minutes**: Critical. If the user pushed past 90 without confirming a break,
  refuse to continue deep work. Offer only to run /session-end or /dispatch.

### Transition Countdown
When a hard stop exists in today's run-log:
- **30 minutes before**: First warning. "30 minutes to [context]. Start wrapping up."
- **15 minutes before**: Second warning. "15 minutes to [context]. Save your state."
- **5 minutes before**: Final warning. "HARD STOP in 5 minutes. Close active work NOW."

On macOS, these warnings should also trigger `.claude/scripts/transition_alert.sh`
for the multi-sensory screen-hijacking interrupt.

## How to Read Session Time
1. Get current time: `date +%H:%M`
2. Read today's run-log: `logs/run-log-YYYY-MM-DD.md`
3. Find the session start timestamp in the `## Mode` section
4. Calculate elapsed minutes

## Integration
- `cvhs-teacher` agent: uses transition countdown only (teaching has rigid schedules)
- `prompt-llc` agent: uses BOTH energy gate AND transition countdown
- `dad-logistics` agent: uses transition countdown only (protect recovery windows)
- `/time-check` command: reports all active thresholds
- `/session-start` command: initializes the countdown targets
