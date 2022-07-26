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
from views.disclaimer_view import DisclaimerView

class DisclaimerController(QObject):
    """controller class for the disclaimer view

    Args:
        QObject ([type]): [description]
    """
    viewClose_Signal = pyqtSignal()

    def __init__(self, model: DataModel, view: DisclaimerView):
        """initiates the disclaimer view

        Args:
            model (DataModel): reference of the model instance
            view (DisclaimerView): reference of the view instance
        """
        super().__init__()
        self.model = model
        self.view = view
        
        self.view.closeView_Signal.connect(self.disclaimerViewClosed)

        self.view.textLabel.setText(self.model.disclaimerText)

        self.view.show()

    def disclaimerViewClosed(self):
        """handles closing process of the view
        """
        self.model.wasDisclaimerAccepted = True
        self.view.closeSignalState = True
        self.viewClose_Signal.emit()
        self.view.close()