#!/usr/bin/env python3
"""
Combined Runner for AI Resume Analyzer
Runs both the FastAPI Web API and Telegram Bot concurrently
"""

import asyncio
import uvicorn
import threading
import logging
from app.main import app
from app.services.telegram_bot import start_telegram_bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_api():
    """Run the FastAPI server in a separate thread"""
    logger.info("🚀 Starting FastAPI Web API on http://0.0.0.0:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


async def run_bot():
    """Run the Telegram bot"""
    logger.info("🤖 Starting Telegram Bot...")
    await start_telegram_bot()


async def main():
    """Run both API and bot concurrently"""
    # Start API in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Give API time to start
    await asyncio.sleep(2)

    # Run bot in main asyncio context
    try:
        await run_bot()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped")
        exit(0)
