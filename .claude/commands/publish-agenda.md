# /publish-agenda -- Asynchronous Curriculum Pipeline

You are executing the curriculum auto-publish pipeline. This command translates
a raw teaching idea into a structured Canvas agenda and pushes it as a DRAFT.

The user shifts from CREATING the agenda to merely APPROVING it.

## Input
The user provides a raw, unstructured teaching idea. Examples:
- "Tomorrow for Autos 101, brake pad replacement. Safety check on caliper pins.
   Include that YouTube video. 3-question exit ticket on fluid types."
- "Metals shop: intro to MIG welding. Demo first, then supervised practice.
   Safety focus on UV exposure and fume ventilation."

## Step 1: Structure the Agenda
Parse the raw input into a structured agenda. Fill in reasonable defaults for
anything not specified. Use your knowledge of CTE pedagogy.

Create a JSON object:
```json
{
    "title": "Brake Pad Replacement",
    "course_name": "Autos 101",
    "date": "YYYY-MM-DD",
    "objective": "Clear, measurable learning objective",
    "safety_focus": "The specific safety emphasis for this lesson",
    "materials": ["Item 1", "Item 2"],
    "procedure": ["Step 1", "Step 2", "Step 3"],
    "media": [{"label": "Demo Video", "url": "https://..."}],
    "notes": "Any additional teacher context"
}
```

If the user mentioned a video but did not provide a URL, note it as
`{"label": "Video TBD", "url": "#"}` so it shows up in the draft for manual linking.

## Step 2: Structure the Exit Ticket (if requested)
If the user mentioned an exit ticket, quiz, or check-for-understanding, create:
```json
{
    "title": "Topic Name",
    "questions": ["Question 1?", "Question 2?", "Question 3?"],
    "points": 10
}
```

Generate pedagogically sound questions that check comprehension, not trivia.
Use the humanizer skill tone: direct, second-person, CTE-appropriate language.

## Step 3: Write JSON Files
Save the structured data to temporary JSON files:
- Agenda: `/tmp/agenda-YYYY-MM-DD.json`
- Exit ticket: `/tmp/exit-ticket-YYYY-MM-DD.json`

## Step 4: Push to Canvas as Draft
Run the publisher script for each item:
```bash
cd canvas-agent-grader
python canvas_publisher.py agenda --course COURSE_ID --date YYYY-MM-DD --json /tmp/agenda-YYYY-MM-DD.json
python canvas_publisher.py exit-ticket --course COURSE_ID --date YYYY-MM-DD --json /tmp/exit-ticket-YYYY-MM-DD.json
```

IMPORTANT: The `--course` flag requires a Canvas Course ID. Check
`memory/cvhs/active_curriculum.md` for stored course IDs. If no course ID
is found, ask the user for it ONCE and store it in `memory/cvhs/active_curriculum.md`
for future use.

ALL content is pushed as UNPUBLISHED DRAFT. The user reviews and clicks Publish
in Canvas when ready. This is a safety guardrail -- never auto-publish.

## Step 5: Confirm
Report:
```
CURRICULUM PIPELINE COMPLETE
-----------------------------
Agenda:      [title] --> Canvas DRAFT page
Exit Ticket: [title] --> Canvas DRAFT assignment (N pts)
Course:      [course name] (ID: XXXX)

Review and publish in Canvas when ready.
```

## Step 6: Log
Append to today's run-log under `## Captures`:
- "Curriculum: [title] pushed to Canvas as draft for [date]"

Update `memory/cvhs/active_curriculum.md` with the new lesson entry.
