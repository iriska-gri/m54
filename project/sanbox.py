import datetime
import os

base_dir = "C:\\Project\\Magnit\\marketplace"  # Базовая директория

if not os.path.exists(base_dir):
    os.makedirs(base_dir, exist_ok=True)
    print(f"Создана папка: {base_dir}")
else:
    print(f"Папка '{base_dir}' уже существует.")  