import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def audit_discrepancy():
    xl = pd.ExcelFile(file_path)
    
    # 1. Read 'Toko' sheet
    df_toko_raw = pd.read_excel(xl, sheet_name='Toko')
    # Find header for Toko
    header_idx_toko = None
    for i, row in df_toko_raw.iterrows():
        if 'Code' in row.values or 'CODE' in row.values:
            header_idx_toko = i
            break
    if header_idx_toko is not None:
        df_toko = pd.read_excel(xl, sheet_name='Toko', header=header_idx_toko)
    else:
        df_toko = df_toko_raw
    
    # 2. Read 'Staff' sheet
    df_staff_raw = pd.read_excel(xl, sheet_name='Staff')
    header_idx_staff = None
    for i, row in df_staff_raw.iterrows():
        if 'Code' in row.values or 'CODE' in row.values:
            header_idx_staff = i
            break
    if header_idx_staff is not None:
        df_staff = pd.read_excel(xl, sheet_name='Staff', header=header_idx_staff)
    else:
        df_staff = df_staff_raw

    # 3. Read 'Code' sheet
    df_code_raw = pd.read_excel(xl, sheet_name='Code')
    header_idx_code = None
    for i, row in df_code_raw.iterrows():
        if 'Code' in row.values or 'CODE' in row.values:
            header_idx_code = i
            break
    if header_idx_code is not None:
        df_code = pd.read_excel(xl, sheet_name='Code', header=header_idx_code)
    else:
        df_code = df_code_raw

    # Clean columns
    df_toko.columns = [str(c).strip() for c in df_toko.columns]
    df_staff.columns = [str(c).strip() for c in df_staff.columns]
    df_code.columns = [str(c).strip() for c in df_code.columns]

    print("Toko columns:", df_toko.columns.tolist())
    print("Staff columns:", df_staff.columns.tolist())
    print("Code columns:", df_code.columns.tolist())

    # Grouping
    # Assuming 'QTY' column in Toko and Staff
    qty_col_toko = 'QTY' if 'QTY' in df_toko.columns else ('qty' if 'qty' in df_toko.columns else None)
    qty_col_staff = 'QTY' if 'QTY' in df_staff.columns else ('qty' if 'qty' in df_staff.columns else None)
    
    if not qty_col_toko:
        # Look for other potential names
        for c in df_toko.columns:
            if 'qty' in c.lower(): qty_col_toko = c; break
            
    if not qty_col_staff:
        for c in df_staff.columns:
            if 'qty' in c.lower(): qty_col_staff = c; break

    print(f"Using QTY columns: Toko={qty_col_toko}, Staff={qty_col_staff}")

    # Sum by Code
    toko_sums = df_toko.groupby('Code')[qty_col_toko].sum().reset_index() if qty_col_toko and 'Code' in df_toko.columns else pd.DataFrame()
    staff_sums = df_staff.groupby('Code')[qty_col_staff].sum().reset_index() if qty_col_staff and 'Code' in df_staff.columns else pd.DataFrame()

    # Merge with Code sheet
    # Code sheet has 'Toko' and 'Requisition' (which might be Staff)
    # Let's check 'Requisition' column in Code sheet
    
    df_merged = df_code[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL']].copy()
    df_merged = df_merged.merge(toko_sums, on='Code', how='left', suffixes=('', '_calc_toko'))
    df_merged = df_merged.merge(staff_sums, on='Code', how='left', suffixes=('', '_calc_staff'))
    
    # Fill NaNs
    df_merged['Toko'] = pd.to_numeric(df_merged['Toko'], errors='coerce').fillna(0)
    df_merged['Requisition'] = pd.to_numeric(df_merged['Requisition'], errors='coerce').fillna(0)
    df_merged[qty_col_toko if qty_col_toko else 'calc_toko'] = pd.to_numeric(df_merged[qty_col_toko] if qty_col_toko in df_merged else 0, errors='coerce').fillna(0)
    df_merged[qty_col_staff if qty_col_staff else 'calc_staff'] = pd.to_numeric(df_merged[qty_col_staff] if qty_col_staff in df_merged else 0, errors='coerce').fillna(0)

    # Comparison
    df_merged['Diff_Toko'] = df_merged['Toko'] - df_merged[qty_col_toko] if qty_col_toko in df_merged else 0
    df_merged['Diff_Req'] = df_merged['Requisition'] - df_merged[qty_col_staff] if qty_col_staff in df_merged else 0
    
    discrepancies = df_merged[(np.abs(df_merged['Diff_Toko']) > 0.01) | (np.abs(df_merged['Diff_Req']) > 0.01)]
    
    print("\n--- Discrepancies between Source Sheets (Toko/Staff) and Summary (Code) ---")
    if not discrepancies.empty:
        print(discrepancies[['Code', 'DESCRIPTION', 'Toko', qty_col_toko, 'Diff_Toko', 'Requisition', qty_col_staff, 'Diff_Req']].head(30).to_string())
    else:
        print("No discrepancies found between source sheets and summary.")

    # Check specifically for codes 02 and 04
    print("\n--- Analyzing Codes 02 and 04 specifically ---")
    df_merged['Code_Str'] = df_merged['Code'].astype(str)
    for prefix in ['02', '04']:
        sub = df_merged[df_merged['Code_Str'].str.startswith(prefix)]
        print(f"\nPrefix {prefix}:")
        if sub.empty:
            print("No items found.")
        else:
            sub_diff = sub[(np.abs(sub['Diff_Toko']) > 0.01) | (np.abs(sub['Diff_Req']) > 0.01)]
            if not sub_diff.empty:
                print("Discrepancies found:")
                print(sub_diff[['Code', 'DESCRIPTION', 'Toko', qty_col_toko, 'Diff_Toko', 'Requisition', qty_col_staff, 'Diff_Req']].to_string())
            else:
                print("No discrepancies found in this prefix.")

audit_discrepancy()
