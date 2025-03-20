import pandas as pd
import os

file_path = 'C:/Project/Magnit/promo/MIP_Report_for_Magnit_2025-02-07_part1_mag_online_promo_fri_2025_6.csv'
df = pd.read_csv(file_path)
df = df[['Сеть', 'Наименование товара', 'Наименование товара Магнит']]
# print(df)
pivot_table_name = df.groupby(['Сеть'])['Наименование товара'].nunique().reset_index()
pivot_table_magnit = df.groupby(['Сеть'])['Наименование товара Магнит'].nunique().reset_index()
pivot_table = pivot_table_name.merge(pivot_table_magnit, how="right")
pivot_table["% Соотношение"] = (pivot_table["Наименование товара Магнит"] / pivot_table["Наименование товара"]) * 100
pivot_table.to_excel('C:/Project/Magnit/promo/calc/Calc_for_Magnit_2025-02-07_part1_mag_online_promo_fri_2025_6.xlsx')
