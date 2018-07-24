#######################
#   Toolbar Class     #
#######################

__DEBUG__ = True

import time, pylab, os, cPickle, sys
import tkMessageBox
import tkSimpleDialog
import app_toolbar
import spectro 
import litho
import iprog
import camera
import scanner
import xlia

PDF_VIEWER = 'evince'

help_path = os.path.join(os.curdir, 'docs')
files = os.listdir(help_path)
files.sort()
help_files = []
for file in files:
	if os.path.splitext(file)[-1] == '.pdf':
	    help_files.append(file)

HELP_FILE = help_files[-1]

CAM_VIEWER = 'cheese'
INSIM = 'IN SIM CAMERA'
OUTSIM = 'THIRD PARTY'

logpath      	 = os.path.join(os.curdir, 'log')
globlogfile  	 = os.path.join(logpath, 'glob.dat')

def dicReadGlobalParam():
    f = open(globlogfile)
    dicGlobalParam = cPickle.load(f)
    f.close()
    return dicGlobalParam 


if __DEBUG__ == True:
	from Tkinter import *

def toolbar(f=None):
	"""
	Creates toolbar object
	"""
	if not f:
		root = Tk()
		f = Frame(root).grid()
	oAppToolbar = app_toolbar.app_toolbar()
	oAppToolbar.createTBwindow(f)
	oToolbar = Toolbar(oAppToolbar)
	if not f :
		root.title('Toolbar')
		root.mainloop()
	return oToolbar

