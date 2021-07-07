import socket
import pyautogui
import time
import _thread
import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QWidget, QPushButton, QApplication, QGridLayout, QVBoxLayout, QSystemTrayIcon, QMenu,
                             QAction)
from PySide2.QtCore import QThread, QObject, Signal, Slot

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP



screenWidth, screenHeight = pyautogui.size()
currentMouseX, currentMouseY = pyautogui.position()

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

localIP = "0.0.0.0"

UDPLocalPort = 1028
TCPLocalPort = 1029

bufferSize = 512
hostName = socket.gethostname()

print("Host name: " + hostName + ", IP: " + get_ip())


hostNameInBytes = str.encode(hostName)


# def init_udp_server():
#     # Create a datagram socket
#
#     UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#
#     # Bind to address and ip
#
#     UDPServerSocket.bind((localIP, UDPLocalPort))
#
#     print("UDP server up and listening")
#
#     # Listen for incoming datagrams
#     moveCount = 0
#     while (True):
#
#         try:
#
#             bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
#
#             print(len(bytesAddressPair))
#             message = bytesAddressPair[0]
#
#             address = bytesAddressPair[1]
#
#             clientMsg = "Message from Client:{}".format(message)
#             clientIP = "Client IP Address:{}".format(address)
#
#             print(clientMsg)
#             print(clientIP)
#
#             if message.startswith('getName'.encode()):
#                 UDPServerSocket.sendto(hostNameInBytes, address)
#
#             elif message.startswith('move'.encode()):
#
#                 start = time.time()
#                 stringMessage = message.decode()
#                 stringTokens = stringMessage.split(" ")
#                 xpos = int(stringTokens[1])
#                 ypos = int(stringTokens[2])
#                 currentMouseX, currentMouseY = pyautogui.position()
#
#                 nextMouseX = currentMouseX + xpos
#                 nextMouseY = currentMouseY + ypos
#
#                 nextMouseX = clamp(nextMouseX, 0, screenWidth)
#                 nextMouseY = clamp(nextMouseY, 0, screenHeight)
#
#                 pyautogui.moveTo(nextMouseX, nextMouseY, logScreenshot=False, _pause=False)
#                 end = time.time()
#                 print(end - start)
#
#             elif message.startswith('click'.encode()):
#                 print("Click....")
#                 pyautogui.click()
#
#             elif message.startswith('setText'.encode()):
#                 print("setText....")
#                 stringMessage = message.decode()
#                 stringTokens = stringMessage.split(" ")
#                 lastReceiveWord = stringTokens[1]
#
#         except Exception as err:
#             exception_type = type(err).__name__
#             print("ERROR UDP: ", exception_type)
#
# def init_tcp_server():
#     # Create a TCP/IP socket
#     TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#     # Bind the socket to the port
#     server_address = (localIP, 1029)
#     TCPServerSocket.bind(server_address)
#     TCPServerSocket.listen(1)
#     print("TCP server up and listening")
#
#     while True:
#         try:
#             connection, client_address = TCPServerSocket.accept()
#
#             print('connection from', client_address)
#
#             # Receive the data in small chunks and retransmit it
#             while True:
#                 data = connection.recv(16)
#                 print('received "%s"' % data)
#                 if data:
#                     print('sending data back to the client')
#                     # connection.sendall(hostNameInBytes)
#                     connection.sendto(hostNameInBytes, client_address)
#                 else:
#                     print('no more data from', client_address)
#                     break
#             # Clean up the connection
#             connection.close()
#             print("Connection close")
#
#         except Exception as err:
#             exception_type = type(err).__name__
#             print("ERROR: ", exception_type)


# try:
#     _thread.start_new_thread(init_udp_server, ())
#     _thread.start_new_thread(init_tcp_server, ())
#
# except:
#     print("Error TCP: unable to start thread")
# while 1:
#     pass
# init_udp_server()

