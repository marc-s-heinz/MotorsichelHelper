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

from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from helper.meta_classes import WidgetInterface

class CalibrationView(QWidget, QObject, WidgetInterface):
    """view class for calibration process

    Args:
        QWidget ([type]): [description]
        QObject ([type]): [description]
        WidgetInterface (class): provides abstract class methods for setting the icons and updating the view
    """
    closeView_Signal = pyqtSignal()
    showGeneralInfo_Signal = pyqtSignal()
    loadCalImages_Signal = pyqtSignal()
    chessboardRows_Signal = pyqtSignal(int)
    chessboardColumns_Signal = pyqtSignal(int)
    chessboardSize_Signal = pyqtSignal(float)
    calculateCalData_Signal = pyqtSignal()
    saveCalData_Signal = pyqtSignal()
    undoChanges_Signal = pyqtSignal()
    
    def __init__(self):
        """initiates the calibration view
        """
        super().__init__()

        self.calState = False

        self.setWindowTitle('Calibration View')
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.general_information_header = QLabel('Enter general information about the used camera')
        self.general_information_button = QPushButton('Information')
        self.general_information_status = QLabel()
        self.grid_layout.addWidget(self.general_information_header, 1, 1)
        self.grid_layout.addWidget(self.general_information_button, 1, 2)
        self.grid_layout.addWidget(self.general_information_status, 1, 3)
        self.general_information_button.clicked.connect(self.showGeneralInformationView)

        self.open_cal_image_dir_header = QLabel('Open calibration images directory.\nAt least 10 images needed.')
        self.open_cal_image_dir_button = QPushButton('Open')
        self.open_cal_dir_status = QLabel()
        self.grid_layout.addWidget(self.open_cal_image_dir_header, 2, 1)
        self.grid_layout.addWidget(self.open_cal_image_dir_button, 2, 2)
        self.grid_layout.addWidget(self.open_cal_dir_status, 2, 3)
        self.open_cal_image_dir_button.clicked.connect(self.loadCalibrationImages)
        self.open_cal_image_dir_button.setEnabled(False)

        self.chessboard_row_header = QLabel('Number of chessboard fields in a row')
        self.input_chessboard_rows = QLineEdit()
        self.input_chessboard_rows.setMaxLength(2)
        self.input_chessboard_rows.setPlaceholderText('7')
        self.input_cb_rows_status = QLabel()
        self.grid_layout.addWidget(self.chessboard_row_header, 3, 1)
        self.grid_layout.addWidget(self.input_chessboard_rows, 3, 2)
        self.grid_layout.addWidget(self.input_cb_rows_status, 3, 3)
        self.input_chessboard_rows.editingFinished.connect(self.chessboardRowsInput)
        self.input_chessboard_rows.setEnabled(False)

        self.chessboard_column_header = QLabel('Number of chessboard fields in a collumn')
        self.input_chessboard_columns = QLineEdit()
        self.input_chessboard_columns.setMaxLength(2)
        self.input_chessboard_columns.setPlaceholderText('9')
        self.input_cb_cols_status = QLabel()
        self.grid_layout.addWidget(self.chessboard_column_header, 4, 1)
        self.grid_layout.addWidget(self.input_chessboard_columns, 4, 2)
        self.grid_layout.addWidget(self.input_cb_cols_status, 4, 3)
        self.input_chessboard_columns.editingFinished.connect(self.chessboardColumnsInput)
        self.input_chessboard_columns.setEnabled(False)

        self.chessboard_square_header = QLabel('Size of chessboard square in mm')
        self.input_chessboard_square = QLineEdit()
        self.input_chessboard_square.setMaxLength(5)
        self.input_chessboard_square.setPlaceholderText('28.75')
        self.input_cb_square_status = QLabel()
        self.grid_layout.addWidget(self.chessboard_square_header, 5, 1)
        self.grid_layout.addWidget(self.input_chessboard_square, 5, 2)
        self.grid_layout.addWidget(self.input_cb_square_status, 5, 3)
        self.input_chessboard_square.editingFinished.connect(self.chessboardSquareInput)
        self.input_chessboard_square.setEnabled(False)

        self.calibration_start_header = QLabel('Generate calibration data')
        self.calibration_start_button = QPushButton('Start')
        self.calibration_status_label = QLabel()
        self.grid_layout.addWidget(self.calibration_start_header, 6, 1)
        self.grid_layout.addWidget(self.calibration_start_button, 6, 2)
        self.grid_layout.addWidget(self.calibration_status_label, 6, 3)
        self.calibration_start_button.clicked.connect(self.calculateCalibrationData)
        self.calibration_start_button.setEnabled(False)

        self.save_file_header = QLabel('Save calibration data for later use (optional)')
        self.save_button = QPushButton('Save')
        self.save_status = QLabel()
        self.grid_layout.addWidget(self.save_file_header, 7, 1)
        self.grid_layout.addWidget(self.save_button, 7, 2)
        self.grid_layout.addWidget(self.save_status, 7, 3)
        self.save_button.clicked.connect(self.saveCalibrationFile)
        self.save_button.setEnabled(False)

        self.close_button = QPushButton('Apply and Close')
        self.grid_layout.addWidget(self.close_button, 8, 1)
        self.close_button.clicked.connect(self.close)

    def showGeneralInformationView(self):
        """emits a signal for opening the view for entering general information
        """
        self.showGeneralInfo_Signal.emit()

    def loadCalibrationImages(self):
        """emits a signal for loading the calibration images
        """
        self.loadCalImages_Signal.emit()

    def chessboardRowsInput(self):
        """emits a signal with number of inner chessboard row borders as parameter
        """
        input = self.input_chessboard_rows.text()
        rows = int(input, base=10)
        rows -= 1
        self.chessboardRows_Signal.emit(rows)

    def chessboardColumnsInput(self):
        """emits a signal with number of inner chessboard columns borders as parameter
        """
        input = self.input_chessboard_columns.text()
        columns = int(input, base=10)
        columns -= 1
        self.chessboardColumns_Signal.emit(columns)

    def chessboardSquareInput(self):
        """emits a signal with size of the chessboard squares as parameter
        """
        input = self.input_chessboard_square.text()
        size = float(input)
        self.chessboardSize_Signal.emit(size)

    def calculateCalibrationData(self):
        """emits a signal for calculating the calibration date
        """
        self.calculateCalData_Signal.emit()

    def saveCalibrationFile(self):
        """emits a signal for saving the calibration data in a file
        """
        self.saveCalData_Signal.emit()

    def closeEvent(self, event):
        """method for handling the closing process of the view

        Args:
            event (event): triggered when view gets closed
        """
        if self.calState == True:
            self.closeView_Signal.emit()
            event.accept()
        else:
            reply = QMessageBox.question(self, 'Discard progress?', 'Calibration not finished.\nDiscard any progress?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.undoChanges_Signal.emit()
                event.accept()
            else:
                event.ignore()