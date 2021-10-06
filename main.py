import sys
import os
import glob
import cv2
import json
import numpy as np

from PyQt5.QtCore import Qt, QTimer
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

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self)+1
        return members[index] if index != len(members) else None
    
    def prev(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self)-1
        return members[index] if index != -1 else None

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
        
        self.pushButton_clip_play.clicked.connect(self.handlePlayPause)
        self.playerTimer = QTimer()
        self.playerTimer.timeout.connect(self.playerTimerEvent)
        self.fps = 30.0

        self.pushButton_clip_1x.setFlat(True)
        self.pushButton_clip_2x.setFlat(False)
        self.pushButton_clip_4x.setFlat(False)
        self.pushButton_clip_8x.setFlat(False)
        self.pushButton_clip_1x.clicked.connect(self.onChangeFPS)
        self.pushButton_clip_2x.clicked.connect(self.onChangeFPS)
        self.pushButton_clip_4x.clicked.connect(self.onChangeFPS)
        self.pushButton_clip_8x.clicked.connect(self.onChangeFPS)

        self.lineEdit_start_frame.editingFinished.connect(lambda : self.moveToFrame(Target.START_FRAME, int(self.lineEdit_start_frame.text())))
        self.lineEdit_clip.editingFinished.connect(lambda : self.moveToFrame(Target.CLIP, int(self.lineEdit_clip.text())))
        self.lineEdit_end_frame.editingFinished.connect(lambda : self.moveToFrame(Target.END_FRAME, int(self.lineEdit_end_frame.text())))

        self.horizontalSlider.valueChanged.connect(lambda : self.onChangeSliderValue())
        # self.horizontalSlider.valueChanged.connect(lambda : self.moveToFrame(Target.CLIP, self.horizontalSlider.value()))

        self.radioButton_CloseUp.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Pitch.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Hit.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Overlook.toggled.connect(lambda : self.onChangeClazz())
        self.radioButton_Other.toggled.connect(lambda : self.onChangeClazz())

        
    def initProject(self):
        data_list = [os.path.basename(filename) for filename in glob.glob(os.path.join(self.project.imgDirPath, '*.png'))]
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
        

        # self.initFrames()

        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(len(self.imageArray)-1)
        self.horizontalSlider.setSingleStep(1)
        # self.horizontalSlider.setValue([self.scenePairs[0][0], int((self.scenePairs[0][0] + self.scenePairs[0][1])/2), self.scenePairs[0][1]])
        self.horizontalSlider.setBarMovesAllHandles(False)
        self.horizontalSlider.setBarIsRigid(False)
        # self.horizontalSlider.setValue(self.scenePairs[0][0])

        self.initFrames()

        self.keyPressEvent = self.keyPressEvent

        self.curRadioButton = None

    def initFrames(self):
        self.frameIdxs = [self.scenePairs[0][0], int((self.scenePairs[0][0] + self.scenePairs[0][1])/2), self.scenePairs[0][1]]
        self.zoomInSlider()
        for target in Target:
            self.frames[target] = cv2.imdecode(np.fromfile(os.path.join(self.project.imgDirPath, self.imageArray[self.frameIdxs[target]]), dtype = np.uint8), -1)
            utils.showImgAtLabel(self.labels[target], self.frames[target])
            self.lineEdits[target].setText(str(self.frameIdxs[target]))
        self.horizontalSlider.setValue(self.frameIdxs)

    def nextFrame(self, target):
        self.moveToFrame(target, self.frameIdxs[target]+1)

    def prevFrame(self, target):
        self.moveToFrame(target, self.frameIdxs[target]-1)

    def moveToFrame(self, target, targetFrameIdx):
        if self.frameIdxs[target] == targetFrameIdx:
            return

        if target.next() is not None and targetFrameIdx >= self.frameIdxs[target.next()]:
            return
        elif target.prev() is not None and targetFrameIdx <= self.frameIdxs[target.prev()]:
            return

        self.horizontalSlider.setRange( min(self.horizontalSlider.minimum(), targetFrameIdx), \
            max(self.horizontalSlider.maximum(), targetFrameIdx))

        print("moveToFrame", target, targetFrameIdx)
        if targetFrameIdx < 0 or targetFrameIdx >= len(self.imageArray):
            print("=== Frame: " + str(targetFrameIdx) + " is out of range !!! ===")
            return
        self.frameIdxs[target] = targetFrameIdx
        self.frames[target] = cv2.imdecode(np.fromfile(os.path.join(self.project.imgDirPath, self.imageArray[self.frameIdxs[target]]), dtype = np.uint8), -1)
        utils.showImgAtLabel(self.labels[target], self.frames[target])
        self.lineEdits[target].setText(str(targetFrameIdx))

        # if target == Target.CLIP:
        #     self.horizontalSlider.setValue(targetFrameIdx) # This setValue will call the connected function(moveToFrame)
        self.horizontalSlider.setValue(self.frameIdxs)

    def handlePlayPause(self):
        if not self.playerTimer.isActive():
            self.pushButton_clip_play.setText("Pause")
            self.playerTimer.start(1000/self.fps)
        else:
            self.pushButton_clip_play.setText("Play")
            self.playerTimer.stop()

    def playerTimerEvent(self):
        if self.frameIdxs[Target.CLIP]+1 >= len(self.imageArray): # or use > self.frameIdxs[Target.END_FRAME] instead
            self.playerTimer.stop()
        else:
            self.moveToFrame(Target.CLIP, self.frameIdxs[Target.CLIP]+1)


    def onChangeClazz(self):
        if self.sender().isChecked():
            self.curRadioButton = self.sender()

    def onChangeSliderValue(self):
        for target in Target:
            self.moveToFrame(target, self.horizontalSlider.value()[target])
            
    def onChangeFPS(self):
        def clearAllDefault():
            self.pushButton_clip_1x.setFlat(False)
            self.pushButton_clip_2x.setFlat(False)
            self.pushButton_clip_4x.setFlat(False)
            self.pushButton_clip_8x.setFlat(False)

        self.fps = 30.0*int(self.sender().text()[0])

        if self.playerTimer.isActive():
            self.playerTimer.stop()
            self.playerTimer.start(1000/self.fps)

        clearAllDefault()
        self.sender().setFlat(True)

    def zoomInSlider(self):
        clipRange = self.frameIdxs[Target.END_FRAME] - self.frameIdxs[Target.START_FRAME]
        startPoint = max(0, self.frameIdxs[Target.START_FRAME] - int(clipRange/3))
        endPoint = min((len(self.imageArray) - 1), self.frameIdxs[Target.END_FRAME] + int(clipRange/3))
        print("Change Slider Range: %d / %d" % (startPoint, endPoint))
        self.horizontalSlider.setRange(startPoint, endPoint)

    def zoomOutSlider(self):
        startPoint = 0
        endPoint = len(self.imageArray) - 1
        print("Change Slider Range: %d / %d" % (startPoint, endPoint))
        self.horizontalSlider.setRange(startPoint, endPoint)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Plus:
            self.zoomInSlider()
        elif e.key() == Qt.Key_Minus:
            self.zoomOutSlider()


    def resetRadioButton(self):
        self.curRadioButton.setAutoExclusive(False)
        self.curRadioButton.setChecked(False)
        self.curRadioButton.setAutoExclusive(True)
        self.curRadioButton = None

    def nextClip(self):
        if self.curRadioButton == None:
            print("Warning: Please choose one class for labeling.")
            return
        
        if self.frameIdxs[Target.START_FRAME] >= self.frameIdxs[Target.END_FRAME]:
            print("Warning: Start Frame can't be greater than End Frame.")
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

        if self.frameIdxs[Target.START_FRAME] >= self.frameIdxs[Target.END_FRAME]:
            print("Warning: Start Frame can't be greater than End Frame.")
            return

        # Update self.scenePairs and scene.txt
        oldPair = self.scenePairs.pop(0)

        if not self.frameIdxs[Target.END_FRAME]+1 > oldPair[1]:
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
