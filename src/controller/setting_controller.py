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

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal

from model.model import DataModel
from views.setting_view import SettingView

class SettingController(QObject):
    """controller class for the setting view

    Args:
        QObject ([type]): [description]
    """
    viewClose_Signal = pyqtSignal()

    def __init__(self, model: DataModel, view: SettingView):
        """initiates the setting controller

        Args:
            model (DataModel): reference to model instance
            view (SettingView): reference to view instance
        """
        super().__init__()
        self.model = model
        self.view = view

        if self.model.workspaceSetState:
            currentPath = self.model.workspaceDir
            self.view.path_info.setText(currentPath)
        else:
            text = 'None, used exec_path: ' + self.model.dir
            self.view.path_info.setText(text)

        self.view.morph_combobox.addItems(self.model.morph_options)
        self.view.morph_combobox.setCurrentText('')
        self.view.scale_input.setText(str(self.model.scaleFactor))
        self.view.roundness_input.setText(str(self.model.roundnessThreshold))
        self.view.screen_input.setText(str(model.maxScreenSize))
        self.view.show_input.setText(str(model.showImagesDuration))
        self.view.startup_checkbox.setChecked(model.showNewInfoAtStartup)
        
        self.view.chooseWorkspace_Signal.connect(self.setWorkspaceDirectory)
        self.view.scaleFactor_Signal.connect(self.setScaleFactor)
        self.view.roundnessThreshold_Signal.connect(self.setRoundnessThreshold)
        self.view.maxScreenSize_Signal.connect(self.setMaxScreenSize)
        self.view.showDuration_Signal.connect(self.setShowDuration)
        self.view.toggleStartupView_Signal.connect(self.setStartupViewState)
        self.view.closeView_Signal.connect(self.settingViewClosed)
        self.view.morphSelect_Signal.connect(self.setMorphOption)

        self.view.morph_combobox.setCurrentIndex(self.model.morphMode)

        self.view.show()

    def setWorkspaceDirectory(self):
        """sets a new workspace directory
        """
        workspace = QFileDialog.getExistingDirectory()
        if not workspace:
            self.model.workspaceDir = None
            self.model.workspaceSetState = False
        else:
            workspace = workspace.replace('\\', '/')
            self.model.workspaceDir = workspace
            self.model.workspaceSetState = True
            self.view.path_info.setText(workspace)

    def setScaleFactor(self):
        """sets a new scale factor for images
        """
        scale_str = self.view.scale_input.text()
        scale = float(scale_str)
        if isinstance(scale, float):
            if scale > 0.0 and scale <= 1.0:
                self.model.scaleFactor = scale
            else:
                self.showNoValidInput()
        else:
            self.showNoValidInput()

    def setRoundnessThreshold(self):
        """sets a new threshold value for the roundness of holes
        """
        thresh_str = self.view.roundness_input.text()
        thresh = float(thresh_str)
        if isinstance(thresh, float):
            if thresh > 0.0 and thresh < 1.0:
                self.model.roundnessThreshold = thresh
            else:
                self.showNoValidInput()
        else:
            self.showNoValidInput()

    def setMaxScreenSize(self):
        """sets a new maximum size for images when shown on screen
        """
        size_str = self.view.screen_input.text()
        size = float(size_str)
        if isinstance(size, float):
            if size > 0.0 and size <= 1.0:
                self.model.maxScreenSize = size
            else:
                self.showNoValidInput()
        else:
            self.showNoValidInput()

    def setShowDuration(self):
        """sets a new duration for showing images during action
        "None" -> no images shown
        >0 -> time images will be shown in ms
        """
        duration_str = self.view.show_input.text()
        if duration_str == 'None':
            self.model.showImagesDuration = None
        else:
            duration = int(duration_str)
            if isinstance(duration, int):
                self.model.showImagesDuration = duration
            else:
                self.showNoValidInput()

    def setStartupViewState(self):
        """toggles the setting for the startup view
        """
        state = self.view.startup_checkbox.isChecked()
        self.model.showNewInfoAtStartup = state

    def setMorphOption(self, listItem):
        if listItem == '':
            pass
        elif listItem == 'Dilation':
            self.model.morphMode = 1
        elif listItem == 'Erosion':
            self.model.morphMode = 2
        elif listItem == 'Opening':
            self.model.morphMode = 3
        elif listItem == 'Closing':
            self.model.morphMode = 4
        else:
            self.model.morphMode = 1#default

    def showNoValidInput(self):
        """shows a warning message if an input is not valid
        """
        QMessageBox.warning(self.view, 'Warning', 'No valid input, please retry!', QMessageBox.Ok)

    def settingViewClosed(self):
        """closes the view
        """
        self.view.closeSignalState = True
        self.viewClose_Signal.emit()
        self.view.close()