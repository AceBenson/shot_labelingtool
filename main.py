import sys
import os
import glob
import cv2
import json
import numpy as np

from PyQt5.QtWidgets import QMainWindow, QApplication
from qt.ui_MainWindow import Ui_MainWindow


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.showMaximized()
    sys.exit(app.exec_())
