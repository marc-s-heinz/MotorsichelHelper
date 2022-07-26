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

from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from helper.meta_classes import WidgetInterface

class DisclaimerView(QWidget, QObject, WidgetInterface):
    """view class for showing the disclaimer once for every user

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface (class): provides abstract class methods for setting the icons and updating the view
    """
    closeView_Signal = pyqtSignal()

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.closeSignalState = False

        self.setWindowTitle('Welcome')
        self.v_box = QVBoxLayout()
        self.setLayout(self.v_box)

        self.textLabel = QLabel()
        self.v_box.addWidget(self.textLabel)
        self.v_box.addSpacing(20)

        self.close_button = QPushButton('Agree and Close')
        self.v_box.addWidget(self.close_button)
        self.close_button.clicked.connect(self.reqClose)      

    def reqClose(self):
        """emits a signal to request closing of the view
        """
        self.closeView_Signal.emit()

    def closeEvent(self, event):
        """handles closing of the view

        Args:
            event (event): gets triggered when view gets closed
        """
        if not self.closeSignalState:
            self.closeView_Signal.emit()
        else:
            event.accept()