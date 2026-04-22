"""
Push 10/10 on Shop Cleanup -- Thursday 4/16 to every student in the
4 Metals sections. Post personalized feedback comments for:
  Trevor Skaggs    (P3 Metals 1, user_id 8401)
  Dawson Richards  (P3 Metals 2, user_id 8370)
  Colton Hankey    (P3 Metals 1, user_id 15415)

Shop Cleanup 4/16 is ungraded for every student because 4/16 and 4/17
were conference days (no school). Giving full credit for a day that
didn't happen avoids penalizing students who never had the chance to
earn it.

Usage:
    python3 push_cleanup_points_0420.py --dry-run    # see plan
    python3 push_cleanup_points_0420.py --execute    # post grades
"""
import argparse
import sys
import time

from canvas_api import _make_request, _make_put_request, post_grade

SCORE = 10.0

# Section -> (course_id, 4/16 assignment_id, human label)
SECTIONS = [
    (23164, 476550, "P3 Metals 1"),
    (23132, 476567, "P3 Metals 2"),
    (23188, 476601, "P5 Metals 1"),
    (23177, 476618, "P5 Metals 2"),
]

# Students who get a personalized comment alongside full points
# Key: user_id. Value: dict with name, section, and comment text.
TARGETED_COMMENTS = {
    8401: {
        "name": "Trevor Skaggs",
        "section": "P3 Metals 1",
        "comment": (
            "Trevor, the welding practice time is great, keep using "
            "the booth. The problem is the state of the booth when "
            "you are done. I have been in here on weekends cleaning "
            "up rods, spatter, and scrap. For the last stretch of "
            "the year, put your rods and cups back, sweep your "
            "station, and leave it ready for the next person. Full "
            "points here. This is the warning."
        ),
    },
    8370: {
        "name": "Dawson Richards",
        "section": "P3 Metals 2",
        "comment": (
            "Dawson, same note I am giving Trevor. The welding "
            "practice is great, keep using the booth. But it keeps "
            "getting left a mess and I have been in here on weekends "
            "cleaning up after you. Put rods and cups back, sweep "
            "your station, leave it ready for the next person. For "
            "the last stretch of the year I want to see this dialed. "
            "Full points here. This is the warning."
        ),
    },
    15415: {
        "name": "Colton Hankey",
        "section": "P3 Metals 1",
        "comment": (
            "Colton, you take on more projects than almost anyone in "
            "the shop and your work ethic shows. The flip side: you "
            "leave a mess in both Autos and Metals, and Bob cleans "
            "up after you on weekends. Bob is 83. Stop. Before you "
            "move to the next task or walk out the door, put tools "
            "back, sweep your station, and leave the bay better than "
            "you found it. Full points here. This last stretch, be "
            "the student who sets the example."
        ),
    },
}


def get_roster(course_id):
    """Return [{user_id, name}] for real students in a course."""
    enrollments = _make_request(
        f"courses/{course_id}/enrollments",
        params={"per_page": 100, "type[]": "StudentEnrollment"},
    )
    out = []
    seen = set()
    for e in enrollments:
        user = e.get("user") or {}
        uid = user.get("id")
        name = user.get("name", "")
        if not uid or uid in seen:
            continue
        if name.strip().lower() == "test student":
            continue
        seen.add(uid)
        out.append({"user_id": uid, "name": name})
    return out


def get_assignment(course_id, assignment_id):
    return _make_request(f"courses/{course_id}/assignments/{assignment_id}")


def get_current_submission(course_id, assignment_id, user_id):
    return _make_request(
        f"courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
    )


def verify_targets():
    """Confirm the three targeted students are exactly where we think."""
    errors = []
    for uid, info in TARGETED_COMMENTS.items():
        section = info["section"]
        cid_by_section = {s[2]: s[0] for s in SECTIONS}
        cid = cid_by_section[section]
        try:
            user = _make_request(f"courses/{cid}/users/{uid}")
            actual_name = user.get("name", "")
            if actual_name != info["name"]:
                errors.append(
                    f"ID {uid} in {section}: Canvas says {actual_name!r}, "
                    f"expected {info['name']!r}"
                )
            else:
                print(f"  VERIFIED  {info['name']} ({uid}) in {section}")
        except Exception as e:
            errors.append(f"ID {uid} in {section}: lookup failed {e}")
    return errors


