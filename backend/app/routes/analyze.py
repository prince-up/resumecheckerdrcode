from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import AIResumeAnalyzer
from app.utils.pdf_handler import PDFHandler
import io
import json

# Pydantic models
class ResumeDownloadRequest(BaseModel):
    resume_text: Optional[str] = None
    overall_score: Optional[int] = None

router = APIRouter()
analyzer = AIResumeAnalyzer()
pdf_handler = PDFHandler()

# Store the last generated resume in memory (in production, use database/cache)
last_generated_resume = None

@router.post("/analyze")
async def analyze_resume(
    job_description: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Analyze resume against job description
    
    - **job_description**: The job posting text
    - **resume_file**: PDF or text file containing the resume
    """
    try:
        # Read resume file
        file_content = await resume_file.read()
        
        # Extract text from PDF
        if resume_file.filename.lower().endswith('.pdf'):
            resume_text = pdf_handler.extract_text_from_pdf(file_content)
        else:
            # Assume it's plain text
            resume_text = file_content.decode('utf-8')
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty")
        
        # Analyze and optimize
        analysis = analyzer.analyze_and_optimize(job_description, resume_text)
        
        # Store optimized resume for download
        global last_generated_resume
        last_generated_resume = analysis.get("optimized_resume", resume_text)
        
        return {
            "success": True,
            "data": analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/download")
async def download_optimized_resume(request: ResumeDownloadRequest):
    """Download the optimized resume as PDF"""
    try:
        resume_text = request.resume_text or last_generated_resume
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="No resume text provided")
        
        # Generate PDF
        pdf_content = pdf_handler.generate_resume_pdf(resume_text)
        
        # Return PDF as bytes
        return FileResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=optimized_resume.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/download")
async def download_optimized_resume_get():
    """Download the last generated optimized resume as PDF (GET method)"""
    try:
        if not last_generated_resume:
            raise HTTPException(status_code=400, detail="No resume to download. Please analyze first.")
        
        # Generate PDF
        pdf_content = pdf_handler.generate_resume_pdf(last_generated_resume)
        
        return FileResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=optimized_resume.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Resume Analyzer"}
