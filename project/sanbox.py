import pandas as pd
import gspread
import datetime
import glob
import os
from datetime import timedelta

# Задаем путь к папке path
try:
    path = sys.argv[1] + "/"
except:
    # path = '/Users/mariapetrova/Documents/Magnit/promo/path/'
    path = 'C:/Project/Magnit/brand/'

inpath = path + "in/"
outpath = path + "tmp/"

report_vert2 = pd.read_csv(inpath + 'MIP_Report_for_Magnit__part2.csv')
report_vert2['Бренд'] = report_vert2['Бренд'].astype(str).str.lower().str.replace(r'\s+', '', regex=True)
brand = pd.read_excel(inpath + 'brand_new.xlsx')
brand['promo_brand'] = brand['promo_brand'].astype(str).str.lower().str.replace(r'\s+', '', regex=True)
result = pd.merge(report_vert2, brand, left_on='Бренд', right_on='promo_brand', how='left')
# 🔹 Заменяем старый столбец цен новым
result['Бренд'] = result['client_brand']
result = result.drop(columns=['promo_brand', 'client_brand'])
result.to_csv(outpath + 'MIP_Report_for_Magnit_part2.csv', index=False)