def plan():
    """Return the full push plan without making any writes."""
    lines = []
    totals = {"grades": 0, "comments": 0}
    for cid, aid, label in SECTIONS:
        asn = get_assignment(cid, aid)
        asn_name = asn.get("name", "")
        asn_points = asn.get("points_possible")
        lines.append(f"\n{'=' * 70}")
        lines.append(f"{label}  course={cid}  assignment={aid}")
        lines.append(f"Assignment: {asn_name}  points_possible={asn_points}")
        assert "4/16" in asn_name, f"Assignment ID mismatch in {label}: got {asn_name}"
        assert asn_points == 10.0, f"Expected 10.0 pts in {label}, got {asn_points}"
        roster = get_roster(cid)
        lines.append(f"Roster: {len(roster)} students")
        for s in roster:
            uid = s["user_id"]
            name = s["name"]
            if uid in TARGETED_COMMENTS:
                tc = TARGETED_COMMENTS[uid]
                lines.append(
                    f"  -> GRADE {SCORE}/10 + COMMENT for {name} (uid {uid})"
                )
                lines.append(f"     Comment: {tc['comment'][:80]}...")
                totals["grades"] += 1
                totals["comments"] += 1
            else:
                lines.append(f"  -> GRADE {SCORE}/10 for {name} (uid {uid})")
                totals["grades"] += 1
    lines.append(f"\n{'=' * 70}")
    lines.append(
        f"TOTALS: {totals['grades']} grades to push, "
        f"{totals['comments']} of those with targeted comments."
    )
    return "\n".join(lines)


def publish_assignment(course_id, assignment_id):
    """Publish an unpublished assignment so grades can be posted."""
    return _make_put_request(
        f"courses/{course_id}/assignments/{assignment_id}",
        {"assignment": {"published": True}},
    )


def execute():
    """Actually post the grades and comments."""
    pushed = 0
    failed = []
    for cid, aid, label in SECTIONS:
        print(f"\n--- {label} (course {cid}, assignment {aid}) ---")
        asn = get_assignment(cid, aid)
        assert "4/16" in asn.get("name", "")
        assert asn.get("points_possible") == 10.0
        # Canvas refuses to accept grades on an unpublished assignment.
        if not asn.get("published"):
            pub = publish_assignment(cid, aid)
            print(f"  PUBLISHED  now published={pub.get('published')}")
        roster = get_roster(cid)
        for s in roster:
            uid = s["user_id"]
            name = s["name"]
            comment = None
            if uid in TARGETED_COMMENTS:
                comment = TARGETED_COMMENTS[uid]["comment"]
            try:
                post_grade(cid, aid, uid, SCORE, comment=comment)
                tag = " + COMMENT" if comment else ""
                print(f"  OK  {name:<28}  10/10{tag}")
                pushed += 1
            except Exception as e:
                print(f"  FAIL  {name:<28}  {e}")
                failed.append((label, name, uid, str(e)))
            time.sleep(0.15)  # gentle rate limit
    print(f"\nPushed {pushed} grades. Failures: {len(failed)}")
    for f in failed:
        print(f"  {f}")
    return len(failed) == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    if not (args.dry_run or args.execute) or (args.dry_run and args.execute):
        print("Pick exactly one of --dry-run or --execute")
        sys.exit(2)

    print("Verifying target students ...")
    errors = verify_targets()
    if errors:
        print("\nVERIFICATION ERRORS -- refusing to continue:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("\nBuilding plan ...")
    print(plan())

    if args.execute:
        print("\n\n==== EXECUTING NOW ====")
        ok = execute()
        sys.exit(0 if ok else 1)
    else:
        print("\n(Dry run only; re-run with --execute to push.)")


if __name__ == "__main__":
    main()
