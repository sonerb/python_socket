import json
import logging
import socket
import threading
import time
import queue

import coloredlogs

from crypton import Crypton

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

        self.user_chat_queue = dict()

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
        data = {'action': 'connect', 'username': self.username}
        self.sck.send(self.json_to_str(data).encode('utf-8'))
        LOGGER.info('Username set')

    def set_username(self, username):
        """ request set username method """
        if self.is_connected:
            self.username = username

            uname_hs_t = threading.Thread(target=self.set_username_thread)
            self.threads.append(uname_hs_t)
            uname_hs_t.start()

    def create_message(self, username, message, date_time):
        """ message create method """
        return '<span style="color: red; font-weight: bold; font-size: 10pt">[{0}]:</span>\
                <span style="font-size: 10pt">{1}</span>\
                <span style="font-size: 6pt">({2})</span>'\
                .format(username, message, date_time[1])

    def on_connect(self, user_data):
        """ connect response method """
        m_from = user_data['from']
        m_status = user_data['status']
        m_message = user_data['message']
        m_date_time = user_data['date_time']

        if m_from == 'server' and m_status:
            self.signals.signal_on_connect.emit()
            self.signals.signal_on_message.emit(self.create_message(m_from, m_message, m_date_time))
        elif m_from == 'server' and not m_status:
            self.signals.signal_on_message.emit(self.create_message(m_from, m_message, m_date_time))

    def on_disconnect(self, user_data):
        """ disconnect response method """
        m_from = user_data['from']
        m_status = user_data['status']
        m_message = user_data['message']
        m_date_time = user_data['date_time']

        if m_from == 'server' and m_status:
            self.signals.signal_on_disconnect.emit()
            self.signals.signal_on_message.emit(self.create_message(m_from, m_message, m_date_time))
            self.signals.signal_clear_user_list.emit()

        self.sck.shutdown(socket.SHUT_WR)
        self.sck.close()
        LOGGER.info('Disconnect oldum')
        return True

    def on_message(self, user_data):
        """ Message arrived event """
        m_from = user_data['from']
        m_message = user_data['message']
        m_date_time = user_data['date_time']

        self.signals.signal_on_message.emit(self.create_message(m_from, m_message, m_date_time))

    def on_pm_message(self, user_data):
        """ PM Message arrived event """
        m_from = user_data['from']
        m_to = user_data['to']
        m_message = user_data['message']
        m_date_time = user_data['date_time']
        
        # if m_from == self.username:
        self.signals.signal_on_pm_message.emit(self.create_message(m_from, m_message, m_date_time), m_from, m_to)
        # else:
        #     self.signals.signal_on_pm_message.emit(self.create_message(m_from, m_message, m_date_time), m_from, m_to)
        

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
                    elif action == 'gm':
                        self.on_message(j_data)
                    elif action == 'pm':
                        self.on_pm_message(j_data)
                    else:
                        LOGGER.warning('Undefied action type')

        self.sck.close()

    def talk(self, message, to='server'):
        """ talk to server """
        if self.is_connected:
            LOGGER.info('message : %s', message)
            try:
                data = {'action': 'chat', 'from': self.username, 'to': to, 'message': message}
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
                data = {'action': 'disconnect', 'username': self.username}
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