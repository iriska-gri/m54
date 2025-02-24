import pandas as pd
import psycopg2
import os
import numpy as np
import re

current_week = [2025, 8]

base_dir = "C:\\Project\\Magnit\\marketplace"  # Базовая директория

# Основная папка для outh
outh_base = os.path.join(base_dir, "outh", str(current_week[0]), str(current_week[1]))


# Пути для "raw" и "report"
folders = [
    os.path.join(base_dir, "in"), 
    os.path.join(outh_base, "raw"), 
    os.path.join(outh_base, "report")
]

# Создание папок
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print(f"Создана папка: {folder}")
    else:
        print(f"Папка '{folder}' уже существует.")  

path_report = [current_week[0], current_week[1] - 1]

if current_week[1]-1 == 0:
   path_report[0] = current_week[0]-1
   path_report[1] = 53
      

# находим все доступные маркетплейсы
pattern_files = [entry.name for entry in os.scandir(folders[0]) if entry.is_file()]
pattern = r"_([^_]+(?:_[^_]+)?).xls"

# Извлечение названий
marketplaces = [re.search(pattern, file).group(1) for file in pattern_files if re.search(pattern, file)]

# Получить все файлы из папки
report_path = os.path.join(base_dir, "outh", str(path_report[0]), str(path_report[1]), 'report')
report_files= [entry.name for entry in os.scandir(report_path) if entry.is_file()]

for val in marketplaces:
    pattern_path = fr"pattern_{val}"
    pattern_report = fr"_{path_report[1]}_{val}_"

    # Находим все файлы шаблона с 27777 товарками
    pattern_matching_files = [f for f in pattern_files if re.search(pattern_path, f)]
    print(pattern_matching_files,  pattern_path, ' --------------------------------------------------------------')
    # Находим нужный файл прошлых отчетов
    matching_files = [f for f in report_files if re.search(pattern_report, f)]
    print(matching_files, pattern_report)

    if matching_files:
        file_path_report = os.path.join(report_path, matching_files[0])
        df_report = pd.read_excel(file_path_report)  # Открываем файл
    #     print(f"Открыт файл: {matching_files[0]}")
        # print(df_report)
    else:
        print("Файл не найден!")

    if pattern_matching_files:
        file_path_pattern = os.path.join(folders[0], pattern_matching_files[0])    
        df_pattern = pd.read_excel(file_path_pattern)  # Открываем файл
    #     print(f"Открыт файл: {matching_files[0]}")
        print(df_pattern)
    else:
        print("Файл не найден!")
# print(report_path)
# # 



# print(report_files)  
# for val in marketplaces:
#     pattern = fr"_7_{val}_"

# # Фильтруем файлы
#     matching_files = [file for file in files if re.search(pattern, file)]

#     print(matching_files)



# # Устанавливаем соединение с базой данных
# def connect_base(): 
#     try:
#         conn = psycopg2.connect(dbname='pm', user='psqlreader',
#                             password='aImf3fivls34', host='localhost', port=8089)
#         print('\nСоединение установлено')
#         connect(conn)
#     except:
#         print('\nСоединение недоступно. Проверьте туннель к серверу')

# def connect(conn):

#         sql = f"""select
#         r.id report_id,
#         r.custom_fields ->> 'competitor' competitor,
#         r.custom_fields ->> 'ext_id' ext_id,
#         coalesce(r.sku_title, r.custom_fields ->> 'name') sku_title,
#         r.metro_price metro_price,
#         r.promo_price promo_price,
#         r.card_price card_price,
#         r.custom_fields ->> 'site_url'     site_url,
#         r.custom_fields ->> 'objstore_url' screenshot_url,
#         r.updated_at created_at,
#         t.wave,
#         r.custom_fields ->> 'subsys_art_no' subsys_art_no,
#         r.custom_fields ->> 'out_of_stock' out_of_stock,
#         r.custom_fields ->> 'seller' seller
#         --r.task_id
#         from
#         ma_metro.reports r
#         join ma_metro.tasks t on r.task_id = t.id
#         where
#             t.wave in ('mag_online_2025_8_megamarket_kvi') -- !!!!!!!! поменять название волны
#             and t.project_id = 2
#             AND r.updated_at > current_date - '30 day':: interval
#             AND r.updated_at < current_date + '1 day':: interval;"""
        
#         file_raw = os.path.join(folders[1], "raw_megamarket.xlsx")
#         file_new_raw = os.path.join(folders[1], "raw_new_megamarket.xlsx")

#         raw_data = pd.read_sql_query(sql, conn)
 

#     # Очистка данных
#         new_raw_data = raw_data.drop_duplicates(subset='subsys_art_no', keep='first')
       
#         # Фильтрация по столбцу 'out_of_stock'
#         new_raw_data = new_raw_data[(new_raw_data['out_of_stock'] == 'false') 
#                                     | (new_raw_data['out_of_stock'].isna())]
      
#         # Замена значения в столбце 'ext_id' на NaN
#         new_raw_data['promo_price'] = new_raw_data['promo_price'].replace(0, np.nan)

#         remove_if_exists(file_raw)
#         remove_if_exists(file_new_raw)

#     # Сохранение исходных данных
#         raw_data.to_excel(file_raw, index=False)
#         print(f'Сохранено: {file_raw} ----------- {raw_data.shape[0]} строк')
#         new_raw_data.to_excel(file_new_raw, index=False)
#         print(f'Сохранено: {file_new_raw} ----------- {new_raw_data.shape[0]} строк')
        

# def remove_if_exists(file_path):
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         print(f"Удален старый файл: {file_path}")

# def get_report_pattern():
#     pattern_files = [entry.name for entry in os.scandir(folders[0]) if entry.is_file()]

#     print(pattern_files)

# get_report_pattern()
# connect_base() 
