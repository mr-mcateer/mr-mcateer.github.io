#!/usr/bin/env python3
"""
Award full cleanup scores for all enrolled students on past cleanup assignments.
+1 bonus point for students who submitted a comment (with a note saying so).

Publishes unpublished assignments before grading.

Usage:
    python3 push_cleanup_grades.py              # dry run
    python3 push_cleanup_grades.py --execute    # post to Canvas
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')
HEADERS = {'Authorization': f'Bearer {CANVAS_API_TOKEN}'}

ACTIVE_COURSES = ['23164', '23132', '23157', '23188', '23177', '23124', '23344']
CUTOFF = datetime(2026, 4, 12, 23, 59, 59, tzinfo=timezone.utc)

EXPORTS = os.path.join(os.path.dirname(__file__), "exports")


def load_snapshot():
    with open(os.path.join(EXPORTS, "gradebook_snapshot.json")) as f:
        return json.load(f)


def publish_assignment(course_id, assignment_id):
    """Publish an unpublished assignment."""
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}"
    payload = {"assignment": {"published": True}}
    resp = requests.put(url, headers=HEADERS, json=payload)
    return resp.status_code == 200


def post_grade(course_id, assignment_id, student_id, score, comment=None):
    """Post a grade (and optional comment) to Canvas."""
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}"
    payload = {
        "submission": {
            "posted_grade": str(score)
        }
    }
    if comment:
        payload["comment"] = {"text_comment": comment}
    resp = requests.put(url, headers=HEADERS, json=payload)
    return resp.status_code, resp.text[:200] if resp.status_code != 200 else "OK"


def get_submission_comments(course_id, assignment_id, student_id):
    """Check if a student has comments on a submission."""
    url = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}"
    params = {"include[]": "submission_comments"}
    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200:
        return False, False
    data = resp.json()
    comments = data.get("submission_comments", [])
    # Check for student comments (not teacher)
    student_comments = [c for c in comments if not c.get("author", {}).get("display_name", "").startswith("Andy")]
    has_submission = data.get("submission_type") is not None
    return has_submission, len(student_comments) > 0


def main():
    execute = "--execute" in sys.argv
    snapshot = load_snapshot()

    total_ok = 0
    total_err = 0
    total_bonus = 0
    total_published = 0

    for cid in ACTIVE_COURSES:
        if cid not in snapshot:
            continue

        course = snapshot[cid]
        cname = course.get('label', '')
        enrollments = course.get('enrollments', [])
        enrolled_map = {str(e['user_id']): e.get('name', '') for e in enrollments}

        if not enrolled_map:
            continue

        for a in course.get('assignments', []):
            aname = a.get('name', '')
            if 'clean' not in aname.lower():
                continue

            aid = a.get('id')
            pts = a.get('points_possible', 0)
            due_at = a.get('due_at')
            published = a.get('published', True)

            # Skip future assignments
            if due_at:
                try:
                    due_dt = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                    if due_dt > CUTOFF:
                        continue
                except (ValueError, TypeError):
                    continue
            else:
                continue

            # Find who already has a grade
            submissions = a.get('submissions', [])
            graded_ids = set()
            for s in submissions:
                uid = str(s.get('user_id', ''))
                if s.get('score') is not None:
                    graded_ids.add(uid)

            need_grade = set(enrolled_map.keys()) - graded_ids
            if not need_grade:
                continue

            # Publish if needed
            if not published:
                if execute:
                    ok = publish_assignment(cid, aid)
                    tag = "PUBLISHED" if ok else "PUB_ERR"
                    print(f"\n  [{tag}] {cname} | {aname}")
                    if ok:
                        total_published += 1
                    time.sleep(0.1)
                else:
                    print(f"\n  [DRY RUN PUBLISH] {cname} | {aname}")
                    total_published += 1

            print(f"\n{cname} | {aname} ({pts} pts) | {len(need_grade)} students")

            for uid in sorted(need_grade):
                name = enrolled_map.get(uid, uid)

                # Check for student comments (bonus)
                has_sub, has_comment = False, False
                if execute:
                    has_sub, has_comment = get_submission_comments(cid, aid, uid)
                    time.sleep(0.05)

                if has_comment:
                    score = pts + 1
                    comment = "Bonus point for thorough documentation. Nice work."
                    total_bonus += 1
                else:
                    score = pts
                    comment = None

                if execute:
                    status, result = post_grade(cid, aid, uid, score, comment)
                    if status == 200:
                        bonus_tag = " +1 BONUS" if has_comment else ""
                        print(f"  [OK] {name} -> {score}/{pts}{bonus_tag}")
                        total_ok += 1
                    else:
                        print(f"  [ERR {status}] {name} -> {result[:80]}")
                        total_err += 1
                    time.sleep(0.1)
                else:
                    print(f"  [DRY RUN] {name} -> {pts}/{pts}")

    print(f"\n{'=' * 60}")
    print(f"Published: {total_published} assignments")
    print(f"Grades OK: {total_ok} | Errors: {total_err} | Bonus: {total_bonus}")
    if not execute:
        print("DRY RUN. Use --execute to post.")
    else:
        print("Done.")


if __name__ == "__main__":
    main()
