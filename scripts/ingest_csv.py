import pandas as pd

df_hdfc_balancesheet = pd.read_csv("data/hdfc_balancesheet.csv")
df_hdfc_cashflow = pd.read_csv("data/hdfc_cashflow.csv")
df_hdfc_income = pd.read_csv("data/hdfc_income.csv")

df_icici_balancesheet = pd.read_csv("data/icici_balancesheet.csv")
df_icici_cashflow = pd.read_csv("data/icici_cashflow.csv")
df_icici_income = pd.read_csv("data/icici_income.csv")


print("Balance Sheet Structure")
print(df_hdfc_balancesheet.info())
print(df_hdfc_balancesheet.iloc[:, 0].tolist())
print('\n')
print("Cash Flow Structure")
print(df_hdfc_cashflow.info())
print(df_hdfc_cashflow.iloc[:, 0].tolist())
print('\n')
print("Income Statement Structure")
print(df_hdfc_income.info())
print(df_hdfc_income.iloc[:, 0].tolist())