import pandas as pd
import psycopg2
import os
import numpy as np
import re
from datetime import datetime, timedelta

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





# Устанавливаем соединение с базой данных
def connect_base(market_val, df_pattern, df_report): 
    try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
        print('\nСоединение установлено')
        connect(conn, market_val, df_pattern, df_report)
    except:
        print('\nСоединение недоступно. Проверьте туннель к серверу')
        
 

def connect(conn, market, df_pattern, df_report):

        sql = f"""select
        r.id report_id,
        r.custom_fields ->> 'competitor' competitor,
        r.custom_fields ->> 'ext_id' ext_id,
        coalesce(r.sku_title, r.custom_fields ->> 'name') sku_title,
        r.metro_price metro_price,
        r.promo_price promo_price,
        r.card_price card_price,
        r.custom_fields ->> 'site_url'     site_url,
        r.custom_fields ->> 'objstore_url' screenshot_url,
        r.updated_at created_at,
        t.wave,
        r.custom_fields ->> 'subsys_art_no' subsys_art_no,
        r.custom_fields ->> 'out_of_stock' out_of_stock,
        r.custom_fields ->> 'seller' seller
        --r.task_id
        from
        ma_metro.reports r
        join ma_metro.tasks t on r.task_id = t.id
        where
            t.wave in ('{f'mag_online_{path_report[0]}_{current_week[1]}_{market}_kvi'}') -- !!!!!!!! поменять название волны
            and t.project_id = 2
            AND r.updated_at > current_date - '30 day':: interval
            AND r.updated_at < current_date + '1 day':: interval;"""
        
        file_raw = os.path.join(folders[1], f"raw_{market}.xlsx")
        file_new_raw = os.path.join(folders[1], f"raw_new_{market}.xlsx")

        raw_data = pd.read_sql_query(sql, conn)
 

    # Очистка данных
        new_raw_data = raw_data.drop_duplicates(subset='subsys_art_no', keep='first')
       
        # Фильтрация по столбцу 'out_of_stock'
        new_raw_data = new_raw_data[(new_raw_data['out_of_stock'] == 'false') 
                                    | (new_raw_data['out_of_stock'].isna())]
      
        # Замена значения в столбце 'ext_id' на NaN
        new_raw_data['promo_price'] = new_raw_data['promo_price'].replace(0, np.nan)

        remove_if_exists(file_raw)
        remove_if_exists(file_new_raw)

    # Сохранение исходных данных
        raw_data.to_excel(file_raw, index=False)
        print(f'Сохранено: {file_raw} ----------- {raw_data.shape[0]} строк')
        new_raw_data.to_excel(file_new_raw, index=False)
        print(f'Сохранено: {file_new_raw} ----------- {new_raw_data.shape[0]} строк')

        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        print(f'MIP_Report_for_Magnit_{today.year}_{today.isocalendar()[1]}_{market}_{tomorrow.strftime("%d.%m")} - {new_raw_data.shape[0]}_raw')
        new_raw_data = new_raw_data.rename(columns={
            'sku_title': 'Наименование КНК',
            'metro_price': 'Цена регулярная за 1 единицу товара',
            'promo_price':'Цена акционная за 1 единицу товара',
            'site_url': 'Ссылка',
            'screenshot_url': 'Ссылка на фото карточки товара',
            'created_at': 'Дата парсинга',
            'card_price':'Цена по карте'

        })
        # df_pattern  = pd.DataFrame() 
        # 
        new_raw_data  = pd.DataFrame(new_raw_data)  
        new_raw_data['subsys_art_no'] = new_raw_data['subsys_art_no'].astype(str)
        df_pattern = df_pattern[['Маркетплейс', 'Идентификатор ТП', 'Код ТП', 'Наименование ТП из карточки товара', 'ГР20', 'ГР21', 'ГР22','ГР23']]
   
        df_pattern  = pd.DataFrame(df_pattern) 
        df_pattern['Код ТП'] = df_pattern['Код ТП'].astype(str)
        # df_pattern.to_excel(os.path.join(folders[1], f"file_{market}.xlsx"), index=False)
        # print('сохранено что-то')
        # df_pattern.to_excel(os.path.join(folders[1], f"file_{market}.xlsx"), index=False)

        
        df_report = df_report[['Код ТП', 'кол-во шт. в уп']]
        df_report  = pd.DataFrame(df_report)  
        df_report['Код ТП'] = df_report['Код ТП'].astype(str)
        # df_report.to_excel(os.path.join(folders[1], f"file_report_{market}.xlsx"), index=False)
        result  = pd.DataFrame()  
        
        result = pd.merge(new_raw_data, df_pattern, left_on='subsys_art_no', right_on='Код ТП', how='right')
        # print( result, '1???????????????????????????')
        result = pd.merge(df_report, result, on='Код ТП', how='right')
        # print(result, '2???????????????????????????')
        result = result[[
            'Маркетплейс', 'Идентификатор ТП', 'Код ТП', 'Наименование ТП из карточки товара', 'ГР20', 'ГР21', 'ГР22','ГР23', 'Наименование КНК',	
            'кол-во шт. в уп',	
            'Цена регулярная за 1 единицу товара',	'Цена акционная за 1 единицу товара', 'Цена по карте',	'Ссылка',	'Ссылка на фото карточки товара',	'Дата парсинга'
        ]]
        # print(market)
        # print(result, '-----------------???????????????????????????----------')
        # print(market)
        # result.to_excel(f'C:/Project/Magnit/marketplace/for_import/{file_name}.xlsx', sheet_name='Report', index =False)
        report_fin_path = os.path.join(base_dir, "outh", str(current_week[0]), str(current_week[1]), 'report')
        # result['Дата парсинга'] = result['Дата парсинга'].dt.strftime('%Y-%m-%d %H:%M:%S')
        result.to_excel(f'{report_fin_path}/MIP_Report_for_Magnit_{today.year}_{today.isocalendar()[1]}_{market}_{tomorrow.strftime("%d.%m")}.xlsx', sheet_name='Report', index =False)
        print(f'MIP_Report_for_Magnit_{today.year}_{today.isocalendar()[1]}_{market}_{tomorrow.strftime("%d.%m")} - {result["Ссылка"].notna().sum()}')
    

        

def remove_if_exists(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Удален старый файл: {file_path}")




for val in marketplaces:
    pattern_path = fr"pattern_{val}"
    pattern_report = fr"_{path_report[1]}_{val}_"

    # Находим все файлы шаблона с 27777 товарками
    pattern_matching_files = [f for f in pattern_files if re.search(pattern_path, f)]

   
    # Находим нужный файл прошлых отчетов
    matching_files = [f for f in report_files if re.search(pattern_report, f)]


    if matching_files:
        file_path_report = os.path.join(report_path, matching_files[0])
        df_report = pd.read_excel(file_path_report)  # Открываем файл
    #     print(f"Открыт файл: {matching_files[0]}")
     
    else:
        print("Файл не найден!")

    if pattern_matching_files:
        file_path_pattern = os.path.join(folders[0], pattern_matching_files[0])    
        df_pattern = pd.read_excel(file_path_pattern)  # Открываем файл

    else:
        print("Файл не найден!")
    
    connect_base(val, df_pattern, df_report)




