import openpyxl
import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def audit_toko():
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb['Toko']
    data = []
    # Row 5 is first data row
    for row in ws.iter_rows(min_row=5, values_only=True):
        if any(row):
            data.append(row)
    
    # Columns based on Row 4 (index 3)
    # Date, id, Name, nan, Code, Item, Type, Qty, Price, Total, nan, nan, FinalTotal
    df = pd.DataFrame(data)
    # We'll just map indices
    # 0: Date, 1: ID, 2: Name, 4: Code, 5: Item, 7: QTY, 8: Price, 9: Total
    df = df[[0, 4, 7, 8, 9]].rename(columns={0: 'Date', 4: 'Code', 7: 'QTY', 8: 'Price', 9: 'Total_in_Sheet'})
    
    df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce').fillna(0)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
    df['Total_in_Sheet'] = pd.to_numeric(df['Total_in_Sheet'], errors='coerce').fillna(0)
    
    df['Calc_Total'] = df['QTY'] * df['Price']
    df['Diff'] = df['Total_in_Sheet'] - df['Calc_Total']
    
    err = df[np.abs(df['Diff']) > 0.1]
    print(f"--- Toko Sheet Internal Audit ---")
    if not err.empty:
        print(f"Found {len(err)} row errors in Toko sheet (QTY * Price != Total):")
        print(err.head(50).to_string())
    else:
        print("No row errors found in Toko sheet.")

audit_toko()
