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

from PyQt5.QtCore import QObject, pyqtSignal

from model.model import DataModel
from views.calibration_view import CalibrationView
from views.general_info_view import GeneralInformationView
from controller.general_info_controller import GeneralInformationController

class CalibrationController(QObject):
    """controller class for the calibration view
    """
    viewClose_Signal = pyqtSignal(bool)

    def __init__(self, model: DataModel, view: CalibrationView):
        """initiates the controller

        Args:
            model (DataModel): reference to the model
            view (CalibrationView): reference to the view
        """
        super().__init__()
        self.model = model
        self.view = view

        self.genInfo = False
        self.calImg = False
        self.cbRows = False
        self.cbColumns = False
        self.cbSize = False
        self.calState = False

        self.imageLoadResult = False

        self.status_icon_none, self.status_icon_okay, self.status_icon_wait, self.status_icon_fail = model.getStatusIcons()
        self.view.general_information_status.setPixmap(self.status_icon_none)
        self.view.open_cal_dir_status.setPixmap(self.status_icon_none)
        self.view.input_cb_rows_status.setPixmap(self.status_icon_none)
        self.view.input_cb_cols_status.setPixmap(self.status_icon_none)
        self.view.input_cb_square_status.setPixmap(self.status_icon_none)
        self.view.calibration_status_label.setPixmap(self.status_icon_none)
        self.view.save_status.setPixmap(self.status_icon_none)

        self.view.closeView_Signal.connect(self.calViewClosed)
        self.view.showGeneralInfo_Signal.connect(self.showGeneralInfoView)
        self.view.loadCalImages_Signal.connect(self.openCalImages)
        self.view.chessboardRows_Signal.connect(self.setChessboardRows)
        self.view.chessboardColumns_Signal.connect(self.setChessboardColumns)
        self.view.chessboardSize_Signal.connect(self.setChessboardSize)
        self.view.calculateCalData_Signal.connect(self.calculateCalData)
        self.model.calibrationState_Signal.connect(self.setCalState)
        self.view.saveCalData_Signal.connect(self.saveCalData)
        self.view.undoChanges_Signal.connect(self.undoChanges)

        self.view.show()

    def showGeneralInfoView(self):
        """Creates a controller and view for entering general information
        hides calibration view while general information view is opened
        """
        self.view.general_information_status.setPixmap(self.status_icon_wait)
        self.generalInfo_controller = GeneralInformationController(self.model, GeneralInformationView())
        self.generalInfo_controller.viewClose_Signal.connect(self.genViewClosed)
        self.view.setVisible(False)

    def genViewClosed(self, state):
        """handles closing of the general information view
        sets the state for provided information and sets calibration view visible

        Args:
            state (bool): state of general information, true when all necessary information were provided
        """
        if state == True:
            self.genInfo = True
            self.view.general_information_status.setPixmap(self.status_icon_okay)
            self.view.open_cal_image_dir_button.setEnabled(True)
        else:
            self.view.general_information_status.setPixmap(self.status_icon_fail)
        self.view.setVisible(True)
        self.generalInfo_controller = None

    def openCalImages(self):
        """method for opening the calibration images
        """
        self.view.open_cal_dir_status.setPixmap(self.status_icon_wait)
        result = self.model.loadCalImagesFromDirectory()
        if result == True:
            self.calImg = True
            self.view.open_cal_dir_status.setPixmap(self.status_icon_okay)
            self.view.input_chessboard_rows.setEnabled(True)
        else:
            self.view.open_cal_dir_status.setPixmap(self.status_icon_fail)        

    def setChessboardRows(self, rows):
        """method that sets the number of the inner chessboard rows in the model
        and handles the status of it

        Args:
            rows (int): number of inner chessboard rows, e.g. the borders between the chessboard rows
        """
        self.cbRows = True
        self.view.input_cb_rows_status.setPixmap(self.status_icon_okay)
        self.model.chessboardRows = rows
        self.view.input_chessboard_columns.setEnabled(True)

    def setChessboardColumns(self, columns):
        """method that sets the number of the inner chessboard columns in the model
        and handles the status of it

        Args:
            columns (int): number of inner chessboard columns, e.g. the borders between the chessboard columns
        """
        self.cbColumns = True
        self.view.input_cb_cols_status.setPixmap(self.status_icon_okay)
        self.model.chessboardColumns = columns
        self.view.input_chessboard_square.setEnabled(True)

    def setChessboardSize(self, size):
        """method that sets the size of the chessboard squares in the model
        and handles the status of it

        Args:
            size (float): size of the edge of a chessboard square in mm
        """
        self.cbSize = True
        self.view.input_cb_square_status.setPixmap(self.status_icon_okay)
        self.model.chessboardSize = size
        self.view.calibration_start_button.setEnabled(True)

    def calculateCalData(self):
        """calls a method that calculates the calibration data, handles the calibration status
        """
        self.view.calibration_status_label.setPixmap(self.status_icon_wait)
        result = self.model.calculateCalibrationData()
        if result == True:
            self.view.calibration_status_label.setPixmap(self.status_icon_okay)
        else:
            self.view.calibration_status_label.setPixmap(self.status_icon_fail)
        self.model.setCalibrationState(result)

    def setCalState(self, state):
        """sets the calibration status in the view and main view

        Args:
            state (bool): calibration status
        """
        self.view.calState = state
        self.calState = state
        self.view.save_button.setEnabled(state)

    def saveCalData(self):
        """calls a method for saving the calibration data, handles save status
        """
        result = self.model.saveCalibrationData()
        if result == True:
            self.view.save_status.setPixmap(self.status_icon_okay)
        else:
            self.view.save_status.setPixmap(self.status_icon_fail)

    def undoChanges(self):
        """calls a method to reset the calibration status in the model.
        also resets the calibration status in the controller itself
        """
        result = self.model.undoCalibrationProgress()
        if result == True:
            self.genInfo = False
            self.calImg = False
            self.cbRows = False
            self.cbColumns = False
            self.cbSize = False
            self.calState = False
            self.calViewClosed()

    def calViewClosed(self):
        """method for closing the calibration view, also sets calibration status
        """
        state = self.calState
        self.model.setCalibrationState(state)
        self.viewClose_Signal.emit(state)