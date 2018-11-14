__author__ = "Soner Bayram, Orhan Yılmaz"
__copyright__ = "Copyright 2018, The Socket Chat Program"
__credits__ = ["sonerb", "mafgom"]
__license__ = "GPL"
__version__ = "0.0.1"
__status__ = "Development"

import socket
import threading
import json
import sys, time, signal
import logging, coloredlogs

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QStandardItem

from form_main import Ui_SocketChat
from ui_events import UI_Events

from crypton import Crypton

PASSWORD = "My Secret Word!"

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

logger = logging.getLogger(__name__)
coloredlogs.install(
    fmt=FORMAT, 
    level='DEBUG',
    logger=logger,
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES,)


HOST = '10.90.4.109'
PORT = 80

lock = threading.Lock()

class SocketClient(object):
    def __init__(self, *args, **kwargs):
        self.is_connected = False
        self.status = True
        self.s = socket.socket()
        self.threads = []
        self.username = None

        if 'ui' not in kwargs:
            logger.error('UI not defined!')
        else:
            self.ui = kwargs['ui']

        if 'signals' not in kwargs:
            logger.error('signals not defined!')
        else:
            self.signals = kwargs['signals']


        # self.s.settimeout(1.0)
    def json_to_str(self, j_data):
        return kripton.crypt(json.dumps(j_data))

    def connect(self):
        if not self.is_connected:
            self.s = socket.socket()
            logger.info('Connecting...')
            try:
                self.s.connect((HOST, PORT))
                self.is_connected = True
            except ConnectionRefusedError:
                logger.error('Connection Refused!')
                self.is_connected = False
            except ConnectionAbortedError:
                logger.error('Connection Aborted!')
                self.is_connected = False
            except ConnectionResetError:
                logger.error('Connection Reset!')
                self.is_connected = False
        else:
            logger.info('Already Connected')
        
        if not self.is_connected:
            self.s.close()
            self.signals.signal_show_dialog_box.emit('Hata', 'Sunucuya erişilemedi!', 'c')
        else:
            self.status = True


    def set_username(self, username):
        if self.is_connected:
            self.username = username
            data = {'action': 'connect', 'username': self.username, 'message': ''}
            self.s.send(self.json_to_str(data).encode('utf-8'))
            logger.info('Username set')

    def create_message(self, username, message):
        return '<span style="color: red; font-weight: bold;">[{0}]:</span> <span class="message">{1}</span>'.format(username, message)

    def on_connect(self, user_data):
        username = user_data['username']
        status = user_data['status']
        message = user_data['message']

        if username == 'server' and status:
            self.signals.signal_on_connect.emit()
            self.signals.signal_on_message.emit(self.create_message(username, message))
        elif username == 'server' and not status:
            self.signals.signal_on_message.emit(self.create_message(username, message))

    def on_disconnect(self, user_data):
        username = user_data['username']
        status = user_data['status']
        message = user_data['message']

        if username == 'server' and status:
            self.signals.signal_on_disconnect.emit()
            self.signals.signal_on_message.emit(self.create_message(username, message))
            self.signals.signal_clear_user_list.emit()
    
        logger.info('Disconnect oldum')
        return True

    def on_message(self, user_data):
        username = user_data['username']
        message = user_data['message']

        self.signals.signal_on_message.emit(self.create_message(username, message))

    def on_user_list(self, user_data):
        usernames = user_data['message']

        self.signals.signal_on_user_list.emit(usernames)

    def on_handshake(self, hash):
        logger.info('Handshake : {0}'.format(hash))

        if kripton.crypt('MERHABA') != hash:
            return False
        else:
            return True


    def listen(self):
        while self.status :
            logger.info('Dinliyorum')
            
            try:
                data = self.s.recv(1024).decode("utf-8")
            except Exception as e:
                logger.exception(e)
                self.status = False
                self.is_connected = False
                self.s.close()
                self.signals.signal_on_disconnect.emit()
                self.signals.signal_clear_user_list.emit()
                self.signals.signal_show_dialog_box.emit('Hata', 'Sunucu bağlantısı koptu', 'c')
                break
            else:
                if len(data) == 0:
                    logger.warning('No data available')
                    self.status = False
                    self.is_connected = False
                    self.s.close()
                    self.signals.signal_on_disconnect.emit()
                    self.signals.signal_clear_user_list.emit()
                    self.signals.signal_show_dialog_box.emit('Hata', 'Sunucu bağlantısı koptu', 'c')
                    break
                else:
                    if data[:12] == '##HANDSHAKE:':
                        if not self.on_handshake(data[12:]):
                            self.status = False
                            self.is_connected = False
                            self.s.close()
                            self.signals.signal_on_disconnect.emit()
                            self.signals.signal_clear_user_list.emit()
                            self.signals.signal_show_dialog_box.emit('Hata', 'Güvenli bağlantı sağlanamadı!', 'c')
                        else:
                            continue

                    data = kripton.decrypt(data)
                    try:
                        j_data = json.loads(data)
                    except json.JSONDecodeError:
                        logger.error('JSON Error')
                        continue

                    action = j_data['action']

                    logger.info(j_data)

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

        self.s.close()

    def talk(self, message):
        if self.is_connected:
            logger.info('message : {0}'.format(message))
            try:
                data = {'action': 'chat', 'username': self.username, 'message': message}
                self.s.send(self.json_to_str(data).encode('utf-8'))
            except ConnectionRefusedError:
                logger.exception('Connection Refused!')
            except ConnectionAbortedError:
                logger.exception('Connection Aborted!')
            except ConnectionResetError:
                logger.exception('Connection Reset!')
        else:
            logger.error("Not Connected!")

    def disconnect(self):
        if self.is_connected:
            logger.info('{} request disconnect'.format(self.username))
            try:
                data = {'action': 'disconnect', 'username': self.username, 'message': ''}
                self.s.send(self.json_to_str(data).encode('utf-8'))
            except ConnectionRefusedError:
                logger.exception('Connection Refused!')
            except ConnectionAbortedError:
                logger.exception('Connection Aborted!')
            except ConnectionResetError:
                logger.exception('Connection Reset!')
        else:
            logger.error("Not Connected!")

    def start(self):
        if self.is_connected:

            self.s.send('##HANDSHAKE:{0}'.format(kripton.crypt('MERHABA')).encode('utf-8'))
            
            t = threading.Thread(target=self.listen)
            self.threads.append(t)
            t.start()
            logger.info("Dinleme başladı")
            
        else:
            logger.error("Not Connected!")
            
    def stop(self):
        logger.warning('Stop çağırıldı.')
        self.disconnect()
        self.status = False
        # self.s.close()
        for i in self.threads:
            i.join()

        logger.info('Finito!')

    def signal_handler(self, signal, frame):
        logger.warning('You pressed Ctrl+C!')
        self.stop()
        sys.exit()

