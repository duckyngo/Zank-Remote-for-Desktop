import socket
from enum import Enum

import pyautogui
import time
import sys

from PyQt5.QtGui import QIcon, QPalette, QPixmap, QImage, QCursor, QFont
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QGridLayout, QVBoxLayout, QSystemTrayIcon, QMenu,
                             QAction, QHBoxLayout, QLabel, QSizePolicy, QTabWidget, QMainWindow)
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

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
    logo_link = 'app_icon_rgb.jpg'

    logo = Image.open(logo_link)

    # taking base width
    basewidth = 70

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
    QRimg = QRcode.make_image().convert('RGB')

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
           (QRimg.size[1] - logo.size[1]) // 2)

    QRimg.paste(logo, pos)

    return QRimg


def pil2pixmap(im):
    if im.mode == "RGB":
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
    elif im.mode == "RGBA":
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")

    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
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


class ShowIPWindow(QWidget):

    def __init__(self):
        super().__init__()

        # Buttons:

        self.title_lable = QLabel('Your computer IP address is: ', self)
        self.title_label_font = QFont('Arial', 16)
        self.title_label_font.setBold(True)
        self.title_lable.setFont(self.title_label_font)
        self.title_lable.setAlignment(Qt.AlignCenter)

        self.ip_label = QLabel(hostIP, self)
        self.ip_label_font = QFont('Arial', 26)
        self.ip_label_font.setBold(True)
        self.ip_label.setFont(self.ip_label_font)
        self.ip_label.setContentsMargins(10, 40, 20, 10)
        self.ip_label.setAlignment(Qt.AlignCenter)

        qr_image = generate_qr_code()
        qr_pixmap = pil2pixmap(qr_image)
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContentsMargins(10, 30, 10, 30)
        self.imageLabel.setPixmap(qr_pixmap)

        self.btn_stop = QPushButton('Done')
        self.btn_stop.resize(self.btn_stop.sizeHint())
        self.btn_stop.move(150, 50)

        # GUI title, size, etc...
        self.setGeometry(250, 200, 300, 420)
        self.setWindowTitle('Zank Remote Desktop')
        self.ip_layout = QVBoxLayout()
        self.ip_layout.addWidget(self.title_lable)
        self.ip_layout.addWidget(self.ip_label)
        self.ip_layout.addWidget(self.imageLabel)
        self.ip_layout.addWidget(self.btn_stop)
        self.setLayout(self.ip_layout)

        self.btn_stop.clicked.connect(self.close)

    def show_top(self):
        self.show()
        self.setWindowState(self.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        # this will activate the window
        self.activateWindow()


class ControlPanelMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Zank Remote Desktop'
        self.left = 0
        self.top = 0
        self.width = 500
        self.height = 300
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.table_widget = ControlPanelTabWidget(self)
        self.setCentralWidget(self.table_widget)

    def show_top(self):
        self.show()
        self.setWindowState(self.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        # this will activate the window
        self.activateWindow()


class ControlPanelTabWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.statusTab = QWidget()
        self.settingTab = QWidget()
        self.aboutTab = QWidget()

        # Add tabs
        self.tabs.addTab(self.statusTab, "Status")
        # self.tabs.addTab(self.settingTab, "Setting")
        self.tabs.addTab(self.aboutTab, "About")

        # Create first tab

        self.name_label = QLabel("Computer Name: " + hostName, self)
        self.name_label_font = QFont('Arial', 20)
        self.name_label_font.setBold(True)
        self.name_label.setFont(self.name_label_font)
        self.name_label.setContentsMargins(10, 40, 20, 10)
        self.name_label.setAlignment(Qt.AlignLeft)

        self.ip_label = QLabel("Computer IP Address: " + hostIP, self)
        self.ip_label_font = QFont('Arial', 20)
        self.ip_label_font.setBold(True)
        self.ip_label.setFont(self.ip_label_font)
        self.ip_label.setContentsMargins(10, 40, 20, 10)
        self.ip_label.setAlignment(Qt.AlignLeft)

        qr_image = generate_qr_code()
        qr_pixmap = pil2pixmap(qr_image)
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContentsMargins(10, 30, 10, 30)
        self.imageLabel.setPixmap(qr_pixmap)

        self.statusTab.layout = QVBoxLayout(self)
        self.statusTab.layout.addWidget(self.name_label)
        self.statusTab.layout.addWidget(self.ip_label)
        self.statusTab.layout.addWidget(self.imageLabel)
        self.statusTab.setLayout(self.statusTab.layout)

        # Create second tab

        # Create third tab

        self.appPixmap = QPixmap('app_icon_rgb.jpg')

        self.appImageLabel = QLabel()
        self.appImageLabel.setAlignment(Qt.AlignCenter)
        self.scaled = self.appPixmap.scaled(self.appImageLabel.size(), Qt.KeepAspectRatio)
        self.appImageLabel.setPixmap(self.scaled)
        self.sp = self.appImageLabel.sizePolicy()
        self.sp.setHorizontalPolicy(QSizePolicy.Maximum)
        self.appImageLabel.setSizePolicy(self.sp)

        self.app_name_label = QLabel("Zank Remote Desktop", self)
        self.app_name_label_font = QFont('Arial', 20)
        self.app_name_label_font.setBold(True)
        self.app_name_label.setFont(self.app_name_label_font)
        # self.app_name_label.setContentsMargins(10, 5, 20, 10)
        self.app_name_label.setAlignment(Qt.AlignCenter)

        self.app_slogan_label = QLabel("Control everything in your hand", self)
        self.app_slogan_label_font = QFont('Arial', 18)
        # self.app_slogan_label_font.setBold(True)
        self.app_slogan_label.setFont(self.app_slogan_label_font)
        # self.app_slogan_label.setContentsMargins(10, 40, 20, 10)
        self.app_slogan_label.setAlignment(Qt.AlignCenter)

        self.app_web_label = QLabel("www.zankremote.com", self)
        self.app_web_label_font = QFont('Arial', 14)
        self.app_web_label.setFont(self.app_web_label_font)
        # self.app_slogan_label.setContentsMargins(10, 40, 20, 10)
        self.app_web_label.setAlignment(Qt.AlignCenter)

        self.aboutTab.layout = QVBoxLayout(self)
        self.aboutTab.layout.addWidget(self.appImageLabel)
        self.aboutTab.layout.addWidget(self.app_name_label)
        self.aboutTab.layout.addWidget(self.app_slogan_label)
        self.aboutTab.layout.addWidget(self.app_web_label)
        self.aboutTab.setLayout(self.aboutTab.layout)

        # Add tabs to widget
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


class ZankRemoteApplication(QApplication):

    stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

    def __init__(self, args):
        """ In the constructor we're doing everything to get our application
            started, which is basically constructing a basic QApplication by
            its __init__ method, then adding our widgets and finally starting
            the exec_loop."""
        QApplication.__init__(self, args)

        self.thread = QThread()
        self.tcp_thread = QThread()
        self.worker = UDPWorker()
        self.tcp_worker = TCPWorker()

        self.app_icon = QIcon("app_icon_round.png")
        self.showIpWindow = ShowIPWindow()
        self.controlPanelMainWindow = ControlPanelMainWindow()
        self.icon = QIcon("app_icon_round.png")


        self.addWidgets()

    def addWidgets(self):
        """ In this method, we're adding widgets and connecting signals from
            these widgets to methods of our class, the so-called "slots"
        """
        # Set app icon
        self.setWindowIcon(self.app_icon)

        # Create the icon

        # Create the tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)

        # Create the menu
        self.menu = QMenu()

        self.see_tutorials = QAction("Tutorials")
        self.menu.addAction(self.see_tutorials)

        self.show_ip_window = QAction("Show IP Address")
        self.show_ip_window.triggered.connect(self.showIpWindow.show_top)
        self.menu.addAction(self.show_ip_window)

        self.restart = QAction("Restart")
        self.menu.addAction(self.restart)

        self.control_panel = QAction("Control Panels")
        self.control_panel.triggered.connect(self.controlPanelMainWindow.show_top)
        self.menu.addAction(self.control_panel)

        # Add a Quit option to the menu.
        self.quit_action = QAction("Quit Zank Remote")
        self.quit_action.triggered.connect(self.stop_thread)
        self.quit_action.triggered.connect(self.quit)
        self.menu.addAction(self.quit_action)

        # Add the menu to the tray
        self.tray.setContextMenu(self.menu)

        self.start_server()

    def slotSayHello(self):
        """ This is an example slot, a method that gets called when a signal is
            emitted """
        print ("Hello, World!")

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
    app = ZankRemoteApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.exec_()
    # sys.exit(app.exec_())
