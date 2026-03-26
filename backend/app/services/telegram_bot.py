"""
Telegram Bot Integration for AI Resume Analyzer
Handles user interactions and resume analysis on Telegram
"""

import logging
from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.core.config import settings
from app.services.ai_service import AIResumeAnalyzer
from app.utils.pdf_handler import PDFHandler
import io
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize services
ai_analyzer = AIResumeAnalyzer()
pdf_handler = PDFHandler()


class TelegramResumeBot:
    def __init__(self, token: str):
        self.token = token
        self.app = None
        self.user_jobs = {}  # Store job descriptions by user
        self.user_files = {}  # Store uploaded files by user
        self.user_resumes = {}  # Store optimized resumes by user
        self.expecting_jd_file = {} # Store expectation of JD file upload state
        self.user_job_files = {} # Store uploaded JD files

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        welcome_message = """
🤖 Welcome to AI Resume Analyzer Bot!

I'll help you optimize your resume for any job description.

**How to use:**
1. Send /setjob <job description> - Provide the job you're applying for
2. Upload your resume (PDF or text file)
3. I'll analyze and provide:
   • Overall match score (0-10)
   • Skills match analysis
   • Keywords suggestions
   • Experience alignment
   • ATS compatibility score
   • Strengths and weaknesses
   • Improvement suggestions

**Commands:**
/start - Show this message
/setjob - Set job description
/analyze - Analyze your resume
/help - More information

Example:
/setjob Senior Python Developer - FastAPI, MongoDB, AWS experience required

Then upload your resume file!
        """
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📋 <b>AI Resume Analyzer Help</b>

<b>Quick Start (3 Steps):</b>
1️⃣ /setjob Your job description
2️⃣ Upload your resume file (PDF or TXT)
3️⃣ /analyze to get results!

<b>Additional Commands:</b>
/download - Download optimized resume as PDF
/ask <question> - Ask questions about your resume!

<b>What You Get:</b>
✅ Overall Match Score (0-10)
✅ Matching Skills List
✅ Missing Keywords
✅ Experience Alignment
✅ ATS Compatibility Score
✅ Strengths & Areas to Improve
✅ Optimization Suggestions

<b>Example Usage:</b>
/setjob Senior Python Developer with FastAPI
(Upload resume file)
/analyze
/ask Should I highlight Docker experience more?
/ask How well does my resume match this role?

<b>Tips:</b>
• Be specific with job descriptions
• Use clear, well-formatted resumes
• Ask any CV-related questions!

