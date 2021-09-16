import os

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from qt.ui_NewProject import Ui_NewProject

class Project(QWidget, Ui_NewProject):
    def __init__(self, newProject):
        super().__init__()
        self.setupUi(self)
        self.cwd = os.getcwd()

        self.newProject = newProject

        self.pushButton_img_dir.clicked.connect(self.getPath_imgDir)
        self.pushButton_shot_detection_result.clicked.connect(self.getPath_shotDetectionResult)
        self.pushButton_output_dir.clicked.connect(self.getPath_outputDir)

        self.pushButton_Cancel.clicked.connect(self.close)
        self.pushButton_Open.clicked.connect(self.open)

    def getPath_imgDir(self):
        filePath = QFileDialog.getExistingDirectory(self, "Select the Directory of Images", self.cwd)
        self.img_dir_path.setText(filePath)

    def getPath_shotDetectionResult(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, "Select the Shot Detection Result File", self.cwd, "Txt Files (*.txt);;All Files (*)")
        self.shot_detection_result_path.setText(filePath)

    def getPath_outputDir(self):
        filePath = QFileDialog.getExistingDirectory(self, "Select the Directory of Output", self.cwd)
        self.output_dir_path.setText(filePath)

    def open(self):
        isEmpty = False
        msg = ""
        if self.img_dir_path.text() == "":
            isEmpty = True
            msg = "Image Directory Path is Empty"
        elif self.shot_detection_result_path.text() == "":
            isEmpty = True
            msg = "Shot Detection Path is Empty"
        elif self.output_dir_path.text() == "":
            isEmpty = True
            msg = "Output Directory Path is Empty"
        
        if isEmpty:
            QMessageBox.warning(self,'Warning', mes, QMessageBox.Ok)
            return

        self.newProject(self.img_dir_path.text(), self.shot_detection_result_path.text(), self.output_dir_path.text())
        self.close()
        