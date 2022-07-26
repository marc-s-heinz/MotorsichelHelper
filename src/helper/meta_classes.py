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

from abc import abstractclassmethod, abstractmethod

class WidgetInterface():
    """class to provide methods for the views and their controllers
    """

    @abstractmethod
    def setImage(self, icon_none, icon_wait, icon_okay, icon_fail):
        """abstract method for setting the status icons needed for the views

        Args:
            icon_none (QPixmap): pixmap for status when nothing was done yet
            icon_wait (QPixmap): pixmap for status when process was started
            icon_okay (QPixmap): pixmap for status when process was succesfull
            icon_fail (QPixmap): pixmap for status when process failed
        """
        pass

    @abstractclassmethod
    def updateView(self):
        """abstract mehtod for updating the view when something was changed
        """
        pass