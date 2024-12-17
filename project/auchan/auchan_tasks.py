import pandas as pd
import gspread
import datetime

class Tasks():

    def __init__(self):
        gc = gspread.oauth()
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1QXFnls8bVv3HElpnRMe_ZGJ6r7XBMaWTai6iihxTwto/edit?pli=1&gid=368938107#gid=368938107')
        sh = gr.worksheet("График")
        data = sh.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        # self.filter_for_week(df)

    def open_forming_auchan(self):
        gc = gspread.oauth()
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1QXFnls8bVv3HElpnRMe_ZGJ6r7XBMaWTai6iihxTwto/edit?pli=1&gid=368938107#gid=368938107')
        sh = gr.worksheet("График")
        data = sh.get_all_values()
        headers = data.pop(0)
        return pd.DataFrame(data, columns=headers)


    def googletable_auchan(self, input_text_wave):
        gc = gspread.oauth()
       
        gr = gc.open_by_url('https://docs.google.com/spreadsheets/d/1QXFnls8bVv3HElpnRMe_ZGJ6r7XBMaWTai6iihxTwto/edit?pli=1&gid=368938107#gid=368938107')
        
        sh = gr.worksheet("График")
        data = sh.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        # self.filter_for_wave(df)

        # return dict_tt

    def filter_for_wave(self, input_text_wave):
        df = self.open_forming_auchan()
        df = df[df["Волна"]==input_text_wave]
        print(df)

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