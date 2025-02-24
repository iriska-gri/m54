import pandas as pd
import os
import glob
import numpy as np
from datetime import datetime, timedelta

class Marketplace():

    def __init__(self):
        pass

    def settings(self):
        get_file = {
            'megamarket':
            {
                'raw_data': 'raw_data_megamarket.xlsx',
                'file': 'pattern_megamarket.xlsx',
                'file_count': 'megamarket.xlsx'
            },
            'ozon':
            {
                'raw_data': 'raw_data_ozon.xlsx',
                'file': 'pattern_ozon.xlsx',
                'file_count': 'ozon.xlsx'
            },
            'wildberries':
            {
                'raw_data': 'raw_data_wildberries.xlsx',
                'file': 'pattern_wildberries.xlsx',
                'file_count': 'wildberries.xlsx'
            },
            'yandex_market':
            {
                'raw_data': 'raw_data_yandex_market.xlsx',
                'file': 'pattern_yandex_market.xlsx',
                'file_count': 'yandex_market.xlsx'
            },  
        }

        for [key, val] in get_file.items():
            self.open_file(key, val)


    def open_file(self, file_name, val):

        raw_data = pd.read_excel(f'C:/Project/Magnit/marketplace/raw_data/{val["raw_data"]}', sheet_name = 'result 1', header = 0)
        # Удаление дубликатов на основе столбца 'subsys_art_no'

        raw_data = raw_data.drop_duplicates(subset='subsys_art_no', keep='first')
        # Фильтрация по столбцу 'out_of_stock'
        raw_data = raw_data[(raw_data['out_of_stock'] == False) | (raw_data['out_of_stock'].isna())]

        # Замена значения в столбце 'ext_id' на NaN
        raw_data['promo_price'] = raw_data['promo_price'].replace(0, np.nan)
        raw_data['out_of_stock'] = raw_data['out_of_stock'].replace(False, 'false')
        file_path = f'C:/Project/Magnit/marketplace/for_import/raw/raw_new_{file_name}.xlsx'
        if os.path.exists(file_path):
            os.remove(file_path)
        raw_data.to_excel(file_path, index =False)
        # Получение сегодняшней даты
        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        print(f'MIP_Report_for_Magnit_{today.year}_{today.isocalendar()[1]}_{file_name}_{tomorrow.strftime("%d.%m")} - {raw_data.shape[0]}_raw')
        raw_data = raw_data.rename(columns={
            'sku_title': 'Наименование КНК',
            'metro_price': 'Цена регулярная за 1 единицу товара',
            'promo_price':'Цена акционная за 1 единицу товара',
            'site_url': 'Ссылка',
            'screenshot_url': 'Ссылка на фото карточки товара',
            'created_at': 'Дата парсинга',
            'card_price':'Цена по карте'

        })
        file = pd.read_excel(f'C:/Project/Magnit/marketplace/file/{val["file"]}', sheet_name = 'Report', header = 0)
        file = file[['Маркетплейс', 'Идентификатор ТП', 'Код ТП', 'Наименование ТП из карточки товара', 'ГР20', 'ГР21', 'ГР22','ГР23']]
        
        file_count = pd.read_excel(f'C:/Project/Magnit/marketplace/file/{val["file_count"]}', sheet_name = 'Report', header = 0)
        file_count = file_count[['Код ТП', 'кол-во шт. в уп']]
      
        result = pd.merge(raw_data, file, left_on='subsys_art_no', right_on='Код ТП', how='right')
        result = pd.merge(file_count, result, on='Код ТП', how='right')
        result = result[[
            'Маркетплейс', 'Идентификатор ТП', 'Код ТП', 'Наименование ТП из карточки товара', 'ГР20', 'ГР21', 'ГР22','ГР23', 'Наименование КНК',	
            'кол-во шт. в уп',	
            'Цена регулярная за 1 единицу товара',	'Цена акционная за 1 единицу товара', 'Цена по карте',	'Ссылка',	'Ссылка на фото карточки товара',	'Дата парсинга'
        ]]
        # result.to_excel(f'C:/Project/Magnit/marketplace/for_import/{file_name}.xlsx', sheet_name='Report', index =False)
        result.to_excel(f'C:/Project/Magnit/marketplace/for_import/MIP_Report_for_Magnit_{today.year}_{today.isocalendar()[1]}_{file_name}_{tomorrow.strftime("%d.%m")}.xlsx', sheet_name='Report', index =False)
        print(f'MIP_Report_for_Magnit_{today.year}_{today.isocalendar()[1]}_{file_name}_{tomorrow.strftime("%d.%m")} - {result["Ссылка"].notna().sum()}')
        print(file_name)
        # print(raw_data)