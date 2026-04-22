"""
Force swarm to re-grade ALL submissions for "03 -- The Real Price Tag"
in both P1 Engines/Fab sections (23124/476274 and 23344/476303).

Why: the assignment point value was just corrected from 40 to 20 to match
the rubric sum. Previously-graded submissions were scored at the 40-pt
scale and now display as >100%. Ungraded submissions are being handled by
the evaluate-course swarm run. This script handles everything including
previously graded ones.

Output: exports/regrade_real_price_tag.csv
Does NOT auto-push. Review before running `python3 cli.py submit`.
"""
import os
import time
import pandas as pd
from canvas_api import (
    _make_request,
    get_assignment_rubric,
    get_ungraded_submissions,
    get_student_name,
)
from swarm import run_swarm_on_submission, format_rubric_from_canvas, extract_submission_parts

TARGETS = [
    {"course": 23124, "assignment": 476274, "label": "P1 Engines Fab 1"},
    {"course": 23344, "assignment": 476303, "label": "P1 Engines Fab 2"},
]


def main():
    all_results = []
    for t in TARGETS:
        cid = t["course"]
        aid = t["assignment"]
        label = t["label"]
        print(f"\n{'='*70}\n{label} -- Real Price Tag (course {cid} asn {aid})\n{'='*70}")

        assignment = _make_request(f"courses/{cid}/assignments/{aid}")
        a_pts = assignment.get("points_possible")
        print(f"Current points_possible: {a_pts}")

        raw_rubric = get_assignment_rubric(cid, aid)
        rubric_text = format_rubric_from_canvas(raw_rubric)

        # Fetch ALL submissions (includes already-graded ones). The
        # get_ungraded_submissions helper actually returns all; the filter
        # happens in cli.py. We want the full list here.
        subs = get_ungraded_submissions(cid, aid)
        print(f"Retrieved {len(subs)} submission rows.")

        for sub in subs:
            uid = sub.get("user_id")
            state = sub.get("workflow_state")
            sub_type = sub.get("submission_type")

            # Skip unsubmitted
            if state == "unsubmitted" or not sub_type:
                continue

            name = get_student_name(cid, uid)
            current_score = sub.get("score")
            print(f"\n  -> {name} (uid {uid})  state={state} current_score={current_score}")

            parts = extract_submission_parts(sub)
            has_comments = bool(sub.get("submission_comments"))
            if not has_comments and (not parts or (len(parts) == 1 and "No content" in str(parts[0]))):
                print("     Skipping: empty.")
                continue

            excerpt = "Multimodal content"
            if isinstance(parts[0], str):
                excerpt = parts[0][:150] + "..."

            try:
                swarm_eval = run_swarm_on_submission(parts, rubric_text, a_pts)
                final = swarm_eval["final_conclusion"]
                final_score = final.get("final_suggested_score")
                if a_pts is not None and final_score is not None:
                    final_score = min(float(final_score), float(a_pts))

                all_results.append({
                    "Course Name": label,
                    "Assignment Name": "03 -- The Real Price Tag",
                    "Assignment ID": aid,
                    "User ID": uid,
                    "Student Name": name,
                    "Points Possible": a_pts,
                    "Previous Canvas Score (raw)": current_score,
                    "Was Graded Before": state == "graded",
                    "Submission Excerpt": excerpt,
                    "Has Comments": has_comments,
                    "Strict Agent Score": swarm_eval["strict_agent"].get("suggested_score"),
                    "Strict Rationale": swarm_eval["strict_agent"].get("rationale"),
                    "Holistic Agent Score": swarm_eval["holistic_agent"].get("suggested_score"),
                    "Final Recommended Score": final_score,
                    "Resolution Rationale": final.get("resolution_rationale"),
                })
                print(f"     Recommended: {final_score}/{a_pts} (was {current_score})")
            except Exception as e:
                print(f"     [ERROR] {e}")

        # Gentle rate-limit pause between courses
        time.sleep(5)

    if all_results:
        os.makedirs("exports", exist_ok=True)
        out = "exports/regrade_real_price_tag.csv"
        pd.DataFrame(all_results).to_csv(out, index=False)
        print(f"\nWrote {len(all_results)} regrades to {out}")
    else:
        print("\nNo regrades produced.")


if __name__ == "__main__":
    main()
