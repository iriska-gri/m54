# Form implementation generated from reading ui file 'pqt/ui_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.textEdit_mess = QtWidgets.QTextEdit(parent=Dialog)
        self.textEdit_mess.setGeometry(QtCore.QRect(10, 10, 381, 241))
        self.textEdit_mess.setObjectName("textEdit_mess")
        self.pushButton_close_dialog = QtWidgets.QPushButton(parent=Dialog)
        self.pushButton_close_dialog.setGeometry(QtCore.QRect(150, 260, 93, 28))
        self.pushButton_close_dialog.setObjectName("pushButton_close_dialog")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton_close_dialog.setText(_translate("Dialog", "ОК"))
