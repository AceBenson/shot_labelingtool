import cv2
import errno
import os

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel

def creatFolder(folder_name):
    try:
        os.makedirs(folder_name)
    except FileExistsError:
        # directory already exists
        pass
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def resizeImgToLabelSize(label: QLabel, cv_img):   
    height, width, channel = cv_img.shape
    if width / height >= label.width() / label.height():
        showImg = cv2.resize(cv_img, (label.width(), int(height * label.width() / width)))
        scale = label.width()/width
    else:
        showImg = cv2.resize(cv_img, (int(width * label.height() / height), label.height()))
        scale = label.height()/height

    return showImg, scale


def showImgAtLabel(label: QLabel, cv_img):
    showImg, _ = resizeImgToLabelSize(label, cv_img)

    height, width, channel = showImg.shape
    bytesPerline = 3 * width
    qImg = QImage(showImg.data, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
    
    label.setPixmap(QPixmap.fromImage(qImg))
    return width, height