import argparse
import sys
import os
import pandas as pd
from canvas_api import (
    get_assignments,
    get_ungraded_submissions,
    get_assignment_rubric,
    post_grade,
    get_student_name,
    get_course_name,
    get_active_courses
)
from swarm import run_swarm_on_submission, format_rubric_from_canvas, extract_submission_parts
from anonymizer import AnonymizationContext

def cmd_fetch(course_id):
    """List recent assignments to help the user pick an assignment ID."""
    print(f"Fetching assignments for Course {course_id}...")
    assignments = get_assignments(course_id)
    print("\n--- Recent Assignments ---")
    for a in assignments[:10]: # Just show top 10 recent
        has_rubric = "Yes" if a.get('rubric') else "No"
        print(f"ID: {a['id']} | Name: {a['name']} | Has Rubric: {has_rubric}")

def cmd_evaluate(course_id, assignment_id):
    """
    Core Loop:
    1. Fetch rubric & submissions from Canvas.
    2. Pass to the Swarm.
    3. Output the results to a local CSV.
    """
    print(f"Loading data for Assignment {assignment_id} in Course {course_id}...")

    # Initialize anonymization context for this evaluation run
    anon = AnonymizationContext()

    # 1. Get Rubric
    raw_rubric = get_assignment_rubric(course_id, assignment_id)
    if not raw_rubric:
        print("[WARNING] No rubric found on this assignment in Canvas! The agents will grade purely holistically.")
    rubric_text = format_rubric_from_canvas(raw_rubric)

    # 2. Get Submissions
    submissions = get_ungraded_submissions(course_id, assignment_id)
    if not submissions:
        print("No submissions found (or all are already graded).")
        return

    print(f"Found {len(submissions)} total submissions.")

    results = []
    # 3. Process each submission (filtering to just those that are ungraded and actually submitted something)
    for sub in submissions:
        # Skip if already graded (unless we want to overwrite)
        if sub.get('workflow_state') == 'graded':
            continue

        # Skip missing submissions
        if sub.get('workflow_state') == 'unsubmitted':
            continue

        user_id = sub['user_id']
        name = get_student_name(course_id, user_id)

        # Register student in anonymization context
        pseudonym = anon.anonymize_name(name)
        print(f"\nEvaluating student: {pseudonym} (anonymized)...")
        submission_parts = extract_submission_parts(sub)

        # Determine if it's text we can evaluate
        if not submission_parts or len(submission_parts) == 1 and "No content" in str(submission_parts[0]):
            print("  -> Skipping: No content found to evaluate.")
            continue

        # Extract a short excerpt for the CSV regardless of type
        excerpt = "Multimodal content (Images/Docs)"
        if isinstance(submission_parts[0], str):
            excerpt = submission_parts[0][:150] + "..."

        # Anonymize submission text before sending to external AI
        anon_parts = anon.anonymize_parts(submission_parts)

        # Hit the swarm (with anonymized data)
        try:
            swarm_eval = run_swarm_on_submission(anon_parts, rubric_text)
            final = swarm_eval['final_conclusion']

            # Deanonymize rationale text for the CSV (teacher needs real names)
            results.append({
                "User ID": user_id,
                "Student Name": name,
                "Submission Excerpt": excerpt,
                "Strict Agent Score": swarm_eval['strict_agent'].get('suggested_score'),
                "Strict Rationale": anon.deanonymize_text(
                    swarm_eval['strict_agent'].get('rationale', '')),
                "Holistic Agent Score": swarm_eval['holistic_agent'].get('suggested_score'),
                "Final Recommended Score": final.get('final_suggested_score'),
                "Resolution Rationale": anon.deanonymize_text(
                    final.get('resolution_rationale', ''))
            })
            print(f"  -> Recommended Score: {final.get('final_suggested_score')}")

        except Exception as e:
            print(f"  -> [ERROR] Failed to evaluate student {pseudonym}: {e}")
            
    # 4. Save
    if results:
        df = pd.DataFrame(results)
        os.makedirs('exports', exist_ok=True)
        filename = os.path.join('exports', f"draft_grades_{assignment_id}.csv")
        df.to_csv(filename, index=False)
        print(f"\n✅ Created report: {filename}")
        print("Please review this file, adjust 'Final Recommended Score' if needed, and run `python cli.py submit` to sync to Canvas.")
    else:
        print("No valid, ungraded submissions were evaluated.")

