from Tkinter import *

RES = (640, 480)

def app_camera():
	"""
	Returns CameraGui object
	"""
	oCamGui = CamGui()
	return oCamGui

class CamGui:

    def __init__(self):
	"""
	Class Contructor
	"""
	print 'Camera Window Opened'
	return

    def vCreateCamWindow(self, master):
	"""
	Create Camera GUI
	"""
	self.camGroup = master
        self._createCVwidgets()
	return

    def _createCVwidgets(self):
        self.CanvasCam = Canvas(self.camGroup, \
            width=RES[0], height=RES[1], \
            relief=RIDGE, \
            bg = "light yellow")
        self.CanvasCam.grid(row=0, column=0, sticky=N+E+W+S)
        return

