from cmath import nan
import re
import pandas as pd
import os

file_path = 'C:/Users/IRINA/Desktop/Project/m54/project/magnit/promo_brand.xlsx'
df = pd.read_excel(file_path, sheet_name='Лист1')

first_array = df['name'].dropna().tolist()

df['Название'] = df['Название'].dropna()
h = df['Название'].dropna().tolist()
second_array = df['Название'].dropna().tolist()
result_dict = {}
k = 0

# Для каждого элемента из второго массива
batch_size = 1000
while second_array:
    batch = second_array[:batch_size]

    for part in batch :
      
        # Для каждого слова из первого массива
        for word in first_array:
            
            if len(re.findall(f'({re.escape(part).lower()})', word.lower())) > 0:
                # Если совпадения есть, добавляем в словарь
                if part not in result_dict:
                 
                    result_dict[part] = []
                result_dict[part].append(word)
    k =k +1
    print(f'{k} из {len(h)/batch_size}')
    second_array = second_array[batch_size:]

    # Выводим результат

    # if len(result_dict) > 0:
    df_dict = pd.DataFrame.from_dict(result_dict, orient='index')
    df_dict.to_excel(f'C:/Users/IRINA/Desktop/Project/m54/project/magnit/brand_{k}.xlsx')
    if os.path.exists(f'C:/Users/IRINA/Desktop/Project/m54/project/magnit/brand_{k-1}.xlsx'):
        os.remove(f'C:/Users/IRINA/Desktop/Project/m54/project/magnit/brand_{k-1}.xlsx')
    