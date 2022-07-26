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

from PyQt5.QtWidgets import QLabel, QPushButton, QSlider, QVBoxLayout, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from helper.meta_classes import WidgetInterface

class CenterView(QWidget, QObject, WidgetInterface):
    """view class for finding a reference point in the center of an image

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface (class):  provides abstract class methods for setting the icons and updating the view
    """
    closeView_Signal = pyqtSignal()
    sliderChanged_Signal = pyqtSignal()

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.closeSignalState = False

        self.setWindowTitle('Center View')
        self.v_box = QVBoxLayout()

        self.dpSlider_label = QLabel('Inverse accumulator value (dp)')
        self.dpSlider = QSlider(Qt.Horizontal)
        self.dpSlider.setMinimum(5)
        self.dpSlider.setMaximum(35)
        self.dpSlider.setTickInterval(2)
        self.dpSlider.setTickPosition(QSlider.TicksBelow)
        self.dpSlider.valueChanged.connect(self.sliderChanged)

        self.v_box.addWidget(self.dpSlider_label)
        self.v_box.addWidget(self.dpSlider)

        self.imageLabel = QLabel()
        self.v_box.addWidget(self.imageLabel)

        self.closeButton = QPushButton('Apply and Close')
        self.v_box.addWidget(self.closeButton)
        self.closeButton.clicked.connect(self.reqClose)

        self.setLayout(self.v_box)

    def sliderChanged(self):
        """emits a signal when a slider was changed
        """
        self.sliderChanged_Signal.emit()

    def reqClose(self):
        """emits a signal to request closing the view
        """
        self.closeView_Signal.emit()

    def closeEvent(self, event):
        """handles closing of the view

        Args:
            event (event): [description]
        """
        if not self.closeSignalState:
            self.closeView_Signal.emit()
        else:
            event.accept()