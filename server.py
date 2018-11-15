# -*- coding: utf-8 -*-
__author__ = "Soner Bayram, Orhan Yılmaz"
__copyright__ = "Copyright 2018, The Socket Chat Program"
__credits__ = ["sonerb", "mafgom"]
__license__ = "GPL"
__version__ = "0.0.1"
__status__ = "Development"

import socket
import threading
import sys, signal, json, time
import uuid
import logging, coloredlogs

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

LOGGER = logging.getLogger(__name__)
coloredlogs.install(
    fmt=FORMAT, 
    level='DEBUG',
    logger=LOGGER,
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES,)


HOST = ''
PORT = 80

BANNED_USERS = ['server', 'root', 'admin', 'administrator']

class SocketServer(object):
    def __init__(self, *args, **kwargs):
        self.status = True
        self.connections = {}
        self.threads = []
        self.sck = socket.socket() 
        self.host = HOST
        self.port = 12345
        if 'port' in kwargs:
            self.port = kwargs['port']

        self.sck.settimeout(1.0)
        self.sck.bind((self.host, self.port))
        LOGGER.info("Server kuruldu: " + self.host + ":" + str(self.port))

    def json_to_str(self, j_data):
        return kripton.crypt(json.dumps(j_data))

    def get_date_time(self):
        """ return to current date time object """
        local_time = time.localtime()
        t_str_date  = time.strftime("%d/%m/%Y", local_time)
        t_str_time  = time.strftime("%H:%M", local_time)
        return [t_str_date, t_str_time]

    def send_user_list(self):
        users = []
        for key, val in self.connections.items():
            users.append( val['username'])

        data = {'action': 'user_list', 'username': 'server', 'message': users, 'date_time': self.get_date_time()}

        for key, val in self.connections.items():
            val['c'].send(self.json_to_str(data).encode('utf-8'))
    
    def on_connect(self, id, user_socket, user_data):
        username = user_data['username']

        if username in BANNED_USERS:
            data = {'action': 'connect', 'username': 'server', 'message': 'Geçersiz kullanıcı adı girdiniz.', 'date_time': self.get_date_time(), 'status': False}
            user_socket['c'].send(self.json_to_str(data).encode('utf-8'))
            return

        data = {'action': 'response', 'username': 'server', 'message': 'Hoşgeldiniz, {0}'.format(username), 'date_time': self.get_date_time()}
        
        self.connections[id]['username'] = username

        for u_id in self.connections:
            if u_id != id:
                self.connections[u_id]['c'].send(self.json_to_str(data).encode('utf-8'))
            else:
                data = {'action': 'connect', 'username': 'server', 'message': 'Hoşgeldiniz, {0}'.format(username), 'date_time': self.get_date_time(), 'status': True}
                user_socket['c'].send(self.json_to_str(data).encode('utf-8'))
        
        time.sleep(0.1)
        self.send_user_list()

    def on_disconnect(self, id, user_socket, user_data):
        username = user_data['username']

        data = {'action': 'response', 'username': 'server', 'message': 'Güle güle, {0}'.format(username), 'date_time': self.get_date_time()}

        for u_id in self.connections:
            if u_id != id:
                self.connections[u_id]['c'].send(self.json_to_str(data).encode('utf-8'))
            else:
                data = {'action': 'disconnect', 'username': 'server', 'message': 'Güle güle, {0}'.format(username), 'date_time': self.get_date_time(), 'status': True}
                user_socket['c'].send(self.json_to_str(data).encode('utf-8'))

        # self.connections[id]['c'].shutdown(socket.SHUT_WR)
        # self.connections[id]['c'].close()
        del self.connections[id]
    
        LOGGER.info('%s kullanıcısı silindi', id)

        self.send_user_list()

    def on_chat(self, id, user_socket, user_data):
        """ send chat message to all client """ 
        username = user_data['username']
        message = user_data['message']
       
        data = {'action': 'response', 'username': username, 'message': message, 'date_time': self.get_date_time()}

        for u_id in self.connections:
            self.connections[u_id]['c'].send(self.json_to_str(data).encode('utf-8'))

    def on_handshake(self, id, user_socket, hash):
        LOGGER.info('Handshake : {0}'.format(hash))
        # LOGGER.info('Handshake geldi!')
        user_socket['c'].send('##HANDSHAKE:{0}'.format(kripton.crypt('MERHABA')).encode('utf-8'))

        if kripton.crypt('MERHABA') != hash:
            LOGGER.error('Hash not match')
            return False
        else:
            return True


    def listen(self, id):
        while self.status :
            
            my_conn = self.connections[id]
            try:
                data = my_conn['c'].recv(1024).decode("utf-8")
            except (ConnectionError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as e:
                LOGGER.warning(e)
                my_conn['c'].shutdown(socket.SHUT_WR)
                my_conn['c'].close()
                del self.connections[id]
                break
            else:
                if not data:
                    LOGGER.warning('No data Available')
                    my_conn['c'].shutdown(socket.SHUT_WR)
                    my_conn['c'].close()
                    del self.connections[id]
                    break
                else:
                    if data[:12] == '##HANDSHAKE:':
                        self.on_handshake(id, my_conn, data[12:])
                        continue

                    data = kripton.decrypt(data)

                    LOGGER.info("[{0}]: {1}".format(my_conn['addr'][0], data))

                    try:
                        j_data = json.loads(data)
                    except json.JSONDecodeError:
                        LOGGER.error('json data : %s', data)
                        LOGGER.error('JSON Error')
                        continue

                    action = j_data['action']

                    if action == 'connect':
                        self.on_connect(id, my_conn, j_data)
                    elif action == 'disconnect':
                        self.on_disconnect(id, my_conn, j_data)
                        break
                    elif action == 'chat':
                        self.on_chat(id, my_conn, j_data)

    def wait_connection(self):
        while self.status :
            try:
                self.sck.listen(5)
                LOGGER.info("Socket Dinleniyor...")
                c, addr = self.sck.accept()

                LOGGER.info('[i] {0}:{1} bağlandı.'.format(addr[0], addr[1]))

                gen_id = uuid.uuid4()
                new_conn = {'c': c, 'addr': addr, 'username': None}
                self.connections[gen_id] = new_conn

                t = threading.Thread(target=self.listen, args=(gen_id,))
                self.threads.append(t)
                t.start()

                LOGGER.info("Thread Başlatıldı!")
            except IOError:
                continue
    
    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.wait_connection()

        # t = threading.Thread(target=self.wait_connection)
        # self.threads.append(t)
        # t.start()

    def stop(self):
        LOGGER.warning('Stop çağırıldı.')
        self.status = False
        
        for k,v in self.connections.items():
            v['c'].shutdown(socket.SHUT_WR)

        for i in self.threads:
            i.join
        LOGGER.info('Finito')

    def signal_handler(self, signal, frame):
        LOGGER.warning('You pressed Ctrl+C!')
        self.stop()
        sys.exit()


def main():
    myServer = SocketServer(port=PORT)
    myServer.start()

if __name__ == '__main__':
    kripton = Crypton(PASSWORD)
    main()