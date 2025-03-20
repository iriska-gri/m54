import os.path
import pandas as pd
import psycopg2

from datetime import datetime
import os.path

# path = sys.argv[1] + "/"

# Задаем путь к папке path
try:
   path = sys.argv[1] + "/"
except:
   path = "C:\\Project\\Magnit\\promo\\"  # Базовая директория

inpath = path + "in/"
outpath = path + "tmp/"

# Достаем дату парсинга из parsing.csv
df = pd.read_csv(inpath + 'parsing.csv')

# Получаем дату
date = str(df['start_at'].values[0])
date = date.split()[0]
df["start_at"] = pd.to_datetime(df["start_at"])

# Извлекаем год и номер недели
year = df["start_at"].dt.year[0]
week = df["start_at"].dt.isocalendar().week[0]

# Проверяем, есть ли "5ka_dostavka" в столбце shop_row_id чтобы определить пт или вт
if "5ka_dostavka" in df["store"].astype(str).values:
    print("Значение '5ka_dostavka' найдено в shop_row_id!")
    wave = f'mag_online_promo_tue_{year}_{week}'
    print(wave)
else:
    print("Значение '5ka_dostavka' отсутствует в shop_row_id.")
    wave = f'mag_online_promo_fri_{year}_{week-1}'
    print(wave)





def connect_base(sql): 
    # try:
        conn = psycopg2.connect(dbname='pm', user='psqlreader',
                            password='aImf3fivls34', host='localhost', port=8089)
        df = pd.read_sql_query(sql, conn)
        
        conn.close()
        print('\nСоединение установлено')
        return df
   

def main():
    sql =f"""select a.id  article_id,

    r.id  report_id
    from ma_metro.articles a
    join ma_metro.reports_articles_relations rar on a.id = rar.article_id
    join ma_metro.reports r on rar.report_id = r.id
    join ma_metro.tasks t on r.task_id = t.id
    where a.initial_wave = '{wave}'
    and ((rar.is_chosen = TRUE) or (rar.is_chosen isnull and rar.sim >= 0.8));"""
    df = connect_base(sql)
    df.to_csv(outpath + 'articles_matching_result_B.csv', index=False)

main()