class Communicate(QObject):

    signal_on_message = pyqtSignal(str)
    signal_on_connect = pyqtSignal()
    signal_on_disconnect = pyqtSignal()
    signal_on_user_list = pyqtSignal(object)
    signal_clear_user_list = pyqtSignal()
    signal_show_dialog_box = pyqtSignal(str, str, str)

    def __init__(self):
        QObject.__init__(self)

if __name__ == '__main__':

    if (len(sys.argv) > 1):
        PASSWORD = sys.argv[1]

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_SocketChat()
    ui.setupUi(MainWindow)
    kripton = Crypton(PASSWORD)

    signals = Communicate()
    myClient = SocketClient(ui=ui, signals=signals)
    events = UI_Events(app, ui, myClient, MainWindow)
    
    signals.signal_on_message.connect(events.on_message)
    signals.signal_on_connect.connect(events.on_connect)
    signals.signal_on_disconnect.connect(events.on_disconnect)
    signals.signal_on_user_list.connect(events.on_user_list)
    signals.signal_clear_user_list.connect(events.on_clear_user_list)
    signals.signal_show_dialog_box.connect(events.show_dialog_box)

    ui.btn_connect.clicked.connect(events.btn_connect_clicked)
    ui.btn_disconnect.clicked.connect(events.btn_disconnect_clicked)

    ui.actionConnect.triggered.connect(events.btn_connect_clicked)
    ui.actionDisconnect.triggered.connect(events.btn_disconnect_clicked)
    ui.actionClose.triggered.connect(events.on_close)

    ui.btn_send.clicked.connect(events.btn_send_clicked)
    ui.txt_message.returnPressed.connect(events.txt_message_enter)
    ui.txt_username.returnPressed.connect(events.txt_username_enter)

    ui.lst_users.doubleClicked.connect(events.lst_users_double_clicked)

    ui.btn_disconnect.setVisible(False)
    ui.actionDisconnect.setVisible(False)

    ui.statusbar.showMessage('Disconnected')
    ui.txt_message.setReadOnly(True)
    
    MainWindow.closeEvent = events.closeEvent

    MainWindow.show()
    sys.exit(app.exec_())

