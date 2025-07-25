import pandas as pd
from data1.db import SessionLocal
from collections import defaultdict
from decimal import Decimal
from sqlalchemy import text
from mcp_server.schemas import (
    CompareNetIncomeInput,
    CashFlowInput,
    CompareNetIncomeOutput,
    CashFlowOutput,
    SummarizeBalanceSheetInput,
    SummarizeBalanceSheetOutput,
    QuarterlyIncomeInput,
    QuarterlyIncomeOutput,
    Company_Info_Input,
    Company_Info_Output,
    Financial_Ratio_Input,
    Financial_Ratio_Output,
    YearlyShareholdingInput,
    YearlyShareholdingOutput,
    QuarterlyShareholdingInput,
    QuarterlyShareholdingOutput,
)
from datetime import datetime
from typing import Union, List, Dict, Any



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
    
    if tool_name == "company_info_":
        validated = Company_Info_Input(**parameters)
        return company_info(validated).dict()

    elif tool_name == "compare_net_income":
        validated = CompareNetIncomeInput(**parameters)
        return compare_net_income(validated).dict()

    elif tool_name == "cash_flow":
        validated = CashFlowInput(**parameters)
        return cash_flow(validated).dict()

    elif tool_name == "summarize_balance_sheet":
        validated = SummarizeBalanceSheetInput(**parameters)
        return summarize_balance_sheet(validated).dict()

    elif tool_name == "yearly_shareholding":
        validated = YearlyShareholdingInput(**parameters)
        return yearly_shareholding(validated).dict()

    elif tool_name == "financial_ratio":
        validated = Financial_Ratio_Input(**parameters)
        return financial_ratio(validated).dict()

    elif tool_name == "compare_quarterly_income":
        validated = QuarterlyIncomeInput(**parameters)
        return compare_quarterly_income(validated).dict()

    elif tool_name == "quarterly_shareholding":
        validated = QuarterlyShareholdingInput(**parameters)
        return quarterly_shareholding(validated).dict()

    else:
        return "Unknown tool"


def three_statements_tool(tool_name, parameters):

    total_statements_data = []
    if tool_name == "three_statements_":
        validated = CompareNetIncomeInput(**parameters)
        f1_data = compare_net_income(validated).dict()
        total_statements_data.append(f1_data)

    if tool_name == "three_statements_":
        validated = CashFlowInput(**parameters)
        f2_data = cash_flow(validated).dict()
        total_statements_data.append(f2_data)

    if tool_name == "three_statements_":
        validated = SummarizeBalanceSheetInput(**parameters)
        f3_data = summarize_balance_sheet(validated).dict()
        total_statements_data.append(f3_data)
        return total_statements_data
    


#For financial ratio
def financial_ratio(input_data: Financial_Ratio_Input) -> Financial_Ratio_Output:
    result = {}
    session = SessionLocal()


    for company in input_data.company_names:
        year = input_data.year
        query = text("""
                SELECT
                f.ratio_date AS year,
                f.debtor_days,
                f.inventory_days,
                f.days_payable,
                f.cash_conversion_cycle,
                f.working_capital_days,
                f.roce_percentage,
                f.roe_percentage
                FROM financial_ratios f
                INNER JOIN companies c ON f.company_id = c.id
                WHERE c.company_name = :company  AND YEAR(f.ratio_date) = :year
            """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": input_data.year  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                    "total_financial_ratio" : ["financial ratio", "ratio","financial ratios", "ratios"],
                    "ratio_date": ["ratio date", "date", "reporting date", "data as of", "period end", "fiscal date"],
                    "debtor_days": ["debtor days", "receivables days", "days sales outstanding", "dso", "debtor turnover days", "avg collection period"],
                    "inventory_days": ["inventory days", "days inventory outstanding", "inventory holding period", "inventory turnover days", "doi"],
                    "days_payable": ["days payable", "payable days", "days payables outstanding", "dpo", "average payment period", "creditor days"],
                    "cash_conversion_cycle": ["cash conversion cycle", "ccc", "working capital cycle", "cash cycle", "net operating cycle"],
                    "working_capital_days": ["working capital days", "net working capital days", "wc days", "working capital cycle"],
                    "roce_percentage": ["roce percent","roce ratio", "roce %", "return on capital employed", "roce", "operating return", "capital efficiency"],
                    "roe_percentage": ["roe percent", "roe ratio", "roe %", "return on equity", "roe", "shareholders return", "equity return", "net worth return"]
                }

             # Filter fields if input_data.fields provided
            if input_data.fields:

                field_data = {
                    i: {
                        # "ratio date" : float(row["ratio_date"]) if row["ratio_date"] is not None else "N/A",
                        "debtor days": float(row["debtor_days"]) if row["debtor_days"] is not None else "N/A",
                        "inventory days" : float(row["inventory_days"]) if row["inventory_days"] is not None else "N/A",
                        "days payable": float(row["days_payable"]) if row["days_payable"] is not None else "N/A",
                        "cash conversion cycle": float(row["cash_conversion_cycle"]) if row["cash_conversion_cycle"] is not None else "N/A",
                        "working capital days": float(row["working_capital_days"]) if row["working_capital_days"] is not None else "N/A",
                        "roce percentage": float(row["roce_percentage"]) if row["roce_percentage"] is not None else "N/A",
                        "roe percentage": float(row["roe_percentage"]) if row["roe_percentage"] is not None else "N/A"
                    } if k == "total_financial_ratio" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }

            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}
 

    session.close()

    # ✅ FIXED: Return both comparison and year
    return Financial_Ratio_Output(
        comparison=result,
        year=input_data.year
    )



