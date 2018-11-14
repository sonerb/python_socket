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

logger = logging.getLogger(__name__)
coloredlogs.install(
    fmt=FORMAT, 
    level='DEBUG',
    logger=logger,
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES,)


HOST = ''
PORT = 80

BANNED_USERS = ['server', 'root', 'admin', 'administrator']

print_lock = threading.Lock()

class SocketServer(object):
    def __init__(self, *args, **kwargs):
        self.status = True
        self.connections = {}
        self.threads = []
        self.s = socket.socket() 
        self.host = HOST
        self.port = 12345
        if 'port' in kwargs:
            self.port = kwargs['port']

        self.s.settimeout(1.0)
        self.s.bind((self.host, self.port))
        logger.info("Server kuruldu: " + self.host + ":" + str(self.port))

    def json_to_str(self, j_data):
        return kripton.crypt(json.dumps(j_data))

    def send_user_list(self):
        users = []
        for key, val in self.connections.items():
            users.append( val['username'])

        data = {'action': 'user_list', 'username': 'server', 'message': users}

        for key, val in self.connections.items():
            val['c'].send(self.json_to_str(data).encode('utf-8'))
    
    def on_connect(self, id, user_socket, user_data):
        username = user_data['username']

        if username in BANNED_USERS:
            data = {'action': 'connect', 'username': 'server', 'message': 'Geçersiz kullanıcı adı girdiniz.', 'status': False}
            user_socket['c'].send(self.json_to_str(data).encode('utf-8'))
            return

        data = {'action': 'response', 'username': 'server', 'message': 'Hoşgeldiniz, {0}'.format(username)}
        
        self.connections[id]['username'] = username

        for u_id in self.connections:
            if u_id != id:
                self.connections[u_id]['c'].send(self.json_to_str(data).encode('utf-8'))
            else:
                data = {'action': 'connect', 'username': 'server', 'message': 'Hoşgeldiniz, {0}'.format(username), 'status': True}
                user_socket['c'].send(self.json_to_str(data).encode('utf-8'))
            
        self.send_user_list()

    def on_disconnect(self, id, user_socket, user_data):
        username = user_data['username']

        data = {'action': 'response', 'username': 'server', 'message': 'Güle güle, {0}'.format(username)}

        for u_id in self.connections:
            if u_id != id:
                self.connections[u_id]['c'].send(self.json_to_str(data).encode('utf-8'))
            else:
                data = {'action': 'disconnect', 'username': 'server', 'message': 'Güle güle, {0}'.format(username), 'status': True}
                user_socket['c'].send(self.json_to_str(data).encode('utf-8'))

        del self.connections[id]

        self.send_user_list()

    def on_chat(self, id, user_socket, user_data):
        username = user_data['username']
        message = user_data['message']
        
        data = {'action': 'response', 'username': username, 'message': message}

        for u_id in self.connections:
            self.connections[u_id]['c'].send(self.json_to_str(data).encode('utf-8'))

    def on_handshake(self, id, user_socket, hash):
        logger.info('Handshake : {0}'.format(hash))
        user_socket['c'].send('##HANDSHAKE:{0}'.format(kripton.crypt('MERHABA')).encode('utf-8'))

        if kripton.crypt('MERHABA') != hash:
            logger.error('Hash not match')
            return False
        else:
            return True


    def listen(self, id):
        while self.status :
            
            my_conn = self.connections[id]
            try:
                data = my_conn['c'].recv(1024).decode("utf-8")
            except Exception as e:
                logger.exception(e)
                my_conn['c'].shutdown(socket.SHUT_WR)
                my_conn['c'].close()
                del self.connections[id]
                break
            else:
                if len(data) == 0:
                    logger.warning('No data Available')
                    my_conn['c'].shutdown(socket.SHUT_WR)
                    my_conn['c'].close()
                    del self.connections[id]
                    break
                else:
                    if data[:12] == '##HANDSHAKE:':
                        self.on_handshake(id, my_conn, data[12:])
                        continue

                    data = kripton.decrypt(data)

                    logger.info("[{0}]: {1}".format(my_conn['addr'][0], data))

                    try:
                        j_data = json.loads(data)
                    except json.JSONDecodeError:
                        logger.error('JSON Error')
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
                self.s.listen(5)
                logger.info("Socket Dinleniyor...")
                c, addr = self.s.accept()

                logger.info('[i] {0}:{1} bağlandı.'.format(addr[0], addr[1]))

                gen_id = uuid.uuid4()
                new_conn = {'c': c, 'addr': addr, 'username': None}
                self.connections[gen_id] = new_conn

                t = threading.Thread(target=self.listen, args=(gen_id,))
                self.threads.append(t)
                t.start()

                logger.info("Thread Başlatıldı!")
            except IOError:
                continue
    
    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.wait_connection()

        # t = threading.Thread(target=self.wait_connection)
        # self.threads.append(t)
        # t.start()

    def stop(self):
        logger.warning('Stop çağırıldı.')
        self.status = False
        
        for k,v in self.connections.items():
            v['c'].shutdown(socket.SHUT_WR)

        for i in self.threads:
            i.join
        logger.info('Finito')

    def signal_handler(self, signal, frame):
        logger.warning('You pressed Ctrl+C!')
        self.stop()
        sys.exit()


def main():
    myServer = SocketServer(port=PORT)
    myServer.start()

if __name__ == '__main__':
    kripton = Crypton(PASSWORD)
    main()