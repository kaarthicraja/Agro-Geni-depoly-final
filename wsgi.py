#!/usr/bin/env python
"""
WSGI entry point for Gunicorn.
Uses relative imports in the backend package to ensure modules can find each other.
"""
import sys
from pathlib import Path

# Add the project root to sys.path as a safety measure
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import the Flask app from the backend package
from backend.app import app

if __name__ == "__main__":
    app.run()
