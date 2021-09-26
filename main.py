import sys
import os
import glob
import cv2
import json
import numpy as np

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QSlider
from qt.ui_MainWindow import Ui_MainWindow

from project import Project
import utils

from enum import IntEnum

class Target(IntEnum):
    START_FRAME = 0
    CLIP = 1
    END_FRAME = 2

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.project = Project(self.initProject)

        self.actionNew.triggered.connect(self.project.show)
        self.actionLoad.triggered.connect(self.project.loadProject)

        self.pushButton_next_clip.clicked.connect(self.nextClip)
        self.pushButton_split_clip.clicked.connect(self.splitClip)

        self.pushButton_start_frame_next.clicked.connect(lambda : self.nextFrame(Target.START_FRAME))
        self.pushButton_clip_next.clicked.connect(lambda : self.nextFrame(Target.CLIP))
        self.pushButton_end_frame_next.clicked.connect(lambda : self.nextFrame(Target.END_FRAME))

        self.pushButton_start_frame_prev.clicked.connect(lambda : self.prevFrame(Target.START_FRAME))
        self.pushButton_clip_prev.clicked.connect(lambda : self.prevFrame(Target.CLIP))
        self.pushButton_end_frame_prev.clicked.connect(lambda : self.prevFrame(Target.END_FRAME))

        self.lineEdit_start_frame.editingFinished.connect(lambda : self.moveToFrame(Target.START_FRAME, int(self.lineEdit_start_frame.text())))
        self.lineEdit_clip.editingFinished.connect(lambda : self.moveToFrame(Target.CLIP, int(self.lineEdit_clip.text())))
        self.lineEdit_end_frame.editingFinished.connect(lambda : self.moveToFrame(Target.END_FRAME, int(self.lineEdit_end_frame.text())))

        # self.horizontalSlider.valueChanged.connect(self.onChangeSliderValue)
        self.horizontalSlider.valueChanged.connect(lambda : self.moveToFrame(Target.CLIP, self.horizontalSlider.value()))

        self.radioButton_CloseUp.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Pitch.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Hit.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Overlook.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Other.toggled.connect(lambda : self.onChangeClazz())

        
    def initProject(self):
        data_list = [os.path.basename(filename) for filename in glob.glob(os.path.join(self.project.imgDirPath, '*.jpg'))]
        self.imageArray = [img for img in sorted(data_list)] # Why not self.imageArray = sorted(data_list) ?
        
        with open(self.project.shotDetectionResultPath, 'r') as txtFile:
            self.scenePairs = [ (int(line.split()[0]), int(line.split()[1])) for line in txtFile.readlines()]

        # cv2.imdecode + np.fromfile can solve problem with chinese in path
        self.frameIdxs = [None] * 3
        self.frames = [None] * 3
        self.labels = [self.label_start_frame, self.label_clip, self.label_end_frame]
        self.lineEdits = [self.lineEdit_start_frame, self.lineEdit_clip, self.lineEdit_end_frame]

        for target in Target:
            self.lineEdits[target].setValidator(QIntValidator(0, len(self.imageArray)-1))
        
        

        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(len(self.imageArray)-1)
        self.horizontalSlider.setSingleStep(1)
        # self.horizontalSlider.setValue([self.scenePairs[0][0], self.scenePairs[0][0], self.scenePairs[0][1]])
        self.horizontalSlider.setValue(self.scenePairs[0][0])

        self.initFrames()

        self.curRadioButton = None

    def initFrames(self):
        self.frameIdxs = [self.scenePairs[0][0], self.scenePairs[0][0], self.scenePairs[0][1]]
        for target in Target:
            self.moveToFrame(target, self.frameIdxs[target])

    def nextFrame(self, target):
        self.moveToFrame(target, self.frameIdxs[target]+1)

    def prevFrame(self, target):
        self.moveToFrame(target, self.frameIdxs[target]-1)

    def moveToFrame(self, target, targetFrameIdx):
        print("moveToFrame", target, targetFrameIdx)
        if targetFrameIdx < 0 or targetFrameIdx >= len(self.imageArray):
            print("=== Frame: " + str(targetFrameIdx) + " is out of range !!! ===")
            return
        self.frameIdxs[target] = targetFrameIdx
        self.frames[target] = cv2.imdecode(np.fromfile(os.path.join(self.project.imgDirPath, self.imageArray[self.frameIdxs[target]]), dtype = np.uint8), -1)
        utils.showImgAtLabel(self.labels[target], self.frames[target])

        self.lineEdits[target].setText(str(targetFrameIdx))

        if target == Target.CLIP:
            self.horizontalSlider.setValue(targetFrameIdx) # This setValue will call the connected function(moveToFrame)

    def onChangeClazz(self):
        if self.sender().isChecked():
            self.curRadioButton = self.sender()

    def resetRadioButton(self):
        self.curRadioButton.setAutoExclusive(False)
        self.curRadioButton.setChecked(False)
        self.curRadioButton.setAutoExclusive(True)
        self.curRadioButton = None

    def onChangeSliderValue(self):
        # print(type(self.horizontalSlider.value()[0]))
        print(type(self.horizontalSlider.value()))
        print(self.horizontalSlider.value())

    def nextClip(self):
        if self.curRadioButton == None:
            print("Warning: Please choose one class for labeling.")
            return

        # Update self.scenePairs and scene.txt
        self.scenePairs.pop(0)
        with open(self.project.shotDetectionResultPath, 'w') as txtFile:
            txtFile.writelines(["%s %s\n" % (str(pair[0]), str(pair[1])) for pair in self.scenePairs])

        # Save Video Clip with label json
        self.project.saveClip(self.frameIdxs[Target.START_FRAME], self.frameIdxs[Target.END_FRAME], self.curRadioButton.text())

        self.resetRadioButton()
        self.initFrames()


    def splitClip(self):
        if self.curRadioButton == None:
            print("Warning: Please choose one class for labeling.")
            return

        # Update self.scenePairs and scene.txt
        oldPair = self.scenePairs.pop(0)
        self.scenePairs.insert(0, (self.frameIdxs[Target.END_FRAME]+1, oldPair[1]))
        with open(self.project.shotDetectionResultPath, 'w') as txtFile:
            txtFile.writelines(["%s %s\n" % (str(pair[0]), str(pair[1])) for pair in self.scenePairs])

        # Save Video Clip with label json
        self.project.saveClip(self.frameIdxs[Target.START_FRAME], self.frameIdxs[Target.END_FRAME], self.curRadioButton.text())

        self.resetRadioButton()
        self.initFrames()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.showMaximized()
    sys.exit(app.exec_())
