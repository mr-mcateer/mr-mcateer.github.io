#!/usr/bin/env python3
"""
Canvas deployment for March 30-31, 2026.

March 30 (sub day): "If I Had $5,000" assignment + announcement for Autos
March 31 (return):  Knee mill quiz + announcement for Metals

Usage:
    python deploy_march30.py              # dry-run
    python deploy_march30.py --execute    # push to Canvas
"""
import sys
import time
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from canvas_api import (
    CANVAS_API_URL,
    create_assignment,
    create_rubric,
    create_quiz,
    create_quiz_question,
    create_announcement,
)

DRY_RUN = "--execute" not in sys.argv

AUTOS_COURSES = {
    23124: "P1 Engines Fab 1",
    23344: "P1 Engines Fab 2",
}

METALS_COURSES = {
    23164: "P3 Metals 1",
    23132: "P3 Metals 2",
    23157: "P3 Metals 3",
    23188: "P5 Metals 1",
    23177: "P5 Metals 2",
}

# Track created IDs for linking announcements
created = {}  # {course_id: {"assignment_id": N} or {"quiz_id": N}}


# ======================================================================
# CONTENT: Autos "If I Had $5,000" Assignment
# ======================================================================

ASSIGNMENT_NAME = "If I Had $5,000 Build Sheet"

ASSIGNMENT_DESCRIPTION = """<h2>Automotive Manufacturing -- 10 pts -- Due end of period -- Submit on Canvas</h2>

<p>Someone hands you $5,000 and says: "Spend it on your vehicle." Pick a vehicle you own, drive,
or want to own. Research real parts at real prices from real websites. Show what you'd buy,
where you'd buy it, and why in that order.</p>

<h3>1. Your Vehicle (1 pt)</h3>
<ul>
  <li>Year / Make / Model / Trim</li>
  <li>Why this one?</li>
  <li>What's wrong with it?</li>
</ul>

<h3>2. Your Build List (3 pts)</h3>
<p>Minimum 5 mods. List them in priority order: safety &rarr; reliability &rarr; performance &rarr; appearance.</p>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><th>#</th><th>Modification</th><th>Exact Part</th><th>Website</th><th>Price</th><th>Why This Before the Next?</th></tr>
  <tr><td>1</td><td></td><td></td><td></td><td></td><td></td></tr>
  <tr><td>2</td><td></td><td></td><td></td><td></td><td></td></tr>
  <tr><td>3</td><td></td><td></td><td></td><td></td><td></td></tr>
  <tr><td>4</td><td></td><td></td><td></td><td></td><td></td></tr>
  <tr><td>5</td><td></td><td></td><td></td><td></td><td></td></tr>
  <tr><td>6</td><td></td><td></td><td></td><td></td><td></td></tr>
  <tr><td>7</td><td></td><td></td><td></td><td></td><td></td></tr>
  <tr><td>8</td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
<p><strong>TOTAL: $__________ / $5,000</strong><br>Under budget is smart. Over budget is a redo.</p>

<h4>Where to Find Parts</h4>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><th>Website</th><th>Best For</th><th>Search Tip</th><th>What to Write Down</th></tr>
  <tr><td>RockAuto.com</td><td>OEM &amp; replacement parts</td><td>Select your vehicle from the dropdown, then browse by category</td><td>Brand + part number + price</td></tr>
  <tr><td>SummitRacing.com</td><td>Performance parts</td><td>Search "[part] [your vehicle]" then filter by "Shop By Vehicle"</td><td>Brand + product name + part number + price</td></tr>
  <tr><td>FitmentIndustries.com</td><td>Wheels &amp; tires</td><td>Click "Gallery," search your vehicle, find a setup you like, then price it in "Shop"</td><td>Wheel brand + size + offset + tire size + package price</td></tr>
  <tr><td>Car-Part.com</td><td>Used/junkyard parts</td><td>Select vehicle, select part, shows real junkyard prices nationwide</td><td>Part + yard name + price</td></tr>
  <tr><td>FB Marketplace</td><td>Used parts from other builds</td><td>Search part + vehicle, filter by distance. Screenshot the listing.</td><td>Part + price + screenshot</td></tr>
</table>

<h3>3. Build Goal (1.5 pts)</h3>
<p>2-3 sentences. What kind of build is this and why does your priority order reflect that?</p>

<h3>4. The Trade-Off (1.5 pts)</h3>
<p>Every real build hits a wall. Answer these three:</p>
<ul>
  <li>What did you want but couldn't fit in the budget?</li>
  <li>What would you have had to cut to afford it?</li>
  <li>Why did you keep what you kept?</li>
</ul>

<h3>Grading</h3>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><th>Criteria</th><th>Pts</th><th>Full Credit Means...</th></tr>
  <tr><td>Vehicle with honest rationale</td><td>1</td><td>Specific vehicle + real reason</td></tr>
  <tr><td>5+ real parts, real prices, real vendors</td><td>3</td><td>I can find every part at that price online</td></tr>
  <tr><td>Priority order is logical</td><td>2</td><td>Safety &rarr; reliability &rarr; performance &rarr; looks</td></tr>
  <tr><td>Build goal matches your choices</td><td>1.5</td><td>Your list tells the same story your goal does</td></tr>
  <tr><td>Trade-off shows real thinking</td><td>1.5</td><td>All 3 questions answered with reasoning</td></tr>
  <tr><td>Budget &le; $5,000</td><td>1</td><td>Math adds up</td></tr>
  <tr><td><strong>TOTAL</strong></td><td><strong>10</strong></td><td></td></tr>
</table>

<p><strong>See the exemplar for what a finished build sheet looks like. Submit on Canvas before you leave.</strong></p>
"""

