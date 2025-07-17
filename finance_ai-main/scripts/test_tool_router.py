import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from llm.tool_router import extract_tool_call

gemini_response = """
Based on the data, HDFC's net income has shown consistent growth from 2021 to 2025. 
You can use the compare_net_income tool to verify this trend.
"""

result = extract_tool_call(gemini_response)
print("=== Parsed Tool Call ===")
print(result)
