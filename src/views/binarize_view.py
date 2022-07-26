#Copyright (C) 2021 Marc Sebastian Heinz
#                   <sebastian.heinz[at]]online.de>
#Copyright (C) 2021 AVL Schrick GmbH
#                   Dreherstraße 3-5
#                   42899 Remscheid
#                   <info@avl-schrick.com>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>

from PyQt5.QtWidgets import QCheckBox, QGridLayout, QLabel, QPushButton, QSlider, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from helper.meta_classes import WidgetInterface


class BinarizeView(QWidget, QObject, WidgetInterface):
    """view class for binarizing an image with hsv color threshold

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface (class): provides abstract class methods for setting the icons and updating the view
    """
    closeView_Signal = pyqtSignal()
    sliderChanged_Signal = pyqtSignal()
    toggleRefImage_Signal = pyqtSignal()
    toggleChannelMode_Signal = pyqtSignal()

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.closeSignalState = False

        self.setWindowTitle('Binarize View')
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.ref_label = QLabel('Show reference image for hsv color range')
        self.ref_button = QPushButton('Show')
        self.ref_button.clicked.connect(self.toggleRefImage)

        self.channel_label = QLabel('Extended threshold: select two seperate color channels')
        self.channel_checkbox = QCheckBox()
        self.channel_checkbox.toggled.connect(self.toggleChannelMode)

        self.colorChannel_label1 = QLabel('Color Threshold Channel 1')

        self.hue_min_label1 = QLabel('min. Hue')
        self.hue_min_slider1 = QSlider(Qt.Horizontal)
        self.hue_min_slider1.setMinimum(0)
        self.hue_min_slider1.setMaximum(180)
        self.hue_min_slider1.setTickInterval(1)
        self.hue_min_slider1.setValue(0)
        self.hue_min_slider1.valueChanged.connect(self.sliderChanged)

        self.saturation_min_label1 = QLabel('min. Saturation')
        self.saturation_min_slider1 = QSlider(Qt.Horizontal)
        self.saturation_min_slider1.setMinimum(0)
        self.saturation_min_slider1.setMaximum(255)
        self.saturation_min_slider1.setTickInterval(1)
        self.saturation_min_slider1.setValue(0)
        self.saturation_min_slider1.valueChanged.connect(self.sliderChanged)

        self.value_min_label1 = QLabel('min. Value')
        self.value_min_slider1 = QSlider(Qt.Horizontal)
        self.value_min_slider1.setMinimum(0)
        self.value_min_slider1.setMaximum(255)
        self.value_min_slider1.setTickInterval(1)
        self.value_min_slider1.setValue(20)
        self.value_min_slider1.valueChanged.connect(self.sliderChanged)

        self.hue_max_label1 = QLabel('max. Hue')
        self.hue_max_slider1 = QSlider(Qt.Horizontal)
        self.hue_max_slider1.setMinimum(0)
        self.hue_max_slider1.setMaximum(180)
        self.hue_max_slider1.setTickInterval(1)
        self.hue_max_slider1.setValue(180)
        self.hue_max_slider1.valueChanged.connect(self.sliderChanged)

        self.saturation_max_label1 = QLabel('max. Saturation')
        self.saturation_max_slider1 = QSlider(Qt.Horizontal)
        self.saturation_max_slider1.setMinimum(0)
        self.saturation_max_slider1.setMaximum(255)
        self.saturation_max_slider1.setTickInterval(1)
        self.saturation_max_slider1.setValue(255)
        self.saturation_max_slider1.valueChanged.connect(self.sliderChanged)

        self.value_max_label1 = QLabel('max. Value')
        self.value_max_slider1 = QSlider(Qt.Horizontal)
        self.value_max_slider1.setMinimum(0)
        self.value_max_slider1.setMaximum(255)
        self.value_max_slider1.setTickInterval(1)
        self.value_max_slider1.setValue(255)
        self.value_max_slider1.valueChanged.connect(self.sliderChanged)

        self.hsv_min_label1 = QLabel()
        self.hsv_max_label1 = QLabel()

        self.distance_dummy = QLabel('')

        self.colorChannel_label2 = QLabel('Color Threshold Channel 2')

        self.hue_min_label2 = QLabel('min. Hue')
        self.hue_min_slider2 = QSlider(Qt.Horizontal)
        self.hue_min_slider2.setMinimum(0)
        self.hue_min_slider2.setMaximum(180)
        self.hue_min_slider2.setTickInterval(1)
        self.hue_min_slider2.setValue(0)
        self.hue_min_slider2.valueChanged.connect(self.sliderChanged)

        self.saturation_min_label2 = QLabel('min. Saturation')
        self.saturation_min_slider2 = QSlider(Qt.Horizontal)
        self.saturation_min_slider2.setMinimum(0)
        self.saturation_min_slider2.setMaximum(255)
        self.saturation_min_slider2.setTickInterval(1)
        self.saturation_min_slider2.setValue(0)
        self.saturation_min_slider2.valueChanged.connect(self.sliderChanged)

        self.value_min_label2 = QLabel('min. Value')
        self.value_min_slider2 = QSlider(Qt.Horizontal)
        self.value_min_slider2.setMinimum(0)
        self.value_min_slider2.setMaximum(255)
        self.value_min_slider2.setTickInterval(1)
        self.value_min_slider2.setValue(20)
        self.value_min_slider2.valueChanged.connect(self.sliderChanged)

        self.hue_max_label2 = QLabel('max. Hue')
        self.hue_max_slider2 = QSlider(Qt.Horizontal)
        self.hue_max_slider2.setMinimum(0)
        self.hue_max_slider2.setMaximum(180)
        self.hue_max_slider2.setTickInterval(1)
        self.hue_max_slider2.setValue(180)
        self.hue_max_slider2.valueChanged.connect(self.sliderChanged)

        self.saturation_max_label2 = QLabel('max. Saturation')
        self.saturation_max_slider2 = QSlider(Qt.Horizontal)
        self.saturation_max_slider2.setMinimum(0)
        self.saturation_max_slider2.setMaximum(255)
        self.saturation_max_slider2.setTickInterval(1)
        self.saturation_max_slider2.setValue(255)
        self.saturation_max_slider2.valueChanged.connect(self.sliderChanged)

        self.value_max_label2 = QLabel('max. Value')
        self.value_max_slider2 = QSlider(Qt.Horizontal)
        self.value_max_slider2.setMinimum(0)
        self.value_max_slider2.setMaximum(255)
        self.value_max_slider2.setTickInterval(1)
        self.value_max_slider2.setValue(255)
        self.value_max_slider2.valueChanged.connect(self.sliderChanged)

        self.hsv_min_label2 = QLabel()
        self.hsv_max_label2 = QLabel()

        self.close_button = QPushButton('Apply and close')
        self.close_button.clicked.connect(self.reqClose)

        self.grid_layout.addWidget(self.ref_label, 1, 1)
        self.grid_layout.addWidget(self.ref_button, 1, 2)

        self.grid_layout.addWidget(self.channel_label, 2, 1)
        self.grid_layout.addWidget(self.channel_checkbox, 2, 2)

        self.grid_layout.addWidget(self.colorChannel_label1, 3, 1, 1, 2)

        self.grid_layout.addWidget(self.hue_min_label1, 4, 1)
        self.grid_layout.addWidget(self.hue_min_slider1, 5, 1, 1, 2)
        self.grid_layout.addWidget(self.hue_max_label1, 6, 1)
        self.grid_layout.addWidget(self.hue_max_slider1, 7, 1, 1, 2)

        self.grid_layout.addWidget(self.saturation_min_label1, 8, 1)
        self.grid_layout.addWidget(self.saturation_min_slider1, 9, 1, 1, 2)
        self.grid_layout.addWidget(self.saturation_max_label1, 10, 1)
        self.grid_layout.addWidget(self.saturation_max_slider1, 11, 1, 1, 2)

        self.grid_layout.addWidget(self.value_min_label1, 12, 1)
        self.grid_layout.addWidget(self.value_min_slider1, 13, 1, 1, 2)
        self.grid_layout.addWidget(self.value_max_label1, 14, 1)
        self.grid_layout.addWidget(self.value_max_slider1, 15, 1, 1, 2)

        self.grid_layout.addWidget(self.hsv_min_label1, 16, 1, 1, 2)
        self.grid_layout.addWidget(self.hsv_max_label1, 17, 1, 1, 2)

        self.grid_layout.addWidget(self.distance_dummy, 18, 1)

        self.grid_layout.addWidget(self.colorChannel_label2, 19, 1, 1, 2)

        self.grid_layout.addWidget(self.hue_min_label2, 20, 1)
        self.grid_layout.addWidget(self.hue_min_slider2, 21, 1, 1, 2)
        self.grid_layout.addWidget(self.hue_max_label2, 22, 1)
        self.grid_layout.addWidget(self.hue_max_slider2, 23, 1, 1, 2)

        self.grid_layout.addWidget(self.saturation_min_label2, 24, 1)
        self.grid_layout.addWidget(self.saturation_min_slider2, 25, 1, 1, 2)
        self.grid_layout.addWidget(self.saturation_max_label2, 26, 1)
        self.grid_layout.addWidget(self.saturation_max_slider2, 27, 1, 1, 2)

        self.grid_layout.addWidget(self.value_min_label2, 28, 1)
        self.grid_layout.addWidget(self.value_min_slider2, 29, 1, 1, 2)
        self.grid_layout.addWidget(self.value_max_label2, 30, 1)
        self.grid_layout.addWidget(self.value_max_slider2, 31, 1, 1, 2)

        self.grid_layout.addWidget(self.hsv_min_label2, 32, 1, 1, 2)
        self.grid_layout.addWidget(self.hsv_max_label2, 33, 1, 1, 2)

        self.grid_layout.addWidget(self.close_button, 34, 1)

    def sliderChanged(self):
        """emits a slider changed signal
        """
        self.sliderChanged_Signal.emit()

    def toggleRefImage(self):
        """emits a signal for toggling the hsv reference
        """
        self.toggleRefImage_Signal.emit()

    def toggleChannelMode(self):
        """emits a signal for toggling channel mode
        """
        self.toggleChannelMode_Signal.emit()

    def reqClose(self):
        """emits a signal that requests closing of the view
        """
        self.closeView_Signal.emit()
    
    def closeEvent(self, event):
        """method to handle closing event of the view

        Args:
            event (any): triggered when view gets closed
        """
        if not self.closeSignalState:
            self.closeView_Signal.emit()
        else:
            event.accept()