def cmd_evaluate_course(course_id):
    """
    Evaluates all ungraded submissions across all assignments in a given course.
    Outputs a single combined CSV report.
    """
    course_name = get_course_name(course_id)
    # create safe string for filename
    clean_course_name = "".join([c if c.isalnum() else "_" for c in course_name])

    # Initialize anonymization context for this course evaluation
    anon = AnonymizationContext()

    print(f"Loading assignments for Course: {course_name} ({course_id})...")
    assignments = get_assignments(course_id)

    all_results = []

    for a in assignments:
        assignment_id = a['id']
        assignment_name = a['name']
        print(f"\n--- Processing Assignment: {assignment_name} ({assignment_id}) ---")

        # 1. Get Rubric
        raw_rubric = get_assignment_rubric(course_id, assignment_id)
        if not raw_rubric:
            print("[WARNING] No rubric found on this assignment in Canvas! The agents will grade purely holistically.")
        rubric_text = format_rubric_from_canvas(raw_rubric)

        # 2. Get Submissions
        submissions = get_ungraded_submissions(course_id, assignment_id)
        if not submissions:
            print("No submissions found (or all are already graded).")
            continue

        print(f"Found {len(submissions)} total submissions.")

        # 3. Process each submission
        for sub in submissions:
            if sub.get('workflow_state') == 'graded':
                continue
            if sub.get('workflow_state') == 'unsubmitted':
                continue

            user_id = sub['user_id']
            name = get_student_name(course_id, user_id)
            pseudonym = anon.anonymize_name(name)

            print(f"\nEvaluating student: {pseudonym} (anonymized)...")
            submission_parts = extract_submission_parts(sub)

            if not submission_parts or len(submission_parts) == 1 and "No content" in str(submission_parts[0]):
                print("  -> Skipping: No content found to evaluate.")
                continue

            excerpt = "Multimodal content (Images/Docs)"
            if isinstance(submission_parts[0], str):
                excerpt = submission_parts[0][:150] + "..."

            # Anonymize before sending to external AI
            anon_parts = anon.anonymize_parts(submission_parts)

            try:
                swarm_eval = run_swarm_on_submission(anon_parts, rubric_text)
                final = swarm_eval['final_conclusion']

                all_results.append({
                    "Course Name": course_name,
                    "Assignment Name": assignment_name,
                    "Assignment ID": assignment_id,
                    "User ID": user_id,
                    "Student Name": name,
                    "Submission Excerpt": excerpt,
                    "Strict Agent Score": swarm_eval['strict_agent'].get('suggested_score'),
                    "Strict Rationale": anon.deanonymize_text(
                        swarm_eval['strict_agent'].get('rationale', '')),
                    "Holistic Agent Score": swarm_eval['holistic_agent'].get('suggested_score'),
                    "Final Recommended Score": final.get('final_suggested_score'),
                    "Resolution Rationale": anon.deanonymize_text(
                        final.get('resolution_rationale', ''))
                })
                print(f"  -> Recommended Score: {final.get('final_suggested_score')}")

            except Exception as e:
                print(f"  -> [ERROR] Failed to evaluate student {pseudonym}: {e}")
                
    if all_results:
        df = pd.DataFrame(all_results)
        os.makedirs('exports', exist_ok=True)
        filename = os.path.join('exports', f"draft_grades_{clean_course_name}.csv")
        df.to_csv(filename, index=False)
        print(f"\n✅ Created course-wide report: {filename}")
        print("Please review this file, adjust 'Final Recommended Score' if needed, and run `python cli.py submit` to sync to Canvas.")
    else:
        print("\nNo valid, ungraded submissions were evaluated in the entire course.")

def cmd_evaluate_all():
    """
    Evaluates all active courses the instructor is enrolled in.
    Each course will generate its own CSV in the exports directory.
    """
    print("Fetching all active courses...")
    courses = get_active_courses()
    if not courses:
        print("No active courses found.")
        return
        
    for c in courses:
        course_id = c.get('id')
        course_name = c.get('name', 'Unknown')
        print(f"\n==================================================")
        print(f"STARTING BATCH EVALUATION FOR: {course_name} ({course_id})")
        print(f"==================================================")
        cmd_evaluate_course(course_id)
        
    print("\n✅ All active courses have been processed!")

def cmd_submit(course_id, file_path, assignment_id=None):
    """
    Reads the validated CSV, loops through it, and posts the grade/comments 
    back to the Canvas gradebook.
    """
    print(f"Reading {file_path} for grades...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")
        return
        
    for index, row in df.iterrows():
        user_id = row['User ID']
        name = row['Student Name']
        grade = row['Final Recommended Score']
        
        current_assignment_id = assignment_id
        if current_assignment_id is None:
            if 'Assignment ID' in row:
                current_assignment_id = row['Assignment ID']
            else:
                print(f"  [ERROR] No Assignment ID provided or found in CSV for {name}")
                continue
                
        print(f"Submitting {grade} for {name} on assignment {current_assignment_id}...")
        try:
            post_grade(course_id, current_assignment_id, user_id, grade)
        except Exception as e:
            print(f"  [ERROR] Failed to post grade for {name}: {e}")
            
    print("\n✅ All grades synced to Canvas!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canvas AI Agent Swarm Grader")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # FETCH
    fetch_parser = subparsers.add_parser("fetch", help="List recent assignments for a course to find the ID")
    fetch_parser.add_argument("--course", required=True, help="Canvas Course ID")
    
    # EVALUATE
    eval_parser = subparsers.add_parser("evaluate", help="Pull submissions and run the AI swarm")
    eval_parser.add_argument("--course", required=True, help="Canvas Course ID")
    eval_parser.add_argument("--assignment", required=True, help="Canvas Assignment ID")
    
    # EVALUATE COURSE
    eval_course_parser = subparsers.add_parser("evaluate-course", help="Evaluate all ungraded submissions across an entire course")
    eval_course_parser.add_argument("--course", required=True, help="Canvas Course ID")
    
    # EVALUATE ALL COURSES
    subparsers.add_parser("evaluate-all", help="Evaluate all active courses at once (Takes significant time)")
    
    # SUBMIT
    submit_parser = subparsers.add_parser("submit", help="Push a drafted CSV of grades back to Canvas")
    submit_parser.add_argument("--course", required=True, help="Canvas Course ID")
    submit_parser.add_argument("--assignment", required=False, help="Canvas Assignment ID (Not needed if evaluating an entire course)")
    submit_parser.add_argument("--file", required=True, help="Path to the draft_grades.csv file")
    
    args = parser.parse_args()
    
    if args.command == "fetch":
        cmd_fetch(args.course)
    elif args.command == "evaluate":
        cmd_evaluate(args.course, args.assignment)
    elif args.command == "evaluate-course":
        cmd_evaluate_course(args.course)
    elif args.command == "evaluate-all":
        cmd_evaluate_all()
    elif args.command == "submit":
        cmd_submit(args.course, args.file, args.assignment)
