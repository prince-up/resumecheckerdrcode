# Telegram Bot Integration Guide

## Overview

The AI Resume Analyzer now includes a **Telegram Bot** that allows users to analyze their resumes directly through Telegram without needing the web interface.

## Setup

### 1. Bot Token
Your bot token is already configured in `.env`:
```
TELEGRAM_BOT_TOKEN=8771668632:AAHG-xodtBbHWrVTOGlWUWWltO-sLNd7sVI
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt  # python-telegram-bot 20.7 is included
```

### 3. Start the Bot

**Option A: Telegram Bot Only**
```bash
python telegram_bot_runner.py
```

**Option B: Web API Only (default)**
```bash
python run.py
```

**Option C: Both Web API + Telegram Bot**
```bash
python run_combined.py
```

## Bot Commands

### `/start`
- Shows welcome message
- Explains how to use the bot

### `/help`
- Shows detailed instructions
- How to analyze your resume

### `/setjob <job description>`
- Set the job description to match against
- **Example:** `/setjob Senior Python Developer - FastAPI, MongoDB, AWS`

### `/analyze`
- Analyze your uploaded resume
- Requires job description and resume file first

## How to Use

### Step 1: Start the Bot
Send `/start` to begin

### Step 2: Set Job Description
```
/setjob Your job title and description here
```
**Example:**
```
/setjob Junior Data Scientist - Python, SQL, Pandas, Machine Learning
```

### Step 3: Upload Resume
- Send your resume as a file (PDF or TXT)
- Max file size: 5MB
- Supported formats:
  - PDF (.pdf)
  - Text (.txt)

### Step 4: Get Analysis
Send `/analyze` to receive your detailed resume analysis

## Analysis Results

The bot will return:

1. **📈 Scores (0-10 scale)**
   - Overall Match Score
   - Skills Match
   - Keywords Match
   - Experience Alignment
   - ATS Compatibility

2. **✅ Matching Skills**
   - Skills from your resume that match the job

3. **⚠️ Missing Keywords**
   - Important keywords to add

4. **💪 Your Strengths**
   - What makes you a good fit

5. **⚡ Areas to Improve**
   - Gaps in your resume

6. **💡 Improvement Suggestions**
   - Actionable tips to optimize

## Example Conversation

```
User: /start

Bot: 🤖 Welcome to AI Resume Analyzer Bot!
[Shows detailed instructions]

User: /setjob Senior Full Stack Engineer - React, Node.js, PostgreSQL, Docker, AWS

Bot: ✅ Job description saved!
📝 Position: Senior Full Stack Engineer - React, Node.js, PostgreSQL, Docker, AWS
Now upload your resume (PDF or text file) for analysis.

User: [Uploads CV.pdf]

Bot: ✅ Resume uploaded: CV.pdf
Send /analyze to get your analysis!

User: /analyze

Bot: ⏳ Analyzing your resume... This may take a moment...

Bot: 📊 AI Resume Analysis Results
📈 Scores:
• Overall Match: 8/10 🟢
• Skills Match: 8/10
• Keywords Match: 7/10
• Experience: 9/10
• ATS Score: 8/10

✅ Matching Skills:
• React
• Node.js
• PostgreSQL
• Docker
[...]
```

## Features

✅ **Resume Analysis** - Detailed matching against job descriptions  
✅ **Score Generation** - Multiple dimensions of fit  
✅ **Skill Matching** - Identifies matching and missing skills  
✅ **ATS Compatibility** - Check resume parsing  
✅ **Improvement Tips** - Actionable suggestions  
✅ **File Handling** - Supports PDF and text resumes  

## Troubleshooting

### Bot not responding?
1. Check bot token in `.env` is correct
2. Ensure `python-telegram-bot` is installed: `pip install python-telegram-bot==20.7`
3. Check internet connection
4. Verify bot is running: `python telegram_bot_runner.py`

### "TELEGRAM_BOT_TOKEN not set" error?
- Ensure `.env` file contains `TELEGRAM_BOT_TOKEN=your_token_here`
- Restart the bot after updating `.env`

### File upload issues?
- Maximum file size: 5MB
- Only PDF and text files supported
- Try uploading a different file format

### Analysis errors?
- Ensure Gemini API key is set in `.env`
- Check internet connection
- Try with a simpler resume file

## Deployment

### For Production

1. **Set environment variables** on your server:
   ```bash
   export GEMINI_API_KEY=your_key_here
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   export CORS_ORIGINS=your_domains_here
   ```

2. **Run with systemd** (Linux/VPS):
   ```bash
   sudo systemctl start resume-analyzer-bot
   ```

3. **Run with Docker**:
   ```dockerfile
   FROM python:3.13
   WORKDIR /app
   COPY . .
   RUN pip install -r backend/requirements.txt
   CMD ["python", "backend/telegram_bot_runner.py"]
   ```

4. **Run with PM2** (Node.js process manager):
   ```bash
   npm install -g pm2
   pm2 start "python backend/telegram_bot_runner.py" --name "resume-bot"
   pm2 save
   ```

## File Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── telegram_bot.py      # Telegram bot implementation
│   │   ├── ai_service.py        # AI analysis logic
│   │   └── ...
│   └── ...
├── telegram_bot_runner.py       # Run bot only
├── run.py                       # Run web API only
├── run_combined.py              # Run both
└── requirements.txt             # Dependencies
```

## Support

For issues or questions:
- Check the main README.md
- Review error logs
- Test with simple resume files first
- Ensure all dependencies are installed

---

**Happy analyzing! 🚀**
