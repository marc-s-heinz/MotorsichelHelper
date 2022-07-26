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
from views.general_info_view import GeneralInformationView

class GeneralInformationController(QObject):
    """controller class for the general information view

    Args:
        QObject ([type]): [description]
    """
    viewClose_Signal = pyqtSignal(bool)

    def __init__(self, model: DataModel, view: GeneralInformationView):
        """initiates the controller

        Args:
            model (DataModel): reference of model instance
            view (GeneralInformationView): reference of view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        self.owner = False
        self.camera = False
        self.lens = False
        self.focLen = False

        self.status_icon_none, self.status_icon_okay, self.status_icon_wait, self.status_icon_fail = model.getStatusIcons()
        self.view.camera_owner_status.setPixmap(self.status_icon_none)
        self.view.camera_name_status.setPixmap(self.status_icon_none)
        self.view.lens_name_status.setPixmap(self.status_icon_none)
        self.view.lens_focal_length_status.setPixmap(self.status_icon_none)

        self.view.closeGenView_Signal.connect(self.genViewClosed)
        self.view.cameraOwner_Signal.connect(self.ownerInput)
        self.view.cameraName_Signal.connect(self.cameraInput)
        self.view.lensName_Signal.connect(self.lensNameInput)
        self.view.lensFocalLength_Signal.connect(self.lensFocalLengthInput)

        self.view.show()

    def genViewClosed(self):
        """handles closing of the view
        """
        if (self.owner and self.camera and self.lens and self.focLen) == True:
            state = True
        else:
            state = False
        self.view.closeSignalState = True
        self.viewClose_Signal.emit(state)
        self.view.close()

    def ownerInput(self, cameraOwner):
        """saves args argument in model instance and sets status in the view

        Args:
            cameraOwner (str): Name of the camera owner
        """
        self.view.camera_owner_status.setPixmap(self.status_icon_okay)
        self.owner = True
        self.model.cameraOwner = cameraOwner

    def cameraInput(self, cameraName):
        """saves args argument in model instance and sets status in the view

        Args:
            cameraName (str): camera model
        """
        self.view.camera_name_status.setPixmap(self.status_icon_okay)
        self.camera = True
        self.model.cameraName = cameraName

    def lensNameInput(self, lensName):
        """saves args argument in model instance and sets status in the view

        Args:
            lensName (str): camera lens model
        """
        self.view.lens_name_status.setPixmap(self.status_icon_okay)
        self.lens = True
        self.model.lensName = lensName

    def lensFocalLengthInput(self, focalLength):
        """saves args argument in model instance and sets status in the view

        Args:
            focalLength (str): focal length of camera lens
        """
        self.view.lens_focal_length_status.setPixmap(self.status_icon_okay)
        self.focLen = True
        self.model.lensFocalLength = focalLength