ASSIGNMENT_RUBRIC_CRITERIA = [
    {
        "description": "Vehicle with honest rationale",
        "points": 1.0,
        "ratings": [
            {"description": "Specific vehicle + real reason for choosing it", "points": 1.0},
            {"description": "Vague choice or no real reason given", "points": 0.5},
            {"description": "No vehicle selected", "points": 0.0},
        ]
    },
    {
        "description": "5+ real parts, real prices, real vendors",
        "points": 3.0,
        "ratings": [
            {"description": "5+ mods with exact parts, real prices, real vendor links", "points": 3.0},
            {"description": "3-4 mods or some prices/vendors missing", "points": 2.0},
            {"description": "1-2 mods or mostly vague/made-up prices", "points": 1.0},
            {"description": "No build list or entirely fictional", "points": 0.0},
        ]
    },
    {
        "description": "Priority order is logical",
        "points": 2.0,
        "ratings": [
            {"description": "Safety > reliability > performance > looks", "points": 2.0},
            {"description": "Mostly logical with minor ordering issues", "points": 1.0},
            {"description": "No logical order or all cosmetic first", "points": 0.0},
        ]
    },
    {
        "description": "Build goal matches your choices",
        "points": 1.5,
        "ratings": [
            {"description": "Goal clearly reflects the build list story", "points": 1.5},
            {"description": "Goal is vague or disconnected from list", "points": 0.75},
            {"description": "No build goal written", "points": 0.0},
        ]
    },
    {
        "description": "Trade-off shows real thinking",
        "points": 1.5,
        "ratings": [
            {"description": "All 3 trade-off questions answered with reasoning", "points": 1.5},
            {"description": "1-2 questions answered or shallow reasoning", "points": 0.75},
            {"description": "No trade-off section", "points": 0.0},
        ]
    },
    {
        "description": "Budget is at or under $5,000",
        "points": 1.0,
        "ratings": [
            {"description": "Math adds up and total is at or under $5,000", "points": 1.0},
            {"description": "Over budget or math doesn't add up", "points": 0.0},
        ]
    },
]


# ======================================================================
# CONTENT: Metals Knee Mill Quiz
# ======================================================================

QUIZ_TITLE = "Knee Mill Operation Quiz"
QUIZ_DESCRIPTION = (
    "<p>10 questions on knee mill safety, operation, and terminology. "
    "If you watched the spring break video and paid attention in the shop, "
    "this should be straightforward.</p>"
)

