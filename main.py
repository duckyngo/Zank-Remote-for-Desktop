import os
import socket
from enum import Enum
from functools import partial

import pyautogui
import time
import _thread
import sys

from PyQt5.QtGui import QIcon, QPalette, QPixmap, QImage, QCursor, QFont
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QGridLayout, QVBoxLayout, QSystemTrayIcon, QMenu,
                             QAction, QHBoxLayout, QLabel, QSizePolicy)
from PyQt5.QtCore import QThread, QObject, pyqtSignal

import qrcode
from PIL import Image
from PyQt5.QtCore import Qt

from PIL import Image

import plistlib
from sys import platform


class FlatformName(Enum):
    WINDOW = 1
    MACOS = 2
    LINUX = 3


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


def get_platform_type():
    if platform == "linux" or platform == "linux2":
        return FlatformName.LINUX
    elif platform == "darwin":
        return FlatformName.MACOS
    elif platform == "win32":
        return FlatformName.WINDOW


def generate_qr_code():
    # taking image which user wants
    # in the QR code center
    logo_link = 'app_icon.png'

    logo = Image.open(logo_link)

    # taking base width
    basewidth = 100

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    # taking url or text
    url = hostIP

    # addingg URL or text to QRcode
    QRcode.add_data(url)

    # generating QR code
    QRcode.make()

    # taking color name from user
    QRcolor = 'Black'

    # adding color to QR code
    QRimg = QRcode.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
           (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)

    return QRimg


def pil2pixmap(im):
    if im.mode == "RGB":
        pass
    elif im.mode == "L":
        im = im.convert("RGBA")
    data = im.convert("RGBA").tobytes()
    qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qim)
    return pixmap


screenWidth, screenHeight = pyautogui.size()
currentMouseX, currentMouseY = pyautogui.position()

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

localIP = "0.0.0.0"

UDPLocalPort = 1028
TCPLocalPort = 1029

bufferSize = 4080
hostName = socket.gethostname()
hostIP = get_ip()

print("Host name: " + hostName + ", IP: " + hostIP)

hostNameInBytes = str.encode(hostName)


class UDPWorker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class

    def do_work(self):
        # Create a datagram socket

        udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Bind to address and ip

        udp_server_socket.bind((localIP, UDPLocalPort))

        print("UDP server up and listening Qt")

        # Listen for incoming datagrams
        while self.continue_run:

            try:
                bytes_address_pair = udp_server_socket.recvfrom(bufferSize)

                print(len(bytes_address_pair))
                message = bytes_address_pair[0]

                address = bytes_address_pair[1]

                clientMsg = "Message from Client:{}".format(message)
                clientIP = "Client IP Address:{}".format(address)

                print(clientMsg)
                print(clientIP)

                if message.startswith('getName'.encode()):
                    udp_server_socket.sendto(hostNameInBytes, address)

                elif message.startswith('move'.encode()):

                    start = time.time()
                    string_message = message.decode()
                    string_tokens = string_message.split(" ")
                    xpos = int(string_tokens[1])
                    ypos = int(string_tokens[2])
                    current_mouse_x, current_mouse_y = pyautogui.position()

                    next_mouse_x = current_mouse_x + xpos
                    next_mouse_y = current_mouse_y + ypos

                    next_mouse_x = clamp(next_mouse_x, 0, screenWidth)
                    next_mouse_y = clamp(next_mouse_y, 0, screenHeight)

                    pyautogui.moveTo(next_mouse_x, next_mouse_y, logScreenshot=False, _pause=False)
                    end = time.time()
                    print(end - start)

                elif message.startswith('click'.encode()):
                    print("Click....")
                    pyautogui.click()

                elif message.startswith('setText'.encode()):
                    print("setText....")
                    string_message = message.decode()
                    string_tokens = string_message.split(" ")
                    lastReceiveWord = string_tokens[1]

            except Exception as err:
                exception_type = type(err).__name__
                print("ERROR UDP: ", exception_type)
        self.finished.emit()

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop


