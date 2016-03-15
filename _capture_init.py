import cv2
import numpy as np
import vehicle_tracking as proc
import time

from PyQt4 import QtGui, QtCore
from PyQt4 import uic

# Global variable
main_ui = uic.loadUiType("gtk/video_frame.ui")[0]
start_time = None
width = 960     # pixel
height = 540    # pixel
alpha = 8       # second
mask_status = False
mask_frame = None

class QtCapture(QtGui.QFrame, main_ui):
    def __init__(self, fps, filename):
        global avg
        super(QtGui.QFrame, self).__init__()

        self.fps = fps
        self.setupUi(self)

        # Start Capture Video
        self.cap = cv2.VideoCapture(filename)

        # Initiation to motion blur
        _, frame = self.cap.read()
        frame = proc.convBGR2RGB(frame)
        avg = np.float32(frame)

    def setFPS(self, fps):
        self.fps = fps

    def start(self):
        global start_time
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrame)
        self.timer.start(1000. / self.fps)
        start_time = time.time()
        print format(start_time)
        return start_time

    def stop(self):
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QtGui.QFrame, self).deleteLater()

    def nextFrame(self):
        global mask_status, mask_frame
        real_time = time.time()
        ret, frame_ori = self.cap.read()

        # ---------- Do not disturb this source code ---------- #
        # Default color model is BGR format
        rgb_frame = proc.convBGR2RGB(frame_ori)                 # convert from BGR color model to RGB color model
        # ----------------------------------------------------- #

        # Initiation background subtraction
        # Motion blur object subtraction
        acuWeight = cv2.accumulateWeighted(rgb_frame, avg, 0.01)
        initSubtrack = cv2.convertScaleAbs(acuWeight)               # return rgb color for background subtraction
        initBackground = proc.initBackgrounSubtraction(real_time, start_time, alpha)

        if not mask_status:
            if not initBackground:
                print "initiation background subtraction"
            else:
                print "mask found"
                mask_frame = initSubtrack
                mask_status = True
            subtract_frame = initSubtrack
        else:
            print "mask frame"
            subtract_frame = mask_frame

        # Image processing
        gray_frame = proc.convRGB2GRAY(initSubtrack)

        # Last variable to show must 'show_frame'
        show_frame = gray_frame
        show_frame = cv2.resize(show_frame, (width, height))    # resize frame

        # ---------- Do not disturb this source code ----------- #
        # Gray scale, binary image - Format_Indexed8
        # RGB image - Format_RGB888
        img = QtGui.QImage(show_frame, show_frame.shape[1], show_frame.shape[0], QtGui.QImage.Format_Indexed8)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)
        # ------------------------------------------------------ #
