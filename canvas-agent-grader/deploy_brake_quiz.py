#!/usr/bin/env python3
"""
Canvas deployment: Brake Pads & Rotors Video Quiz (April 6, 2026).

Creates a 15-question auto-graded quiz based on the ChrisFix video:
  "How to Replace Brake Pads and Rotors"
  https://youtu.be/6RQ9UabOIPg?si=u9B5O_rQMPeLEEtl

Target courses: P1 Engines Fab 1 (23124), P1 Engines Fab 2 (23344)
Due: April 6, 2026 at 11:59 PM Pacific

Usage:
    python deploy_brake_quiz.py              # dry-run
    python deploy_brake_quiz.py --execute    # push to Canvas
"""
import sys
import time
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from canvas_api import (
    create_quiz,
    create_quiz_question,
    _make_request,
    _make_post_request,
)

DRY_RUN = "--execute" not in sys.argv

COURSES = {
    23124: "P1 Engines Fab 1",
    23344: "P1 Engines Fab 2",
}

VIDEO_URL = "https://youtu.be/6RQ9UabOIPg?si=u9B5O_rQMPeLEEtl"

QUIZ_PARAMS = {
    "title": "Brake Pads & Rotors Replacement -- Video Quiz",
    "description": (
        "<p><strong>Watch the full video before starting this quiz.</strong></p>"
        f'<p><a href="{VIDEO_URL}" target="_blank">'
        "ChrisFix -- How to Replace Brake Pads and Rotors</a></p>"
        "<p>15 multiple-choice questions, 1 point each. "
        "Auto-graded. One attempt. Due tonight at 11:59 PM.</p>"
    ),
    "quiz_type": "assignment",
    "assignment_group_id": None,  # filled per-course if needed
    "time_limit": None,
    "shuffle_answers": True,
    "allowed_attempts": 1,
    "scoring_policy": "keep_highest",
    "show_correct_answers": True,
    "show_correct_answers_last_attempt": True,
    "one_question_at_a_time": False,
    "published": False,  # create unpublished, add questions, then publish
    "due_at": "2026-04-07T06:59:00Z",  # 11:59 PM Pacific = 06:59 UTC next day
    "lock_at": "2026-04-07T06:59:00Z",
}

# ======================================================================
# QUESTIONS -- each is (question_text, [answers], correct_index)
# correct_index is 0-based position in the answers list
# ======================================================================

