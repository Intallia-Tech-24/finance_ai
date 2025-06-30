import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.context_manager import format_tool_result

# Simulated tool output
sample_output = {
    "comparison": {
        "HDFC": {
            "2021": "318,332.10",
            "2022": "380,527.50",
            "2023": "459,971.10"
        },
        "ICICI": {
            "2021": "183,843.19",
            "2022": "251,100.96",
            "2023": "340,366.41"
        }
    }
}

print("=== Formatted Tool Result ===")
print(format_tool_result("compare_net_income", sample_output))
