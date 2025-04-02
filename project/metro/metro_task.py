import pandas as pd
import gspread
import datetime
import glob
import os
from datetime import timedelta
from datetime import datetime
import locale
# Добавить замену года на лист календаря
# заменить номер недели на ввод с приложения

class Metro_task():

    def __init__(self):
        pass

    def open_forming_metro(self):
        gc = gspread.oauth()
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1LOU86hUB7ug-y2SKX8eTuXlGuPYy89SMH6ogHFgDFeA/edit?gid=1031776011#gid=1031776011')
        current_year = datetime.today().year
        sh = gr.worksheet(f"График М54 {current_year}")
        data = sh.get_all_values()
        headers = data.pop(0)
        return pd.DataFrame(data, columns=headers)
    
    def wave(self, graphic_wave, excel, info):

        date = pd.to_datetime(info['Дата окончания сбора'], format="%d.%m.%Y")
        start =  pd.to_datetime(info['Дата начала сбора'], format="%d.%m.%Y")
        # Добавляем 1 день
        new_date = date + pd.Timedelta(days=1)

        # Преобразуем в строку с нужным форматом
        formatted_date = new_date.strftime("%d.%m.%Y")
        start_date = start.strftime("%d.%m")
        excel['task_start_date'] = info['Дата начала сбора']
        excel['task_stop_date'] = formatted_date

        replace_dict = {
            'oif': ['',f'М54: Мониторинг овощей и фруктов ({start_date}) Выгрузка не позднее 12:00 по местному времени'],
            'reg': ['', f'М54: Основной мониторинг. Сбор {start_date}. Выгрузка не позднее 12:00 по местному времени'],
            'siberia': ['', f'М54: Мониторинг овощей и фруктов ({start_date}) Выгрузка не позднее 12:00 по местному времени'],
            'chicken': ['', f'М54: Дополнительный мониторинг. Курица. Сбор {start_date}. Выгрузка не позднее 12:00 по местному времени']
        }
        for key, value in replace_dict.items():
            found_items = [item for item in graphic_wave if key in item]
            replace_dict[key][0] = found_items[0]
        replace_dict['m54_zs_Regular'] = replace_dict.pop('reg')

        for key, value in replace_dict.items():
            excel.loc[excel['wave'].str.contains(key, na=False), 'wave'] = value[0]

        replace_dict['reg'] = replace_dict.pop('m54_zs_Regular')
        for key, value in replace_dict.items():
            excel.loc[excel['wave'].str.contains(key,case=False, na=False), 'subgroup1'] = value[1]
        return excel

    def task_processing(self, year, week):
        self.dir_path = r'C:/Project/Metro/task/'
        base_dir = r"C:/Project/Metro/outh/"  # Базовая директория
        outh_base = os.path.join(base_dir, str(year), str(week))
        self.create_folder_week(base_dir, str(year), str(week))
        graphic = self.open_forming_metro()
        graphic = graphic[(graphic["Неделя"]==str(week)) & (graphic['Волна'].str.contains('m54_zs_', na=False))]
        wave_array = graphic['Волна'].values  # NumPy массив

        task_reg = pd.read_excel(self.dir_path + 'task_metro.xlsx')
        task_chiken = pd.read_excel(self.dir_path + 'task_chiken.xlsx')
        task = pd.concat([task_reg, task_chiken], ignore_index=True)

        task = self.wave(wave_array, task, graphic.iloc[1])

        task['monitoring_type'] = 'old'

        task.to_excel(f'{outh_base}/task.xlsx', index =False)

        # 🔹 Разбиваем строку на список и считаем количество значений
        task['article_count'] = task['active_article_ids'].str.split(',').apply(len)

        # 🔹 Группируем по geo_object_id и суммируем количество статей
        result_geo = task.groupby('geo_object_id')['article_count'].sum().reset_index()
        result_geo.to_excel(f'{outh_base}/result_geo.xlsx', index =False)
        result_wave = task.groupby('wave')['article_count'].sum().reset_index()
        # # Выводим результат
        # print(result_geo)
        mess = result_wave.apply(lambda x: f"{x['wave']} - {x['article_count']}", axis=1)
        self.open_statistic_metro(result_geo, graphic.iloc[1],outh_base)
        return mess

    def create_folder_week(self, get_base_dir, year, week):
 
        outh_base = os.path.join(get_base_dir, str(year), str(week))

        folders = [
            outh_base
        ]

        # Создание папок
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                print(f"Создана папка: {folder}")
            else:
                print(f"Папка '{folder}' уже существует.")  

    
    def open_statistic_metro(self, result_geo, info, path):
        date = pd.to_datetime(info['Дата начала сбора'], format="%d.%m.%Y")

# Форматируем дату в нужном виде
        formatted_date = date.strftime("%#d.%m")  
        # Получаем название месяца с заглавной буквы
        locale.setlocale(locale.LC_TIME, 'Russian') # Устанавливаем русскую локаль
        month_name_russian = date.strftime("%B").lower()
        gc = gspread.oauth()
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1wBvrUs5qgrTrq2kNLOSxsrYLN7czbg3IrO0dBwBwIWY/edit?gid=0#gid=0')
        sh = gr.worksheet(f"АП {month_name_russian}")
        data = sh.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)  # Пропускаем заголовки
        df.to_excel(f'{path}/M54_pole.xlsx', index =False)
        df['ID точки'] = df['ID точки'].astype(str)
        result_geo['geo_object_id'] = result_geo['geo_object_id'].astype(str)
        df = pd.merge(df, result_geo, left_on='ID точки', right_on='geo_object_id', how='left')
        df[f'СКУ\n{formatted_date}'] = df['article_count']
        df = df.drop(['article_count'], axis = 1)
        df = df.drop(['geo_object_id'], axis = 1)
        # Заполняем пустые значения в столбце'
        sh.update([df.columns.values.tolist()] + df.values.tolist())
        
 
