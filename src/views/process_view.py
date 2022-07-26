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

from PyQt5.QtWidgets import QGridLayout, QLabel, QMessageBox, QPushButton, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from helper.meta_classes import WidgetInterface

class ProcessView(QWidget, QObject, WidgetInterface):
    """view class for processing the image

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface ([type]):  provides abstract class methods for setting the icons and updating the view
    """
    openBinaryView_Signal = pyqtSignal()
    findContours_Signal = pyqtSignal()
    findCenter_Signal = pyqtSignal()
    setReference_Signal = pyqtSignal()
    closeView_Signal = pyqtSignal()
    undoChanges_Signal = pyqtSignal()
    
    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.processState = False

        self.setWindowTitle('Process View')
        self.grid_layout =QGridLayout()
        self.setLayout(self.grid_layout)

        self.binarize_header = QLabel('Binarize image by selecting HSV values.')
        self.adj_binarize_button = QPushButton('Binarize')
        self.binarizeState_label = QLabel()
        self.grid_layout.addWidget(self.binarize_header, 1, 1)
        self.grid_layout.addWidget(self.adj_binarize_button, 1, 2)
        self.grid_layout.addWidget(self.binarizeState_label, 1, 4)
        self.adj_binarize_button.clicked.connect(self.showBinarizeView)

        self.contours_header = QLabel('Find contours in the binarized image')
        self.contours_button = QPushButton('Contours')
        self.contoursState_label = QLabel()
        self.grid_layout.addWidget(self.contours_header, 2, 1)
        self.grid_layout.addWidget(self.contours_button, 2, 2)
        self.grid_layout.addWidget(self.contoursState_label, 2, 4)
        self.contours_button.clicked.connect(self.findContours)
        self.contours_button.setEnabled(False)

        self.center_header = QLabel('Find the center of the object\nor select a coordinate origin')
        self.center_button = QPushButton('Find Center')
        self.setOrigin_button = QPushButton('Set Origin')
        self.referenceState_label = QLabel()
        self.grid_layout.addWidget(self.center_header, 3, 1)
        self.grid_layout.addWidget(self.center_button, 3, 2)
        self.grid_layout.addWidget(self.setOrigin_button, 3, 3)
        self.grid_layout.addWidget(self.referenceState_label, 3, 4)
        self.center_button.clicked.connect(self.findCenter)
        self.setOrigin_button.clicked.connect(self.setReference)
        self.center_button.setEnabled(False)
        self.setOrigin_button.setEnabled(False)

        self.close_button = QPushButton('Apply and Close')
        self.grid_layout.addWidget(self.close_button, 8, 1)
        self.close_button.clicked.connect(self.reqClose)

    def showBinarizeView(self):
        """shows the binarize view
        """
        self.openBinaryView_Signal.emit()

    def findContours(self):
        """tries to find contours in the image
        """
        self.findContours_Signal.emit()

    def findCenter(self):
        """tries to find a center in the image
        """
        self.findCenter_Signal.emit()

    def setReference(self):
        """sets a reference point in the image
        """
        self.setReference_Signal.emit()

    def reqClose(self):
        """requests closing of the view
        """
        self.closeView_Signal.emit()

    def closeEvent(self, event):
        """method to handle closing event of the view

        Args:
            event ([type]): triggered when view gets closed
        """
        if self.processState == True:
            event.accept()
        else:
            reply = QMessageBox.question(self, 'Discard progress?', 'Processing not finished.\nDiscard any progress?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.undoChanges_Signal.emit()
                event.accept()
            else:
                event.ignore()