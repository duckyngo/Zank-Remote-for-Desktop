import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon


def action():
    print('System tray icon clicked.')

app = QApplication(sys.argv)
icon = QSystemTrayIcon(QIcon('app_icon.png'), parent=app)
icon.activated.connect(action)
icon.show()



menu = QMenu(parent=None)
menu.aboutToShow.connect(action)
icon.setContextMenu(menu)

sys.exit(app.exec_())