Need help? Contact support!
        """
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def set_job(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setjob command"""
        user_id = update.effective_user.id

        if not context.args:
            await update.message.reply_text(
                "Please provide a job description text.\n\n"
                "Usage: /setjob <job description>\n"
                "Example: /setjob Senior Python Developer\n\n"
                "Or, to upload a JD file, use /setjobfile instead."
            )
            return

        job_desc = " ".join(context.args)
        self.user_jobs[user_id] = job_desc

        await update.message.reply_text(
            f"✅ Job description text saved!\n\n"
            f"📝 Position: {job_desc}\n\n"
            f"Now upload your resume (PDF or text file) for analysis."
        )

    async def set_job_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setjobfile command"""
        user_id = update.effective_user.id
        self.expecting_jd_file[user_id] = True
        await update.message.reply_text("📁 Please upload your Job Description (PDF or TXT file) now.")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle file uploads"""
        user_id = update.effective_user.id
        document = update.message.document

        # Check file size and type
        if document.file_size > 5 * 1024 * 1024:  # 5MB limit
            await update.message.reply_text("❌ File too large! Max 5MB")
            return

        if not (document.mime_type.startswith('application/pdf') or 
                document.mime_type.startswith('text/')):
            await update.message.reply_text(
                "❌ Invalid file type! Please send PDF or text files only."
            )
            return

        # Download and store file
        try:
            file = await update.message.document.get_file()
            file_content = await file.download_as_bytearray()
            
            if self.expecting_jd_file.get(user_id):
                self.user_job_files[user_id] = {
                    'content': file_content,
                    'filename': document.file_name,
                    'mime_type': document.mime_type
                }
                self.expecting_jd_file[user_id] = False
                await update.message.reply_text(
                    f"✅ Job Description file uploaded: {document.file_name}\n\n"
                    f"Now upload your resume file!"
                )
            else:
                self.user_files[user_id] = {
                    'content': file_content,
                    'filename': document.file_name,
                    'mime_type': document.mime_type
                }
                await update.message.reply_text(
                    f"✅ Resume uploaded: {document.file_name}\n\n"
                    f"Send /analyze to get your analysis!"
                )
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            await update.message.reply_text("❌ Error uploading file. Please try again.")

    async def analyze_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze resume"""
        user_id = update.effective_user.id
        await update.message.reply_text("⏳ Analyzing your resume... This may take a moment...")

        try:
            # Check if job and resume are set
            if user_id not in self.user_jobs and user_id not in self.user_job_files:
                await update.message.reply_text("❌ Please set a job description first using /setjob or /setjobfile")
                return

            if user_id not in self.user_files:
                await update.message.reply_text("❌ Please upload your resume first!")
                return

            # Determine job description text
            job_desc = ""
            if user_id in self.user_job_files:
                jd_file_data = self.user_job_files[user_id]
                try:
                    if 'pdf' in jd_file_data['mime_type'].lower():
                        job_desc = pdf_handler.extract_text_from_pdf(jd_file_data['content'])
                    else:
                        job_desc = jd_file_data['content'].decode('utf-8', errors='ignore')
                except Exception as e:
                    logger.error(f"Error extracting JD text: {e}")
                    await update.message.reply_text("❌ Error reading Job Description file.")
                    return
            else:
                job_desc = self.user_jobs[user_id]

            file_data = self.user_files[user_id]

            # Extract text from file - handle both PDF and text
            try:
                if 'pdf' in file_data['mime_type'].lower():
                    # For PDF files - robust extraction with multiple fallbacks
                    try:
                        resume_text = pdf_handler.extract_text_from_pdf(file_data['content'])
                    except Exception as pdf_error:
                        logger.warning(f"PDF extraction failed: {pdf_error}")
                        # Check if PDF is corrupted or scanned
                        if len(file_data['content']) < 100:
                            raise ValueError("PDF file appears to be corrupted or empty")
                        # Try to extract with fallback
                        resume_text = ""
                    
                    # Validate PDF extraction
                    if not resume_text or len(resume_text.strip()) < 10:
                        await update.message.reply_text(
                            "❌ Could not extract text from PDF.\n\n"
                            "This might be because:\n"
                            "• PDF is an image/scanned document (OCR required)\n"
                            "• PDF is corrupted or encrypted\n\n"
                            "✅ **Solution: Convert to TXT**\n"
                            "1. Open your PDF with Acrobat/Word\n"
                            "2. Select all text (Ctrl+A)\n"
                            "3. Copy (Ctrl+C)\n"
                            "4. Paste into Notepad\n"
                            "5. Save as resume.txt\n"
                            "6. Upload the TXT file\n\n"
                            "Send /analyze after uploading the TXT file!"
                        )
                        return
                else:
                    # For text files
                    resume_text = file_data['content'].decode('utf-8', errors='ignore')
                
                # Final validation
                if not resume_text or len(resume_text.strip()) < 10:
                    await update.message.reply_text(
                        "❌ No text content found in file. File might be empty or unreadable.\n\n"
                        "Please check:\n"
                        "• File is not empty\n"
                        "• File is properly formatted\n"
                        "• Try uploading a different file"
                    )
                    return
                    
            except Exception as e:
                logger.error(f"Error extracting text: {e}")
                await update.message.reply_text(
                    "❌ Error reading resume file.\n\n"
                    "**Recommended Solution:**\n"
                    "1. Open your resume in any PDF reader\n"
                    "2. Select all text (Ctrl+A)\n"
                    "3. Copy (Ctrl+C)\n"
                    "4. Open Notepad\n"
                    "5. Paste the text (Ctrl+V)\n"
                    "6. Save as resume.txt\n"
                    "7. Upload the txt file here\n\n"
                    "Then send /analyze again!"
                )
                return

            # Analyze resume
            try:
                analysis = ai_analyzer.analyze_and_optimize(job_desc, resume_text)
            except Exception as e:
                logger.error(f"Error in analysis: {e}")
                await update.message.reply_text(
                    "❌ Error analyzing resume. Check:\n"
                    "• Gemini API key is correct\n"
                    "• Internet connection is stable\n"
                    "• Resume content is valid"
                )
                return

            # Format and send results
            results_message = self._format_analysis_results(analysis)
            
            # Store optimized resume for download
            optimized = analysis.get('optimized_resume', resume_text)
            self.user_resumes[user_id] = optimized
            
            # Split message if too long (Telegram limit is 4096 characters)
            if len(results_message) > 4000:
                for i in range(0, len(results_message), 4000):
                    await update.message.reply_text(results_message[i:i+4000], parse_mode='HTML')
            else:
                await update.message.reply_text(results_message, parse_mode='HTML')
            
            # Send download instruction as SEPARATE message with emphasis
            try:
                await update.message.reply_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📥 <b>DOWNLOAD YOUR RESUME</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Send /download to get your optimized resume as PDF!\n\n"
                    "✨ The AI has improved:\n"
                    "• Keywords matching\n"
                    "• ATS compatibility\n"
                    "• Formatting\n\n"
                    "<b>Ready? → Send /download</b>",
                    parse_mode='HTML'
                )
                logger.info(f"Download instruction message sent to user {user_id}")
            except Exception as msg_e:
                logger.error(f"Error sending download instruction: {msg_e}")
                
            # Try to automatically generate and send PDF
            try:
                logger.info(f"Generating PDF for user {user_id}...")
                pdf_content = pdf_handler.generate_resume_pdf(optimized)
                logger.info(f"PDF generated successfully, size: {len(pdf_content)} bytes")
                
                # Create BytesIO and send
                file_obj = io.BytesIO(pdf_content)
                
                await update.message.reply_document(
                    document=file_obj,
                    filename="optimized_resume.pdf",
                    caption="Done , Now you can download the updated resume"
                )
                logger.info(f"PDF sent successfully to user {user_id}")
            except Exception as pdf_e:
                logger.error(f"PDF auto-generation failed: {pdf_e}", exc_info=True)
                # If auto-PDF fails, just remind about manual download
                try:
                    await update.message.reply_text(
                        "⚠️ PDF auto-generation encountered an issue.\n\n"
                        "No problem! Just send /download and the bot will create your PDF."
                    )
                except Exception as err_msg_e:
                    logger.error(f"Error sending fallback message: {err_msg_e}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await update.message.reply_text("❌ An unexpected error occurred. Please try again.")

    async def download_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Download the optimized resume as PDF"""
        user_id = update.effective_user.id
        await update.message.reply_text("⏳ Generating PDF... Please wait...")

        try:
            if user_id not in self.user_resumes:
                await update.message.reply_text(
                    "❌ No optimized resume found!\n\n"
                    "Please:\n"
                    "1. Send /setjob <job description>\n"
                    "2. Upload your resume\n"
                    "3. Send /analyze\n\n"
                    "Then you can download!"
                )
                return

            resume_text = self.user_resumes[user_id]
            
            # Generate PDF
            try:
                pdf_content = pdf_handler.generate_resume_pdf(resume_text)
                
                # Send PDF file to user
                from telegram import Document
                file_obj = io.BytesIO(pdf_content)
                file_obj.name = "optimized_resume.pdf"
                
                await update.message.reply_document(
                    document=file_obj,
                    caption="Done , Now you can download the updated resume"
                )
                
                await update.message.reply_text("✅ Resume downloaded successfully!")
                
            except Exception as e:
                logger.error(f"Error generating PDF: {e}")
                await update.message.reply_text(
                    "❌ Error generating PDF.\n\n"
                    "You can copy the optimized resume text and convert it manually using:\n"
                    "• Google Docs\n"
                    "• Microsoft Word\n"
                    "• Online PDF converters"
                )
                
        except Exception as e:
            logger.error(f"Error in download: {e}")
            await update.message.reply_text("❌ Error downloading resume. Please try again.")

    async def ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Answer questions about resume in context of job"""
        user_id = update.effective_user.id
        
        # Extract question from command
        if not context.args:
            await update.message.reply_text(
                "📚 <b>Ask Me Anything About Your Resume!</b>\n\n"
                "Usage: <code>/ask Your question here</code>\n\n"
                "Example Questions:\n"
                "• /ask Should I add more technical skills?\n"
                "• /ask How well does my experience match?\n"
                "• /ask What keywords should I highlight?\n"
                "• /ask How can I improve my skills section?\n\n"
                "<b>Requirements:</b>\n"
                "✓ Job description set (/setjob)\n"
                "✓ Resume uploaded\n"
                "✓ Analysis completed (/analyze)",
                parse_mode='HTML'
            )
            return
        
        # Check prerequisites
        if user_id not in self.user_jobs:
            await update.message.reply_text("❌ Please set a job description first using /setjob")
            return
        
        if user_id not in self.user_files:
            await update.message.reply_text("❌ Please upload your resume first!")
            return
        
        if user_id not in self.user_resumes:
            await update.message.reply_text("❌ Please run /analyze first to get context!")
            return
        
        # Get question text
        question = " ".join(context.args)
        
        await update.message.reply_text("🤔 Analyzing your question... Please wait...")
        
        try:
            # Get data
            job_desc = self.user_jobs[user_id]
            file_data = self.user_files[user_id]
            
            # Extract resume text
            if 'pdf' in file_data['mime_type'].lower():
                try:
                    from app.utils.pdf_handler import extract_text_from_pdf
                    resume_text = extract_text_from_pdf(file_data['content'])
                except:
                    # Use optimized resume from analysis
                    resume_text = self.user_resumes[user_id]
            else:
                resume_text = file_data['content'].decode('utf-8')
            
            # Ask AI
            response = ai_analyzer.ask_about_resume(resume_text, job_desc, question)
            
            # Format answer
            msg = "<b>💡 AI Answer</b>\n\n"
            msg += f"<b>Question:</b> {question}\n\n"
            msg += f"<b>Answer:</b>\n{response.get('answer', 'Unable to answer')}\n\n"
            
            # Key points
            if response.get('key_points'):
                msg += "<b>Key Points:</b>\n"
                for point in response['key_points'][:3]:
                    msg += f"• {point}\n"
                msg += "\n"
            
            # Action items
            if response.get('action_items'):
                msg += "<b>What You Can Do:</b>\n"
                for item in response['action_items'][:3]:
                    msg += f"✓ {item}\n"
            
            await update.message.reply_text(msg, parse_mode='HTML')
            logger.info(f"Question answered for user {user_id}: {question[:50]}")
            
        except Exception as e:
            logger.error(f"Error answering question: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Error processing your question.\n\n"
                f"Please try:\n"
                f"• Rephrasing your question\n"
                f"• Checking your internet connection\n"
                f"• Running /analyze again"
            )

    def _format_analysis_results(self, analysis: dict) -> str:
        """Format analysis results for Telegram (HTML format)"""
        try:
            logger.info(f"Analysis data received: {list(analysis.keys())}")
            
            msg = "<b>📊 AI Resume Analysis Results</b>\n\n"

            # Scores - Handle both key variations
            msg += "<b>📈 Scores:</b>\n"
            overall = analysis.get('overall_score', 0)
            msg += f"• Overall Match: {overall}/10 {'🟢' if overall >= 7 else '🟡' if overall >= 4 else '🔴'}\n"
            msg += f"• Skills Match: {analysis.get('skill_score') or analysis.get('skills_score', 0)}/10\n"
            msg += f"• Keywords Match: {analysis.get('keyword_score') or analysis.get('keywords_score', 0)}/10\n"
            msg += f"• Experience: {analysis.get('experience_score', 0)}/10\n"
            msg += f"• ATS Score: {analysis.get('ats_compatibility_score') or analysis.get('ats_score', 0)}/10\n\n"

            # Matching Skills
            if analysis.get('matching_skills'):
                msg += "<b>✅ Matching Skills:</b>\n"
                skills = analysis['matching_skills']
                if isinstance(skills, list):
                    for skill in skills[:5]:
                        msg += f"• {skill}\n"
                msg += "\n"

            # Missing Keywords
            if analysis.get('missing_keywords'):
                msg += "<b>⚠️ Missing Keywords:</b>\n"
                keywords = analysis['missing_keywords']
                if isinstance(keywords, list):
                    for keyword in keywords[:5]:
                        msg += f"• {keyword}\n"
                msg += "\n"

            # Strengths
            if analysis.get('strengths'):
                msg += "<b>💪 Your Strengths:</b>\n"
                strengths = analysis['strengths']
                if isinstance(strengths, list):
                    for strength in strengths[:3]:
                        msg += f"• {strength}\n"
                msg += "\n"

            # Weaknesses
            if analysis.get('weaknesses'):
                msg += "<b>⚡ Areas to Improve:</b>\n"
                weaknesses = analysis['weaknesses']
                if isinstance(weaknesses, list):
                    for weakness in weaknesses[:3]:
                        msg += f"• {weakness}\n"
                msg += "\n"

            # Suggestions
            if analysis.get('improvement_suggestions'):
                msg += "<b>💡 Improvement Suggestions:</b>\n"
                suggestions = analysis['improvement_suggestions']
                if isinstance(suggestions, list):
                    for suggestion in suggestions[:3]:
                        msg += f"• {suggestion}\n"

            msg += "\n\n<b>📥 Download Optimized Resume:</b>\nSend /download to download your optimized resume as PDF!"

            return msg

        except Exception as e:
            logger.error(f"Error formatting results: {e}", exc_info=True)
            logger.error(f"Analysis data: {analysis}")
            # Return basic info about what we got
            return f"✅ Analysis Complete!\n\nOverall Match: {analysis.get('overall_score', 'N/A')}/10\n\nDetailed report sent separately."

    async def main(self):
        """Start the bot"""
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set in .env")
            return

        # Create application
        self.app = Application.builder().token(self.token).build()

        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("setjob", self.set_job))
        self.app.add_handler(CommandHandler("setjobfile", self.set_job_file))
        self.app.add_handler(CommandHandler("analyze", self.analyze_resume))
        self.app.add_handler(CommandHandler("download", self.download_resume))
        self.app.add_handler(CommandHandler("ask", self.ask_question))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))

        # Error handler
        self.app.add_error_handler(self._error_handler)

        logger.info("🤖 Telegram Bot Initialized")
        logger.info("✅ Bot started successfully!")
        logger.info("🔄 Bot is polling for updates...")
        
        # Run polling
        try:
            await self.app.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"❌ Bot error: {e}", exc_info=True)
            raise

    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")


async def start_telegram_bot():
    """Start the Telegram bot - Simple version"""
    token = settings.TELEGRAM_BOT_TOKEN
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env")
        return
    
    logger.info("🤖 Starting Telegram Bot...")
    logger.info(f"Token: {token[:20]}...")
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Initialize bot instance
    bot = TelegramResumeBot(token)
    
    # Add handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("setjob", bot.set_job))
    app.add_handler(CommandHandler("setjobfile", bot.set_job_file))
    app.add_handler(CommandHandler("analyze", bot.analyze_resume))
    app.add_handler(CommandHandler("download", bot.download_resume))
    app.add_handler(MessageHandler(filters.Document.ALL, bot.handle_document))
    app.add_error_handler(bot._error_handler)
    
    logger.info("✅ Telegram Bot initialized successfully!")
    logger.info("🔄 Bot is polling for updates...")
    
    # Run the bot
    await app.run_polling(allowed_updates=Update.ALL_TYPES)
