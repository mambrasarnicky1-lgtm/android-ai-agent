import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def audit():
    xl = pd.ExcelFile(file_path)
    
    # 1. Read Code sheet correctly
    df_code = pd.read_excel(xl, sheet_name='Code', header=None)
    # Map columns based on Row 3 (index 3) and Row 2 (index 2)
    # We'll use row 3 as the primary names but fill in from row 2
    cols = list(df_code.iloc[3])
    row2 = list(df_code.iloc[2])
    for i in range(len(cols)):
        if pd.isna(cols[i]) and not pd.isna(row2[i]):
            cols[i] = row2[i]
        cols[i] = str(cols[i]).strip()
    
    df_code.columns = cols
    df_code = df_code.iloc[5:].reset_index(drop=True) # Data starts at row 5 (index 5)
    
    # Clean data
    for col in ['Code', 'Toko', 'Requisition', 'TOTAL', 'qty', 'rest', 'price', 'Sales price']:
        if col in df_code.columns:
            if col == 'Code':
                df_code[col] = df_code[col].astype(str).str.strip()
            else:
                df_code[col] = pd.to_numeric(df_code[col], errors='coerce').fillna(0)

    # 2. Read Toko sheet
    df_toko_raw = pd.read_excel(xl, sheet_name='Toko', header=None)
    # Find Code and QTY in Toko
    toko_header_idx = 0
    for i, row in df_toko_raw.iterrows():
        if 'Code' in [str(x).strip() for x in row.values]:
            toko_header_idx = i
            break
    df_toko = pd.read_excel(xl, sheet_name='Toko', header=toko_header_idx)
    df_toko.columns = [str(c).strip() for c in df_toko.columns]
    
    # 3. Read Staff sheet
    df_staff_raw = pd.read_excel(xl, sheet_name='Staff', header=None)
    staff_header_idx = 0
    for i, row in df_staff_raw.iterrows():
        if 'Code' in [str(x).strip() for x in row.values]:
            staff_header_idx = i
            break
    df_staff = pd.read_excel(xl, sheet_name='Staff', header=staff_header_idx)
    df_staff.columns = [str(c).strip() for c in df_staff.columns]

    # Analysis
    print("--- Audit Analysis ---")
    
    # Group by Code
    toko_sum = df_toko.groupby('Code')['QTY'].sum().reset_index() if 'Code' in df_toko.columns and 'QTY' in df_toko.columns else pd.DataFrame(columns=['Code', 'QTY'])
    staff_sum = df_staff.groupby('Code')['QTY'].sum().reset_index() if 'Code' in df_staff.columns and 'QTY' in df_staff.columns else pd.DataFrame(columns=['Code', 'QTY'])
    
    # Merge into Code sheet
    df_audit = df_code[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL']].copy()
    df_audit = df_audit.merge(toko_sum, on='Code', how='left').rename(columns={'QTY': 'Toko_Source'})
    df_audit = df_audit.merge(staff_sum, on='Code', how='left').rename(columns={'QTY': 'Staff_Source'})
    
    df_audit['Toko_Source'] = df_audit['Toko_Source'].fillna(0)
    df_audit['Staff_Source'] = df_audit['Staff_Source'].fillna(0)
    
    df_audit['Diff_Toko'] = df_audit['Toko'] - df_audit['Toko_Source']
    df_audit['Diff_Req'] = df_audit['Requisition'] - df_audit['Staff_Source']
    
    # Filter for interesting codes
    print("\nChecking for discrepancies in ALL codes...")
    all_diff = df_audit[(np.abs(df_audit['Diff_Toko']) > 0.01) | (np.abs(df_audit['Diff_Req']) > 0.01)]
    if not all_diff.empty:
        print(f"Found {len(all_diff)} items with discrepancies.")
        print(all_diff[['Code', 'DESCRIPTION', 'Toko', 'Toko_Source', 'Diff_Toko', 'Requisition', 'Staff_Source', 'Diff_Req']].head(20).to_string())

    # Focus on 02 and 04
    print("\n--- Specifically checking Codes starting with 02 and 04 ---")
    for prefix in ['02', '04']:
        sub = df_audit[df_audit['Code'].str.startswith(prefix)]
        print(f"\nPrefix {prefix} (Items: {len(sub)}):")
        sub_diff = sub[(np.abs(sub['Diff_Toko']) > 0.01) | (np.abs(sub['Diff_Req']) > 0.01)]
        if not sub_diff.empty:
            print("Discrepancies:")
            print(sub_diff[['Code', 'DESCRIPTION', 'Toko', 'Toko_Source', 'Diff_Toko', 'Requisition', 'Staff_Source', 'Diff_Req']].to_string())
            
            # Investigate the cause for 02 and 04
            # We can check the source entries
            for code in sub_diff['Code']:
                print(f"\nDetail for Code {code}:")
                t_entries = df_toko[df_toko['Code'] == code]
                s_entries = df_staff[df_staff['Code'] == code]
                print(f"  Toko entries: {len(t_entries)}, Sum QTY: {t_entries['QTY'].sum()}")
                print(f"  Staff entries: {len(s_entries)}, Sum QTY: {s_entries['QTY'].sum()}")
                if not t_entries.empty:
                    print("  Toko items (first 5):")
                    print(t_entries[['DATE', 'NAME', 'QTY', 'PRICE']].head(5).to_string())
                if not s_entries.empty:
                    print("  Staff items (first 5):")
                    print(s_entries[['DATE', 'NAME', 'QTY', 'PRICE']].head(5).to_string())
        else:
            print("No discrepancies found in this prefix.")

audit()
