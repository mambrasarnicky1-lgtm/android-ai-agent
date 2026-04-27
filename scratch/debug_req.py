import pandas as pd

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

xl = pd.ExcelFile(file_path)
df = pd.read_excel(xl, sheet_name='Req ', nrows=10)
print("\n--- Sheet: Req ---")
print("Columns:", df.columns.tolist())
for i, row in df.iterrows():
    print(f"Row {i}: {row.tolist()}")
