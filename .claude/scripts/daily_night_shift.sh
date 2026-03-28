#!/bin/bash
# daily_night_shift.sh -- Autonomous memory sorting and morning prep.
# Designed to run via cron at 2:00 AM on the Mac deployment.
#
# Cron entry: 0 2 * * * ~/.claude/scripts/daily_night_shift.sh
# Requires: Claude CLI (`claude` command available in PATH)

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT" || exit 1

TODAY=$(date +%Y-%m-%d)
TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)

claude -p "
Execute the Night Shift Protocol. Adhere strictly to CLAUDE.md rules.

1. INTAKE: Read all files in logs/capture-*.md where today's dispatches were routed.

2. ROUTE: Move actionable items to the correct memory directories:
   - School/shop items to memory/cvhs/active_curriculum.md
   - Consulting/LLC items to memory/llc/active_projects.md
   - Family/personal items to memory/dad/boys_routines.md or memory/dad/stacie_sync.md

3. COMPRESS: Read logs/run-log-${TODAY}.md. Summarize the day into 3 bullet points.
   Append the summary to memory/archive/${TODAY}-summary.md.

4. PREP: Create or overwrite memory/morning_briefing.md for tomorrow (${TOMORROW}).
   Structure:
   - First line: the date and day of week
   - CVHS: The first priority teaching task
   - LLC: The first priority consulting task
   - Family: Any schedule notes for James, John, or Stacie
   - Energy note: If yesterday was high-output, recommend a lighter start

5. FLUSH: Clear the contents of all logs/capture-*.md files (leave the files, empty the content).

6. Log all actions taken to logs/run-log-${TODAY}.md under a '## Night Shift' heading.
"
