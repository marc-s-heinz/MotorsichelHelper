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

from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from helper.meta_classes import WidgetInterface

class SettingView(QWidget, QObject, WidgetInterface):
    """class for the settings view

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface ([type]): provides abstract class methods for setting the icons and updating the view
    """
    closeView_Signal = pyqtSignal()
    chooseWorkspace_Signal = pyqtSignal()
    scaleFactor_Signal = pyqtSignal()
    roundnessThreshold_Signal = pyqtSignal()
    maxScreenSize_Signal = pyqtSignal()
    showDuration_Signal = pyqtSignal()
    toggleStartupView_Signal = pyqtSignal()
    morphSelect_Signal = pyqtSignal(str)

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.closeSignalState = False

        self.setWindowTitle('Setting')
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.dir_label = QLabel('Select a working directory')
        self.dir_button = QPushButton('Select')
        self.grid_layout.addWidget(self.dir_label, 1, 1)
        self.grid_layout.addWidget(self.dir_button, 1, 2)
        self.dir_button.clicked.connect(self.chooseDir)

        self.path_label = QLabel('Current workspace:')
        self.path_info = QLabel()
        self.grid_layout.addWidget(self.path_label, 2, 1)
        self.grid_layout.addWidget(self.path_info, 2, 2)

        self.startup_label = QLabel('Show window for new engine at startup?')
        self.startup_checkbox = QCheckBox()
        self.grid_layout.addWidget(self.startup_label, 3, 1)
        self.grid_layout.addWidget(self.startup_checkbox, 3, 2)
        self.startup_checkbox.toggled.connect(self.toggleStartupView)

        self.scale_label = QLabel('Scale factor for all images [0.0 - 1.0]')
        self.scale_input = QLineEdit()
        self.scale_input.setMaxLength(4)
        self.grid_layout.addWidget(self.scale_label, 4, 1)
        self.grid_layout.addWidget(self.scale_input, 4, 2)
        self.scale_input.editingFinished.connect(self.scaleInput)

        self.screen_label = QLabel('Maximum area any image should occupy while shown on screen. (<1.0 == 100%)')
        self.screen_input = QLineEdit()
        self.screen_input.setMaxLength(4)
        self.grid_layout.addWidget(self.screen_label, 5, 1)
        self.grid_layout.addWidget(self.screen_input, 5, 2)
        self.screen_input.editingFinished.connect(self.screenInput)

        self.show_label = QLabel('Duration any image should be shown on screen before moving on (in ms) or type in None.')
        self.show_input = QLineEdit()
        self.show_input.setMaxLength(5)
        self.grid_layout.addWidget(self.show_label, 6, 1)
        self.grid_layout.addWidget(self.show_input, 6, 2)
        self.show_input.editingFinished.connect(self.showDurationInput)

        self.roundness_label = QLabel('Roundness threshold for deciding whether a contour is a drill hole (0.00 < r < 1.00)')
        self.roundness_input = QLineEdit()
        self.roundness_input.setMaxLength(4)
        self.grid_layout.addWidget(self.roundness_label, 7, 1)
        self.grid_layout.addWidget(self.roundness_input, 7, 2)
        self.roundness_input.editingFinished.connect(self.roundnessInput)

        self.morph_label = QLabel('Method used for morphological operation on binary image')
        self.morph_combobox = QComboBox()
        self.grid_layout.addWidget(self.morph_label, 8, 1)
        self.grid_layout.addWidget(self.morph_combobox, 8, 2)
        self.morph_combobox.activated[str].connect(self.morphSelect)

        self.close_button = QPushButton('Apply and close')
        self.grid_layout.addWidget(self.close_button, 9, 1)
        self.close_button.clicked.connect(self.reqClose)

    def chooseDir(self):
        """emits a signal for choosing a workspace directory
        """
        self.chooseWorkspace_Signal.emit()
    
    def scaleInput(self):
        """emits a signal when a new scale factor was entered
        """
        self.scaleFactor_Signal.emit()

    def roundnessInput(self):
        """emits a signal when a new roundness threshold was entered
        """
        self.roundnessThreshold_Signal.emit()

    def screenInput(self):
        """emits a signal when a new maximum screen size for images was entered
        """
        self.maxScreenSize_Signal.emit()

    def showDurationInput(self):
        """emits a signal when a duration for showing images was entered
        """
        self.showDuration_Signal.emit()

    def toggleStartupView(self):
        """emits a signal for toggling the startup view
        """
        self.toggleStartupView_Signal.emit()

    def morphSelect(self, listItem):
        """emits a signal for morphological operation selection with listItem as parameter

        Args:
            listItem (str): selected list item
        """
        self.morphSelect_Signal.emit(listItem)

    def reqClose(self):
        """requests closing of the settings view
        """
        self.closeView_Signal.emit()
    def closeEvent(self, event):
        """method for handling closing of the view

        Args:
            event ([type]): triggered when view gets closed
        """
        if not self.closeSignalState:
            self.reqClose()
        else:
            event.accept()