QUIZ_QUESTIONS = [
    # --- Multiple Choice (7) ---
    {
        "question_name": "Q1 - Pre-start check",
        "question_text": "What is the FIRST thing you should check before turning on a knee mill?",
        "question_type": "multiple_choice_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "The workpiece is secure in the vise", "answer_weight": 100},
            {"answer_text": "The spindle speed is set to maximum", "answer_weight": 0},
            {"answer_text": "The coolant reservoir is full", "answer_weight": 0},
            {"answer_text": "The table is at its lowest position", "answer_weight": 0},
        ]
    },
    {
        "question_name": "Q2 - Quill axis",
        "question_text": "The quill on a knee mill controls movement in which direction?",
        "question_type": "multiple_choice_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "Up and down (Z axis)", "answer_weight": 100},
            {"answer_text": "Left and right (X axis)", "answer_weight": 0},
            {"answer_text": "Front and back (Y axis)", "answer_weight": 0},
            {"answer_text": "It rotates the spindle", "answer_weight": 0},
        ]
    },
    {
        "question_name": "Q3 - Common cutter",
        "question_text": "What is the most common type of cutter used for face milling on a knee mill?",
        "question_type": "multiple_choice_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "End mill", "answer_weight": 100},
            {"answer_text": "Twist drill bit", "answer_weight": 0},
            {"answer_text": "Lathe tool bit", "answer_weight": 0},
            {"answer_text": "Bandsaw blade", "answer_weight": 0},
        ]
    },
    {
        "question_name": "Q4 - Tool change safety",
        "question_text": "Before changing a tool in the spindle, you must:",
        "question_type": "multiple_choice_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "Lock the spindle and disconnect power", "answer_weight": 100},
            {"answer_text": "Set the spindle to its lowest speed", "answer_weight": 0},
            {"answer_text": "Remove the vise from the table", "answer_weight": 0},
            {"answer_text": "Turn on the coolant pump", "answer_weight": 0},
        ]
    },
    {
        "question_name": "Q5 - Feed direction",
        "question_text": "When conventional milling on a manual knee mill, the feed direction should be:",
        "question_type": "multiple_choice_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "Against the rotation of the cutter", "answer_weight": 100},
            {"answer_text": "With the rotation of the cutter (climb milling)", "answer_weight": 0},
            {"answer_text": "It does not matter on a manual mill", "answer_weight": 0},
            {"answer_text": "Perpendicular to the cutter rotation", "answer_weight": 0},
        ]
    },
    {
        "question_name": "Q6 - What the knee does",
        "question_text": "On a knee mill, the 'knee' moves:",
        "question_type": "multiple_choice_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "The entire table assembly up and down", "answer_weight": 100},
            {"answer_text": "The spindle left and right", "answer_weight": 0},
            {"answer_text": "The quill forward and back", "answer_weight": 0},
            {"answer_text": "The motor housing", "answer_weight": 0},
        ]
    },
    {
        "question_name": "Q7 - Chatter fix",
        "question_text": "If your end mill starts chattering during a cut, you should:",
        "question_type": "multiple_choice_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "Reduce feed rate and/or depth of cut", "answer_weight": 100},
            {"answer_text": "Increase spindle speed to maximum", "answer_weight": 0},
            {"answer_text": "Push harder to force through the material", "answer_weight": 0},
            {"answer_text": "Switch to a larger end mill immediately", "answer_weight": 0},
        ]
    },
    # --- Short Answer (3) ---
    {
        "question_name": "Q8 - PPE",
        "question_text": (
            "Name TWO pieces of personal protective equipment (PPE) "
            "required when operating the knee mill."
        ),
        "question_type": "short_answer_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "safety glasses", "answer_weight": 100},
            {"answer_text": "hearing protection", "answer_weight": 100},
            {"answer_text": "closed-toe shoes", "answer_weight": 100},
            {"answer_text": "safety goggles", "answer_weight": 100},
            {"answer_text": "ear protection", "answer_weight": 100},
        ]
    },
    {
        "question_name": "Q9 - Chuck key safety",
        "question_text": "Why should you NEVER leave a chuck key in the collet or drill chuck?",
        "question_type": "short_answer_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "It will fly out when the spindle starts", "answer_weight": 100},
            {"answer_text": "It can become a projectile", "answer_weight": 100},
        ]
    },
    {
        "question_name": "Q10 - Cutting fluid",
        "question_text": "What is the purpose of using cutting fluid when milling steel?",
        "question_type": "short_answer_question",
        "points_possible": 2,
        "answers": [
            {"answer_text": "Reduces heat and friction", "answer_weight": 100},
            {"answer_text": "Extends tool life", "answer_weight": 100},
            {"answer_text": "Improves surface finish", "answer_weight": 100},
        ]
    },
]


# ======================================================================
# CONTENT: Announcements / Agendas
# ======================================================================

