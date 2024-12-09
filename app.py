import sys
from pqt.design import Ui_MainWindow
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
from auchan_frov import Frov

# Приложению нужен один (и только один) экземпляр QApplication.
# Передаём sys.argv, чтобы разрешить аргументы командной строки для приложения.
# Если не будете использовать аргументы командной строки, QApplication([]) тоже работает


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.the_button_was_clicked)
        # self.setWindowTitle("My App")
        # self.setFixedSize(QSize(400, 300))
        # button = QPushButton("Press Me!")

        # # Set the central widget of the Window.
        # self.setCentralWidget(button)
        # button.setCheckable(True)
        # button.clicked.connect(self.the_button_was_clicked)

        # # Set the central widget of the Window.
        # self.setCentralWidget(button)

    def the_button_was_clicked(self):
        t= Frov()
        t.filefrov()
     

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    