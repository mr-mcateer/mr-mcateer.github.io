import os
from canvas_api import get_assignments, get_ungraded_submissions

COURSE_ID = "23164" # P3 Metals 1

def main():
    print(f"Fetching assignments for Course {COURSE_ID}...")
    assignments = get_assignments(COURSE_ID)
    
    for a in assignments:
        assignment_id = a['id']
        name = a['name']
        print(f"\nChecking Assignment {assignment_id}: {name}")
        
        try:
            submissions = get_ungraded_submissions(COURSE_ID, assignment_id)
            if not submissions:
                continue
                
            types = set()
            submitted_count = 0
            has_attachments = False
            
            for sub in submissions:
                if sub.get('workflow_state') != 'unsubmitted':
                    submitted_count += 1
                    sub_type = sub.get('submission_type')
                    if sub_type:
                        types.add(sub_type)
                    if sub.get('attachments'):
                        has_attachments = True
                        
            if submitted_count > 0:
                print(f"  -> Found {submitted_count} real submissions.")
                print(f"  -> Types: {', '.join(types)}")
                if has_attachments:
                    print("  -> CONTAINS ATTACHMENTS (Potential mixed media!)")
                    
                if len(types) > 1 or has_attachments:
                    print(f"  *** GOOD CANDIDATE FOR MULTIMODAL TEST: {assignment_id} ***")
                    
        except Exception as e:
            print(f"  Error checking {assignment_id}: {e}")

if __name__ == "__main__":
    main()
