import sys
from pqt.design import Ui_MainWindow
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
from project.auchan import auchan_zn
from project.auchan.auchan_frov import Auchan_frov
from project.auchan.auchan_zn import Auchan_zn
import os

# Приложению нужен один (и только один) экземпляр QApplication.
# Передаём sys.argv, чтобы разрешить аргументы командной строки для приложения.
# Если не будете использовать аргументы командной строки, QApplication([]) тоже работает


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButtonFrov.clicked.connect(self.the_button_was_clicked_FROV)
        self.pushButtonZN.clicked.connect(self.the_button_was_clicked_ZN)
        self.setWindowTitle("Контроль обработки файлов")
        self.pushButtonTz.clicked.connect(lambda: self.open_folder(r'C:\Project\Auchan\tz'))
        self.pushButtonfFor_import.clicked.connect(lambda: self.open_folder(r'C:\Project\Auchan\for_import'))
        # self.setFixedSize(QSize(400, 300))
        # button = QPushButton("Press Me!")

        # # Set the central widget of the Window.
        # self.setCentralWidget(button)
        # button.setCheckable(True)
        # button.clicked.connect(self.the_button_was_clicked)

        # # Set the central widget of the Window.
        # self.setCentralWidget(button)

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
     

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    