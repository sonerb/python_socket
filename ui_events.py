# -*- coding: utf-8 -*-
import json
import queue 

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import (QCloseEvent, QIcon, QPixmap, QStandardItem,
                         QStandardItemModel, QCursor, QFont)
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon

import resources_rc

from form_chat import Ui_ChatWindow
from form_settings import Ui_Settings

from functools import partial


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

    def btn_pm_send_clicked(self, ui):
        message = ui.txt_message.text()
        self.client.talk(message, ui.username)
        ui.txt_message.setText('')

    QtCore.pyqtSlot(str)
    def on_message(self, msg):
        self.ui.txt_chat.append(msg)

    QtCore.pyqtSlot(str, str, str)
    def on_pm_message(self, msg, m_from, m_to):
        if self.client.username == m_from:
            self.create_chat_window(m_to)
            self.ui.windows.chat[m_to].ui.txt_chat.append(msg)
        else:
            self.create_chat_window(m_from)

            if self.ui.windows.chat[m_from].window.isVisible():
                self.ui.windows.chat[m_from].ui.txt_chat.append(msg)
            else:
                if not m_from in self.client.user_chat_queue:
                    self.client.user_chat_queue[m_from] = queue.Queue()

                self.client.user_chat_queue[m_from].put(msg)
                print('karşı, queue eklendi.')

                model = self.ui.lst_users.model()
                std_items = model.findItems(m_from)
                if std_items:
                    item = std_items[0]
                    tmp_font = item.font()
                    tmp_font.setBold(True)
                    item.setFont(tmp_font)
                # item.setText('{0} ({1})'.format(item.text(), self.client.user_chat_queue[m_from].qsize()))
                    print(item.text())

                # for index in range(model.rowCount()):
                #     item = model.item(index)
                #     tmp_font = item.font()
                #     tmp_font.setBold(True)
                #     item.setFont(tmp_font)
                #     print(item.text())


        # if self.client.username == m_from:
        #     self.create_chat_window(m_to)
        #     self.ui.windows.chat[m_to][1].txt_chat.append(msg)
        # else:
        #     self.create_chat_window(m_from)

        #     # if self.ui.windows.chat[m_from][0].isVisible():
        #     #     self.ui.windows.chat[m_from][1].txt_chat.append(msg)
        #     # else:
        #     #     self.ui.windows.chat[m_from][1].txt_chat.append(msg)
        #     #     self.ui.windows.chat[m_from][0].hide()

        #     if self.ui.windows.chat[m_from][0].isVisible():
        #         print('isVisible True')
        #         self.ui.windows.chat[m_from][1].txt_chat.append(msg)
        #     else:
        #         print('isVisible False')
        #         self.ui.windows.chat[m_from][1].txt_chat.append(msg)
        #         self.ui.windows.chat[m_from][0].showMinimized()

        #         self.window.tray_icon.messageClicked.connect(self.ui.windows.chat[m_from][0].show)
        #         self.window.tray_icon.showMessage(
        #             self.window.windowTitle(),
        #             "%s send a message"%(m_from),
        #             QSystemTrayIcon.Information,
        #             2000
        #         )

    QtCore.pyqtSlot(object)
    def on_user_list(self, obj):
        model = QStandardItemModel(self.ui.lst_users)

        for user in obj:
            item = QStandardItem(user)     
            item.setEditable(False)   
            model.appendRow(item)
        
        self.ui.lst_users.setModel(model)

        self.ui.lbl_sbar_user_count.setText('{0}'.format(model.rowCount()))
    
    QtCore.pyqtSlot()
    def on_connect(self):
        self.ui.btn_connect.setVisible(False)
        self.ui.actionConnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(True)
        self.ui.btn_disconnect.setVisible(True)
        self.ui.lbl_sbar_conn.setStyleSheet('color: green')
        self.ui.lbl_sbar_conn.setText('Connected')
        self.ui.lbl_sbar_login.setText('Logged as <b>{0}</b>'.format(self.client.username))

        self.chat_windows_status(True)

        self.ui.txt_message.setReadOnly(False)
        self.ui.txt_username.setReadOnly(True)
        self.ui.txt_message.setFocus()
    
    QtCore.pyqtSlot()
    def on_disconnect(self):
        self.ui.btn_disconnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(False)
        self.ui.actionConnect.setVisible(True)
        self.ui.btn_connect.setVisible(True)
        self.ui.lbl_sbar_conn.setStyleSheet('color: red')
        self.ui.lbl_sbar_conn.setText('Disconnected')
        self.ui.lbl_sbar_login.setText('')
        self.ui.lbl_sbar_user_count.setText('0')

        self.chat_windows_status(False)

        self.ui.txt_message.setReadOnly(True)
        self.ui.txt_username.setReadOnly(False)
        self.ui.txt_username.setFocus()

    QtCore.pyqtSlot()
    def on_clear_user_list(self):
        model = QStandardItemModel(self.ui.lst_users)        
        self.ui.lst_users.setModel(model)

        QtCore.pyqtSlot(str, str, str)
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
            if hasattr(self.ui, 'windows'):
                if hasattr(self.ui.windows, 'settings'):
                    self.ui.windows.settings.window.close()

                if hasattr(self.ui.windows, 'chat'):
                    for key, val in self.ui.windows.chat.items():
                        val.window.close()

            self.client.stop()
            event.accept()
    
    def appQuitEvent(self):
        self.client.stop()
        self.app.quit()

    def create_chat_window(self, username):
        if not hasattr(self.ui, 'windows'):
            self.ui.windows = lambda: None

        if not hasattr(self.ui.windows, 'chat'):
            setattr(self.ui.windows, 'chat', dict())
        
        # if not 'chat' in self.ui.windows:
        #     self.ui.windows.chat = dict()

        if not username in self.ui.windows.chat:
            icon = QIcon()
            icon.addPixmap(QPixmap(":/images/resources/images/chat_48x48.ico"), QIcon.Normal, QIcon.Off)

            tmp_window = QtWidgets.QMainWindow()
            tmp_ui = Ui_ChatWindow()
            tmp_ui.setupUi(tmp_window)
            tmp_ui.username = username

            tmp_ui.btn_send.clicked.connect(partial(self.btn_pm_send_clicked, tmp_ui))
            tmp_ui.txt_message.returnPressed.connect(partial(self.btn_pm_send_clicked, tmp_ui))

            tmp_ui.statusbar.addPermanentWidget(tmp_ui.lbl_sbar_conn, 2)
            tmp_ui.statusbar.addPermanentWidget(tmp_ui.lbl_sbar_login, 8)

            tmp_window.setWindowIcon(icon)
            tmp_window.setWindowTitle('{} - Chat'.format(username))

            self.ui.windows.chat[username] = lambda: None

            setattr(self.ui.windows.chat[username], 'window', tmp_window)
            setattr(self.ui.windows.chat[username], 'ui', tmp_ui)

            self.chat_windows_status(True)

    def lst_users_double_clicked(self, item: QModelIndex):
        username = item.data()

        model = self.ui.lst_users.model()
        std_item = model.item(item.row())
        tmp_font = std_item.font()
        tmp_font.setBold(False)
        std_item.setFont(tmp_font)

        self.create_chat_window(username)

        self.ui.windows.chat[username].window.show()
        self.ui.windows.chat[username].ui.txt_message.setFocus()

        if username in self.client.user_chat_queue:
            while not self.client.user_chat_queue[username].empty():
                msg = self.client.user_chat_queue[username].get()
                print(msg)
                self.ui.windows.chat[username].ui.txt_chat.append(msg)

    def load_settings_form(self):
        tmp_ui = self.ui.windows.settings.ui
        tmp_ui.txt_server_address.setText(str(self.settings['settings']['server'][0]))
        tmp_ui.txt_server_port.setText(str(self.settings['settings']['server'][1]))
        tmp_ui.txt_enc_password.setText(str(self.settings['settings']['encryption']))
        tmp_ui.chb_minimize.setChecked(self.settings['settings']['minimize'])
    
    def settings_form_ok(self):
        tmp_ui = self.ui.windows.settings.ui
        tmp_window = self.ui.windows.settings.window
        
        server_address = str(tmp_ui.txt_server_address.text())
        server_port = int(tmp_ui.txt_server_port.text())
        enc_password = str(tmp_ui.txt_enc_password.text())


        self.settings['settings']['server'] = [server_address, server_port]
        self.settings['settings']['encryption'] = enc_password
        self.settings['settings']['minimize'] = tmp_ui.chb_minimize.isChecked()

        with open('settings.json', 'w') as file:
            file.write(json.dumps(self.settings))

        self.client.host_port = (server_address, server_port)
        self.client.enc_pass = enc_password

        print('Saved!')
        tmp_window.hide()


    def open_preferences(self):
        if not hasattr(self.ui, 'windows'):
            self.ui.windows = lambda: None
        
        if not hasattr(self.ui.windows, 'settings'):
            setattr(self.ui.windows, 'settings', lambda: None)
            setattr(self.ui.windows.settings, 'window', None)
            setattr(self.ui.windows.settings, 'ui', None)

            icon = QIcon()
            icon.addPixmap(QPixmap(":/images/resources/images/chat_48x48.ico"), QIcon.Normal, QIcon.Off)
            
            tmp_window = QtWidgets.QDialog()
            tmp_ui = Ui_Settings()
            tmp_ui.setupUi(tmp_window)
            tmp_window.setWindowIcon(icon)
            tmp_window.accept = self.settings_form_ok

            self.ui.windows.settings.window = tmp_window
            self.ui.windows.settings.ui = tmp_ui

        self.load_settings_form()
        self.ui.windows.settings.window.show()

    def sys_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.window.tray_icon.contextMenu().exec_(QCursor().pos())
        elif reason == QSystemTrayIcon.Trigger:
            self.window.show()

    def chat_windows_status(self, status):
        if status:
            if hasattr(self.ui, 'windows') and hasattr(self.ui.windows, 'chat'):
                for key, val in self.ui.windows.chat.items():
                    val.ui.lbl_sbar_conn.setStyleSheet('color: green')
                    val.ui.lbl_sbar_conn.setText('Connected')
                    val.ui.lbl_sbar_login.setText('Logged as <b>{0}</b>'.format(self.client.username))
        else:
            if hasattr(self.ui, 'windows') and hasattr(self.ui.windows, 'chat'):
                for key, val in self.ui.windows.chat.items():
                    val.ui.lbl_sbar_conn.setStyleSheet('color: red')
                    val.ui.lbl_sbar_conn.setText('Disconnected')
                    val.ui.lbl_sbar_login.setText('')