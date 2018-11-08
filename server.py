import socket
import threading
import sys, signal, json, time

print_lock = threading.Lock()

class SocketServer(object):
    def __init__(self, *args, **kwargs):
        self.stop = False
        self.connections = []
        self.threads = []
        self.s = socket.socket() 
        self.host = ''
        self.port = 12345
        if 'port' in kwargs:
            self.port = kwargs['port']

        self.s.bind((self.host, self.port))
        print("Server kuruldu: " + self.host + ":" + str(self.port))

    def listen(self, conn):
        while True:
            msg = conn['c'].recv(1024).decode("utf-8")
            print("[{0}]: {1}".format(conn['addr'][0], msg))

            j_data = json.loads(msg)
            action = j_data['action']

            if action == 'connect':
                data = {'action': 'response', 'username': 'server', 'message': 'Hoşgeldiniz, {0}'.format(j_data['username'])}
                conn['c'].send(json.dumps(data).encode('utf-8'))
            elif action == 'chat':
                msg = j_data['message']
                data = {'action': 'response', 'username': j_data['username'] , 'message': msg}
                for u_conn in self.connections:
                    u_conn['c'].send(json.dumps(data).encode('utf-8'))

    def wait_connection(self):
        while True:
            self.s.listen(5)
            print("Socket Dinleniyor...")
            c, addr = self.s.accept()

            print('[i] {0}:{1} bağlandı.'.format(addr[0], addr[1]))

            new_conn = {'c': c, 'addr': addr}
            self.connections.append(new_conn)

            t = threading.Thread(target=self.listen, args=(new_conn,))
            self.threads.append(t)
            t.start()

            print("Thread Başlatıldı!")
    
    def start(self):
        t = threading.Thread(target=self.wait_connection)
        self.threads.append(t)
        t.start()



def main():
    myServer = SocketServer(port=80)
    myServer.start()

if __name__ == '__main__':
    main()