# Resume Parser

Extract structured information from PDF resumes using AI (AWS Bedrock).

## Features

- **PDF Upload**: Simple UI to upload resume PDFs
- **Text Extraction**: Automatic text extraction from PDF files
- **LLM Processing**: Uses AWS Bedrock to parse resume data
- **Structured Output**: Returns JSON with:
  - Name and contact information
  - Professional summary
  - Skills (technical and soft)
  - Work experience with responsibilities
  - Projects (personal or professional with technologies)
  - Educational background
  - Certifications
  - Languages


## Quick Start

### 1. Clone and Setup

```bash
cd "Resume Parser"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.temp` to `.env` and fill in your AWS Bedrock credentials




### 4. Get AWS Bedrock Access

1. Ensure you have AWS credentials configured.
   - You can set them in `.env` using `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
2. Choose a model ID for `BEDROCK_MODEL`.


### 5. Run the Application

#### Terminal 1 - Start FastAPI Backend

```bash
python -m uvicorn backend.main:app --reload
```

Backend will be available at: http://127.0.0.1:8000

API Documentation: http://127.0.0.1:8000/docs

#### Terminal 2 - Start Streamlit Frontend

```bash
streamlit run frontend/app.py
```

Frontend will open at: http://localhost:8501

## Usage

1. Open Streamlit app at http://localhost:8501
2. Check API connection status in sidebar
3. Upload a PDF resume
4. Click "Parse Resume"
5. View extracted information:
   - Contact info
   - Professional summary
   - Skills
   - Work experience
   - Education
   - Certifications
   - Languages
6. Download results as JSON

## API Endpoints

### Health Check
```bash
GET /health
```

Returns API status and LLM provider info.

### Parse Resume
```bash
POST /parse-resume
```

**Request:**
- Content-Type: multipart/form-data
- File parameter: PDF resume file


## Troubleshooting

### Backend Not Connecting
- Ensure FastAPI is running: `python -m uvicorn backend.main:app --reload`
- Check if port 8000 is available
- Verify no firewall blocking connections

### "API key not set"
- Copy `.env.example` to `.env`
- Add your actual API keys
- Restart both frontend and backend

### PDF Extraction Failed
- Ensure PDF is not corrupted
- Try a different PDF file
- Check PDF doesn't exceed size limit

### Timeout Errors
- LLM API may be slow, wait for response
- Try smaller resumes first
- Increase timeout in backend if needed


## License

This project is open source and available under the MIT License.
