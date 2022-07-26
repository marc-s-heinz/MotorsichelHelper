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
from PyQt5.QtWidgets import QMessageBox
import cv2, copy

from model.model import DataModel
from views.center_view import CenterView

class CenterController(QObject):
    """controller class for handling the center view

    Args:
        QObject ([type]): [description]
    """
    viewClose_Signal = pyqtSignal(bool)

    def __init__(self, model: DataModel, view: CenterView):
        """initiates the controller

        Args:
            model (DataModel): reference of model instance
            view (CenterView): reference of view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        self.dp = 1.2
        self.minDist = 800
        self.image = None
        self.offsetX = None
        self.offsetV = None
        self.bytesPerLine = None

        self.view.dpSlider.setValue(self.dp*10)
        self.prepareImage()
        self.findCircles()

        self.view.show()

        self.view.closeView_Signal.connect(self.centerViewClosed)
        self.view.sliderChanged_Signal.connect(self.sliderChanged)


    def prepareImage(self):
        """prepares an image for the view
        """
        self.image, self.offsetH, self.offsetV = self.model.prepareImageForCenterView()
        self.imageHeight, self.imageWidth, self.imageChannels = self.image.shape
        self.bytesPerLine = self.imageWidth * self.imageChannels

    def sliderChanged(self):
        """reads the slider value and calls a method for finding circles in the image
        """
        self.dp = (self.view.dpSlider.value() / 10)
        self.findCircles()

    def findCircles(self):
        """finds circles in the image
        """
        imageSingleChannel = copy.copy(self.model.centerGrayImage)
        imageThreeChannel = copy.copy(self.image)
        x, y, r = self.model.findCircles(image=imageSingleChannel, dp=self.dp, minDist=self.minDist)
        if (x and y and r) is not None:
            self.imageCenterX = x
            self.imageCenterY = y
            self.maxR = r
            cv2.circle(imageThreeChannel, (self.imageCenterX, self.imageCenterY), self.maxR, (255, 0, 0), 1)
            cv2.circle(imageThreeChannel, (self.imageCenterX, self.imageCenterY), 3, (255, 128, 0), -1)
            convertedImage = QImage(imageThreeChannel, self.imageWidth, self.imageHeight, self.bytesPerLine, QImage.Format_RGB888)
            self.view.imageLabel.setPixmap(QPixmap.fromImage(convertedImage).scaled(self.view.imageLabel.width(), self.view.imageLabel.height(), Qt.KeepAspectRatio))
            self.view.imageLabel.repaint()

    def centerViewClosed(self):
        """handles closing of the view
        sets new reference point and state in model when result acceptable
        """
        state = False
        if (self.imageCenterX and self.imageCenterY) != 0:
            middlepoint = (self.imageCenterX + self.offsetH, self.imageCenterY + self.offsetV)
            reply = QMessageBox.question(self.view,
                'Acceptable result?',
                'Does the result seem to be acceptable?\nElse try to set another reference point later.',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.model.referencePoint = middlepoint
                result = self.model.transformContoursList()
                if result == True:
                    state = True
                    self.model.setNewReferenceState(True)
        else:
            self.model.setNewReferenceState(False)
        self.view.closeSignalState = True
        self.viewClose_Signal.emit(state)
        self.view.close()
        

