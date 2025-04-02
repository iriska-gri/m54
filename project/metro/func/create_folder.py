import datetime
import os

class Folder_metro(): 
    def __init__(self):
        pass

    def folderMetro(self):

        base_dir = "C:\\Project\\"  # Базовая директория

        mess = []

        # Проверка созданных папок
        folders_info = {
            base_dir: "Основная рабочая директория для всех проектов",
            os.path.join(base_dir, "Metro"): "Директория для проекта Metro",
            os.path.join(base_dir, "Metro\\tz"): "Папка для технических заданий, содержит в себе (актуализировать по мере обновления) \n Забрать файлы с диска",
            os.path.join(base_dir, "Metro\\task"): "Папка для задач, содержит в себе \n task_metro \n task_chiken \n формируются в м54",
            os.path.join(base_dir, "Metro\\outh"): "Папка для выходных данных",
            os.path.join(base_dir, "Metro\\products"): "Папка для хранения товарных позиция для заливку в м54",
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