import re
import json

def extract_tool_call(gemini_response: str) -> dict:
    """
    Parses the Gemini response and returns a tool name and parameters.
    This is a basic rule-based parser and may be improved later with better NLP or structured prompting.

    Returns:
        dict with keys: "tool_name" and "parameters"
    """
    gemini_response = gemini_response.lower()

    if "compare net income" in gemini_response or "net income" in gemini_response:
        # Attempt to find company names
        companies = []
        if "hdfc" in gemini_response:
            companies.append("HDFC")
        if "icici" in gemini_response:
            companies.append("ICICI")

        if companies:
            return {
                "tool_name": "compare_net_income",
                "parameters": {
                    "company_names": companies
                }
            }

    elif "balance sheet" in gemini_response or "total assets" in gemini_response:
        company = "HDFC" if "hdfc" in gemini_response else "ICICI"
        year_match = re.search(r"\b(20\d{2})\b", gemini_response)
        year = year_match.group(1) if year_match else "2023"

        return {
            "tool_name": "summarize_balance_sheet",
            "parameters": {
                "company_name": company,
                "year": year
            }
        }

    return {
        "tool_name": None,
        "parameters": {}
    }
