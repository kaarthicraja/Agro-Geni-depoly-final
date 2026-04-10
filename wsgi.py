import sys
import os
from pathlib import Path

# Set the project directory
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
sys.path.insert(0, str(project_dir / "backend"))

# Set environment variables if not already set
if not os.getenv('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

# Import and run the Flask app from backend
from app import app

if __name__ == "__main__":
    app.run()
