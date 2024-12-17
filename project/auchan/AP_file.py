import pandas as pd
import gspread
import glob
import os

class AP_forming():

    def __init__(self):
        pass

    def open_APForming(self):
        try:
            file_path = f'C:/Project/Auchan/tz/AP.xlsx'
        
            if os.path.exists(file_path):
                os.remove(file_path)
            try:
                file = pd.read_excel(glob.glob('C:/Project/Auchan/tz/АП_*')[0], sheet_name = 'Конкуренты_виды мониторинга', header = 0)
                t_google = self.googletable()
                file['ID_COMP'] = file['ID_COMP'].astype(str)
                t_google['ID_COMP'] = t_google['ID_COMP'].astype(str)
                dffile = file.merge(t_google, on='ID_COMP', how='left')
                dffile.to_excel(f'C:/Project/Auchan/tz/АР.xlsx', index =False)
                print(dffile)
            except:
                print('Файл АП не найден')
        except:
            print('Закройте файл в excel')


    def googletable(self):
        way = gspread.oauth()
        needed_sheet = way.open_by_url('https://docs.google.com/spreadsheets/d/1ZZQMx1IXqaKdaU1YfnfG54Imxr04il3ot_ArE3GE-Ec/edit?gid=0#gid=0')
            
        sh = needed_sheet.worksheet("реестр(актуальный)")

        # создаем датафрейм из справочника TT
        data = sh.get_all_values()
        headers = data.pop(0)
        dict_tt = pd.DataFrame(data, columns=headers)
        dict_tt = dict_tt[['ID_COMP', 'АТ (id)']]
        return dict_tt