#!/usr/bin/env python3
"""
canvas_publisher.py -- Asynchronous Curriculum Pipeline

Translates structured agenda data into Canvas LMS pages and assignments.
Designed to be called by the cvhs-teacher subagent after a /dispatch
captures a curriculum idea.

Usage:
    python canvas_publisher.py agenda --course COURSE_ID --date 2026-03-31 --json agenda.json
    python canvas_publisher.py exit-ticket --course COURSE_ID --date 2026-03-31 --json ticket.json

The --json file contains the structured output from the cvhs-teacher agent.
All content is pushed as DRAFT (unpublished) for teacher review.

Requires: CANVAS_API_URL and CANVAS_API_TOKEN in ../.env
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from html import escape as html_escape
from urllib.parse import urlparse

# Add parent directory so we can import canvas_api from the same package
sys.path.insert(0, os.path.dirname(__file__))
from canvas_api import create_page, create_assignment, get_pages, update_page


def _safe(text):
    """Escape user input for safe HTML embedding."""
    return html_escape(str(text))


def _safe_url(url):
    """Validate and escape a URL. Reject javascript: and data: protocols."""
    parsed = urlparse(url)
    if parsed.scheme in ('javascript', 'data', 'vbscript', ''):
        if not url.startswith(('#', '/', 'http://', 'https://', 'mailto:')):
            return '#'
    return html_escape(url, quote=True)


def _slugify(text):
    """Generate a Canvas-compatible URL slug from a title."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # strip non-alphanumeric
    slug = re.sub(r'[\s]+', '-', slug)          # spaces to hyphens
    slug = re.sub(r'-+', '-', slug)             # collapse consecutive hyphens
    slug = slug.strip('-')                       # trim leading/trailing hyphens
    return slug


def build_agenda_html(agenda):
    """
    Converts a structured agenda dict into clean Canvas-ready HTML.

    Expected agenda format:
    {
        "title": "Brake Pad Replacement",
        "course_name": "Autos 101",
        "date": "2026-03-31",
        "objective": "Understand and execute safe brake pad replacement.",
        "safety_focus": "Caliper pin inspection and lubrication.",
        "materials": ["Brake pads", "C-clamp", "Socket set"],
        "procedure": ["Step 1...", "Step 2..."],
        "media": [{"label": "Demo Video", "url": "https://..."}],
        "notes": "Optional teacher notes"
    }
    """
    title = agenda.get('title', 'Untitled Agenda')
    date = agenda.get('date', datetime.now().strftime('%Y-%m-%d'))
    objective = agenda.get('objective', '')
    safety = agenda.get('safety_focus', '')
    materials = agenda.get('materials', [])
    procedure = agenda.get('procedure', [])
    media = agenda.get('media', [])
    notes = agenda.get('notes', '')

    html_parts = []

    # Header
    html_parts.append(f'<h2>{_safe(title)}</h2>')
    html_parts.append(f'<p><strong>Date:</strong> {_safe(date)}</p>')

    # Objective
    if objective:
        html_parts.append('<h3>Objective</h3>')
        html_parts.append(f'<p>{_safe(objective)}</p>')

    # Safety
    if safety:
        html_parts.append('<h3>Safety Focus</h3>')
        html_parts.append(
            f'<p style="background-color:#fff3cd;padding:10px;'
            f'border-left:4px solid #ffc107;">{_safe(safety)}</p>'
        )

    # Materials
    if materials:
        html_parts.append('<h3>Materials</h3><ul>')
        for item in materials:
            html_parts.append(f'<li>{_safe(item)}</li>')
        html_parts.append('</ul>')

    # Procedure
    if procedure:
        html_parts.append('<h3>Procedure</h3><ol>')
        for step in procedure:
            html_parts.append(f'<li>{_safe(step)}</li>')
        html_parts.append('</ol>')

    # Media
    if media:
        html_parts.append('<h3>Resources</h3><ul>')
        for m in media:
            label = _safe(m.get('label', 'Link'))
            url = _safe_url(m.get('url', '#'))
            html_parts.append(
                f'<li><a href="{url}" target="_blank">{label}</a></li>'
            )
        html_parts.append('</ul>')

    # Notes
    if notes:
        html_parts.append('<h3>Teacher Notes</h3>')
        html_parts.append(f'<p><em>{_safe(notes)}</em></p>')

    return '\n'.join(html_parts)


