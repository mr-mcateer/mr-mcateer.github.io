import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')

if not CANVAS_API_URL or not CANVAS_API_TOKEN:
    raise ValueError("Missing Canvas API credentials in .env file.")

HEADERS = {
    'Authorization': f'Bearer {CANVAS_API_TOKEN}'
}

def _make_request(endpoint, params=None):
    """Internal helper to structure and execute Canvas API GET requests."""
    url = f"{CANVAS_API_URL}/api/v1/{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def _make_put_request(endpoint, payload=None):
    """Internal helper for PUT requests (like submitting grades)"""
    url = f"{CANVAS_API_URL}/api/v1/{endpoint}"
    response = requests.put(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def _make_post_request(endpoint, payload=None):
    """Internal helper for POST requests (creating pages, assignments, etc.)"""
    url = f"{CANVAS_API_URL}/api/v1/{endpoint}"
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def get_active_courses():
    """Returns a list of active courses the user is enrolled in/teaching."""
    params = {'enrollment_state': 'active', 'per_page': 100}
    return _make_request('courses', params)


def get_course_name(course_id):
    """Fetches the name of a specific course for organization."""
    try:
        course = _make_request(f'courses/{course_id}')
        return course.get('name', f'Course_{course_id}')
    except Exception as e:
        print(f"Error fetching course name: {e}")
        return f'Course_{course_id}'


def get_assignments(course_id):
    """Returns a list of assignments for a specific course ID."""
    params = {'per_page': 100}
    return _make_request(f'courses/{course_id}/assignments', params)


def get_assignment_rubric(course_id, assignment_id):
    """
    Attempts to fetch the structured rubric for a specific assignment.
    Returns None if no rubric is attached.
    """
    try:
        assignment = _make_request(f'courses/{course_id}/assignments/{assignment_id}')
        if 'rubric' in assignment:
            return assignment['rubric']
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching assignment rubric: {e}")
        return None


def get_ungraded_submissions(course_id, assignment_id):
    """
    Returns submissions for an assignment. 
    Can be filtered to only return ungraded ones, but for now fetches all 
    and lets the client decide. 
    Includes submission history/attachments.
    """
    params = {
        'include[]': ['submission_history', 'submission_comments', 'rubric_assessment'],
        'per_page': 100
    }
    return _make_request(f'courses/{course_id}/assignments/{assignment_id}/submissions', params)


def get_student_name(course_id, user_id):
    """Fetches a specific user's name given their Canvas ID."""
    try:
        user = _make_request(f'courses/{course_id}/users/{user_id}')
        return user.get('name', f'Unknown User {user_id}')
    except:
        return f'Unknown User {user_id}'


def download_attachment(url, dest_path):
    """
    Downloads a Canvas attachment securely using the API token.
    Saves the file to dest_path. Returns True if successful.
    """
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading attachment: {e}")
        return False


def post_grade(course_id, assignment_id, user_id, grade, comment=None):
    """
    Submits a final grade and optional text comment to a specific user's submission.
    """
    payload = {
        'submission': {
            'posted_grade': grade
        }
    }
    if comment:
        payload['comment'] = {
            'text_comment': comment
        }
        
    endpoint = f"courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
    return _make_put_request(endpoint, payload)

def get_pages(course_id):
    """Returns a list of pages (wiki pages) for a course."""
    params = {'per_page': 100, 'sort': 'updated_at', 'order': 'desc'}
    return _make_request(f'courses/{course_id}/pages', params)


def get_page(course_id, page_url):
    """Returns a single page by its URL slug."""
    return _make_request(f'courses/{course_id}/pages/{page_url}')


def create_page(course_id, title, body_html, published=False, front_page=False):
    """
    Creates a new wiki page in a Canvas course.
    Body must be HTML. Set published=False to create as draft for review.
    """
    payload = {
        'wiki_page': {
            'title': title,
            'body': body_html,
            'published': published,
            'front_page': front_page
        }
    }
    return _make_post_request(f'courses/{course_id}/pages', payload)


def update_page(course_id, page_url, title=None, body_html=None, published=None):
    """Updates an existing wiki page by its URL slug."""
    payload = {'wiki_page': {}}
    if title is not None:
        payload['wiki_page']['title'] = title
    if body_html is not None:
        payload['wiki_page']['body'] = body_html
    if published is not None:
        payload['wiki_page']['published'] = published
    return _make_put_request(f'courses/{course_id}/pages/{page_url}', payload)


def create_assignment(course_id, name, description_html, points_possible=100,
                      submission_types=None, due_at=None, published=False):
    """
    Creates a new assignment in a Canvas course.
    Set published=False to create as draft for review.
    """
    payload = {
        'assignment': {
            'name': name,
            'description': description_html,
            'points_possible': points_possible,
            'submission_types': submission_types or ['online_text_entry'],
            'published': published
        }
    }
    if due_at:
        payload['assignment']['due_at'] = due_at
    return _make_post_request(f'courses/{course_id}/assignments', payload)


# Interactive testing block
if __name__ == "__main__":
    print("Testing Canvas API connection...")
    try:
        courses = get_active_courses()
        print(f"Successfully retrieved {len(courses)} active courses.")
        for c in courses[:3]:
            print(f"- {c.get('name')} (ID: {c.get('id')})")
    except Exception as e:
        print(f"Connection failed: {e}")
