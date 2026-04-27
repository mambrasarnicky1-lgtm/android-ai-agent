import openpyxl

file_path = r'C:\Users\ASUS\Downloads\04 Toko-Requisition April 2026.xlsx'

wb = openpyxl.load_workbook(file_path, read_only=True)
print("All sheets:")
for sheet in wb.sheetnames:
    ws = wb[sheet]
    print(f"- {sheet} (Visible: {ws.sheet_state})")
