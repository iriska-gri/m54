import pandas as pd
import os
import glob

class Marketplace():

    def __init__(self):
        pass

    def settings(self):
        get_file = {
            'market.xlsx':
            {
                'raw_data': 'raw_data_megamarket.xlsx',
                'file': 'pattern_megamarket.xlsx',
                'file_count': 'megamarket.xlsx'
            },
            'ozon.xlsx':
            {
                'raw_data': 'raw_data_ozon.xlsx',
                'file': 'pattern_ozon.xlsx',
                'file_count': 'ozon.xlsx'
            },
            'wildberries.xlsx':
            {
                'raw_data': 'raw_data_wildberries.xlsx',
                'file': 'pattern_wildberries.xlsx',
                'file_count': 'wildberries.xlsx'
            },
            'yandex_market.xlsx':
            {
                'raw_data': 'raw_data_yandex_market.xlsx',
                'file': 'pattern_yandex_market.xlsx',
                'file_count': 'yandex_market.xlsx'
            },  
        }

        for [key, val] in get_file.items():
            self.open_file(key, val)


    def open_file(self, file_name, val):
        print(val['raw_data'])
        # for [key, file] in val.items():
        #     print(key, file)
        raw_data = pd.read_excel(f'C:/Project/Magnit/marketplace/raw_data/{val["raw_data"]}', sheet_name = 'result 1', header = 0)
        raw_data = raw_data.rename(columns={
            'sku_title': 'Наименование КНК',
            'metro_price': 'Цена регулярная за 1 единицу товара',
            'promo_price':'Цена акционная за 1 единицу товара',
            'site_url': 'Ссылка',
            'screenshot_url': 'Ссылка на фото карточки товара',
            'created_at': 'Дата парсинга'
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
            'Цена регулярная за 1 единицу товара',	'Цена акционная за 1 единицу товара',	'Ссылка',	'Ссылка на фото карточки товара',	'Дата парсинга'
        ]]
        result.to_excel(f'C:/Project/Magnit/marketplace/for_import/{file_name}', index =False)

        
        
        print(result)
        # print(raw_data)