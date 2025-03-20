import sys
from pqt.design import Ui_MainWindow
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QTableWidgetItem, QMessageBox
from project.auchan.auchan_frov import Auchan_frov
from project.auchan.auchan_zn import Auchan_zn
from project.auchan.auchan_tasks import Tasks
# from project.auchan.AP_file import Tasks
import os
import webbrowser  # Модуль для открытия ссылок

# Приложению нужен один (и только один) экземпляр QApplication.
# Передаём sys.argv, чтобы разрешить аргументы командной строки для приложения.
# Если не будете использовать аргументы командной строки, QApplication([]) тоже работает


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.get_info_wave_auchan()
        self.pushButtonFrov.clicked.connect(self.the_button_was_clicked_FROV)
        self.pushButtonZN.clicked.connect(self.the_button_was_clicked_ZN)
        self.setWindowTitle("Контроль обработки файлов")
        self.pushButtonTz.clicked.connect(lambda: self.open_folder(r'C:\Project\Auchan\tz'))
        self.pushButtonfFor_import.clicked.connect(lambda: self.open_folder(r'C:\Project\Auchan\for_import'))
        self.pushButton_timetableAuchan.clicked.connect(lambda: webbrowser.open("https://docs.google.com/spreadsheets/d/1QXFnls8bVv3HElpnRMe_ZGJ6r7XBMaWTai6iihxTwto/edit?pli=1&gid=368938107#gid=368938107"))
        self.pushButton_timetableMetro.clicked.connect(lambda: webbrowser.open("https://docs.google.com/spreadsheets/d/1LOU86hUB7ug-y2SKX8eTuXlGuPYy89SMH6ogHFgDFeA/edit?gid=1699846861#gid=1699846861"))
        self.pushButton_diskRegular.clicked.connect(lambda: webbrowser.open("https://metro-my.sharepoint.com/personal/darya_demina_metro-cc_ru/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fdarya%5Fdemina%5Fmetro%2Dcc%5Fru%2FDocuments%2FMA%26Metro%2FFood%2FQuestionnaires%2FRegular%2F2024"))
        self.pushButton_diskAdditional.clicked.connect(lambda: webbrowser.open("https://metro-my.sharepoint.com/personal/darya_demina_metro-cc_ru/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fdarya%5Fdemina%5Fmetro%2Dcc%5Fru%2FDocuments%2FMA%26Metro%2FFood%2FQuestionnaires%2FAdditional%2F2024"))
        self.pushButton_timetableSemishagoff.clicked.connect(lambda: webbrowser.open("https://docs.google.com/spreadsheets/d/1vljvqy1fBs6CxelZ9kCG10teQLd9srzPVAyodXgz838/edit?gid=1867200013#gid=1867200013"))
        self.pushButton_timetableMagnit.clicked.connect(lambda: webbrowser.open("https://docs.google.com/spreadsheets/d/1b8qWS0IUElJv2v3N2-X6t3WYdG2EgwL_omeWHVY0vvA/edit?gid=1046779328#gid=1046779328"))
        self.pushButton_timetableParsers.clicked.connect(lambda: webbrowser.open("https://docs.google.com/spreadsheets/d/14l_CX55DyV_jEALoNktn4Y8Fqb3seQ-jSA4NVLJh5eQ/edit?gid=0#gid=0"))
        self.pushButton_tasks_auchan.clicked.connect(self.the_button_was_task_auchan)
   

    def the_button_was_clicked_FROV(self):
        auchanFrov = Auchan_frov()
        frov = auchanFrov.filefrov()
        self.file_frov.setText(str(frov[0]))
        self.file_frov_2.setText(str(frov[1]))
        self.file_frov_3.setText(str(frov[2]))

    def the_button_was_clicked_ZN(self):
        auchanZN = Auchan_zn()
        zn = auchanZN.file_zn()
        self.file_zn.setText(str(zn[0]))
        self.file_zn_2.setText(str(zn[1]))
        self.file_zn_3.setText(str(zn[2]))

    def open_folder(self, path):
        # Укажите путь к папке
        folder_path = path


        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # Windows
            if os.name == "nt":
                os.startfile(folder_path)
        else:
            print(f"Путь не найден: {folder_path}")
     
    def the_button_was_task_auchan(self):
        task = Tasks()
        input_tt = self.lineEdit__idTT_aushan.text()
        input_text_wave = self.lineEdit_wave_auchan.text()
          # Проверяем, какая радиокнопка выбрана
        if self.radioButton_frov.isChecked():
            selected_option = "FROV"
        elif self.radioButton_samdesch.isChecked():
            selected_option = "samdesch"
        else:
            QMessageBox.warning(self, "Ошибка", "Не выбрана ни одна из опций!")
            return
        task.filter_for_wave(input_tt, input_text_wave, selected_option)
        
        # task.filter_for_wave(input_text_wave)  
 

    def get_info_wave_auchan(self):
        task = Tasks()
        # number_week = self.lineEdit_week_auchan.text()
        # info_wave = task.filter_for_week(number_week) 
        # self.tableWidget_auchan.setRowCount(len(info_wave))
        # self.tableWidget_auchan.setColumnCount(len(info_wave[0]))
        # for i in range(len(info_wave)):
        #     for j in range(len(info_wave[0])):
        #         self.tableWidget_auchan.setItem(i, j, QTableWidgetItem(str(info_wave[i][j])))
        # self.tableWidget_auchan.resizeColumnsToContents()
        # self.tableWidget_auchan.horizontalHeader().setStretchLastSection(True)      
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    