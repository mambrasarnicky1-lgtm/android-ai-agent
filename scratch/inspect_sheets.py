import pandas as pd

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

xl = pd.ExcelFile(file_path)
for sheet in xl.sheet_names:
    print(f"\n--- Sheet: {sheet} ---")
    df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
    print(df.to_string())
