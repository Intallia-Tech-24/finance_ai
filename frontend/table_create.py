import pandas as pd

def three_statements_df(data):
    income_statement = {}
    cash_flow_statement = {}
    balance_sheet = {}

    # Categorize each section of the data
    for section in data:
        comparison = section.get("comparison", {})
        for company, year_data in comparison.items():
            for date_key, content in year_data.items():
                financials = content.get("financial statement", {})
                if "sales" in financials:
                    income_statement.update(financials)
                elif "cash from operating activities" in financials:
                    cash_flow_statement.update(financials)
                elif "total assets" in financials:
                    balance_sheet.update(financials)

    # Convert dict to DataFrame with index reset
    def dict_to_df(d):
        df = pd.DataFrame(d.items(), columns=["Financial Statement", "Value"])
        df["Value"] = df["Value"].astype(str)
        return df


    df_income = dict_to_df(income_statement)
    df_cash = dict_to_df(cash_flow_statement)
    df_balance = dict_to_df(balance_sheet)

    return df_income, df_cash, df_balance




def flatten_all_financials(tool_result):
    results = []

    for company, years_data in tool_result.get("comparison", {}).items():
        for year, year_data in years_data.items():
            record = {"Company": company, "Year": year}
            financials = {}

            for key, value in year_data.items():
                if isinstance(value, dict):
                    financials.update(value)
                else:
                    financials[key] = value

            # Convert to DataFrame format
            for field, val in financials.items():
                results.append({
                    "Company": company,
                    "Year": year,
                    "Field": field,
                    "Value": val
                })

    df = pd.DataFrame(results)
    df["Value"] = df["Value"].astype(str)
    return df
