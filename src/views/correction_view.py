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

from PyQt5.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from helper.meta_classes import WidgetInterface

class CorrectionView(QWidget, QObject, WidgetInterface):
    """view for correcting the calculated diameters of the found contours

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface (class): provides abstract class methods for setting the icons and updating the view
    """
    closeView_Signal = pyqtSignal()
    inputChanged_Signal = pyqtSignal(object)

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.closeSignalState = False

        self.setWindowTitle('Correction View')
        self.grid_layout =QGridLayout()
        self.setLayout(self.grid_layout)

        self.imageLabel = QLabel()
        self.closeButton = QPushButton('Apply and Close')
        self.closeButton.clicked.connect(self.reqClose)

    def onChange(self):
        """emits a signal when a diameter was changed
        """
        source_input = self.sender()
        self.inputChanged_Signal.emit(source_input)

    def reqClose(self):
        """emits a signal as request for closing the view
        """
        self.closeView_Signal.emit()

    def closeEvent(self, event):
        """method that handles closing the view

        Args:
            event (event): triggered when view gets closed
        """
        if not self.closeSignalState:
            self.closeView_Signal.emit()
        else:
            event.accept()