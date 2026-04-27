import openpyxl
import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def audit_toko_totals():
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb['Toko']
    data = []
    for row in ws.iter_rows(min_row=5, values_only=True):
        if any(row):
            data.append(row)
    
    df = pd.DataFrame(data)
    # 9: Total, 12: FinalTotal
    df = df[[0, 4, 9, 12]].rename(columns={0: 'Date', 4: 'Code', 9: 'Total', 12: 'FinalTotal'})
    
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
    df['FinalTotal'] = pd.to_numeric(df['FinalTotal'], errors='coerce').fillna(0)
    
    df['Diff'] = df['FinalTotal'] - df['Total']
    err = df[np.abs(df['Diff']) > 0.1]
    
    print("--- Toko Sheet: Total vs FinalTotal Audit ---")
    if not err.empty:
        print(f"Found {len(err)} discrepancies:")
        print(err.head(50).to_string())
    else:
        print("No discrepancies between Total and FinalTotal.")

audit_toko_totals()
