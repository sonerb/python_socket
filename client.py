import socket
import threading
import json
import sys, time, signal

HOST = ''
PORT = 80

lock = threading.Lock()

class SocketClient(object):
    def __init__(self, *args, **kwargs):
        self.stop = False
        self.s = socket.socket()
        self.threads = []
        if 'username' not in kwargs:
            print('[i] Kullanıcı adı tanımlanmadı.')
        else:
            self.username = kwargs['username']

        self.s.connect((HOST, PORT))

        data = {'action': 'connect', 'username': self.username, 'message': ''}
        self.s.send(json.dumps(data).encode('utf-8'))

    def listen(self):
        while not self.stop:
            data = self.s.recv(1024).decode("utf-8")
            j_data = json.loads(data)
            with lock:
                print('\r[{0}]: {1}\n\r[->]: '.format(j_data['username'], j_data['message']), end='', flush=True)

    
    def talk(self):
        while not self.stop:
            msg = input('')
            data = {'action': 'chat', 'username': self.username, 'message': msg}
            self.s.send(json.dumps(data).encode('utf-8'))

    def start(self):
        t = threading.Thread(target=self.listen)
        self.threads.append(t)
        t.start()
        print("[i] Dinliyorum")
        
        t = threading.Thread(target=self.talk)
        self.threads.append(t)
        t.start()
        print("[i] Konuşuyorum...")


def main(uname):
    myClient = SocketClient(username=uname)
    myClient.start()

if __name__ == '__main__':
    main(sys.argv[1])