QUESTIONS = [
    {
        "name": "Q1: Before lifting the car",
        "text": "Before lifting the car, what should you do to the lug nuts?",
        "answers": [
            "Remove them completely",
            "Loosen (crack) them while the tires are still on the ground",
            "Tighten them to full torque",
            "Spray them with brake cleaner",
        ],
        "correct": 1,
    },
    {
        "name": "Q2: Wheel chock purpose",
        "text": "What is the purpose of using a wheel chock before jacking up the vehicle?",
        "answers": [
            "To mark the tire position for reinstallation",
            "To prevent the vehicle from rolling while lifted",
            "To protect the rim from scratches",
            "To keep the jack aligned",
        ],
        "correct": 1,
    },
    {
        "name": "Q3: Ceramic vs semi-metallic",
        "text": "Why does the video recommend ceramic brake pads over semi-metallic pads for street use?",
        "answers": [
            "Ceramic pads are cheaper",
            "Ceramic pads generate more stopping power",
            "Ceramic pads produce less dust and tend to last longer",
            "Ceramic pads do not require a break-in period",
        ],
        "correct": 2,
    },
    {
        "name": "Q4: Caliper piston tool",
        "text": "What specialized tool is required to push the caliper piston back into the caliper body?",
        "answers": [
            "Torque wrench",
            "Breaker bar",
            "Brake piston compressor",
            "Ball peen hammer",
        ],
        "correct": 2,
    },
    {
        "name": "Q5: Caliper placement",
        "text": "After removing the caliper from the bracket, where should you place it?",
        "answers": [
            "Set it on the ground next to the tire",
            "Let it hang by the brake line so it stays out of the way",
            "Support it so there is no pressure or strain on the brake line",
            "Remove the brake line and set the caliper on the fender",
        ],
        "correct": 2,
    },
    {
        "name": "Q6: Rust-welded rotor removal",
        "text": "What is the correct method for removing a rotor that is rust-welded to the hub?",
        "answers": [
            "Pry it off with a screwdriver behind the rotor fins",
            "Strike the outer edge of the rotor with a large hammer, rotating as you go",
            "Heat the hub with a torch until the rust releases",
            "Spray penetrating oil and wait 24 hours",
        ],
        "correct": 1,
    },
    {
        "name": "Q7: Cleaning the hub surface",
        "text": "Why should you clean the hub surface before installing the new rotor?",
        "answers": [
            "To remove paint so the rotor can bond permanently",
            "To create a smooth, flat mating surface so the rotor sits flush",
            "To allow the rotor to spin freely without contact",
            "To expose bare metal for the anti-seize compound",
        ],
        "correct": 1,
    },
    {
        "name": "Q8: New rotor protective film",
        "text": "New rotors ship with an oily protective film. How should you remove it before installation?",
        "answers": [
            "Wipe with a dry rag only",
            "Sand both surfaces with 80-grit sandpaper",
            "Spray both rotor surfaces with brake cleaner and wipe clean",
            "Soak the rotor in soapy water for 10 minutes",
        ],
        "correct": 2,
    },
    {
        "name": "Q9: Guide pin lubricant",
        "text": "What type of lubricant should be applied to the caliper guide pins?",
        "answers": [
            "Copper-based anti-seize",
            "White lithium grease",
            "Silicone paste",
            "Motor oil",
        ],
        "correct": 2,
    },
    {
        "name": "Q10: Petroleum-based lubricant issue",
        "text": "Why is petroleum-based lubricant inappropriate for caliper guide pins?",
        "answers": [
            "It attracts too much road dirt",
            "It degrades the rubber boots and seals on the caliper",
            "It has too low a melting point",
            "It reacts with the brake fluid chemically",
        ],
        "correct": 1,
    },
    {
        "name": "Q11: Anti-seize application",
        "text": "Where should copper anti-seize be applied during a brake job?",
        "answers": [
            "On the rotor friction surface",
            "On the lug nut threads",
            "On the caliper bracket contact points, brake hardware, and the back of the brake pads",
            "Inside the caliper piston bore",
        ],
        "correct": 2,
    },
    {
        "name": "Q12: Clean hands after anti-seize",
        "text": "Why is it critical to clean your hands (or change gloves) after applying anti-seize and before handling pads or rotors?",
        "answers": [
            "Anti-seize stains are permanent on skin",
            "Anti-seize on the pad surface or rotor can cause brake failure",
            "Anti-seize will corrode the pad backing plate",
            "Anti-seize prevents the burnishing compound from working",
        ],
        "correct": 1,
    },
    {
        "name": "Q13: Lug-nut tightening pattern",
        "text": "What is the correct lug-nut tightening pattern when reinstalling wheels?",
        "answers": [
            "Clockwise, one after the other",
            "Tighten opposite lugs in a star pattern",
            "Start with the top nut and work downward",
            "Hand-tight only until the first test drive",
        ],
        "correct": 1,
    },
    {
        "name": "Q14: Before driving after brake job",
        "text": "After the brake job is complete and the car is back on the ground, what must you do before driving?",
        "answers": [
            "Bleed the brake lines at each caliper",
            "Start the engine and pump the brake pedal several times until it feels firm",
            "Pour new brake fluid into the master cylinder reservoir",
            "Let the car idle for five minutes to warm the rotors",
        ],
        "correct": 1,
    },
    {
        "name": "Q15: Replacement sets",
        "text": "Brake pads and rotors should always be replaced in ___.",
        "answers": [
            "Singles -- only the side showing the most wear",
            "Sets of four -- all corners at the same time",
            "Pairs -- both sides of the same axle",
            "Whatever order the technician prefers",
        ],
        "correct": 2,
    },
]


# ======================================================================
# MODULE HELPERS
# ======================================================================

