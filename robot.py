__author__ = 'Rafał'

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication

"""
MAC: 80:1f:02:a2:f2:43
login: pi
haslo: UJlidar
"""

from PySide2 import QtCore
import sys
import communication
import signal


class RobotController:
    """
    Main class for robot controller
    """
    def __init__(self):
        # Time
        self.t = 0
        self.scan_time = 100  # ms

        # Robot

        # Communication
        self.communication = communication.Communication()
        self.communication.make_server()
        self.communication.new_data.connect(self.new_message)

        # run clock
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.run)
        self.timer.start(self.scan_time)

    @QtCore.Slot(object)
    def run(self):
        pass

    @QtCore.Slot(object)
    def new_message(self, message):
        print("new_message")
        # self.robot.move(message['left_motor']/255.0, message['right_motor']/255.0)

    def sigint_handler(self, *args):
        """
        Stop thread before end
        """
        self.communication.stop()
        QtCore.QCoreApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    robotController = RobotController()
    signal.signal(signal.SIGINT, robotController.sigint_handler)  # allow ctrl+c

    app_icon = QIcon("app_icon_round.png")
    icon = QIcon("app_icon_round.png")

    # Set app icon
    app.setWindowIcon(app_icon)

    # Create the icon

    # Create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # Create the menu
    menu = QMenu()

    see_tutorials = QAction("Tutorials")
    # see_tutorials.triggered.connect(thread_status)
    menu.addAction(see_tutorials)

    show_ip_window = QAction("Show IP Address")
    # show_ip_window.triggered.connect(showIpWindow.show_top)
    menu.addAction(show_ip_window)

    restart = QAction("Restart")
    restart.triggered.connect(quit)
    menu.addAction(restart)

    control_panel = QAction("Control Panels")
    control_panel.triggered.connect(robotController.communication.dissconect)
    menu.addAction(control_panel)

    # Add a Quit option to the menu.
    quit_action = QAction("Quit Zank Remote")
    quit_action.triggered.connect(robotController.communication.stop)
    menu.addAction(quit_action)

    # Add the menu to the tray
    tray.setContextMenu(menu)
    
    app.exec_()
    sys.exit()