#For company info
def company_info(input_data: Company_Info_Input) -> Company_Info_Output:
    result = {}
    session = SessionLocal()

    
    for company in input_data.company_names:
        year = input_data.year
        query = text("""
                SELECT 
                c.id,
                y.year_period AS year , 
                c.company_name,
                c.sector,
                c.bse,
                c.nse,
                c.market_cap,
                c.current_price,
                c.high_low,
                c.stock_pe,
                c.book_value,
                c.dividend_yield,
                c.roce,
                c.roe,
                c.face_value,
                c.price_to_sales,
                c.sales_growth,
                c.sales_growth_3years,
                c.sales_growth_5years,
                c.sales_growth_7years,
                c.sales_growth_10years,
                c.profit_growth,
                c.profit_growth_3years,
                c.profit_growth_5years,
                c.profit_growth_7years,
                c.profit_growth_10years,
                c.eps,
                c.eps_last_year,
                c.debt,
                c.debt_3years_back,
                c.debt_5years_back,
                c.debt_7years_back,
                c.debt_10years_back
                FROM companies c
                INNER JOIN yearly_pnl y ON c.id = y.company_id
                WHERE c.company_name = :company  AND YEAR(y.year_period) = :year
            """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": f"{input_data.year}-03-31"  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue


        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                "company info": ["basic company details", "company profile", "company profile","company details",
                                "company overview","company summary", "firm profile","business profile"
                                ,"corporate profile" , "company background", "organization overview","basic information","basic info"],

                "sector": ["industry", "sector", "business segment"],
                "bse": [ "bse", "bse code", "bse ticker", "bse symbol"],
                "nse": ["nse", "nse code", "nse ticker", "nse symbol"],
                "market_cap": ["market cap", "market capitalization", "company size", "market value"],
                "current_price": ["current price", "stock price", "share price", "cmp", "current market price"],
                "high_low": ["high low", "52-week high", "52-week low", "stock range"],
                "stock_pe": ["stock pe","p/e ratio", "price to earnings"],
                "book_value": ["book value","book value per share", "net asset value"],
                "dividend_yield": ["dividend yield","yield", "dividend %", "payout ratio"],
                "roce": ["roce","return on capital employed", "efficiency ratio"],
                "roe": ["roe", "return on equity", "shareholder return"],
                "face_value": ["face value", "fv", "nominal value", "par value"],
                "price_to_sales": ["price to sales","p/s ratio", "price to revenue"],
                "sales_growth": ["sales growth", "revenue growth", "sales increase"],
                "sales_growth_3years": ["sales growth 3years", "3y sales growth", "cagr (sales 3y)"],
                "sales_growth_5years": ["sales growth 5years", "5y sales growth", "cagr (sales 5y)"],
                "sales_growth_7years": ["sales growth 7years", "7y sales growth", "cagr (sales 7y)"],
                "sales_growth_10years": ["sales growth 10years", "10y sales growth", "long-term sales growth"],
                "profit_growth": ["profit growth", "net profit growth", "earnings growth"],
                "profit_growth_3years": ["profit growth 3years", "3y profit growth", "cagr (profit 3y)"],
                "profit_growth_5years": ["profit growth 5years", "5y profit growth", "cagr (profit 5y)"],
                "profit_growth_7years": ["profit growth 7years", "7y profit growth", "cagr (profit 7y)"],
                "profit_growth_10years": ["profit growth 10years", "10y profit growth", "long-term profit growth"],
                "eps": ["eps", "earnings per share", "eps (current)"],
                "eps_last_year": ["eps last year", "eps (previous year)", "last year eps"],
                "debt": ["debt", "current debt", "total debt", "outstanding debt"],
                "debt_3years_back": ["debt 3years back", "debt (3y ago)", "historical debt (3y)"],
                "debt_5years_back": ["debt 5years back", "debt (5y ago)", "historical debt (5y)"],
                "debt_7years_back": ["debt 7years back", "debt (7y ago)", "historical debt (7y)"],
                "debt_10years_back": ["debt 10years back", "debt (10y ago)", "historical debt (10y)"]
            }

             # Filter fields if input_data.fields provided

            if input_data.fields:
                # requested_fields = [f.lower() for f in input_data.fields]
                                # field_data = {field: all_fields[field] for field in requested_fields if field in all_fields}
                field_data = {
                    i: {
                        "sector": str(row["sector"]) if row["sector"] is not None else "N/A",
                        "bse": float(row["bse"]) if row["bse"] is not None else "N/A",
                        "nse": str(row["nse"]) if row["nse"] is not None else "N/A",
                        "market_cap": float(row["market_cap"]) if row["market_cap"] is not None else "N/A",
                        "current_price": float(row["current_price"]) if row["current_price"] is not None else "N/A",
                        "high_low": row["high_low"].strip() if row["high_low"] is not None else "N/A",
                        "stock_pe": float(row["stock_pe"]) if row["stock_pe"] is not None else "N/A",
                        "book_value": float(row["book_value"]) if row["book_value"] is not None else "N/A",
                        "dividend_yield": float(row["dividend_yield"]) if row["dividend_yield"] is not None else "N/A",
                        "roce": float(row["roce"]) if row["roce"] is not None else "N/A",
                        "roe": float(row["roe"]) if row["roe"] is not None else "N/A",
                        "face_value": float(row["face_value"]) if row["face_value"] is not None else "N/A",
                        "price_to_sales": float(row["price_to_sales"]) if row["price_to_sales"] is not None else "N/A",
                        "sales_growth": float(row["sales_growth"]) if row["sales_growth"] is not None else "N/A",
                        "sales_growth_3years": float(row["sales_growth_3years"]) if row["sales_growth_3years"] is not None else "N/A",
                        "sales_growth_5years": float(row["sales_growth_5years"]) if row["sales_growth_5years"] is not None else "N/A",
                        "sales_growth_7years": float(row["sales_growth_7years"]) if row["sales_growth_7years"] is not None else "N/A",
                        "sales_growth_10years": float(row["sales_growth_10years"]) if row["sales_growth_10years"] is not None else "N/A",
                        "profit_growth": float(row["profit_growth"]) if row["profit_growth"] is not None else "N/A",
                        "profit_growth_3years": float(row["profit_growth_3years"]) if row["profit_growth_3years"] is not None else "N/A",
                        "profit_growth_5years": float(row["profit_growth_5years"]) if row["profit_growth_5years"] is not None else "N/A",
                        "profit_growth_7years": float(row["profit_growth_7years"]) if row["profit_growth_7years"] is not None else "N/A",
                        "profit_growth_10years": float(row["profit_growth_10years"]) if row["profit_growth_10years"] is not None else "N/A",
                        "eps": float(row["eps"]) if row["eps"] is not None else "N/A",
                        "eps_last_year": float(row["eps_last_year"]) if row["eps_last_year"] is not None else "N/A",
                        "debt": float(row["debt"]) if row["debt"] is not None else "N/A",
                        "debt_3years_back": float(row["debt_3years_back"]) if row["debt_3years_back"] is not None else "N/A",
                        "debt_5years_back": float(row["debt_5years_back"]) if row["debt_5years_back"] is not None else "N/A",
                        "debt_7years_back": float(row["debt_7years_back"]) if row["debt_7years_back"] is not None else "N/A",
                        "debt_10years_back": float(row["debt_10years_back"]) if row["debt_10years_back"] is not None else "N/A",
                    } if k == "company info" else (
                    str(row[k]) if k == "nse" and row[k] is not None else
                    str(row[k]) if k =="sector" and row[k] is not None else
                    row["high_low"].strip() if k == "high_low" and row[k] is not None else
                    float(row[k]) if row[k] is not None else "N/A"
                    )
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                    }

            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}



    session.close()

    # ✅ FIXED: Return both comparison and year
    return Company_Info_Output(
        comparison=result,
        year=input_data.year
    )


