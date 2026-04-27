import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def analyze_code_sheet():
    # Read without header first to find the header row
    raw_df = pd.read_excel(file_path, sheet_name='Code', nrows=10)
    print("Raw Column Preview:")
    print(raw_df.head(5))
    
    # Try to find which row contains 'Code' or 'DESCRIPTION'
    header_idx = None
    for i, row in raw_df.iterrows():
        if 'Code' in row.values or 'DESCRIPTION' in row.values:
            header_idx = i + 1 # pandas header is 0-indexed but it includes the row we found? 
            # Actually if I read with header=i, then row i becomes the header.
            header_idx = i
            break
    
    if header_idx is None:
        print("Could not find header row. Using columns as is.")
        df = raw_df
    else:
        print(f"Found header at row {header_idx}")
        df = pd.read_excel(file_path, sheet_name='Code', header=header_idx)
    
    print("Columns found:", df.columns.tolist())
    
    # Strip column names
    df.columns = [str(c).strip() for c in df.columns]
    
    # Identify discrepancies
    print("\n--- Code Sheet Analysis ---")
    
    # Check for TOTAL discrepancy
    if 'Toko' in df.columns and 'Requisition' in df.columns and 'TOTAL' in df.columns:
        df['Toko_val'] = pd.to_numeric(df['Toko'], errors='coerce').fillna(0)
        df['Req_val'] = pd.to_numeric(df['Requisition'], errors='coerce').fillna(0)
        df['Total_val'] = pd.to_numeric(df['TOTAL'], errors='coerce').fillna(0)
        
        df['Calc_Total'] = df['Toko_val'] + df['Req_val']
        diff_total = df[np.abs(df['Calc_Total'] - df['Total_val']) > 0.01]
        
        if not diff_total.empty:
            print(f"Found {len(diff_total)} rows with TOTAL discrepancy (Toko + Req != TOTAL):")
            # Filter out rows where Code is NaN
            diff_total = diff_total[diff_total['Code'].notna()]
            print(diff_total[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'Calc_Total']].head(20).to_string())

    if 'qty' in df.columns and 'TOTAL' in df.columns and 'rest' in df.columns:
        df['qty_val'] = pd.to_numeric(df['qty'], errors='coerce').fillna(0)
        df['Rest_val'] = pd.to_numeric(df['rest'], errors='coerce').fillna(0)
        df['Calc_Rest'] = df['qty_val'] - df['Total_val']
        diff_rest = df[np.abs(df['Calc_Rest'] - df['Rest_val']) > 0.01]
        
        if not diff_rest.empty:
            print(f"\nFound {len(diff_rest)} rows with 'rest' discrepancy (qty - TOTAL != rest):")
            diff_rest = diff_rest[diff_rest['Code'].notna()]
            print(diff_rest[['Code', 'DESCRIPTION', 'qty', 'TOTAL', 'rest', 'Calc_Rest']].head(20).to_string())

    # Search for codes starting with 02 and 04
    print("\n--- Items with Code 02-xxxx and 04-xxxx ---")
    if 'Code' in df.columns:
        df['Code_Str'] = df['Code'].astype(str)
        code_02 = df[df['Code_Str'].str.startswith('02')]
        code_04 = df[df['Code_Str'].str.startswith('04')]
        
        print(f"Items starting with 02: {len(code_02)}")
        print(f"Items starting with 04: {len(code_04)}")
        
        for prefix, sub_df in [('02', code_02), ('04', code_04)]:
            if not sub_df.empty:
                print(f"\nChecking Code {prefix} specifically:")
                # Calculation check in this subset
                sub_df['Toko_v'] = pd.to_numeric(sub_df['Toko'], errors='coerce').fillna(0)
                sub_df['Req_v'] = pd.to_numeric(sub_df['Requisition'], errors='coerce').fillna(0)
                sub_df['Tot_v'] = pd.to_numeric(sub_df['TOTAL'], errors='coerce').fillna(0)
                sub_df['Qty_v'] = pd.to_numeric(sub_df['qty'], errors='coerce').fillna(0)
                sub_df['Rst_v'] = pd.to_numeric(sub_df['rest'], errors='coerce').fillna(0)
                
                sub_diff = sub_df[(np.abs((sub_df['Toko_v'] + sub_df['Req_v']) - sub_df['Tot_v']) > 0.01) | 
                                  (np.abs((sub_df['Qty_v'] - sub_df['Tot_v']) - sub_df['Rst_v']) > 0.01)]
                if not sub_diff.empty:
                    print("Discrepancies found in these items:")
                    print(sub_diff[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'qty', 'rest']].to_string())
                else:
                    print(f"No calculation errors found in prefix {prefix}.")

analyze_code_sheet()
