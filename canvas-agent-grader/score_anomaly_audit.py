#!/usr/bin/env python3
"""
Score anomaly audit -- finds over-graded submissions and grading typos.
Read-only: does not modify any grades.

Usage:
    python3 score_anomaly_audit.py            # use existing snapshot
    python3 score_anomaly_audit.py --refresh   # regenerate snapshot first
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

EXPORTS = os.path.join(os.path.dirname(__file__), "exports")
SNAPSHOT_FILE = os.path.join(EXPORTS, "gradebook_snapshot.json")
REPORT_FILE = os.path.join(EXPORTS, "score_anomaly_report.json")

MINOR_THRESHOLD = 1.0
MAJOR_THRESHOLD = 1.10
EXTREME_THRESHOLD = 2.0


def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        print(f"ERROR: {SNAPSHOT_FILE} not found.")
        print("Run gradebook_audit.py first to generate the snapshot.")
        sys.exit(1)
    with open(SNAPSHOT_FILE) as f:
        return json.load(f)


def build_name_lookup(course_data):
    return {e["user_id"]: e["name"] for e in course_data.get("enrollments", [])}


def classify_severity(ratio):
    if ratio >= EXTREME_THRESHOLD:
        return "EXTREME"
    if ratio >= MAJOR_THRESHOLD:
        return "MAJOR"
    return "MINOR"


def scan_submissions(snapshot):
    anomalies = []
    for course_id, course_data in snapshot.items():
        names = build_name_lookup(course_data)
        label = course_data.get("label", course_id)

        for a in course_data.get("assignments", []):
            pts = a.get("points_possible")
            if not pts or pts <= 0:
                continue

            for s in a.get("submissions", []):
                if s.get("excused"):
                    continue
                score = s.get("score")
                if score is None:
                    continue
                if score <= pts:
                    continue

                ratio = score / pts
                anomalies.append({
                    "course_id": course_id,
                    "course_label": label,
                    "assignment_id": a["id"],
                    "assignment_name": a["name"],
                    "points_possible": pts,
                    "user_id": s["user_id"],
                    "student_name": names.get(s["user_id"], f"User {s['user_id']}"),
                    "score": score,
                    "grade": s.get("grade"),
                    "overage": round(score - pts, 2),
                    "ratio": round(ratio, 4),
                    "severity": classify_severity(ratio),
                    "graded_at": s.get("graded_at"),
                })
    return anomalies


def scan_enrollments(snapshot):
    anomalies = []
    for course_id, course_data in snapshot.items():
        label = course_data.get("label", course_id)
        for e in course_data.get("enrollments", []):
            cs = e.get("current_score")
            if cs is not None and cs > 100:
                anomalies.append({
                    "course_id": course_id,
                    "course_label": label,
                    "user_id": e["user_id"],
                    "student_name": e["name"],
                    "current_score": cs,
                    "current_grade": e.get("current_grade"),
                    "final_score": e.get("final_score"),
                    "overage": round(cs - 100, 2),
                })
    return anomalies


SEVERITY_ORDER = {"EXTREME": 0, "MAJOR": 1, "MINOR": 2}


def print_report(sub_anomalies, enroll_anomalies):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  SCORE ANOMALY AUDIT")
    print(f"  Generated: {now}")
    print(f"  Snapshot:  exports/gradebook_snapshot.json")
    print(f"{sep}")

    sorted_subs = sorted(sub_anomalies, key=lambda x: (
        SEVERITY_ORDER.get(x["severity"], 9),
        x["course_label"],
        x["assignment_name"],
    ))

    for severity_label in ["EXTREME", "MAJOR", "MINOR"]:
        group = [a for a in sorted_subs if a["severity"] == severity_label]
        descriptions = {
            "EXTREME": "Score is 2x+ the points possible",
            "MAJOR": "Score exceeds points possible by 10%+",
            "MINOR": "Score slightly over points possible",
        }
        print(f"\n--- {severity_label}: {descriptions[severity_label]} ---")

        if not group:
            print("\n  (none found)")
            continue

        current_course = None
        current_assignment = None
        for a in group:
            if a["course_label"] != current_course:
                current_course = a["course_label"]
                print(f"\n  {current_course}")
                current_assignment = None
            if a["assignment_name"] != current_assignment:
                current_assignment = a["assignment_name"]
                print(f"    {current_assignment} ({a['points_possible']:.0f} pts)")
            score_col = f"{a['score']:.1f} / {a['points_possible']:.1f}"
            over_col = f"+{a['overage']:.1f} over"
            ratio_col = f"({a['ratio']:.2f}x)"
            print(f"      {a['student_name']:<20s} {score_col:<16s} {over_col:<12s} {ratio_col}")

    print(f"\n--- STUDENTS OVER 100% CURRENT SCORE ---")
    if not enroll_anomalies:
        print("\n  (none found)")
    else:
        current_course = None
        for e in sorted(enroll_anomalies, key=lambda x: x["course_label"]):
            if e["course_label"] != current_course:
                current_course = e["course_label"]
                print(f"\n  {current_course}")
            print(f"    {e['student_name']:<20s} {e['current_score']:.2f}%   (+{e['overage']:.2f} over 100%)")

    extreme = sum(1 for a in sub_anomalies if a["severity"] == "EXTREME")
    major = sum(1 for a in sub_anomalies if a["severity"] == "MAJOR")
    minor = sum(1 for a in sub_anomalies if a["severity"] == "MINOR")

    print(f"\n{sep}")
    print(f"  SUMMARY")
    print(f"{sep}")
    print(f"  Submission anomalies: {len(sub_anomalies)} ({extreme} extreme, {major} major, {minor} minor)")
    print(f"  Students over 100%:  {len(enroll_anomalies)}")
    print(f"  Report saved to:     exports/score_anomaly_report.json")
    print(f"{sep}\n")


def save_report(sub_anomalies, enroll_anomalies):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    extreme = sum(1 for a in sub_anomalies if a["severity"] == "EXTREME")
    major = sum(1 for a in sub_anomalies if a["severity"] == "MAJOR")
    minor = sum(1 for a in sub_anomalies if a["severity"] == "MINOR")

    report = {
        "generated_at": now,
        "snapshot_file": "exports/gradebook_snapshot.json",
        "submission_anomalies": sub_anomalies,
        "enrollment_anomalies": enroll_anomalies,
        "summary": {
            "total_submission_anomalies": len(sub_anomalies),
            "extreme": extreme,
            "major": major,
            "minor": minor,
            "students_over_100_pct": len(enroll_anomalies),
        },
    }
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2, default=str)


def run():
    if "--refresh" in sys.argv:
        print("Refreshing gradebook snapshot...")
        import gradebook_audit
        gradebook_audit.run()
        print()

    snapshot = load_snapshot()
    sub_anomalies = scan_submissions(snapshot)
    enroll_anomalies = scan_enrollments(snapshot)
    print_report(sub_anomalies, enroll_anomalies)
    save_report(sub_anomalies, enroll_anomalies)

    has_critical = any(a["severity"] in ("EXTREME", "MAJOR") for a in sub_anomalies)
    return 1 if has_critical else 0


if __name__ == "__main__":
    sys.exit(run())
