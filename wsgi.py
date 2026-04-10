import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import and run the Flask app
from app import app

if __name__ == "__main__":
    app.run()
