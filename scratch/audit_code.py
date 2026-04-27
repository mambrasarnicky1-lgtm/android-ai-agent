import pandas as pd
import numpy as np

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def analyze_code_sheet():
    # Headers are likely in row 2 (0-indexed: row 1 or 2)
    # Based on preview, row 2 (index 1) has the labels but row 1 has some too.
    # Let's try header=2 (3rd row)
    df = pd.read_excel(file_path, sheet_name='Code', header=2)
    
    # Identify discrepancies
    print("--- Code Sheet Analysis ---")
    
    # Check if 'Toko', 'Requisition', 'TOTAL' columns exist
    if 'Toko' in df.columns and 'Requisition' in df.columns and 'TOTAL' in df.columns:
        # Fill NaNs with 0
        df['Toko'] = df['Toko'].fillna(0)
        df['Requisition'] = df['Requisition'].fillna(0)
        df['TOTAL'] = df['TOTAL'].fillna(0)
        
        df['Calc_Total'] = df['Toko'] + df['Requisition']
        diff_total = df[np.abs(df['Calc_Total'] - df['TOTAL']) > 0.01]
        
        if not diff_total.empty:
            print(f"Found {len(diff_total)} rows with TOTAL discrepancy:")
            print(diff_total[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'Calc_Total']].head(20))
        else:
            print("No discrepancy found in TOTAL (Toko + Requisition).")

    if 'qty' in df.columns and 'TOTAL' in df.columns and 'rest' in df.columns:
        df['qty'] = df['qty'].fillna(0)
        df['rest'] = df['rest'].fillna(0)
        df['Calc_Rest'] = df['qty'] - df['TOTAL']
        diff_rest = df[np.abs(df['Calc_Rest'] - df['rest']) > 0.01]
        
        if not diff_rest.empty:
            print(f"\nFound {len(diff_rest)} rows with 'rest' discrepancy:")
            print(diff_rest[['Code', 'DESCRIPTION', 'qty', 'TOTAL', 'rest', 'Calc_Rest']].head(20))

    # Search for codes starting with 02 and 04
    print("\n--- Items with Code 02-xxxx and 04-xxxx ---")
    df['Code_Str'] = df['Code'].astype(str)
    code_02 = df[df['Code_Str'].str.startswith('02')]
    code_04 = df[df['Code_Str'].str.startswith('04')]
    
    print(f"Items starting with 02: {len(code_02)}")
    print(f"Items starting with 04: {len(code_04)}")
    
    # Analyze 02 and 04 specifically
    for prefix, sub_df in [('02', code_02), ('04', code_04)]:
        if not sub_df.empty:
            print(f"\nDiscrepancies in Code {prefix}:")
            # Check for any calculation errors in these subsets
            sub_diff = sub_df[(np.abs((sub_df['Toko'] + sub_df['Requisition']) - sub_df['TOTAL']) > 0.01) | 
                              (np.abs((sub_df['qty'] - sub_df['TOTAL']) - sub_df['rest']) > 0.01)]
            if not sub_diff.empty:
                print(sub_diff[['Code', 'DESCRIPTION', 'Toko', 'Requisition', 'TOTAL', 'qty', 'rest']])
            else:
                print(f"No calculation errors found in prefix {prefix}.")

analyze_code_sheet()
