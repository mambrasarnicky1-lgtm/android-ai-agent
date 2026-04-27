import openpyxl
import pandas as pd

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def read_hidden_use():
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb['Use']
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(row)
    
    df = pd.DataFrame(data)
    print("--- Use Sheet (Hidden) ---")
    print(df.head(20).to_string())

read_hidden_use()
