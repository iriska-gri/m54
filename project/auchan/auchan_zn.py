
import pandas as pd
import glob
import os

class Auchan_zn():

    def __init__(self):
        pass

    def file_zn(self):

        self.settings = {
                'zn' : {
                    'sheet_name' : 'ЗНАКОВЫЕ ТОВАРЫ_НГ',
                    'columns' : {
                                'NEED': 'Название артикула',
                                'Артикул': 'Артикул Метро',
                                'Название артикула': 'Название артикула_site',
                                'ШК': 'Артикул МГБ',
                                'СЕГМЕНТ': 'Код корзины',
                                'НАЗВАНИЕ СЕГМЕНТА': 'Категория',
                                'Бренд /Производитель товара': 'Бренд',
                                'Описание товара (для мониторинга)': 'Описание'
                                },
                    'add' : {
                        'Название города' : 'Moscow',
                        'Конкурент': "Pyaterochka Gur'evskij 17"
                    },
                    'column' : 'Артикул МГБ',
                    'save': {'to_excel': '.xlsx'}
                },
                'Анкета в заявку' : {
                    'sheet_name' : 'ЗНАКОВЫЕ ТОВАРЫ_НГ',
                    'columns' : {
                                'Название артикула': 'ART_NAME',
                                'Артикул': 'SKU',
                                'ШК': 'BARCODE',
                                'СЕГМЕНТ': 'SEGMENT_NUM',
                                'НАЗВАНИЕ СЕГМЕНТА': 'SEGMENT_NAM',
                                'Бренд /Производитель товара': 'BREND',
                                },
                    'add' : {
                        'REGION' : 'MOSCOW',
                        'CITY': 'MOSCOW',
                        'TYPE': 'KVI',
                        'CONTRACTOR_NAME': 'MA',
                      
                   
                        'PRODUCT_NAME_CONTR': '',
                        'PRODUCT WEIGHT_CONTR': '',
                        'MANUF_CONTR': '',
                        'REG_PRICE': '',
                        'CARD_PRICE': '',
                        'PROMO_PRICE': '',
                        'PHOTO': '',
                     

                    },
                    'column' : 'BARCODE',
                    'save': {'to_csv': '.csv', 'to_excel': '.xlsx'}
                },
        }

        self.applicationForm = ['REGION',
            'CITY',
            'COMPETITOR',
            'ADDRESS',
            'SEGMENT_NUM',
            'SEGMENT_NAM',
            'SKU',
            'ART_NAME',
            'BARCODE',
            'PRODUCT_NAME_CONTR',
            'PRODUCT WEIGHT_CONTR',
            'MANUF_CONTR',
            'BREND',
            'REG_PRICE',
            'CARD_PRICE',
            'PROMO_PRICE',
            'TYPE',
            'CONTRACTOR_NAME',
            'PHOTO',
            'ID_COMP'
            ]
        
        self.re = ['Код города',
            'Название города',
            'Артикул Метро',
            'Артикул МГБ',
            'Название артикула',
            'Название артикула_site',
            'Бренд',
            'Метод сбора',
            'Описание',
            'Единица измерения цены Мetro',
            'Вес Метро',
            'Вид упаковки',
            'Страна',
            'Код конкурента',
            'Конкурент',
            'Категория',
            'Подкатегория',
            'Код корзины',
            'Название корзины',
            'ЦЕНА, (в рубл. С НДС)',
            'Промо отметка (1- Да, 0 - нет)',
            'OOS (отметка) (1- Да, 0 - нет)',
            'Бренд конкурента',
            'Дата',
            'Гиперссылка на фотоколлаж',
            'Гиперссылка на фото цены',
            'Гиперссылка на фото товара',
            'ID отчета  агентства']

        df = pd.DataFrame()  

        for [key, val] in self.settings.items():
            # print(glob.glob(f'{key}.*'))
            file_path = glob.glob(f'C:/Project/Auchan/for_import/{key}.*')
            # file_path = glob.glob(f'C:/Project/Auchan/for_import/Анкета в заявку.*')

            if file_path:
                for i in file_path:
                    if os.path.exists(i):
                        os.remove(i)
            
            df = self.file_formation(val, key)
            df[val['column']] = df[val['column']].astype('string')
            for [key_save, val_save] in val['save'].items():
                getattr(df, key_save)(f'C:/Project/Auchan/for_import/{key}{val_save}', index =False)
        return self.mess


    def file_formation(self,settings_file, filename):
        file = pd.read_excel(glob.glob('C:/Project/Auchan/tz/ТЗ_*')[0], sheet_name = settings_file['sheet_name'], header = 0)
        file.rename(columns=settings_file['columns'], inplace=True)
        file = self.new_column(file, settings_file['add'], filename)
        
        return file
    
    def new_column(self, filepd, add, filename):
        newcolumn =  {
            'empty':  ['Код города', 'Метод сбора', 'Единица измерения цены Мetro',
                    'Вес Метро','Вид упаковки','Страна','Код конкурента','Подкатегория', 'Название корзины',
                    'ЦЕНА, (в рубл. С НДС)','Промо отметка (1- Да, 0 - нет)',
                    'OOS (отметка) (1- Да, 0 - нет)','Бренд конкурента', 'Дата',
                    'Гиперссылка на фотоколлаж','Гиперссылка на фото цены','Гиперссылка на фото товара',
                    'ID отчета  агентства'],
            **self.wsiterator(add)
        }
        
        for [key, val] in newcolumn.items():
           
            if key == "empty" :
                for x in val:
                    filepd[x] = ''
            else:
                filepd[key] = val
        self.mess = [] # Заполняем информацию для отображения в приложении об анкете в заявку
        if (filename == 'zn'):
            filepd = filepd[self.re].drop_duplicates()
            print(f'Количество товаров в файле zn - {filepd.shape[0]}')
        if (filename == 'Анкета в заявку'):
            filepd = self.apFile(filepd)
            filepd = filepd[self.applicationForm].drop_duplicates()
            
        return filepd 
    
    def wsiterator(self, setting):
        newdict = {}
        for [key, val] in setting.items():
            newdict[key] = val
        return newdict
    
    def apFile(self, df):
        
        

        file = pd.read_excel(glob.glob('C:/Project/Auchan/tz/АП_*')[0], sheet_name = 'Конкуренты_виды мониторинга', header = 0)
        file = file[file['ЗНАКОВЫЕ ТОВАРЫ'] == 'ЗНАКОВЫЕ ТОВАРЫ']
        file = file[['COMPETITOR', 'ADDRESS', 'ID_COMP']]
        file['key1'] = 0
        df['key1'] = 0
        df = df.rename(columns={'ADDRESS': 'ADDRESS_y', 'ID_COMP': 'ID_COMP_y'})
        dffile = df.merge(file, on='key1', how='right')
        self.mess.extend([f'Количество адресов - {file.shape[0]}',
                          f'Количество товаров - {df.shape[0]}',
                          f'Файл с потребностями "Анкета в заявку" сформирован. Количество SKU к поиску в каждой ТТ - {dffile.shape[0]}'
                        ])
        
        return dffile
        