#For net income
def compare_net_income(input_data: CompareNetIncomeInput) -> CompareNetIncomeOutput:
    result = {}
    session = SessionLocal()


    for company in input_data.company_names:
        year = input_data.year
        query = text("""
                SELECT y.net_profit AS net_income,
                y.year_period AS year,
                y.sales,
                y.expenses,
                y.operating_profit,
                y.omp_percentage,
                y.other_income,
                y.interest,
                y.depreciation,
                y.profit_before_tax,
                y.tax_percentage,
                y.eps_in_rs,
                y.revenue,
                y.financing_profit,
                y.financing_margin_percentage
                FROM yearly_pnl y
                INNER JOIN companies c ON y.company_id = c.id
                WHERE c.company_name = :company  AND YEAR(y.year_period) = :year
            """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": int(input_data.year)  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                "yearly_income_statement":["profit and loss statement", "income statement", "financial statement","three financial statement"],
                "net_income": ["net income","net profit", "profit after tax", "bottom line"],
                "sales": ["turnover", "gross sales", "total sales","sales"],
                "expenses": ["total expenses", "operating expenses", "costs", "expenses"],
                "operating_profit" : ["ebit", "earnings before interest and taxes", "operating income", "operating profit"],
                "other_income": ["non-operating income", "miscellaneous income", "other income"],
                "interest" : ["interest expense", "finance costs", "interest paid", "interest"],
                "depreciation": ["depreciation expense", "amortization", "depreciation"],
                "profit_before_tax" : ["pbt", "earnings before tax", "pre-tax profit", "profit before tax"],
                "tax_percentage" : ["effective tax rate", "tax rate", "tax percentage"],
                "eps_in_rs" : ["earnings per share", "basic eps","eps", "eps in rs"],
                "revenue" : ["total revenue", "gross revenue", "income", "revenue"],
                "financing_profit" : ["net interest income", "financial income", "financing profit"],
                "financing_margin_percentage" : ["net interest margin", "financial margin", "financing margin percentage"],
                "omp_percentage" : ["omp", "opm", "operating profit margin","omp percentage"]
            }

             # Filter fields if input_data.fields provided
            if input_data.fields:
                # requested_fields = [f.lower() for f in input_data.fields]
                # field_data = {field: all_fields[field] for field in requested_fields if field in all_fields}

                field_data = {
                    i: {
                        "net income" : float(row["net_income"]) if row["net_income"] is not None else "N/A",
                        "sales": float(row["sales"]) if row["sales"] is not None else "N/A",
                        "expenses" : float(row["expenses"]) if row["expenses"] is not None else "N/A",
                        "operating profit": float(row["operating_profit"]) if row["operating_profit"] is not None else "N/A",
                        "other income": float(row["other_income"]) if row["other_income"] is not None else "N/A",
                        "interest": float(row["interest"]) if row["interest"] is not None else "N/A",
                        "depreciation": float(row["depreciation"]) if row["depreciation"] is not None else "N/A",
                        "profit before tax": float(row["profit_before_tax"]) if row["profit_before_tax"] is not None else "N/A",
                        "tax percentage": float(row["tax_percentage"]) if row["tax_percentage"] is not None else "N/A",
                        "eps in rs": float(row["eps_in_rs"]) if row["eps_in_rs"] is not None else "N/A",
                        "revenue": float(row["revenue"]) if row["revenue"] is not None else "N/A",
                        "financing_profit": float(row["financing_profit"]) if row["financing_profit"] is not None else "N/A",
                        "financing margin percentage": float(row["financing_margin_percentage"]) if row["financing_margin_percentage"] is not None else "N/A",
                        "omp percentage": float(row["omp_percentage"]) if row["omp_percentage"] is not None else "N/A",
                    } if k == "yearly_income_statement" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }
                # field_data = {keyword : float(row[field]) if row[field] is not None else "N/A"
                #             for keyword in input_data.fields 
                #             for field, aliases in all_fields.items()if keyword.lower() in aliases }

            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}
 
    

    session.close()

    # ✅ FIXED: Return both comparison and year
    return CompareNetIncomeOutput(
        comparison=result,
        year=input_data.year
    )


