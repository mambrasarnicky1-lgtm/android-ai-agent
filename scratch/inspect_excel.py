import pandas as pd

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    print("Sheet names:", xl.sheet_names)
except Exception as e:
    print(f"Error reading file: {e}")
