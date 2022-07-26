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

from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2, copy

from model.model import DataModel
from views.reference_view import ReferenceView

class ReferenceController(QObject):
    """controller class for reference view

    Args:
        QObject ([type]): [description]
    """
    viewClose_Signal = pyqtSignal(bool)

    def __init__(self, model: DataModel, view: ReferenceView):
        """initializes the controller for the reference view

        Args:
            model (DataModel): reference to model instance
            view (ReferenceView): reference to view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        self.fontSize = self.model.scaleFactor * 5.5
        self.fontWeight = int(self.model.scaleFactor * 10)
        
        if self.model.threeChannelGrayImage is not None:
            image = copy.copy(self.model.threeChannelGrayImage)
        else:
            temp = copy.copy(self.model.originalImage)
            grayTemp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
            image = cv2.merge((grayTemp, grayTemp, grayTemp))
            self.model.threeChannelGrayImage = copy.copy(image)
        self.referencePoint = None
        self.indexDict = {}
        self.comboList = []
        self.comboList.append('')

        indexCounter = 0
        for cont in model.contoursList:
            if cont['contour_is_hole']:
                x, y = cont['contour_center_px']
                r = int(cont['diameter_px'] / 2)
                cv2.rectangle(image, (x-r, y-r), (x+r, y+r), (0, 128, 255), self.fontWeight)
                cv2.putText(image, str(indexCounter), (x+r+r, y+r), cv2.FONT_HERSHEY_SIMPLEX, self.fontSize, (0, 255, 0), self.fontWeight)
                self.indexDict.update({str(indexCounter): (x, y)})
            indexCounter += 1
        cv_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = cv_image.shape
        bytes_per_line = width * channels
        converted_image = QImage(cv_image, width, height, bytes_per_line, QImage.Format_RGB888)
        self.view.image_label.setPixmap(QPixmap.fromImage(converted_image).scaled(
            self.view.image_label.width(), self.view.image_label.height(),
            Qt.KeepAspectRatio))

        for i in self.indexDict.keys():
            self.comboList.append(i)
        self.view.ref_combobox.addItems(self.comboList)
        self.view.ref_combobox.setCurrentText('')

        self.view.show()

        self.view.setReferencePoint_Signal.connect(self.setReferencePoint)
        self.view.closeView_Signal.connect(self.closeView)

    def setReferencePoint(self, listItem):
        """sets the new reference point

        Args:
            listItem (str): string representing the new reference point
        """
        if listItem == '':
            pass
        else:
            self.referencePoint = self.indexDict[listItem]

    def closeView(self):
        """closes the reference view
        """
        state = False
        if self.referencePoint is not None:
            self.model.referencePoint = self.referencePoint
            state = self.model.transformContoursList()
        self.model.setNewReferenceState(state)
        self.view.closeSignalState = True
        self.viewClose_Signal.emit(state)
        self.view.close()