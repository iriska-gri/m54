import datetime
import os


# current_week = "2025_10"
# tuesday = datetime.datetime(2025, 3, 11) 
# print(tuesday.isocalendar()[1], tuesday.year)

# current_week = [2025, 10]

# print(current_week[0], current_week[1])



folder_path = "C:\\Project\\Magnit\\marketplace\\in"
files = [entry.name for entry in os.scandir(folder_path) if entry.is_file()]

print(files)