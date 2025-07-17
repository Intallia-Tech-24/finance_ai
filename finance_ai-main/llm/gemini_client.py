import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("API_KEY") 

# 
if not api_key:
    raise ValueError("API_KEY not found in .env file")

genai.configure(api_key=api_key)

# Create model
model = genai.GenerativeModel("models/gemini-1.5-flash")


def run_gemini_prompt(prompt: str) -> str:
    """Send prompt to Gemini and return response text."""
    response = model.generate_content(prompt)
    # 
    return response.text.strip()
