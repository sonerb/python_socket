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
import logging
import socket
import sys
import threading
import time

import coloredlogs
import pprint

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QSystemTrayIcon, QStyle, QAction, QMenu
from PyQt5.QtGui import QPixmap, QIcon

from crypton import Crypton
from form_main import Ui_SocketChat
from ui_events import UI_Events

PASSWORD = "My Secret Word!"
HOST = '10.90.4.109'
PORT = 80

FIELD_STYLES = dict(
    asctime=dict(color='green'),
    hostname=dict(color='magenta'),
    levelname=dict(color='green'),
    filename=dict(color='magenta'),
    name=dict(color='yellow'),
    threadName=dict(color='green')
)

LEVEL_STYLES = dict(
    debug=dict(color='green'),
    info=dict(color='cyan'),
    verbose=dict(color='blue'),
    warning=dict(color='yellow'),
    error=dict(color='red'),
    critical=dict(color='red', bold=coloredlogs.CAN_USE_BOLD_FONT)
)

FORMAT = '[%(asctime)-15s] %(filename)s[%(process)d] : %(message)s'
logging.basicConfig(format=FORMAT)

LOGGER = logging.getLogger(__name__)
coloredlogs.install(
    fmt=FORMAT,
    level='DEBUG',
    logger=LOGGER,
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES,)

