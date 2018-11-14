from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMessageBox

from form_chat import Ui_ChatWindow

class UI_Events(object):
    def __init__(self, app, ui, client, window):
        self.ui = ui
        self.app = app
        self.client = client
        self.window = window

    def btn_connect_clicked(self):
        username = self.ui.txt_username.text()
        self.client.connect()
        self.client.start()
        self.client.set_username(username)
    
    def btn_disconnect_clicked(self):
        self.client.disconnect()

    def btn_send_clicked(self):
        message = self.ui.txt_message.text()
        self.client.talk(message)
        self.ui.txt_message.setText('')

    def txt_message_enter(self):
        self.btn_send_clicked()
    
    def txt_username_enter(self):
        self.btn_connect_clicked()

    def on_message(self, msg):
        self.ui.txt_chat.append(msg)

    def on_user_list(self, obj):
        model = QStandardItemModel(self.ui.lst_users)

        for user in obj:
            item = QStandardItem(user)     
            item.setEditable(False)   
            model.appendRow(item)
        
        self.ui.lst_users.setModel(model)
    
    def on_connect(self):
        self.ui.btn_connect.setVisible(False)
        self.ui.actionConnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(True)
        self.ui.btn_disconnect.setVisible(True)
        self.ui.statusbar.showMessage('Connected')
        self.ui.txt_message.setReadOnly(False)
        self.ui.txt_username.setReadOnly(True)
        self.ui.txt_message.setFocus()

    def on_disconnect(self):
        self.ui.btn_disconnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(False)
        self.ui.actionConnect.setVisible(True)
        self.ui.btn_connect.setVisible(True)
        self.ui.statusbar.showMessage('Disconnected')
        self.ui.txt_message.setReadOnly(True)
        self.ui.txt_username.setReadOnly(False)
        self.ui.txt_username.setFocus()

    def on_clear_user_list(self):
        model = QStandardItemModel(self.ui.lst_users)        
        self.ui.lst_users.setModel(model)

    def on_close(self):
        self.app.closeAllWindows()

    def closeEvent(self, QCloseEvent):
        self.client.stop()

    def show_dialog_box(self, title, message, mb_type):
        if mb_type == 'c':
            QMessageBox.critical(self.window, title, message)
        elif mb_type == 'i':
            QMessageBox.information(self.window, title, message)
        elif mb_type == 'q':
            QMessageBox.question(self.window, title, message)
        elif mb_type == 'w':
            QMessageBox.warning(self.window, title, message)
        else:
            QMessageBox.information(self.window, title, message)

    def lst_users_double_clicked(self, item: QModelIndex):
        # print(self.ui.lst_users.selectionModel.select(item))
        self.ui.MainWindow = QtWidgets.QMainWindow()
        self.ui.cw = Ui_ChatWindow()
        self.ui.cw.setupUi(self.ui.MainWindow)
        self.ui.MainWindow.show()
