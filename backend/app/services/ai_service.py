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

Return ONLY a valid JSON object (no markdown formatting, no code blocks) with this exact structure:
{{
    "overall_score": (number 0-10),
    "skill_score": (number 0-10),
    "keyword_score": (number 0-10),
    "experience_score": (number 0-10),
    "ats_compatibility_score": (number 0-10),
    "matching_skills": (array of strings),
    "missing_keywords": (array of strings),
    "missing_skills": (array of strings),
    "strengths": (array of 3-4 strings),
    "weaknesses": (array of 3-4 strings),
    "improvement_suggestions": (array of 5-6 strings),
    "ats_issues": (array of strings),
    "optimized_resume": (string with the complete optimized resume text that is ATS-friendly, keyword-matched, uses action verbs)
}}

Be critical but fair. Return ONLY the JSON object, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Extract JSON from response (handle extra text before/after)
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                # Fix any trailing issues
                if not json_str.endswith('}'):
                    json_str = json_str + '}'
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(response_text)
            
            # Ensure all expected keys exist with valid defaults
            analysis.setdefault('overall_score', 5)
            analysis.setdefault('skill_score', 5)
            analysis.setdefault('keyword_score', 5)
            analysis.setdefault('experience_score', 5)
            analysis.setdefault('ats_compatibility_score', 5)
            analysis.setdefault('matching_skills', [])
            analysis.setdefault('missing_keywords', [])
            analysis.setdefault('weaknesses', [])
            analysis.setdefault('strengths', [])
            analysis.setdefault('improvement_suggestions', [])
            analysis.setdefault('ats_issues', [])
            analysis.setdefault('missing_skills', [])
            # CRITICAL: Ensure optimized_resume is always present
            analysis.setdefault('optimized_resume', resume_text)
            
            # Ensure scores are integers
            for key in ['overall_score', 'skill_score', 'keyword_score', 'experience_score', 'ats_compatibility_score']:
                if key in analysis:
                    try:
                        analysis[key] = int(analysis[key])
                        if analysis[key] > 10:
                            analysis[key] = 10
                        elif analysis[key] < 0:
                            analysis[key] = 0
                    except (ValueError, TypeError):
                        analysis[key] = 5
            
            return analysis
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text: {response_text[:500]}")
            # Return fallback structure instead of raising error
            return {
                'overall_score': 5,
                'skill_score': 5,
                'keyword_score': 5,
                'experience_score': 5,
                'ats_compatibility_score': 5,
                'matching_skills': [],
                'missing_keywords': [],
                'weaknesses': ['Could not parse response'],
                'strengths': ['Resume was analyzed'],
                'improvement_suggestions': ['Try uploading as TXT format for better analysis'],
                'ats_issues': [],
                'missing_skills': [],
                'optimized_resume': resume_text  # Use original as fallback
            }
        except Exception as e:
            print(f"AI Analysis error: {str(e)}")
            # Return fallback structure
            return {
                'overall_score': 5,
                'skill_score': 5,
                'keyword_score': 5,
                'experience_score': 5,
                'ats_compatibility_score': 5,
                'matching_skills': [],
                'missing_keywords': [],
                'weaknesses': [f'Error: {str(e)}'],
                'strengths': ['Analysis attempted'],
                'improvement_suggestions': ['Try again with different format'],
                'ats_issues': [],
                'missing_skills': [],
                'optimized_resume': resume_text  # Use original as fallback
            }
    
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
