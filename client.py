import socket
import threading
import json
import sys, time, signal
import logging, coloredlogs

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

from form_main import Ui_SocketChat
from ui_events import UI_Events

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

        # if 'username' not in kwargs:
        #     logger.error('[i] Kullanıcı adı tanımlanmadı.')
        # else:
        #     self.username = kwargs['username']

        if 'ui' not in kwargs:
            logger.error('UI not defined!')
        else:
            self.ui = kwargs['ui']
        

        if 'signals' not in kwargs:
            logger.error('signals not defined!')
        else:
            self.signals = kwargs['signals']


        # self.s.settimeout(1.0)
    
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

    def set_username(self, username):
        self.username = username
        data = {'action': 'connect', 'username': self.username, 'message': ''}
        self.s.send(json.dumps(data).encode('utf-8'))
        logger.info('Username set')

    # def show_dialog(self, txt):
    #     msg = QMessageBox()
    #     msg.setIcon(QMessageBox.Information)
    #     msg.setText(txt)
    #     msg.setWindowTitle("Dialog")
    #     msg.exec_()

    def on_connect(self, user_data):
        username = user_data['username']
        status = user_data['status']
        message = user_data['message']

        if username == 'server' and status:
            self.signals.signal_on_connect.emit()
            self.signals.signal_on_message.emit('[{0}]: {1}'.format(username, message))
        elif username == 'server' and not status:
            self.signals.signal_on_message.emit('[{0}]: {1}'.format(username, message))

    def on_disconnect(self, user_data):
        username = user_data['username']
        status = user_data['status']
        message = user_data['message']

        if username == 'server' and status:
            self.signals.signal_on_disconnect.emit()
            self.signals.signal_on_message.emit('[{0}]: {1}'.format(username, message))
    
        logger.info('Disconnect oldum')
        return True

    def on_message(self, user_data):
        username = user_data['username']
        message = user_data['message']

        self.signals.signal_on_message.emit('[{0}]: {1}'.format(username, message))

    def on_user_list(self, user_data):
        usernames = user_data['message']

        self.signals.signal_on_user_list.emit(usernames)

    def listen(self):
        while self.status :
            logger.info('Dinliyorum')
            # try:
            data = self.s.recv(1024).decode("utf-8")
            j_data = json.loads(data)
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

            # except IOError:
            #     continue
        self.s.close()

    def talk(self, message):
        if self.is_connected:
            logger.info('message : {0}'.format(message))
            try:
                data = {'action': 'chat', 'username': self.username, 'message': message}
                self.s.send(json.dumps(data).encode('utf-8'))
            except ConnectionRefusedError:
                logger.error('Connection Refused!')
            except ConnectionAbortedError:
                logger.error('Connection Aborted!')
            except ConnectionResetError:
                logger.error('Connection Reset!')
        else:
            logger.error("Not Connected!")

    def disconnect(self):
        if self.is_connected:
            logger.info('{} request disconnect'.format(self.username))
            try:
                data = {'action': 'disconnect', 'username': self.username, 'message': ''}
                self.s.send(json.dumps(data).encode('utf-8'))
            except ConnectionRefusedError:
                logger.error('Connection Refused!')
            except ConnectionAbortedError:
                logger.error('Connection Aborted!')
            except ConnectionResetError:
                logger.error('Connection Reset!')
        else:
            logger.error("Not Connected!")

    def start(self):
        if self.is_connected:
            t = threading.Thread(target=self.listen)
            self.threads.append(t)
            t.start()
            logger.info("Dinleme başladı")
            
            # t = threading.Thread(target=self.talk)
            # self.threads.append(t)
            # t.start()
            # logger.info("[i] Konuşuyorum...")

            # signal.signal(signal.SIGINT, self.signal_handler)

            # while True:
            #     time.sleep(1)
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

    def __init__(self):
        QObject.__init__(self)
    #     self._message = None
 
    # @property
    # def message(self):
    #     return self._message
 
    # @message.setter
    # def message(self, new_msg):
    #     self._message = new_msg
    #     self.signal_on_message.emit(new_msg)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_SocketChat()
    ui.setupUi(MainWindow)

    signals = Communicate()
    myClient = SocketClient(ui=ui, signals=signals)
    events = UI_Events(app, ui, myClient)


    signals.signal_on_message.connect(events.on_message)
    signals.signal_on_connect.connect(events.on_connect)
    signals.signal_on_disconnect.connect(events.on_disconnect)
    signals.signal_on_user_list.connect(events.on_user_list)

    ui.btn_connect.clicked.connect(events.btn_connect_clicked)
    ui.btn_disconnect.clicked.connect(events.btn_disconnect_clicked)

    ui.actionConnect.triggered.connect(events.btn_connect_clicked)
    ui.actionDisconnect.triggered.connect(events.btn_disconnect_clicked)
    ui.actionClose.triggered.connect(events.on_close)

    ui.btn_send.clicked.connect(events.btn_send_clicked)
    ui.txt_message.returnPressed.connect(events.txt_message_enter)

    ui.btn_disconnect.setVisible(False)
    ui.actionDisconnect.setVisible(False)

    ui.statusbar.showMessage('Disconnected')
    ui.txt_message.setReadOnly(True)
    
    MainWindow.closeEvent = events.closeEvent

    myClient.connect()

    MainWindow.show()
    sys.exit(app.exec_())

