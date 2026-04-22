#!/usr/bin/env python3
"""
Detailed audit of ungraded submissions across all active courses.
Shows exactly what each student submitted: text, URLs, attachments, comments.
Designed to give the instructor confidence before running the grading swarm.
"""
import sys
import os
import json
import time
sys.path.insert(0, os.path.dirname(__file__))

from canvas_api import (
    get_assignments, get_course_name, _make_request
)

COURSES = {
    23164: "P3 Metals 1",
    23132: "P3 Metals 2",
    23157: "P3 Metals 3",
    23188: "P5 Metals 1",
    23177: "P5 Metals 2",
    23124: "P1 Engines Fab 1",
    23344: "P1 Engines Fab 2",
}

def get_detailed_submissions(course_id, assignment_id):
    """Get submissions with comments, rubric assessments, and full history."""
    params = {
        'include[]': ['submission_history', 'submission_comments', 'rubric_assessment'],
        'per_page': 100
    }
    return _make_request(f'courses/{course_id}/assignments/{assignment_id}/submissions', params)

def get_enrollments(course_id):
    """Get enrolled students."""
    params = {'type[]': 'StudentEnrollment', 'per_page': 100}
    return _make_request(f'courses/{course_id}/enrollments', params)

def describe_submission(sub):
    """Build a human-readable description of what was actually submitted."""
    details = {}

    # Basic state
    details['workflow_state'] = sub.get('workflow_state', 'unknown')
    details['submitted_at'] = sub.get('submitted_at')
    details['graded_at'] = sub.get('graded_at')
    details['score'] = sub.get('score')
    details['grade'] = sub.get('grade')
    details['late'] = sub.get('late', False)
    details['missing'] = sub.get('missing', False)
    details['excused'] = sub.get('excused', False)
    details['attempt'] = sub.get('attempt')
    details['submission_type'] = sub.get('submission_type')

    # What did they actually turn in?
    content = []
    sub_type = sub.get('submission_type')

    if sub_type == 'online_text_entry':
        body = sub.get('body', '')
        if body:
            # Strip HTML but keep it short
            from bs4 import BeautifulSoup
            text = BeautifulSoup(body, 'html.parser').get_text(strip=True)
            content.append(f"TEXT ({len(text)} chars): {text[:200]}{'...' if len(text) > 200 else ''}")
        else:
            content.append("TEXT: (empty body)")
    elif sub_type == 'online_url':
        url = sub.get('url', '')
        content.append(f"URL: {url}")
    elif sub_type == 'online_upload':
        attachments = sub.get('attachments', [])
        for att in attachments:
            fname = att.get('display_name', 'unknown')
            fsize = att.get('size', 0)
            content.append(f"FILE: {fname} ({fsize} bytes)")
    elif sub_type == 'online_quiz':
        content.append("QUIZ submission")
    elif sub_type == 'basic_lti_launch':
        url = sub.get('url', '')
        content.append(f"LTI LAUNCH: {url}")
    elif sub_type is None:
        content.append("(no submission)")
    else:
        content.append(f"TYPE: {sub_type}")

    details['content'] = content

    # Comments
    comments = sub.get('submission_comments', [])
    details['comments'] = []
    for c in comments:
        author = c.get('author_name', 'Unknown')
        body = c.get('comment', '')
        created = c.get('created_at', '')
        details['comments'].append({
            'author': author,
            'comment': body[:300],
            'created_at': created
        })

    return details

def run():
    report = {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'courses': {}
    }

    # Also build a plain-text summary for terminal output
    print("=" * 70)
    print("DETAILED SUBMISSION AUDIT")
    print(f"Generated: {report['generated_at']}")
    print("=" * 70)

    for course_id, course_label in COURSES.items():
        print(f"\n{'='*70}")
        print(f"  {course_label} (ID: {course_id})")
        print(f"{'='*70}")

        # Build student name lookup
        try:
            enrollments = get_enrollments(course_id)
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error fetching enrollments: {e}")
            continue

        student_map = {}
        for e in enrollments:
            if e.get('type') == 'StudentEnrollment':
                user = e.get('user', {})
                student_map[user.get('id')] = user.get('name', 'Unknown')

        if not student_map:
            print("  (no students enrolled)")
            continue

        print(f"  {len(student_map)} students enrolled")

        course_report = {
            'label': course_label,
            'students': student_map,
            'assignments_needing_grading': []
        }

        # Get assignments
        try:
            assignments = get_assignments(course_id)
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error fetching assignments: {e}")
            continue

        for a in assignments:
            a_id = a.get('id')
            a_name = a.get('name', 'Unknown')
            a_pts = a.get('points_possible', 0)
            has_rubric = 'rubric' in a
            due = a.get('due_at')

            try:
                subs = get_detailed_submissions(course_id, a_id)
                time.sleep(0.1)
            except Exception as e:
                print(f"  Error on {a_name}: {e}")
                continue

            # Find ungraded submissions that have actual content
            ungraded = []
            for s in subs:
                ws = s.get('workflow_state', '')
                has_score = s.get('score') is not None

                # "submitted" or "pending_review" = turned in but not graded
                # Also catch "graded" with no score (edge case)
                if ws in ('submitted', 'pending_review') or (ws == 'graded' and not has_score):
                    desc = describe_submission(s)
                    desc['student_name'] = student_map.get(s.get('user_id'), f"User {s.get('user_id')}")
                    desc['user_id'] = s.get('user_id')
                    ungraded.append(desc)

            if not ungraded:
                continue

            # This assignment has ungraded work — report it
            assignment_report = {
                'id': a_id,
                'name': a_name,
                'points_possible': a_pts,
                'has_rubric': has_rubric,
                'due_at': due,
                'ungraded_submissions': ungraded
            }
            course_report['assignments_needing_grading'].append(assignment_report)

            print(f"\n  [{a_name}] ({a_pts} pts) {'[RUBRIC]' if has_rubric else '[NO RUBRIC]'} Due: {due or 'no due date'}")
            print(f"  {len(ungraded)} ungraded submission(s):")

            for u in ungraded:
                print(f"    - {u['student_name']} (ID: {u['user_id']})")
                print(f"      State: {u['workflow_state']} | Submitted: {u['submitted_at']} | Late: {u['late']}")
                print(f"      Type: {u['submission_type']}")
                for c in u['content']:
                    print(f"      Content: {c}")
                if u['comments']:
                    for cmt in u['comments']:
                        print(f"      COMMENT ({cmt['author']}, {cmt['created_at']}): {cmt['comment']}")
                else:
                    print(f"      (no comments)")

        report['courses'][str(course_id)] = course_report

    # Save full JSON report
    out_path = os.path.join(os.path.dirname(__file__), 'exports', 'detailed_audit.json')
    os.makedirs(os.path.join(os.path.dirname(__file__), 'exports'), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print(f"\n{'='*70}")
    print("SUMMARY — NEEDS GRADING")
    print(f"{'='*70}")
    total_ungraded = 0
    for cid, cdata in report['courses'].items():
        course_total = sum(len(a['ungraded_submissions']) for a in cdata['assignments_needing_grading'])
        if course_total > 0:
            print(f"\n  {cdata['label']}: {course_total} ungraded submissions")
            for a in cdata['assignments_needing_grading']:
                count = len(a['ungraded_submissions'])
                names = ', '.join(u['student_name'] for u in a['ungraded_submissions'])
                print(f"    {a['name']}: {count} — {names}")
        total_ungraded += course_total

    print(f"\n  TOTAL UNGRADED: {total_ungraded}")
    print(f"\nFull report saved to: {out_path}")

if __name__ == "__main__":
    run()
