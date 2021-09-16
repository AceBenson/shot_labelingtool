import sys
import os
import glob
import cv2
import json
import numpy as np

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from qt.ui_MainWindow import Ui_MainWindow

from project import Project

import utils


### Todo
# 1. projet class?
# 2. next clip and split clip

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.project = Project(self.newProject)

        self.actionNew.triggered.connect(self.project.show)
        self.actionLoad.triggered.connect(self.loadProject)

        self.pushButton_next_clip.clicked.connect(self.nextClip)
        self.pushButton_split_clip.clicked.connect(self.splitClip)
    
    def newProject(self, img_dir_path, shot_detection_result_path, output_dir_path):
        # print("new project")
        self.imgDirPath = img_dir_path
        self.shotDetectionResultPath = shot_detection_result_path
        self.outputDirPath = output_dir_path
        self.curClipIdx = 0

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
            self.curClipIdx = data["curClipIdx"]
        self.initProject()

    def saveProject(self):
        with open(os.path.join(self.outputDirPath, "config.json"), 'w') as jsonfile:
            data = {
                'imgDirPath': self.imgDirPath,
                'shotDetectionResultPath': self.shotDetectionResultPath,
                'outputDirPath': self.outputDirPath,
                'curClipIdx': self.curClipIdx,
            }
            json.dump(data, jsonfile, indent=4)

    def initProject(self):
        data_list = [os.path.basename(filename) \
            for filename in glob.glob(os.path.join(self.imgDirPath, '*.jpg'))]
        self.imageArray = [img for img in sorted(data_list)] # Why not self.imageArray = sorted(data_list) ?
        
        with open(self.shotDetectionResultPath, 'r') as txtFile:
            self.scenePairs = [ (int(line.split()[0]), int(line.split()[1])) for line in txtFile.readlines()]

        # cv2.imdecode + np.fromfile can solve problem with chinese in path
        self.startFrameIdx = self.scenePairs[self.curClipIdx][0]
        self.startFrame = cv2.imdecode(np.fromfile(os.path.join(self.imgDirPath, self.imageArray[self.startFrameIdx]), dtype = np.uint8), -1)
        utils.showImgAtLabel(self.label_start_frame, self.startFrame)

        self.endFrameIdx = self.scenePairs[self.curClipIdx][1]
        self.endFrame = cv2.imdecode(np.fromfile(os.path.join(self.imgDirPath, self.imageArray[self.endFrameIdx]), dtype = np.uint8), -1)
        utils.showImgAtLabel(self.label_end_frame, self.endFrame)

        self.clipFrameIdx = self.scenePairs[self.curClipIdx][0]
        self.clipFrame = cv2.imdecode(np.fromfile(os.path.join(self.imgDirPath, self.imageArray[self.clipFrameIdx]), dtype = np.uint8), -1)
        utils.showImgAtLabel(self.label_clip, self.clipFrame)
        
    def nextClip(self):
        self.scenePairs[self.curClipIdx] = (self.startFrameIdx, self.endFrameIdx)

        # Also update scene txt
        with open(self.shotDetectionResultPath, 'w') as txtFile:
            for scenePair in self.scenePairs:
                txtFile.write(str(scenePair[0]) + " " + str(scenePair[1]) + "\n")

        # Save current clip to self.outputDirPath


        self.curClipIdx += 1
        self.saveProject()
        self.initProject() # initFrame

    def splitClip(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.showMaximized()
    sys.exit(app.exec_())
