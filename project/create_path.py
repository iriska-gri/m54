import os

def create_pach():
# Путь к папке на диске C:
    current_week = [2025, 10]
    folder_name = "Project"  # Название папки
    folder_path = os.path.join("C:\\", folder_name)

    # Проверяем наличие папки и создаем, если её нет
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Папка '{folder_name}' создана на диске C:.")
    else:
        print(f"Папка '{folder_name}' уже существует.")