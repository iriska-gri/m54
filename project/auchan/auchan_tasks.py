import pandas as pd
import gspread
import datetime
import glob
import os
from datetime import timedelta
# from datetime import timedelta

class Tasks():

    def __init__(self):
        pass

    def open_forming_auchan(self):
        gc = gspread.oauth()
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1QXFnls8bVv3HElpnRMe_ZGJ6r7XBMaWTai6iihxTwto/edit?pli=1&gid=368938107#gid=368938107')
        sh = gr.worksheet("График")
        data = sh.get_all_values()
        headers = data.pop(0)
        return pd.DataFrame(data, columns=headers)

    def filter_for_wave(self, id_tt, input_text_wave, radio):
    # def filter_for_wave(self, input_text_wave):
        if os.path.exists(f'C:/Project/Auchan/for_import/task_{input_text_wave}.xlsx'):
            os.remove(f'C:/Project/Auchan/for_import/task_{input_text_wave}.xlsx')
        data = [int(x) for x in id_tt.split()]
        df_data = pd.DataFrame(data, columns=["geo_object_id"])
        df = self.open_forming_auchan()
        df = df[df["Волна"]==input_text_wave]
        first = df.iloc[0]
       
        # print(df['Дата начала сбора'].iloc[0])
        # df.to_excel(f'C:/Project/Auchan/for_import/task.xlsx', index =False)
        file = pd.read_excel(glob.glob('C:/Project/Auchan/task/*')[0], sheet_name = 'Tasks', header = 0)
        df_data['key1'] = 0
        file['key1'] = 0
        dffile = df_data.merge(file, on='key1', how='left')
        dffile['monitoring_type'] = 'old'
        
        dffile['task_start_date'] = df['Дата начала сбора'].iloc[0]
        dffile['task_stop_date'] = (pd.to_datetime(df['Дата окончания сбора'], format='%d.%m.%Y') + timedelta(days=1)).iloc[0]
        dffile['task_stop_date'] =  dffile['task_stop_date'].apply(lambda x:  datetime.datetime.strftime(x,'%d.%m.%Y'))
        dffile['wave'] = input_text_wave

        # Преобразование строки в datetime
        df['Дата начала сбора'] = pd.to_datetime(df['Дата начала сбора'], format='%d.%m.%Y')
        first['Дата начала сбора'] = pd.to_datetime(first['Дата начала сбора'], format='%d.%m.%Y')
        first['Дата окончания сбора'] = pd.to_datetime(first['Дата окончания сбора'], format='%d.%m.%Y')
        
        if radio == 'FROV':
            dffile['subgroup1'] = f"KVI. ЗС УТРО, выгрузка отчетов строго до 12:30 ({ df['Дата начала сбора'].iloc[0].strftime('%d.%m')})"
        if radio == 'samdesch':
            dffile['subgroup1'] = f"А21: ЗС СамДеш. Сбор ({first['Дата начала сбора'].strftime('%d.%m')} - {first['Дата окончания сбора'].strftime('%d.%m')})"
        dffile = dffile.rename(columns={'geo_object_id_x': 'geo_object_id'})
        dffile = dffile[['project_id',
                        'title',
                        'description',
                        'category',
                        'type',	
                        'geo_object_id',
                        'user_ids',
                        'wave',
                        'subgroup1',
                        'subgroup2',
                        'subgroup3',
                        'monitoring_type',
                        'active_article_ids',
                        'company_id',
                        'search_by_price',
                        'important_article_ids',
                        'level',
                        'min',
                        'pretender',
                        'pretender_min',
                        'task_start_date',
                        'task_stop_date'
                        ]].drop_duplicates()
        dffile.to_excel(f'C:/Project/Auchan/for_import/task_{input_text_wave}.xlsx', index =False)
        print('Задания сформированы')
        
        # print(dffile)

    def filter_for_week(self, week):
        df = self.open_forming_auchan()
        current_date = datetime.date.today()
# Получаем номер недели
        week_number = current_date.isocalendar()[1]+1
        if week:
            df = df[df["Нед"]==str(week)]
        else:
            df = df[df["Нед"]==str(week_number)]
        df = df[['Волна', 'Наименование мониторинга']]
        return df.values.tolist()