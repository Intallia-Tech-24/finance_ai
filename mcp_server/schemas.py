from typing import List, Dict , Optional ,Union, Any
from pydantic import BaseModel

# For yearly purpose..
# Schema for compare_net_income tool
class CompareNetIncomeInput(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class CashFlowInput(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class CashFlowOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str


class CompareNetIncomeOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str


class SummarizeBalanceSheetInput(BaseModel):
    company_names: List[str]
    year: str
    fields: Optional[List[str]] = None 

class SummarizeBalanceSheetOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str


class QuarterlyIncomeInput(BaseModel):
    company_names: List[str]
    year: str
    quarter_month: List[str]
    fields: Optional[List[str]] = None 


class QuarterlyIncomeOutput(BaseModel):
    comparison: Dict[str, Dict[str, Dict[str, Any]]]
    year: str