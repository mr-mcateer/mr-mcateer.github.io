#!/usr/bin/env python3
"""
Push audit grades to Canvas - March 18 sweep.

Policy:
- Engine portfolios: only comment on 100% obvious cases (inaccessible, blank, wrong doc)
- Zack Morris: encouraging comment about progress this week
- Dell Rutherford: full credit on Cell Phone Stand POP
- Iain Bailes: full credit on Bookend Project
- Vehicle ownership A grades: post grade
- Vehicle ownership below A: "is this your final submission?" nudge
"""
import sys
import time
import os
sys.path.insert(0, os.path.dirname(__file__))

from canvas_api import _make_put_request, post_grade

DRY_RUN = "--execute" not in sys.argv


def comment_only(course_id, assignment_id, user_id, comment, label=""):
    """Post a comment WITHOUT changing the grade."""
    payload = {'comment': {'text_comment': comment}}
    endpoint = f"courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
    tag = f"  COMMENT -> {label} (user {user_id})"
    if DRY_RUN:
        print(f"[DRY RUN] {tag}")
        print(f"           {comment}")
    else:
        _make_put_request(endpoint, payload)
        print(f"[POSTED]  {tag}")
        time.sleep(0.15)


def grade(course_id, assignment_id, user_id, score, label=""):
    """Post a grade (no comment)."""
    tag = f"  GRADE {score} -> {label} (user {user_id})"
    if DRY_RUN:
        print(f"[DRY RUN] {tag}")
    else:
        post_grade(course_id, assignment_id, user_id, score)
        print(f"[POSTED]  {tag}")
        time.sleep(0.15)


def run():
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    print(f"\n{'='*60}")
    print(f"  Canvas Audit Grade Push  [{mode}]")
    print(f"{'='*60}\n")

    # ==================================================================
    # 1) ENGINE PORTFOLIOS - 100% confidence comments only
    #    (inaccessible docs, blank templates, wrong files)
    # ==================================================================
    print("--- Engine Teardown Portfolios (obvious cases only) ---\n")

    # Hazel Shaub - Google Doc inaccessible
    comment_only(23124, 475434, 3719,
        "Hey Hazel -- I wasn't able to open your Google Doc. "
        "Could you double-check that sharing is set to "
        "'Anyone with the link can view' and resubmit?",
        "Hazel Shaub - Teardown Portfolio")

    # Daniel Darling - admitted blank ("most of this worksheet is missing")
    comment_only(23124, 475434, 14996,
        "Hey Daniel -- looks like most of the portfolio still needs to be filled in. "
        "No worries, just get your documentation added and resubmit when you're ready.",
        "Daniel Darling - Teardown Portfolio")

    # Cynthia Tran - 01 First Car had wrong doc (retrospective template)
    comment_only(23124, 476272, 8312,
        "Hey Cynthia -- it looks like the wrong document got attached here. "
        "I'm seeing a project retrospective template instead of your vehicle research. "
        "Could you resubmit with the right file?",
        "Cynthia Tran - 01 First Car (wrong doc)")

    # ==================================================================
    # 2) INACCESSIBLE METALS SUBMISSIONS
    # ==================================================================
    print("\n--- Inaccessible / Blank Metals Submissions ---\n")

    # Calvin Slupe - Google Doc inaccessible
    comment_only(23188, 475441, 20460,
        "Hey Calvin -- I wasn't able to open your Google Doc. "
        "Could you check that sharing is set to "
        "'Anyone with the link can view' and resubmit?",
        "Calvin Slupe - Metal Entrepreneur")

    # Hans Tarubal - blank template submitted
    comment_only(23188, 475441, 20756,
        "Hey Hans -- looks like the blank template got submitted "
        "instead of your completed project. "
        "Fill in your work and resubmit when you're ready!",
        "Hans Tarubal - Metal Entrepreneur")

    # ==================================================================
    # 3) ZACK MORRIS - encouraging comment, no grade
    # ==================================================================
    print("\n--- Zack Morris - Encouragement ---\n")

    # Metal Entrepreneur (23188, 475441)
    comment_only(23188, 475441, 1320,
        "Hey Zack -- we're going to make huge progress in class this week. "
        "Let's get these projects wrapped up on Wednesday so you can "
        "have a real grade in here. See you 3/19!",
        "Zack Morris - Metal Entrepreneur")

    # Bookend Project (23188, 477272)
    comment_only(23188, 477272, 1320,
        "Hey Zack -- we're going to make huge progress in class this week. "
        "Let's get these projects wrapped up on Wednesday so you can "
        "have a real grade in here. See you 3/19!",
        "Zack Morris - Bookend Project")

    # ==================================================================
    # 4) FULL CREDIT - Dell & Iain
    # ==================================================================
    print("\n--- Full Credit Awards ---\n")

    # Dell Rutherford - Cell Phone Stand POP Writeup (50 pts possible)
    grade(23188, 475451, 22591, 50, "Dell Rutherford - Cell Phone Stand POP (FULL CREDIT)")

    # Iain Bailes - Bookend Project (100 pts possible, no rubric)
    grade(23164, 477271, 8384, 100, "Iain Bailes - Bookend Project (FULL CREDIT)")

    # ==================================================================
    # 5) VEHICLE OWNERSHIP - A grades get posted, below A get a nudge
    # ==================================================================
    print("\n--- Vehicle Ownership - A Grades ---\n")

    # David O'Briant - 01 First Car: 18/20 = 90% -> A
    grade(23344, 476301, 763, 18, "David O'Briant - 01 First Car (90%)")

    print("\n--- Vehicle Ownership - Below A (final submission check) ---\n")

    NUDGE = (
        "Hey {name} -- just wanted to check, is this your final submission "
        "for this assignment? You still have time to make updates "
        "before I finalize the grade."
    )

    # Ian Fuhrman - 02 Before You Buy: 16/20 = 80% B
    comment_only(23124, 476273, 2567,
        NUDGE.format(name="Ian"),
        "Ian Fuhrman - 02 Before You Buy (80%)")

    # Alex Eigel - 04 Insurance Decoded: 10/20 = 50%
    comment_only(23124, 476275, 1424,
        NUDGE.format(name="Alex"),
        "Alex Eigel - 04 Insurance Decoded (50%)")

    # Alex Eigel - 05 Keep It Running: 13/15 = 87% B+
    comment_only(23124, 476277, 1424,
        NUDGE.format(name="Alex"),
        "Alex Eigel - 05 Keep It Running (87%)")

    # Noah Steele - 01 First Car: 14/20 = 70% C
    comment_only(23344, 476301, 8410,
        NUDGE.format(name="Noah"),
        "Noah Steele - 01 First Car (70%)")

    # David O'Briant - 02 Before You Buy: 16/20 = 80% B
    comment_only(23344, 476302, 763,
        NUDGE.format(name="David"),
        "David O'Briant - 02 Before You Buy (80%)")

    # Oliver Norris - 02 Before You Buy: 12/20 = 60% D
    comment_only(23344, 476302, 1875,
        NUDGE.format(name="Oliver"),
        "Oliver Norris - 02 Before You Buy (60%)")

    # Noah Steele - 02 Before You Buy: 6/20 = 30%
    comment_only(23344, 476302, 8410,
        NUDGE.format(name="Noah"),
        "Noah Steele - 02 Before You Buy (30%)")

    # ==================================================================
    print(f"\n{'='*60}")
    print(f"  Done! [{mode}]")
    if DRY_RUN:
        print("  Re-run with --execute to push to Canvas.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
