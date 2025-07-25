import re
import json
from data1.db import SessionLocal
from sqlalchemy import text
import difflib
from fuzzywuzzy import fuzz


def get_all_company_names():
    session = SessionLocal()
    query = text("SELECT company_name FROM companies")
    rows = session.execute(query).fetchall()
    session.close()
    return [row[0] for row in rows]

def find_matching_companies(user_input: str, company_list: list):
    return [company for company in company_list if company.lower() in user_input.lower()]


def get_typo_tolerant_matches(field_list, user_input, threshold=80, match_ratio=0.8):
    input_words = user_input.lower().split()
    matches = []

    for field in field_list:
        field_words = field.lower().split()
        match_count = 0

        for fw in field_words:
            for iw in input_words:
                if fuzz.ratio(fw, iw) >= threshold:
                    match_count += 1
                    break  # stop checking after first good match

        if (match_count / len(field_words)) >= match_ratio:
            matches.append(field)

    return matches


def extract_tool_call(gemini_response: str) -> dict:
    """
    Extracts the tool name and parameters from a Gemini model response.
    Returns:
        dict: with keys "tool_name" and "parameters"
    """
    gemini_response_lower = gemini_response.lower()
    

    matching_sheets_company_info_ = []
    matching_sheets_yearly_pnl = []
    matching_sheets_cashflow = []
    matching_balance_sheet = []
    matching_financial_ratio = []
    matching_sheets_quarterly_pnl = []
    matching_yearly_shareholding = []
    matching_quarterly_shareholding = []

    ALL_COMPANIES = get_all_company_names()
    companies = find_matching_companies(gemini_response_lower, ALL_COMPANIES)


    if not gemini_response_lower:
        return {"tool_name": None, "parameters": {}}

    # ✅ Year extraction
    year_match = re.search(r"\b(20\d{2})\b", gemini_response)
    year = year_match.group(1) if year_match else "2023"


    # 
    # 🛠 1. Net Income Tool
    if ("quarter" not in gemini_response_lower and 
        "quarterly" not in gemini_response_lower and
        "roe ratio" not in gemini_response_lower and
        "roce ratio" not in gemini_response_lower
        # "financial statement" not in gemini_response_lower and
        # "three financial statement" not in gemini_response_lower
    ):
        # 🛠 1. For company info
        _company_info_ = [
            "basic company details", "company profile", "company profile","basic information","basic info","company details",
            "company overview","company summary", "firm profile","business profile",
            "corporate profile" , "company background", "organization overview",
            "company name", "firm name", "entity name",
            "sector", "industry", "business segment",
            "bse", "bse code", "bse ticker", "bse symbol",
            "nse", "nse code", "nse ticker", "nse symbol",
            "market cap", "market capitalization", "company size", "market value",
            "current price", "stock price", "share price", "cmp (current market price)",
            "high / low", "52-week high", "52-week low", "stock range", "high low",
            "stock p/e", "p/e ratio", "price to earnings",
            "book value", "book value per share", "net asset value",
            "dividend yield", "yield", "dividend %", "payout ratio",
            "roce", "return on capital employed", "efficiency ratio",
            "roe", "return on equity", "shareholder return",
            "face value", "fv", "nominal value", "par value",
            "price to sales", "p/s ratio", "price to revenue",
            "sales growth", "revenue growth", "sales increase",
            "sales growth 3years", "3y sales growth", "cagr (sales 3y)",
            "sales growth 5years", "5y sales growth", "cagr (sales 5y)",
            "sales growth 7years", "7y sales growth", "cagr (sales 7y)",
            "sales growth 10years", "10y sales growth", "long-term sales growth",
            "profit growth", "net profit growth", "earnings growth",
            "profit growth 3years", "3y profit growth", "cagr (profit 3y)",
            "profit growth 5years", "5y profit growth", "cagr (profit 5y)",
            "profit growth 7years", "7y profit growth", "cagr (profit 7y)",
            "profit growth 10years", "10y profit growth", "long-term profit growth",
            "eps", "earnings per share", "eps (current)",
            "eps last year", "eps (previous year)", "last year eps",
            "debt", "current debt", "total debt", "outstanding debt",
            "debt 3years back", "debt (3y ago)", "historical debt (3y)",
            "debt 5years back", "debt (5y ago)", "historical debt (5y)",
            "debt 7years back", "debt (7y ago)", "historical debt (7y)",
            "debt 10years back", "debt (10y ago)", "historical debt (10y)"
        ]
           
        matching_sheets_company_info_ = get_typo_tolerant_matches(_company_info_, gemini_response_lower) 

        
        # 🛠 1. For yearlypnl
        yearly_pnl_ = [
            "profit and loss statement","income statement",
            "net income", "net profit", "profit after tax", "bottom line",
            "yearly net income", "annual net income", "annual profit", "yearly profit after tax",
            "yearly net profit", "annual net profit", "annual earnings", "yearly profit",
            "sales", "turnover", "gross sales", "total sales",
            "expenses", "total expenses", "operating expenses", "costs",
            "operating profit", "ebit", "earnings before interest and taxes", "operating income",
            "other income", "non-operating income", "miscellaneous income",
            "interest", "interest expense", "finance costs", "interest paid",
            "depreciation", "depreciation expense", "amortization",
            "profit before tax", "pbt", "earnings before tax", "pre-tax profit",
            "tax percentage", "effective tax rate", "tax rate",
            "earnings per share", "basic eps",
            "revenue", "total revenue", "gross revenue", "income",
            "financing profit", "net interest income", "financial income",
            "financing margin percentage", "net interest margin", "financial margin",
            "eps", "basic earnings per share", "omp", 
            "operating margin percentage","opm", "operating profit margin"
        ]

        
        matching_sheets_yearly_pnl = get_typo_tolerant_matches(yearly_pnl_, gemini_response_lower)
        # matching_sheets_yearly_pnl  = [sheet for sheet in yearly_pnl_ if sheet in gemini_response_lower]
        
        # 🛠 2. For cashflow
        yearly_cashflow = [
            "cash from operating activities" ," net cash from operations", "operating cash flow",
            "cash flow from operations","operating activities","investing activities","financing activities","cash flow"
            "cash from investing activities","net cash used in investing"," investing cash flow",
            "cash from financing activities",  "net cash from financing", "financing cash flow",
            "net cash flow","net increase/decrease in cash" ," net change in cash",
            "cash flow","cash movements","statement of cash flows","overall cash flow"
        ]
        matching_sheets_cashflow = get_typo_tolerant_matches(yearly_cashflow, gemini_response_lower)
        # matching_sheets_cashflow = [sheet for sheet in yearly_cashflow if sheet in gemini_response_lower]

        financial_ratio_ = [
            "financial ratio", "ratio","financial ratios", "ratios",
            "ratio date", "date", "reporting date", "data as of", "period end", "fiscal date",
            "debtor days", "receivables days", "days sales outstanding", "dso", "debtor turnover days", "avg collection period",
            "inventory days", "days inventory outstanding", "inventory holding period", "inventory turnover days", "doi",
            "days payable", "payable days", "days payables outstanding", "dpo", "average payment period", "creditor days",
            "cash conversion cycle", "ccc", "working capital cycle", "cash cycle", "net operating cycle",
            "working capital days", "net working capital days", "wc days", "working capital cycle",
            "roce percent",  "roce ratio", "operating return", "capital efficiency",
            "roe percent", "roe ratio", "shareholders  return", "equity return", "net worth return"
        ]

        matching_financial_ratio = get_typo_tolerant_matches(financial_ratio_, gemini_response_lower)

        # 🛠 3. For yearly balance sheet
        yearly_balance_sheet = [
            "balance sheet", "statement of financial position",
            "total assets", "gross assets", "sum of assets",
            "net loans", "net advances", "loans and advances (net)", "net loan portfolio",
            "total liabilities", "aggregate liabilities", "total obligations",
            "equity capital", "shareholders’ equity", "owner’s equity", "paid-up capital", "common equity",
            "reserves", "retained earnings", "surplus reserves", "capital reserves",
            "other liabilities", "miscellaneous liabilities", "sundry liabilities",
            "fixed assets", "property, plant & equipment (PPE)", "tangible assets",
            "cwip", "capital work-in-progress", "assets under construction",
            "investments", "long-term investments", "financial investments",
            "other assets", "miscellaneous assets", "sundry assets",
            "preference capital", "preferred stock", "preference shares"
        ]

        # matching_balance_sheet = [sheet for sheet in yearly_balance_sheet if sheet in gemini_response_lower]
        matching_balance_sheet = get_typo_tolerant_matches(yearly_balance_sheet, gemini_response_lower)

        yearly_shareholding = [
            "shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern"
            "promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders",
            "fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders",
            "diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies",
            "public", "public holding", "retail investors", "non-institutional investors", "general public",
            "no. of shareholders", "shareholder count", "number of shareholders", "investor base size",
            "others", "others category", "miscellaneous holding", "unidentified shareholders",
            "government", "government holding", "state holding", "public sector holding", "govt stake"
        ]

        matching_yearly_shareholding = get_typo_tolerant_matches(yearly_shareholding, gemini_response_lower)

        financial_statement_list = ["financial statement"]
        matching_financial_statement = get_typo_tolerant_matches(financial_statement_list, gemini_response_lower)

    else:
        quarterly_pnl_ = [
            "profit and loss statement", "income statement","quarterly results", "quarterly pnl","quarter wise results"
            "sales", "turnover", "gross sales", "total sales", "revenue",
            "expenses", "total expenses", "operating expenses", "costs", "outflows",
            "operating_profit", "ebit", "earnings before interest and taxes", "operating income",
            "opm_percentage", "operating margin %", "operating profit margin", "opm %",
            "other_income", "non-operating income", "miscellaneous income", "additional income",
            "interest", "interest expense", "finance costs", "interest paid",
            "depreciation", "depreciation expense", "amortization",
            "profit_before_tax", "pbt", "earnings before tax", "pre-tax profit", "ebt",
            "tax_percentage", "effective tax rate", "tax rate",
            "net_profit", "net income", "profit after tax", "bottom line", "earnings",
            "eps_in_rs", "earnings per share", "basic eps",
            "revenue", "total revenue", "gross revenue", "income",
            "financing_profit", "net interest income", "financial income",
            "financing_margin", "net interest margin", "financial margin",
            "gross_npa", "gross non-performing assets", "gross npa ratio",
            "net_npa", "net non-performing assets", "net npa ratio", "non-performing assets"
        ]

        matching_sheets_quarterly_pnl = get_typo_tolerant_matches(quarterly_pnl_, gemini_response_lower)

        quarterly_shareholding = [
            "shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern"
            "promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders",
            "fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders",
            "diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies",
            "public", "public holding", "retail investors", "non-institutional investors", "general public",
            "no. of shareholders", "shareholder count", "number of shareholders", "investor base size",
            "others", "others category", "miscellaneous holding", "unidentified shareholders",
            "government", "government holding", "state holding", "public sector holding", "govt stake"
        ]

        matching_quarterly_shareholding = get_typo_tolerant_matches(quarterly_shareholding, gemini_response_lower)

        ratios_to_check = ['roe ratio', 'roce ratio']
        matching_financial_ratio = [r for r in ratios_to_check if r in gemini_response_lower]
    

    if matching_sheets_company_info_ and companies:
        return {
            "tool_name": "company_info_",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_sheets_company_info_
            }
    }

    elif matching_sheets_yearly_pnl and companies:
        return {
            "tool_name": "compare_net_income",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_sheets_yearly_pnl
            }
    }

    elif matching_sheets_cashflow and companies:

        return {
            "tool_name": "cash_flow",
            "parameters": {
                "company_names": companies,
                "year": year,
                "fields": matching_sheets_cashflow
            }
        }

    elif matching_balance_sheet and companies:

            if companies:
                return {
                    "tool_name": "summarize_balance_sheet",
                    "parameters": {
                        "company_names": companies,
                        "year": year,
                        "fields" : matching_balance_sheet
                    }
                }
    elif matching_yearly_shareholding and companies:

            if companies:
                return {
                    "tool_name": "yearly_shareholding",
                    "parameters": {
                        "company_names": companies,
                        "year": year,
                        "fields" : matching_yearly_shareholding
                    }
                }
    elif matching_financial_ratio and companies:

                return {
                    "tool_name": "financial_ratio",
                    "parameters": {
                        "company_names": companies,
                        "year": year,
                        "fields" : matching_financial_ratio
                    }
                }

    elif matching_sheets_quarterly_pnl and companies:
        quarter_month = {
            "first": "first",
            "1st" : "first",
            "second": "second",
            "2nd": "second",
            "third": "third",
            "3rd" : "third",
            "fourth": "fourth",
            "4th": "fourth",
            "last" : "fourth"
        }

        quarter_get = []
        for k, v in quarter_month.items():
            if k in gemini_response_lower:
                quarter_get.append(v)

        return {
            "tool_name": "compare_quarterly_income",
            "parameters": {
                "company_names": companies,
                "year": year,
                "quarter_month": quarter_get,
                "fields": matching_sheets_quarterly_pnl
            }
        }
    

    elif matching_quarterly_shareholding and companies:
        quarter_month = {
            "first": "first",
            "1st" : "first",
            "second": "second",
            "2nd": "second",
            "third": "third",
            "3rd" : "third",
            "fourth": "fourth",
            "4th": "fourth",
            "last" : "fourth"
        }

        quarter_get = []
        for k, v in quarter_month.items():
            if k in gemini_response_lower:
                quarter_get.append(v)


        return {
            "tool_name": "quarterly_shareholding",
            "parameters": {
                "company_names": companies,
                "year": year,
                "quarter_month": quarter_get,
                "fields": matching_quarterly_shareholding
            }
        }

    elif matching_financial_statement and companies:

            return {
                "tool_name": "three_statements_",
                "parameters": {
                    "company_names": companies,
                    "year": year,
                    "fields" : matching_financial_statement
                }
            }
    # 🛑 If nothing matched
    return {
        "tool_name": None,
        "parameters": {}
    }