#For cash flow
def cash_flow(input_data: CashFlowInput) -> CashFlowOutput:
    result = {}
    session = SessionLocal()
    
    
    for company in input_data.company_names:
        year = input_data.year
        query = text("""
                    SELECT
                    c.company_name,
                    y.cashflow_date as year, 
                    y.cash_from_operating_activity, 
                    y.cash_from_investing_activity, 
                    y.cash_from_financing_activity, 
                    y.net_cash_flow 
                    FROM yearly_cash_flow y 
                    INNER JOIN companies c ON y.company_id = c.id
                    WHERE c.company_name = :company  AND YEAR(y.cashflow_date) = :year
                """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": int(input_data.year)  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                "cash_from_operating_activity": ["cash from operating activities","operating activities", "net cash from operations","operating cash flow","cash flow from operations"],
                "cash_from_investing_activity": ["cash from investing activities", "investing activities", "net cash used in investing","investing cash flow"],
                "cash_from_financing_activity": [ "cash from financing activities","financing activities","net cash from financing","financing cash flow"],
                "net_cash_flow": ["net cash flow", "net increase/decrease in cash","net change in cash","cash flow"],
                "cash_flow" : ["cash flow", "cash movements","statement of cash flows","overall cash flow","financial statement", "three financial statement"]
            }


             # Filter fields if input_data.fields provided
            if input_data.fields:
                # requested_fields = [f.lower() for f in input_data.fields]
                field_data = {
                    i: {
                        "cash from operating activities": float(row["cash_from_operating_activity"]) if row["cash_from_operating_activity"] is not None else "N/A",
                        "cash from investing activities": float(row["cash_from_investing_activity"]) if row["cash_from_investing_activity"] is not None else "N/A",
                        "cash from financing activities": float(row["cash_from_financing_activity"]) if row["cash_from_financing_activity"] is not None else "N/A",
                        "net cash flow": float(row["net_cash_flow"]) if row["net_cash_flow"] is not None else "N/A",
                    } if k == "cash_flow" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }
                # field_data = {field: all_fields[field] for field in requested_fields if field in all_fields}
            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}


    session.close()

    # ✅ FIXED: Return both comparison and year
    return CashFlowOutput(
        comparison=result,
        year=input_data.year
    )