class UDPWorker(QObject):

    finished = Signal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class

    def do_work(self):
        # Create a datagram socket

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Bind to address and ip

        self.UDPServerSocket.bind((localIP, UDPLocalPort))

        print("UDP server up and listening Qt")

        # Listen for incoming datagrams
        while self.continue_run:

            try:
                bytesAddressPair = self.UDPServerSocket.recvfrom(bufferSize)

                print(len(bytesAddressPair))
                message = bytesAddressPair[0]

                address = bytesAddressPair[1]

                clientMsg = "Message from Client:{}".format(message)
                clientIP = "Client IP Address:{}".format(address)

                print(clientMsg)
                print(clientIP)

                if message.startswith('getName'.encode()):
                    self.UDPServerSocket.sendto(hostNameInBytes, address)

                elif message.startswith('move'.encode()):

                    start = time.time()
                    stringMessage = message.decode()
                    stringTokens = stringMessage.split(" ")
                    xpos = int(stringTokens[1])
                    ypos = int(stringTokens[2])
                    currentMouseX, currentMouseY = pyautogui.position()

                    nextMouseX = currentMouseX + xpos
                    nextMouseY = currentMouseY + ypos

                    nextMouseX = clamp(nextMouseX, 0, screenWidth)
                    nextMouseY = clamp(nextMouseY, 0, screenHeight)

                    pyautogui.moveTo(nextMouseX, nextMouseY, logScreenshot=False, _pause=False)
                    end = time.time()
                    print(end - start)

                elif message.startswith('click'.encode()):
                    print("Click....")
                    pyautogui.click()

                elif message.startswith('setText'.encode()):
                    print("setText....")
                    stringMessage = message.decode()
                    stringTokens = stringMessage.split(" ")
                    lastReceiveWord = stringTokens[1]

            except Exception as err:
                exception_type = type(err).__name__
                print("ERROR UDP: ", exception_type)
        print("self.finished.emit()")
        self.finished.emit()

    def init_tcp_server(self):
        # Create a TCP/IP socket
        TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (localIP, 1029)
        TCPServerSocket.bind(server_address)
        TCPServerSocket.listen(1)
        print("TCP server up and listening")

        while self.continue_run:
            try:
                connection, client_address = TCPServerSocket.accept()

                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(16)
                    print('received "%s"' % data)
                    if data:
                        print('sending data back to the client')
                        # connection.sendall(hostNameInBytes)
                        connection.sendto(hostNameInBytes, client_address)
                    else:
                        print('no more data from', client_address)
                        break
                # Clean up the connection
                connection.close()
                print("Connection close")

            except Exception as err:
                exception_type = type(err).__name__
                print("ERROR: ", exception_type)

    @Slot()
    def stop(self):
        print("Close - Stop UDP")
        self.continue_run = False  # set the run condition to false on stop
        self.UDPServerSocket.close()


class TCPWorker(QObject):

    finished = Signal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class

    def do_work(self):
        # Create a TCP/IP socket
        self.TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (localIP, 1029)
        self.TCPServerSocket.bind(server_address)
        self.TCPServerSocket.listen(1)
        print("TCP server up and listening")

        while self.continue_run:
            try:
                connection, client_address = self.TCPServerSocket.accept()

                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(16)
                    print('received "%s"' % data)
                    if data:
                        print('sending data back to the client')
                        # connection.sendall(hostNameInBytes)
                        connection.sendto(hostNameInBytes, client_address)
                    else:
                        print('no more data from', client_address)
                        break
                # Clean up the connection
                connection.close()
                print("Connection close")

            except Exception as err:
                exception_type = type(err).__name__
                print("ERROR: ", exception_type)
        print("self.finished.emit()")
        self.finished.emit()

    @Slot()
    def stop(self):
        print("Close - Stop TCP")
        self.continue_run = False  # set the run condition to false on stop
        self.TCPServerSocket.close()


