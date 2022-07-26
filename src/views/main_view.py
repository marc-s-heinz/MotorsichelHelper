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

from PyQt5.QtWidgets import QAction, QGridLayout, QLabel, QMainWindow, QPushButton, QWidget
from PyQt5.QtCore import QObject, pyqtSignal
import sys

from helper.meta_classes import WidgetInterface

class MainView(QMainWindow, QObject, WidgetInterface):
    """view class of the main window

    Args:
        QMainWindow ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface ([type]): provides abstract class methods for setting the icons and updating the view
    """
    showCal_Signal = pyqtSignal()
    loadCal_Signal = pyqtSignal()
    loadCbImg_Signal = pyqtSignal()
    loadObjImg_Signal = pyqtSignal()
    showProcess_Signal = pyqtSignal()
    generateReference_Signal = pyqtSignal()
    printReference_Signal = pyqtSignal()
    correctDiameter_Signal = pyqtSignal()
    exportData_Signal = pyqtSignal()
    reqClose_Signal = pyqtSignal()
    showStartupView_Signal = pyqtSignal()
    loadSettings_Signal = pyqtSignal()
    showSettings_Signal = pyqtSignal()
    showDisclaimer_Signal = pyqtSignal()
    showManual_Signal = pyqtSignal()
    showLicense_Signal = pyqtSignal()

    def __init__(self):
        """initiates the view"""
        super().__init__()

        self.closeSignalState = False

        self.setupView()
        self.setupMenu()
        

    def setupView(self):
        """initiates the content area of the view
        """
        self.setWindowTitle('AVL Schrick - MotorsichelHelper')
        self.grid_layout = QGridLayout()

        self.calHeader = QLabel('Calibrate Camera or load calibration data')
        self.calView_button = QPushButton('Calibrate')
        self.loadCal_button = QPushButton('Load calibration data')
        self.calViewStateLabel = QLabel('False')
        self.grid_layout.addWidget(self.calHeader, 1, 1)
        self.grid_layout.addWidget(self.calView_button, 1, 2)
        self.grid_layout.addWidget(self.loadCal_button, 1, 3)
        self.grid_layout.addWidget(self.calViewStateLabel, 1, 4)
        self.calView_button.clicked.connect(self.calView)
        self.loadCal_button.clicked.connect(self.loadCal)

        self.objImage_header = QLabel('Load image with object and chessboard as reference')
        self.objImage_button = QPushButton('Load')
        self.chessboardImage_label = QLabel()
        self.grid_layout.addWidget(self.objImage_header, 2, 1)
        self.grid_layout.addWidget(self.objImage_button, 2, 2)
        self.grid_layout.addWidget(self.chessboardImage_label, 2, 4)
        self.objImage_button.clicked.connect(self.loadChessboardImage)
        self.objImage_button.setEnabled(False)

        self.image_header = QLabel('Load object image from file')
        self.image_button = QPushButton('Image')
        self.imageLoadState_label = QLabel()
        self.grid_layout.addWidget(self.image_header, 3, 1)
        self.grid_layout.addWidget(self.image_button, 3, 2)
        self.grid_layout.addWidget(self.imageLoadState_label, 3, 4)
        self.image_button.clicked.connect(self.loadObjImage)
        self.image_button.setEnabled(False)

        #subview where image is edited in steps
        self.process_header = QLabel('Process image and extract information')
        self.process_button = QPushButton('Process')
        self.processState_label = QLabel()
        self.grid_layout.addWidget(self.process_header, 4, 1)
        self.grid_layout.addWidget(self.process_button, 4, 2)
        self.grid_layout.addWidget(self.processState_label, 4, 4)
        self.process_button.clicked.connect(self.procView)
        self.process_button.setEnabled(False)

        #generate and print a reference image and list
        self.print_header = QLabel('Generate and print a reference image and list')
        self.generate_button = QPushButton('Generate')
        self.print_button = QPushButton('Print')
        self.refImgListState_label = QLabel()
        self.grid_layout.addWidget(self.print_header, 5, 1)
        self.grid_layout.addWidget(self.generate_button, 5, 2)
        self.grid_layout.addWidget(self.print_button, 5, 3)
        self.grid_layout.addWidget(self.refImgListState_label, 5, 4)
        self.generate_button.clicked.connect(self.generateReference)
        self.print_button.clicked.connect(self.printReference)
        self.generate_button.setEnabled(False)
        self.print_button.setEnabled(False)

        #adjust found diameters
        self.correct_header = QLabel('Correct hole diameter manually')
        self.correct_button = QPushButton('Correct')
        self.correctState_label = QLabel()
        self.grid_layout.addWidget(self.correct_header, 6, 1)
        self.grid_layout.addWidget(self.correct_button, 6, 2)
        self.grid_layout.addWidget(self.correctState_label, 6, 4)
        self.correct_button.clicked.connect(self.corView)
        self.correct_button.setEnabled(False)

        #export data
        self.export_header = QLabel('Export found information to a dxf-file\nfor further use in a CAD program')
        self.export_button = QPushButton('Export')
        self.exportState_label = QLabel()
        self.grid_layout.addWidget(self.export_header, 7, 1)
        self.grid_layout.addWidget(self.export_button, 7, 2)
        self.grid_layout.addWidget(self.exportState_label, 7, 4)
        self.export_button.clicked.connect(self.exportData)
        self.export_button.setEnabled(False)

        self.close_button = QPushButton('Close Program')
        self.grid_layout.addWidget(self.close_button, 8, 1)
        self.close_button.clicked.connect(self.reqClose)

        self.container = QWidget()
        self.container.setLayout(self.grid_layout)
        self.setCentralWidget(self.container)

    def setupMenu(self):
        """initiates a menu bar for the main window
        """
        self.manufacturer_act = QAction('Manufacturer and model', self)
        self.manufacturer_act.triggered.connect(self.showStartupView)
        self.loadSettings_act = QAction('Load Settings', self)
        self.loadSettings_act.triggered.connect(self.loadSettings)
        self.settings_act = QAction('Open Settings Window', self)
        self.settings_act.triggered.connect(self.showSettings)

        self.disclaimer_act = QAction('Disclaimer', self)
        self.disclaimer_act.triggered.connect(self.showDisclaimer)
        self.documentation_act = QAction('Dokumentation', self)
        self.documentation_act.triggered.connect(self.showManual)
        self.license_act = QAction('License', self)
        self.license_act.triggered.connect(self.showLicense)
        #create menu bar
        self.menu_bar = self.menuBar()
        self.menu_bar.setNativeMenuBar(False)
        #create help menu and add actions
        self.settings_menu = self.menu_bar.addMenu('Settings')
        self.settings_menu.addAction(self.manufacturer_act)
        self.settings_menu.addAction(self.loadSettings_act)
        self.settings_menu.addAction(self.settings_act)

        self.help_menu = self.menu_bar.addMenu('Help')
        self.help_menu.addAction(self.disclaimer_act)
        self.help_menu.addAction(self.documentation_act)
        self.help_menu.addAction(self.license_act)

    def showStartupView(self):
        """emits a signal for showing the startup view
        """
        self.showStartupView_Signal.emit()
    def loadSettings(self):
        """emits a signal for loading settings
        """
        self.loadSettings_Signal.emit()
    def showSettings(self):
        """emits a signal for showing the settings view
        """
        self.showSettings_Signal.emit()
    def showDisclaimer(self):
        """emits a signal for showing the disclaimer view
        """
        self.showDisclaimer_Signal.emit()
    def showManual(self):
        """emits a signal for opening the manual
        """
        self.showManual_Signal.emit()
    def showLicense(self):
        """emits a signal for showing the license
        """
        self.showLicense_Signal.emit()

    def calView(self):
        """emits a signal for opening the calibration view
        """
        self.showCal_Signal.emit()
    def loadCal(self):
        """emits a signal for loading calibration data
        """
        self.loadCal_Signal.emit()
    def loadChessboardImage(self):
        """emits a signal for loading chessboard images"""
        self.loadCbImg_Signal.emit()
    def loadObjImage(self):
        """Loads an image of an engine with color-highlighted areas"""
        self.loadObjImg_Signal.emit()
    def procView(self):
        """opens the processing view
        """
        self.showProcess_Signal.emit()
    def generateReference(self):
        """Generates an reference image and list for checking the diameters
        """
        self.generateReference_Signal.emit()
    def printReference(self):
        """prints the generated reference image and list
        """
        self.printReference_Signal.emit()
    def corView(self):
        """opens a view for correcting diameters"""
        self.correctDiameter_Signal.emit()
    def exportData(self):
        """exports the calculated data to an dxf drawing for use in a CAD programm
        """
        self.exportData_Signal.emit()
    def reqClose(self):
        """Requests closing of the view"""
        self.reqClose_Signal.emit()
    def closeEvent(self, event):
        """Closes the view and exits the programm"""
        if not self.closeSignalState:
            self.reqClose()
        else:
            sys.exit()