import pandas as pd
import gspread
import datetime
import glob
import os
from datetime import timedelta
from datetime import datetime
import locale
import psycopg2


class Metro_fild():
    def __init__(self):
        pass

    def connect(self, conn, get_wave_array):
            df = pd.DataFrame() 
            for x in get_wave_array:
                sql = f"""select t.id, t.geo_object_id from ma_metro.tasks t
                    where t.wave in ({f"'{x}'"})
                    and t.project_id = 1"""
                
                raw_data = pd.read_sql_query(sql, conn)
                df = pd.concat([df, raw_data]) 
            return df

    def connect_base(self, get_wave_array): 
        # try:
            conn = psycopg2.connect(dbname='pm', user='psqlreader',
                                password='aImf3fivls34', host='localhost', port=8089)
            print('\nСоединение установлено')
          
            return self.connect(conn, get_wave_array)
        # except:
        #     print('\nСоединение недоступно. Проверьте туннель к серверу')

    def open_forming_metro(self):
        gc = gspread.oauth()
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1LOU86hUB7ug-y2SKX8eTuXlGuPYy89SMH6ogHFgDFeA/edit?gid=1031776011#gid=1031776011')
        current_year = datetime.today().year
        sh = gr.worksheet(f"График М54 {current_year}")
        data = sh.get_all_values()
        headers = data.pop(0)
        return pd.DataFrame(data, columns=headers)

    def open_statistic_metro(self, info):
         
        date = pd.to_datetime(info.iloc[1]['Дата начала сбора'], format="%d.%m.%Y")

# Форматируем дату в нужном виде
        locale.setlocale(locale.LC_TIME, 'Russian') # Устанавливаем русскую локаль
        month_name_russian = date.strftime("%B").lower()
        
        gc = gspread.oauth()
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1wBvrUs5qgrTrq2kNLOSxsrYLN7czbg3IrO0dBwBwIWY/edit?gid=0#gid=0')
        sh = gr.worksheet(f"АП поля {month_name_russian}")
        data = sh.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        return df


    def open_fild_metro(self, year, week):       
        graphic = self.open_forming_metro()
        graphic = graphic[(graphic["Неделя"]==str(week)) & (graphic['Волна'].str.contains('m54_zs_', na=False))]
        wave_array = graphic['Волна'].values  # NumPy массив
        wave_array = wave_array[1:]
        raw_data = self.connect_base(wave_array) # данные по ид тасков для филдов

        statistic = self.open_statistic_metro(graphic)
        raw_data['geo_object_id'] = raw_data['geo_object_id'].astype(str)
        statistic['ID точки'] = statistic['ID точки'].astype(str)
        result = pd.merge(raw_data, statistic, left_on='geo_object_id', right_on='ID точки', how='outer') 
        result = result.rename(columns={
            'Филд': 'custom_fields.manager'
        })

        base_dir = r"C:/Project/Metro/outh/"  # Базовая директория
        outh_base = os.path.join(base_dir, str(year), str(week))
        result[['id', 'custom_fields.manager']].to_excel(f'{outh_base}/custom_fields.xlsx', index =False)
        return 'Файл с филдом сформирован', f'{outh_base}/custom_fields.xlsx'