class TCPWorker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class

    def do_work(self):
        # Create a TCP/IP socket
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (localIP, 1029)
        tcp_server_socket.bind(server_address)
        tcp_server_socket.listen(1)
        print("TCP server up and listening")

        while self.continue_run:
            # try:
            connection, client_address = tcp_server_socket.accept()

            print('connection from', client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(bufferSize)
                print('received "%s"' % data)
                if data:

                    message_string = data.decode()
                    print("message: " + message_string + ", " + message_string.strip())
                    message_string = message_string.strip()

                    if message_string.__contains__("getAppList"):
                        print("getAppList")
                        connection.close()

                    elif message_string.startswith("getAppIcon"):
                        print("getAppIcon")
                        connection.close()

                    elif message_string.startswith("openLink"):
                        print("openLink")
                        connection.close()
                    else:
                        connection.close()

                    # print('sending data back to the client')
                    # # connection.sendall(hostNameInBytes)
                    # connection.sendto(hostNameInBytes, client_address)
                else:
                    print('no more data from', client_address)
                    connection.close()
                    break
            # Clean up the connection
            # connection.close()
            # print("Connection close")

        # except Exception as err:
        #     exception_type = type(err).__name__
        #     print("ERROR: ", exception_type)
        self.finished.emit()

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop


class ShowIPText(QWidget):

    def __init__(self):
        super().__init__()

        # Buttons:

        self.title_lable = QLabel('Your computer IP address is: ', self)
        self.title_lable.setFont(QFont('Arial', 16))
        self.title_lable.setAlignment(Qt.AlignCenter)

        self.ip_label = QLabel(hostIP, self)
        self.ip_label.setFont(QFont('Arial', 24))
        self.ip_label.setAlignment(Qt.AlignCenter)
        self.ip_label.setContentsMargins(10, 40, 20, 10)

        qr_image = generate_qr_code()
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContentsMargins(10, 30, 10, 30)
        self.imageLabel.setPixmap(pil2pixmap(qr_image))

        self.btn_stop = QPushButton('Done')
        self.btn_stop.resize(self.btn_stop.sizeHint())
        self.btn_stop.move(150, 50)

        # GUI title, size, etc...
        self.setWindowTitle('Zank Remote Desktop')
        self.ip_layout = QVBoxLayout()
        self.ip_layout.addWidget(self.title_lable)
        self.ip_layout.addWidget(self.ip_label)
        self.ip_layout.addWidget(self.imageLabel)
        self.ip_layout.addWidget(self.btn_stop)
        self.setLayout(self.ip_layout)

        self.btn_stop.clicked.connect(self.closeEvent)

    def show_ip_window(self):
        self.show()


class Gui(QWidget):
    stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

    def __init__(self):
        super().__init__()
        # Thread:
        self.thread = QThread()
        self.tcp_thread = QThread()
        self.worker = UDPWorker()
        self.tcp_worker = TCPWorker()

        # self.initUI()

    def initUI(self):
        # Buttons:
        self.btn_start = QPushButton('Start')
        self.btn_start.resize(self.btn_start.sizeHint())
        self.btn_start.move(50, 50)
        self.btn_stop = QPushButton('Stop')
        self.btn_stop.resize(self.btn_stop.sizeHint())
        self.btn_stop.move(150, 50)

        # GUI title, size, etc...
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Zank Remote Desktop')
        self.layout = QGridLayout()
        self.layout.addWidget(self.btn_start, 0, 0)
        self.layout.addWidget(self.btn_stop, 0, 50)
        self.setLayout(self.layout)

        # Start Button action:
        self.btn_start.clicked.connect(self.start_server)

        # Stop Button action:
        self.btn_stop.clicked.connect(self.stop_thread)

        self.show()

    def start_server(self):
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

        self.tcp_thread.started.connect(self.tcp_worker.do_work)
        self.tcp_thread.finished.connect(self.tcp_worker.stop)
        self.tcp_thread.start()

    # When stop_btn is clicked this runs. Terminates the worker and the thread.
    def stop_thread(self):
        print("Stop signal emit")
        self.stop_signal.emit()  # emit the finished signal on stop


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Set app icon
    app_icon = QIcon("app_icon.png")
    app.setWindowIcon(app_icon)

    gui = Gui()
    show_ip = ShowIPText()

    gui.start_server()

    # Create the icon
    icon = QIcon("app_icon.png")

    # Create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # Create the menu
    menu = QMenu()

    see_tutorials = QAction("Tutorials")
    menu.addAction(see_tutorials)

    show_ip_window = QAction("Show IP Address")
    show_ip_window.triggered.connect(show_ip.show_ip_window)
    menu.addAction(show_ip_window)

    restart = QAction("Restart")
    menu.addAction(restart)

    control_panel = QAction("Control Panels")
    control_panel.triggered.connect(gui.initUI)
    menu.addAction(control_panel)

    # Add a Quit option to the menu.
    quit = QAction("Quit Zank Remote")
    quit.triggered.connect(gui.stop_thread)
    quit.triggered.connect(app.quit)
    menu.addAction(quit)

    # Add the menu to the tray
    tray.setContextMenu(menu)

    # app.exec_()
    sys.exit(app.exec_())