#For balance sheet
def summarize_balance_sheet(input_data: SummarizeBalanceSheetInput) -> SummarizeBalanceSheetOutput:
    session = SessionLocal()
    result = {}
   
    for company in input_data.company_names:
        query = text("""
            SELECT
                c.company_name, 
                y.balance_date AS year, 
                y.total_assets,
                y.total_liabilities,
                y.borrowings AS net_loans,
                y.equity_capital,
                y.reserves,
                y.other_liabilities,
                y.fixed_assets,
                y.cwip,
                y.investments,
                y.other_assets,
                y.Preference_Capital
            FROM companies c
            INNER JOIN yearly_balance_sheet y ON c.id = y.company_id
            WHERE c.company_name = :company
            AND YEAR(y.balance_date) = :balance_date
            LIMIT 1
        """)

        try:
            row = session.execute(query, {
                "company": company,
                "balance_date": f"{input_data.year}-03-31"
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}
            continue
        
        if not row:
            result[company] = {"error": "Data not found"}
            continue
        
        # All fields available in the DB row
        all_fields = {
            "balance_sheet": [ "balance sheet", "statement of financial position","financial statement", "three financial statement"],
            "total_assets": [ "total assets","gross assets", "sum of assets"],
            "net_loans": ["net loans","net advances", "loans and advances (net)", "net loan portfolio"],
            "total_liabilities": ["total liabilities", "aggregate liabilities", "total obligations"],
            "equity_capital": [ "equity capital", "shareholders’ equity", "owner’s equity", "paid-up capital", "common equity"],
            "reserves": ["reserves", "retained earnings", "surplus reserves", "capital reserves"],
            "other_liabilities": ["other liabilities", "miscellaneous liabilities", "sundry liabilities"],
            "fixed_assets": ["fixed assets", "property, plant & equipment (PPE)", "tangible assets"],
            "cwip": [ "cwip", "capital work-in-progress", "assets under construction"],
            "investments": ["investments", "long-term investments", "financial investments"],
            "other_assets": ["other assets", "miscellaneous assets", "sundry assets"],
            "Preference_Capital": ["preference capital", "preferred stock", "preference shares"]
        }
        
        # Filter fields if input_data.fields provided
        if input_data.fields:
            # requested_fields = [f.lower() for f in input_data.fields]
            summary = {
                    i: {
                        "total assets" : float(row["total_assets"]) if row["total_assets"] is not None else "N/A",
                        "net loans": float(row["net_loans"]) if row["net_loans"] is not None else "N/A",
                        "total liabilities" : float(row["total_liabilities"]) if row["total_liabilities"] is not None else "N/A",
                        "equity capital": float(row["equity_capital"]) if row["equity_capital"] is not None else "N/A",
                        "reserves": float(row["reserves"]) if row["reserves"] is not None else "N/A",
                        "other liabilities": float(row["other_liabilities"]) if row["other_liabilities"] is not None else "N/A",
                        "fixed assets": float(row["fixed_assets"]) if row["fixed_assets"] is not None else "N/A",
                        "cwip": float(row["cwip"]) if row["cwip"] is not None else "N/A",
                        "investments": float(row["investments"]) if row["investments"] is not None else "N/A",
                        "other assets": float(row["other_assets"]) if row["other_assets"] is not None else "N/A",
                        "Preference Capital": float(row["Preference_Capital"]) if row["Preference_Capital"] is not None else "N/A",
                    } if k == "balance_sheet" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }
            # summary = {keyword : float(row[field]) if row[field] is not None else "N/A"
            #                 for keyword in input_data.fields 
            #                 for field, aliases in all_fields.items()if keyword.lower() in aliases }
        else:
            summary = all_fields

        result[company] = {input_data.year: summary}

    session.close()

    return SummarizeBalanceSheetOutput(
        comparison=result,
        year = input_data.year
    )


#For yearly shareholding
def yearly_shareholding(input_data: YearlyShareholdingInput) -> YearlyShareholdingOutput:
    result = {}
    session = SessionLocal()
    
    
    for company in input_data.company_names:
        year = input_data.year
        query = text("""        
                SELECT 
                y.yearly_shareholding_date AS year,
                y.promoters,
                y.fiis,
                y.diis,
                y.public,
                y.no_of_shareholders,
                y.others,
                y.government
                FROM yearly_shareholding y
                INNER JOIN companies c ON y.company_id = c.id
                WHERE c.company_name = :company  AND YEAR(y.yearly_shareholding_date) = :year
            """)

        try:
            row = session.execute(query, {
                "company": company,
                "year": input_data.year  # ✅ Year should be int for SQL
            }).mappings().fetchone()
        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}  # ✅ always return dict
            continue

        if not row:
            result[company] = {"error": "Data not available"}
        else:
            all_fields = {
                "shareholdingpattern": ["shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern"],
                "promoters": ["promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders"],
                "fiis": ["fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders"],
                "diis": ["diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies"],
                "public": ["public", "public holding", "retail investors", "non-institutional investors", "general public"],
                "no_of_shareholders": ["no of shareholders", "shareholder count", "number of shareholders", "investor base size"],
                "others": ["others", "others category", "miscellaneous holding", "unidentified shareholders"],
                "government": ["government", "government holding", "state holding", "public sector holding", "govt stake"]
            }


             # Filter fields if input_data.fields provided
            if input_data.fields:

                field_data = {
                    i: {
                        # "ratio date" : float(row["ratio_date"]) if row["ratio_date"] is not None else "N/A",
                        "promoters": float(row["promoters"]) if row["promoters"] is not None else "N/A",
                        "fiis" : float(row["fiis"]) if row["fiis"] is not None else "N/A",
                        "diis": float(row["diis"]) if row["diis"] is not None else "N/A",
                        "public": float(row["public"]) if row["public"] is not None else "N/A",
                        "no. of shareholders": float(row["no_of_shareholders"]) if row["no_of_shareholders"] is not None else "N/A",
                        "others": float(row["others"]) if row["others"] is not None else "N/A",
                        "government": float(row["government"]) if row["government"] is not None else "N/A"
                    } if k == "shareholdingpattern" else float(row[k]) if row[k] is not None else "N/A"
                    for i in input_data.fields
                    for k, v in all_fields.items()
                    if i.lower() in v
                }

            else:
                field_data = all_fields

            year_key = str(row["year"].year) if hasattr(row["year"], 'year') else str(row["year"])
            result[company] = {year_key: field_data}
            
    
    session.close()

    # ✅ FIXED: Return both comparison and year
    return YearlyShareholdingOutput(
        comparison=result,
        year=input_data.year
    )



