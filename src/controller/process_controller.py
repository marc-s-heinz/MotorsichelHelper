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
from PyQt5.QtCore import QObject, pyqtSignal

from model.model import DataModel
from views.process_view import ProcessView
from controller.binarize_controller import BinarizeController
from views.binarize_view import BinarizeView
from controller.center_controller import CenterController
from views.center_view import CenterView
from controller.reference_controller import ReferenceController
from views.reference_view import ReferenceView

class ProcessController(QObject):
    """controller class for the processing view

    Args:
        QObject ([type]): [description]
    """
    viewClose_Signal = pyqtSignal(bool)

    def __init__(self, model: DataModel, view: ProcessView):
        """initiates the controller

        Args:
            model (DataModel): reference to model instance
            view (ProcessView): reference to view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        self.binState = False
        self.contState = False
        self.refState = False

        self.status_icon_none, self.status_icon_okay, self.status_icon_wait, self.status_icon_fail = model.getStatusIcons()
        self.view.binarizeState_label.setPixmap(self.status_icon_none)
        self.view.contoursState_label.setPixmap(self.status_icon_none)
        self.view.referenceState_label.setPixmap(self.status_icon_none)

        self.view.openBinaryView_Signal.connect(self.showBinaryView)
        self.view.findContours_Signal.connect(self.findContours)
        self.view.findCenter_Signal.connect(self.findCenter)
        self.view.setReference_Signal.connect(self.setReference)
        self.model.contoursState_Signal.connect(self.setContoursState)
        self.view.closeView_Signal.connect(self.processViewClosed)
        self.view.undoChanges_Signal.connect(self.undoChanges)

        self.view.show()


    def showBinaryView(self):
        """shows the binary view, hides the processing view
        """
        self.view.binarizeState_label.setPixmap(self.status_icon_wait)
        self.binarizeController = BinarizeController(self.model, BinarizeView())
        self.binarizeController.viewClose_Signal.connect(self.binViewClosed)
        self.view.setVisible(False)
    def binViewClosed(self, state):
        """restores visibility of processing view, sets status of binarization process

        Args:
            state (bool): status of binarization process
        """
        self.binState = state
        if self.binState == True:
            self.view.binarizeState_label.setPixmap(self.status_icon_okay)
            self.view.contours_button.setEnabled(True)
        else:
            self.view.binarizeState_label.setPixmap(self.status_icon_fail)
        self.view.setVisible(True)
        self.binarizeController = None

    def findContours(self):
        """tries to find contours in an image
        """
        self.view.contoursState_label.setPixmap(self.status_icon_wait)
        result = self.model.findContours()
        self.model.setContoursState(result)
    def setContoursState(self, state):
        """sets the state of the contour finding process

        Args:
            state (bool): result of contour finding process
        """
        self.contState = state
        if state == True:
            self.view.contoursState_label.setPixmap(self.status_icon_okay)
            self.view.center_button.setEnabled(True)
            self.view.setOrigin_button.setEnabled(True)
        else:
            self.view.contoursState_label.setPixmap(self.status_icon_fail)

    def findCenter(self):
        """tries to find the center of an image
        first atempt is static,
        second one user can change an accumulator value, while seeing the result in a special view
        hiding processing view for second atempt
        """
        self.view.referenceState_label.setPixmap(self.status_icon_wait)
        middlePoint = self.model.findObjectCenter()
        if middlePoint:
            reply = QMessageBox.question(self.view,
                'Found the right origin?',
                'Does the result seem to be acceptable?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.model.referencePoint = middlePoint
                result = self.model.transformContoursList()
                if result == True:
                    self.view.referenceState_label.setPixmap(self.status_icon_okay)
                    self.model.setNewReferenceState(True)
                    self.refState = True
            else:
                self.centerController = CenterController(self.model, CenterView())
                self.centerController.viewClose_Signal.connect(self.centerViewClosed)
                self.view.setVisible(False)
        else:
            self.model.setNewReferenceState(False)
    def centerViewClosed(self, state):
        """restores visibility of processing view, sets state of finding a center a new reference point

        Args:
            state (bool): result of finding center point
        """
        self.setReferenceState(state)
        self.view.setVisible(True)
        self.centerController = None

    def setReference(self):
        """shows a view with all found holes and hides processing view
        center point of one hole can be set as reference point
        """
        self.view.referenceState_label.setPixmap(self.status_icon_wait)
        self.referenceController = ReferenceController(self.model, ReferenceView())
        self.referenceController.viewClose_Signal.connect(self.referenceViewClosed)
        self.view.setVisible(False)
    def referenceViewClosed(self, state):
        """resores visibility of processing view

        Args:
            state (bool): state of finding reference point
        """
        self.setReferenceState(state)
        self.view.setVisible(True)
        self.referenceController = None

    def setReferenceState(self, state):
        """sets the result of finding a new reference point

        Args:
            state (bool): state of finding a new reference point
        """
        if state == True:
            self.view.referenceState_label.setPixmap(self.status_icon_okay)
        else:
            self.view.referenceState_label.setPixmap(self.status_icon_fail)
        self.refState = state

    def undoChanges(self):
        """method to undo all changes made in current process
        """
        result = self.model.undoProcessProgress()
        if result == True:
            self.binState = False
            self.contState = False
            self.refState = False
            self.processViewClosed()

    def processViewClosed(self):
        """closes the processing view
        """
        if (self.binState and self.contState and self.refState) == True:
            state = True
        else:
            state = False
        self.view.processState = state
        self.model.setProcessState(state)
        self.viewClose_Signal.emit(state)
        self.view.close()