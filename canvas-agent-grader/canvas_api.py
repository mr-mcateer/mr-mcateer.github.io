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
    """Internal helper for POST requests (creating assignments, quizzes, etc.)"""
    url = f"{CANVAS_API_URL}/api/v1/{endpoint}"
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def create_assignment(course_id, params):
    """
    Creates an assignment in a course.
    params: dict with keys like name, description, points_possible,
            submission_types, published, due_at, etc.
    Returns the created assignment JSON.
    """
    payload = {'assignment': params}
    return _make_post_request(f'courses/{course_id}/assignments', payload)


def create_rubric(course_id, assignment_id, title, criteria):
    """
    Creates and associates a rubric with an assignment.
    criteria: list of dicts with keys: description, points, ratings
      ratings: list of dicts with keys: description, points
    Returns the created rubric JSON.
    """
    # Canvas expects criteria as indexed dict {"0": {...}, "1": {...}}
    criteria_payload = {}
    for i, c in enumerate(criteria):
        ratings_payload = {}
        for j, r in enumerate(c['ratings']):
            ratings_payload[str(j)] = {
                'description': r['description'],
                'points': r['points']
            }
        criteria_payload[str(i)] = {
            'description': c['description'],
            'points': c['points'],
            'ratings': ratings_payload
        }

    payload = {
        'rubric': {
            'title': title,
            'criteria': criteria_payload
        },
        'rubric_association': {
            'association_id': assignment_id,
            'association_type': 'Assignment',
            'use_for_grading': True,
            'purpose': 'grading'
        }
    }
    return _make_post_request(f'courses/{course_id}/rubrics', payload)


def create_quiz(course_id, params):
    """
    Creates a Classic Quiz in a course.
    params: dict with keys like title, description, quiz_type,
            allowed_attempts, published, etc.
    Returns the created quiz JSON.
    """
    payload = {'quiz': params}
    return _make_post_request(f'courses/{course_id}/quizzes', payload)


def create_quiz_question(course_id, quiz_id, params):
    """
    Adds a question to a Classic Quiz.
    params: dict with keys like question_name, question_text,
            question_type, points_possible, answers, etc.
    Returns the created question JSON.
    """
    payload = {'question': params}
    return _make_post_request(
        f'courses/{course_id}/quizzes/{quiz_id}/questions', payload)


def create_announcement(course_id, title, message_html, delayed_post_at=None):
    """
    Creates an announcement (discussion_topic with is_announcement=True).
    delayed_post_at: optional ISO 8601 timestamp for scheduled posting.
    Returns the created announcement JSON.
    """
    payload = {
        'title': title,
        'message': message_html,
        'is_announcement': True,
        'published': True,
    }
    if delayed_post_at:
        payload['delayed_post_at'] = delayed_post_at
    return _make_post_request(
        f'courses/{course_id}/discussion_topics', payload)


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
