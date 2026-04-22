#!/usr/bin/env python3
"""
Canvas deployment for April 2, 2026 (Thursday).

Autos: Course reset announcement + catch-up day
Metals: Guided mill practice day

Usage:
    python deploy_april2.py              # dry-run
    python deploy_april2.py --execute    # push to Canvas
"""
import sys
import time
import os

sys.path.insert(0, os.path.dirname(__file__))

from canvas_api import create_announcement

DRY_RUN = "--execute" not in sys.argv

AUTOS_COURSES = {
    23124: "P1 Engines Fab 1",
    23344: "P1 Engines Fab 2",
}

METALS_COURSES = {
    23164: "P3 Metals 1",
    23132: "P3 Metals 2",
    23157: "P3 Metals 3",
    23188: "P5 Metals 1",
    23177: "P5 Metals 2",
}


# ======================================================================
# CONTENT: Autos -- Course Reset Announcement
# ======================================================================

AUTOS_ANNOUNCEMENT_TITLE = "Automotive Manufacturing -- Where We Are and What's Next"

AUTOS_ANNOUNCEMENT_HTML = """<h2>AUTOMOTIVE MANUFACTURING | 04.02.2026</h2>

<h3>Real Talk: Where We Stand</h3>
<p>We have covered a lot of ground this semester. Engine teardowns. Oil changes. Brakes.
Six modules on what it really costs to own a car. That was intentional -- you cannot work
on something you do not understand, and you cannot afford something you have not planned for.</p>

<p>Starting today, we are tightening up. The research phase is wrapping up.
The remaining weeks are shop-heavy. Here is the plan:</p>

<ul>
  <li><strong>Today (Thursday):</strong> Catch up on any outstanding Canvas work.
      "03 -- The Real Price Tag" is due tonight. If you are current, start organizing
      your portfolio -- teardown photos, lab write-ups, build sheet.</li>
  <li><strong>Next week:</strong> New hands-on unit begins. Details coming Monday.</li>
  <li><strong>Final weeks:</strong> Capstone project and portfolio showcase.</li>
</ul>

<h3>Today's Expectations</h3>
<ol>
  <li>Open Canvas. Check your grades. What is missing?</li>
  <li>If you owe work -- get it done. No excuses, no YouTube, no free browsing.</li>
  <li>If you are caught up -- organize your portfolio. Clean up your teardown
      documentation. Make it something you would show an employer.</li>
  <li>"03 -- The Real Price Tag" is due by end of day.</li>
</ol>

<h3>Coming Up</h3>
<p>The rest of this course is hands-on. We are done with worksheets. But you need
to be current to move forward -- today is your window.</p>

<p><strong>EXIT TICKET:</strong> Before you leave, show Mr. McAteer your Canvas.
Are you caught up? What is your plan for next class?</p>
"""


# ======================================================================
# CONTENT: Metals -- Guided Mill Practice
# ======================================================================

METALS_ANNOUNCEMENT_TITLE = "Metals -- Guided Mill Practice"

METALS_ANNOUNCEMENT_HTML = """<h2>METALS &amp; FABRICATION | 04.02.2026</h2>

<h3>Bell Work</h3>
<p>Quick-write (3 minutes): What did you learn on the mill this week?
What still feels uncomfortable? Write it down -- this is for you, not a grade.</p>

<h3>Today's Focus: Guided Mill Practice</h3>
<ul>
  <li>If you have not run the Haas yet, today is the day. See Bob first.</li>
  <li>Mill stations: practice facing and edge-finding on scrap stock</li>
  <li>If you are comfortable on the mill, continue your Bookend project</li>
</ul>

<h3>Shop Expectations</h3>
<ul>
  <li>Bob is in the shop. Use him. Ask questions before you cut.</li>
  <li>Measure twice. Cut once. If you are unsure, ask.</li>
  <li>Clean your station before you leave. Leave it better than you found it.</li>
</ul>

<p><strong>EXIT TICKET:</strong> Before you leave, show Mr. McAteer one thing
you machined today. What is your plan for next class?</p>
"""


# ======================================================================
# DEPLOYMENT
# ======================================================================

def deploy_announcements():
    """Post announcements to all courses."""
    print("\n--- Announcements ---\n")

    # Schedule for Thursday 7 AM Pacific
    delay = "2026-04-02T07:00:00-07:00"

    # Autos
    for cid, name in AUTOS_COURSES.items():
        tag = f"[{name} ({cid})]"
        if DRY_RUN:
            print(f"[DRY RUN] {tag} CREATE announcement: {AUTOS_ANNOUNCEMENT_TITLE}")
            print(f"           Scheduled: {delay}")
        else:
            create_announcement(cid, AUTOS_ANNOUNCEMENT_TITLE, AUTOS_ANNOUNCEMENT_HTML, delayed_post_at=delay)
            print(f"[CREATED] {tag} announcement: {AUTOS_ANNOUNCEMENT_TITLE}")
            time.sleep(0.15)

    # Metals
    for cid, name in METALS_COURSES.items():
        tag = f"[{name} ({cid})]"
        if DRY_RUN:
            print(f"[DRY RUN] {tag} CREATE announcement: {METALS_ANNOUNCEMENT_TITLE}")
            print(f"           Scheduled: {delay}")
        else:
            create_announcement(cid, METALS_ANNOUNCEMENT_TITLE, METALS_ANNOUNCEMENT_HTML, delayed_post_at=delay)
            print(f"[CREATED] {tag} announcement: {METALS_ANNOUNCEMENT_TITLE}")
            time.sleep(0.15)

    print()


def run():
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    print(f"\n{'='*60}")
    print(f"  Canvas April 2 Deployment  [{mode}]")
    print(f"{'='*60}")
    print(f"  Autos courses:  {list(AUTOS_COURSES.values())}")
    print(f"  Metals courses: {list(METALS_COURSES.values())}")
    print(f"{'='*60}")

    deploy_announcements()

    print(f"{'='*60}")
    print(f"  Done! [{mode}]")
    if DRY_RUN:
        print(f"  Re-run with --execute to push to Canvas.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
