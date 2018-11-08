import socket
import threading
import sys, signal, json, time
import uuid

print_lock = threading.Lock()

class SocketServer(object):
    def __init__(self, *args, **kwargs):
        self.stop = False
        self.connections = {}
        self.threads = []
        self.s = socket.socket() 
        self.host = ''
        self.port = 12345
        if 'port' in kwargs:
            self.port = kwargs['port']

        self.s.settimeout(1.0)
        self.s.bind((self.host, self.port))
        print("Server kuruldu: " + self.host + ":" + str(self.port))

    def listen(self, id):
        while True:
            try:
                my_conn = self.connections[id]
                msg = my_conn['c'].recv(1024).decode("utf-8")

                print("[{0}]: {1}".format(my_conn['addr'][0], msg))

                j_data = json.loads(msg)
                action = j_data['action']
                username = j_data['username']
                message = j_data['message']

                if action == 'connect':
                    data = {'action': 'response', 'username': 'server', 'message': 'Hoşgeldiniz, {0}'.format(username)}
                    self.connections[id]['username'] = username
                    for u_id in self.connections:
                        if u_id != id:
                            self.connections[u_id]['c'].send(json.dumps(data).encode('utf-8'))
                        else:
                            my_conn['c'].send(json.dumps(data).encode('utf-8'))
                            
                elif action == 'chat':
                    data = {'action': 'response', 'username': username, 'message': message}
                    for u_id in self.connections:
                        if u_id != id:
                            self.connections[u_id]['c'].send(json.dumps(data).encode('utf-8'))
            except ConnectionResetError:
                del self.connections[id]
                print("[i] {0} disconnected!".format(my_conn['username']))

    def wait_connection(self):
        while True:
            try:
                self.s.listen(5)
                print("Socket Dinleniyor...")
                c, addr = self.s.accept()

                print('[i] {0}:{1} bağlandı.'.format(addr[0], addr[1]))

                gen_id = uuid.uuid4()
                new_conn = {'c': c, 'addr': addr, 'username': None}
                self.connections[gen_id] = new_conn

                t = threading.Thread(target=self.listen, args=(gen_id,))
                self.threads.append(t)
                t.start()

                print("Thread Başlatıldı!")
            except IOError:
                continue
    
    def start(self):
        t = threading.Thread(target=self.wait_connection)
        self.threads.append(t)
        t.start()



def main():
    myServer = SocketServer(port=80)
    myServer.start()

if __name__ == '__main__':
    main()