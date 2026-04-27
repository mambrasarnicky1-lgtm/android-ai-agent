import pandas as pd

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'
xl = pd.ExcelFile(file_path)
print("Sheet names:", xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)
    print(f"\n--- Sheet: {sheet} ---")
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print(df.head(10).to_string())
