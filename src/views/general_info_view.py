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

class GeneralInformationView(QWidget, QObject, WidgetInterface):
    """view class for entering general information in the calibration process

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface (class): provides abstract class methods for setting the icons and updating the view
    """
    closeGenView_Signal = pyqtSignal()
    cameraOwner_Signal = pyqtSignal(str)
    cameraName_Signal = pyqtSignal(str)
    lensName_Signal = pyqtSignal(str)
    lensFocalLength_Signal = pyqtSignal(str)

    def __init__(self):
        """initiates the view
        """
        super().__init__()

        self.closeSignalState = False

        self.setWindowTitle('General Information')
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.explanation_label = QLabel('The general information is mainly needed to identify the computed calibration data.')
        self.grid_layout.addWidget(self.explanation_label, 1, 1, 1, 3)
        
        self.camera_owner_label = QLabel('Camera owner (minimum 3 letters)')
        self.input_camera_owner = QLineEdit()
        self.input_camera_owner.setMaxLength(25)
        self.input_camera_owner.setPlaceholderText('AVL Schrick')
        self.camera_owner_status = QLabel()
        self.grid_layout.addWidget(self.camera_owner_label, 2, 1)
        self.grid_layout.addWidget(self.input_camera_owner, 2, 2)
        self.grid_layout.addWidget(self.camera_owner_status, 2, 3)
        self.input_camera_owner.editingFinished.connect(self.cameraOwnerInput)
        
        self.camera_name_label = QLabel('Camera name (minimum 3 letters)')
        self.input_camera_name = QLineEdit()
        self.input_camera_name.setMaxLength(25)
        self.input_camera_name.setPlaceholderText('Canon Rebel T3i')
        self.camera_name_status = QLabel()
        self.grid_layout.addWidget(self.camera_name_label, 3, 1)
        self.grid_layout.addWidget(self.input_camera_name, 3, 2)
        self.grid_layout.addWidget(self.camera_name_status, 3, 3)
        self.input_camera_name.editingFinished.connect(self.cameraNameInput)

        self.lens_name_label = QLabel('Lens name (minimum 3 letters)')
        self.input_lens_name = QLineEdit()
        self.input_lens_name.setMaxLength(25)
        self.input_lens_name.setPlaceholderText('Canon EF 50mm')
        self.lens_name_status = QLabel()
        self.grid_layout.addWidget(self.lens_name_label, 4, 1)
        self.grid_layout.addWidget(self.input_lens_name, 4, 2)
        self.grid_layout.addWidget(self.lens_name_status, 4, 3)
        self.input_lens_name.editingFinished.connect(self.lensNameInput)

        self.lens_focal_length_label = QLabel('Lens focal length (minimum 2 numbers)')
        self.input_lens_focal_length = QLineEdit()
        self.input_lens_focal_length.setMaxLength(25)
        self.input_lens_focal_length.setPlaceholderText('50mm')
        self.lens_focal_length_status = QLabel()
        self.grid_layout.addWidget(self.lens_focal_length_label, 5, 1)
        self.grid_layout.addWidget(self.input_lens_focal_length, 5, 2)
        self.grid_layout.addWidget(self.lens_focal_length_status, 5, 3)
        self.input_lens_focal_length.editingFinished.connect(self.lensFocalLengthInput)

        self.close_button = QPushButton('Apply and Close')
        self.grid_layout.addWidget(self.close_button, 6, 2)
        self.close_button.clicked.connect(self.reqClose)

    def cameraOwnerInput(self):
        """emits a signal when input was entered, with input as parameter, input is camera owner
        """
        input = self.input_camera_owner.text()
        if len(input) >= 3:
            input.replace(' ', '_')
            self.cameraOwner_Signal.emit(input)

    def cameraNameInput(self):
        """emits a signal when input was entered, with input as parameter, input is camera model
        """
        input = self.input_camera_name.text()
        if len(input) >= 3:
            input.replace(' ', '_')
            self.cameraName_Signal.emit(input)

    def lensNameInput(self):
        """emits a signal when input was entered, with input as parameter, input is lens model
        """
        input = self.input_lens_name.text()
        if len(input) >= 3:
            input.replace(' ', '_')
            self.lensName_Signal.emit(input)

    def lensFocalLengthInput(self):
        """emits a signal when input was entered, with input as parameter, input is focal length of lens
        """
        input = self.input_lens_focal_length.text()
        if len(input) >= 2:
            input.replace(' ', '_')
            self.lensFocalLength_Signal.emit(input)

    def reqClose(self):
        """emits a signal to request closing the view
        """
        self.closeGenView_Signal.emit()

    def closeEvent(self, event):
        """handles closing process of the view

        Args:
            event ([type]): triggered when view gets closed
        """
        if not self.closeSignalState:
            self.closeGenView_Signal.emit()
        else:
            event.accept()