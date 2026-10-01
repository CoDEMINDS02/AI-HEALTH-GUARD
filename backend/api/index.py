import os
import sys

# Make the backend root importable so "app.main" is found on Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

app = fastapi_app