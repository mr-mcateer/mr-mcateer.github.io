#!/usr/bin/env python3
"""
Pull full gradebook snapshot from all active courses for analysis.
Outputs JSON with assignments, submissions, and grades per course.
"""
import sys
import os
import json
import time
sys.path.insert(0, os.path.dirname(__file__))

from canvas_api import (
    get_assignments, get_ungraded_submissions, get_course_name,
    _make_request
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

def get_all_submissions(course_id, assignment_id):
    """Get ALL submissions (graded + ungraded)."""
    params = {
        'include[]': ['submission_history'],
        'per_page': 100
    }
    return _make_request(f'courses/{course_id}/assignments/{assignment_id}/submissions', params)

def get_enrollments(course_id):
    """Get enrolled students."""
    params = {'type[]': 'StudentEnrollment', 'per_page': 100,
              'include[]': ['total_scores']}
    return _make_request(f'courses/{course_id}/enrollments', params)

def run():
    output = {}

    for course_id, course_label in COURSES.items():
        print(f"\n--- {course_label} ({course_id}) ---")
        course_data = {
            'label': course_label,
            'course_id': course_id,
            'enrollments': [],
            'assignments': []
        }

        # Get enrollments with grades
        try:
            enrollments = get_enrollments(course_id)
            for e in enrollments:
                if e.get('type') == 'StudentEnrollment':
                    user = e.get('user', {})
                    grades = e.get('grades', {})
                    course_data['enrollments'].append({
                        'user_id': user.get('id'),
                        'name': user.get('name', 'Unknown'),
                        'current_score': grades.get('current_score'),
                        'current_grade': grades.get('current_grade'),
                        'final_score': grades.get('final_score'),
                        'final_grade': grades.get('final_grade'),
                    })
            print(f"  {len(course_data['enrollments'])} students enrolled")
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error fetching enrollments: {e}")

        # Get assignments
        try:
            assignments = get_assignments(course_id)
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error fetching assignments: {e}")
            assignments = []

        for a in assignments:
            a_id = a.get('id')
            a_name = a.get('name', 'Unknown')
            a_pts = a.get('points_possible', 0)
            published = a.get('published', False)
            due = a.get('due_at')
            sub_types = a.get('submission_types', [])

            a_data = {
                'id': a_id,
                'name': a_name,
                'points_possible': a_pts,
                'published': published,
                'due_at': due,
                'submission_types': sub_types,
                'has_rubric': 'rubric' in a,
                'submissions': []
            }

            # Get submissions
            try:
                subs = get_all_submissions(course_id, a_id)
                time.sleep(0.1)
                for s in subs:
                    workflow = s.get('workflow_state', '')
                    a_data['submissions'].append({
                        'user_id': s.get('user_id'),
                        'workflow_state': workflow,
                        'submitted_at': s.get('submitted_at'),
                        'graded_at': s.get('graded_at'),
                        'score': s.get('score'),
                        'grade': s.get('grade'),
                        'late': s.get('late', False),
                        'missing': s.get('missing', False),
                        'excused': s.get('excused', False),
                        'attempt': s.get('attempt'),
                    })
            except Exception as e:
                print(f"  Error on {a_name}: {e}")

            graded_count = sum(1 for s in a_data['submissions']
                             if s['score'] is not None)
            submitted_count = sum(1 for s in a_data['submissions']
                                if s['workflow_state'] in ('submitted', 'graded', 'pending_review'))
            total = len(a_data['submissions'])

            a_data['summary'] = {
                'total_students': total,
                'submitted': submitted_count,
                'graded': graded_count,
                'ungraded': submitted_count - graded_count,
                'not_submitted': total - submitted_count,
            }

            course_data['assignments'].append(a_data)
            if graded_count > 0 or submitted_count > 0:
                print(f"  {a_name}: {submitted_count}/{total} submitted, {graded_count} graded")

        output[str(course_id)] = course_data

    out_path = os.path.join(os.path.dirname(__file__), 'exports', 'gradebook_snapshot.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    run()
