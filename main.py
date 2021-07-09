import socket
from enum import Enum

import pyautogui
import time
import sys

from PySide2 import QtWidgets
from PySide2.QtGui import QIcon, QPalette, QPixmap, QImage, QCursor, QFont
from PySide2.QtWidgets import (QWidget, QPushButton, QApplication, QGridLayout, QVBoxLayout, QSystemTrayIcon, QMenu,
                               QAction, QHBoxLayout, QLabel, QSizePolicy, QTabWidget, QMainWindow, QScrollArea)
from PySide2.QtCore import Qt, QThread, QObject, Signal, Slot, QTimer, QThreadPool, QRunnable, QCoreApplication, QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView

import qrcode
from PIL import Image
from sys import platform

from sys import platform as _platform

import communication
import utils


class PlatformName(Enum):
    WINDOW = 1
    MACOS = 2
    LINUX = 3


if _platform == "darwin":
    # MAC OS X
    from AppKit import NSWorkspace
    from Foundation import NSURL
    PLATFORM_NAME = PlatformName.MACOS

elif _platform == "linux" or _platform == "linux2":
    # Linux
    PLATFORM_NAME = PlatformName.LINUX

elif _platform == "win32":
    # Windows
    PLATFORM_NAME = PlatformName.WINDOW

class TutorialMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons


        self.notice_title = QLabel("Notice:", self)
        self.notice_title_font = QFont('Arial', 26)
        self.notice_title_font.setBold(True)
        self.notice_title.setFont(self.notice_title_font)
        self.notice_title.setAlignment(Qt.AlignLeft)

        self.notice_detail = QLabel('macOS has significantly enhanced the security & privacy protection, therefore it requires re-authorization when using Remote Mouse or a specific feature for the first time under macOS, otherwise Remote Mouse will not be able to work. This is very similar to how you authorize an app on the iPhone.', self)
        self.notice_detail_font = QFont('Arial', 16)
        self.notice_detail_font.setBold(True)
        self.notice_detail.setFont(self.notice_detail_font)
        self.notice_detail.setAlignment(Qt.AlignLeft)
        self.notice_detail.setContentsMargins(10, 40, 20, 10)
        self.notice_detail.setWordWrap(True)

        self.accessibility_title = QLabel("Accessibility", self)
        self.accessibility_title_font = QFont('Arial', 26)
        self.accessibility_title_font.setBold(True)
        self.accessibility_title.setFont(self.accessibility_title_font)
        self.accessibility_title.setAlignment(Qt.AlignLeft)
        
        self.accessibility_detail = QLabel("The first time to use Remote Mouse after connecting to the Mac, you will be prompted to grant access.", self)
        self.accessibility_detail_font = QFont('Arial', 16)
        self.accessibility_detail_font.setBold(True)
        self.accessibility_detail.setFont(self.accessibility_detail_font)
        self.accessibility_detail.setAlignment(Qt.AlignLeft)
        self.accessibility_detail.setContentsMargins(10, 40, 20, 10)
        self.accessibility_detail.setWordWrap(True)
        
        self.accessibility_detail_step1 = QLabel("1. Choose \"Go to Accessibility\" to open the Accessibility window.", self)
        self.accessibility_detail_step1_font = QFont('Arial', 16)
        self.accessibility_detail_step1_font.setBold(True)
        self.accessibility_detail_step1.setFont(self.accessibility_detail_step1_font)
        self.accessibility_detail_step1.setAlignment(Qt.AlignLeft)
        self.accessibility_detail_step1.setWordWrap(True)
        
        self.accessibility_detail_step2 = QLabel("2. Click the lock icon in the lower left corner and enter your Mac password to unlock it.", self)
        self.accessibility_detail_step2_font = QFont('Arial', 16)
        self.accessibility_detail_step2_font.setBold(True)
        self.accessibility_detail_step2.setFont(self.accessibility_detail_step2_font)
        self.accessibility_detail_step2.setAlignment(Qt.AlignLeft)
        self.accessibility_detail_step2.setWordWrap(True)

        self.appPixmap_2 = QPixmap('tut1.png')
        self.access_step_2 = QLabel()
        self.access_step_2.setAlignment(Qt.AlignCenter)
        self.scaled = self.appPixmap_2.scaled(self.access_step_2.size(), Qt.KeepAspectRatio)
        self.access_step_2.setPixmap(self.scaled)
        self.sp = self.access_step_2.sizePolicy()
        self.sp.setHorizontalPolicy(QSizePolicy.Maximum)
        self.access_step_2.setSizePolicy(self.sp)
        
        self.accessibility_detail_step3 = QLabel("3. Tick Remote Mouse in the list on the right.", self)
        self.accessibility_detail_step3_font = QFont('Arial', 16)
        self.accessibility_detail_step3_font.setBold(True)
        self.accessibility_detail_step3.setFont(self.accessibility_detail_step3_font)
        self.accessibility_detail_step3.setAlignment(Qt.AlignLeft)
        self.accessibility_detail_step3.setWordWrap(True)

        self.appPixmap_3 = QPixmap('tut1.png')
        self.access_step_3 = QLabel()
        self.access_step_3.setAlignment(Qt.AlignCenter)
        self.scaled = self.appPixmap_3.scaled(self.access_step_3.size(), Qt.KeepAspectRatio)
        self.access_step_3.setPixmap(self.scaled)
        self.sp = self.access_step_3.sizePolicy()
        self.sp.setHorizontalPolicy(QSizePolicy.Maximum)
        self.access_step_3.setSizePolicy(self.sp)

        self.btn_stop = QPushButton('Go to Accessibility')
        self.btn_stop.resize(self.btn_stop.sizeHint())
        self.btn_stop.move(150, 100)

        self.vbox.addWidget(self.notice_title)
        self.vbox.addWidget(self.notice_detail)
        self.vbox.addWidget(self.accessibility_title)
        self.vbox.addWidget(self.accessibility_detail)

        self.vbox.addWidget(self.accessibility_detail_step1)
        self.vbox.addWidget(self.accessibility_detail_step2)
        self.vbox.addWidget(self.access_step_2)
        self.vbox.addWidget(self.accessibility_detail_step3)
        self.vbox.addWidget(self.access_step_3)
        self.vbox.addWidget(self.btn_stop)

        self.btn_stop.clicked.connect(self.open_accessibility_setting)

        # for i in range(1,50):
        #     object = QLabel("TextLabel")
        #     self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle('Zank Remote Tutorials')
        return

    def open_accessibility_setting(self):

        sys_pref_link = 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'

        # create workspace object
        workspace = NSWorkspace.sharedWorkspace()

        # Open System Preference
        workspace.openURL_(NSURL.URLWithString_(sys_pref_link))


    def show_top(self):
        self.show()
        self.setWindowState(self.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        # this will activate the window
        self.activateWindow()



class WebViewMainWindow(QMainWindow):

    def __init__(self, url):
        super().__init__()
        self.initUI()
        self.url = url

    def initUI(self):
        self.view = QWebEngineView()
        self.app_icon = QIcon("app_icon_round.png")

        self.view.load(QUrl(self.url))

        self.setCentralWidget(self.view)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowIcon(self.app_icon)
        self.setWindowTitle('Zank Remote Tutorials')
        return

    def show_top(self):
        self.show()
        self.setWindowState(self.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        # this will activate the window
        self.activateWindow()


class ShowIPWindow(QWidget):

    def __init__(self, parent=None):
        super(ShowIPWindow, self).__init__(parent)
        # Buttons:
        self.title_lable = QLabel('Your computer IP address is: ', self)
        self.title_label_font = QFont('Arial', 16)
        self.title_label_font.setBold(True)
        self.title_lable.setFont(self.title_label_font)
        self.title_lable.setAlignment(Qt.AlignCenter)

        self.ip_label = QLabel(utils.get_ip(), self)
        self.ip_label_font = QFont('Arial', 26)
        self.ip_label_font.setBold(True)
        self.ip_label.setFont(self.ip_label_font)
        self.ip_label.setContentsMargins(10, 40, 20, 10)
        self.ip_label.setAlignment(Qt.AlignCenter)

        qr_image = utils.generate_qr_code(utils.get_ip())
        qr_pixmap = utils.pil2pixmap(qr_image)
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

        # self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)


    def show_top(self):
        self.show()
        self.setWindowState(self.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        # this will activate the window
        self.activateWindow()


class ControlPanelTabWidget(QWidget):

    def __init__(self, parent):
        super(ControlPanelTabWidget, self).__init__(parent)

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

        self.name_label = QLabel("Computer Name: " + utils.get_computer_host_name(), self)
        self.name_label_font = QFont('Arial', 20)
        self.name_label_font.setBold(True)
        self.name_label.setFont(self.name_label_font)
        self.name_label.setContentsMargins(10, 40, 20, 10)
        self.name_label.setAlignment(Qt.AlignLeft)

        self.ip_label = QLabel("Computer IP Address: " + utils.get_ip(), self)
        self.ip_label_font = QFont('Arial', 20)
        self.ip_label_font.setBold(True)
        self.ip_label.setFont(self.ip_label_font)
        self.ip_label.setContentsMargins(10, 40, 20, 10)
        self.ip_label.setAlignment(Qt.AlignLeft)

        qr_image = utils.generate_qr_code(utils.get_ip())
        qr_pixmap = utils.pil2pixmap(qr_image)
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

    @Slot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


class ZankRemoteApplication(QApplication):

    def __init__(self, args):
        """ In the constructor we're doing everything to get our application
            started, which is basically constructing a basic QApplication by
            its __init__ method, then adding our widgets and finally starting
            the exec_loop."""
        QApplication.__init__(self, args)

        self.setQuitOnLastWindowClosed(False)
        # Communication
        self.setApplicationName("Zank Remote Desktop")
        self.setOrganizationName("Zank Remote")
        self.setOrganizationDomain("https://zankremote.com")

        self.udp_communication = communication.UDPCommunication()
        self.udp_communication.make_server()

        self.tcp_communication = communication.TCPCommunication()
        self.tcp_communication.make_server()

        self.app_icon = QIcon("app_icon_round.png")
        self.showIpWindow = ShowIPWindow()
        self.icon = QIcon("app_icon_round.png")

        self.controlPanelMainWindow = ControlPanelMainWindow()
        self.showIpWindow = ShowIPWindow()

        self.tutorialsWindow = TutorialMainWindow()

        self.addWidgets()

    def addWidgets(self):
        """ In this method, we're adding widgets and connecting signals from
            these widgets to methods of our class, the so-called "slots"
        """
        # Set app icon
        self.setWindowIcon(self.app_icon)

        # Create the tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)

        # Create the menu
        self.menu = QMenu()

        self.see_tutorials = QAction("Tutorials")
        self.see_tutorials.triggered.connect(self.tutorialsWindow.show_top)
        self.menu.addAction(self.see_tutorials)

        self.show_ip_window = QAction("Show IP Address")
        self.show_ip_window.triggered.connect(self.showIpWindow.show_top)
        self.menu.addAction(self.show_ip_window)

        self.control_panel = QAction("Control Panels")
        self.control_panel.triggered.connect(self.controlPanelMainWindow.show_top)
        self.menu.addAction(self.control_panel)

        # Add a Quit option to the menu.
        self.quit_action = QAction("Quit Zank Remote")
        self.quit_action.triggered.connect(self.stop_thread)
        self.quit_action.triggered.connect(self.check_and_quit_program)
        self.menu.addAction(self.quit_action)

        # Add the menu to the tray
        self.tray.setContextMenu(self.menu)


        self.tray.activated.connect(self.system_icon)

        # TODO: Check and stop all thread before quit application
        # self.aboutToQuit.connect(self.closeEvent()

    # When stop_btn is clicked this runs. Terminates the worker and the thread.
    def stop_thread(self):
        print("Stop signal emit")
        self.udp_communication.stop()
        self.tcp_communication.stop()

        self.udp_communication.dissconect()
        self.tcp_communication.dissconect()

    def check_and_quit_program(self):
        if self.is_all_server_close():
            self.quit()
        else:
            QTimer.singleShot(1000, self.check_and_quit_program)

    def is_all_server_close(self):
        print("UDP Running:", self.udp_communication.isRunning())
        print("TCP Running:", self.tcp_communication.isRunning())

        if self.udp_communication.isRunning() is False and self.tcp_communication.isRunning() is False:
            return True
        else:
            return False

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self,
                                               "QUIT",
                                               "Are you sure want to stop process?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def system_icon(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            print('Clicked')
            self.tray.contextMenu().popup(QCursor.pos())
            # self.controlPanelMainWindow.show_top()


if __name__ == '__main__':
    app = ZankRemoteApplication(sys.argv)
    app.exec_()
    # sys.exit(app.exec_())
