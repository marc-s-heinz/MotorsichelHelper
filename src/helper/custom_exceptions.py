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

class NoCalDataException(Exception):
    def __str__(self):
        return 'No calibration data found'

class NoGeneralCalibrationInformationException(Exception):
    def __str__(self):
        return 'No general information found to create file name'

class NoImageException(Exception):
    def __str__(self):
        return 'No image found'

class MissingInputException(Exception):
    def __str__(self):
        return 'Missing input for function'

class InappropriateParameterException(Exception):
    def __str__(self):
        return 'Inappropriate parameter for this function'

class NoChessboardException(Exception):
    def __str__(self):
        return 'No chessboard was detected'

class NoFormException(Exception):
    def __str__(self):
        return 'No form was detected'

class NotSupportedException(Exception):
    def __str__(self):
        return 'Function not supported yet.'