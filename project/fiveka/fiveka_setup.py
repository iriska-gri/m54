import pandas as pd
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import gspread

# try:
#     arg_names = ['command', 'path']
#     args = dict(zip(arg_names, sys.argv))
#     path = args['path'] + "/"
#     inpath = path + "in/"
#     sys.path.append(inpath)
# except:
class Fiveka():


    # ID гуглотаблицы со словарями    
    # SPREADSHEET_ID = '19hOfOlyoKLqcevZLKevkHULf0qNBwnoenjpLtJkGUmA'

    # Авторизация в гугл
    # CREDENTIALS_PATH = inpath + 'credentials.json'
    # SCOPE = ['https://spreadsheets.google.com/feeds',
    #          'https://www.googleapis.com/auth/drive']
    # credentials = ServiceAccountCredentials.from_json_keyfile_name(
    #     CREDENTIALS_PATH, SCOPE)
    # gc = gspread.authorize(credentials)

    # Функция для импорта листов из гуглотаблиц
    def __init__(self):
        self.path = 'C:/Project/5ka/'

        self.inpath = self.path + "in/"
        self.outpath = self.path + "tmp/"

    def get_data_from_gsheet(self, sheet_title):
        gc = gspread.oauth()
        sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/19hOfOlyoKLqcevZLKevkHULf0qNBwnoenjpLtJkGUmA/edit?gid=0#gid=0')
        # wks = gc.open_by_key(SPREADSHEET_ID).worksheet(sheet_title)
        wks = sh.worksheet(sheet_title)
        data = wks.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        return df

    def merge_columns_from_dict(self, dict_data, dict_old):
        # Добавляем из dict_old оставшиеся необходимые столбцы по столбцу "сцепка"
        merged_df = pd.merge(dict_data, dict_old[['сцепка', 'Название 3-го уровня иерархии (расшифровка)', 'Название группы материалов (расшифровка)', 'Задание', 'Описание', 'Группировка', 'keys']], on='сцепка', how='left')
        return merged_df
    
    def fileGeneration(self):

        # Файл матрицы клиента (классификатор)
        df = pd.read_excel(self.inpath + 'Классификатор 1 кв 2025.xlsx', sheet_name='1 кв 2025')
   

        # Файл словаря-классификатора
        dict_old = self.get_data_from_gsheet('Лист1')

        # # Создание словаря
        dict_data = df[['Название 1-го уровня иерархии', 'Название 2-го уровня иерархии', 'Название 3-го уровня иерархии', 'Группа материалов', 'Название группы материалов']]
        dict_data = dict_data.rename(columns={"Название 1-го уровня иерархии": "fields.level1",
                                            "Название 2-го уровня иерархии": "fields.level2",
                                            "Название 3-го уровня иерархии": "fields.level3",
                                            "Название группы материалов": "fields.level4",
                                            "Название 3-го уровня иерархии (расшифровка)": "level3_view"
                                            })
        dict_data = dict_data.drop_duplicates()
        dict_data['сцепка'] = dict_data['fields.level1'] + dict_data['fields.level2'] + dict_data['fields.level3'] + dict_data['Группа материалов'] + dict_data['fields.level4']
        cols = list(dict_data.columns)
        cols.insert(0, cols.pop(cols.index('сцепка')))
        dict_data = dict_data.reindex(columns=cols)

        print(dict_data)

        # # Объединение данных
        result_df = self.merge_columns_from_dict(dict_data, dict_old)
        result_df.to_excel(self.outpath + 'dict_5ka_updated.xlsx', index=False)

        task_all =  result_df[['Группировка', 'Задание', 'Описание']].drop_duplicates() 
        task_fresh = result_df[result_df['fields.level1'] == 'FRESH'][['Группировка', 'Задание', 'Описание']].drop_duplicates()
        task_food_non_food = result_df[result_df['fields.level1'] != 'FRESH'][['Группировка', 'Задание', 'Описание']].drop_duplicates()
        task_food_fresh = result_df[result_df['fields.level1'] != 'NON_FOOD'][['Группировка', 'Задание', 'Описание']].drop_duplicates()

        # Выгрузка заданий для рабочего дока
        task_all.to_excel(self.outpath + 'task_all.xlsx', index=False)
        task_fresh.to_excel(self.outpath + 'task_fresh.xlsx', index=False)
        task_food_non_food.to_excel(self.outpath + 'task_food_non_food.xlsx', index=False)
        task_food_fresh.to_excel(self.outpath + 'task_food_fresh.xlsx', index=False)

        # Выгрузка словаря 105
        dict_105 = result_df[['fields.level1', 'fields.level2', 'fields.level3', 'Название 3-го уровня иерархии (расшифровка)', 'fields.level4', 'Название группы материалов (расшифровка)', 'Задание']].drop_duplicates()
        dict_105 = dict_105.rename(columns={"Задание": "task_title",
                                            "Название 3-го уровня иерархии (расшифровка)":"level3_view",
                                            "Название группы материалов (расшифровка)": "fields.level4_view"
                                            })
        dict_105.to_csv(self.outpath + 'dict_105.csv', index=False)

        # Выгрузка словаря 106
        dict_106 = result_df[['fields.level4', 'keys']].drop_duplicates()
        dict_106 = dict_106.rename(columns={"fields.level4": "column1",
                                            "keys": "column2"})
        dict_106.to_csv(self.outpath + 'dict_106.csv', index=False)

        # Выгрузка файлов в заявку
        levels_dict = df[['Новый фин.код', 'Группа материалов', 'Название группы материалов']].drop_duplicates()
        levels_dict = levels_dict.rename(columns={"Новый фин.код": "scd_fin_code",
                                            "Группа материалов": "scd_material",
                                            "Название группы материалов": "scd_level4"})
        levels_dict.to_csv(self.outpath + 'levels_dict.csv', index=False)

        facets = result_df[['fields.level4', 'keys']].drop_duplicates()
        facets.insert(len(facets.columns)-1, 'geo_object.title', '')
        facets.info()
        facets.to_csv(self.outpath + 'facets.csv', index=False)

        # Выгрузка файла матрицы
        matrix = df
        matrix = matrix.rename(columns={"Номер материала": "code",
                                "Название материала": "title",
                                "Базисная ЕИ": "fields.unit",
                                "Код EAN/UPC": "barcode",
                                "Новый фин.код": "fields.fin_code",
                                "Название 1-го уровня иерархии": "fields.level1",
                                "Название 2-го уровня иерархии": "fields.level2",
                                "Название 3-го уровня иерархии": "fields.level3",
                                "Группа материалов": "fields.level4_code",
                                "Название группы материалов": "fields.level4",
                                "LEVEL5": "fields.level5",
                                "LEVEL6": "fields.level6",
                                "Название бренда": "brand",
                                "Норм.Ед.Потребления": "fields.segment",
                                "Вес": "fields.weight"})


        # Создание пустого столбца ma_title перед столбцом fields.weight
        matrix.insert(len(matrix.columns)-1, 'ma_title', '')
        matrix['fields.weight'] = matrix['fields.weight'] * 1000
        matrix = matrix.drop_duplicates()

        matrix.to_csv(self.outpath + 'matrix_5ka.csv', index=False)

