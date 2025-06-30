import pandas as pd

df1 = pd.read_csv("data/hdfc_balancesheet.csv")

print(df1.info())
print(df1.iloc[:, 0].tolist())