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

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject

from model.model import DataModel
from views.main_view import MainView
from controller.calibration_controller import CalibrationController
from views.calibration_view import CalibrationView
from controller.setting_controller import SettingController
from views.setting_view import SettingView
from controller.process_controller import ProcessController
from views.process_view import ProcessView
from controller.correction_controller import CorrectionController
from views.correction_view import CorrectionView
from controller.disclaimer_controller import DisclaimerController
from views.disclaimer_view import DisclaimerView
from controller.startup_controller import StartupController
from views.startup_view import StartupView

class MainController(QObject):
    """controller class for the main view

    Args:
        QObject ([type]): [description]
    """
    def __init__(self, model: DataModel, view: MainView):
        """initiates the controller

        Args:
            model (DataModel): reference to model instance
            view (MainView): reference to view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        self.status_icon_none, self.status_icon_okay, self.status_icon_wait, self.status_icon_fail = model.getStatusIcons()
        self.view.calViewStateLabel.setPixmap(self.status_icon_none)
        self.view.chessboardImage_label.setPixmap(self.status_icon_none)
        self.view.imageLoadState_label.setPixmap(self.status_icon_none)
        self.view.processState_label.setPixmap(self.status_icon_none)
        self.view.refImgListState_label.setPixmap(self.status_icon_none)
        self.view.correctState_label.setPixmap(self.status_icon_none)
        self.view.exportState_label.setPixmap(self.model.status_icon_none)

        self.view.showCal_Signal.connect(self.showCalibrationView)
        self.view.loadCal_Signal.connect(self.loadCalibrationData)
        self.model.calibrationState_Signal.connect(self.updateCalibrationState)
        self.view.loadCbImg_Signal.connect(self.loadChessboardObjectImage)
        self.model.chessboardImageState_Signal.connect(self.calculateDistanceAndRatio)
        self.view.loadObjImg_Signal.connect(self.loadObjectImage)
        self.model.imageLoadState_Signal.connect(self.objectImageSet)
        self.view.showProcess_Signal.connect(self.showProcessView)
        self.view.generateReference_Signal.connect(self.generateReference)
        self.view.printReference_Signal.connect(self.printReference)
        self.view.correctDiameter_Signal.connect(self.showCorrectionView)
        self.view.exportData_Signal.connect(self.exportData)
        self.model.exportDataState_Signal.connect(self.dataExported)
        self.view.reqClose_Signal.connect(self.closeView)
        self.view.showStartupView_Signal.connect(self.showStartupView)
        self.view.loadSettings_Signal.connect(self.loadSettings)
        self.view.showSettings_Signal.connect(self.showSettingsView)
        self.view.showDisclaimer_Signal.connect(self.showDisclaimerView)
        self.view.showManual_Signal.connect(self.showManual)
        self.view.showLicense_Signal.connect(self.showLicense)
        
        self.view.show()

        if not self.model.wasDisclaimerAccepted:
            self.showDisclaimerView()
        self.model.startupDone = True

        if self.model.showNewInfoAtStartup:
            self.showStartupView()

    def noSettingsWarning(self):
        """Shows a message if settings were not loaded
        """
        _ = QMessageBox.warning(self.view, 'No settings loaded!', 'No settings were loaded,\nyou can load settings manually.\n(Optional)\nSettings -> Load Settings',
                QMessageBox.Ok, QMessageBox.Ok)

    def showStartupView(self):
        """initiates and shows the startup view, hides main view
        """
        self.startup_controller = StartupController(self.model, StartupView())
        self.startup_controller.viewClose_Signal.connect(self.startupViewClosed)
        self.view.setVisible(False)
    def startupViewClosed(self):
        """restores visibility of main view when startup view is closed
        """
        self.view.setVisible(True)
        self.startup_controller = None
    
    def loadSettings(self):
        """loads the settings
        """
        self.model.loadSettings()

    def showSettingsView(self):
        """opens the settings view and hides main view
        """
        self.setting_controller = SettingController(self.model, SettingView())
        self.setting_controller.viewClose_Signal.connect(self.settingViewClosed)
        self.view.setVisible(False)
    def settingViewClosed(self):
        """resores visibility of main view when settings view is closed
        """
        self.view.setVisible(True)
        self.setting_controller = None

    def showDisclaimerView(self):
        """shows the disclaimer view and hides main view
        """
        self.disclaimer_controller = DisclaimerController(self.model, DisclaimerView())
        self.disclaimer_controller.viewClose_Signal.connect(self.disclaimerViewClosed)
        self.view.setVisible(False)
    def disclaimerViewClosed(self):
        """restores visibility of main view when disclaimer view is closed,
        also saves state of accepted disclaimer
        """
        self.view.setVisible(True)
        self.disclaimer_controller = None
        self.noSettingsWarning()

    def showManual(self):
        """opens the manual as pdf file
        """
        ret = self.model.openPDFinExternalViewer(fileName=self.model.manualName)
        if not ret == True:
            _ = QMessageBox.warning(self.view, 'File not Found!', 'Manual not found!\nSearch for documentation manually.',
                QMessageBox.Ok, QMessageBox.Ok)

    def showLicense(self):
        """opens the license as pdf file
        """
        ret = self.model.openPDFinExternalViewer(fileName=self.model.licenseName)
        if not ret == True:
            _ = QMessageBox.warning(self.view, 'File not Found!', 'License not found!\nSearch for license manually.',
                QMessageBox.Ok, QMessageBox.Ok)

    def showCalibrationView(self):
        """initiates the calibration view and hides main view
        """
        self.view.calViewStateLabel.setPixmap(self.status_icon_wait)
        self.cal_controller = CalibrationController(self.model, CalibrationView())
        self.cal_controller.viewClose_Signal.connect(self.calViewClosed)
        self.view.setVisible(False)
    def calViewClosed(self, state):
        """sets calibration status in main view, sets main view visible when calibration view
        is closed
        Args:
            state (bool): state of calibration process
        """
        if state == True:
            self.view.calViewStateLabel.setPixmap(self.status_icon_okay)
        else:
            self.view.calViewStateLabel.setPixmap(self.status_icon_fail)
        self.view.setVisible(True)
        self.cal_controller = None
    
    def loadCalibrationData(self):
        """loads calibration data
        """
        self.view.calViewStateLabel.setPixmap(self.status_icon_wait)
        self.model.loadCalibrationData()

    def updateCalibrationState(self, state):
        """updates the calibration state and enables next button

        Args:
            state (bool): calibration state
        """
        if state == True:
            self.view.calViewStateLabel.setPixmap(self.status_icon_okay)
            self.view.objImage_button.setEnabled(True)
        else:
            self.view.calViewStateLabel.setPixmap(self.status_icon_fail)
    
    def loadChessboardObjectImage(self):
        """loads an image of an engine with a chessboard attached to it
        """
        self.view.chessboardImage_label.setPixmap(self.status_icon_wait)
        image = self.model.loadImagefromFile()
        if image is not None and self.model.calibrationState:
            croppedChessboardImage, _ = self.model.undistortAndCropImage(image=image)
            if croppedChessboardImage.any():
                self.model.chessboardImage = croppedChessboardImage
                self.model.setChessboardImageState(True)
                
    def calculateDistanceAndRatio(self):
        """calculates the distance camera-object and a mm-per-pixel-ratio
        """
        result = self.model.calcCameraObjectDistance()
        if result == True:
            self.view.chessboardImage_label.setPixmap(self.status_icon_okay)
            self.view.image_button.setEnabled(True)
        else:
            self.view.chessboardImage_label.setPixmap(self.status_icon_fail)

    def loadObjectImage(self):
        """loads an image with colored areas of an engine
        """
        self.view.imageLoadState_label.setPixmap(self.status_icon_wait)
        image = self.model.loadImagefromFile()
        if image is not None:
            self.model.originalImageSize_preCrop = image.shape
            croppedObjectImage, _ = self.model.undistortAndCropImage(image=image)
            if croppedObjectImage.any():
                self.model.originalImageSize_afterCrop = croppedObjectImage.shape
                self.model.originalImage = croppedObjectImage
                self.model.setImageLoadState(True)
                
    def objectImageSet(self, state):
        """sets a state for loading an engine image
        Args:
            state (bool): state of loading the image
        """
        if state == True:
            self.view.imageLoadState_label.setPixmap(self.status_icon_okay)
            self.view.process_button.setEnabled(True)
        else:
            self.view.imageLoadState_label.setPixmap(self.status_icon_fail)

    def showProcessView(self):
        """shows the processing view where the image is manipulated and information are extracted,
        hides the main view
        """
        self.view.processState_label.setPixmap(self.status_icon_wait)
        self.process_controller = ProcessController(self.model, ProcessView())
        self.process_controller.viewClose_Signal.connect(self.processViewClosed)
        self.view.setVisible(False)
    def processViewClosed(self, state):
        """restores visibility if process view is closed, enables the next button if processing was successfull
        Args:
            state (bool): state of processing process
        """
        if state == True:
            self.view.processState_label.setPixmap(self.status_icon_okay)
            self.view.generate_button.setEnabled(True)
        else:
            self.view.processState_label.setPixmap(self.status_icon_fail)
        self.view.setVisible(True)
        self.process_controller = None

    def generateReference(self):
        """generates a reference image and list, enables next button
        """
        self.view.refImgListState_label.setPixmap(self.status_icon_wait)
        result = self.model.saveReferenceImageAndList()
        if result == True:
            self.view.refImgListState_label.setPixmap(self.status_icon_okay)
            self.view.print_button.setEnabled(True)
            self.view.correct_button.setEnabled(True)
            self.view.export_button.setEnabled(True)
        else:
            self.view.refImgListState_label.setPixmap(self.status_icon_fail)

    def printReference(self):
        """prints the reference image and list
        """
        result = self.model.referencePrinter()

    def showCorrectionView(self):
        """initiates a view for correcting the found diameters, hides the main view
        """
        self.view.correctState_label.setPixmap(self.status_icon_wait)
        self.correct_controller = CorrectionController(self.model, CorrectionView())
        self.correct_controller.viewClose_Signal.connect(self.correctionViewClosed)
        self.view.setVisible(False)
    def correctionViewClosed(self, state):
        """restores visibility of main view when correction view is closed and sets a state that correction was opened

        Args:
            state (bool): correction view was opened, True even if no diameter was changed
        """
        if state == True:
            self.view.correctState_label.setPixmap(self.status_icon_okay)
        else:
            self.view.correctState_label.setPixmap(self.status_icon_fail)
        self.view.export_button.setEnabled(True)
        self.view.setVisible(True)
        self.correct_controller = None

    def exportData(self):
        """exports the calculated data to a dxf file
        """
        self.view.exportState_label.setPixmap(self.model.status_icon_wait)
        result = self.model.exportToDXF()
        self.model.setExportDataState(result)
    def dataExported(self, state):
        if state == True:
            self.view.exportState_label.setPixmap(self.model.status_icon_okay)
        else:
            self.view.exportState_label.setPixmap(self.model.status_icon_fail)

    def closeView(self):
        """saves settings and closes the programm
        """
        result = self.model.saveSettings()
        self.view.closeSignalState = True
        self.view.close()