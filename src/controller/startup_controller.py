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
from views.startup_view import StartupView

class StartupController(QObject):
    """controller class for startup view

    Args:
        QObject ([type]): [description]
    """
    viewClose_Signal = pyqtSignal()

    def __init__(self, model: DataModel, view: StartupView):
        """initiates the startup controller

        Args:
            model (DataModel): reference to model instance
            view (StartupView): reference to the view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        self.view.apply_Signal.connect(self.setInput)

        self.view.show()

    def setInput(self):
        """handles possible input
        """
        self.view.signalState = True
        manufacturer = self.view.manufacturer_input.text()
        objectModel = self.view.model_input.text()
        self.model.manufacturer = manufacturer
        self.model.modelName = objectModel
        self.viewClose_Signal.emit()
        self.view.close()