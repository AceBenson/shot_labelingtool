from PyQt5.QtGui import QPaintEvent, QMouseEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider, QStylePainter, QStyle, QStyleOptionSlider

from pprint import pprint
import time

def current_time():
    return round(time.time() * 1000)

class _CustomSlider(QSlider):
    def __init__(self, *args, **kwargs) -> None:

        self._value = [0, 0, 0]
        ### TODO: Add self._pressedControl & self._pressedControl

        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_Hover)
    
    # ############ QtOverrides ############

    def value(self):
        return self._value

    def setValue(self, value):
        print("setValue")
        self._value = value


    
    # ############ Paint Event for draw ui ############

    def paintEvent(self, paintEvent: QPaintEvent) -> None:
        painter = QStylePainter(self)
        opt = self._styleOption

        # Draw SliderGroove
        opt.subControls = QStyle.SubControl.SC_SliderGroove
        
        # Draw Tickmarks
        if opt.tickPosition != QSlider.NoTicks:
            opt.subControls |= QStyle.SubControl.SC_SliderTickmarks

        # Draw SliderHandle
        opt.subControls |= QStyle.SubControl.SC_SliderHandle
            
        painter.drawComplexControl(QStyle.ComplexControl.CC_Slider, opt)

        # self.setSliderPosition(current_time() % 5000)
    
    @property
    def _styleOption(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        return opt

    # ############ Events for update data ############

    # def mousePressEvent(self, paintEvent: QMouseEvent) -> None:
    #     print("mousePressEvent")

    # def mouseMoveEvent(self, paintEvent: QMouseEvent) -> None:
    #     print("mouseMoveEvent")

    def setSliderPosition(self, position):
        print('setSliderPosition')