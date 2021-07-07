import socket
import time
import json
from PySide2 import QtCore

"""
https://docs.python.org/3/howto/sockets.html
Data frame:
!ASCII length of data!json data
"""


class Communication(QtCore.QThread):
    new_data = QtCore.Signal(object)

    def __init__(self):
        QtCore.QThread.__init__(self, parent=None)
        print("comm.. init")
        self.port = 5678
        self.ip = ""
        self.is_server = False
        self.reconnect_server = False
        # socket for client or server socket for communication
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # socket for server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.is_connected = False
        self.running = True

    def set_ip(self, ip):
        self.ip = ip

    def make_connect(self):
        print("make_connect")
        self.s.connect((self.ip, self.port))
        self.is_server = False
        self.is_connected = True
        self.start()

    def make_server(self):
        print("make_server")
        self.server.bind(('', self.port))
        self.is_server = True
        self.reconnect_server = True
        self.start()

    def send_message(self, message):
        print("send_message")
        if self.is_connected:
            msg_json = json.dumps(message).encode()
            header = "!" + str(len(msg_json)) + "!"
            msg = b''.join([header.encode(), msg_json])
            self.s.send(msg)

    def get_message(self):
        print("get_message")
        data = self.s.recv(1).strip().decode("utf-8")
        if data == "!":
            data = self.s.recv(1).strip().decode("utf-8")
            length = 0
            while data != "!":
                length = length*10+int(data)
                data = self.s.recv(1).strip().decode("utf-8")
            try:
                data = json.loads(self.s.recv(length).strip().decode("utf-8"))
                self.new_data.emit(data)
            except ValueError:
                print("JSON error\n")

    def stop(self):
        print("comm...stop")
        if self.is_connected:
            self.is_connected = False
            self.s.close()
            if self.is_server:
                self.server.close()
        self.running = False

    def run(self):
        print("running....")
        while self.running:
            if self.is_server and self.reconnect_server:
                self.server.listen(1)
                self.s, addr = self.server.accept()
                self.reconnect_server = False
                self.is_connected = True
                print(addr)

            try:
                self.get_message()
                time.sleep(.05)
            except socket.error:
                self.reconnect_server = True
                self.is_connected = False

    def dissconect(self):
        self.s.close()
        self.server.close()

