# -*- coding: utf-8 -*-
import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import (QCloseEvent, QIcon, QPixmap, QStandardItem,
                         QStandardItemModel, QCursor)
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon

import resources_rc
from form_chat import Ui_ChatWindow
from form_settings import Ui_Settings


class UI_Events(object):
    def __init__(self, _app, _ui, _client, _window, _settings):
        self.ui = _ui
        self.app = _app
        self.client = _client
        self.window = _window
        self.settings = _settings

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

    def closeEvent(self, event:QCloseEvent):
        if self.settings['settings']['minimize']:
            event.ignore()
            self.window.hide()
            self.window.tray_icon.showMessage(
                self.window.windowTitle(),
                "Application was minimized to Tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.client.stop()
            event.accept()
    
    def appQuitEvent(self):
        self.client.stop()
        self.app.quit()

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
        if not hasattr(self.ui, 'windows'):
            self.ui.windows = dict()
        
        if not 'chat' in self.ui.windows:
            self.ui.windows['chat'] = dict()

        username = item.data()

        if not username in self.ui.windows['chat']:
            icon = QIcon()
            icon.addPixmap(QPixmap(":/images/resources/images/chat_48x48.ico"), QIcon.Normal, QIcon.Off)

            tmp_window = QtWidgets.QMainWindow()
            self.ui.windows['chat'][username] = tmp_window
            cw = self.ui.windows['chat'][username]
            tmp_ui = Ui_ChatWindow()
            tmp_ui.setupUi(cw)
            cw.setWindowIcon(icon)
            cw.setWindowTitle('{} - Chat'.format(username))
            cw.show()
        else:
            self.ui.windows['chat'][username].show()
    
    def sys_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.window.tray_icon.contextMenu().exec_(QCursor().pos())
        elif reason == QSystemTrayIcon.Trigger:
            self.window.show()

    def load_settings_form(self):
        ui = self.ui.windows['settings'][1]
        ui.txt_server_address.setText(str(self.settings['settings']['server'][0]))
        ui.txt_server_port.setText(str(self.settings['settings']['server'][1]))
        ui.txt_enc_password.setText(str(self.settings['settings']['encryption']))
        ui.chb_minimize.setChecked(self.settings['settings']['minimize'])
    
    def settings_form_ok(self):
        ui = self.ui.windows['settings'][1]
        window = self.ui.windows['settings'][0]
        
        server_address = str(ui.txt_server_address.text())
        server_port = int(ui.txt_server_port.text())
        enc_password = str(ui.txt_enc_password.text())


        self.settings['settings']['server'] = [server_address, server_port]
        self.settings['settings']['encryption'] = enc_password
        self.settings['settings']['minimize'] = ui.chb_minimize.isChecked()

        with open('settings.json', 'w') as file:
            file.write(json.dumps(self.settings))

        self.client.host_port = (server_address, server_port)
        self.client.enc_pass = enc_password

        print('Saved!')
        window.hide()


    def open_preferences(self):
        if not hasattr(self.ui, 'windows'):
            self.ui.windows = dict()

        if not 'settings' in self.ui.windows:
            icon = QIcon()
            icon.addPixmap(QPixmap(":/images/resources/images/chat_48x48.ico"), QIcon.Normal, QIcon.Off)
            
            tmp_window = QtWidgets.QDialog()
            tmp_ui = Ui_Settings()
            tmp_ui.setupUi(tmp_window)
            tmp_window.setWindowIcon(icon)
            tmp_window.accept = self.settings_form_ok
            self.ui.windows['settings'] = [tmp_window, tmp_ui]
        
        self.load_settings_form()
        self.ui.windows['settings'][0].show()
