#!/usr/bin/env python
"""
Main entry point for the AI Resume Analyzer backend
Run this file to start the server
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting AI Resume Analyzer Backend...")
    print("Server will run on http://0.0.0.0:8000")
    print("API Docs available at http://localhost:8000/docs")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on file changes during development
        log_level="info"
    )
