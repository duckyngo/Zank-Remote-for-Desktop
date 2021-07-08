import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class Main(QMainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setWindowFlags(Qt.Tool)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())