def autos_announcement_html(assignment_url):
    return f"""<h2>AUTOMOTIVE MANUFACTURING | 03.30.2026</h2>
<p><strong>Sub Day</strong> -- Mr. McAteer will be back tomorrow.</p>

<h3>TODAY'S ASSIGNMENT: If I Had $5,000 Build Sheet</h3>
<p><a href="{assignment_url}">Click here to open the assignment</a></p>

<p>Someone hands you $5,000. Spec out a real build on a real vehicle
using real parts at real prices.</p>

<ul>
  <li>See the exemplar on Canvas or printed on Mr. McAteer's desk</li>
  <li>Use Chromebooks or your phone for research</li>
  <li>Submit on Canvas before end of period</li>
  <li>No YouTube unless it's a build video for YOUR vehicle</li>
</ul>

<p><strong>If you finish early:</strong> second build on a different platform,
review Canvas feedback, or update your portfolio. No free browsing.</p>

<p><strong>TOMORROW:</strong> Oil changes and brake labs. Come ready to work.</p>
"""


def metals_announcement_html(quiz_url):
    return f"""<h2>METALS &amp; FABRICATION | 03.31.2026</h2>
<p>Welcome back from spring break.</p>

<h3>BELL WORK: Knee Mill Operation Quiz</h3>
<p><a href="{quiz_url}">Click here to take the quiz</a></p>

<h3>TODAY'S FOCUS: Knee mill proficiency</h3>
<p>If you watched the video over break, this quiz will be straightforward.
If you didn't -- now you know why we assigned it.</p>

<p><strong>After the quiz:</strong></p>
<ul>
  <li>Mill demo with Bob</li>
  <li>Shop time on your project</li>
  <li>If you haven't run the Haas yet, today is the day</li>
</ul>

<h3>Shop Expectations</h3>
<ul>
  <li>Bob is in the shop. Use him. Ask questions.</li>
  <li>Clean your station before you leave. Leave it better than you found it.</li>
</ul>

<p><strong>EXIT TICKET:</strong> Before you leave, check in with Mr. McAteer:
What did you work on today? What's your plan for next class?</p>
"""


# ======================================================================
# DEPLOYMENT FUNCTIONS
# ======================================================================

def deploy_autos_assignment():
    """Create the If I Had $5,000 assignment + rubric in both Autos courses."""
    print("\n--- Autos: If I Had $5,000 Assignment ---\n")

    for cid, name in AUTOS_COURSES.items():
        tag = f"[{name} ({cid})]"

        params = {
            "name": ASSIGNMENT_NAME,
            "description": ASSIGNMENT_DESCRIPTION,
            "points_possible": 10,
            "submission_types": ["online_text_entry", "online_upload"],
            "published": False,
            "grading_type": "points",
        }

        if DRY_RUN:
            print(f"[DRY RUN] {tag} CREATE assignment: {ASSIGNMENT_NAME} (10 pts)")
            print(f"           submission_types: online_text_entry, online_upload")
            print(f"           published: False")
            created[cid] = {"assignment_id": 999999}  # placeholder
        else:
            result = create_assignment(cid, params)
            aid = result["id"]
            created[cid] = {"assignment_id": aid}
            print(f"[CREATED] {tag} assignment ID {aid}: {ASSIGNMENT_NAME}")
            time.sleep(0.15)

        # Attach rubric
        if DRY_RUN:
            print(f"[DRY RUN] {tag} ATTACH rubric: 6 criteria, 10 pts total")
            for c in ASSIGNMENT_RUBRIC_CRITERIA:
                print(f"           - {c['description']} ({c['points']} pts)")
        else:
            try:
                rubric_result = create_rubric(
                    cid, aid, "If I Had $5,000 Rubric", ASSIGNMENT_RUBRIC_CRITERIA
                )
                print(f"[CREATED] {tag} rubric attached (ID {rubric_result.get('rubric', {}).get('id', '?')})")
            except Exception as e:
                print(f"[WARNING] {tag} rubric creation failed: {e}")
                print(f"           Assignment still created. Add rubric manually in Canvas.")
            time.sleep(0.15)

        print()


