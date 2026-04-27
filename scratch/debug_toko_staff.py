import pandas as pd

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

xl = pd.ExcelFile(file_path)
for sheet in ['Toko', 'Staff']:
    df = pd.read_excel(xl, sheet_name=sheet, nrows=5)
    print(f"\n--- Sheet: {sheet} ---")
    print("Columns:", df.columns.tolist())
    for i, row in df.iterrows():
        print(f"Row {i}: {row.tolist()}")
