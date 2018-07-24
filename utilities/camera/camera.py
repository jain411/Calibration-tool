from Tkinter import *
from PIL import Image, ImageTk
import time
import tkMessageBox
import tkSimpleDialog 
import os
import cPickle
#import cv #as opencv
#from opencv import highgui

import app_camera

CAM_RES = (640, 480)

CAM_VIEWER = ['guvcview', 'cheese']

logpath      	 = os.path.join(os.curdir, 'log')
globlogfile  	 = os.path.join(logpath, 'glob.dat')

def dicReadGlobalParam():
    f = open(globlogfile)
    dicGlobalParam = cPickle.load(f)
    f.close()
    return dicGlobalParam 

class Camera:

	cameraApp = CAM_VIEWER[0]

	def __init__(self):
		dicGlobParam = dicReadGlobalParam()
		if dicGlobParam['CamMode'] not in CAM_VIEWER:
			print 'Camera Application not found...'
			print 'Using default Camera Application...'
			self.cameraApp = CAM_VIEWER[0]
		else:
			self.cameraApp = dicGlobParam['CamMode']
		return

	def detectCamera (self):
		self.cameraList = []
		if os.name == 'posix':
			DEV_PATH = '/dev'
			DEV_ID = 'video'
			device_list = os.listdir(DEV_PATH)
			for device in device_list:
				if device[:5] == DEV_ID:
					self.cameraList.append(os.path.join(DEV_PATH, device))
		return self.cameraList

	def displayCameraOutput(self, camId):
		if self.cameraApp == CAM_VIEWER[0]:
			camDev = self.cameraList [camId]
			cmd = self.cameraApp + ' -d ' + camDev + ' &'
	    	os.popen(cmd)
		return

'''
def bDetectCamera():
    #strGetCamDevice()
    CamDev = cv.CaptureFromCAM(0)	# TODO: dev string instead of 0
    if CamDev == None:
	return False
    else:
	#cv.ReleaseCapture(CamDev)
	return True
'''


def camera(master):
    oAppCam = app_camera.app_camera()
    oAppCam.vCreateCamWindow(master)
    oCV  = CamView(oAppCam)
    return oCV

class CamView:
    def __init__(self, oAppCam):
	if self.bOpenCamera() == False:
	    tkMessageBox.showerror('Camera Error', 'Camera could not be opened')
	    return
        self.MovieStatus = BooleanVar()
        self.MovieStatus.set(False)
	self.oAppCam = oAppCam
	self._initCanvasImage()
        self.vShowCamImage()
        return

    def bOpenCamera(self):
	#self.strGetCamDevice()
        self.CamDev = cv.CreateCameraCapture(0)	# TODO: dev string instead of 0
	if self.CamDev == None:
	    return False
	else:
	    return True

    def _initCanvasImage(self):
        self.CanImage = Image.new('RGB', CAM_RES)
        self.CanSnap = ImageTk.PhotoImage(self.CanImage)
	self.oAppCam.CanvasCam.configure(height=CAM_RES[1], width=CAM_RES[0])
        self.iCanSnapshot = self.oAppCam.CanvasCam.create_image(0,0, image=self.CanSnap, anchor=NW)
        #self.oAppCam.camGroup.protocol('WM_DELETE_WINDOW', self.vCloseCamWindowCB)
        self.oAppCam.camGroup.title('nanoREV Camera View')
        return

    def vShowCamImage(self):
        im = highgui.cvQueryFrame(self.CamDev)
	# Add the line below if you need it (Ubuntu 8.04+)
	im = opencv.cvGetMat(im)
	#convert Ipl image to PIL image
        imCanSnap = opencv.adaptors.Ipl2PIL(im)
	#imCanSnap = ImageTk.PhotoImage(img)
        self.CanSnap.paste(imCanSnap)
        self.oAppCam.camGroup.update()
        return

    def vShowMovie(self, delay=0.1):
        self.MovieStatus.set(True)
        while (self.MovieStatus.get() != False):
            self.vShowCamImage()
            #self.oAppCam.camGroup.update()
            time.sleep(delay)
	self.MovieStatus.set(False)
        self.oAppCam.camGroup.destroy()
        return

    def vCloseCamWindowCB(self):
        #self.MovieStatus.set(False)
	highgui.cvReleaseCapture(self.CamDev)
	print 'Cam Dectivated'
        self.oAppCam.camGroup.destroy()
        return

if __name__ == '__main__':
    root = Tk()
    oCV = camera(root)
    #oCV.vShowCamImage()
    oCV.vShowMovie()
    root.mainloop()
