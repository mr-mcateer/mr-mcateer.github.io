---
name: daily-briefing
description: Pull grades, schedules, and agendas to generate a daily teaching briefing
user_invocable: true
command: daily-briefing
---

# Daily Briefing Skill

Generates a comprehensive daily teaching briefing by pulling live data from Canvas, Google Sites schedules, and Google Calendar, then compiling everything into an Apple Note.

## When to activate
- User invokes `/daily-briefing`
- User asks to "plan for tomorrow", "pull grades", "build a briefing"
- Sunday night or early morning before school

## Inputs
- Target date (default: next teaching day)
- Optional: `--cached` to skip Canvas API pull and reuse last snapshot

## Workflow

### Step 1: Determine Target Date and Schedule
Run `python3 canvas-agent-grader/countdown.py` to get:
- Day type (ALL / ODD / EARLY_ODD)
- Period minutes (P1, P3, P5)
- Teaching days remaining
- Semester progress

Check Google Calendar for the target date for meetings and events.

### Step 2: Pull Curriculum from Google Sites
Fetch current schedules using WebFetch:
- Autos: `https://sites.google.com/corvallis.k12.or.us/mcateermetals/autos-schedule`
- Metals: `https://sites.google.com/corvallis.k12.or.us/mcateermetals/metals-schedule`

Extract the most recent agenda entries to understand current unit focus and active projects.

### Step 3: Pull Fresh Gradebook Data
```bash
cd canvas-agent-grader
python3 gradebook_audit.py          # -> exports/gradebook_snapshot.json
python3 detailed_audit.py           # -> exports/detailed_audit.json
```

### Step 4: Analyze Grades
From the snapshot, extract per course:
- Enrollment count and average score
- At-risk students (3+ missing OR score < 60%)
- High performers (90%+)
- Ungraded submissions with student names and assignment details
- Cross-roster students (enrolled in multiple courses)

### Step 5: Screenshot SpeedGrader (Optional)
For each ungraded submission with actual content, open SpeedGrader in Chrome:
```
https://csd509j.instructure.com/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&student_id={user_id}
```
Capture and save screenshots for reference.

### Step 6: Build Agendas
Create period-specific agendas following this format:
- DAILY JOURNAL: thought-provoking question related to current unit
- TODAY'S PRIORITIES: numbered list of activities
- EXPECTATIONS: behavioral reminders appropriate to shop setting

Agenda content should reflect:
- Current projects from Google Sites schedule
- Grading queue items students may need to address
- Upcoming deadlines or schedule changes

### Step 7: Compile Apple Note
Create an Apple Note titled "Daily Briefing -- {Day} {Date}" with sections:
1. Schedule (day type, period times, meetings)
2. Dashboard (total students, averages, at-risk count, ungraded count)
3. Per-course roster with scores and grading queue
4. Period agendas (P1 Autos, P3 Metals, P5 Metals)
5. At-risk roster (all students below 60%)
6. Action items checklist
7. Cross-roster students

## Key Data Sources
- Canvas API: `csd509j.instructure.com` (token in .env)
- Google Sites: `sites.google.com/corvallis.k12.or.us/mcateermetals/`
- Google Calendar: via gcal MCP tools
- Schedule config: `canvas-agent-grader/countdown.py`

## Course IDs
- P3 Metals 1: 23164
- P3 Metals 2: 23132
- P3 Metals 3: 23157
- P5 Metals 1: 23188
- P5 Metals 2: 23177
- P1 Engines Fab 1: 23124
- P1 Engines Fab 2: 23344

## Style Rules
- No em-dashes. Use -- instead.
- Plain text formatting suitable for Apple Notes
- Direct, shop-teacher tone for agendas
- Flag at-risk students prominently with ** markers
- Include actionable items as [ ] checkboxes
