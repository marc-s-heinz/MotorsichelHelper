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

from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from helper.meta_classes import WidgetInterface

class StartupView(QWidget, QObject, WidgetInterface):
    """class for the startup view

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface ([type]): provides abstract class methods for setting the icons and updating the view
    """
    apply_Signal = pyqtSignal()

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.signalState = False

        self.explanation_text = (
            'Information is just needed for the filenames of exported data.\n'
            'If not wanted just click \"Apply\" to close the Window.\n\n'
            'Information can also be provided later\n'
            '(Settings -> Manufacturer and Model)')

        self.setWindowTitle('Engine information')
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.explanation_label = QLabel(self.explanation_text)
        self.grid_layout.addWidget(self.explanation_label, 1, 1, 1, 2)

        self.manufacturer_label = QLabel('Manufacturer')
        self.manufacturer_input = QLineEdit()
        self.grid_layout.addWidget(self.manufacturer_label, 2, 1)
        self.grid_layout.addWidget(self.manufacturer_input, 2, 2)

        self.model_label = QLabel('Model')
        self.model_input = QLineEdit()
        self.grid_layout.addWidget(self.model_label, 3, 1)
        self.grid_layout.addWidget(self.model_input, 3, 2)

        self.apply_button = QPushButton('Apply')
        self.grid_layout.addWidget(self.apply_button, 4, 1)
        self.apply_button.clicked.connect(self.apply)

    def apply(self):
        """emits an apply signal
        """
        self.apply_Signal.emit()

    def closeEvent(self, event):
        """method to handle closing event of the view

        Args:
            event ([type]): triggered when view gets closed
        """
        if not self.signalState:
            self.apply_Signal.emit()
        else:
            event.accept()