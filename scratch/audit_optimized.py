import pandas as pd
import numpy as np
import gc

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def audit():
    print("Loading workbook...")
    with pd.ExcelFile(file_path) as xl:
        # --- 1. CODE SHEET (SUMMARY) ---
        print("Processing 'Code' sheet...")
        df_code_raw = pd.read_excel(xl, sheet_name='Code', header=None)
        cols = list(df_code_raw.iloc[3])
        row2 = list(df_code_raw.iloc[2])
        for i in range(len(cols)):
            if pd.isna(cols[i]) and not pd.isna(row2[i]):
                cols[i] = row2[i]
            cols[i] = str(cols[i]).strip()
        
        df_code = df_code_raw.iloc[5:].copy()
        df_code.columns = cols
        del df_code_raw
        gc.collect()
        
        df_code = df_code[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'qty', 'rest']].copy()
        df_code['Code'] = df_code['Code'].astype(str).str.strip()
        for col in ['Toko', 'Requisition', 'TOTAL', 'qty', 'rest']:
            df_code[col] = pd.to_numeric(df_code[col], errors='coerce').fillna(0)

        # --- 2. TOKO SHEET (SOURCE) ---
        print("Processing 'Toko' sheet...")
        df_toko_raw = pd.read_excel(xl, sheet_name='Toko', header=None)
        # Use col indices 4 (Code) and 7 (QTY)
        df_toko = pd.DataFrame({
            'Code': df_toko_raw.iloc[4:, 4].astype(str).str.strip(),
            'QTY': pd.to_numeric(df_toko_raw.iloc[4:, 7], errors='coerce').fillna(0)
        })
        del df_toko_raw
        gc.collect()
        toko_summary = df_toko.groupby('Code')['QTY'].sum().reset_index()
        del df_toko
        gc.collect()

        # --- 3. REQ SHEET (SOURCE) ---
        print("Processing 'Req ' sheet...")
        df_req_raw = pd.read_excel(xl, sheet_name='Req ', header=None)
        # Use col indices 1 (Code) and 4 (QTY)
        df_req = pd.DataFrame({
            'Code': df_req_raw.iloc[3:, 1].astype(str).str.strip(),
            'QTY': pd.to_numeric(df_req_raw.iloc[3:, 4], errors='coerce').fillna(0)
        })
        del df_req_raw
        gc.collect()
        req_summary = df_req.groupby('Code')['QTY'].sum().reset_index()
        del df_req
        gc.collect()

        # --- 4. AUDIT MERGE ---
        print("Merging data for audit...")
        df_audit = df_code.merge(toko_summary, on='Code', how='left').rename(columns={'QTY': 'Toko_Source'})
        df_audit = df_audit.merge(req_summary, on='Code', how='left').rename(columns={'QTY': 'Req_Source'})
        
        df_audit['Toko_Source'] = df_audit['Toko_Source'].fillna(0)
        df_audit['Req_Source'] = df_audit['Req_Source'].fillna(0)
        
        df_audit['Diff_Toko'] = df_audit['Toko'] - df_audit['Toko_Source']
        df_audit['Diff_Req'] = df_audit['Requisition'] - df_audit['Req_Source']
        df_audit['Calc_Total'] = df_audit['Toko'] + df_audit['Requisition']
        df_audit['Diff_Internal_Total'] = df_audit['TOTAL'] - df_audit['Calc_Total']

        # --- 5. REPORTING ---
        print("\n--- AUDIT REPORT ---\n")
        
        # Discrepancies in Summary vs Source
        ext_diff = df_audit[(np.abs(df_audit['Diff_Toko']) > 0.01) | (np.abs(df_audit['Diff_Req']) > 0.01)]
        if not ext_diff.empty:
            print(f"1. Discrepancies (Code vs Source Sheets): {len(ext_diff)} items found.")
            # Only print rows where Code is not 'nan'
            ext_diff = ext_diff[ext_diff['Code'] != 'nan']
            if not ext_diff.empty:
                print(ext_diff[['Code', 'DESCRIPTION', 'Toko', 'Toko_Source', 'Diff_Toko', 'Requisition', 'Req_Source', 'Diff_Req']].head(50).to_string())

        # Internal Total Errors
        int_diff = df_audit[np.abs(df_audit['Diff_Internal_Total']) > 0.01]
        if not int_diff.empty:
            print(f"\n2. Internal Errors (Toko + Req != TOTAL): {len(int_diff)} items found.")
            int_diff = int_diff[int_diff['Code'] != 'nan']
            if not int_diff.empty:
                print(int_diff[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'Calc_Total', 'Diff_Internal_Total']].head(50).to_string())

        # Specific Prefixes
        print("\n3. Focus: Prefixes 02 and 04")
        for prefix in ['02', '04']:
            sub = df_audit[df_audit['Code'].str.startswith(prefix)]
            sub_err = sub[(np.abs(sub['Diff_Toko']) > 0.01) | (np.abs(sub['Diff_Req']) > 0.01) | (np.abs(sub['Diff_Internal_Total']) > 0.01)]
            print(f"\n   Prefix {prefix} (Errors: {len(sub_err)}):")
            if not sub_err.empty:
                print(sub_err[['Code', 'DESCRIPTION', 'Toko', 'Toko_Source', 'Requisition', 'Req_Source', 'Diff_Internal_Total']].to_string())

audit()
gc.collect()
