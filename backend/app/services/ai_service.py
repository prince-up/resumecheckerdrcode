import json
import re
import google.generativeai as genai
from app.core.config import settings


class AIResumeAnalyzer:
    """AI Service for Resume Analysis and Optimization"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_and_optimize(self, job_description: str, resume_text: str) -> dict:
        """
        Analyze resume against job description and provide optimization suggestions
        Returns a dictionary with scores, suggestions, and optimized resume
        """
        
        prompt = f"""You are an expert AI Resume Analyzer and Career Coach.

Analyze the following resume against the job description. Be thorough and critical.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Provide a detailed analysis in JSON format with the following structure (return pure JSON only, no markdown):
{{
    "overall_score": <integer 0-10>,
    "skill_score": <integer 0-10>,
    "keyword_score": <integer 0-10>,
    "experience_score": <integer 0-10>,
    "ats_compatibility_score": <integer 0-10>,
    "matching_skills": [<list of skills from resume that match JD>],
    "missing_keywords": [<list of important keywords from JD not in resume>],
    "missing_skills": [<list of important skills from JD not mentioned in resume>],
    "strengths": [<list of 3-4 resume strengths relative to the JD>],
    "weaknesses": [<list of 3-4 resume weaknesses relative to the JD>],
    "improvement_suggestions": [<list of 5-6 specific, actionable improvement suggestions>],
    "ats_issues": [<list of ATS-related issues if any>],
    "optimized_resume": <complete optimized resume text that is:
        - More ATS-friendly
        - Better keyword-matched to the JD
        - Uses strong action verbs
        - Maintains truthfulness
        - Properly formatted with sections
        - Highlighted matching experiences>
}}

Be critical but fair. Ensure scores reflect objective analysis. Return ONLY valid JSON."""

        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(response_text)
            
            return analysis
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text: {response_text[:500]}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            raise Exception(f"AI Analysis error: {str(e)}")
    
    def generate_optimized_resume(self, original_resume: str, job_description: str) -> str:
        """Generate an optimized version of the resume"""
        
        prompt = f"""You are an expert resume writer specializing in ATS optimization.

Original Resume:
{original_resume}

Target Job Description:
{job_description}

Generate an optimized, ATS-friendly version of this resume that:
1. Incorporates key technical skills and keywords from the JD
2. Uses strong action verbs (e.g., Developed, Implemented, Managed, Optimized)
3. Maintains complete truthfulness - DO NOT add fake experience
4. Improves formatting for ATS readability
5. Highlights quantifiable achievements
6. Aligns experience with job requirements

Return ONLY the optimized resume text, properly formatted with clear sections."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Resume optimization error: {str(e)}")
