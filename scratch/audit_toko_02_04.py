import openpyxl
import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def audit_toko_02_04():
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb['Toko']
    data = []
    for row in ws.iter_rows(min_row=5, values_only=True):
        if any(row):
            data.append(row)
    
    df = pd.DataFrame(data)
    df = df[[0, 4, 9, 12]].rename(columns={0: 'Date', 4: 'Code', 9: 'Total', 12: 'FinalTotal'})
    
    df['Code'] = df['Code'].astype(str).str.strip()
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
    df['FinalTotal'] = pd.to_numeric(df['FinalTotal'], errors='coerce').fillna(0)
    
    df['Diff'] = df['FinalTotal'] - df['Total']
    
    print("--- Toko Sheet: Prefix 02 and 04 Discrepancies ---")
    for pref in ['02', '04']:
        sub = df[df['Code'].str.startswith(pref)]
        sub_err = sub[np.abs(sub['Diff']) > 0.1]
        print(f"\nPrefix {pref} (Items with Diff: {len(sub_err)}):")
        if not sub_err.empty:
            print(sub_err.to_string())
        else:
            print("No discrepancies found in this prefix.")

audit_toko_02_04()
