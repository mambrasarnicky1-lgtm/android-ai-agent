import openpyxl
import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def get_sheet_data(sheet):
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)
    return pd.DataFrame(data)

def audit():
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    
    ws_code = wb['Code']
    df_code_raw = get_sheet_data(ws_code)
    
    cols = list(df_code_raw.iloc[3])
    row2 = list(df_code_raw.iloc[2])
    for i in range(len(cols)):
        if pd.isna(cols[i]) and not pd.isna(row2[i]):
            cols[i] = row2[i]
        cols[i] = str(cols[i]).strip()
    
    df_code = df_code_raw.iloc[5:].copy()
    df_code.columns = cols
    df_code = df_code[['Code', 'DESCRIPTION', 'qty', 'Toko', 'Requisition', 'TOTAL', 'rest']].copy()
    df_code['Code'] = df_code['Code'].astype(str).str.strip()
    for col in ['qty', 'Toko', 'Requisition', 'TOTAL', 'rest']:
        df_code[col] = pd.to_numeric(df_code[col], errors='coerce').fillna(0)
    
    # Internal Calculation Audit
    df_code['Calc_Total'] = df_code['Toko'] + df_code['Requisition']
    df_code['Calc_Rest'] = df_code['qty'] - df_code['TOTAL']
    
    df_code['Diff_Total'] = df_code['TOTAL'] - df_code['Calc_Total']
    df_code['Diff_Rest'] = df_code['rest'] - df_code['Calc_Rest']
    
    print("--- Internal Calculations Audit ---")
    int_err = df_code[(np.abs(df_code['Diff_Total']) > 0.01) | (np.abs(df_code['Diff_Rest']) > 0.01)]
    int_err = int_err[df_code['Code'] != 'None']
    if not int_err.empty:
        print(f"Found {len(int_err)} calculation errors in 'Code' sheet:")
        print(int_err[['Code', 'DESCRIPTION', 'qty', 'Toko', 'Requisition', 'TOTAL', 'Calc_Total', 'rest', 'Calc_Rest']].head(50).to_string())
    else:
        print("No internal calculation errors found in 'Code' sheet.")

    # Check specifically for codes 02 and 04
    print("\n--- Prefix 02 and 04 Audit ---")
    for pref in ['02', '04']:
        sub = df_code[df_code['Code'].str.startswith(pref)]
        print(f"\nPrefix {pref} (Items: {len(sub)}):")
        sub_err = sub[(np.abs(sub['Diff_Total']) > 0.01) | (np.abs(sub['Diff_Rest']) > 0.01)]
        if not sub_err.empty:
            print("Errors found:")
            print(sub_err[['Code', 'DESCRIPTION', 'qty', 'Toko', 'Requisition', 'TOTAL', 'Calc_Total', 'rest', 'Calc_Rest']].to_string())
        else:
            # Maybe the selisih is in QTY?
            print("No internal calc errors. Checking if any item has TOTAL > 0 or QTY > 0:")
            sub_active = sub[(sub['TOTAL'] > 0) | (sub['qty'] > 0)]
            print(sub_active[['Code', 'DESCRIPTION', 'qty', 'Toko', 'Requisition', 'TOTAL', 'rest']].head(10).to_string())

audit()
