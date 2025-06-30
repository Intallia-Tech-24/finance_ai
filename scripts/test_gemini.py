import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.gemini_client import run_gemini_prompt


if __name__ == "__main__":
    user_query = "What is the net income trend of HDFC?"
    reply = run_gemini_prompt(user_query)
    print("Gemini Response:\n", reply)
