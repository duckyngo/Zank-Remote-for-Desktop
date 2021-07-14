import socket
import time
import pyautogui
from PySide2.QtCore import QThread, Signal, QThreadPool, QRunnable

import utils

screenWidth, screenHeight = pyautogui.size()
currentMouseX, currentMouseY = pyautogui.position()

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

localIP = "0.0.0.0"

UDPLocalPort = 1028
TCPLocalPort = 1029
hostName = utils.get_computer_host_name()
bufferSize = 4080
hostIP = utils.get_ip()

isRunning = False

print("Host name: " + hostName + ", IP: " + hostIP)

hostNameInBytes = str.encode(hostName)


class Runnable(QRunnable):

    def __init__(self, xpos, ypos):
        super().__init__()
        self.xpos = xpos
        self.ypos = ypos
        self.isFinished = False

    def run(self):
        start = time.time()
        pyautogui.moveRel(self.xpos, self.ypos, logScreenshot=False, _pause=False)
        self.isFinished = True

        end = time.time()
        print("Runnable time: ", end - start)


class TCPCommunication(QThread):
    new_data = Signal(object)

    def __init__(self):
        QThread.__init__(self, parent=None)
        print("comm.. init")
        self.port = 9200
        self.ip = "0.0.0.0"
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
            # msg_json = json.dumps(message).encode()
            msg_json = "fff"
            header = "!" + str(len(msg_json)) + "!"
            msg = b''.join([header.encode(), msg_json])
            self.s.send(msg)

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

            try:
                self.server.listen(1)
                self.s, addr = self.server.accept()
                self.reconnect_server = False
                self.is_connected = True
                print(addr)

                data = self.s.recv(1024).strip().decode("utf-8")
                print("Get: ", data)

            except Exception as err:
                exception_type = type(err).__name__
                print("ERROR UDP: ", exception_type)

    def dissconect(self):
        self.s.close()
        self.server.close()


class UDPCommunication(QThread):
    keyboard_new_event = Signal(object)
    keyboard_final_event = Signal(object)
    volume_event = Signal(object)
    mouse_move_event = Signal(object)
    mouse_click_event = Signal(object)
    mouse_scroll_event = Signal(object)

    def __init__(self):
        QThread.__init__(self, parent=None)
        print("comm.. init")
        self.port = 1028
        self.ip = "0.0.0.0"
        self.is_server = False
        self.reconnect_server = False
        # socket for client or server socket for communication
        # self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # socket for server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.is_connected = False
        self.running = True
        self.runnable = None
        self.count = 0
        self.last_move_time = 0
        self.threadpool = QThreadPool()
        self.threadpool.setExpiryTimeout(300)
        self.threadpool.setMaxThreadCount(50)
        print("Max Thread Pool Count: ", self.threadpool.maxThreadCount())
        self.host_ip = utils.get_ip()
        self.host_name = socket.gethostname()
        self.host_name_in_bytes = str.encode(self.host_name + " - " + self.host_ip)


    def set_ip(self, ip):
        self.ip = ip

    def make_connect(self):
        print("UDP make_connect...")
        self.s.connect((self.ip, self.port))
        self.is_server = False
        self.is_connected = True
        self.start()

    def make_server(self):
        print("UDP make_server...")
        self.server.bind((self.ip, self.port))
        self.is_server = True
        self.reconnect_server = True
        self.start()

    def send_message(self, message):
        print("send_messsage udp")
        if self.is_connected:
            # msg_json = json.dumps(message).encode()
            msg_json = "fff"
            header = "!" + str(len(msg_json)) + "!"
            msg = b''.join([header.encode(), msg_json])
            self.s.sendall(msg)

    def stop(self):
        print("UDP stop...")
        if self.is_connected:
            self.is_connected = False
            self.s.close()
            if self.is_server:
                self.server.close()
        self.running = False

    def run(self):
        print("UDP running...")
        while self.running:
            # try:
                bytes_address_pair = self.server.recvfrom(1028)
                message, address = bytes_address_pair[0], bytes_address_pair[1]

                clientMsg = "Message from Client:{}".format(message)
                clientIP = "Client IP Address:{}".format(address)

                print(clientMsg)
                print(clientIP)

                if message.startswith('getName'.encode()):
                    self.server.sendto(hostNameInBytes, address)

                elif message.startswith('move'.encode()):

                    start = time.time()
                    string_message = message.decode()

                    now = time.time()
                    if now - self.last_move_time > 0.02:
                        self.mouse_move_event.emit(string_message)
                        self.last_move_time = now

                    # if self.runnable is None or self.runnable.isFinished:
                    #     self.count = 0
                    #     self.runnable = Runnable(xpos, ypos)
                    #     self.threadpool.start(self.runnable, priority=QThread.Priority.HighestPriority)
                    # else:
                    #     self.count += 1
                    #     print("isRunning True, Count: ", self.count, "ActiveCount: ", self.threadpool.activeThreadCount())
                    #     if self.count > 3:
                    #         self.threadpool.clear()
                    #         self.runnable = None

                    end = time.time()
                    print(end - start)

                elif message.startswith('click'.encode()):
                    print("Click....")
                    self.mouse_click_event.emit("click")

                elif message.startswith('setText '.encode()):
                    string_message = message.decode()
                    print("setText....", string_message)
                    last_receive_word = string_message[len("setText "):]
                    print(last_receive_word)
                    self.keyboard_new_event.emit(last_receive_word)

                elif message.startswith('setFinalText '.encode()):
                    string_message = message.decode()
                    print("setFinalText....", string_message)
                    last_receive_word = string_message[len("setFinalText "):]
                    print(last_receive_word)
                    self.keyboard_final_event.emit(last_receive_word)

                elif message == 'scrollUp'.encode():
                    pyautogui.scroll(30)

                elif message == 'scrollDown'.encode():
                    pyautogui.scroll(-30)

                elif message == 'pageRight'.encode():
                    pyautogui.hscroll(10)

                elif message == 'pageLeft'.encode():
                    pyautogui.hscroll(-10)

                elif message == 'pageUp'.encode():
                    pyautogui.scroll(100)

                elif message == 'pageDown'.encode():
                    pyautogui.scroll(-100)

                elif message == 'volumeUp'.encode()\
                        or message == 'volumeDown'.encode()\
                        or message == 'volumeMute'.encode():
                    print("volume", message)
                    self.volume_event.emit(message.decode())

                elif message == 'hideMouse'.encode():
                    print("hideMouse")





        # except Exception as err:a a a a
            #     exception_type = type(err).__name__
            #     print("ERROR UDP: ", exception_type, err)

    def dissconect(self):
        self.server.close()
