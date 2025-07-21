import streamlit as st
import google.generativeai as genai

# Load API key from Streamlit secrets
api_key = st.secrets["API_KEY"]

# Validate API key
if not api_key:
    raise ValueError("API_KEY not found in Streamlit secrets")

# Configure Gemini
genai.configure(api_key=api_key)

# Create Gemini model instance
model = genai.GenerativeModel("models/gemini-1.5-flash")

def run_gemini_prompt(prompt: str) -> str:
    """Send prompt to Gemini and return response text."""
    response = model.generate_content(prompt)
    return response.text.strip()