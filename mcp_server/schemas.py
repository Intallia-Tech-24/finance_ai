from typing import List, Dict
from pydantic import BaseModel

# Schema for compare_net_income tool
class CompareNetIncomeInput(BaseModel):
    company_names: List[str]

class CompareNetIncomeOutput(BaseModel):
    comparison: Dict[str, Dict[str, str]]  # Adjusted to match actual output structure

# Schema for summarize_balance_sheet tool
class SummarizeBalanceSheetInput(BaseModel):
    company_name: str
    year: str

class SummarizeBalanceSheetOutput(BaseModel):
    company: str
    year: str
    summary: Dict[str, str]  # Corrected from str to dict
