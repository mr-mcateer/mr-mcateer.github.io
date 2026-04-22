#!/usr/bin/env python3
"""
Teaching countdown timer for McAteer shop classes.

Schedule:
  Mon = ALL day (50min P1, 45min P3/P5)
  Tue = ODD day (90min all periods)
  Thu = ODD day (90min all periods)
  Wed/Fri = EVEN (prep, no classes)

Key dates:
  Apr 16-17: No school
  Apr 14: Early Release ODD
  May 25: Memorial Day
  Jun 11: Last day of school

Usage:
    python countdown.py
"""
from datetime import date, timedelta
import sys

# -- CONFIG --
LAST_DAY = date(2026, 6, 11)

NO_SCHOOL = {
    date(2026, 4, 16),
    date(2026, 4, 17),
    date(2026, 5, 25),  # Memorial Day
}

EARLY_RELEASE = {
    date(2026, 4, 14),  # Early Release ODD
}

# Teaching days: Mon=0, Tue=1, Thu=3
TEACHING_WEEKDAYS = {0, 1, 3}

def day_type(d):
    wd = d.weekday()
    if d in NO_SCHOOL:
        return None
    if wd == 0:
        return "ALL"
    if wd in (1, 3):
        if d in EARLY_RELEASE:
            return "EARLY_ODD"
        return "ODD"
    return None  # Wed/Fri = prep

def minutes_for(dtype):
    return {
        "ALL": {"P1": 50, "P3": 45, "P5": 45},
        "ODD": {"P1": 90, "P3": 90, "P5": 90},
        "EARLY_ODD": {"P1": 60, "P3": 60, "P5": 60},
    }.get(dtype, {})

def get_teaching_days(start, end):
    days = []
    d = start
    while d <= end:
        dt = day_type(d)
        if dt:
            days.append((d, dt))
        d += timedelta(days=1)
    return days

def main():
    today = date.today()
    remaining = get_teaching_days(today, LAST_DAY)

    if not remaining:
        print("No teaching days remaining.")
        return

    total_days = len(remaining)
    odd_days = sum(1 for _, dt in remaining if dt in ("ODD", "EARLY_ODD"))
    all_days = sum(1 for _, dt in remaining if dt == "ALL")

    total_p1_min = sum(minutes_for(dt).get("P1", 0) for _, dt in remaining)
    total_p3_min = sum(minutes_for(dt).get("P3", 0) for _, dt in remaining)

    calendar_days = (LAST_DAY - today).days

    # Find next teaching day
    next_day = remaining[0] if remaining else None

    print()
    print("=" * 58)
    print("  MCATEER SHOP -- TEACHING COUNTDOWN")
    print("=" * 58)
    print(f"  Today:          {today.strftime('%A, %B %d, %Y')}")
    if next_day:
        nd, ndt = next_day
        if nd == today:
            print(f"  Today's type:   {ndt} day ({minutes_for(ndt).get('P1',0)} min periods)")
        else:
            print(f"  Next class:     {nd.strftime('%A %b %d')} ({ndt})")
    print(f"  Last day:       {LAST_DAY.strftime('%A, %B %d, %Y')}")
    print("-" * 58)
    print(f"  Calendar days left:    {calendar_days}")
    print(f"  Teaching days left:    {total_days}")
    print(f"    ODD days (90 min):   {odd_days}")
    print(f"    ALL days (50/45):    {all_days}")
    print("-" * 58)
    print(f"  P1 Autos minutes left: {total_p1_min:,} min ({total_p1_min/60:.1f} hrs)")
    print(f"  P3 Metals minutes left:{total_p3_min:,} min ({total_p3_min/60:.1f} hrs)")
    print(f"  P5 Metals minutes left:{total_p3_min:,} min ({total_p3_min/60:.1f} hrs)")
    print("=" * 58)

    # Weekly breakdown
    print()
    print("  WEEK-BY-WEEK REMAINING")
    print("-" * 58)

    from collections import defaultdict
    weeks = defaultdict(list)
    for d, dt in remaining:
        week_start = d - timedelta(days=d.weekday())
        weeks[week_start].append((d, dt))

    for ws in sorted(weeks):
        we = ws + timedelta(days=4)
        days_in_week = weeks[ws]
        day_labels = []
        for d, dt in days_in_week:
            label = d.strftime("%a")
            if dt == "EARLY_ODD":
                label += "(early)"
            day_labels.append(label)
        week_min = sum(minutes_for(dt).get("P1", 0) for _, dt in days_in_week)
        print(f"  {ws.strftime('%b %d')} - {we.strftime('%b %d')}:  {', '.join(day_labels):20s}  {len(days_in_week)} days  {week_min} min P1")

    print("=" * 58)

    # Progress bar
    total_school_days = len(get_teaching_days(date(2026, 1, 6), LAST_DAY))  # approx semester start
    elapsed = total_school_days - total_days
    pct = (elapsed / total_school_days) * 100 if total_school_days else 0
    bar_len = 40
    filled = int(bar_len * pct / 100)
    bar = "#" * filled + "-" * (bar_len - filled)
    print(f"\n  Semester progress: [{bar}] {pct:.0f}%")
    print(f"  {elapsed} days taught / {total_school_days} total")
    print()


if __name__ == "__main__":
    main()
