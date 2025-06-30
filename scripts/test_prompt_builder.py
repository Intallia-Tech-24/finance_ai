import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.prompt_builder import build_prompt

# Dummy inputs
query = "What is the trend of net income for HDFC?"
tools = [
    {"name": "compare_net_income", "description": "Compare net income between companies over time"},
    {"name": "summarize_balance_sheet", "description": "Summarize balance sheet for a specific company and year"}
]
resources = [
    {"name": "hdfc_income.csv", "description": "HDFC income statement data"},
    {"name": "icici_income.csv", "description": "ICICI income statement data"}
]

# Build and print prompt
prompt = build_prompt(query, tools=tools, resources=resources)
print("=== Final Prompt ===\n")
print(prompt)
