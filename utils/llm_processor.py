"""LLM processing utilities for resume parsing."""

import json
from typing import Dict, Any
import re


RESUME_PARSING_PROMPT = """Extract structured information from the following resume text and return it as JSON.

Extract the following fields:
1. name: Full name of the candidate
2. email: Email address (if available)
3. phone: Phone number (if available)
4. summary: Professional summary or objective (if available)
5. skills: List of technical and soft skills
6. experience: List of work experiences with:
   - company: Company name
   - position: Job title
   - duration: Time period (start and end dates)
   - responsibilities: Key responsibilities and achievements
7. education: List of educational qualifications with:
   - school: Institution name
   - degree: Degree type
   - field: Field of study
   - graduation_year: Year of graduation (if available)
8. projects: List of personal or professional projects with:
   - name: Project name
   - bullets: List each bullet point under the project as a separate string, same format as responsibilities in experience.
   - technologies: Technologies/tools used
   - url: GitHub or project URL (if available)
9. certifications: List of professional certifications (if available)
10. languages: List of languages spoken (if available)
11. linkedin: LinkedIn website (if available)
12. website: Personal website (if available)

Resume Text:
{resume_text}

Return ONLY valid JSON with the structure above. Use empty strings or empty lists for missing information.\n\nJSON:\n"""


def get_llm_prompt(resume_text: str) -> str:
    """
    Get the prompt for LLM resume parsing.
    
    Args:
        resume_text: Extracted resume text
        
    Returns:
        Formatted prompt for LLM
    """
    return RESUME_PARSING_PROMPT.format(resume_text=resume_text)


def parse_llm_response(response_text: str) -> dict:
    import json, re
    print("DEBUG raw input:", repr(response_text[:500]))
    response_text = response_text.strip()
    response_text = re.sub(r"^```(json)?", "", response_text)
    response_text = re.sub(r"```.*$", "", response_text, flags=re.DOTALL).strip()  # strip everything after closing ```
    print("DEBUG response_text:", repr(response_text[:500]))
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM response.")

    print("DEBUG match:", match.group()[:200])  # add this temporarily

    try:
        parsed = json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {str(e)}")

    # Fill missing fields with defaults
    fields = ["name", "skills", "experience", "education", "projects", "certifications", "languages"]
    for f in fields:
        if f not in parsed:
            parsed[f] = [] if f != "name" else ""

    return parsed

def create_bedrock_input(resume_text: str) -> dict:
    """Create AWS Bedrock input payload.

    Bedrock expects a JSON payload like {"inputText": "..."} for text models.
    """
    return {"inputText": get_llm_prompt(resume_text)}
