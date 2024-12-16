import pandas as pd
import os
import glob
from google.oauth2.service_account import Credentials
import gspread

class Auchan_frov(): 
    def __init__(self):
        pass

    def filefrov(self):
      
        self.dir_path = r'C:/Project/Auchan/tz'

        self.settings = {
                'frov.xlsx' : {
                    'sheet_name' : 'ФРОВ_список_форма',
                    'columns' : {
                                'NEED': 'Название артикула',
                                'ART_NUM': 'Артикул Метро',
                                'ART_NAME': 'Название артикула_site',
                                'Что ищут мониторщики у конкурентов': 'Описание',
                                'ШК': 'Артикул МГБ',
                                'SEGMENT_NAME': 'Подкатегория'
                                },
                    'add' : {
                        'Название корзины' : 'ФРОВ'
                        },
                    'mess' : 'Файл с потребностями ФРОВ сформирован. Количество SKU к поиску в каждой ТТ - '
                },

                'frov_szt.xlsx' : {
                    'sheet_name' : 'СОЦТОВАРЫ_список_форма',
                    'columns' : {
                                'NEED': 'Название артикула',
                                'ОПИСАНИЕ': 'Описание',
                                'SEGMENT_NAME': 'Подкатегория'
                                },
                    'add' : {
                                'Название корзины' : 'СОЦТОВАРЫ',
                                'Артикул Метро': ''
                            },
                    'mess' : 'Файл с потребностями СЗТ(Соцтовары) сформирован. Количество SKU к поиску в каждой ТТ - '
                    
                },

                'frov_szt_emblematika.xlsx' : {
                    'sheet_name' : 'Эмблематичные товары',
                    'columns' : {
                                    'Артикул': 'Артикул Метро',
                                    'Описание товара (для мониторинга)': 'Описание',
                                    'СЕГМЕНТ': 'Код корзины',
                                    'НАЗВАНИЕ СЕГМЕНТА': 'Категория',
                                    'Бренд /Производитель товара': 'Бренд'
                                },
                    'add' : {
                                'Название корзины' : 'Эмблематичные товары',
                                'Подкатегория': ''
                            },
                    'mess' : 'Файл с потребностями Эмблематика сформирован. Количество SKU к поиску в каждой ТТ - '
                }
            }
            
        

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
        mass_quantily = []
        for [key, val] in self.settings.items():
            file_path = f'C:/Project/Auchan/{key}'
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
               
                df = pd.concat([df, self.file_formation(key, val)]) 
                df.to_excel(f'C:/Project/Auchan/for_import/{key}', index =False)
                quantily = len(df[df['Название корзины'] == val['add']['Название корзины']])
                mass_quantily.append(f'{val["mess"]} {quantily}')
        print("Формирование файлов завершена")


        return mass_quantily

    def file_formation(self, filename, settings_file):

        file = pd.read_excel(glob.glob('C:/Project/Auchan/tz/ТЗ_*')[0], sheet_name = settings_file['sheet_name'], header = 0)
        file.rename(columns=settings_file['columns'], inplace=True)
        file = self.new_column(file, settings_file['add'])
        # Забираем все Артикул Метро из словаря tov_szt и вставляем в одноименный столбец стобец 
        if (filename == 'frov_szt.xlsx'):
            df_tov_szt = pd.read_excel(r'C:\Project\Auchan\tz\tov_szt.xlsx')
            result_dict = df_tov_szt.set_index('Название артикула')['Артикул Метро'].to_dict()
            file['Артикул Метро'] = file['Название артикула'].map(result_dict)
        return file

    def new_column(self, filepd, add):
        newcolumn =  {
            'empty':  ['Код города', 'Бренд','Метод сбора', 'Единица измерения цены Мetro',
                    'Вес Метро','Вид упаковки','Страна','Код конкурента','Категория',
                    'Код корзины', 'ЦЕНА, (в рубл. С НДС)','Промо отметка (1- Да, 0 - нет)',
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

        filepd = filepd[self.re].drop_duplicates()
        return filepd  
    
    # def googletable(self):
    #     way = gspread.oauth()
    #     needed_sheet = way.open_by_url('https://docs.google.com/spreadsheets/d/1ZZQMx1IXqaKdaU1YfnfG54Imxr04il3ot_ArE3GE-Ec/edit?gid=0#gid=0')
            
    #     sh = needed_sheet.worksheet("реестр(актуальный)")

    #     # создаем датафрейм из справочника TT
    #     data = sh.get_all_values()
    #     headers = data.pop(0)
    #     dict_tt = pd.DataFrame(data, columns=headers)
    #     print(dict_tt)

      
    def wsiterator(self, setting):
        newdict = { 'Название города' : 'Moscow',
                    'Конкурент' : "Pyaterochka Gur'evskij 17",
                    'Название артикула_site': '',
                    'Артикул МГБ': ''
                    }
        for [key, val] in setting.items():
            newdict[key] = val
        return newdict