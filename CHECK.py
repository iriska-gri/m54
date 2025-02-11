import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import psycopg2

#ЗАПРОС ДЛ4Я МЕТРО
def check_Metro():
    print ('Введите номер недели')
    week=input()
    scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
    ]
    # credentials = Credentials.from_service_account_file(
    #         'C:/vitg-306909-31021d096578.json',
    #         scopes=scopes)
    gc = gspread.oauth()
    Check_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1bVX088YYqKJ73aF8pyroiDC9PaFFvrX8mJQmrqzQmYg/edit#gid=567406995')
    gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1LOU86hUB7ug-y2SKX8eTuXlGuPYy89SMH6ogHFgDFeA/edit?pli=1#gid=2094227955')
    
    sh = gr.worksheet("График М54 2025")
    check_sh = Check_sheet.worksheet("Метро")

    # создаем датафрейм из графика
    data = sh.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    final_df = df.loc[lambda df: df.Неделя == week, :][["Неделя","Волна","Объем","ID проекта","Дата начала сбора","Дата окончания сбора"]]
    final_df["Неделя"] = pd.to_numeric(final_df["Неделя"])
    final_df["Объем"] = pd.to_numeric(final_df["Объем"])
    final_df["ID проекта"] = pd.to_numeric(final_df["ID проекта"])
    #final_df["Дата начала сбора"] = pd.to_datetime(final_df["Дата начала сбора"]) №# таблички гугла ругаются, надо смотреть
    #print(final_df)

    # создаем список волн из графика по указанному номеру недели
    waves_to_check = final_df.loc[lambda df: df.Неделя == int(week), :]["Волна"].values.tolist() 

    # формируем список волн для запроса
    rqst =[]
    rqst=str(waves_to_check).replace('"', '').replace(']', '').replace('[', '')
    if len(rqst)==0:
        print('\nВ графике нет сборов для недели ' + week)
        menu()
    print('\nСобираю данные по волнам :\n ')
    print('\n'.join([str(item) for item in waves_to_check]))

    #Запрос на количество скю в волнах из списка по 1 анкете
    sql = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем1" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на количество скю в волнах из списка по 2 анкете
    sql1 = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем2" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на блюпринт
    sql2 = f"""select t.title as "Волна", 
    t.blueprint_id as "Блюпринт" 
    from ma_metro.waves t where t.title in ({rqst})"""

    #Запрос на наличие заявки
    sql3 = f"""select t.title as "Волна",
    t.id as "Заявка"
    FROM ma_metro.clientreqs t where t.title in ({rqst})"""

    #Запрос на даты начала и конца сбора
    sql5 = f"""select distinct t.wave as "Волна",
    t.start_date as "Начало сбора",
    t.stop_date as "Конец сбора"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1"""

    #Запрос на количество заданий в волнах из списка по 1 анкете
    sql6 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""

    #Запрос на количество заданий в волнах из списка по 2 анкете
    sql7 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%'"""

    sql8 = f"""select distinct t.wave as "Волна", case when t.custom_fields ->> 'manager' is not null then 'Проставлен' else 'Пусто' end as "Филд"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""  
    
    # Импортируем raw data
    print('Импортируем raw data')

    try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
    except:
        print('\nСоединение недоступно. Проверьте туннель к серверу')
        menu()
    sku_1 = pd.read_sql_query(sql, conn)
    sku_2 = pd.read_sql_query(sql1, conn)
    blueprint = pd.read_sql_query(sql2, conn)
    clientreq = pd.read_sql_query(sql3, conn)
    tasks_1 = pd.read_sql_query(sql6, conn)
    tasks_2 = pd.read_sql_query(sql7, conn)

    value_counts = tasks_1['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts1 = pd.DataFrame(value_counts)
    df_value_counts1 = df_value_counts1.reset_index()
    df_value_counts1.columns = ['Волна', 'Количество 1']

    value_counts = tasks_2['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts2 = pd.DataFrame(value_counts)
    df_value_counts2 = df_value_counts2.reset_index()
    df_value_counts2.columns = ['Волна', 'Количество 2']


    #Тут необходимо дописать проверку на наличие нескольких значений времени, на случай, если в пределах одной волны есть задания с разным временем
    dates = pd.read_sql_query(sql5, conn)
    dates['Начало сбора']=pd.to_datetime(dates["Начало сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    dates['Конец сбора']=pd.to_datetime(dates["Конец сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    
      # список ID заявок для проверки наличия шаблонов
    rqst_1 =[]
    clientreq_values = clientreq['Заявка'].values.tolist()
    #print(clientreq_values)
    rqst_1=str(clientreq_values).replace('"', '').replace(']', '').replace('[', '')

    #Запрос на наличие шаблона в заявке
    sql4 = f"""select t.clientreq_id as "Заявка",
    t.title as "Шаблон"
    FROM ma_metro.clientreq_files t where t.clientreq_id in ({rqst_1}) and t.title like '%metro_anketa%' or t.title like '%metro_a_dict%'
    or t.title like '%tasks%' or t.title like '%addresses%'"""

    try:
        template = pd.read_sql_query(sql4, conn)
    #Объединяем все имена шаблонов в 1 строку
        template = template.groupby('Заявка')['Шаблон'].apply(list).reset_index(name='Шаблон')
        template['Шаблон'] = template['Шаблон'].apply(lambda x: ','.join([str(i) for i in x]))#убираем квадратные скобки из списка шаблонов(не влазят в гуглотаблицы)
    except:
        print('')

    conn.close()
    
    # Добавляем к фрейму данные из запросов
    final_df = final_df.merge(sku_1, how="left")
    final_df = final_df.merge(sku_2, how="left")
    final_df.loc[(final_df.Объем1 == 0), ('Объем1')] = '' # убираем нули из количества скю в волнах
    final_df.loc[(final_df.Объем2 == 0), ('Объем2')] = ''
    final_df = final_df.merge(blueprint, how="left")
    final_df = final_df.merge(clientreq, how="left")
    try:
        final_df = final_df.merge(template, how="left")
    except:
        final_df['Шаблон'] = ''
    final_df = final_df.merge(dates, how="left")
    final_df = final_df.merge(df_value_counts1, how="left")
    final_df = final_df.merge(df_value_counts2, how="left")
    final_df["Заявка"].fillna('0', inplace=True) # меняем наны столбца на нули
    final_df.fillna('', inplace=True) #дропаем Nans
    final_df["Заявка"] = final_df["Заявка"].astype(int)
    final_df.loc[:,'Заявка'] = final_df.Заявка.apply(lambda x: 'https://m54.millionagents.com/clientreqs/' + str(x) + '/show' if x!=0 else None) #добавляем символы для получения ссылки из номера заявки
    #print(final_df["Заявка"])
    
    
    final_df = final_df[['Неделя','Волна','Объем','Объем1','Объем2','Количество 1','Количество 2','ID проекта','Блюпринт','Заявка','Шаблон','Дата начала сбора','Начало сбора','Дата окончания сбора','Конец сбора']] #устанавливаем порядок столбцов

    Check_sheet.values_clear("Метро!A2:O100") # Удаляем все записи в диапазоне а1 o100
    check_sh.update('A2',final_df.values.tolist()) # переносим данные в отчет
    print('Данные по сборам "Метро" созданы')

#ЗАПРОС ДЛЯ АШАНА
def check_Aushan():
    print ('Введите номер недели')
    week=input()
    scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
    ]
    # credentials = Credentials.from_service_account_file(
    #         'C:/vitg-306909-31021d096578.json',
    #         scopes=scopes)
    gc = gspread.oauth()
    Check_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1bVX088YYqKJ73aF8pyroiDC9PaFFvrX8mJQmrqzQmYg/edit#gid=567406995')
    gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1QXFnls8bVv3HElpnRMe_ZGJ6r7XBMaWTai6iihxTwto/edit#gid=368938107')
    
    sh = gr.worksheet("График")
    check_sh = Check_sheet.worksheet("Ашан")

    # создаем датафрейм из графика
    data = sh.get_all_values()
    print(data, ' -----------')
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    final_df = df.loc[lambda df: df.Нед == week, :][["Год","Нед","Волна","К поиску","Проект","Дата начала сбора","Дата окончания сбора"]]
    final_df = final_df.loc[final_df['Год'] == '2025']
    final_df.rename(columns = {'Нед':'Неделя', 'К поиску':'Объем','Проект':'ID проекта'}, inplace = True)
    final_df["Неделя"] = pd.to_numeric(final_df["Неделя"])
    final_df["Объем"] = pd.to_numeric(final_df["Объем"])
    final_df["ID проекта"] = pd.to_numeric(final_df["ID проекта"])

    # создаем список волн из графика по указанному номеру недели
    waves_to_check = final_df.loc[lambda df: df.Неделя == int(week), :]["Волна"].values.tolist() 

    # формируем список волн для запроса
    rqst =[]
    rqst=str(waves_to_check).replace('"', '').replace(']', '').replace('[', '')
    if len(rqst)==0:
        print('\nВ графике нет сборов для недели ' + week)
        menu()
    print('\nСобираю данные по волнам :\n ')
    print('\n'.join([str(item) for item in waves_to_check]))

    #Запрос на количество скю в волнах из списка по 1 анкете
    sql = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем1" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на количество скю в волнах из списка по 2 анкете
    sql1 = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем2" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на блюпринт
    sql2 = f"""select t.title as "Волна", 
    t.blueprint_id as "Блюпринт" 
    from ma_metro.waves t where t.title in ({rqst})"""

    #Запрос на наличие заявки
    sql3 = f"""select t.title as "Волна",
    t.id as "Заявка"
    FROM ma_metro.clientreqs t where t.title in ({rqst})"""

    #Запрос на даты начала и конца сбора
    sql5 = f"""select distinct t.wave as "Волна",
    t.start_date as "Начало сбора",
    t.stop_date as "Конец сбора"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1"""

    #Запрос на количество заданий в волнах из списка по 1 анкете
    sql6 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""

    #Запрос на количество заданий в волнах из списка по 2 анкете
    sql7 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%'"""

    # #Запрос на простановку филда в волнах из списка по 1 анкете
    sql8 = f"""select distinct t.wave as "Волна", case when t.custom_fields ->> 'manager' is not null then 'Проставлен' else 'Пусто' end as "Филд"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""    
    
    # Импортируем raw data
    print('Импортируем raw data')
    try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
    except:
        print('\nСоединение недоступно. Проверьте туннель к серверу')
        menu()
    sku_1 = pd.read_sql_query(sql, conn)
    sku_2 = pd.read_sql_query(sql1, conn)
    blueprint = pd.read_sql_query(sql2, conn)
    clientreq = pd.read_sql_query(sql3, conn)
    tasks_1 = pd.read_sql_query(sql6, conn)
    tasks_2 = pd.read_sql_query(sql7, conn)
    fild = pd.read_sql_query(sql8, conn)

    value_counts = tasks_1['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts1 = pd.DataFrame(value_counts)
    df_value_counts1 = df_value_counts1.reset_index()
    df_value_counts1.columns = ['Волна', 'Количество 1']

    value_counts = tasks_2['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts2 = pd.DataFrame(value_counts)
    df_value_counts2 = df_value_counts2.reset_index()
    df_value_counts2.columns = ['Волна', 'Количество 2']

    #Тут необходимо дописать проверку на наличие нескольких значений времени, на случай, если в пределах одной волны есть задания с разным временем
    dates = pd.read_sql_query(sql5, conn)
    dates['Начало сбора']=pd.to_datetime(dates["Начало сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    dates['Конец сбора']=pd.to_datetime(dates["Конец сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    
      # список ID заявок для проверки наличия шаблонов
    rqst_1 =[]
    clientreq_values = clientreq['Заявка'].values.tolist()
    #print(clientreq_values)
    rqst_1=str(clientreq_values).replace('"', '').replace(']', '').replace('[', '')

    #Запрос на наличие шаблона в заявке
    sql4 = f"""select t.clientreq_id as "Заявка",
    t.title as "Шаблон"
    FROM ma_metro.clientreq_files t where t.clientreq_id in ({rqst_1}) and t.title like '%anketa%' or t.title like '%ap%'"""

    try:
        template = pd.read_sql_query(sql4, conn)
    #Объединяем все имена шаблонов в 1 строку
        template = template.groupby('Заявка')['Шаблон'].apply(list).reset_index(name='Шаблон')
        template['Шаблон'] = template['Шаблон'].apply(lambda x: ','.join([str(i) for i in x]))#убираем квадратные скобки из списка шаблонов(не влазят в гуглотаблицы)
    except:
        print('')

    conn.close()
    
    # Добавляем к фрейму данные из запросов
    final_df = final_df.merge(sku_1, how="left")
    final_df = final_df.merge(sku_2, how="left")
    final_df.loc[(final_df.Объем1 == 0), ('Объем1')] = ''
    final_df.loc[(final_df.Объем2 == 0), ('Объем2')] = ''
    final_df = final_df.merge(blueprint, how="left")
    final_df = final_df.merge(clientreq, how="left")
    final_df = final_df.merge(fild, how="left")
    final_df.to_excel(f'C:/Project/Auchan/ss.xlsx', index =False)
    try:
        final_df = final_df.merge(template, how="left")
    except:
        final_df['Шаблон'] = ''
    final_df = final_df.merge(dates, how="left")
    final_df = final_df.merge(df_value_counts1, how="left")
    final_df = final_df.merge(df_value_counts2, how="left")
    final_df["Заявка"].fillna('0', inplace=True) # меняем наны столбца на нули
    final_df.fillna('', inplace=True) #дропаем Nans
    final_df["Заявка"] = final_df["Заявка"].astype(int)
    final_df.loc[:,'Заявка'] = final_df.Заявка.apply(lambda x: 'https://m54.millionagents.com/clientreqs/' + str(x) + '/show' if x!=0 else None) #добавляем символы для получения ссылки из номера заявки
    final_df = final_df[['Неделя','Волна','Объем','Объем1','Объем2','Количество 1','Количество 2','ID проекта','Блюпринт','Заявка','Шаблон','Дата начала сбора','Начало сбора','Дата окончания сбора','Конец сбора', 'Филд']] #устанавливаем порядок столбцов
    
    Check_sheet.values_clear("Ашан!A2:P100") # Удаляем все записи в диапазоне а1 o100
    check_sh.update('A2',final_df.values.tolist()) # переносим данные в отчет
    print('Данные по сборам "Ашан" созданы')

#ЗАПРОС ДЛЯ КАРУСЕЛИ
def check_Karousel():
    print ('Введите номер недели')
    week=input()
    scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
    ]
    # credentials = Credentials.from_service_account_file(
    #         'C:/vitg-306909-31021d096578.json',
    #         scopes=scopes)
    gc = gspread.oauth()
    Check_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1bVX088YYqKJ73aF8pyroiDC9PaFFvrX8mJQmrqzQmYg/edit#gid=567406995')
    gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/17seiwhcujpIPW1NuerpqCkz1HmcsH7vH4p2VsvnHB5M/edit#gid=1451963061')
    
    sh = gr.worksheet("График 2021")
    check_sh = Check_sheet.worksheet("Карусель")

    # создаем датафрейм из графика
    data = sh.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    final_df = df.loc[lambda df: df.Неделя == week, :][["Неделя","Волна","К сбору","ID проекта","Дата начала сбора","Дата окончания сбора"]]
    final_df.rename(columns = {'К сбору':'Объем'}, inplace = True)
    final_df["Неделя"] = pd.to_numeric(final_df["Неделя"])
    final_df["Объем"] = pd.to_numeric(final_df["Объем"])
    final_df["ID проекта"] = pd.to_numeric(final_df["ID проекта"])

    # создаем список волн из графика по указанному номеру недели
    waves_to_check = final_df.loc[lambda df: df.Неделя == int(week), :]["Волна"].values.tolist()  

    # формируем список волн для запроса
    rqst =[]
    rqst=str(waves_to_check).replace('"', '').replace(']', '').replace('[', '')
    if len(rqst)==0:
        print('\nВ графике нет сборов для недели ' + week)
        menu()
    print('\nСобираю данные по волнам :\n ')
    print('\n'.join([str(item) for item in waves_to_check]))

    #Запрос на количество скю в волнах из списка по 1 анкете
    sql = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем1" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на количество скю в волнах из списка по 2 анкете
    sql1 = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем2" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на блюпринт
    sql2 = f"""select t.title as "Волна", 
    t.blueprint_id as "Блюпринт" 
    from ma_metro.waves t where t.title in ({rqst})"""

    #Запрос на наличие заявки
    sql3 = f"""select t.title as "Волна",
    t.id as "Заявка"
    FROM ma_metro.clientreqs t where t.title in ({rqst})"""

    #Запрос на даты начала и конца сбора
    sql5 = f"""select distinct t.wave as "Волна",
    t.start_date as "Начало сбора",
    t.stop_date as "Конец сбора"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1"""

    #Запрос на количество заданий в волнах из списка по 1 анкете
    sql6 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""

    #Запрос на количество заданий в волнах из списка по 2 анкете
    sql7 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%'"""
    
    
    # Импортируем raw data
    print('Импортируем raw data')
    try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
    except:
        print('\nСоединение недоступно. Проверьте туннель к серверу')
        menu()
    sku_1 = pd.read_sql_query(sql, conn)
    sku_2 = pd.read_sql_query(sql1, conn)
    try:
        blueprint = pd.read_sql_query(sql2, conn)
    except:
        final_df['Блюпринт'] = ''
    clientreq = pd.read_sql_query(sql3, conn)
    tasks_1 = pd.read_sql_query(sql6, conn)
    tasks_2 = pd.read_sql_query(sql7, conn)

    value_counts = tasks_1['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts1 = pd.DataFrame(value_counts)
    df_value_counts1 = df_value_counts1.reset_index()
    df_value_counts1.columns = ['Волна', 'Количество 1']

    value_counts = tasks_2['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts2 = pd.DataFrame(value_counts)
    df_value_counts2 = df_value_counts2.reset_index()
    df_value_counts2.columns = ['Волна', 'Количество 2']

    #Тут необходимо дописать проверку на наличие нескольких значений времени, на случай, если в пределах одной волны есть задания с разным временем
    dates = pd.read_sql_query(sql5, conn)
    dates['Начало сбора']=pd.to_datetime(dates["Начало сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    dates['Конец сбора']=pd.to_datetime(dates["Конец сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    
      # список ID заявок для проверки наличия шаблонов
    rqst_1 =[]
    clientreq_values = clientreq['Заявка'].values.tolist()
    #print(clientreq_values)
    rqst_1=str(clientreq_values).replace('"', '').replace(']', '').replace('[', '')

    #Запрос на наличие шаблона в заявке
    sql4 = f"""select t.clientreq_id as "Заявка",
    t.title as "Шаблон"
    FROM ma_metro.clientreq_files t where t.clientreq_id in ({rqst_1}) and t.title like '%addresses%' or t.title like '%karusel_articles_tz%'"""

    try:
        template = pd.read_sql_query(sql4, conn)
    #Объединяем все имена шаблонов в 1 строку
        template = template.groupby('Заявка')['Шаблон'].apply(list).reset_index(name='Шаблон')
        template['Шаблон'] = template['Шаблон'].apply(lambda x: ','.join([str(i) for i in x]))#убираем квадратные скобки из списка шаблонов(не влазят в гуглотаблицы)
    except:
        print('')

    conn.close()
    
    # Добавляем к фрейму данные из запросов
    final_df = final_df.merge(sku_1, how="left")
    final_df = final_df.merge(sku_2, how="left")
    final_df.loc[(final_df.Объем1 == 0), ('Объем1')] = ''
    final_df.loc[(final_df.Объем2 == 0), ('Объем2')] = ''
    final_df = final_df.merge(blueprint, how="left")
    final_df = final_df.merge(clientreq, how="left")
    try:
        final_df = final_df.merge(template, how="left")
    except:
        final_df['Шаблон'] = ''
    final_df = final_df.merge(dates, how="left")
    final_df = final_df.merge(df_value_counts1, how="left")
    final_df = final_df.merge(df_value_counts2, how="left")
    final_df["Заявка"].fillna('0', inplace=True) # меняем наны столбца на нули
    final_df.fillna('', inplace=True) #дропаем Nans
    final_df["Заявка"] = final_df["Заявка"].astype(int)
    final_df.loc[:,'Заявка'] = final_df.Заявка.apply(lambda x: 'https://m54.millionagents.com/clientreqs/' + str(x) + '/show' if x!=0 else None) #добавляем символы для получения ссылки из номера заявки
    final_df = final_df[['Неделя','Волна','Объем','Объем1','Объем2','Количество 1','Количество 2','ID проекта','Блюпринт','Заявка','Шаблон','Дата начала сбора','Начало сбора','Дата окончания сбора','Конец сбора']] #устанавливаем порядок столбцов
    Check_sheet.values_clear("Карусель!A2:O100") # Удаляем все записи в диапазоне а1 o100
    check_sh.update('A2',final_df.values.tolist()) # переносим данные в отчет
    print('Данные по сборам "Карусель" созданы')

#ЗАПРОС ДЛЯ МАГНИТА
def check_Magnit():
    print ('Введите номер недели')
    week=input()
    scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
    ]
    # credentials = Credentials.from_service_account_file(
    #         'C:/vitg-306909-31021d096578.json',
    #         scopes=scopes)
    gc = gspread.oauth()
    Check_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1bVX088YYqKJ73aF8pyroiDC9PaFFvrX8mJQmrqzQmYg/edit#gid=567406995')
    gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1b8qWS0IUElJv2v3N2-X6t3WYdG2EgwL_omeWHVY0vvA/edit#gid=0')
    
    sh = gr.worksheet("График 2025")
    check_sh = Check_sheet.worksheet("Магнит")
    
    # создаем датафрейм из графика
    data = sh.get_all_values()
   
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    
    df.rename(columns = {'Нед':'Неделя'}, inplace = True)
    df.rename(columns = {'Проект':'ID проекта'}, inplace = True)
    final_df = df.loc[lambda df: df.Неделя == week, :][["Неделя","Волна","ID проекта","Дата начала сбора","Дата окончания сбора"]]
    print(final_df)
    final_df["Неделя"] = pd.to_numeric(final_df["Неделя"])
    final_df["ID проекта"] = pd.to_numeric(final_df["ID проекта"])
    
    # создаем список волн из графика по указанному номеру недели
    waves_to_check = final_df.loc[lambda df: df.Неделя == int(week), :]["Волна"].values.tolist()  
    
    # формируем список волн для запроса
    rqst =[]
    rqst=str(waves_to_check).replace('"', '').replace(']', '').replace('[', '')
    if len(rqst)==0:
        print('\nВ графике нет сборов для недели ' + week)
        menu()
    print('\nСобираю данные по волнам :\n ')
    print('\n'.join([str(item) for item in waves_to_check]))

    #Запрос на блюпринт
    sql2 = f"""select t.title as "Волна", 
    t.blueprint_id as "Блюпринт" 
    from ma_metro.waves t where t.title in ({rqst})"""

    #Запрос на наличие заявки
    sql3 = f"""select t.title as "Волна",
    t.id as "Заявка"
    FROM ma_metro.clientreqs t where t.title in ({rqst})"""

    #Запрос на даты начала и конца сбора
    sql5 = f"""select distinct t.wave as "Волна",
    t.start_date as "Начало сбора",
    t.stop_date as "Конец сбора"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1"""

    #Запрос на количество заданий в волнах из списка по 1 анкете
    sql6 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""

    #Запрос на количество заданий в волнах из списка по 2 анкете
    sql7 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%'"""
    
    
    # Импортируем raw data
    print('Импортируем raw data')

    try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
    except:
        print('\nСоединение недоступно. Проверьте туннель к серверу')
        menu()
    try:
        blueprint = pd.read_sql_query(sql2, conn)
    except:
        final_df['Блюпринт'] = ''
    clientreq = pd.read_sql_query(sql3, conn)
    tasks_1 = pd.read_sql_query(sql6, conn)
    tasks_2 = pd.read_sql_query(sql7, conn)

    value_counts = tasks_1['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts1 = pd.DataFrame(value_counts)
    df_value_counts1 = df_value_counts1.reset_index()
    df_value_counts1.columns = ['Волна', 'Количество 1']

    value_counts = tasks_2['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts2 = pd.DataFrame(value_counts)
    df_value_counts2 = df_value_counts2.reset_index()
    df_value_counts2.columns = ['Волна', 'Количество 2']

    #Тут необходимо дописать проверку на наличие нескольких значений времени, на случай, если в пределах одной волны есть задания с разным временем
    dates = pd.read_sql_query(sql5, conn)
    dates['Начало сбора']=pd.to_datetime(dates["Начало сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    dates['Конец сбора']=pd.to_datetime(dates["Конец сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    
      # список ID заявок для проверки наличия шаблонов
    rqst_1 =[]
    clientreq_values = clientreq['Заявка'].values.tolist()
    #print(clientreq_values)
    rqst_1=str(clientreq_values).replace('"', '').replace(']', '').replace('[', '')

    #Запрос на наличие шаблона в заявке
    sql4 = f"""select t.clientreq_id as "Заявка",
    t.title as "Шаблон"
    FROM ma_metro.clientreq_files t where t.clientreq_id in ({rqst_1}) and t.title like '%addresses%' or t.title like '%facets%'"""

    try:
        template = pd.read_sql_query(sql4, conn)
    #Объединяем все имена шаблонов в 1 строку
        template = template.groupby('Заявка')['Шаблон'].apply(list).reset_index(name='Шаблон')
        template['Шаблон'] = template['Шаблон'].apply(lambda x: ','.join([str(i) for i in x]))#убираем квадратные скобки из списка шаблонов(не влазят в гуглотаблицы)
    except:
        print('')

    conn.close()
    
    # Добавляем к фрейму данные из запросов
    final_df = final_df.merge(blueprint, how="left")
    final_df = final_df.merge(clientreq, how="left")
    try:
        final_df = final_df.merge(template, how="left")
    except:
        final_df['Шаблон'] = ''
    final_df = final_df.merge(dates, how="left")
    final_df = final_df.merge(df_value_counts1, how="left")
    final_df = final_df.merge(df_value_counts2, how="left")
    final_df["Заявка"].fillna('0', inplace=True) # меняем наны столбца на нули
    final_df.fillna('', inplace=True) #дропаем Nans
    final_df["Заявка"] = final_df["Заявка"].astype(int)
    final_df.loc[:,'Заявка'] = final_df.Заявка.apply(lambda x: 'https://m54.millionagents.com/clientreqs/' + str(x) + '/show' if x!=0 else None) #добавляем символы для получения ссылки из номера заявки
    final_df = final_df[['Неделя','Волна','Количество 1','Количество 2','ID проекта','Блюпринт','Заявка','Шаблон','Дата начала сбора','Начало сбора','Дата окончания сбора','Конец сбора']] #устанавливаем порядок столбцов
    Check_sheet.values_clear("Магнит!A2:O100") # Удаляем все записи в диапазоне а1 o100
    check_sh.update('A2',final_df.values.tolist()) # переносим данные в отчет
    print('Данные по сборам "Магнит" созданы')

#ЗАПРОС ДЛЯ ОКЕЯ
def check_Okey():
    print ('Введите номер недели')
    week=input()
    scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
    ]
    # credentials = Credentials.from_service_account_file(
    #         'C:/vitg-306909-31021d096578.json',
    #         scopes=scopes)
    gc = gspread.oauth()
    Check_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1bVX088YYqKJ73aF8pyroiDC9PaFFvrX8mJQmrqzQmYg/edit#gid=567406995')
    gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1N09ANK2wpJtM9g5njpJqjxrVmdvn7dvU7qilqizqtKY/edit#gid=599454814')
    
    sh = gr.worksheet("График 2024")
    check_sh = Check_sheet.worksheet("Окей")

    # создаем датафрейм из графика
    data = sh.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    final_df = df.loc[lambda df: df.Неделя == week, :][["Неделя","Волна","К сбору всего","ИД проекта м54","Начало сбора","Конец сбора"]]
    final_df.rename(columns = {'К сбору всего':'Объем','ИД проекта м54':'ID проекта','Начало сбора':'Дата начала сбора','Конец сбора':'Дата окончания сбора'}, inplace = True)
    final_df["Неделя"] = pd.to_numeric(final_df["Неделя"])
    final_df["Объем"] = pd.to_numeric(final_df["Объем"])
    final_df["ID проекта"] = pd.to_numeric(final_df["ID проекта"])
    sum_df = final_df.groupby('Волна').Объем.sum()
    sum_df = sum_df.reset_index()
    sum_df.columns = ['Волна', 'Объем']
    final_df = final_df.drop(['Объем'], axis = 1)
    final_df = final_df.drop_duplicates()
    final_df = final_df.merge(sum_df, how="left")

    # создаем список волн из графика по указанному номеру недели
    waves_to_check = final_df.loc[lambda df: df.Неделя == int(week), :]["Волна"].values.tolist() 
    waves_to_check = list(set(waves_to_check)) # удаляем дубликаты из списка, преобразуя его в набор и обратно в список

    # формируем список волн для запроса
    rqst =[]
    rqst=str(waves_to_check).replace('"', '').replace(']', '').replace('[', '')
    if len(rqst)==0:
        print('\nВ графике нет сборов для недели ' + week)
        menu()
    print('\nСобираю данные по волнам :\n ')
    print('\n'.join([str(item) for item in waves_to_check]))

    #Запрос на количество скю в волнах из списка по 1 анкете
    sql = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем1" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на количество скю в волнах из списка по 2 анкете
    sql1 = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем2" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на блюпринт
    sql2 = f"""select t.title as "Волна", 
    t.blueprint_id as "Блюпринт" 
    from ma_metro.waves t where t.title in ({rqst})"""

    #Запрос на наличие заявки
    sql3 = f"""select t.title as "Волна",
    t.id as "Заявка"
    FROM ma_metro.clientreqs t where t.title in ({rqst})"""

    #Запрос на даты начала и конца сбора
    sql5 = f"""select distinct t.wave as "Волна",
    t.start_date as "Начало сбора",
    t.stop_date as "Конец сбора"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1"""

    #Запрос на количество заданий в волнах из списка по 1 анкете
    sql6 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""

    #Запрос на количество заданий в волнах из списка по 2 анкете
    sql7 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%'"""
    
    
    # Импортируем raw data
    print('Импортируем raw data')

    try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
    except:
        print('\nСоединение недоступно. Проверьте туннель к серверу')
        menu()
    sku_1 = pd.read_sql_query(sql, conn)
    sku_2 = pd.read_sql_query(sql1, conn)
    blueprint = pd.read_sql_query(sql2, conn)
    clientreq = pd.read_sql_query(sql3, conn)
    tasks_1 = pd.read_sql_query(sql6, conn)
    tasks_2 = pd.read_sql_query(sql7, conn)

    value_counts = tasks_1['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts1 = pd.DataFrame(value_counts)
    df_value_counts1 = df_value_counts1.reset_index()
    df_value_counts1.columns = ['Волна', 'Количество 1']

    value_counts = tasks_2['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts2 = pd.DataFrame(value_counts)
    df_value_counts2 = df_value_counts2.reset_index()
    df_value_counts2.columns = ['Волна', 'Количество 2']

    #Тут необходимо дописать проверку на наличие нескольких значений времени, на случай, если в пределах одной волны есть задания с разным временем
    dates = pd.read_sql_query(sql5, conn)
    dates['Начало сбора']=pd.to_datetime(dates["Начало сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    dates['Конец сбора']=pd.to_datetime(dates["Конец сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    
      # список ID заявок для проверки наличия шаблонов
    rqst_1 =[]
    clientreq_values = clientreq['Заявка'].values.tolist()
    #print(clientreq_values)
    rqst_1=str(clientreq_values).replace('"', '').replace(']', '').replace('[', '')

    #Запрос на наличие шаблона в заявке
    sql4 = f"""select t.clientreq_id as "Заявка",
    t.title as "Шаблон"
    FROM ma_metro.clientreq_files t where t.clientreq_id in ({rqst_1}) and t.title like '%template%'"""

    try:
        template = pd.read_sql_query(sql4, conn)
    #Объединяем все имена шаблонов в 1 строку
        template = template.groupby('Заявка')['Шаблон'].apply(list).reset_index(name='Шаблон')
        template['Шаблон'] = template['Шаблон'].apply(lambda x: ','.join([str(i) for i in x]))#убираем квадратные скобки из списка шаблонов(не влазят в гуглотаблицы)
    except:
        print('')
    conn.close()
    
    # Добавляем к фрейму данные из запросов
    final_df = final_df.merge(sku_1, how="left")
    final_df = final_df.merge(sku_2, how="left")
    final_df.loc[(final_df.Объем1 == 0), ('Объем1')] = ''
    final_df.loc[(final_df.Объем2 == 0), ('Объем2')] = ''
    final_df = final_df.merge(blueprint, how="left")
    final_df = final_df.merge(clientreq, how="left")
    try:
        final_df = final_df.merge(template, how="left")
    except:
        final_df['Шаблон'] = ''
    final_df = final_df.merge(dates, how="left")
    final_df = final_df.merge(df_value_counts1, how="left")
    final_df = final_df.merge(df_value_counts2, how="left")
    final_df["Заявка"].fillna('0', inplace=True) # меняем наны столбца на нули
    final_df.fillna('', inplace=True) #дропаем Nans
    final_df["Заявка"] = final_df["Заявка"].astype(int)
    final_df.loc[:,'Заявка'] = final_df.Заявка.apply(lambda x: 'https://m54.millionagents.com/clientreqs/' + str(x) + '/show' if x!=0 else None) #добавляем символы для получения ссылки из номера заявки
    final_df = final_df[['Неделя','Волна','Объем','Объем1','Объем2','Количество 1','Количество 2','ID проекта','Блюпринт','Заявка','Шаблон','Дата начала сбора','Начало сбора','Дата окончания сбора','Конец сбора']] #устанавливаем порядок столбцов
    Check_sheet.values_clear("Окей!A2:O100") # Удаляем все записи в диапазоне а1 o100
    check_sh.update('A2',final_df.values.tolist()) # переносим данные в отчет
    print('Данные по сборам "Окей" созданы')

#ЗАПРОС ДЛЯ ЛЕНТЫ
def check_Lenta():
    print ('Введите номер недели')
    week=input()
    scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
    ]
    # credentials = Credentials.from_service_account_file(
    #         'C:/vitg-306909-31021d096578.json',
    #         scopes=scopes)
    gc = gspread.oauth()
    Check_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1bVX088YYqKJ73aF8pyroiDC9PaFFvrX8mJQmrqzQmYg/edit#gid=567406995')
    gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/17jIEecPKu44de5xCgVB6SBgBKPjMlLSRawqSXOy1RiU/edit#gid=1447527042')
    
    sh = gr.worksheet("График 2024")
    check_sh = Check_sheet.worksheet("Лента")

    # создаем датафрейм из графика
    data = sh.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)
    final_df = df.loc[lambda df: df.Неделя == week, :][["Неделя","Волна","К сбору всего","ID проекта","Старт сбора","Конец сбора"]]
    final_df.rename(columns = {'К сбору всего':'Объем','Старт сбора':'Дата начала сбора','Конец сбора':'Дата окончания сбора'}, inplace = True)
    final_df["Неделя"] = pd.to_numeric(final_df["Неделя"])
    final_df["Объем"] = pd.to_numeric(final_df["Объем"])
    final_df["ID проекта"] = pd.to_numeric(final_df["ID проекта"])

    sum_df = final_df.groupby('Волна').Объем.sum()
    sum_df = sum_df.reset_index()
    sum_df.columns = ['Волна', 'Объем']
    final_df = final_df.drop(['Объем'], axis = 1)
    final_df = final_df.drop_duplicates()
    final_df = final_df.merge(sum_df, how="left")

    # создаем список волн из графика по указанному номеру недели
    waves_to_check = final_df.loc[lambda df: df.Неделя == int(week), :]["Волна"].values.tolist() 
    waves_to_check = list(set(waves_to_check)) # удаляем дубликаты из списка, преобразуя его в набор и обратно в список

    # формируем список волн для запроса
    rqst =[]
    rqst=str(waves_to_check).replace('"', '').replace(']', '').replace('[', '')
    if len(rqst)==0:
        print('\nВ графике нет сборов для недели ' + week)
        menu()
    print('\nСобираю данные по волнам :\n')
    print('\n'.join([str(item) for item in waves_to_check]))

    #Запрос на количество скю в волнах из списка по 1 анкете
    sql = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем1" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на количество скю в волнах из списка по 2 анкете
    sql1 = f"""select t.wave as "Волна", 
    sum(jsonb_array_length(to_jsonb(t.active_article_ids))) 
    as "Объем2" 
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%' 
    group by t.wave"""

    #Запрос на блюпринт
    sql2 = f"""select t.title as "Волна", 
    t.blueprint_id as "Блюпринт" 
    from ma_metro.waves t where t.title in ({rqst})"""

    #Запрос на наличие заявки
    sql3 = f"""select t.title as "Волна",
    t.id as "Заявка"
    FROM ma_metro.clientreqs t where t.title in ({rqst})"""

    #Запрос на даты начала и конца сбора
    sql5 = f"""select distinct t.wave as "Волна",
    t.start_date as "Начало сбора",
    t.stop_date as "Конец сбора"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1"""

    #Запрос на количество заданий в волнах из списка по 1 анкете
    sql6 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 1 and t.title not like 'Перепроход:%'"""

    #Запрос на количество заданий в волнах из списка по 2 анкете
    sql7 = f"""select t.wave as "Волна"
    from ma_metro.tasks t where t.wave in ({rqst}) and t.project_id = 2 and t.title not like 'Перепроход:%'"""
    
    
    # Импортируем raw data
    print('Импортируем raw data')

    try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
    except:
        print('\nСоединение недоступно. Проверьте туннель к серверу')
        menu()
    sku_1 = pd.read_sql_query(sql, conn)
    sku_2 = pd.read_sql_query(sql1, conn)
    blueprint = pd.read_sql_query(sql2, conn)
    clientreq = pd.read_sql_query(sql3, conn)
    tasks_1 = pd.read_sql_query(sql6, conn)
    tasks_2 = pd.read_sql_query(sql7, conn)

    value_counts = tasks_1['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts1 = pd.DataFrame(value_counts)
    df_value_counts1 = df_value_counts1.reset_index()
    df_value_counts1.columns = ['Волна', 'Количество 1']

    value_counts = tasks_2['Волна'].value_counts()
    # преобразование в df и присвоение новых имен колонкам
    df_value_counts2 = pd.DataFrame(value_counts)
    df_value_counts2 = df_value_counts2.reset_index()
    df_value_counts2.columns = ['Волна', 'Количество 2']

    #Тут необходимо дописать проверку на наличие нескольких значений времени, на случай, если в пределах одной волны есть задания с разным временем
    dates = pd.read_sql_query(sql5, conn)
    dates['Начало сбора']=pd.to_datetime(dates["Начало сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    dates['Конец сбора']=pd.to_datetime(dates["Конец сбора"],errors='coerce').dt.strftime('%d.%m.%Y %H:%M:%S').replace('NaT','')
    
      # список ID заявок для проверки наличия шаблонов
    rqst_1 =[]
    clientreq_values = clientreq['Заявка'].values.tolist()
    #print(clientreq_values)
    rqst_1=str(clientreq_values).replace('"', '').replace(']', '').replace('[', '')

    #Запрос на наличие шаблона в заявке
    sql4 = f"""select t.clientreq_id as "Заявка",
    t.title as "Шаблон"
    FROM ma_metro.clientreq_files t where t.clientreq_id in ({rqst_1}) and t.title like '%template%'"""

    try:
        template = pd.read_sql_query(sql4, conn)
    #Объединяем все имена шаблонов в 1 строку
        template = template.groupby('Заявка')['Шаблон'].apply(list).reset_index(name='Шаблон')
        template['Шаблон'] = template['Шаблон'].apply(lambda x: ','.join([str(i) for i in x]))#убираем квадратные скобки из списка шаблонов(не влазят в гуглотаблицы)
    except:
        print('')

    conn.close()
    
    # Добавляем к фрейму данные из запросов
    final_df = final_df.merge(sku_1, how="left")
    final_df = final_df.merge(sku_2, how="left")
    final_df.loc[(final_df.Объем1 == 0), ('Объем')] = ''
    final_df.loc[(final_df.Объем2 == 0), ('Объем1')] = ''
    final_df.loc[(final_df.Объем2 == 0), ('Объем2')] = ''
    final_df = final_df.merge(blueprint, how="left")
    final_df = final_df.merge(clientreq, how="left")
    try:
        final_df = final_df.merge(template, how="left")
    except:
        final_df['Шаблон'] = ''
    final_df = final_df.merge(dates, how="left")
    final_df = final_df.merge(df_value_counts1, how="left")
    final_df = final_df.merge(df_value_counts2, how="left")
    final_df["Заявка"].fillna('0', inplace=True) # меняем наны столбца на нули
    final_df.fillna('', inplace=True) #дропаем Nans
    final_df["Заявка"] = final_df["Заявка"].astype(int)
    final_df.loc[:,'Заявка'] = final_df.Заявка.apply(lambda x: 'https://m54.millionagents.com/clientreqs/' + str(x) + '/show' if x!=0 else None) #добавляем символы для получения ссылки из номера заявки
    final_df = final_df[['Неделя','Волна','Объем','Объем1','Объем2','Количество 1','Количество 2','ID проекта','Блюпринт','Заявка','Шаблон','Дата начала сбора','Начало сбора','Дата окончания сбора','Конец сбора']] #устанавливаем порядок столбцов
    Check_sheet.values_clear("Лента!A2:O100") # Удаляем все записи в диапазоне а1 o100
    check_sh.update('A2',final_df.values.tolist()) # переносим данные в отчет
    print('Данные по сборам "Лента" созданы')

def menu(): # Основное меню скрипта
    print('\n   < < < < < МЕНЮ > > > > >\
    \nВВЕДИТЕ НОМЕР КЛИЕНТА\
    \nАшан (0)\
    \nКарусель (1)\
    \nМагнит (2)\
    \nОкей (3)\
    \nЛента (4)\
    \nМетро (5)')
    answer=input()

    if answer == '0':check_Aushan(),input("Нажмите Enter для возврата в меню"), menu()
    elif answer == '1':check_Karousel(),input("Нажмите Enter для возврата в меню"), menu()
    elif answer == '2':check_Magnit(),input("Нажмите Enter для возврата в меню"), menu()
    elif answer == '3':check_Okey(),input("Нажмите Enter возврата в меню"), menu()        
    elif answer == '4':check_Lenta(),input("Нажмите Enter для возврата в меню"), menu()
    elif answer == '5':check_Metro(),input("Нажмите Enter для возврата в меню"), menu()

menu()