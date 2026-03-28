#!/bin/bash
# sunday_reset.sh -- Weekly deep-prune and bottleneck detection.
# Designed to run via cron on Sundays at 3:00 AM on the Mac deployment.
#
# Cron entry: 0 3 * * 0 ~/.claude/scripts/sunday_reset.sh
# Requires: Claude CLI, mcp-ical (for calendar reads on Mac)

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT" || exit 1

WEEK_START=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)

claude -p "
Execute the Sunday Reset Protocol. Adhere strictly to CLAUDE.md rules.

1. ARCHIVE: Scan all memory directories (memory/cvhs/, memory/llc/, memory/dad/).
   Move any completed items (finished lessons, paid invoices, resolved logistics)
   to memory/archive/ with today's date prefix.

2. CONTEXT PRUNE: Ensure no active .md file in memory/ exceeds 500 words.
   If a file is over 500 words, compress it: keep only active/pending items,
   move completed items to archive.

3. BOTTLENECK AUDIT: If mcp-ical is available, read Apple Calendar for the
   upcoming week starting ${WEEK_START}. Cross-reference:
   - CVHS teaching blocks
   - LLC deadlines
   - Stacie's schedule and childcare handoffs
   If mcp-ical is not available, read memory/dad/stacie_sync.md and
   memory/cvhs/active_curriculum.md for manual schedule data.

4. ALERT: If you detect a high-friction day (back-to-back shop classes followed
   immediately by solo Dad shift with no recovery time), flag it at the very top
   of memory/morning_briefing.md with a proposed mitigation strategy.

5. WEEKLY STATS: Append to memory/archive/weekly-stats.md:
   - Total dispatches processed this week
   - Total deep work sessions
   - Any recurring bottlenecks

6. Log all actions to the Sunday run-log.
"
