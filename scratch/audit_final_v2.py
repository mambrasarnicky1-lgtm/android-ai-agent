import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def audit():
    xl = pd.ExcelFile(file_path)
    
    # --- 1. CODE SHEET (SUMMARY) ---
    df_code_raw = pd.read_excel(xl, sheet_name='Code', header=None)
    # Mapping columns based on row 2 and 3
    # Row 2 (index 2) has some headers, Row 3 (index 3) has others
    cols = list(df_code_raw.iloc[3])
    row2 = list(df_code_raw.iloc[2])
    for i in range(len(cols)):
        if pd.isna(cols[i]) and not pd.isna(row2[i]):
            cols[i] = row2[i]
        cols[i] = str(cols[i]).strip()
    
    df_code = df_code_raw.iloc[5:].copy()
    df_code.columns = cols
    df_code = df_code.reset_index(drop=True)
    
    # Basic data cleaning for Code sheet
    for col in ['Code', 'Toko', 'Requisition', 'TOTAL', 'qty', 'rest']:
        if col in df_code.columns:
            if col == 'Code':
                df_code[col] = df_code[col].astype(str).str.strip()
            else:
                df_code[col] = pd.to_numeric(df_code[col], errors='coerce').fillna(0)

    # --- 2. TOKO SHEET (SOURCE) ---
    # Based on debug: Code is col index 4, QTY is col index 7
    df_toko_raw = pd.read_excel(xl, sheet_name='Toko', header=None)
    # Find start row (where row 3 or 4 starts having dates)
    # Actually let's just find where 'Code' or 'CODE' is
    toko_code_col = 4
    toko_qty_col = 7
    # Data likely starts around row 4 or 5
    df_toko = df_toko_raw.iloc[4:].copy()
    df_toko_clean = pd.DataFrame({
        'Code': df_toko[toko_code_col].astype(str).str.strip(),
        'QTY': pd.to_numeric(df_toko[toko_qty_col], errors='coerce').fillna(0)
    })
    toko_summary = df_toko_clean.groupby('Code')['QTY'].sum().reset_index()

    # --- 3. REQ SHEET (SOURCE) ---
    # Based on debug: Code is col index 1, QTY is col index 4
    df_req_raw = pd.read_excel(xl, sheet_name='Req ', header=None)
    req_code_col = 1
    req_qty_col = 4
    df_req = df_req_raw.iloc[3:].copy() # Row 3 is first data row
    df_req_clean = pd.DataFrame({
        'Code': df_req[req_code_col].astype(str).str.strip(),
        'QTY': pd.to_numeric(df_req[req_qty_col], errors='coerce').fillna(0)
    })
    req_summary = df_req_clean.groupby('Code')['QTY'].sum().reset_index()

    # --- 4. AUDIT MERGE ---
    df_audit = df_code[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'qty', 'rest']].copy()
    df_audit = df_audit.merge(toko_summary, on='Code', how='left').rename(columns={'QTY': 'Toko_Source'})
    df_audit = df_audit.merge(req_summary, on='Code', how='left').rename(columns={'QTY': 'Req_Source'})
    
    df_audit['Toko_Source'] = df_audit['Toko_Source'].fillna(0)
    df_audit['Req_Source'] = df_audit['Req_Source'].fillna(0)
    
    df_audit['Diff_Toko'] = df_audit['Toko'] - df_audit['Toko_Source']
    df_audit['Diff_Req'] = df_audit['Requisition'] - df_audit['Req_Source']
    
    # Internal checks
    df_audit['Calc_Total'] = df_audit['Toko'] + df_audit['Requisition']
    df_audit['Diff_Internal_Total'] = df_audit['TOTAL'] - df_audit['Calc_Total']
    
    # --- 5. REPORTING ---
    print("--- AUDIT REPORT: 04 Toko-Requisition April 2026 ---\n")
    
    # Discrepancies in Summary Sheet vs Source Sheets
    ext_diff = df_audit[(np.abs(df_audit['Diff_Toko']) > 0.01) | (np.abs(df_audit['Diff_Req']) > 0.01)]
    print(f"1. Discrepancies between Summary (Code sheet) and Source (Toko/Req sheets): {len(ext_diff)} items found.")
    if not ext_diff.empty:
        print(ext_diff[['Code', 'DESCRIPTION', 'Toko', 'Toko_Source', 'Diff_Toko', 'Requisition', 'Req_Source', 'Diff_Req']].to_string())

    # Discrepancies in Internal Calculations
    int_diff = df_audit[np.abs(df_audit['Diff_Internal_Total']) > 0.01]
    print(f"\n2. Internal Summary Errors (Toko + Requisition != TOTAL): {len(int_diff)} items found.")
    if not int_diff.empty:
        print(int_diff[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'Calc_Total', 'Diff_Internal_Total']].to_string())

    # Special Focus: Codes 02 and 04
    print("\n3. Focus: Codes starting with 02 and 04")
    for prefix in ['02', '04']:
        sub = df_audit[df_audit['Code'].str.startswith(prefix)]
        print(f"\n   Prefix {prefix} Analysis:")
        sub_diff = sub[(np.abs(sub['Diff_Toko']) > 0.01) | (np.abs(sub['Diff_Req']) > 0.01) | (np.abs(sub['Diff_Internal_Total']) > 0.01)]
        if not sub_diff.empty:
            print(sub_diff[['Code', 'DESCRIPTION', 'Toko', 'Toko_Source', 'Requisition', 'Req_Source', 'Diff_Internal_Total']].to_string())
            
            # Find specific cause
            for code in sub_diff['Code']:
                print(f"\n      Investigating Code {code}:")
                t_source = df_toko_clean[df_toko_clean['Code'] == code]
                r_source = df_req_clean[df_req_clean['Code'] == code]
                print(f"      - Toko Source Count: {len(t_source)}, Total QTY: {t_source['QTY'].sum()}")
                print(f"      - Req Source Count: {len(r_source)}, Total QTY: {r_source['QTY'].sum()}")
                print(f"      - Summary Sheet Values: Toko={df_audit.loc[df_audit['Code']==code, 'Toko'].values[0]}, Requisition={df_audit.loc[df_audit['Code']==code, 'Requisition'].values[0]}")
        else:
            print("      No discrepancies found in this prefix.")

audit()