class SocketClient(object):
    """ Socket Client class """
    def __init__(self, *args, **kwargs):
        """ initialize class """
        self.is_connected = False
        self.is_handshake_done = False
        self.status = True
        self.sck = socket.socket()
        self.threads = []
        self.username = None

        if 'signals' in kwargs:
            self.signals = kwargs['signals']
        else:
            LOGGER.error('signal not defined!')
        
        if 'server' in kwargs:
            self.host_port = kwargs['server']
        else:
            LOGGER.error('server not defined!')

        if 'enc_pass' in kwargs:
            self._enc_pass = kwargs['enc_pass']
        else:
            LOGGER.error('enc_pass not defined!')

        self.kripton = Crypton(self._enc_pass)

    @property
    def enc_pass(self):
        """ return enc_pass value """
        return self._enc_pass

    @enc_pass.setter
    def enc_pass(self, x):
        """ set enc_pass value """
        self._enc_pass = x
        self.kripton = Crypton(self._enc_pass)

    def json_to_str(self, j_data):
        """ json data to string with crypton encryption """
        return self.kripton.crypt(json.dumps(j_data))

    def connect(self):
        """ start connection method """
        if not self.is_connected:
            try:
                self.sck = socket.socket()
                self.sck.settimeout(5)
                LOGGER.info('Connecting...')
                self.sck.connect(self.host_port)
            except ConnectionRefusedError:
                LOGGER.error('Connection Refused!')
                error_message = "Connection Refused!"
            except ConnectionAbortedError:
                LOGGER.error('Connection Aborted!')
                error_message = "Connection Aborted!"
            except ConnectionResetError:
                LOGGER.error('Connection Reset!')
                error_message = "Connection Reset!"
            except socket.timeout:
                LOGGER.error('Socket Timeout Error')
                error_message = "Socket Timeout Error!"
            except TimeoutError:
                LOGGER.error('Timeout Error')
                error_message = "Timeout Error!"
            else:
                self.sck.settimeout(None)
                self.is_connected = True
        else:
            LOGGER.info('Already Connected')

        if not self.is_connected:
            self.sck.close()
            self.signals.signal_show_dialog_box.emit('Error', error_message, 'c')
        else:
            self.status = True

    def set_username_thread(self):
        while not self.is_handshake_done:
            LOGGER.info('handshake not done')
            time.sleep(0.1)
        data = {'action': 'connect', 'username': self.username, 'message': ''}
        self.sck.send(self.json_to_str(data).encode('utf-8'))
        LOGGER.info('Username set')

    def set_username(self, username):
        """ request set username method """
        if self.is_connected:
            self.username = username

            uname_hs_t = threading.Thread(target=self.set_username_thread)
            self.threads.append(uname_hs_t)
            uname_hs_t.start()

            # data = {'action': 'connect', 'username': self.username, 'message': ''}
            # self.sck.send(self.json_to_str(data).encode('utf-8'))
            # LOGGER.info('Username set')

    def create_message(self, username, message, date_time):
        """ message create method """
        return '<span style="color: red; font-weight: bold; font-size: 10pt">[{0}]:</span>\
                <span style="font-size: 10pt">{1}</span>\
                <span style="font-size: 6pt">({2})</span>'\
                .format(username, message, date_time[1])

    def on_connect(self, user_data):
        """ connect response method """
        username = user_data['username']
        status = user_data['status']
        message = user_data['message']
        date_time = user_data['date_time']

        if username == 'server' and status:
            self.signals.signal_on_connect.emit()
            self.signals.signal_on_message.emit(self.create_message(username, message, date_time))
        elif username == 'server' and not status:
            self.signals.signal_on_message.emit(self.create_message(username, message, date_time))

    def on_disconnect(self, user_data):
        """ disconnect response method """
        username = user_data['username']
        status = user_data['status']
        message = user_data['message']
        date_time = user_data['date_time']

        if username == 'server' and status:
            self.signals.signal_on_disconnect.emit()
            self.signals.signal_on_message.emit(self.create_message(username, message, date_time))
            self.signals.signal_clear_user_list.emit()

        self.sck.shutdown(socket.SHUT_WR)
        self.sck.close()
        LOGGER.info('Disconnect oldum')
        return True

    def on_message(self, user_data):
        """ Message arrived event """
        username = user_data['username']
        message = user_data['message']
        date_time = user_data['date_time']

        self.signals.signal_on_message.emit(self.create_message(username, message, date_time))

    def on_user_list(self, user_data):
        """ user list response method """
        usernames = user_data['message']

        self.signals.signal_on_user_list.emit(usernames)

    def on_handshake(self, handshake_hash):
        """ handshake response method """
        LOGGER.info('Handshake : %s', handshake_hash)
        # LOGGER.info('Handshake geldi')
        if self.kripton.crypt('MERHABA') != handshake_hash:
            return False
        else:
            return True


    def listen(self):
        """ listen server """
        while self.status:
            LOGGER.info('Dinliyorum')

            try:
                data = self.sck.recv(1024).decode("utf-8")
            except (ConnectionError,\
                    ConnectionResetError,\
                    ConnectionRefusedError,\
                    ConnectionAbortedError) as ex:
                LOGGER.warning(ex)
                self.status = False
                self.is_connected = False
                self.sck.close()
                self.signals.signal_on_disconnect.emit()
                self.signals.signal_clear_user_list.emit()
                self.signals.signal_show_dialog_box.emit('Hata', 'Sunucu bağlantısı koptu', 'c')
                break
            else:
                if not data:
                    LOGGER.warning('No data available')
                    self.status = False
                    self.is_connected = False
                    self.sck.close()
                    self.signals.signal_on_disconnect.emit()
                    self.signals.signal_clear_user_list.emit()
                    self.signals.signal_show_dialog_box.emit('Hata', 'Sunucu bağlantısı koptu', 'c')
                    break
                else:
                    if data[:12] == '##HANDSHAKE:':
                        if not self.on_handshake(data[12:]):
                            self.status = False
                            self.is_connected = False
                            self.sck.close()
                            self.signals.signal_on_disconnect.emit()
                            self.signals.signal_clear_user_list.emit()
                            self.signals.signal_show_dialog_box.emit('Hata', \
                            'Güvenli bağlantı sağlanamadı!', 'c')
                        else:
                            self.is_handshake_done = True
                            continue

                    data = self.kripton.decrypt(data)
                    try:
                        j_data = json.loads(data)
                    except json.JSONDecodeError:
                        LOGGER.error('json data : %s', data)
                        LOGGER.error('JSON Error')
                        continue

                    action = j_data['action']

                    LOGGER.info(j_data)

                    if action == 'connect':
                        self.on_connect(j_data)
                    elif action == 'user_list':
                        self.on_user_list(j_data)
                    elif action == 'disconnect':
                        if self.on_disconnect(j_data):
                            self.is_connected = False
                            break
                    else:
                        self.on_message(j_data)

        self.sck.close()

    def talk(self, message):
        """ talk to server """
        if self.is_connected:
            LOGGER.info('message : %s', message)
            try:
                data = {'action': 'chat', 'username': self.username, 'message': message}
                self.sck.send(self.json_to_str(data).encode('utf-8'))
            except ConnectionRefusedError:
                LOGGER.warning('Connection Refused!')
            except ConnectionAbortedError:
                LOGGER.warning('Connection Aborted!')
            except ConnectionResetError:
                LOGGER.warning('Connection Reset!')
        else:
            LOGGER.error("Not Connected!")

    def disconnect(self):
        """ disconnect request to ui """
        if self.is_connected:
            LOGGER.info('%s request disconnect', self.username)
            try:
                data = {'action': 'disconnect', 'username': self.username, 'message': ''}
                self.sck.send(self.json_to_str(data).encode('utf-8'))
            except ConnectionRefusedError:
                LOGGER.warning('Connection Refused!')
            except ConnectionAbortedError:
                LOGGER.warning('Connection Aborted!')
            except ConnectionResetError:
                LOGGER.warning('Connection Reset!')
        else:
            LOGGER.error("Not Connected!")

    def start(self):
        """ start listen thread """
        if self.is_connected:

            self.sck.send('##HANDSHAKE:{0}'.format(self.kripton.crypt('MERHABA')).encode('utf-8'))

            listen_thread = threading.Thread(target=self.listen)
            self.threads.append(listen_thread)
            listen_thread.start()
            LOGGER.info("Dinleme başladı")

        else:
            LOGGER.error("Not Connected!")

    def stop(self):
        """ stop request client """
        LOGGER.warning('Stop çağırıldı.')
        self.disconnect()
        self.status = False
        # self.s.close()
        for i in self.threads:
            i.join()

        LOGGER.info('Finito!')

class Communicate(QObject):
    """ Communication class """

    signal_on_message = pyqtSignal(str)
    signal_on_connect = pyqtSignal()
    signal_on_disconnect = pyqtSignal()
    signal_on_user_list = pyqtSignal(object)
    signal_clear_user_list = pyqtSignal()
    signal_show_dialog_box = pyqtSignal(str, str, str)

    def __init__(self):
        QObject.__init__(self)

import resources_rc

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
        PASSWORD = j_settings['settings']['encryption']
        HOST = j_settings['settings']['server'][0]
        PORT = int(j_settings['settings']['server'][1])

    signals = Communicate()
    sck_client = SocketClient(server=(HOST, PORT), enc_pass=PASSWORD, signals=signals)
    events = UI_Events(app, qt_ui, sck_client, main_window, j_settings)

    signals.signal_on_message.connect(events.on_message)
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

    '''
        Define and add steps to work with the system tray icon
        show - show window
        hide - hide window
        exit - exit from application
    '''
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
        PASSWORD = sys.argv[1]

    main()
