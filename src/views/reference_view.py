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

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QComboBox
from PyQt5.QtCore import QObject, pyqtSignal

from helper.meta_classes import WidgetInterface

class ReferenceView(QWidget, QObject, WidgetInterface):
    """view class for setting a new reference point

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface ([type]): provides abstract class methods for setting the icons and updating the view
    """
    closeView_Signal = pyqtSignal()
    setReferencePoint_Signal = pyqtSignal(str)

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.closeSignalState = False

        self.setWindowTitle('Reference View')
        self.v_box = QVBoxLayout()

        self.ref_header = QLabel('Choose a reference point')
        self.ref_combobox = QComboBox()
        self.ref_combobox.activated[str].connect(self.onSelect)
        self.image_label = QLabel()
        self.close_button = QPushButton('Apply and Close')
        self.close_button.clicked.connect(self.reqClose)

        self.v_box.addWidget(self.ref_header)
        self.v_box.addWidget(self.ref_combobox)
        self.v_box.addSpacing(5)
        self.v_box.addWidget(self.image_label)
        self.v_box.addSpacing(5)
        self.v_box.addWidget(self.close_button)
        self.setLayout(self.v_box)

    def onSelect(self, listItem):
        """emits a signal with list item for corresponding new reference point as parameter

        Args:
            listItem (str): string that represents the new reference point
        """
        self.setReferencePoint_Signal.emit(listItem)

    def reqClose(self):
        """requests closing of the view
        """
        self.closeView_Signal.emit()

    def closeEvent(self, event):
        """method to handle closing process of the view

        Args:
            event ([type]): triggered when view gets closed
        """
        if not self.closeSignalState:
            self.reqClose()
        else:
            event.accept()