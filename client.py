# -*- coding: utf-8 -*-
"""
client.py
"""
__author__ = "Soner Bayram, Orhan Yılmaz"
__copyright__ = "Copyright 2018, The Socket Chat Program"
__credits__ = ["sonerb", "mafgom"]
__license__ = "GPL"
__version__ = "0.0.1"
__status__ = "Development"

import os
import json
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QSystemTrayIcon, QAction, QMenu
from PyQt5.QtGui import QPixmap, QIcon

from form_main import Ui_SocketChat
from ui_events import UI_Events
from socket_client import SocketClient

password = "My Secret Word!"
host = '10.90.4.109'
port = 80

class Communicate(QObject):
    """ Communication class """

    signal_on_message = pyqtSignal(str)
    signal_on_pm_message = pyqtSignal(str, str, str)
    signal_on_connect = pyqtSignal()
    signal_on_disconnect = pyqtSignal()
    signal_on_user_list = pyqtSignal(object)
    signal_clear_user_list = pyqtSignal()
    signal_show_dialog_box = pyqtSignal(str, str, str)

    def __init__(self):
        QObject.__init__(self)

def load_settings():
    if os.path.exists('settings.json'):
        json_data = open('settings.json').read()

        data = json.loads(json_data)
        return data
    else:
        return False

def main():
    """ main function """
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    qt_ui = Ui_SocketChat()
    qt_ui.setupUi(main_window)

    # j_settings = json.load('settings.json')
    j_settings = load_settings()
    if j_settings:
        password = j_settings['settings']['encryption']
        host = j_settings['settings']['server'][0]
        port = int(j_settings['settings']['server'][1])

    signals = Communicate()
    sck_client = SocketClient(server=(host, port), enc_pass=password, signals=signals)
    events = UI_Events(app, qt_ui, sck_client, main_window, j_settings)

    signals.signal_on_message.connect(events.on_message)
    signals.signal_on_pm_message.connect(events.on_pm_message)
    signals.signal_on_connect.connect(events.on_connect)
    signals.signal_on_disconnect.connect(events.on_disconnect)
    signals.signal_on_user_list.connect(events.on_user_list)
    signals.signal_clear_user_list.connect(events.on_clear_user_list)
    signals.signal_show_dialog_box.connect(events.show_dialog_box)

    qt_ui.btn_connect.clicked.connect(events.btn_connect_clicked)
    qt_ui.btn_disconnect.clicked.connect(events.btn_disconnect_clicked)

    qt_ui.actionConnect.triggered.connect(events.btn_connect_clicked)
    qt_ui.actionDisconnect.triggered.connect(events.btn_disconnect_clicked)
    qt_ui.actionClose.triggered.connect(events.on_close)

    qt_ui.btn_send.clicked.connect(events.btn_send_clicked)
    qt_ui.txt_message.returnPressed.connect(events.txt_message_enter)
    qt_ui.txt_username.returnPressed.connect(events.txt_username_enter)

    qt_ui.lst_users.doubleClicked.connect(events.lst_users_double_clicked)
    qt_ui.actionPrerefences.triggered.connect(events.open_preferences)

    qt_ui.btn_disconnect.setVisible(False)
    qt_ui.actionDisconnect.setVisible(False)

    qt_ui.statusbar.showMessage('Disconnected')
    qt_ui.txt_message.setReadOnly(True)

    ############################# SYSTEM TRAY ICON #############################
    icon = QIcon()
    icon.addPixmap(QPixmap(":/images/resources/images/chat_48x48.ico"), QIcon.Normal, QIcon.Off)

    main_window.tray_icon = QSystemTrayIcon(main_window)
    main_window.tray_icon.setIcon(icon) #setIcon(main_window.style().standardIcon(QStyle.SP_ComputerIcon))
    main_window.tray_icon.activated.connect(events.sys_tray_icon_activated)
    # main_window.tray_icon.messageClicked.connect(main_window.show)

    show_action = QAction("Show", main_window)
    quit_action = QAction("Exit", main_window)
    hide_action = QAction("Hide", main_window)
    show_action.triggered.connect(main_window.show)
    hide_action.triggered.connect(main_window.hide)
    quit_action.triggered.connect(events.appQuitEvent)

    tray_menu = QMenu()
    tray_menu.addAction(show_action)
    tray_menu.addAction(hide_action)
    tray_menu.addAction(quit_action)

    main_window.tray_icon.setContextMenu(tray_menu)
    main_window.tray_icon.show()
    ########################################3###################################

    main_window.closeEvent = events.closeEvent

    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':

    if len(sys.argv) > 1:
        password = sys.argv[1]

    main()