class Worker(QObject):

    finished = Signal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class

    def do_work(self):
        i = 1
        while self.continue_run:  # give the loop a stoppable condition
            print(i)
            QThread.sleep(1)
            i = i + 1
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop


class Gui(QObject):
    stop_signal = Signal()

    class Ducky(QObject):
        stop_signal = Signal()  # make a stop signal to communicate with the worker in another thread

    def __init__(self):
        super().__init__()
        # Thread:
        self.thread = QThread()
        self.tcp_thread = QThread()
        self.worker = UDPWorker()
        self.tcp_worker = TCPWorker()

        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.do_work)
        self.thread.finished.connect(self.worker.stop)
        self.thread.start()

        self.stop_signal.connect(self.tcp_worker.stop)  # connect stop signal to worker stop method
        self.tcp_worker.moveToThread(self.tcp_thread)

        self.tcp_worker.finished.connect(self.tcp_thread.quit)  # connect the workers finished signal to stop thread
        self.tcp_worker.finished.connect(
            self.tcp_worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.tcp_thread.finished.connect(
            self.tcp_thread.deleteLater)  # connect threads finished signal to clean up thread

        self.tcp_thread.start()
        self.tcp_thread.started.connect(self.tcp_worker.do_work)
        self.tcp_thread.finished.connect(self.tcp_worker.stop)

        self.initUI()

    def initUI(self):
        # Buttons:
        self.btn_start = QPushButton('Start')
        self.btn_start.resize(self.btn_start.sizeHint())
        self.btn_start.move(50, 50)
        self.btn_stop = QPushButton('Stop')
        self.btn_stop.resize(self.btn_stop.sizeHint())
        self.btn_stop.move(150, 50)
        #
        # # GUI title, size, etc...
        # self.setGeometry(300, 300, 300, 220)
        # self.setWindowTitle('Zank Remote Desktop')
        # self.layout = QGridLayout()
        # self.layout.addWidget(self.btn_start, 0, 0)
        # self.layout.addWidget(self.btn_stop, 0, 50)
        # self.setLayout(self.layout)
        #
        # # Start Button action:
        # self.btn_start.clicked.connect(self.start_server)
        #
        # # Stop Button action:
        # self.btn_stop.clicked.connect(self.stop_thread)
        #
        # self.show():


    # When stop_btn is clicked this runs. Terminates the worker and the thread.
    def stop_thread(self):
        print("Close - Stop stop_thread")
        self.stop_signal.emit()  # emit the finished signal on stop
        self.worker.stop()
        self.tcp_worker.stop()
        self.thread.quit()
        self.tcp_thread.quit()

    def check_thread(self):
        print("udp thread: " + str(self.thread.isRunning()) + ", " + str(self.thread.isFinished()))
        print("tcp thread: " + str(self.tcp_thread.isRunning()) + ", " + str(self.tcp_thread.isFinished()))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # sys.exit(app.exec_())

    app.setQuitOnLastWindowClosed(False)

    gui = Gui()
    # Create the icon
    icon = QIcon("10.jpg")

    # Create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # Create the menu
    menu = QMenu()
    show_ip_window = QAction("Show IP Address")
    menu.addAction(show_ip_window)

    # Create the menu
    show_ip_qr = QAction("Show IP QR code")
    menu.addAction(show_ip_qr)

    # Create the menu
    see_tutorials = QAction("Tutorials")
    menu.addAction(see_tutorials)

    # Create the menu
    restart = QAction("Restart")
    restart.triggered.connect(gui.check_thread)
    menu.addAction(restart)

    check_update = QAction("Check for updates")
    check_update.triggered.connect(app.quit)
    menu.addAction(check_update)

    # Add a Quit option to the menu.
    quit = QAction("Quit Zank Remote")
    quit.triggered.connect(gui.stop_thread)
    # quit.triggered.connect(app.quit)
    menu.addAction(quit)

    # Add the menu to the tray
    tray.setContextMenu(menu)

    # app.exec_()
    sys.exit(app.exec_())


