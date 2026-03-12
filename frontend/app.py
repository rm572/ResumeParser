"""Streamlit frontend for Resume Parser application."""

import streamlit as st
import requests
import json
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


# Page configuration
st.set_page_config(
    page_title="Resume Parser",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        max-width: 1200px;
    }
    .stButton button {
        width: 100%;
        padding: 0.5rem;
        font-size: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def get_api_url() -> str:
    """Get FastAPI backend URL."""
    return f"http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}"


def check_api_health() -> bool:
    """Check if FastAPI backend is running."""
    try:
        response = requests.get(f"{get_api_url()}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def upload_and_parse_resume(file_data: bytes, filename: str) -> Optional[Dict[str, Any]]:
    """
    Upload resume to backend and get parsed results.
    
    Args:
        file_data: PDF file content
        filename: Original filename
        
    Returns:
        Parsed resume data or None if error
    """
    try:
        files = {"file": (filename, file_data, "application/pdf")}
        response = requests.post(
            f"{get_api_url()}/parse-resume",
            files=files,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.ConnectionError:
        st.error("Cannot connect to backend. Make sure FastAPI is running.")
        return None
    except requests.Timeout:
        st.error("Request timed out. Resume may be too large.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def display_resume_data(data: Dict[str, Any]):
    """Display parsed resume data in Streamlit."""
    
    resume_data = data.get("data", {})
    
    # Header with name and contact info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        name = resume_data.get("name", "Unknown")
        st.title(f"{name}")
    
    with col2:
        st.metric("Provider", data.get("provider", "N/A").upper())
    
    # Contact Information
    if any([resume_data.get("email"), resume_data.get("phone"), resume_data.get("linkedin"), resume_data.get("website")]):
        with st.expander("Contact Information", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            if resume_data.get("email"):
                with col1:
                    st.markdown(f"**Email:** {resume_data.get('email', 'N/A')}")
            
            if resume_data.get("phone"):
                with col2:
                    st.markdown(f"**Phone:** {resume_data.get('phone', 'N/A')}")
            if resume_data.get("linkedin"):
                with col3:
                    st.markdown(f"**LinkedIn:** {resume_data.get('linkedin', 'N/A')}")   
                    
            if resume_data.get("website"):
                with col4:
                    st.markdown(f"**Website:** {resume_data.get('wensite', 'N/A')}")                  
    
    # Professional Summary
    if resume_data.get("summary"):
        with st.expander("Professional Summary", expanded=False):
            st.write(resume_data.get("summary"))
    
    # Skills
    if resume_data.get("skills"):
        with st.expander("Skills", expanded=True):
            skills = resume_data.get("skills", [])
            
            if isinstance(skills, list) and skills:
                # Display skills in columns
                cols = st.columns(3)
                for idx, skill in enumerate(skills):
                    with cols[idx % 3]:
                        st.markdown(f"- {skill}")
            else:
                st.write("No skills found")
    
    # Experience
    if resume_data.get("experience"):
        with st.expander("Work Experience", expanded=True):
            experiences = resume_data.get("experience", [])
            
            if isinstance(experiences, list) and experiences:
                for idx, exp in enumerate(experiences):
                    st.markdown(f"### {exp.get('position', 'Position')} @ {exp.get('company', 'Company')}")
                    st.markdown(f"**Duration:** {exp.get('duration', 'N/A')}")
                    
                    if exp.get("responsibilities"):
                        st.markdown("**Responsibilities:**")
                        responsibilities = exp.get("responsibilities", [])
                        if isinstance(responsibilities, list):
                            for resp in responsibilities:
                                st.markdown(f"- {resp}")
                        else:
                            st.write(responsibilities)
                    
                    if idx < len(experiences) - 1:
                        st.divider()
            else:
                st.write("No experience found")
    
    # Education
    if resume_data.get("education"):
        with st.expander("Education", expanded=True):
            education = resume_data.get("education", [])
            
            if isinstance(education, list) and education:
                for idx, edu in enumerate(education):
                    st.markdown(f"### {edu.get('school', 'School')}")
                    st.markdown(f"**Degree:** {edu.get('degree', 'N/A')}")
                    st.markdown(f"**Field:** {edu.get('field', 'N/A')}")
                    
                    if edu.get("graduation_year"):
                        st.markdown(f"**Graduated:** {edu.get('graduation_year')}")
                    
                    if idx < len(education) - 1:
                        st.divider()
            else:
                st.write("No education found")
    
    # Projects
    if resume_data.get("projects"):
        with st.expander("Projects", expanded=True):
            projects = resume_data.get("projects", [])
            
            if isinstance(projects, list) and projects:
                for idx, proj in enumerate(projects):
                    st.markdown(f"### {proj.get('name', 'Project')}")
                    
                    # if proj.get("description"):
                    #     st.markdown(f"**Description:** {proj.get('description')}")
                    if proj.get("bullets"):
                        st.markdown("**Description:**")
                        desc = proj.get("bullets", [])
                        if isinstance(desc, list):
                            for d in desc:
                                st.markdown(f"- {d}")
                        else:
                            st.write(desc)                    
                    
                    if proj.get("technologies"):
                        tech = proj.get("technologies", [])
                        if isinstance(tech, list):
                            st.markdown(f"**Technologies:** {', '.join(tech)}")
                        else:
                            st.markdown(f"**Technologies:** {tech}")
                    
                    if proj.get("url"):
                        st.markdown(f"**URL:** [{proj.get('url')}]({proj.get('url')})")
                    
                    if idx < len(projects) - 1:
                        st.divider()
            else:
                st.write("No projects found")
    
    # Certifications
    if resume_data.get("certifications"):
        with st.expander("Certifications", expanded=False):
            certifications = resume_data.get("certifications", [])
            
            if isinstance(certifications, list) and certifications:
                for cert in certifications:
                    st.markdown(f"- {cert}")
            else:
                st.write("No certifications found")
    
    # Languages
    if resume_data.get("languages"):
        with st.expander("Languages", expanded=False):
            languages = resume_data.get("languages", [])
            
            if isinstance(languages, list) and languages:
                for lang in languages:
                    st.markdown(f"- {lang}")
            else:
                st.write("No languages found")
    
    # Download as JSON
    st.divider()
    st.download_button(
        label="Download as JSON",
        data=json.dumps(resume_data, indent=2),
        file_name=f"resume_parsed_{data.get('filename', 'resume').replace('.pdf', '')}.json",
        mime="application/json"
    )


def main():
    """Main Streamlit application."""
    
    # Sidebar
    with st.sidebar:
        st.title("Settings")
        
        # API Status
        api_status = check_api_health()
        status_color = "🟢" if api_status else "🔴"
        st.markdown(f"{status_color} **API Status:** {'Connected' if api_status else 'Disconnected'}")
        
        st.markdown(f"**Backend URL:** {get_api_url()}")
        st.markdown(f"**Bedrock Model:** {settings.BEDROCK_MODEL}")
        
        if not api_status:
            st.warning("Backend is not running. Please start FastAPI backend first.")
    
    # Main content
    st.header("Resume Parser")
    st.markdown("""
    Welcome to the Resume Parser! Upload a PDF resume to extract structured information
    including name, skills, experience, education, and more using AI.
    """)
    
    if not check_api_health():
        st.error("Backend API is not running. Please start the FastAPI backend first.")
        st.markdown("""
        To start the backend, run:
        ```bash
        python backend/main.py
        ```
        """)
        return
    
    # File upload
    st.divider()
    st.subheader("Upload Resume")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF resume",
        type="pdf",
        help=f"Maximum file size: {settings.MAX_FILE_SIZE_MB}MB"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Name", uploaded_file.name)
        
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        # Parse button
        if st.button("Parse Resume", use_container_width=True):
            with st.spinner("Parsing resume..."):
                file_data = uploaded_file.read()
                result = upload_and_parse_resume(file_data, uploaded_file.name)
                
                if result and result.get("status") == "success":
                    st.success("Resume parsed successfully!")
                    st.divider()
                    
                    # Store result in session state for display
                    st.session_state.parse_result = result
                    st.session_state.show_results = True
    
    # Display results if available
    if st.session_state.get("show_results") and st.session_state.get("parse_result"):
        st.divider()
        st.subheader("Parsed Resume Data")
        display_resume_data(st.session_state.parse_result)


if __name__ == "__main__":
    # Initialize session state
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "parse_result" not in st.session_state:
        st.session_state.parse_result = None
    
    main()