class Toolbar:

	def __init__(self, oAppToolbar):
		"""
		Class Contructor : Toolbar
		"""
		self.oAppToolbar = oAppToolbar
		self._configureCB()
		return 

	def _configureCB(self):
		"""
		Attaches Callbacks to ToolbarGui widgets 
		"""
		self.oAppToolbar.BtnInitStm.config(command=self.BtnInitStmCB) 
		self.oAppToolbar.BtnOpenFile.config(command=self.BtnOpenFileCB) 
		self.oAppToolbar.BtnSaveFile.config(command=self.BtnSaveFileCB) 
		self.oAppToolbar.BtnImageFiltering.config(command=self.BtnImageFilteringCB)
		self.oAppToolbar.BtnAreaSettings.config(command=self.BtnAreaSettingsCB)
		self.oAppToolbar.BtnFB_Settings.config(command=self.BtnFB_SettingsCB)
		self.oAppToolbar.BtnLIASettings.config(command=self.vLaunchXLIACB)
		self.oAppToolbar.BtnSpectro.config(command=self.BtnSpectroCB)
		self.oAppToolbar.BtnLitho.config(command=self.BtnLithoCB)
		#self.oAppToolbar.BtnSoftCRO.config(command=self.BtnSoftCROCB)
                self.oAppToolbar.BtnCam.config(command=self.BtnCamCB)
		self.oAppToolbar.BtnHelp.config(command=self.BtnHelpCB)
		self.oAppToolbar.BtnExit.config(command=self.BtnExitCB)
		self.oAppToolbar.BtnMovieSettings.config(command=self.BtnMovieSettingsCB)

		self.Litho_Instance = 0
		self.IVSpectro_Instance = 0
		self.iprog_Instance = 0
		#self.SoftCRO_Instance = 0
		self.Cam_Instance = 0
		self.movieInstance = 0
		self.XLIA_Instance = 0
		self.FB_Instance = 0
		xlia.setXLIA_Off()

		self.winMovie = None
		self.winCam = None
		self.winLitho = None
		self.winIprog = None
		#self.winCRO = None
		self.winCam = None
		self.winFB = None
		self.strCamVar = StringVar() 
		self.strCamVar.set(camera.CAM_VIEWER[0])
		self.winIV = None
		self.oXLIA = None
		return

	def vGetMain(self, MainMaster):
		"""
		Links Main Window to Toolbar class
		"""
		self.MainMaster = MainMaster
		self.__vConfigureKBShortCuts()
		return

	def vGetMainFrame(self, masterFrame):
		"""
		Links Main Window to Toolbar class
		"""
		self.masterFrame = masterFrame
		return

	def vGetScanner(self, oScanner):
		"""
		Links Scanner object to Toolbar class			
		"""
		self.oScanner = oScanner
		return

	def vGetWalker(self, oWalker):
		"""
		Links Walker object to Toolbar class
		"""
		self.oWalker = oWalker
		return

	def vGetImaging(self,oImaging):	
		"""
		Links Imaging object to Toolbar class			
		"""
		self.oImaging=oImaging		
		return			

	def vGetOffset(self, oOffset):
		"""
		Links Offset object to Toolbar class
		"""
		self.oOffset = oOffset
		return

	def vGetStm(self, oStm):
		"""
		Links Stm object to Toolbar class
		"""
		self.oStm = oStm
		return

	def BtnInitStmCB(self, event=None):
		"""
		Initializes following parameters - X, Y, Z offset, Bias
		"""
		self.oOffset.vInitialSTMSetup(self.MainMaster)
		return

	def BtnOpenFileCB(self, event=None):
		"""
		Opens up a Image File
		"""
		self.oScanner.vOpenImages()		
		return

	def BtnSaveFileCB(self, event=None):
		"""
		Saves an image file
		"""
		self.oScanner.vSaveImages()		
		return

	def BtnImageFilteringCB(self, event=None):
		"""
		Launches I-Prog
		"""
		if self.iprog_Instance > 0:
		    self.vHighlightWindow(self.winIprog)
		    return
		self.iprog_Instance += 1 
		if self.iprog_Instance == 1:
			self.winIprog = Toplevel(takefocus=True)
			self.winIprog.resizable(False, False)
			ip = iprog.iprog(self.winIprog, self, self.oImaging.RGB)
		return

	def BtnSpectroCB(self, event=None):
		"""
		Kick starts IV Spectroscopy application
		"""
		if self.IVSpectro_Instance > 0:
		    self.vHighlightWindow(self.winIV)
		    return
		self.IVSpectro_Instance += 1 
		if self.IVSpectro_Instance == 1:
			self.winIV = Toplevel(takefocus=True)
			self.winIV.resizable(False, False)
			self.winIV.title("IV Spectroscopy")
			self.winIV.protocol('WM_DELETE_WINDOW', self.vCloseIVSpectro)
			self.oIVS = spectro.spectro(self.winIV, self.oStm, self.oScanner)
			#self.oIVS.vGetScanner(self.oScanner)
		return

	def vCloseIVSpectro(self):
		self.IVSpectro_Instance = 0
		self.oIVS.vCloseAppSpectroCB()
		self.winIV = None
		return

	def BtnLithoCB(self, event=None):
		"""
		Launches Lithography utility
		"""
		if self.Litho_Instance > 0:
		    self.vHighlightWindow(self.winLitho)
		    return 
		self.Litho_Instance += 1 
		if self.Litho_Instance == 1: 
			self.winLitho = Toplevel(takefocus=True)
			self.winLitho.resizable(False, False)
			self.winLitho.title("Lithography")
			self.Litho = litho.litho(self.winLitho, self.oStm, self)
		return

	def BtnCamCB(self):
	    oCamera = camera.Camera()
	    camList = oCamera.detectCamera()

	    noOfCameras = len(camList)
	    print 'No Of Cameras Detected', noOfCameras 
		

	    if noOfCameras == 0:
		tkMessageBox.showerror('Camera Error', 'No cameras detected', parent = self.MainMaster)
		return

	    if noOfCameras == 1:
		camId = 0

	    if noOfCameras > 1:
		camId = tkSimpleDialog.askinteger('Select which Camera to open', \
			'Enter Camera ID: \n Range (0 < ID < ' + str(noOfCameras - 1), \
			initialvalue = 0, \
			minvalue = 0, \
			maxvalue = noOfCameras, \
			parent = self.MainMaster)
	    if camId == None:
			camId = 0

	    cmd = oCamera.displayCameraOutput(camId)
            return


        def vCloseCam(self):
            self.Cam_Instance = 0
            self.oCam.vCloseCamWindowCB()
	    self.winCam = None
            return
        
	def vHighlightWindow(self, winObj):
	    winObj.deiconify()
	    winObj.lift()
	    return

	def BtnHelpCB(self, event=None):
		"""
		Displays UserManual
		"""
		cmd = PDF_VIEWER + ' ' + os.path.join(help_path, HELP_FILE) + " &"
		os.popen(cmd)
		return

	def BtnMovieSettingsCB(self, event=None):
		"""
		Launches Movie Scan 
		"""
		if self.movieInstance > 0:
		    self.vHighlightWindow (self.winMovie)
		    return
		self.movieInstance += 1 
		if self.movieInstance == 1:
			self.winMovie = Toplevel (takefocus = True)
			self.winMovie.resizable (False, False)
			self.winMovie.title ("Movie Settings")
			self.winMovie.protocol('WM_DELETE_WINDOW', self.vCloseMovieSettings)
			self.oMovie = scanner.MovieSettingsDialog (self.winMovie, self.oScanner)
		return

	def vCloseMovieSettings (self):
		self.movieInstance = 0
		self.oMovie.closeAppMovie ()
		self.winMovie = None
		return

	def BtnAreaSettingsCB(self, event=None):
		"""
		Launches Scan Area Control
		"""
		self.oScanner.vSetScanArea()
		return

	def BtnFB_SettingsCB(self, event=None):		
		"""
		Lauches FeedBack and Reset Control	
		"""
		self.FB_Instance += 1
	        if self.FB_Instance > 1:
		    self.vHighlightWindow(self.winFB)
	            return 
		if self.FB_Instance == 1:
			self.winFB = Toplevel(takefocus=True)
			self.winFB.resizable(False, False)
	        	self.winFB.title('Feedback Control')
			self.winFB.protocol('WM_DELETE_WINDOW', self.closeWinFB)
			self.oFB = scanner.FeedbackControlDialog(self.winFB, self.oStm)
		return


	def closeWinFB(self):
		self.FB_Instance = 0
		self.oFB.closeAppFB() 
		self.winFB = None
		return


	def vLaunchXLIACB (self, event=None):
		"""
		Launches LIA Control Window
		"""
		self.XLIA_Instance += 1
	        if self.XLIA_Instance > 1:
		    self.hightlightXLIA_Window()
	            return 
		if self.XLIA_Instance == 1:
			self.winXLIA = Toplevel (takefocus=True)
			self.winXLIA.resizable (False, False)
		        self.winXLIA.title ('nanoREV Lock-In Amplifier')
        	        self.winXLIA.protocol('WM_DELETE_WINDOW', self.vCloseXLIACB)
			self.oXLIA = xlia.xlia (self.winXLIA)
		return


	def hightlightXLIA_Window(self):
		self.vHighlightWindow (self.winXLIA)
		return


	def vCloseXLIACB (self):
		#self.oXLIA.stopAutoUpdater()
		if tkMessageBox.askyesno('Close Lockin AMplifier', 'Do you want to close LIA?', \
			parent = self.winXLIA, \
			) == False:
		    return
		self.vCloseXLIA()
		return


	def vCloseXLIA (self):
		self.oXLIA.vCloseXLIA()
		self.XLIA_Instance = 0
		self.winXLIA.destroy()
		self.winXLIA = None
		del self.oXLIA	
		self.oXLIA = None
		return


	def BtnExitCB(self, event=None):
		"""
		Quits SiM
		"""
		if tkMessageBox.askyesno('Close', '\'Yes\' .. means point of no return !!'):
			self.vCloseAllApps()
			self.MainMaster.destroy()

	def vCloseAllApps(self):
	    if self.winIV != None:
		self.vCloseIVSpectro()
	    if self.winCam != None:
		self.vCloseCam()
	    if self.winMovie != None:
		self.vCloseMovieSettings ()
	    if self.winLitho != None:
		pass
	    if self.winIprog != None:
		pass
	    if self.winCam != None:
		pass
	    pylab.close('all')
	    return

	def vDisableTbGroup(self):
		"""
		Freezes ToolbarGui widgets
                    --> This is essential for suppressing features 
			espicially when scanning is taking place 
		"""
		self.oAppToolbar.BtnInitStm.config(state=DISABLED)
		self.oAppToolbar.BtnOpenFile.config(state=DISABLED)
		self.oAppToolbar.BtnSaveFile.config(state=DISABLED)
		self.oAppToolbar.BtnMovieSettings.config(state=DISABLED)
		self.oAppToolbar.BtnImageFiltering.config(state=DISABLED)
		self.oAppToolbar.BtnAreaSettings.config(state=DISABLED)
		#self.oAppToolbar.BtnPISettings.config(state=DISABLED)
		self.oAppToolbar.BtnLIASettings.config(state=DISABLED)
		self.oAppToolbar.BtnLitho.config(state=DISABLED)
		self.oAppToolbar.BtnSpectro.config(state=DISABLED)
		self.oAppToolbar.BtnHelp.config(state=DISABLED)
		self.oAppToolbar.BtnExit.config(state=DISABLED)
		#self.oAppToolbar.BtnCam.config(state=DISABLED)
		return

	def vEnableTbGroup(self):
		"""
		Enables Toolbar widgets	
		"""
		self.oAppToolbar.BtnInitStm.config(state=NORMAL)
		self.oAppToolbar.BtnOpenFile.config(state=NORMAL)
		self.oAppToolbar.BtnSaveFile.config(state=NORMAL)
		self.oAppToolbar.BtnMovieSettings.config(state=NORMAL)
		self.oAppToolbar.BtnImageFiltering.config(state=NORMAL)
		self.oAppToolbar.BtnAreaSettings.config(state=NORMAL)
		#self.oAppToolbar.BtnPISettings.config(state=NORMAL)
		self.oAppToolbar.BtnLIASettings.config(state=NORMAL)
		self.oAppToolbar.BtnLitho.config(state=NORMAL)
		self.oAppToolbar.BtnSpectro.config(state=NORMAL)
		self.oAppToolbar.BtnHelp.config(state=NORMAL)
		self.oAppToolbar.BtnExit.config(state=NORMAL)
		#self.oAppToolbar.BtnCam.config(state=NORMAL)
		return

	def __vConfigureKBShortCuts(self):
		"""
		Keyboard bindings for different functions
		"""
		self.MainMaster.bind('<Control-o>', self.BtnOpenFileCB)
		self.MainMaster.bind('<Control-s>', self.BtnSaveFileCB)
		self.MainMaster.bind('<Control-a>', self.BtnAreaSettingsCB)
		self.MainMaster.bind('<Control-i>', self.BtnInitStmCB)
		#self.MainMaster.bind('<Control-c>', self.BtnSoftCROCB)
		self.MainMaster.bind('<Control-m>', self.BtnMovieSettingsCB)
		self.MainMaster.bind('<Control-f>', self.BtnImageFilteringCB)
		self.MainMaster.bind('<Control-l>', self.BtnLithoCB)
		self.MainMaster.bind('<Control-v>', self.BtnSpectroCB)
		self.MainMaster.bind('<Control-q>', self.BtnExitCB)
		self.MainMaster.bind('<F1>', self.BtnHelpCB)
		return

######### Only for Testing ###########
if __name__ == "__main__":
	toolbar()
