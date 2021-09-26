import sys
import os
import glob
import cv2
import json
import numpy as np

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from qt.ui_NewProject import Ui_NewProject

import utils

class Project(QWidget, Ui_NewProject):
    def __init__(self, initProject):
        super().__init__()
        self.setupUi(self)
        self.cwd = os.getcwd()

        self.initProject = initProject

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
    
    def newProject(self, img_dir_path, shot_detection_result_path, output_dir_path):
        self.imgDirPath = img_dir_path
        self.shotDetectionResultPath = shot_detection_result_path
        self.outputDirPath = output_dir_path

        for clazz in ["CloseUp", "Pitch", "Hit", "Overlook", "Other"]:
            utils.creatFolder(os.path.join(self.outputDirPath, clazz))

        self.saveProject()
        self.initProject()

    def loadProject(self):
        filePath, filetype  = QFileDialog.getOpenFileName(self, "Select the Project File", os.getcwd(),
                    "Json Files (*.json);;All Files (*)")
        if(filePath == ""):
            return
            
        with open(filePath) as jsonfile:
            data = json.load(jsonfile)
            self.imgDirPath = data["imgDirPath"]
            self.shotDetectionResultPath = data["shotDetectionResultPath"]
            self.outputDirPath = data["outputDirPath"]
        self.initProject()

    def saveProject(self):
        with open(os.path.join(self.outputDirPath, "config.json"), 'w') as jsonfile:
            data = {
                'imgDirPath': self.imgDirPath,
                'shotDetectionResultPath': self.shotDetectionResultPath,
                'outputDirPath': self.outputDirPath,
            }
            json.dump(data, jsonfile, indent=4)

    def saveClip(self, startIdx, endIdx, clazz):
        os.path.join(self.outputDirPath, clazz)