   
from qt.customSlider._custom_slider import _CustomSlider
# from qt.customSlider._generic_range_slider import _GenericRangeSlider
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

app = QApplication([])

slider = _CustomSlider(Qt.Horizontal)

slider.setValue((20, 80))
slider.show()

app.exec_()