def deploy_metals_quiz():
    """Create the Knee Mill quiz + 10 questions in all Metals courses."""
    print("\n--- Metals: Knee Mill Operation Quiz ---\n")

    for cid, name in METALS_COURSES.items():
        tag = f"[{name} ({cid})]"

        quiz_params = {
            "title": QUIZ_TITLE,
            "description": QUIZ_DESCRIPTION,
            "quiz_type": "assignment",
            "allowed_attempts": 1,
            "scoring_policy": "keep_highest",
            "published": False,
            "show_correct_answers": True,
            "show_correct_answers_last_attempt": True,
        }

        if DRY_RUN:
            print(f"[DRY RUN] {tag} CREATE quiz: {QUIZ_TITLE}")
            print(f"           1 attempt, unpublished, show answers after last attempt")
            quiz_id = 999999
            created[cid] = {"quiz_id": quiz_id}
        else:
            result = create_quiz(cid, quiz_params)
            quiz_id = result["id"]
            created[cid] = {"quiz_id": quiz_id}
            print(f"[CREATED] {tag} quiz ID {quiz_id}: {QUIZ_TITLE}")
            time.sleep(0.15)

        # Add questions
        for i, q in enumerate(QUIZ_QUESTIONS, 1):
            if DRY_RUN:
                qtype = "MC" if q["question_type"] == "multiple_choice_question" else "SA"
                print(f"[DRY RUN] {tag}   Q{i} ({qtype}, {q['points_possible']} pts): {q['question_name']}")
            else:
                create_quiz_question(cid, quiz_id, q)
                print(f"[CREATED] {tag}   Q{i}: {q['question_name']}")
                time.sleep(0.15)

        print()


def deploy_announcements():
    """Post announcements with agendas to all courses."""
    print("\n--- Announcements ---\n")

    # Autos announcements
    for cid, name in AUTOS_COURSES.items():
        tag = f"[{name} ({cid})]"
        aid = created.get(cid, {}).get("assignment_id")

        if aid and aid != 999999:
            url = f"{CANVAS_API_URL}/courses/{cid}/assignments/{aid}"
        else:
            url = "[assignment link -- will be populated on execute]"

        title = "Welcome Back! Today's Assignment: If I Had $5,000"
        html = autos_announcement_html(url)

        # Schedule for Monday 7 AM Pacific
        delay = "2026-03-30T07:00:00-07:00"

        if DRY_RUN:
            print(f"[DRY RUN] {tag} CREATE announcement: {title}")
            print(f"           Links to: {url}")
            print(f"           Scheduled: {delay}")
        else:
            create_announcement(cid, title, html, delayed_post_at=delay)
            print(f"[CREATED] {tag} announcement: {title} (scheduled {delay})")
            time.sleep(0.15)

    # Metals announcements
    for cid, name in METALS_COURSES.items():
        tag = f"[{name} ({cid})]"
        qid = created.get(cid, {}).get("quiz_id")

        if qid and qid != 999999:
            url = f"{CANVAS_API_URL}/courses/{cid}/quizzes/{qid}"
        else:
            url = "[quiz link -- will be populated on execute]"

        title = "Welcome Back -- Knee Mill Focus This Week"
        html = metals_announcement_html(url)

        # Schedule for Tuesday 7 AM Pacific
        delay = "2026-03-31T07:00:00-07:00"

        if DRY_RUN:
            print(f"[DRY RUN] {tag} CREATE announcement: {title}")
            print(f"           Links to: {url}")
            print(f"           Scheduled: {delay}")
        else:
            create_announcement(cid, title, html, delayed_post_at=delay)
            print(f"[CREATED] {tag} announcement: {title} (scheduled {delay})")
            time.sleep(0.15)

    print()


# ======================================================================
# MAIN
# ======================================================================

def run():
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    print(f"\n{'='*60}")
    print(f"  Canvas March 30-31 Deployment  [{mode}]")
    print(f"{'='*60}")
    print(f"  Autos courses:  {list(AUTOS_COURSES.values())}")
    print(f"  Metals courses: {list(METALS_COURSES.values())}")
    print(f"{'='*60}")

    deploy_autos_assignment()
    deploy_metals_quiz()
    deploy_announcements()

    print(f"{'='*60}")
    print(f"  Done! [{mode}]")
    if DRY_RUN:
        print(f"  Re-run with --execute to push to Canvas.")
        print(f"  All items will be created UNPUBLISHED.")
        print(f"  Publish the assignment before Monday morning.")
        print(f"  Publish the quiz when ready Tuesday.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
