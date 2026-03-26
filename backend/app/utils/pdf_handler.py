import io
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


class PDFHandler:
    """Handle PDF reading and writing operations"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file with multiple fallbacks"""
        try:
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            # Check if PDF has pages
            if len(pdf_reader.pages) == 0:
                raise Exception("PDF has no pages")
            
            text = ""
            extraction_chars = 0
            
            # Try extracting text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        extraction_chars += len(page_text)
                except Exception as page_error:
                    # Log but continue with other pages
                    pass
            
            # If very little text extracted, might be image-based PDF
            if extraction_chars < 20:
                raise Exception(f"PDF appears to be image-based or scanned (only {extraction_chars} characters extracted)")
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def generate_resume_pdf(resume_text: str, filename: str = "optimized_resume.pdf") -> bytes:
        """Generate PDF from resume text"""
        try:
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=14,
                textColor='#1a1a1a',
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=11,
                textColor='#2c3e50',
                spaceAfter=6,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=10,
                alignment=TA_JUSTIFY,
                spaceAfter=6,
                leading=12
            )
            
            # Parse and format resume content
            story = []
            lines = resume_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 0.1*inch))
                    continue
                
                # Simple heuristic: lines in ALL CAPS or with ** are headings
                if line.isupper() or '**' in line:
                    clean_line = line.replace('**', '')
                    story.append(Paragraph(clean_line, heading_style))
                else:
                    story.append(Paragraph(line, body_style))
            
            doc.build(story)
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
        
        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")
