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

import os, pickle, glob, copy, cv2, ctypes, webbrowser, numpy as np, math, ezdxf, win32print, win32ui, win32api
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog
from PIL import Image, ImageWin

from helper.custom_exceptions import InappropriateParameterException, MissingInputException, NoCalDataException, NoChessboardException, NoFormException, NoGeneralCalibrationInformationException, NoImageException

class DataModel(QObject):
    """class which instance is responsible for storing all data and providing logic
    """
    calibrationState_Signal = pyqtSignal(bool)
    imageLoadState_Signal = pyqtSignal(bool)
    chessboardImageState_Signal = pyqtSignal(bool)
    processState_Signal = pyqtSignal(bool)
    binarizeState_Signal = pyqtSignal(bool)
    contoursState_Signal = pyqtSignal(bool)
    newReferenceState_Signal = pyqtSignal(bool)
    diameterCorrectionState_Signal = pyqtSignal(bool)
    exportDataState_Signal = pyqtSignal(bool)

    def __init__(self):
        """constructor
        """
        super().__init__()

        #general vars
        self.manualName = '/manual.pdf'
        self.licenseName = '/license.pdf'
        self.manufacturer = None
        self.modelName = None

        #states
        self.settingsLoadState = False
        self.calibrationState = False
        self.imageLoadState = False
        self.chessboardImageState = False
        self.processState = False
        self.binarizeState = False
        self.contoursState = False
        self.newReferenceState = False
        self.diameterCorrectionState = False
        self.exportState = False
        self.wasDisclaimerAccepted = False

        #images, Sizes and Lists
        self.status_icon_none = None
        self.status_icon_okay = None
        self.status_icon_wait = None
        self.status_icon_fail = None
        self.calibrationImages = None
        self.originalImage = None
        self.chessboardImage = None
        self.threeChannelGrayImage = None
        self.binarizedImage = None
        self.mask = None
        self.indexImage = None
        self.contoursList = None
        self.originalImageSize_preCrop = None
        self.originalImageSize_afterCrop = None
        self.centerGrayImage = None

        #cal data pickle
        self.cameraName = None
        self.lensName = None
        self.cameraOwner = None
        self.lensFocalLength = None
        self.cameraMatrix = None
        self.new_cameraMatrix = None
        self.distMatrix = None
        self.rotVector = None
        self.tanVector = None
        self.calROI = None
        self.chessboardSize = None
        self.meanError = None
        #DICT FOR FOUND CONTOURS - JUST FOR INFO
        #contour_index           int
        #contour_points_px       []          np array with coordinates
        #contour_points_ref      []          np array with transformed coordinates
        #contour_points_mm       []          np array with coordinates for cad
        #contour_center_px       tuple       old center point
        #contour_area_px         float       area
        #contour_perimeter_px    float       perimeter
        #contour_is_hole         bool        wheather a contours is a hole or not(roundness >= 0.95)
        #center_point_ref        tuple       new center point
        #center_point_ref_mm     tuple       new center point for cad
        #roundness               float       roundness < 1
        #diameter_px             float       average diameter in pixel
        #diameter_mm             float (2)   average diameter in mm
        #deviation_px            float       maximal deviation from avg diameter in px
        #deviation_mm            float (2)   maximal deviation from average diameter in mm
        #set_diameter_manually   bool        True if diameter [mm] was set manually
        
        #settings pickle
        self.workspaceDir = None
        self.workspaceSetState = False
        self.scaleFactor = 0.2
        self.maxScreenSize = 0.8
        self.showImagesDuration = None
        self.debugMode = False
        self.showNewInfoAtStartup = False
        self.generateMask = False
        self.roundnessThreshold = 0.9
        self.wasDisclaimerAccepted = False
        self.morph_options = ['', 'Dilation', 'Erosion', 'Opening', 'Closing']
        self.morphMode = 1#default = dilation

        #program vars
        self.chessboardRows = 6
        self.chessboardColumns = 8
        self.chessboardSize = 1.0
        self.chessboardSquareState = False
        self.objPoints = None
        self.imgPoints = None
        self.objp = None
        self.criteria = None
        self.objectDistance = None
        self.mmPerPxRatio = None
        self.meanError = None
        self.referencePoint = None
        self.referenceImage_path = None
        self.referenceList_path = None
        self.disclaimerText = ('SAFETY WARNING\n\n'
            'It might be possible that external (possibly harmful) code can be loaded during runtime,\n'
            'especially while loading calibration data or settings.\n'
            'Please make sure that you only load data from certain origin or trusted sources.\n'
            'If in doubt generate new calibration data and remove settings file.\n\n\n'

            'Copyright (C) 2021 Marc Sebastian Heinz\n'
            '                   sebastian.heinz[at]]online.de\n'
            'Copyright (C) 2021 AVL Schrick GmbH\n'
            '                   Dreherstraße 3-5\n'
            '                   42899 Remscheid\n'
            '                   info[at]avl-schrick.com\n\n'
            'This program is free software: you can redistribute it and/or modify\n'
            'it under the terms of the GNU General Public License as published by\n'
            'the Free Software Foundation, either version 3 of the License, or\n'
            '(at your option) any later version.\n\n'
            'This program is distributed in the hope that it will be useful,\n'
            'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
            'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
            'GNU General Public License for more details.\n\n'
            'You should have received a copy of the GNU General Public License\n'
            'along with this program.  If not, see <https://www.gnu.org/licenses/>\n\n')

        #prepare program
        self.startupDone = False
        self.settingsLoadState = self.loadSettings()
        self.makeSubDirs()
        self.loadStatusIcons()


    def loadStatusIcons(self):
        """loads status pixmap from file
        """
        self.status_icon_none = QPixmap(self.res_subdir + '/status_none.png')
        self.status_icon_okay = QPixmap(self.res_subdir + '/status_ok.png')
        self.status_icon_wait = QPixmap(self.res_subdir + '/status_waiting.png')
        self.status_icon_fail = QPixmap(self.res_subdir + '/status_fail.png')

    def restart(self):
        """resets program progress
        """
        self.setCalibrationState(False)
        self.setImageLoadState(False)
        self.setChessboardImageState(False)
        self.setProcessState(False)
        self.setBinarizeState(False)
        self.setContoursState(False)
        self.setNewReferenceState(False)
        self.setDiameterCorrectionState(False)
        self.setExportDataState(False)
        self.cameraName = None
        self.lensName = None
        self.cameraOwner = None
        self.lensFocalLength = None
        self.cameraMatrix = None
        self.new_cameraMatrix = None
        self.distMatrix = None
        self.rotVector = None
        self.tanVector = None
        self.calROI = None
        self.chessboardSize = None
        self.meanError = None
        self.workspaceDir = None
        self.workspaceSetState = False
        self.scaleFactor = 0.2
        self.maxScreenSize = 0.8
        self.showImagesDuration = None
        self.debugMode = False
        self.showNewInfoAtStartup = False
        self.calibrationImages = None
        self.originalImage = None
        self.chessboardImage = None
        self.threeChannelGrayImage = None
        self.centerGrayImage = None
        self.mask = None
        self.indexImage = None
        self.contoursList = None
        self.originalImageSize_preCrop = None
        self.originalImageSize_afterCrop = None
        self.generateMask = False
        self.roundnessThreshold = 0.9
        self.chessboardRows = 6
        self.chessboardColumns = 8
        self.chessboardSize = 20
        self.chessboardSquareState = False
        self.objPoints = None
        self.imgPoints = None
        self.objp = None
        self.criteria = None
        self.objectDistance = None
        self.mmPerPxRatio = None
        self.meanError = None
        self.referencePoint = None
        self.referenceImage_path = None
        self.referenceList_path = None

    def undoCalibrationProgress(self):
        """restarts calibration process

        Returns:
            bool: True
        """
        self.calibrationImages = None
        self.cameraOwner = None
        self.cameraName = None
        self.lensName = None
        self.lensFocalLength = None
        self.chessboardRows = 6
        self.chessboardColumns = 8
        self.chessboardSize = 1.0
        self.chessboardSquareState = False
        self.objPoints = None
        self.imgPoints = None
        self.objp = None
        self.criteria = None
        self.objectDistance = None
        self.mmPerPxRatio = None
        self.meanError = None
        return True

    def undoProcessProgress(self):
        """restarts processing progress

        Returns:
            bool: True
        """
        self.binarizedImage = None
        self.binarizeState = False
        self.contoursList = None
        self.contoursState = False
        return True

    def makeSubDirs(self):
        """creates subdirs when not found
        """
        if self.workspaceSetState:
            directory = self.workspaceDir
        else:
            directory = os.getcwd()
        self.dir = directory
        self.dir = self.dir.replace('\\', '/')
        self.data_subdir = self.dir + '/data'
        self.res_subdir = self.dir + '/res'
        self.result_subdir = self.dir + '/result'
        while not os.path.isdir(self.data_subdir):
            os.mkdir(self.data_subdir)
        while not os.path.isdir(self.res_subdir):
            os.mkdir(self.res_subdir)
        while not os.path.isdir(self.result_subdir):
            os.mkdir(self.result_subdir)

    def getStatusIcons(self):
        """returns status icon pixmaps

        Returns:
            tuple: tuple of status icon pixmaps
        """
        return self.status_icon_none, self.status_icon_okay, self.status_icon_wait, self.status_icon_fail      

    def setCalibrationState(self, state):
        """sets calibration state, then emits signal

        Args:
            state (bool): whether the calibration process was finished or calibration data was loaded
        """
        self.calibrationState = state
        self.calibrationState_Signal.emit(state)
    def setImageLoadState(self, state):
        """sets image load state, then emits signal

        Args:
            state (bool): whether an object image was loaded
        """
        self.imageLoadState = state
        self.imageLoadState_Signal.emit(state)
    def setChessboardImageState(self, state):
        """sets chessboard image load state, then emits signal

        Args:
            state (bool): whether a chessboard image was loaded
        """
        self.chessboardImageState = state
        self.chessboardImageState_Signal.emit(state)
    def setProcessState(self, state):
        """sets the state of the image editing process, then emits signal

        Args:
            state (bool): whether the image processing progress was completed
        """
        self.processState = state
        self.processState_Signal.emit(state)
    def setBinarizeState(self, state):
        """sets state of binary image creation, then emits signal

        Args:
            state (bool): whether a binary image was created
        """
        self.binarizeState = state
        self.binarizeState_Signal.emit(state)
    def setContoursState(self, state):
        """sets the state of the contour process, then emits signal

        Args:
            state (bool): whether contours were found
        """
        self.contoursState = state
        if self.contoursList is not None and len(self.contoursList) > 0:
            self.contoursState_Signal.emit(True)
    def setNewReferenceState(self, state):
        """sets the state of a new reference point, then emits signal

        Args:
            state (bool): whether a new reference point was set
        """
        self.newReferenceState = state
        self.newReferenceState_Signal.emit(state)
    def setDiameterCorrectionState(self, state):
        """sets the state whether a found diameter was corrected, then emits signal

        Args:
            state (bool): wether a diameter was changed
        """
        self.diameterCorrectionState = state
        self.diameterCorrectionState_Signal.emit(state)
    def setExportDataState(self, state):
        """sets the state of data export, then emits signal

        Args:
            state (bool): whether data was exported
        """
        self.exportState = state
        self.exportDataState_Signal.emit(state)

    def loadSettings(self):
        """loads the settings from a pickle file

        Returns:
            bool: False if somethin went wrong
        """
        found_file = False
        defaultFilename = '/data/settings.p'
        directory = os.getcwd()
        filepath = directory + defaultFilename
        if os.path.isfile(filepath):
            found_file = True
        else:
            if self.startupDone:
                filepath = self._openFile(directory, 'pickle')
                if not filepath:
                    return False
                else:
                    found_file = True
        if found_file:
            try:
                settingsPickle = pickle.load(open(filepath, 'rb'))
                self.workspaceDir = settingsPickle['workspace_dir']
                self.workspaceSetState = settingsPickle['workspace_state']
                self.scaleFactor = settingsPickle['scale_factor']
                self.maxScreenSize = settingsPickle['max_screen']
                self.showImagesDuration = settingsPickle['show_duration']
                self.debugMode = settingsPickle['debug_mode']
                self.showNewInfoAtStartup = settingsPickle['show_startup']
                self.generateMask = settingsPickle['generate_mask']
                self.roundnessThreshold = settingsPickle['roundness_threshold']
                self.wasDisclaimerAccepted = settingsPickle['disclaimer_accepted']
                self.morphMode = settingsPickle['morph_mode']
            except Exception as e:
                return False

    def saveSettings(self):
        """saves the settings to a pickle file

        Returns:
            bool: True when no exception, False when Exception occured
        """
        filepath = self.data_subdir
        while not os.path.isdir(filepath):
            os.mkdir(filepath)
        filename = filepath + '/settings.p'
        settingsPickle = {}
        settingsPickle['workspace_dir'] = self.workspaceDir
        settingsPickle['workspace_state'] = self.workspaceSetState
        settingsPickle['scale_factor'] = self.scaleFactor
        settingsPickle['max_screen'] = self.maxScreenSize
        settingsPickle['show_duration'] = self.showImagesDuration
        settingsPickle['debug_mode'] = self.debugMode
        settingsPickle['show_startup'] = self.showNewInfoAtStartup
        settingsPickle['generate_mask'] = self.generateMask
        settingsPickle['roundness_threshold'] = self.roundnessThreshold
        settingsPickle['disclaimer_accepted'] = self.wasDisclaimerAccepted
        settingsPickle['morph_mode'] = self.morphMode
        try:
            pickle.dump(settingsPickle, open(filename, 'wb'))
            return True
        except Exception as e:
            return False

    def loadCalibrationData(self):
        """loads calibration data from a pickle file

        Returns:
            bool: True if file was loaded and processed, False when Exception occured
        """
        file = self._openFile(self.data_subdir, 'pickle')
        if file:
            try:
                calData_pickle = pickle.load(open(file, 'rb'))
                self.cameraName = calData_pickle['cam_name']
                self.lensName = calData_pickle['lens_name']
                self.cameraOwner = calData_pickle['owner']
                self.lensFocalLength = calData_pickle['foc_len']
                self.scaleFactor = calData_pickle['scale']
                self.cameraMatrix = calData_pickle['mtx']
                self.new_cameraMatrix = calData_pickle['new_mtx']
                self.distMatrix = calData_pickle['dist']
                self.rotVector = calData_pickle['rvec']
                self.tanVector = calData_pickle['tvec']
                self.calROI = calData_pickle['roi']
                self.chessboardSize = calData_pickle['square_size']
                self.meanError = calData_pickle['mean_error']
                self.setCalibrationState(True)
                return True
            except Exception as e:
                return False

    def saveCalibrationData(self):
        """saves the generated calibration data to a pickle file

        Raises:
            NoGeneralCalibrationInformationException: When no general data was generated before executing function
            NoCalDataException: When no calibration data was generated before executing function

        Returns:
            bool: True when saving without Exception, else False
        """
        if self.calibrationState:
            if (self.cameraOwner or self.cameraName or self.lensName or self.lensFocalLength) == None:
                raise NoGeneralCalibrationInformationException
            calData_pickle = {}
            calData_pickle['cam_name'] = self.cameraName
            calData_pickle['lens_name'] = self.lensName
            calData_pickle['owner'] = self.cameraOwner
            calData_pickle['foc_len'] = self.lensFocalLength
            calData_pickle['scale'] = self.scaleFactor
            calData_pickle['mtx'] = self.cameraMatrix
            calData_pickle['new_mtx'] = self.new_cameraMatrix
            calData_pickle['dist'] = self.distMatrix
            calData_pickle['rvec'] = self.rotVector
            calData_pickle['tvec'] = self.tanVector
            calData_pickle['roi'] = self.calROI
            calData_pickle['square_size'] = self.chessboardSize
            calData_pickle['mean_error'] = self.meanError
            h, w = self.calibrationImages[0].shape[:2]
            if self.workspaceSetState:
                path = self.workspaceDir  + '/data/'
            else:
                path = self.data_subdir + '/'
            filepathAndName = path + self.cameraOwner[0:3] + self.cameraName[0:5] + self.lensName[0:3] + '_' + str(w) + 'x' + str(h) + '_calData.p'
            try:
                pickle.dump(calData_pickle, open(filepathAndName, 'wb'))
                return True
            except Exception as e:
                return False
        else:
            raise NoCalDataException()

    def calculateCalibrationData(self):
        """calculates calibration data

        Raises:
            NoImageException: when no calibration images were found

        Returns:
            bool: True if process was succesfull, else False
        """
        #check if a size of chessboard aquares was given for calculation and store as state
        if self.calibrationImages == None or len(self.calibrationImages) == 0:
            raise NoImageException()
        if self.chessboardSize == None or self.chessboardSize == 1.0:
            self.chessboardSquareState = False
            self.chessboardSize = 1.0
        else:
            self.chessboardSquareState = True
        if self.chessboardRows == None or self.chessboardRows == 0:
            self.chessboardRows = 6 #default
        if self.chessboardColumns == None or self.chessboardColumns == 0:
            self.chessboardColumns = 8  #default
        if self.showImagesDuration == None:
            showImages = False
        else:
            showImages = True
            duration = self.showImagesDuration
        objp = np.zeros((self.chessboardRows * self.chessboardColumns, 3), np.float32)
        objp[:,:2] = np.mgrid[0:self.chessboardRows, 0:self.chessboardColumns].T.reshape(-1, 2) * self.chessboardSize
        objPoints = []
        imgPoints = []
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        for img in self.calibrationImages:
            temp = copy.copy(img)
            gray_temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray_temp, (self.chessboardRows, self.chessboardColumns), None)
            if ret == True:
                objPoints.append(objp)
                corners2 = cv2.cornerSubPix(gray_temp, corners, (5,5), (-1,-1), criteria)
                imgPoints.append(corners2)
                if showImages:
                    temp = cv2.drawChessboardCorners(temp, (self.chessboardColumns, self.chessboardRows), corners2, ret)
                    temp_img = self._scaleImageForScreen(temp)
                    cv2.imshow('Chessboard images', temp_img)
                    cv2.waitKey(duration)
                    cv2.destroyAllWindows()
        ret = None
        ret, cameraMatrix, distMatrix, rotVector, tanVector = cv2.calibrateCamera(objPoints, imgPoints, gray_temp.shape[::-1], None, None)
        if ret is not None:
            self.cameraMatrix = cameraMatrix
            self.distMatrix = distMatrix
            self.rotVector = rotVector
            self.tanVector = tanVector
            self.objPoints = objPoints
            self.imgPoints = imgPoints
        else:
            return False
        new_cameraMatrix, calROI = self._createNewOptimalCameraMatrix()
        if new_cameraMatrix.any() and calROI is not None:
            self.new_cameraMatrix = new_cameraMatrix
            self.calROI = calROI
            result = self._calcMeanError()
            if result == True:
                return True
            else:
                return False
        else:
            return False

    def undistortAndCropImage(self, image=None):
        """undistorts and crops an image after calibration progress finished

        Args:
            image (Numpy ndarray): an image that needs to be undistorted and cropped. Raises Exception if not provided.

        Raises:
            MissingInputException: When no image was provided

        Returns:
            tuple: tuple of cropped image as Numpy ndarray and its size as tuple
        """
        if not (image.any() or self.cameraMatrix.any() or self.distMatrix.any() or self.new_cameraMatrix.any() or self.calROI.any()):
            raise MissingInputException()
        try:
            #undistort
            undistortedImage = cv2.undistort(image, self.cameraMatrix, self.distMatrix, None, self.new_cameraMatrix)
            #crop
            x, y, w, h = self.calROI
            croppedImage = undistortedImage[y:y+h, x:x+w]
            croppedImage_shape = croppedImage.shape
            return croppedImage, croppedImage_shape
        except Exception as e:
            return None, None

    def calcCameraObjectDistance(self):
        """calculates distance between object and camera sensor and the mm per pixel ratio of the image

        Raises:
            MissingInputException: raised when no image or calibration data found
            NoChessboardException: raised when no chessboard detected in image

        Returns:
            bool: True if no error occured, else False if other exception happened
        """
        if not (self.chessboardImage.any() or self.new_cameraMatrix.any() or self.distMatrix.any()) or self.chessboardSize == None:
            raise MissingInputException()
        if self.chessboardRows == None or self.chessboardRows == 0:
            self.chessboardRows = 6 #default value
        if self.chessboardColumns == None or self.chessboardColumns == 0:
            self.chessboardColumns = 8  #default value
        try:
            img = copy.copy(self.chessboardImage)
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray_img = cv2.medianBlur(gray_img, 3)
            objpoints = []
            imgpoints = []
            objp = np.zeros((self.chessboardRows * self.chessboardColumns, 3), np.float32)
            objp[:,:2] = np.mgrid[0:self.chessboardRows, 0:self.chessboardColumns].T.reshape(-1,2) * self.chessboardSize
            ret, corners = cv2.findChessboardCorners(gray_img, (self.chessboardRows,self.chessboardColumns), None)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            if ret == True:
                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray_img, corners, (5,5), (-1,-1), criteria)
                imgpoints.append(corners2)
                ret2, rvec, tvec = cv2.solvePnP(objp, corners2, self.new_cameraMatrix, self.distMatrix)
                if ret2:
                    distance = math.sqrt(tvec[0]*tvec[0] + tvec[1]*tvec[1] + tvec[2]*tvec[2])
                    #
                    #   Indexnummern der Punkte in imgpoints bei 9x7 Schachbrett
                    #   Kann auch rotiert oder gespiegelt auftreten
                    #   42  36  30  24  18  12  6   0
                    #   43  37  31  25  19  13  7   1
                    #   44  38  32  26  20  14  8   2
                    #   45  39  33  27  21  15  9   3
                    #   46  40  34  28  22  16  10  4
                    #   47  41  35  29  23  17  11  5
                    #
                    x1, y1 = imgpoints[0][0][0]
                    x2, y2 = imgpoints[0][5][0]
                    length_px_v = math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
                    x3, y3 = imgpoints[0][42][0]
                    length_px_h = math.sqrt((x1-x3)*(x1-x3) + (y1-y3)*(y1-y3))
                    length_v_mm = 5 * self.chessboardSize
                    length_h_mm = 7 * self.chessboardSize
                    mm_px_ratio_v = length_v_mm/length_px_v
                    mm_px_ratio_h = length_h_mm/length_px_h
                    mm_px_ratio = (mm_px_ratio_v + mm_px_ratio_h) /2
                    self.objectDistance = distance
                    self.mmPerPxRatio = mm_px_ratio
                    return True
                else:
                    raise NoChessboardException()
        except Exception as e:
            return False

    def equalizeHistory(self, image):
        """equalizes the history of an image

        Args:
            image (NumPy ndarray): 3 channel color image

        Returns:
            ndarray: equalized image
        """
        temp = copy.copy(image)
        b, g, r = cv2.split(temp)
        r_eq = cv2.equalizeHist(r)
        g_eq = cv2.equalizeHist(g)
        b_eq = cv2.equalizeHist(b)
        temp = cv2.merge((b_eq, g_eq, r_eq))
        cv2.medianBlur(temp, 3)
        return temp

    def findContours(self):
        """detects contours in an binarized image,
        calculates area perimeter, center of contour and stores in a list of dictionaries

        Raises:
            MissingInputException: if no binarized image saved previously

        Returns:
            bool: True when no error occured
        """
        if not self.binarizeState:
            raise MissingInputException()
        if self.showImagesDuration == None or self.originalImage is None:
            showImages = False
        else:
            showImages = True
        cont = cv2.findContours(self.binarizedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = cont[0]
        hierarchy = cont[1]
        
        if showImages:
            cont_img = copy.copy(self.originalImage)
            target_exists = True
        else:
            target_exists = False
        if self.generateMask == True:
            height, width = self.binarizedImage.shape
            mask_img = np.zeros((width, height), dtype='uint8')
        contoursList = []
        index_counter = 0
        areaThreshold_Low = self.scaleFactor * 500
        areaThreshold_High = self.scaleFactor * 1000000
        for c in contours:
            #calculate area
            area = cv2.contourArea(c)
            #sort out very small areas (=interference)
            if (area > areaThreshold_Low) and (area < areaThreshold_High):
                #calculate smallest surrounding rectangle
                x, y, w, h = cv2.boundingRect(c)
                middle_x_rect = x + (w/2)
                middle_y_rect = y + (h/2)
                #calculate center of area with moments
                M = cv2.moments(c)
                cx_moment = M['m10'] / M['m00']
                cy_moment = M['m01'] / M['m00']
                #calculate arithmetic mean of center
                mean_cx = int(((middle_x_rect + cx_moment) / 2) + 0.5)
                mean_cy = int(((middle_y_rect + cy_moment) / 2) + 0.5)
                #calculate perimeter
                perimeter = cv2.arcLength(c, True)
                dict = {
                    'contour_index': index_counter,
                    'contour_points_px': c,
                    'contour_points_ref': None,
                    'contour_points_mm': None,
                    'contour_center_px': (mean_cx,mean_cy),
                    'contour_area_px': area,
                    'contour_perimeter_px': perimeter,
                    'contour_is_hole': None,
                    'center_point_ref': None,
                    'center_point_ref_mm': None,
                    'roundness': None,
                    'diameter_px': None,
                    'diameter_mm': None,
                    'deviation_px': None,
                    'deviation_mm': None,
                    'set_diameter_manually': False
                }
                contoursList.append(dict)
                index_counter += 1
                if target_exists:
                    #draw rectangle around contour
                    cv2.rectangle(cont_img, (x, y), (x+w, y+h), (0, 128, 255), 2)
                    #highlight contour outline
                    cv2.drawContours(cont_img, [c], -1, (36, 255, 12), 3)
                if self.generateMask == True:
                    cv2.drawContours(mask_img, [c], -1, 255, 1)
        for cont in contoursList:
            self._calcRoundness(contourFromList=cont)
        if target_exists:
            cont_img = self._scaleImageForScreen(cont_img)
            cv2.imshow('Contours image', cont_img)
            cv2.waitKey(self.showImagesDuration*2)
            cv2.destroyAllWindows()
        if self.generateMask == True:
            self.mask = mask_img
        self.contoursList = contoursList
        return True

    def findObjectCenter(self):
        """tries to detect the center of an object image by cutting out everything but the center region of the image and applying hough circle algorithm
        intended to find the center of the crankshaft

        Raises:
            MissingInputException: raised when no object image detected
            NoFormException: raised when no circle was found

        Returns:
            tuple: (x,y) coordinate of the found circle
        """
        if self.originalImage is None:
            raise MissingInputException()
        image = copy.copy(self.originalImage)
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = grayImage.shape
        center_height = int(height*0.25)
        center_width = int(width*0.25)
        center_img = np.zeros((center_height, center_width), dtype='uint8')
        offset_v = int((height - center_height) / 2)
        offset_h = int((width - center_width) / 2)
        for row in range(center_height):
            for col in range(center_width):
                center_img[row, col] = grayImage[row + offset_v, col + offset_h]
        img_center_x = 0
        img_center_y = 0
        circles = cv2.HoughCircles(center_img, cv2.HOUGH_GRADIENT, 1.2, 800)
        if circles is not None:
            circles = np.round(circles[0, :]).astype('int')
            max_r = 0
            for (x, y, r) in circles:
                #größter kreis
                if r > max_r:
                    img_center_x = x
                    img_center_y = y
                #if showImages:
                gray_three_channel = cv2.merge((center_img, center_img, center_img))
                cv2.circle(gray_three_channel, (img_center_x, img_center_y), r, (0, 0, 255), 2)
                #mitte markieren
                cv2.rectangle(gray_three_channel, (img_center_x-3,img_center_y-3), (img_center_x+3,img_center_y+3), (0, 128, 255), -1)
                cv2.imshow('center', gray_three_channel)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            img_center_x = img_center_x + offset_h
            img_center_y = img_center_y + offset_v
            middlePoint = (img_center_x, img_center_y)
            return middlePoint
        else:
            raise NoFormException()

    def prepareImageForCenterView(self):
        """creates a 3 channel gray image of the center region of the object image

        Returns:
            tuple: consisting of the 3-channel-gray image, the horizontal and vertical offset
        """
        image = copy.copy(self.originalImage)
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = grayImage.shape
        centerHeight = int(height * 0.25)
        centerWidth = int(width * 0.25)
        centerGray = np.zeros((centerHeight, centerWidth), dtype='uint8')
        offset_v = int((height - centerHeight) / 2)
        offset_h = int((width - centerWidth) / 2)
        for row in range(centerHeight):
            for col in range(centerWidth):
                centerGray[row, col] = grayImage[row + offset_v, col + offset_h]
        centerImageThreeChan = cv2.merge((centerGray, centerGray, centerGray))
        self.centerGrayImage = centerGray
        return centerImageThreeChan, offset_h, offset_v

    def findCircles(self, image=None, dp=None, minDist=None):
        """tries to find a circle in a given image with the given parameters
        dp (= accumulator value of algorithm) and minDist (= minimum distance between two circles)

        Args:
            image (NumPy ndarray: a grayscale image
            dp (float): accumulator value of hough algorithm
            minDist (int): minimum distance between two circles

        Raises:
            MissingInputException: if at least one argument is None

        Returns:
            tuple: center coordinates of the circle x and y with the radius of the circle or tuple of None if no circle was found
        """
        if not image.any() or (dp or minDist) == None:
            raise MissingInputException()
        circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp, minDist)
        if circles is not None:
            max_r = 0
            circles = np.round(circles[0, :]).astype('int')
            for (x, y, r) in circles:
                if r > max_r:
                    center_x = x
                    center_y = y
                    max_r = r
            return center_x, center_y, max_r
        else:
            return None, None, None

    def transformContoursList(self):
        """transforms coordinates in the list with the saved contours matching a new reference point

        Raises:
            MissingInputException: raised when no contours list or reference point was found

        Returns:
            bool: True if no error occured
        """
        if self.contoursList == None or len(self.contoursList) == 0 or self.referencePoint == None:
            raise MissingInputException()
        else:
            for cont in self.contoursList:
                new_middle = self._pointTransformCoordinateSystem(point=cont['contour_center_px'])
                cont.update({'center_point_ref': new_middle})
                contPointList = cont['contour_points_px']
                for i in range(len(contPointList)):
                    (old_x, old_y) = contPointList[i][0]
                    old_point = (old_x, old_y)
                    new_point = self._pointTransformCoordinateSystem(point=old_point)
                    contPointList[i][0] = new_point
                cont.update({'contour_points_ref': contPointList})
            return True

    #creates a dxf drawing with all found contours
    def exportToDXF(self):
        """exports the contours from the contours list to a R2010 dxf file

        Raises:
            MissingInputException: raised if no contours list was found
            e: if a exception occurs it gets passed through

        Returns:
            bool: True when finished
        """
        if self.contoursList == None or len(self.contoursList) == 0:
            raise MissingInputException()
        try:
            #flig y axis because cv2 and dxf dirextions are opposite
            self._flipYAxis()
            #create a new DXF drawing
            #official version name: 'AC1024'
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            #create a layer for holes
            doc.layers.new(name='HoleLayer')
            doc.layers.new(name='ContourLayer') 
            #iterate through contours and add contour to drawing
            for cont in self.contoursList:
                if cont['contour_is_hole']:
                    radius = cont['diameter_mm']/2
                    msp.add_circle(cont['center_point_ref_mm'], radius, dxfattribs={'layer': 'HoleLayer'})
                else:
                    list = []
                    for i in range(len(cont['contour_points_mm'])):
                        x, y = cont['contour_points_mm'][i]
                        list.append((x, y))
                    list.append(list[0])    #close perimeter line of contour
                    msp.add_lwpolyline(list, dxfattribs={'layer': 'ContourLayer'})
            if self.manufacturer == None or self.modelName == None:
                filename = '/AVL_motorsichel'    #default export name
            else:
                filename = '/' + self.manufacturer + '_' + self.modelName
            filepath = self.result_subdir + filename + '.dxf'
            while os.path.isfile(filepath):             #   file#1.dxf
                temp = filepath.split('.', 1)           #   file#1  dxf
                if len(temp) == 2:
                    sub_temp = temp[0].split('#', 1)    #   file    1
                    if len(sub_temp) == 2:
                        index = int(sub_temp[1])
                        index += 1
                    elif len(sub_temp) == 1:
                        index = 1
                    else:   #something went wrong
                        return False
                else:   #something went wrong
                    return False
                filepath = sub_temp[0] + '#' + str(index) + '.dxf'
            doc.saveas(filepath)

            return True
        except Exception as e:
            raise e #pass the exception through

    def openPDFinExternalViewer(self, fileName=None):
        """opens a given pdf file in a browser or standard program

        Args:
            fileName (string): name of the file stored in the res subdirectory that should be opened

        Raises:
            MissingInputException: raised when no filename given

        Returns:
            bool: True when no error occured, else False
        """
        if fileName == None:
            raise MissingInputException()
        else:
            filepath = self.res_subdir + fileName
            if os.path.isfile(filepath):
                try:
                    webbrowser.open_new(filepath)
                    return True
                except IOError as e:
                    return False
                except FileNotFoundError as e:
                    return False
            else:
                return False

    def loadCalImagesFromDirectory(self):
        """opens dialog to select a directory , then loads all images in directory as calibration images.
        images will be scaled with saved factor.
        showing loaded images is optional.

        Returns:
            bool: True when no error occured, else False
        """
        if self.scaleFactor == None:
            self.scaleFactor = 1.0
        if self.showImagesDuration == None:
            showImages = False
        else:
            showImages = True
        files = self._openFileDirectory('jpg')
        if files:
            temp_images = []
            for fname in files:
                try:
                    img = cv2.imread(fname)
                    if self.scaleFactor != 1.0:
                        img = cv2.resize(img, None, fx=self.scaleFactor, fy=self.scaleFactor, interpolation=cv2.INTER_CUBIC)
                    temp_images.append(img)
                    if showImages:
                        temp = self._scaleImageForScreen(img)
                        cv2.imshow('', temp)
                        cv2.waitKey(self.showImagesDuration)
                        cv2.destroyAllWindows()
                except Exception as e:
                    return False
            if len(temp_images) >= 10:
                self.calibrationImages = temp_images
                return True
            else:
                return False
        else:
            return False

    def loadImagefromFile(self):
        """opens a dialog to select an image from directory. loads choosen image and resizes it with given factor.
        showing image is optional.

        Returns:
            NumPy ndarray/ None: returns image as Numpy ndarray or None if error occured
        """
        if self.scaleFactor == None:
            self.scaleFactor = 1.0
        if self.showImagesDuration == None:
            showImages = False
        else:
            showImages = True
        file = self._openFile(self.data_subdir, 'image')
        if file:
            try:
                img = cv2.imread(file)
                if self.scaleFactor != 1.0:
                    img = cv2.resize(img, None, fx=self.scaleFactor, fy=self.scaleFactor, interpolation=cv2.INTER_CUBIC)
                if showImages:   
                    temp = self._scaleImageForScreen(img) 
                    cv2.imshow('Loaded image', temp)
                    cv2.waitKey(self.showImagesDuration)
                    cv2.destroyAllWindows()
            except Exception as e:
                return None
            return img
        else:
            return None

    def saveReferenceImageAndList(self):
        """saves a list with all necessary contours information with an image as reference for checking calculated data

        Raises:
            MissingInputException: raised if no contours found or if no object image detected

        Returns:
            bool: True when finished
        """
        if not self.contoursState or self.originalImage is None:
            raise MissingInputException()
        filename = self._generateReferenceFilename()
        self._convertContoursListToMM()
        if self.threeChannelGrayImage is None:
            image = copy.copy(self.originalImage)
            image_single_channel = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.threeChannelGrayImage = cv2.merge((image_single_channel, image_single_channel, image_single_channel))
        image = copy.copy(self.threeChannelGrayImage)
        filepath = self.result_subdir + filename
        while os.path.isfile(filepath):             #   image#1.jpg
            temp = filepath.split('.', 1)           #   image#1  jpg
            if len(temp) == 2:
                sub_temp = temp[0].split('#', 1)    #   image    1
                if len(sub_temp) == 2:
                    index = int(sub_temp[1])
                    index += 1
                elif len(sub_temp) == 1:
                    index = 1
                else:   #something went wrong
                    return False
            else:   #something went wrong
                return False
            filepath = sub_temp[0] + '#' + str(index) + '.jpg'
        path_txt = filepath.split('.', 1)
        filepath_txt = path_txt[0] + '.txt'
        self.referenceImage_path = filepath
        self.referenceList_path = filepath_txt
        file = open(filepath_txt, 'a')

        self.fontSize = self.scaleFactor * 5.5
        self.fontWeight = int(self.scaleFactor * 10)

        for cont in self.contoursList:
            if cont['contour_is_hole']:
                x, y = cont['contour_center_px']
                r = int(cont['diameter_px'])
                cont_index = str(cont['contour_index'])
                cv2.rectangle(image, (x-r, y-r), (x+r, y+r), (0, 128, 255), self.fontWeight)
                cv2.putText(image, cont_index, (x+r+r, y+r), cv2.FONT_HERSHEY_SIMPLEX, self.fontSize, (0, 255, 0), self.fontWeight)
                line = '\nContour Nr:' + cont_index
                file.write(line)
                for key in cont:
                    if key == 'contour_points_px':
                        line = '\n' + str(key) + '(length)\t' + str(len(cont[key]))
                    elif  key == 'contour_points_ref':
                        line = '\n' + str(key) + '(length)\t' + str(len(cont[key]))
                    elif key ==  'contour_points_mm':
                        if cont[key] is not None:
                            line = '\n' + str(key) + '(length)\t' + str(len(cont[key]))
                        else:
                            line = '\n' + str(key) + '\t' + str(cont[key])
                    else:
                        line = '\n' + str(key) + '\t' + str(cont[key])
                    file.write(line)
                file.write('\n')

        #write camera and calibration information to reference list
        line = '\nManufacturer: ' + str(self.manufacturer)
        file.write(line)
        line = '\nModel: ' + str(self.modelName)
        file.write(line)
        line = '\n\nCamera owner: ' + str(self.cameraOwner)
        file.write(line)
        line = '\nCamera name: ' + str(self.cameraName)
        file.write(line)
        line = '\nLens name: ' + str(self.lensName)
        file.write(line)
        line = '\nFocal length: ' + str(self.lensFocalLength)
        file.write(line)
        line = '\nImage scale factor: ' + str(self.scaleFactor)
        file.write(line)
        line = '\nImage resolution (pre crop): ' + str(self.originalImageSize_preCrop)
        file.write(line)
        line = '\nImage resolution (after crop): ' + str(self.originalImageSize_afterCrop)
        file.write(line)
        line = '\nChessboard size: ' + str(self.chessboardColumns) + 'x' + str(self.chessboardRows)
        file.write(line)
        line = '\nChessboard square size: ' + str(self.chessboardSize)
        file.write(line)
        line = '\nmm/Pixel ratio: ' + str(self.mmPerPxRatio)
        file.write(line)
        line = '\nMean error: ' + str(self.meanError)
        file.write(line)
        line = '\nDistance to object: ' + str(self.objectDistance)
        file.write(line)
        line = '\nReference point: ' + str(self.referencePoint)
        file.write(line)
        line = '\nRoundness threshold: ' + str(self.roundnessThreshold)
        file.write(line)
        line = '\nBinary image morphology operation mode: ' + str(self.morph_options[self.morphMode])
        file.write(line)
        
        file.close()
        cv2.imwrite(filepath, image)
        self.indexImage = image
        return True

    def referencePrinter(self):
        """print the generated reference image and list on the standard printer

        Raises:
            MissingInputException: raised if no image or list saved

        Returns:
            bool: True when finished
        """
        if self.referenceImage_path == None or self.referenceList_path == None:
            raise MissingInputException()
        printer_name = win32print.GetDefaultPrinter()
        #
        #   Source
        #   http://timgolden.me.uk/python/win32_how_do_i/print.html
        #
        win32api.ShellExecute(
            0,
            "print",
            self.referenceList_path,
            #
            # If this is None, the default printer will
            # be used anyway.
            #
            '/d:"%s"' % printer_name,
            ".",
            0
        )
        #
        #   SOURCE
        #   http://timgolden.me.uk/python/win32_how_do_i/print.html
        #
        #
        # Constants for GetDeviceCaps
        #
        #
        # HORZRES / VERTRES = printable area
        #
        HORZRES = 8
        VERTRES = 10
        #
        # LOGPIXELS = dots per inch
        #
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        #
        # PHYSICALWIDTH/HEIGHT = total area
        #
        PHYSICALWIDTH = 110
        PHYSICALHEIGHT = 111
        #
        # PHYSICALOFFSETX/Y = left / top margin
        #
        PHYSICALOFFSETX = 112
        PHYSICALOFFSETY = 113

        #
        # You can only write a Device-independent bitmap
        #  directly to a Windows device context; therefore
        #  we need (for ease) to use the Python Imaging
        #  Library to manipulate the image.
        #
        # Create a device context from a named printer
        #  and assess the printable size of the paper.
        #
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        printable_area = hDC.GetDeviceCaps (HORZRES), hDC.GetDeviceCaps (VERTRES)
        printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)
        printer_margins = hDC.GetDeviceCaps (PHYSICALOFFSETX), hDC.GetDeviceCaps (PHYSICALOFFSETY)

        #
        # Open the image, rotate it if it's wider than
        #  it is high, and work out how much to multiply
        #  each pixel by to get it as big as possible on
        #  the page without distorting.
        #
        bmp = Image.open (self.referenceImage_path)
        if bmp.size[0] > bmp.size[1]:
            bmp = bmp.rotate (90)

        ratios = [1.0 * printable_area[0] / bmp.size[0], 1.0 * printable_area[1] / bmp.size[1]]
        scale = min (ratios)

        #
        # Start the print job, and draw the bitmap to
        #  the printer device at the scaled size.
        #
        hDC.StartDoc(self.referenceImage_path)
        hDC.StartPage()
        dib = ImageWin.Dib (bmp)
        scaled_width, scaled_height = [int (scale * i) for i in bmp.size]
        x1 = int ((printer_size[0] - scaled_width) / 2)
        y1 = int ((printer_size[1] - scaled_height) / 2)
        x2 = x1 + scaled_width
        y2 = y1 + scaled_height
        dib.draw (hDC.GetHandleOutput(), (x1, y1, x2, y2))
        hDC.EndPage ()
        hDC.EndDoc ()
        hDC.DeleteDC ()
        return True

    def createRefImageHSVRange(self):
        """generates a reference image for selecting the correct hsv value threshold

        Returns:
            ndarray: reference image as NumPy ndarray
        """
        height = 256
        width = 540
        margin_v = 56
        margin_h = 90
        blank_image = np.zeros(((height+2*margin_v), (width+2*margin_h), 3), np.uint8)
        hue = 0
        saturation = 0
        value = 255
        #iterate through pixels of blank image and set incrementing hue val for x-axis
        #and incrementing saturation value on y-axis
        for angle in range(margin_h, width+margin_h, 1):
            for saturation in range(margin_v, height+margin_v, 1):
                hsv_val = np.uint8([[[hue, saturation-margin_v, value]]])
                bgr_val = cv2.cvtColor(hsv_val, cv2.COLOR_HSV2BGR)
                blank_image[saturation, angle] = bgr_val[0]
                #tick marks y-axis
                if (saturation-margin_v) % 50 == 0 and saturation > 0:
                    cv2.line(blank_image, (margin_h-5, saturation), (margin_h+5, saturation), (255, 255, 255), 1)
            #tick marks x-axis
            if (angle-margin_h) % 30 == 0 and angle > 0:
                cv2.line(blank_image, (angle, margin_v+height-5), (angle, margin_v+height+5), (255, 255, 255), 1)
            if (angle-margin_h) % 3 == 0 and angle > 0:
                hue += 1
        #x axis
        cv2.line(blank_image, (margin_h+width, margin_v+height-5), (margin_h+width, margin_v+height+5), (255, 255, 255), 1)
        cv2.line(blank_image, (margin_h-15,margin_v+height), (margin_h+width+15, margin_v+height), (255, 255, 255), 2)
        cv2.putText(blank_image, '0', (margin_h+5, margin_v+height+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '30', (margin_h+80, margin_v+height+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '60', (margin_h+170, margin_v+height+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '90', (margin_h+int(width/2)-10, margin_v+height+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '120', (margin_h+345, margin_v+height+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '150', (margin_h+435, margin_v+height+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '180', (margin_h+width-15, margin_v+height+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, f'x-Axis: range of HUE (0-180) with VALUE fixed', (margin_h+70, margin_v+height+48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        #y axis
        cv2.line(blank_image, (margin_h, margin_v+height+15), (margin_h, margin_v-15), (255, 255, 255), 2)
        cv2.putText(blank_image, '250', (margin_h-55, margin_v+255), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '0', (margin_h-55, margin_v+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '50', (margin_h-55, margin_v+55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '100', (margin_h-55, margin_v+105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '150', (margin_h-55, margin_v+155), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, '200', (margin_h-55, margin_v+205), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, f'y-Axis: range of SATURATION (0-255) with VALUE fixed', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,128,255), 1, cv2.LINE_AA)
        cv2.putText(blank_image, f'VALUE={value} (range 0-255)', (margin_h+int(width/2), margin_v+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        return blank_image


    #######################################################################################################################################################################################
    #   Methods for internal use   
    ####################################################################################################################################################################################### 
    def _generateReferenceFilename(self):
        """generates a filename for the reference image and list

        Returns:
            string: filename
        """
        filename = '/reference.jpg'
        if (self.manufacturer or self.modelName) == None:
            return filename
        else:
            full_filename = self.manufacturer + self.modelName + '_' + filename
            return full_filename

    def _calcRoundness(self, contourFromList=None):
        """calculates the roundness as diameter ratio of an found contour as indicator whether it is a drill hole or not
        also calculates average diameter in pixel and mm and the deviation between to diameters as indicator for the quality of a measurement

        Args:
            contourFromList (dictionary): dictionary with all information regarding a single contour

        Raises:
            MissingInputException: raised when no contour dictionary provided

        Returns:
            bool: True when finished
        """
        if contourFromList == None:
            raise MissingInputException()
        else:
            area = contourFromList['contour_area_px']
            perimeter = contourFromList['contour_perimeter_px']
            #calculate roundness
            d_area = round(math.sqrt(4 * area / math.pi), 2)
            d_perimeter = round(perimeter / math.pi, 2)
            #the nearer the ratio is to 1 the greater is the roundness
            diameter_ratio = round(d_area/d_perimeter, 2)
            average_diameter = round((d_area + d_perimeter) / 2, 2)
            average_diameter_mm = round(self._convertToMM(measure=average_diameter), 2)
            deviation_area = round(abs(average_diameter - d_area), 2)
            deviation_perimeter = round(abs(average_diameter - d_perimeter), 2)
            if deviation_area > deviation_perimeter:
                maxDeviation = deviation_area
            else:
                maxDeviation = deviation_perimeter
            maxDeviation_mm = round(self._convertToMM(measure=maxDeviation), 2)
            if diameter_ratio >= self.roundnessThreshold:
                isHole = True
            else:
                isHole = False
            contourFromList.update({'roundness': diameter_ratio})
            contourFromList.update({'diameter_px': average_diameter})
            contourFromList.update({'diameter_px': maxDeviation})
            contourFromList.update({'diameter_mm': average_diameter_mm})
            contourFromList.update({'deviation_mm': maxDeviation_mm})
            contourFromList.update({'contour_is_hole': isHole})
            return True

    def _convertToMM(self, measure=None):
        """converts a given measurement from pixel to mm

        Args:
            measure (float): value of the measurement that needs to be converted

        Raises:
            MissingInputException: raised when no measurement given

        Returns:
            float: measurement in mm
        """
        if measure == None or self.mmPerPxRatio == None:
            raise MissingInputException()
        else:
            return measure * self.mmPerPxRatio

    def _openFile(self, str_progDir, str_fileType):
        """opens a dialog to open a file

        Args:
            str_progDir (str): name of the directory that should be opened
            str_fileType (str): str as indicator which filetype should be opened

        Returns:
            str: path of the selected file
        """
        if str_fileType == "image":
            fileType = 'Images (*.png *.jpg)'
        if str_fileType == 'pickle':
            fileType = 'Pickles (*.p)'
        file, _ = QFileDialog.getOpenFileName(None, 'Open file',
            str_progDir, fileType)
        if not file:
            return None
        else:
            return file

    def _openFileDirectory(self, str_fileFormat):
        """opens a dialog to select a directory, all files with given fileformat will be selected

        Args:
            str_fileFormat (str): str with file format ending

        Returns:
            list: list with all files with corresponding file ending in selected directory
        """
        sel_dir = QFileDialog.getExistingDirectory()
        if not sel_dir:
            return None
        else:
            path = sel_dir + '//*.' + str_fileFormat
            files = glob.glob(path)
            return files

    def _scaleImageForScreen(self, image):
        """scales an image for screen presentation if necessary

        Args:
            image (ndarray): image as Numpy ndarray that should be scaled

        Returns:
            ndarray/ None: Scaled image, if it was larger than max Size, else image from Args
                            None if error occured
        """
        scale_factor = 1
        if self.maxScreenSize == None:
            maxSize = 0.75
        else:
            maxSize = self.maxScreenSize
        try:
            #size of image
            img_shape = image.shape
            h = img_shape[0]
            w = img_shape[1]
            #screensize primary monitor
            user32 = ctypes.windll.user32
            screen_w = user32.GetSystemMetrics(0)*maxSize
            screen_h = user32.GetSystemMetrics(1)*maxSize
        except Exception as e:
            return None
        else:
            if screen_w < w or screen_h < h:
                ratio_width = 1
                ratio_height = 1
                if h > screen_h:
                    ratio_height = screen_h / h
                if w > screen_w:
                    ratio_width = screen_w / w
                if ratio_width < ratio_height:
                    factor = ratio_width
                else:
                    factor = ratio_height
                scale_factor = round(factor, 2)
                img = copy.copy(image)
                img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation= cv2.INTER_CUBIC)
                return img
            else:
                return image

    def _createNewOptimalCameraMatrix(self):
        """creates a better camera matrix for undisturbing images and calculates a ROI for cropping the images

        Raises:
            MissingInputException: raised when no calibration images, camera matrix or distMatrix provided

        Returns:
            tuple: new camera matrix and matrix with valid pixels in the image or None if error occured
        """
        if (self.calibrationImages or self.cameraMatrix or self.distMatrix) == None:
            raise MissingInputException()
        try:
            h, w = self.calibrationImages[0].shape[:2]
            new_cameraMatrix, calROI = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distMatrix, (w,h), 1, (w,h))
            return new_cameraMatrix, calROI
        except Exception as e:
            return None, None

    def _calcMeanError(self):
        """calculates the mean re-projection error of all found chessboard corners. distance between projected and calculated position of chessboard corner.
        is an indicator for quality of camera calibration

        Raises:
            MissingInputException: raised when at least one of the necessary input is missing

        Returns:
            bool: True when finished, False when error occured
        """
        if (self.objPoints or self.imgPoints or self.rotVector or self.tanVector or self.cameraMatrix or self.distMatrix) == None:
            raise MissingInputException()
        try:
            meanError = 0
            for i in range(len(self.objPoints)):
                imagePoints, _ = cv2.projectPoints(self.objPoints[i], self.rotVector[i], self.tanVector[i], self.cameraMatrix, self.distMatrix)
                error = cv2.norm(self.imgPoints[i], imagePoints, cv2.NORM_L2)/len(imagePoints)
                meanError += error
            meanError = meanError/len(self.objPoints)
            self.meanError = meanError
            return True
        except Exception as e:
            return False

    def _pointTransformCoordinateSystem(self, point=None):
        """recalculates a point, given as x,y-tuple, corresponding to a reference point

        Args:
            point (list/tuple): x and y coordinate of a point or list with tuple of x and y coordinates

        Raises:
            MissingInputException: raised if no reference point saved or no point given
            InappropriateParameterException: raised when args does not match tuple or list

        Returns:
            tuple/ list: tuple with new x and y coordinate or list with new coordinates
        """
        if self.referencePoint == None or point is None:
            raise MissingInputException()
        else:
            if isinstance(point, tuple):
                newPoint = (point[0]-self.referencePoint[0], point[1]-self.referencePoint[1])
                return newPoint
            elif isinstance(point, list):
                newCoordinates = []
                for p in point:
                    newPoint = self._pointTransformCoordinateSystem(point=p)
                    newCoordinates.append(newPoint)
                return newCoordinates
            else:
                raise InappropriateParameterException()

    def _flipYAxis(self):
        """flips the values of the y-axis coordinates, only in mm, in the contours list.
        this is necessary because in this program y-axis is from top to bottom and in cad programs it runs from bottom to top

        Raises:
            MissingInputException: raised when contours state was not set to true

        Returns:
            bool: True when finished flipping x-axis coordinates
        """
        if not self.contoursState:
            raise MissingInputException()
        for cont in self.contoursList:
            for i in range(len(cont['contour_points_mm'])):
                x, y = cont['contour_points_mm'][i]
                y *= -1
                cont['contour_points_mm'][i] = (x, y)
            if cont['contour_is_hole']:
                x, y = cont['center_point_ref_mm']
                y *= -1
                cont['center_point_ref_mm'] = (x, y)
        return True

    def _convertContoursListToMM(self):
        """calculates the values in mm for each x-,y-coordinate in the contours list

        Raises:
            MissingInputException: raised if the states of contours or a new reference are not set to true or if the mm/px ratio was not calculated

        Returns:
            bool: True when finished
        """
        if not self.contoursState or not self.newReferenceState or self.mmPerPxRatio == None:
            raise MissingInputException()
        for cont in self.contoursList:
            new_c = []
            for i in range(len(cont['contour_points_px'])):
                (x_px, y_px) = cont['contour_points_px'][i][0]
                new_x_mm = self._convertToMM(measure=x_px)
                new_y_mm = self._convertToMM(measure=y_px)
                new_c.append(tuple((new_x_mm, new_y_mm)))
            cont['contour_points_mm'] = new_c
            if cont['contour_is_hole']:
                (center_x_px, center_y_px) = cont['center_point_ref']
                center_x_mm = self._convertToMM(measure=center_x_px)
                center_y_mm = self._convertToMM(measure=center_y_px)
                new_center_mm = (center_x_mm, center_y_mm)
                cont.update({'center_point_ref_mm': new_center_mm})
        return True