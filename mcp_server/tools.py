
import sys
import os
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd

from mcp_server.schemas import (
    CompareNetIncomeInput,
    CompareNetIncomeOutput,
    SummarizeBalanceSheetInput,
    SummarizeBalanceSheetOutput,
)

#DATA_PATH = "../data"
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def list_tools():
    return {
        "tools": [
            {
                "name": "compare_net_income",
                "description": "Compare net income between companies over time",
                "parameters": CompareNetIncomeInput.schema()["properties"]
            },
            {
                "name": "summarize_balance_sheet",
                "description": "Summarize balance sheet for a specific company and year",
                "parameters": SummarizeBalanceSheetInput.schema()["properties"]
            }
        ]
    }

def call_tool(tool_name, parameters):
    if tool_name == "compare_net_income":
        validated = CompareNetIncomeInput(**parameters)
        return compare_net_income(validated).dict()

    elif tool_name == "summarize_balance_sheet":
        validated = SummarizeBalanceSheetInput(**parameters)
        return summarize_balance_sheet(validated).dict()

    else:
        return {"error": "Unknown tool"}

def compare_net_income(input_data: CompareNetIncomeInput) -> CompareNetIncomeOutput:
    result = {}

    for company in input_data.company_names:
        file_path = os.path.join(DATA_PATH, f"{company.lower()}_income.csv")
        if not os.path.exists(file_path):
            result[company] = "Data not available"
            continue

        df = pd.read_csv(file_path)
        df = df.set_index("Year")
        try:
            net_income = df.loc["Net Income"]
            result[company] = {
                year: net_income[year] for year in net_income.index if "20" in year
            }
        except KeyError:
            result[company] = "Net Income row missing"

    return CompareNetIncomeOutput(comparison=result)

def summarize_balance_sheet(input_data: SummarizeBalanceSheetInput) -> SummarizeBalanceSheetOutput:
    file_path = os.path.join(DATA_PATH, f"{input_data.company_name.lower()}_balancesheet.csv")
    if not os.path.exists(file_path):
        return SummarizeBalanceSheetOutput(
            company=input_data.company_name,
            year=input_data.year,
            summary={"error": f"No data found for {input_data.company_name}"}
        )

    df = pd.read_csv(file_path)
    if input_data.year not in df.columns:
        return SummarizeBalanceSheetOutput(
            company=input_data.company_name,
            year=input_data.year,
            summary={"error": f"Year {input_data.year} not found in balance sheet"}
        )

    summary_items = [
        "Total Assets",
        "Total Liabilities",
        "Total Equity",
        "Cash And Equivalents",
        "Net Loans"
    ]

    summary = {}
    for item in summary_items:
        try:
            value = df.loc[df["Year"] == item, input_data.year].values[0]
            summary[item] = value
        except IndexError:
            summary[item] = "Not found"

    return SummarizeBalanceSheetOutput(
        company=input_data.company_name,
        year=input_data.year,
        summary=summary
    )
