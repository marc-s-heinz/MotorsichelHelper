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

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import cv2

from model.model import DataModel
from views.correction_view import CorrectionView
from helper.custom_exceptions import MissingInputException

class CorrectionController(QObject):
    """controller class for handling the correction view        
    """
    viewClose_Signal = pyqtSignal(bool)

    def __init__(self, model: DataModel, view: CorrectionView):
        """initiates the controller

        Args:
            model (DataModel): reference to model instance
            view (CorrectionView): reference to view instance

        Raises:
            MissingInputException: raised when no index image is prepared
            MissingInputException: raised when no contours list exists
        """
        super().__init__()
        self.model = model
        self.view = view

        if self.model.indexImage is None:
            raise MissingInputException()
        if self.model.contoursList is None:
            raise MissingInputException()

        self.image = self.model.indexImage
        self.diameter_wasChanged = False

        self.view.closeView_Signal.connect(self.closeCorrectionView)
        self.view.inputChanged_Signal.connect(self.inputChanged)

        self.addWidgets()

        self.view.show()

    def addWidgets(self):
        """dinamically adds labels, handlers and inputfields for each diameter
        """
        indexCounter = 0
        for cont in self.model.contoursList:
            if cont['contour_is_hole']:
                nameLabel = 'Hole' + str(cont['contour_index'])
                label = QLabel(nameLabel)
                self.view.grid_layout.addWidget(label, indexCounter+1, 1)

                cont_index = cont['contour_index']
                inputName = 'input ' + str(cont_index)
                setattr(self, f'lineEdit_{cont_index}', QLineEdit())
                diameter_input = getattr(self, f'lineEdit_{cont_index}')
                diameter_input.setText(str(cont['diameter_mm']))
                diameter_input.setObjectName(inputName)
                self.view.grid_layout.addWidget(diameter_input, indexCounter+1, 2)
                diameter_input.editingFinished.connect(self.view.onChange)
                indexCounter += 1

        self.view.grid_layout.addWidget(self.view.imageLabel, indexCounter+1, 1, 1, 2)
        height, width, channels = self.image.shape
        bytes_per_line = width * channels
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        convertedImage = QImage(image, width, height, bytes_per_line, QImage.Format_RGB888)
        self.view.imageLabel.setPixmap(QPixmap.fromImage(convertedImage).scaled(self.view.imageLabel.width(),
            self.view.imageLabel.height(),
            Qt.KeepAspectRatioByExpanding))

        self.view.grid_layout.addWidget(self.view.closeButton, indexCounter+2, 1)


    def inputChanged(self, source_input):
        """changes the value of the corresponding diameter in the contours list

        Args:
            source_input ([type]): object that triggered the signal
        """
        source = source_input.objectName()
        str_diameter = source_input.text()
        new_diameter = float(str_diameter)
        temp_index = source.split()
        sourceIndex = int(temp_index[1])
        cont = self.model.contoursList[sourceIndex]
        old_diameter = cont['diameter_mm']
        if old_diameter == new_diameter:
            pass
        else:
            self.diameter_wasChanged = True
            cont.update({'diameter_mm': new_diameter})

    def closeCorrectionView(self):
        """method to handle closing of the view
        """
        state = True
        if self.diameter_wasChanged:
            self.model.setDiameterCorrectionState(state)
            reply = QMessageBox.question(self.view,
                'Re-generate reference List?',
                'At least one diameter was changed.\nDo you want to re-generate the reference list\nfor the changes to be applied?\nThe new list can be printed afterwards.',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                result = self.model.saveReferenceImageAndList()
                state = result
        self.view.closeSignalState = True
        self.viewClose_Signal.emit(state)
        self.view.close()