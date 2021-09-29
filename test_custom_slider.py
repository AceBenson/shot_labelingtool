   
from qt.customSlider._custom_slider import _CustomSlider
from qt.customSlider._generic_range_slider import _GenericRangeSlider

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QSlider

def onChange():
    pass
    # print("onChange: ", slider.value())

app = QApplication([])

slider = _CustomSlider(Qt.Horizontal)

slider.setMaximum(5000)
slider.setMinimum(0)
slider.setSingleStep(1)

slider.valueChanged.connect(onChange)

slider.show()

app.exec_()