def build_exit_ticket_html(ticket):
    """
    Converts a structured exit ticket dict into Canvas assignment HTML.

    Expected format:
    {
        "title": "Brake Fluid Types",
        "questions": [
            "What is the difference between DOT 3 and DOT 4 brake fluid?",
            "Why is it important to check caliper pins during pad replacement?",
            "Name two signs that brake pads need replacement."
        ],
        "points": 10
    }
    """
    title = ticket.get('title', 'Exit Ticket')
    questions = ticket.get('questions', [])

    html_parts = [f'<h2>Exit Ticket: {_safe(title)}</h2>']
    html_parts.append('<p>Answer each question in 2-3 sentences.</p>')
    html_parts.append('<ol>')
    for q in questions:
        html_parts.append(f'<li>{_safe(q)}</li>')
    html_parts.append('</ol>')

    return '\n'.join(html_parts)


def publish_agenda(course_id, date_str, agenda_data):
    """Push a formatted agenda to Canvas as a draft page."""
    title = f"Agenda: {agenda_data.get('title', 'Untitled')} ({date_str})"
    body = build_agenda_html(agenda_data)

    # Check if a page with this date already exists (update vs create)
    slug = _slugify(title)
    existing_pages = get_pages(course_id)
    existing_slugs = {p.get('url', ''): p for p in existing_pages}

    if slug in existing_slugs:
        result = update_page(course_id, slug, title=title, body_html=body)
        print(f"Updated existing draft page: {title}")
    else:
        result = create_page(course_id, title, body, published=False)
        print(f"Created draft page: {title}")

    return result


def publish_exit_ticket(course_id, date_str, ticket_data):
    """Push an exit ticket to Canvas as a draft assignment."""
    title = f"Exit Ticket: {ticket_data.get('title', 'Untitled')} ({date_str})"
    body = build_exit_ticket_html(ticket_data)
    points = ticket_data.get('points', 10)

    result = create_assignment(
        course_id,
        name=title,
        description_html=body,
        points_possible=points,
        submission_types=['online_text_entry'],
        published=False
    )
    print(f"Created draft assignment: {title} ({points} pts)")
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Canvas Curriculum Publisher -- push agendas and exit tickets as drafts'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # AGENDA
    agenda_parser = subparsers.add_parser('agenda', help='Push a daily agenda as a draft Canvas page')
    agenda_parser.add_argument('--course', required=True, help='Canvas Course ID')
    agenda_parser.add_argument('--date', required=True, help='Agenda date (YYYY-MM-DD)')
    agenda_parser.add_argument('--json', required=True, help='Path to agenda JSON file')

    # EXIT TICKET
    ticket_parser = subparsers.add_parser('exit-ticket', help='Push an exit ticket as a draft Canvas assignment')
    ticket_parser.add_argument('--course', required=True, help='Canvas Course ID')
    ticket_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
    ticket_parser.add_argument('--json', required=True, help='Path to exit ticket JSON file')

    args = parser.parse_args()

    # Load JSON
    try:
        with open(args.json, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.json}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.json}: {e}")
        sys.exit(1)

    if args.command == 'agenda':
        result = publish_agenda(args.course, args.date, data)
        print(f"Canvas page URL: {result.get('html_url', 'N/A')}")
    elif args.command == 'exit-ticket':
        result = publish_exit_ticket(args.course, args.date, data)
        print(f"Canvas assignment URL: {result.get('html_url', 'N/A')}")


if __name__ == '__main__':
    main()
