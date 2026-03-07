import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = 'gemini-2.5-flash'

def evaluate_with_strict_agent(submission_parts, rubric_text):
    """
    Agent 1: The Strict Rubric Adherent.
    """
    prompt_intro = f"""
    You are the 'Strict Rubric Evaluator' agent. 
    Your ONLY job is to evaluate the provided student submission strictly according to the provided rubric.
    Do not give credit for effort, formatting, or tangential insights unless explicitly stated in the rubric.
    Be extremely critical and objective.
    Review the submission payload, which may contain text, URLs, and images of physical fabrication or design.

    RUBRIC:
    {rubric_text}

    STUDENT SUBMISSION (Images and/or text will follow):
    """
    
    prompt_outro = """
    Output your analysis as raw JSON (no markdown formatting, no code blocks) matching this EXACT schema:
    {
        "agent_name": "Strict Rubric Evaluator",
        "suggested_score": <numeric score>,
        "rationale": "<your detailed step-by-step reasoning based ONLY on the rubric>"
    }
    """
    
    # We feed the model a list of instructions wrapped around the actual submission pieces
    contents = [prompt_intro] + submission_parts + [prompt_outro]
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.1, 
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)


def evaluate_with_holistic_agent(submission_parts, rubric_text):
    """
    Agent 2: The Holistic Reviewer.
    """
    prompt_intro = f"""
    You are the 'Holistic Reviewer' agent. 
    While you should reference the provided rubric, your primary job is to evaluate the student's OVERALL grasp of the concept.
    Look for deep insights, effort, creativity, and critical thinking.
    If a student missed a minor technicality in the rubric but demonstrated profound understanding in their work/photos, suggest a higher score.
    Review the submission payload, which may contain text, URLs, and images of physical fabrication or design.

    RUBRIC:
    {rubric_text}

    STUDENT SUBMISSION (Images and/or text will follow):
    """
    
    prompt_outro = """
    Output your analysis as raw JSON (no markdown formatting, no code blocks) matching this EXACT schema:
    {
        "agent_name": "Holistic Reviewer",
        "suggested_score": <numeric score>,
        "rationale": "<your detailed reasoning focusing on insight, effort, and big-picture understanding>"
    }
    """
    
    contents = [prompt_intro] + submission_parts + [prompt_outro]
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.5, 
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)


def synthesize_final_grade(strict_evaluation, holistic_evaluation, rubric_text):
    """
    Agent 3: The Synthesizer (Lead Agent).
    """
    prompt = f"""
    You are the 'Lead Grading Synthesizer' agent.
    Your job is to read the reports from two specialized grading agents, resolve any discrepancies, and finalize a suggested score for the student.

    RUBRIC context:
    {rubric_text}

    AGENT 1 (Strict Rubric Adherent) REPORT:
    {json.dumps(strict_evaluation, indent=2)}

    AGENT 2 (Holistic Reviewer) REPORT:
    {json.dumps(holistic_evaluation, indent=2)}

    Determine the final fair score. If the two agents widely disagree, use your best judgment to find the middle ground or side with the stronger argument.

    Output your analysis as raw JSON (no markdown formatting, no code blocks) matching this EXACT schema:
    {{
        "final_suggested_score": <numeric score>,
        "resolution_rationale": "<an internal note explaining to the user why you chose this final score based on the two agent reports>"
    }}
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3, 
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)
