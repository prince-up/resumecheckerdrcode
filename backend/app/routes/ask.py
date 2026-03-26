from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.services.ai_service import AIResumeAnalyzer
from app.utils.pdf_handler import extract_text_from_pdf
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ask", tags=["questions"])

# Initialize AI analyzer
ai_analyzer = AIResumeAnalyzer()


class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    resume_text: str
    job_description: str
    question: str


class QuestionResponse(BaseModel):
    """Response model for questions"""
    answer: str
    key_points: list
    action_items: list


@router.post("/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about a resume in context of a job description
    
    **Parameters:**
    - `resume_text`: The resume content
    - `job_description`: The job description
    - `question`: The question to ask
    
    **Returns:**
    - `answer`: Detailed answer to the question
    - `key_points`: Important points related to the answer
    - `action_items`: Actionable steps the user can take
    """
    try:
        if not request.question or len(request.question.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Question must be at least 5 characters long"
            )
        
        if not request.resume_text or len(request.resume_text.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Resume content is empty or too short"
            )
        
        if not request.job_description or len(request.job_description.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Job description is empty or too short"
            )
        
        # Get answer from AI
        response = ai_analyzer.ask_about_resume(
            request.resume_text,
            request.job_description,
            request.question
        )
        
        logger.info(f"Question answered: {request.question[:50]}")
        
        return QuestionResponse(
            answer=response.get('answer', ''),
            key_points=response.get('key_points', []),
            action_items=response.get('action_items', [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_question: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/upload-and-ask")
async def upload_and_ask(
    job_description: str = Form(...),
    question: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Upload a resume file and ask a question in one request
    
    **Parameters:**
    - `job_description`: The job description (form field)
    - `question`: The question to ask (form field)
    - `resume_file`: Resume file to upload (PDF or TXT)
    
    **Returns:**
    - Same as `/question` endpoint
    """
    try:
        # Read file content
        file_content = await resume_file.read()
        
        # Extract text based on file type
        if resume_file.content_type == 'application/pdf':
            try:
                resume_text = extract_text_from_pdf(file_content)
            except Exception as pdf_e:
                logger.warning(f"PDF extraction failed: {pdf_e}")
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from PDF. Please upload a TXT file instead."
                )
        else:
            # Assume it's text
            resume_text = file_content.decode('utf-8')
        
        # Validate content
        if not resume_text or len(resume_text.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Resume file is empty or too small"
            )
        
        # Ask question
        response = ai_analyzer.ask_about_resume(
            resume_text,
            job_description,
            question
        )
        
        logger.info(f"Question answered with file upload: {question[:50]}")
        
        return QuestionResponse(
            answer=response.get('answer', ''),
            key_points=response.get('key_points', []),
            action_items=response.get('action_items', [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_and_ask: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )
