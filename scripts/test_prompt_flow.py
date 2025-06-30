import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from llm.prompt_builder import build_prompt
from llm.gemini_client import run_gemini_prompt
from llm.tool_router import extract_tool_call
from llm.context_manager import build_context

from mcp_server.tools import call_tool

# Step 1: User query
user_query = "Compare net income trend of HDFC and ICICI"

# Step 2: Build prompt
initial_prompt = build_prompt(user_query)

# Step 3: Get Gemini suggestion (tool + args)
tool_response = run_gemini_prompt(initial_prompt)
print("=== Gemini Tool Suggestion ===")
print(tool_response)

# Step 4: Extract tool name and parameters
tool_call = extract_tool_call(tool_response)
if tool_call is None:
    print("No tool call detected.")
    exit()

print("\n=== Tool Call ===")
print(tool_call)

# Step 5: Call the tool
tool_result = call_tool(tool_call["tool_name"], tool_call["parameters"])
print("\n=== Tool Output ===")
print(tool_result)

# Step 6: Format context from tool result
context = build_context(tool_call["tool_name"], tool_result)

# Step 7: Build final prompt including tool result
final_prompt = f"{initial_prompt}\n\nTool Output:\n{context}"

# Step 8: Get final answer from Gemini
final_response = run_gemini_prompt(final_prompt)

print("\n=== Final Gemini Answer ===")
print(final_response)
