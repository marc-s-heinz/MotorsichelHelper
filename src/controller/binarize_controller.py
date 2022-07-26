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

from PyQt5.QtCore import QObject, QThread, pyqtSignal
import cv2, numpy as np

from model.model import DataModel
from views.binarize_view import BinarizeView

class BinarizeController(QObject):
    """Controller class for the binarize view

    Returns:
        [type]: [description]
    """
    viewClose_Signal = pyqtSignal(bool)

    def __init__(self, model: DataModel, view: BinarizeView):
        """initiates the controller

        Args:
            model (DataModel): reference to the model instance
            view (BinarizeView): reference to the corresponding view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        self.binState = False
        self.threadStopFlag = False
        self.showRefFlag = False
        self.channelMode = False
        self.readAdditionalSlider = False

        self.image = self.model.equalizeHistory(self.model.originalImage)

        self.view.sliderChanged_Signal.connect(self.readSlider)
        self.view.toggleRefImage_Signal.connect(self.showRefImage)
        self.view.toggleChannelMode_Signal.connect(self.toggleChannelMode)

        self.showOrHideChannel2Slider()

        self.initView()
        self.view.show()
        self.updateImage()

    def initView(self):
        """sets up the view
        """
        self.hMin1 = self.view.hue_min_slider1.value()
        self.sMin1 = self.view.saturation_min_slider1.value()
        self.vMin1 = self.view.value_min_slider1.value()
        self.hMax1 = self.view.hue_max_slider1.value()
        self.sMax1 = self.view.saturation_max_slider1.value()
        self.vMax1 = self.view.value_max_slider1.value()
        self.view.hsv_min_label1.setText(f'HSV-Channel 1 - lower Threshold = ({self.hMin1}, {self.sMin1}, {self.vMin1})')
        self.view.hsv_max_label1.setText(f'HSV-Channel 1 - upper Threshold = ({self.hMax1}, {self.sMax1}, {self.vMax1})')

    def showOrHideChannel2Slider(self):
        """shows or hides sliders for extended mode
        """
        self.view.distance_dummy.setVisible(self.channelMode)
        self.view.colorChannel_label2.setVisible(self.channelMode)

        self.view.hue_min_label2.setVisible(self.channelMode)
        self.view.hue_min_slider2.setVisible(self.channelMode)
        self.view.hue_max_label2.setVisible(self.channelMode)
        self.view.hue_max_slider2.setVisible(self.channelMode)

        self.view.saturation_min_label2.setVisible(self.channelMode)
        self.view.saturation_min_slider2.setVisible(self.channelMode)
        self.view.saturation_max_label2.setVisible(self.channelMode)
        self.view.saturation_max_slider2.setVisible(self.channelMode)

        self.view.value_min_label2.setVisible(self.channelMode)
        self.view.value_min_slider2.setVisible(self.channelMode)
        self.view.value_max_label2.setVisible(self.channelMode)
        self.view.value_max_slider2.setVisible(self.channelMode)

        self.view.hsv_min_label2.setVisible(self.channelMode)
        self.view.hsv_max_label2.setVisible(self.channelMode)

        self.view.update()
    
    def readSlider(self):
        """reads the sliders of the view
        """
        self.hMin1 = self.view.hue_min_slider1.value()
        self.sMin1 = self.view.saturation_min_slider1.value()
        self.vMin1 = self.view.value_min_slider1.value()
        self.hMax1 = self.view.hue_max_slider1.value()
        self.sMax1 = self.view.saturation_max_slider1.value()
        self.vMax1 = self.view.value_max_slider1.value()
        self.view.hsv_min_label1.setText(f'HSV-Channel 1 - lower Threshold = ({self.hMin1}, {self.sMin1}, {self.vMin1})')
        self.view.hsv_max_label1.setText(f'HSV-Channel 1 - upper Threshold = ({self.hMax1}, {self.sMax1}, {self.vMax1})')
        if self.channelMode == True:
            self.hMin2 = self.view.hue_min_slider2.value()
            self.sMin2 = self.view.saturation_min_slider2.value()
            self.vMin2 = self.view.value_min_slider2.value()
            self.hMax2 = self.view.hue_max_slider2.value()
            self.sMax2 = self.view.saturation_max_slider2.value()
            self.vMax2 = self.view.value_max_slider2.value()
            self.view.hsv_min_label2.setText(f'HSV-CHannel 2 - lower Threshold = ({self.hMin2}, {self.sMin2}, {self.vMin2})')
            self.view.hsv_max_label2.setText(f'HSV-Channel 2 - upper Threshold = ({self.hMax2}, {self.sMax2}, {self.vMax2})')
            self.readAdditionalSlider = True

    def updateImage(self):
        """starts a thread to update the image in the view
        """
        self.thread = QThread()
        self.worker = Worker()
        self.worker.setParentObject(self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.view.closeView_Signal.connect(self.finishThread)
        self.worker.finished.connect(self.grabImage)
        self.worker.window_toggle.connect(self.changeText)

        self.worker.setImage(self.image)
        self.worker.setMorphMode(self.model.morphMode)
        self.thread.start()
    
    def finishThread(self):
        """finishes the worker thread by activating a stop flag
        """
        self.threadStopFlag = True

    def grabImage(self):
        """gets the image from the worker thread and saves it in model
        """
        image = self.worker.getImage()
        if image.any():
            self.binState = True
            self.model.binarizedImage = image
        else:
            self.binState = False
        self.model.setBinarizeState(self.binState)
        self.view.closeSignalState = True
        result = self.view.close()
        self.viewClose_Signal.emit(self.binState)

    def getHSVRefImage(self):
        """calls a method from model to get the hsv value reference image

        Returns:
            ndarray: image as NumPy ndarray
        """
        refImage = self.model.createRefImageHSVRange()
        return refImage

    def showRefImage(self):
        """sets a flag to tell the worker thread to show the reference image or close it
        """
        self.showRefFlag = not self.showRefFlag

    def toggleChannelMode(self):
        """sets a flag to tell the worker thread to toggle channel mode
        """
        self.channelMode = not self.channelMode
        self.showOrHideChannel2Slider()

    def changeText(self):
        """toggles the text on the hsv reference image button in the view 
        """
        if self.showRefFlag:
            self.view.ref_button.setText('Hide')
        else:
            self.view.ref_button.setText('Show')


class Worker(QObject):
    """Worker thread to handle input from the view and apply them on image
    """
    finished = pyqtSignal()
    window_toggle = pyqtSignal()    

    def setMorphMode(self, mode):
        """sets the modus for the morphology operation

        Args:
            mode (int): int representing the mode
        """
        self.morphMode = mode

    def setImage(self, image):
        """sets the image that should be binarized

        Args:
            image (ndarray): image of object as Numpy ndarray
        """
        self.image = image

    def getImage(self):
        """returns the binarized image

        Returns:
            ndarray: binarized image as NumPy ndarray
        """
        return self.binaryImage

    def setParentObject(self, parentObject: BinarizeController):
        """sets the parent object of the worker thread

        Args:
            parentObject (BinarizeController): parent object
        """
        self.parentObject = parentObject

    def run(self):
        """creates an openCV window for showing the image that needs to be binarized,
        in loop gets the threshold values from parent object, applies them and generates a binary mask of the image
        and shows it
        while parentObject doesnt set a stop flag
        """
        cv2.namedWindow('masked image', cv2.WINDOW_NORMAL)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))

        self.ref_image = self.parentObject.getHSVRefImage()
        self.ref_active = False
        self.combinedMask = None
        self.threshold2Ready = False
        self.combinedMaskReady = False

        #cv2.medianBlur(self.image, 3)  Bereits mit model.equalizeHistory() erfolgt
        hsv_img = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        while not self.parentObject.threadStopFlag:
            hMin1 = self.parentObject.hMin1
            sMin1 = self.parentObject.sMin1
            vMin1 = self.parentObject.vMin1
            hMax1 = self.parentObject.hMax1
            sMax1 = self.parentObject.sMax1
            vMax1 = self.parentObject.vMax1
            lowerThreshold1 = np.array([hMin1, sMin1, vMin1])
            upperThreshold1 = np.array([hMax1, sMax1, vMax1])

            if (self.parentObject.channelMode and self.parentObject.readAdditionalSlider) == True:
                hMin2 = self.parentObject.hMin2
                sMin2 = self.parentObject.sMin2
                vMin2 = self.parentObject.vMin2
                hMax2 = self.parentObject.hMax2
                sMax2 = self.parentObject.sMax2
                vMax2 = self.parentObject.vMax2
                lowerThreshold2 = np.array([hMin2, sMin2, vMin2])
                upperThreshold2 = np.array([hMax2, sMax2, vMax2])
                self.threshold2Ready = True
            
            self.mask1 = cv2.inRange(hsv_img, lowerThreshold1, upperThreshold1)

            if self.morphMode == 1:
                self.mask1 = cv2.dilate(self.mask1, kernel, iterations=1)
            elif self.morphMode == 2:
                self.mask1 = cv2.erode(self.mask1, kernel, iterations=1)
            elif self.morphMode == 3:
                self.mask1 = cv2.morphologyEx(self.mask1, cv2.MORPH_OPEN, kernel)
            elif self.morphMode == 4:
                self.mask1 = cv2.morphologyEx(self.mask1, cv2.MORPH_CLOSE, kernel)

            if (self.parentObject.channelMode and self.parentObject.readAdditionalSlider and self.threshold2Ready) == True:
                self.mask2 = cv2.inRange(hsv_img, lowerThreshold2, upperThreshold2)

                if self.morphMode == 1:
                    self.mask2 = cv2.dilate(self.mask2, kernel, iterations=1)
                elif self.morphMode == 2:
                    self.mask2 = cv2.erode(self.mask2, kernel, iterations=1)
                elif self.morphMode == 3:
                    self.mask2 = cv2.morphologyEx(self.mask2, cv2.MORPH_OPEN, kernel)
                elif self.morphMode == 4:
                    self.mask2 = cv2.morphologyEx(self.mask2, cv2.MORPH_CLOSE, kernel)
                
                self.combinedMask = cv2.bitwise_or(self.mask1, self.mask2)

                self.combinedMaskReady = True

            if (self.parentObject.channelMode and self.parentObject.readAdditionalSlider and self.combinedMaskReady) == True:
                result = cv2.bitwise_and(self.image, self.image, mask=self.combinedMask)
            else:
                result = cv2.bitwise_and(self.image, self.image, mask=self.mask1)

            cv2.imshow('masked image', result)
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break

            if self.parentObject.showRefFlag:
                if self.ref_active:
                    pass
                else:
                    self.ref_active = True
                    self.window_toggle.emit()
                cv2.namedWindow('HSV Reference')
                cv2.imshow('HSV Reference', self.ref_image)
            else:
                if not self.ref_active:
                    pass
                else:
                    self.ref_active = False
                    self.window_toggle.emit()
                if cv2.getWindowProperty('HSV Reference', cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow('HSV Reference')
                    
        if self.parentObject.channelMode == True and self.combinedMask.any():
            self.binaryImage = cv2.threshold(self.combinedMask, 120, 255, cv2.THRESH_BINARY)[1]
        else:
            self.binaryImage = cv2.threshold(self.mask1, 120, 255, cv2.THRESH_BINARY)[1]

        cv2.destroyAllWindows()

        self.finished.emit()