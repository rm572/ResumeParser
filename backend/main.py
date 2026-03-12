"""FastAPI backend for Resume Parser application."""

import sys
import os
import json
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import HTTPException
import boto3
from config.settings import settings
from utils.llm_processor import get_llm_prompt

print("MODEL: ")
print(os.getenv("BEDROCK_MODEL"))

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from utils.pdf_extractor import extract_text_from_pdf, validate_pdf
from utils.llm_processor import get_llm_prompt, parse_llm_response


# Validate settings on startup
settings.validate()


# Initialize FastAPI app
app = FastAPI(
    title="Resume Parser API",
    description="Extract structured information from PDF resumes using LLM",
    version="1.0.0"
)

# Add CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def call_bedrock(resume_text: str) -> str:
    import boto3, json, asyncio

    def _invoke():
        client = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)
        payload = json.dumps({
            "prompt": get_llm_prompt(resume_text),
            "max_gen_len": 2048,
        })
        response = client.invoke_model(
            modelId=settings.BEDROCK_MODEL,
            contentType="application/json",
            accept="application/json",
            body=payload.encode("utf-8")
        )
        body = response.get("body")
        if hasattr(body, "read"):
            body = body.read()
        body_text = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else str(body)

        print("DEBUG raw body_text:", repr(body_text[:300]))  # add this

        parsed = json.loads(body_text)
        print("DEBUG parsed keys:", parsed.keys())  # add this
        print("DEBUG generation:", repr(parsed.get("generation", "KEY NOT FOUND")[:200]))  # add this

        generation = parsed["generation"]
        return generation

    return await asyncio.to_thread(_invoke)



@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": "bedrock",
        "model": settings.BEDROCK_MODEL,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }



@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse a resume PDF file and extract structured information.
    
    Args:
        file: PDF file upload
        
    Returns:
        JSON with parsed resume data
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Validate file type
        if file.filename and not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(file_content) > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Validate PDF
        if not validate_pdf(file_content):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(file_content)
        
        # Call Bedrock for resume parsing
        llm_response = await call_bedrock(resume_text)

        # Parse LLM response
        parsed_resume = parse_llm_response(llm_response)
        
        # Optional: Save to DynamoDB
        if settings.USE_DYNAMODB:
            await save_to_dynamodb(parsed_resume, file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "data": parsed_resume,
            "provider": "bedrock",
            "model": settings.BEDROCK_MODEL
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )


async def save_to_dynamodb(resume_data: dict, filename: str) -> bool:
    """
    Save parsed resume to DynamoDB.
    
    Args:
        resume_data: Parsed resume data
        filename: Original filename
        
    Returns:
        True if successful
    """
    try:
        import boto3
        from datetime import datetime
        
        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        table = dynamodb.Table(settings.DYNAMODB_TABLE)
        
        table.put_item(
            Item={
                "id": f"{filename}_{datetime.now().timestamp()}",
                "filename": filename,
                "data": resume_data,
                "created_at": datetime.now().isoformat()
            }
        )
        return True
    except Exception as e:
        print(f"Warning: Failed to save to DynamoDB: {str(e)}")
        return False


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "POST /parse-resume": "Parse a PDF resume and extract structured data",
            "GET /health": "Health check endpoint",
            "GET /": "API information"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True
    )