#For quarterly income
def compare_quarterly_income(input_data: QuarterlyIncomeInput) -> QuarterlyIncomeOutput:
    result = {}
    session = SessionLocal()

    all_fields = {
        "quaterly_income_statement": ["profit and loss statement","quarterly profit and loss statement", "income statement" , "quarterly results", "quarterly pnl","quarter wise results"],
        "sales": ["turnover", "gross sales", "total sales", "revenue", "sales"],
        "expenses": ["total expenses", "operating expenses", "costs", "outflows", "expenses"],
        "operating_profit": ["ebit", "earnings before interest and taxes", "operating income", "operating profit"],
        "opm_percentage": ["operating margin %", "operating profit margin", "opm %", "opm percentage"],
        "other_income": ["non-operating income", "miscellaneous income", "additional income", "other income"],
        "interest": ["interest expense", "finance costs", "interest paid", "interest"],
        "depreciation": ["depreciation expense", "amortization", "depreciation"],
        "profit_before_tax": ["pbt", "earnings before tax", "pre-tax profit", "ebt", "profit before tax"],
        "tax_percentage": ["effective tax rate", "tax rate", "tax percentage"],
        "net_profit": ["net income", "profit after tax", "bottom line", "earnings", "net profit"],
        "eps_in_rs": ["earnings per share", "basic eps", "eps in rs"],
        "revenue": ["total revenue", "gross revenue", "income", "revenue"],
        "financing_profit": ["net interest income", "financial income", "financing profit"],
        "financing_margin": ["net interest margin", "financial margin", "financing margin"],
        "gross_npa": ["gross non-performing assets", "gross npa ratio", "gross npa"],
        "net_npa": ["net non-performing assets", "net npa ratio", "non-performing assets", "net npa"]
    }

    def resolve_field(user_field: str) -> Union[str, None]:
        for key, aliases in all_fields.items():
            if user_field.lower() in aliases:
                return key
        return None

    def get_month_and_adjusted_year(quarter: str, year: int):
        if "first" in quarter:
            return 6, year
        elif "second" in quarter:
            return 9, year
        elif "third" in quarter:
            return 12, year
        elif "fourth" in quarter:
            return 3, year + 1
        return None, year

    for company in input_data.company_names:
        try:
            base_query = """
                SELECT 
                    q.net_profit,
                    q.quarter_date AS year,
                    q.sales,
                    q.expenses,
                    q.operating_profit,
                    q.opm_percentage,
                    q.other_income,
                    q.interest,
                    q.depreciation,
                    q.profit_before_tax,
                    q.tax_percentage,
                    q.net_profit,
                    q.eps_in_rs,
                    q.revenue,
                    q.financing_profit,
                    q.financing_margin,
                    q.gross_npa,
                    q.net_npa
                FROM quarterly_pnl q
                INNER JOIN companies c ON q.company_id = c.id
                WHERE c.company_name = :company AND YEAR(q.quarter_date) = :year
            """

            rows = []
            params = {"company": company, "year": int(input_data.year)}
            # 
            if input_data.quarter_month:
                for qtr in input_data.quarter_month:
                    month, year_adj = get_month_and_adjusted_year(qtr, int(input_data.year))
                    query = base_query + " AND MONTH(q.quarter_date) = :month AND YEAR(q.quarter_date) = :year"
                    q_params = {"company": company, "year": year_adj, "month": month}
                    data = session.execute(text(query), q_params).mappings().fetchall()
                    rows.extend(data)
            else:
                data = session.execute(text(base_query), params).mappings().fetchall()
                rows = [r for r in data if r["year"].month != 3]
                q4_params = {"company": company, "year": int(input_data.year) + 1, "month": 3}
                q4_query = base_query + " AND MONTH(q.quarter_date) = :month AND YEAR(q.quarter_date) = :year"
                q4_data = session.execute(text(q4_query), q4_params).mappings().fetchall()
                rows.extend(q4_data)

        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}
            continue

        if not rows:
            result[company] = {"error": "Data not available"}
            continue

        resolved_fields = [resolve_field(f) for f in input_data.fields if resolve_field(f)]

        if "quaterly_income_statement" not in resolved_fields:
            field_data = {}
            for field in resolved_fields:
                field_data[field] = {
                    str(r["year"]): format(r[field], ".4f") if r[field] is not None else "N/A"
                    for r in rows
                    if field in r and (
                        r["year"].year == int(input_data.year) or
                        (r["year"].year == int(input_data.year) + 1 and r["year"].month == 3)
                    )
                }
        else:
            if isinstance(rows, dict):
                field_data = {
                    str(rows["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in rows.items() if k != "year"
                    }
                }
            else:
                field_data = {
                    str(row["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in row.items() if k != "year"
                    }
                    for row in rows
                }

        result[company] = field_data

    session.close()

    return QuarterlyIncomeOutput(
        comparison=result,
        year=input_data.year
    )


#For quarterly shareholding
def quarterly_shareholding(input_data: QuarterlyShareholdingInput) -> QuarterlyShareholdingOutput:
    result = {}
    session = SessionLocal()
    
    all_fields = {
        "shareholdingpattern": ["shareholdingpattern","shareholding pattern", "ownership structure", "capital structure", "institutional holding pattern"],
        "promoters": ["promoters", "promoter holding", "promoter group", "owner holding", "founders", "controlling shareholders"],
        "fiis": ["fiis", "fii holding", "foreign institutional investors", "foreign investors", "overseas shareholders"],
        "diis": ["diis", "dii holding", "domestic institutional investors", "mutual funds", "insurance companies"],
        "public": ["public", "public holding", "retail investors", "non-institutional investors", "general public"],
        "no_of_shareholders": ["no of shareholders", "shareholder count", "number of shareholders", "investor base size"],
        "others": ["others", "others category", "miscellaneous holding", "unidentified shareholders"],
        "government": ["government", "government holding", "state holding", "public sector holding", "govt stake"]
    }
    

    def resolve_field(user_field: str) -> Union[str, None]:
        for key, aliases in all_fields.items():
            if user_field.lower() in aliases:
                return key
        return None

    def get_month_and_adjusted_year(quarter: str, year: int):
        if "first" in quarter:
            return 6, year
        elif "second" in quarter:
            return 9, year
        elif "third" in quarter:
            return 12, year
        elif "fourth" in quarter:
            return 3, year + 1
        return None, year

    for company in input_data.company_names:
        try:
            base_query = """
            SELECT 
            q.shareholding_date AS year,
            q.promoters,
            q.fiis,
            q.diis,
            q.public,
            q.no_of_shareholders,
            q.others,
            q.government
            FROM quarterly_shareholding q
            INNER JOIN companies c ON q.company_id = c.id
            WHERE c.company_name = :company AND YEAR(q.shareholding_date) = :year
            """
               
            rows = []
            params = {"company": company, "year": int(input_data.year)}
            # 
            if input_data.quarter_month:
                for qtr in input_data.quarter_month:
                    month, year_adj = get_month_and_adjusted_year(qtr, int(input_data.year))
                    query = base_query + " AND MONTH(q.shareholding_date ) = :month AND YEAR(q.shareholding_date ) = :year"
                    q_params = {"company": company, "year": year_adj, "month": month}
                    data = session.execute(text(query), q_params).mappings().fetchall()
                    rows.extend(data)
            else:
                data = session.execute(text(base_query), params).mappings().fetchall()
                rows = [r for r in data if r["year"].month != 3]
                q4_params = {"company": company, "year": int(input_data.year) + 1, "month": 3}
                q4_query = base_query + " AND MONTH(q.shareholding_date) = :month AND YEAR(q.shareholding_date) = :year"
                q4_data = session.execute(text(q4_query), q4_params).mappings().fetchall()
                rows.extend(q4_data)

        except Exception as e:
            result[company] = {"error": f"Query failed: {str(e)}"}
            continue

        if not rows:
            result[company] = {"error": "Data not available"}
            continue

        resolved_fields = [resolve_field(f) for f in input_data.fields if resolve_field(f)]

        if "shareholdingpattern" not in resolved_fields:
            field_data = {}
            for field in resolved_fields:
                field_data[field] = {
                    str(r["year"]): format(r[field], ".4f") if r[field] is not None else "N/A"
                    for r in rows
                    if field in r and (
                        r["year"].year == int(input_data.year) or
                        (r["year"].year == int(input_data.year) + 1 and r["year"].month == 3)
                    )
                }
        else:
            if isinstance(rows, dict):
                field_data = {
                    str(rows["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in rows.items() if k != "year"
                    }
                }
            else:
                field_data = {
                    str(row["year"]): {
                        k: float(v) if v is not None else "N/A"
                        for k, v in row.items() if k != "year"
                    }
                    for row in rows
                }

        result[company] = field_data

    session.close()

    return QuarterlyIncomeOutput(
        comparison=result,
        year=input_data.year
    )


