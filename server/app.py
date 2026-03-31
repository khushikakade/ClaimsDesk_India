import sys
import os

# Ensure backend can be imported safely from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the existing perfectly working FastAPI app
from backend.main import app

def main():
    """Standard entry point for OpenEnv multi-mode."""
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
