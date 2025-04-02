import datetime
import os

class Folder_auchan(): 
    def __init__(self):
        pass

    def folderAuchan(self):

        base_dir = "C:\\Project\\"  # Базовая директория

        mess = []

        # Проверка созданных папок
        folders_info = {
            base_dir: "Основная рабочая директория для всех проектов",
            os.path.join(base_dir, "Auchan"): "Директория для проекта Auchan",
            os.path.join(base_dir, "Auchan\\tz"): "Папка для технических заданий, содержит в себе (актуализировать по мере обновления) \n tov_szt.xlsx, \n АП_Март.xlsx, \n Справочник ТТ (Ашан).xlsx, \n ТЗ_Март 2025_МА.xlsx",
            os.path.join(base_dir, "Auchan\\task"): "Папка для задач, содержит в себе \n pattern_task_frov \n pattern_task_frov_szt \n pattern_task_frov_szt_embl \n формируются в м54",
            os.path.join(base_dir, "Auchan\\outh"): "Папка для выходных данных",
            os.path.join(base_dir, "Auchan\\products"): "Папка для хранения товарных позиция для заливку в м54",
        }

        # Создание папок
        for folder, description in folders_info.items():
          
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                mess.append(f"Создана папка: {folder} - {description}")
                print(f"Создана папка: {folder}")
            else:
 
                mess.append(f"Папка '{folder}' уже существует. {description}")
                print(f"Папка '{folder}' уже существует.")

        return mess  