def get_modules(course_id):
    """List all modules in a course."""
    return _make_request(f"courses/{course_id}/modules", {"per_page": 100})


def create_module_item(course_id, module_id, item_type, content_id, title=None):
    """Add an item (quiz, assignment, etc.) to a module."""
    payload = {
        "module_item": {
            "type": item_type,
            "content_id": content_id,
        }
    }
    if title:
        payload["module_item"]["title"] = title
    return _make_post_request(
        f"courses/{course_id}/modules/{module_id}/items", payload
    )


def publish_quiz(course_id, quiz_id):
    """Publish a quiz by PUT-updating its published flag."""
    from canvas_api import _make_put_request
    return _make_put_request(
        f"courses/{course_id}/quizzes/{quiz_id}",
        {"quiz": {"published": True}},
    )


# ======================================================================
# DEPLOYMENT
# ======================================================================

def deploy_quiz(course_id, course_name):
    """Create the quiz, add questions, find module, publish."""
    tag = f"[{course_name} ({course_id})]"

    # --- 1. Create the quiz (unpublished) ---
    params = dict(QUIZ_PARAMS)
    if DRY_RUN:
        print(f"[DRY RUN] {tag} CREATE quiz: {params['title']}")
        print(f"           Due: {params['due_at']}")
        print(f"           Questions: {len(QUESTIONS)}")
        for i, q in enumerate(QUESTIONS, 1):
            correct_letter = chr(65 + q["correct"])
            print(f"           Q{i}: {q['text'][:60]}... -> {correct_letter}")
        return

    print(f"[CREATING] {tag} quiz: {params['title']}")
    quiz = create_quiz(course_id, params)
    quiz_id = quiz["id"]
    print(f"[CREATED]  {tag} quiz id={quiz_id}")
    time.sleep(0.15)

    # --- 2. Add all 15 questions ---
    for i, q in enumerate(QUESTIONS, 1):
        answers = []
        for j, ans_text in enumerate(q["answers"]):
            answers.append({
                "answer_text": ans_text,
                "answer_weight": 100 if j == q["correct"] else 0,
            })

        qparams = {
            "question_name": q["name"],
            "question_text": f"<p>{q['text']}</p>",
            "question_type": "multiple_choice_question",
            "points_possible": 1,
            "answers": answers,
        }
        create_quiz_question(course_id, quiz_id, qparams)
        print(f"  [Q{i:02d}] {q['name']}")
        time.sleep(0.1)

    # --- 3. Publish the quiz ---
    publish_quiz(course_id, quiz_id)
    print(f"[PUBLISHED] {tag} quiz id={quiz_id}")
    time.sleep(0.15)

    # --- 4. Try to add quiz to the most recent module ---
    try:
        modules = get_modules(course_id)
        if modules:
            # Pick the last module (most recent / current)
            target = modules[-1]
            create_module_item(
                course_id, target["id"], "Quiz", quiz_id,
                title="Brake Pads & Rotors Replacement -- Video Quiz",
            )
            print(f"[MODULE]   {tag} added to module: {target['name']}")
        else:
            print(f"[MODULE]   {tag} no modules found -- quiz is live but not in a module")
    except Exception as e:
        print(f"[MODULE]   {tag} could not add to module: {e}")

    # --- 5. Print quiz URL ---
    canvas_url = os.getenv("CANVAS_API_URL", "")
    quiz_url = f"{canvas_url}/courses/{course_id}/quizzes/{quiz_id}"
    print(f"[LINK]     {quiz_url}")

    return quiz_id


def run():
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    print(f"\n{'='*60}")
    print(f"  Brake Pads & Rotors Video Quiz  [{mode}]")
    print(f"{'='*60}")
    print(f"  Courses: {list(COURSES.values())}")
    print(f"  Due:     April 6, 2026 at 11:59 PM Pacific")
    print(f"  Video:   {VIDEO_URL}")
    print(f"{'='*60}\n")

    for cid, name in COURSES.items():
        deploy_quiz(cid, name)
        print()

    print(f"{'='*60}")
    print(f"  Done! [{mode}]")
    if DRY_RUN:
        print(f"  Re-run with --execute to push to Canvas.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
