import openpyxl
import pandas as pd

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def inspect_02_04():
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb['Code']
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(row)
    
    df = pd.DataFrame(data)
    # Filter for rows where column 0 starts with 02 or 04
    rows_02 = df[df[0].astype(str).str.startswith('02')]
    rows_04 = df[df[0].astype(str).str.startswith('04')]
    
    print("--- Prefix 02 Items in 'Code' sheet ---")
    print(rows_02.to_string())
    print("\n--- Prefix 04 Items in 'Code' sheet ---")
    print(rows_04.to_string())

inspect_02_04()
