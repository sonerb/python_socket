# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form_main.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SocketChat(object):
    def setupUi(self, SocketChat):
        SocketChat.setObjectName("SocketChat")
        SocketChat.resize(680, 400)
        SocketChat.setMinimumSize(QtCore.QSize(550, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/resources/images/chat_48x48.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SocketChat.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(SocketChat)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gLayout_main = QtWidgets.QGridLayout()
        self.gLayout_main.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gLayout_main.setObjectName("gLayout_main")
        self.grp_login = QtWidgets.QGroupBox(self.centralwidget)
        self.grp_login.setStyleSheet("")
        self.grp_login.setObjectName("grp_login")
        self.gridLayout = QtWidgets.QGridLayout(self.grp_login)
        self.gridLayout.setObjectName("gridLayout")
        self.txt_username = QtWidgets.QLineEdit(self.grp_login)
        self.txt_username.setObjectName("txt_username")
        self.gridLayout.addWidget(self.txt_username, 1, 0, 1, 1)
        self.lbl_username = QtWidgets.QLabel(self.grp_login)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lbl_username.setFont(font)
        self.lbl_username.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lbl_username.setObjectName("lbl_username")
        self.gridLayout.addWidget(self.lbl_username, 0, 0, 1, 1)
        self.btn_connect = QtWidgets.QPushButton(self.grp_login)
        self.btn_connect.setObjectName("btn_connect")
        self.gridLayout.addWidget(self.btn_connect, 3, 0, 1, 1)
        self.btn_disconnect = QtWidgets.QPushButton(self.grp_login)
        self.btn_disconnect.setStyleSheet("")
        self.btn_disconnect.setObjectName("btn_disconnect")
        self.gridLayout.addWidget(self.btn_disconnect, 2, 0, 1, 1)
        self.gLayout_main.addWidget(self.grp_login, 0, 0, 1, 1)
        self.txt_chat = QtWidgets.QTextEdit(self.centralwidget)
        self.txt_chat.setStyleSheet("")
        self.txt_chat.setReadOnly(True)
        self.txt_chat.setObjectName("txt_chat")
        self.gLayout_main.addWidget(self.txt_chat, 0, 1, 2, 1)
        self.lst_users = QtWidgets.QListView(self.centralwidget)
        self.lst_users.setStyleSheet("")
        self.lst_users.setObjectName("lst_users")
        self.gLayout_main.addWidget(self.lst_users, 1, 0, 1, 1)
        self.hLayout_send = QtWidgets.QHBoxLayout()
        self.hLayout_send.setObjectName("hLayout_send")
        self.txt_message = QtWidgets.QLineEdit(self.centralwidget)
        self.txt_message.setObjectName("txt_message")
        self.hLayout_send.addWidget(self.txt_message)
        self.btn_send = QtWidgets.QPushButton(self.centralwidget)
        self.btn_send.setObjectName("btn_send")
        self.hLayout_send.addWidget(self.btn_send)
        self.gLayout_main.addLayout(self.hLayout_send, 2, 0, 1, 2)
        self.gLayout_main.setColumnStretch(0, 25)
        self.gLayout_main.setColumnStretch(1, 75)
        self.verticalLayout.addLayout(self.gLayout_main)
        SocketChat.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SocketChat)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        SocketChat.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SocketChat)
        self.statusbar.setObjectName("statusbar")
        SocketChat.setStatusBar(self.statusbar)
        self.actionClose = QtWidgets.QAction(SocketChat)
        self.actionClose.setObjectName("actionClose")
        self.actionDisconnect = QtWidgets.QAction(SocketChat)
        self.actionDisconnect.setObjectName("actionDisconnect")
        self.actionConnect = QtWidgets.QAction(SocketChat)
        self.actionConnect.setObjectName("actionConnect")
        self.menuFile.addAction(self.actionConnect)
        self.menuFile.addAction(self.actionDisconnect)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(SocketChat)
        QtCore.QMetaObject.connectSlotsByName(SocketChat)

    def retranslateUi(self, SocketChat):
        _translate = QtCore.QCoreApplication.translate
        SocketChat.setWindowTitle(_translate("SocketChat", "Socket Chat"))
        self.grp_login.setTitle(_translate("SocketChat", "Login"))
        self.lbl_username.setText(_translate("SocketChat", "Username"))
        self.btn_connect.setText(_translate("SocketChat", "Connect"))
        self.btn_disconnect.setText(_translate("SocketChat", "Disconnect"))
        self.btn_send.setText(_translate("SocketChat", "Send"))
        self.menuFile.setTitle(_translate("SocketChat", "File"))
        self.actionClose.setText(_translate("SocketChat", "Close"))
        self.actionDisconnect.setText(_translate("SocketChat", "Disconnect"))
        self.actionConnect.setText(_translate("SocketChat", "Connect"))

import resources_rc
