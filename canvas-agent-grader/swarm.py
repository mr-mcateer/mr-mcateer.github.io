import os
import time
import tempfile
import requests
import PyPDF2
import docx
from PIL import Image
from bs4 import BeautifulSoup
from agents import evaluate_with_strict_agent, evaluate_with_holistic_agent, synthesize_final_grade
from canvas_api import download_attachment

def run_swarm_on_submission(submission_parts, rubric_text, points_possible=None):
    """
    Orchestrates the 3-agent grading pipeline on a multimodal submission.
    Returns a dictionary with the full multi-agent breakdown.
    """
    print("  -> Spinning up Strict Evaluator...")
    strict_eval = evaluate_with_strict_agent(submission_parts, rubric_text, points_possible)

    # Optional delay to avoid ratelimits if running many concurrently in the future
    time.sleep(15)

    print("  -> Spinning up Holistic Reviewer...")
    holistic_eval = evaluate_with_holistic_agent(submission_parts, rubric_text, points_possible)

    time.sleep(15)

    print("  -> Synthesizing final consensus...")
    final_eval = synthesize_final_grade(strict_eval, holistic_eval, rubric_text, points_possible)
    
    # Package it all together
    return {
        "strict_agent": strict_eval,
        "holistic_agent": holistic_eval,
        "final_conclusion": final_eval
    }

def format_rubric_from_canvas(canvas_rubric_obj):
    """
    Helper to convert the raw JSON rubric array from Canvas into a readable text string for the AI prompt.
    """
    if not canvas_rubric_obj:
        return "No formal rubric provided."
        
    rubric_lines = ["ASSIGNMENT RUBRIC:"]
    for criteria in canvas_rubric_obj:
        desc = criteria.get('description', 'Criterion')
        pts = criteria.get('points', 0)
        rubric_lines.append(f"- {desc} (Total points possible: {pts})")
        
        if 'ratings' in criteria:
            for rating in criteria['ratings']:
                r_desc = rating.get('description', '')
                r_pts = rating.get('points', 0)
                rubric_lines.append(f"   * {r_pts} pts: {r_desc}")
    
    return "\n".join(rubric_lines)

def scrape_url(url):
    """Attempts to scrape text from an external URL (e.g. published docs)"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except:
        return f"[Failed to scrape external URL: {url}]"

def extract_submission_parts(canvas_submission_obj):
    """
    Parses the submission and returns a list of parts (strings or PIL Images)
    to be fed directly into the Gemini model.
    """
    parts = []
    
    # 1. Base text/URL submission
    sub_type = canvas_submission_obj.get('submission_type')
    if sub_type == 'online_text_entry':
        parts.append(canvas_submission_obj.get('body', ''))
    elif sub_type in ['online_url', 'basic_lti_launch']:
        url = canvas_submission_obj.get('url', '')
        parts.append(f"Student submitted URL: {url}\n\nURL Scraped Content:\n{scrape_url(url)}")
        
    # 2. Attachments
    attachments = canvas_submission_obj.get('attachments', [])
    if attachments:
        parts.append("Student submitted the following file attachments:")
        
    for att in attachments:
        fname = att.get('display_name', 'unknown')
        url = att.get('url')
        if not url:
            continue
            
        ext = os.path.splitext(fname)[1].lower()
        
        # Download locally to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp_path = tmp.name
            
        if not download_attachment(url, tmp_path):
            parts.append(f"[Failed to download attachment: {fname}]")
            continue
            
        # Parse based on extension
        try:
            if ext == '.pdf':
                parts.append(f"--- CONTENT OF PDF: {fname} ---")
                with open(tmp_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    parts.append(text)
            elif ext in ['.docx', '.doc']:
                parts.append(f"--- CONTENT OF DOCX: {fname} ---")
                doc = docx.Document(tmp_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                parts.append(text)
            elif ext in ['.png', '.jpg', '.jpeg', '.heic']:
                parts.append(f"--- IMAGE ATTACHMENT: {fname} ---")
                img = Image.open(tmp_path)
                img.load() # load it firmly into memory so we can delete the temp file
                parts.append(img)
            else:
                parts.append(f"[Unsupported file type submitted: {fname}]")
        except Exception as e:
            parts.append(f"[Error parsing file {fname}: {e}]")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    # 3. Comment thread (instructor feedback + student responses)
    comments = canvas_submission_obj.get('submission_comments', [])
    if comments:
        parts.append("\n--- COMMENT THREAD (instructor and student communication) ---")
        parts.append("IMPORTANT: Students were told to communicate corrections, clarifications, and additional context via comments. Give credit for information provided in comments.")
        for c in comments:
            author = c.get('author_name', 'Unknown')
            body = c.get('comment', '')
            created = c.get('created_at', '')
            parts.append(f"[{created}] {author}: {body}")

    if not parts:
        return ["No content found to evaluate."]

    return parts
