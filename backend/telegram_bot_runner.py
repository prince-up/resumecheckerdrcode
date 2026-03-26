#!/usr/bin/env python3
"""
Telegram Bot Runner for AI Resume Analyzer
Run this to start only the Telegram bot (without the web API)
"""

import sys
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.services.telegram_bot import TelegramResumeBot
from app.core.config import settings

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("🤖 Starting AI Resume Analyzer Telegram Bot...")
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not configured in .env file")
        sys.exit(1)
    
    try:
        # Create bot instance
        bot = TelegramResumeBot(settings.TELEGRAM_BOT_TOKEN)
        
        # Create application
        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        from telegram import Update
        from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
        
        app.add_handler(CommandHandler("start", bot.start))
        app.add_handler(CommandHandler("help", bot.help_command))
        app.add_handler(CommandHandler("setjob", bot.set_job))
        app.add_handler(CommandHandler("analyze", bot.analyze_resume))
        app.add_handler(MessageHandler(filters.Document.ALL, bot.handle_document))
        app.add_error_handler(bot._error_handler)
        
        logger.info("✅ Bot initialized successfully!")
        logger.info("🔄 Bot is polling for updates...")
        
        # Run the bot
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("\n✅ Bot stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
