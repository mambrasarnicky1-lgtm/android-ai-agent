import openpyxl

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

def find_total():
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb['Code']
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if any('TOTAL' in str(cell).upper() for cell in row if cell is not None):
            print(f"Row {i}: {row}")

find_total()
