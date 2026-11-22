"""build_excel.py.

Builds excel/duka_branch_summary.xlsx containing:
1. Raw SalesData table
2. SUMIFS Branch Revenue table
3. XLOOKUP Region column
4. Pivot summary table of Revenue by Branch and Channel matching notebook totals.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill
import pandas as pd

df = pd.read_csv('duka_sales.csv', parse_dates=['order_date'])
df['revenue'] = df['quantity'] * df['unit_price']

os.makedirs('excel', exist_ok=True)
wb = openpyxl.Workbook()

# Sheet 1: SalesData
ws_data = wb.active
ws_data.title = 'SalesData'
headers = [
    'order_id',
    'order_date',
    'branch',
    'channel',
    'product',
    'unit_price',
    'quantity',
    'revenue',
]
ws_data.append(headers)

for row in df[headers].itertuples(index=False):
  ws_data.append(list(row))

# Sheet 2: Summary
ws_sum = wb.create_sheet(title='BranchSummary')

# Region Lookup Table (Columns G & H)
ws_sum['G2'] = 'Branch'
ws_sum['H2'] = 'Region'
regions = [
    ('Nairobi', 'Capital'),
    ('Mombasa', 'Coast'),
    ('Kisumu', 'Western'),
    ('Nakuru', 'Rift Valley'),
    ('Eldoret', 'Rift Valley'),
]
for i, (b, r) in enumerate(regions, start=3):
  ws_sum[f'G{i}'] = b
  ws_sum[f'H{i}'] = r

# Table 1: Branch Revenue with SUMIFS and XLOOKUP
ws_sum['A2'] = 'Branch'
ws_sum['B2'] = 'Region'
ws_sum['C2'] = 'Total Revenue'

branches = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
for idx, branch in enumerate(branches, start=3):
  ws_sum[f'A{idx}'] = branch
  ws_sum[f'B{idx}'] = f'=XLOOKUP(A{idx}, G$3:G$7, H$3:H$7, "Unknown")'
  ws_sum[f'C{idx}'] = f'=SUMIFS(SalesData!H:H, SalesData!C:C, A{idx})'

ws_sum['A8'] = 'Total'
ws_sum['C8'] = '=SUM(C3:C7)'

# Table 2: Pivot Table (Branch by Channel)
ws_sum['A11'] = 'Branch'
ws_sum['B11'] = 'In-store'
ws_sum['C11'] = 'Online'
ws_sum['D11'] = 'Phone order'
ws_sum['E11'] = 'Total'

for idx, branch in enumerate(branches, start=12):
  ws_sum[f'A{idx}'] = branch
  ws_sum[f'B{idx}'] = (
      f'=SUMIFS(SalesData!H:H, SalesData!C:C, A{idx}, SalesData!D:D, "In-store")'
  )
  ws_sum[f'C{idx}'] = (
      f'=SUMIFS(SalesData!H:H, SalesData!C:C, A{idx}, SalesData!D:D, "Online")'
  )
  ws_sum[f'D{idx}'] = f'=SUMIFS(SalesData!H:H, SalesData!C:C, A{idx},'
  ' SalesData!D:D, "Phone order")'
  ws_sum[f'E{idx}'] = f'=SUM(B{idx}:D{idx})'

ws_sum['A17'] = 'Total'
ws_sum['B17'] = '=SUM(B12:B16)'
ws_sum['C17'] = '=SUM(C12:C16)'
ws_sum['D17'] = '=SUM(D12:D16)'
ws_sum['E17'] = '=SUM(E12:E16)'

# Styling
hdr_font = Font(bold=True, color='FFFFFF')
hdr_fill = PatternFill(
    start_color='1F4E78', end_color='1F4E78', fill_type='solid'
)
for col in ['A', 'B', 'C']:
  ws_sum[f'{col}2'].font = hdr_font
  ws_sum[f'{col}2'].fill = hdr_fill

for col in ['A', 'B', 'C', 'D', 'E']:
  ws_sum[f'{col}11'].font = hdr_font
  ws_sum[f'{col}11'].fill = hdr_fill

wb.save('excel/duka_branch_summary.xlsx')
print('excel/duka_branch_summary.xlsx successfully created.')