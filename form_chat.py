# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form_chat.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ChatWindow(object):
    def setupUi(self, ChatWindow):
        ChatWindow.setObjectName("ChatWindow")
        ChatWindow.resize(627, 386)
        self.centralwidget = QtWidgets.QWidget(ChatWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.txt_chat = QtWidgets.QTextEdit(self.centralwidget)
        self.txt_chat.setStyleSheet("")
        self.txt_chat.setReadOnly(True)
        self.txt_chat.setObjectName("txt_chat")
        self.verticalLayout.addWidget(self.txt_chat)
        self.hLayout_send = QtWidgets.QHBoxLayout()
        self.hLayout_send.setObjectName("hLayout_send")
        self.txt_message = QtWidgets.QLineEdit(self.centralwidget)
        self.txt_message.setObjectName("txt_message")
        self.hLayout_send.addWidget(self.txt_message)
        self.btn_send = QtWidgets.QPushButton(self.centralwidget)
        self.btn_send.setObjectName("btn_send")
        self.hLayout_send.addWidget(self.btn_send)
        self.verticalLayout.addLayout(self.hLayout_send)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.lbl_sbar_conn = QtWidgets.QLabel(self.centralwidget)
        self.lbl_sbar_conn.setObjectName("lbl_sbar_conn")
        self.verticalLayout_2.addWidget(self.lbl_sbar_conn)
        self.lbl_sbar_login = QtWidgets.QLabel(self.centralwidget)
        self.lbl_sbar_login.setObjectName("lbl_sbar_login")
        self.verticalLayout_2.addWidget(self.lbl_sbar_login)
        ChatWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ChatWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 627, 21))
        self.menubar.setObjectName("menubar")
        ChatWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ChatWindow)
        self.statusbar.setObjectName("statusbar")
        ChatWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ChatWindow)
        QtCore.QMetaObject.connectSlotsByName(ChatWindow)

    def retranslateUi(self, ChatWindow):
        _translate = QtCore.QCoreApplication.translate
        ChatWindow.setWindowTitle(_translate("ChatWindow", "Chat Window"))
        self.btn_send.setText(_translate("ChatWindow", "Send"))
        self.lbl_sbar_conn.setText(_translate("ChatWindow", "lbl_sbar_conn"))
        self.lbl_sbar_login.setText(_translate("ChatWindow", "lbl_sbar_login"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ChatWindow = QtWidgets.QMainWindow()
    ui = Ui_ChatWindow()
    ui.setupUi(ChatWindow)
    ChatWindow.show()
    sys.exit(app.exec_())

