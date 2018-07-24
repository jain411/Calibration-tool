#####################
#   Menubar Class   #
#####################
import os
import tkSimpleDialog
import tkMessageBox
import app_menubar
import scanner
import offset 
import stm7 as stm
import walker 		
import Import 	
import export	
import calibration	
import zcalib
import _print		
import threedimaging
import lext
import hvlext
import about
import dialogs
import mlength
import mangle
import izspectro
import qv
import kbsc

VID_PLAYER = 'vlc'
VIDEO_PATH = os.path.join (os.curdir, 'videos')

from Tkinter import * 

def menubar(root=None, oToolbar=None):	
	"""
	Function : menubar
	"""
	
	f = True 
	if not root :
		root = Tk()
		f = None
	oAppMenubar = app_menubar.app_menubar()
	oAppMenubar.createMenubar(root)
	oMenubar = Menubar(oAppMenubar, oToolbar)
	if not f :
		root.title('Menubar')
		root.mainloop()
	return oMenubar

class Menubar:

    def __init__(self, oAppMenubar, oToolbar):
	"""
	Class Contructor : Menubar
	"""
	self.oToolbar = oToolbar
	self.oAppMenubar = oAppMenubar
	self.bApplyVar = BooleanVar()
	self.bApplyVar.set(False)
	# Scanner Settings #
	self.acCoupledScanningVar = BooleanVar()
	self.acCoupledScanningVar.set(True)
	self.preScanSetupDelayVar = IntVar()
	SCAN_SETUP_DELAY = 5
	self.preScanSetupDelayVar.set(SCAN_SETUP_DELAY)
	##
	self._configureCB()
	return

    def _configureCB(self):
	"""
	Attaches Callbacks to MenubarGui widgets 
	"""
	self.oAppMenubar.filemenu.add_command(label='Init STM <Ctrl+i>', \
			underline=0, \
			command=self.oToolbar.oAppToolbar.BtnInitStm.invoke)
	self.oAppMenubar.filemenu.add_command(label='Open <Ctrl+o>', \
			underline=0, \
			command=self.oToolbar.oAppToolbar.BtnOpenFile.invoke)
	self.oAppMenubar.filemenu.add_command(label='Save <Ctrl+s>', \
			underline=0, \
			command=self.oToolbar.oAppToolbar.BtnSaveFile.invoke)
	self.oAppMenubar.filemenu.add_command(label='Import', \
			underline=1, \
			command=self.vLaunchImportCB)
	self.oAppMenubar.filemenu.add_command(label='Export', \
			underline=0, \
			command=self.vLaunchExportCB)
	self.oAppMenubar.filemenu.add_command(label='Print', \
			underline=1, \
			command=self.vPrintCB)
	self.oAppMenubar.filemenu.add_command(label='Quit', \
			underline=0, \
			command=self.oToolbar.oAppToolbar.BtnExit.invoke)

	self.oAppMenubar.settingsmenu.add_command(label='Global Settings',\
			underline=0, \
			command=self.vGlobSettingsCB)
	self.oAppMenubar.scansettingsmenu.add_command(label='Area Settings <Ctrl+a>', \
			underline=0, \
			command=self.oToolbar.oAppToolbar.BtnAreaSettings.invoke)
	self.oAppMenubar.scansettingsmenu.add_command(label='Pre-Scan Setup Delay', \
			underline=1, \
			command=self.preScanSetupDelayCB)
	self.oAppMenubar.scansettingsmenu.add_checkbutton(label='AC-Coupled Scanning', \
			underline = 2, \
			onvalue = True, \
			offvalue = False, \
			variable = self.acCoupledScanningVar)
	#self.oAppMenubar.scansettingsmenu.add_command(label='Tip Parking Settings', \
	#		underline=1, \
	#		command=self.tipParkingSettingsCB)
	#self.oAppMenubar.scansettingsmenu.add_command(label='Auto-Save Settings', \
	#		underline=1, \
	#		command=self.vAutoSaveSettingsCB)
	self.oAppMenubar.scansettingsmenu.add_command(label='Feedback Control', \
			underline=0, \
			command=self.vFeedbackControlCB)
	self.oAppMenubar.settingsmenu.add_command(label='Bias Settings', \
			underline=0, \
			command=self.vBiasSettingsCB)
	self.oAppMenubar.settingsmenu.add_command(label='T.C. Setpoint', \
			underline=0, \
			command=self.vTCSetpointSettingsCB)
	self.oAppMenubar.settingsmenu.add_command(label='GUI Settings', \
			underline=1, \
			command=self.vGuiSettingsCB)
        self.oAppMenubar.settingsmenu.add_command( \
			label='Port Settings', \
			underline=0, \
			command=self.vPortSettingsCB)
	self.oAppMenubar.offsetsettingsmenu.add_command(label='Tip Motion Speed (V/s)', \
			underline=0, \
			command=self.vSetTipMotionSpeedCB)
	self.oAppMenubar.walkersettingsmenu.add_command(label='Calculated Run', \
			underline=0, \
			command=self.vCalculatedRunCB)
	self.oAppMenubar.walkersettingsmenu.add_command(label='Run Settings', \
			underline=0, \
			command=self.vRunDelayCB)
	self.oAppMenubar.walkersettingsmenu.add_command(label='AutoWalk Settings', \
			underline=0, \
			command=self.vAutoWalkDelayCB)

	self.oAppMenubar.imagesettingsmenu.add_command(label='Load LookUp Table', \
			underline=5, \
			command=self.vLUTCB)
	'''
	self.oAppMenubar.imagesettingsmenu.add_command(label='Color Modes', \
			underline=0, \
			command=self.vDisplaySettings)
	'''
	self.oAppMenubar.displayareamenu.add_command(label='Line Scan', \
			underline=0, \
			command=self.vSetDisplayAlllines)
	self.oAppMenubar.displayareamenu.add_command(label='5 Percent', \
			underline=0, \
			command=self.vSet5PercentDisplaylines)
	self.oAppMenubar.displayareamenu.add_command(label='10 Percent', \
			underline=0, \
			command=self.vSet10PercentDisplaylines)
	self.oAppMenubar.displayareamenu.add_command(label='25 Percent', \
			underline=0, \
			command=self.vSet25PercentDisplaylines)
	self.oAppMenubar.displayareamenu.add_command(label='50 Percent', \
			underline=0, \
			command=self.vSet50PercentDisplaylines)
	self.oAppMenubar.displayareamenu.add_command(label='Full Image', \
			underline=0, \
			command=self.vSetFullImageDisplay)

	self.oAppMenubar.piezosettingsmenu.add_command(label='Z Polarity', \
			underline=2, \
			command=self.vPiezoSettingsCB)
	self.oAppMenubar.piezosettingsmenu.add_command(label='Load X/Y Calibration', \
			underline=5, \
			command=self.vLoadXYCalibrationCB)
	self.oAppMenubar.piezosettingsmenu.add_command(label='Load Z Calibration', \
			underline=5, \
			command=self.vLoadZCalibrationCB)

	self.oAppMenubar.spectromenu.add_command(label='I-V Spectro <Ctrl+v>', \
			underline=0, \
			command=self.oToolbar.oAppToolbar.BtnSpectro.invoke)
	self.oAppMenubar.spectromenu.add_command(label='I-Z Spectro', \
			underline=2, \
			command=self.vIZSpectroCB)
	self.oAppMenubar.threedimagingmenu.add_command(label='Scan Image',\
			underline=0, \
			command=self.vThreedScan)	
	self.oAppMenubar.threedimagingmenu.add_command(label='Ret Image',\
			underline=0, \
			command=self.vThreedRet)			
	self.oAppMenubar.threedimagingmenu.add_command(label='File',\
			underline=0, \
			command=self.vThreedFile)
	self.oAppMenubar.calibmenu.add_command(label='XY-Calibration', \
			underline=0, \
			command=self.vCalibrationCB)
	self.oAppMenubar.calibmenu.add_command(label='Z-Calibration', \
			underline=0, \
			command=self.vZCalibCB)
	self.oAppMenubar.utilitiesmenu.add_command(label='Lithography <Ctrl+l>', \
			underline=2, \
			command=self.oToolbar.oAppToolbar.BtnLitho.invoke)
	self.oAppMenubar.utilitiesmenu.add_command(label='Image Processing <Ctrl+f>', \
			underline=0, \
			command=self.oToolbar.oAppToolbar.BtnImageFiltering.invoke)
	
	self.oAppMenubar.utilitiesmenu.add_command(label='Measure Length', \
			underline=0, \
			command=self.vMLengthCB)
	self.oAppMenubar.utilitiesmenu.add_command(label='Measure Angle', \
			underline=8, \
			command=self.vMAngleCB)
	self.oAppMenubar.utilitiesmenu.add_command(label='QuickView Album', \
			underline=0, \
			command=self.vLaunchQuickViewCB)

	self.oAppMenubar.linextmenu.add_command(label='Horizontal',\
			underline=0, \
			command = self.vHorzLineExtractionCB)
	self.oAppMenubar.linextmenu.add_command(label='Vertical',\
			underline=0, \
			command = self.vVertLineExtractionCB)
	self.oAppMenubar.linextmenu.add_command(label='Between Any Two Points',\
			underline=0, \
			command = self.vLineExtractionCB)

	self.oAppMenubar.helpmenu.add_command(label='About',\
			underline=0, \
			command=self.vAboutSiMCB)
	self.oAppMenubar.helpmenu.add_command(label='Keyboard Shortcuts',\
			underline=0, \
			command=self.vKBSCCB)	
	self.oAppMenubar.helpmenu.add_command(label='nanoREV User Manual<F1>',\
			underline=0, \
			command=self.vSiMhelpCB)	
	self.oAppMenubar.helpmenu.add_command(label='HowTO Videos',\
			underline=0, \
			command=self.vHowTOVideosCB)	

	self.Import_Instance = 0 
	self.Export_Instance = 0
	self.Calib_Instance = 0  
	self.LExt_Instance   = 0
	self.Print_Instance  = 0		
	self.IZSpectro_Instance = 0
	self.QV_Instance = 0 
	self.ZC_Instance = 0
	self.About_Instance = 0  
	self.KBSC_Instance = 0
	self.FB_Instance = 0
	return

    def vThreedScan(self):
	"""
	Launches 3D imaging tool to Display Scan Image present on the Scan Window 	
	"""
	oThreed=threedimaging.ThreeD(self.oImaging)
	oThreed.vOpenImage(threedimaging.SCAN)
	return	
	
    def vThreedRet(self):
	"""
	Launches 3D imaging tool to Display Retrace Image present on the Retrace Window 	
	"""
	oThreed=threedimaging.ThreeD(self.oImaging)
	oThreed.vOpenImage(threedimaging.RET)
	return		

    def vThreedFile(self):
	"""
	Launches 3D imaging tool to Display a user select image
	"""
	oThreed=threedimaging.ThreeD(self.oImaging)
	oThreed.vOpenImage(threedimaging.FILE)
	return	
	
    def vPrintCB(self):
	"""
	Launches Printing utility	
	"""
	print 'TODO'	#TODO
	return
	self.Print_Instance=self.nPrint_Instance(self.Print_Instance)
	if self.Print_Instance==1:
		submain=Toplevel()
		submain.title('Print')
		op = _print._print(submain,self,self.oImaging.RGB)			
	return
	
	
    def nPrint_Instance(self,Instance=0):
	"""
	nPrint_Instance
	"""
	Instance +=1	
	return Instance
   
    def vGetImaging(self, oImaging):
	"""
	Links Imaging object to Menubar class
	"""
	self.oImaging=oImaging
	return
	
    def vGetMain(self, oMainMaster):
	print 'Unpacking main'
	self.oMainMaster = oMainMaster
	return

    def vGetWalker(self, oWalker):
	"""
	Links Walker object to Menubar class
	"""
	self.oWalker = oWalker
	self.oOffset = self.oToolbar.oScanner.oOffset
	return

    def vLaunchExportCB(self):
	"""
	Launches Export Utility
	"""
	if not self.oImaging.bImagePresentVar.get():
	    tkMessageBox.showwarning('Blank','Oops !! No images on Display')
	    return
	oe = export.export(self.oMainMaster.master)
	return

    def vLaunchImportCB(self):
	"""
	Launches Import Utility
	"""
	ip=Import.Import_(self.oToolbar)	
	return	

    def vLineExtractionCB(self, event=None):
	"""
	Launches Line Extraction 
	"""
	oLExt = lext.lext(self.oImaging)
	return

    def vHorzLineExtractionCB(self, event=None):
	"""
	Launches Horizontal Line Extraction 
	"""
	oHVLExt = hvlext.hvlext(self.oImaging, 'H')
	return

    def vVertLineExtractionCB(self, event=None):
	"""
	Launches Vertical Line Extraction 
	"""
	oHVLExt = hvlext.hvlext(self.oImaging, 'V')
	return

    def vLUTCB(self, event=None):
	"""
	Loads a new Look Up Table 
	"""
	self.oImaging.vLoadNewlutFile()
	return	
	
    def vLoadXYCalibrationCB(self):
	"""
	Sets X/Y Piezo Caliberation nm/V
	"""
	PIEZO_XY = scanner.fGetPiezoXCalibration()
	piezo_xy = tkSimpleDialog.askfloat('Load X/Y-Calibration', \
			'Enter X/Y Piezo Calibration \nvalues (in nm/V):', \
			initialvalue=PIEZO_XY)
	if piezo_xy == None:
	    return
	else:
	    scanner.vSavePiezoXCalibration(piezo_xy)
	return

    def vLoadZCalibrationCB(self):
	"""
	Sets X/Y Piezo Caliberation nm/V
	"""
	PIEZO_Z = scanner.fGetPiezoZCalibration()
	piezo_z = tkSimpleDialog.askfloat('Load Z-Calibration', \
			'Enter Z Piezo Calibration \nvalues (in nm/V):', \
			initialvalue=PIEZO_Z)
	if piezo_z == None:
	    return
	else:
	    scanner.vSavePiezoZCalibration(piezo_z)
	return

    def vSetTipMotionSpeedCB(self):
	"""
        Sets Tip Speed
                --> 0.5-5 V/sec
	"""
	velocity = tkSimpleDialog.askfloat('Set Tip Velocity', \
			'Enter Velocity(in V/s): \n Range (0.5<TV<5)', \
			initialvalue=stm.TIP_VELOCITY, \
			minvalue=0.5, \
			maxvalue=5.0)
	if velocity == None:
	    return
	else:
	    stm.TIP_VELOCITY = velocity
	return

    def vBiasSettingsCB(self):
	initBias = stm.getCurrentSampleBias()
	biasVoltage = tkSimpleDialog.askfloat('Bias Settings', \
			'Set Sample Bias(in V):', \
			initialvalue = initBias, \
			minvalue = stm.MIN_BIAS, \
			maxvalue = stm.MAX_BIAS)
	if biasVoltage == None:
	    return
	self.oWalker.vDisableWsGroup()
	self.oOffset.vDisableOsGroup()
	self.oToolbar.vDisableTbGroup()
	self.vDisableMbGroup()
	self.oToolbar.oScanner.vDisableSsGroup()
	self.oMainMaster.master.update()

	self.oToolbar.oStm.set_bias_slow(biasVoltage)	# in V

	self.oToolbar.oScanner.vEnableSsGroup()
	self.vEnableMbGroup()
	self.oWalker.vEnableWsGroup()
	self.oOffset.vEnableOsGroup()
	self.oToolbar.vEnableTbGroup()
	return

    def vTCSetpointSettingsCB(self):
	nInitTCSetpoint = stm.readCurrentSetpoint()	# in pA
	nTCSetpoint = tkSimpleDialog.askinteger('T.C. Setpoint Settings', \
			'Set Tunnel Current Setpoint(in pA):', \
			initialvalue = int(nInitTCSetpoint), \
			minvalue = stm.MIN_TC, \
			maxvalue = stm.MAX_TC)
	if nTCSetpoint == None:
	    return

	self.oWalker.vDisableWsGroup()
	self.oOffset.vDisableOsGroup()
	self.oToolbar.vDisableTbGroup()
	self.vDisableMbGroup()
	self.oToolbar.oScanner.vDisableSsGroup()
	self.oMainMaster.master.update()

	self.oToolbar.oStm.set_tc(nTCSetpoint)	# in pA
	stm.saveSetpointTC(nTCSetpoint)

	self.oToolbar.oScanner.vEnableSsGroup()
	self.vEnableMbGroup()
	self.oWalker.vEnableWsGroup()
	self.oOffset.vEnableOsGroup()
	self.oToolbar.vEnableTbGroup()

	return

    def vCalculatedRunCB(self):
	"""
	Runs the Walker by entered no. of Steps
            --> 10-1000 steps
	"""
	nNoOfSteps = tkSimpleDialog.askinteger('Calculated Run', \
			'Enter no. of Steps to Run:', \
			initialvalue=10, \
			minvalue=1, \
			maxvalue=10000)
	if nNoOfSteps == None:
	    return
	else:
	    self.oWalker.vCalculatedRunHandler(nNoOfSteps)
	return


    def vRunDelayCB(self):

	"""
        Sets Walker Run Delay
                --> 50-200 ms
	"""
	nRunDelay = tkSimpleDialog.askinteger('Run Delay', \
			'Enter Run Delay(in ms): \n Range (50<RD<200)', \
			initialvalue=int(walker.fGetRunDelay()*1000), \
			minvalue=15, \
			maxvalue=200)
	if nRunDelay == None:
	    return
	else:
            walker.vSaveRunDelay(nRunDelay)
            #print "New Run_Delay", nRunDelay
	return

    def vAutoWalkDelayCB(self):
	"""
        Sets AutoWalk Step Delay
                --> 100-5000 ms
	"""
	nAutoWalkDelay = tkSimpleDialog.askinteger('AutoWalk Delay', \
			'Enter AutoWalk Delay(in ms): \n Range (100<RD<4000)', \
			initialvalue=int(walker.fGetRunDelay()*1000), \
			minvalue=100, \
			maxvalue=4000)
	if nAutoWalkDelay == None:
	    return
	else:
	    walker.vSaveAutoWalkDelay(nAutoWalkDelay)
            #print "New Auto-Walk Delay", nAutoWalkDelay
	return	

    def vFeedbackControlCB(self):
	"""
	Lauches FeedBack and Reset Control	
	"""
	self.oToolbar.BtnFB_SettingsCB()
	return


    def tipParkingSettingsCB(self):
	self.oToolbar.oScanner.selectTipParkingModeCB()
	return


    def preScanSetupDelayCB(self):
       	delay = self.preScanSetupDelayVar.get()	# in ms
       	MIN_DELAY = 5
       	MAX_DELAY = 100
	newDelay = tkSimpleDialog.askinteger('Pre-Scan Delay Settings', \
			'Set Pre-Scan Delay (in ms):', \
			initialvalue = int(delay), \
			minvalue = MIN_DELAY, \
			maxvalue = MAX_DELAY)
	if newDelay == None:
	    return
	self.preScanSetupDelayVar.set(newDelay)
	return


    def vAutoSaveSettingsCB(self):
	"""
	Specifies target location for saving the images
	and other auto save options. 	
	"""
	#oAS = dialogs.AutoSaveSettingsDialog(self.oMainMaster.master)
	pass
	return


    def	vCalibrationCB(self):
	"""
	Launches Calibration Utility
	"""
	self.Calib_Instance +=1 
        if self.Calib_Instance > 1:
	    self.vHighlightWindow(self.winCalib)
            return 
	if self.Calib_Instance == 1:
		self.winCalib = Toplevel(takefocus=True)
		self.winCalib.resizable(False, False)
		self.winCalib.title('Calibration')
		cal = calibration.calibration(self.winCalib, self, self.oImaging.RGB)
	return

    def	vZCalibCB(self):
	self.ZC_Instance += 1
        if self.ZC_Instance > 1:
	    self.vHighlightWindow(self.winZCalib)
            return 
	if self.ZC_Instance == 1:
		self.winZCalib = Toplevel(takefocus=True)
		self.winZCalib.resizable(False, False)
		self.winZCalib.title('Calibration')
		oZC = zcalib.zcalib(self.winZCalib, self, self.oImaging.RGB)
	return


    def vDisplaySettings(self):
	"""
        Sets Image Display choice 
                --> RGB
                --> gray
	"""
	self.oToolbar.oImaging.vSetDisplayChoice()
	return	

    def vDisableMbGroup(self):
	"""
	Disables Menubar Window
	"""
	self.vDisableFileMenu()
	return		
	
    def vDisableFileMenu(self):
	"""
	Disable Menubar widgets
	"""
	self.oAppMenubar.mainmenu.entryconfig(0,state=DISABLED)	
	self.oAppMenubar.mainmenu.entryconfig(1,state=DISABLED)	
	self.oAppMenubar.mainmenu.entryconfig(2,state=DISABLED)	
	self.oAppMenubar.mainmenu.entryconfig(3,state=DISABLED)	
	self.oAppMenubar.mainmenu.entryconfig(4,state=DISABLED)	
	return

    def vEnableMbGroup(self):
	"""
	Enables Menubar window
	"""
	self.vEnableFileMenu()
	return	
	
    def vEnableFileMenu(self):
	"""
	Enables Menubar widgets
	"""
	self.oAppMenubar.mainmenu.entryconfig(0,state=NORMAL)	
	self.oAppMenubar.mainmenu.entryconfig(1,state=NORMAL)	
	self.oAppMenubar.mainmenu.entryconfig(2,state=NORMAL)	
	self.oAppMenubar.mainmenu.entryconfig(3,state=NORMAL)	
	self.oAppMenubar.mainmenu.entryconfig(4,state=NORMAL)	
	self.oAppMenubar.mainmenu.entryconfig(5,state=NORMAL)	
	return

    def vSetDisplayAlllines(self):
	"""
	Flash All Scan line Image Display
	"""
	self.oToolbar.oScanner.nDisplayRefreshVar.set(1)
	return

    def vSet5PercentDisplaylines(self):	
	"""
	Flash image at step of 5% scanning	
	"""
	self.oToolbar.oScanner.nDisplayRefreshVar.set(5)
	return
	
    def vSet10PercentDisplaylines(self):
	"""
	Flash image at step of 10% scanning	
	"""
	self.oToolbar.oScanner.nDisplayRefreshVar.set(10)
	return
	
    def vSet25PercentDisplaylines(self):
	"""
	Flash image at step of 25% scanning	
	"""
	self.oToolbar.oScanner.nDisplayRefreshVar.set(25)
	return	

    def vSet50PercentDisplaylines(self):
	"""
	Flash image at step of 50% scanning	
	"""
	self.oToolbar.oScanner.nDisplayRefreshVar.set(50)
	return	

    def vSetFullImageDisplay(self):
	"""
	Flash image after Full image Scan	
	"""
	self.oToolbar.oScanner.nDisplayRefreshVar.set(100)
	return	

    def vPiezoSettingsCB(self):
	"""
	Lauches Piezo Settings Dialog	
	"""
	self.oWalker.vSetPiezoChoice()	
	return

    def vGuiSettingsCB(self):
	"""
	Settings for different labels and info shown over the images.	
	"""
	oGS = dialogs.GuiSettingsDialog(self.oMainMaster.master)
	#print oGS.bApplyVar.get()
	if oGS.bApplyVar.get():
	    #saved the color settings in gui.dat file
	    dicGUISettings = dialogs.dicReadGUISettings()
	    print 'Updating Color Settings'
	    try:
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasScan.\
			itemconfig(self.oToolbar.oScanner.oImaging.TextScanSize, \
			fill=dicGUISettings['AreaInfo'][0] ,\
			activefill=dicGUISettings['AreaInfo'][1] )
	    except:
	        pass
	    try:
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasRetrace.\
			itemconfig(self.oToolbar.oScanner.oImaging.TextRetSize, \
			fill=dicGUISettings['AreaInfo'][0] ,\
			activefill=dicGUISettings['AreaInfo'][1] )
	    except:
	        pass
	
	    try:
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasColor.\
			itemconfig(self.oToolbar.oScanner.oImaging.TextScale[0], \
			fill=dicGUISettings['ZInfo'][0] ,\
			activefill=dicGUISettings['ZInfo'][1] )
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasColor.\
			itemconfig(self.oToolbar.oScanner.oImaging.TextScale[1], \
			fill=dicGUISettings['ZInfo'][0] ,\
			activefill=dicGUISettings['ZInfo'][1] )
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasColor.\
			itemconfig(self.oToolbar.oScanner.oImaging.TextScale[2], \
			fill=dicGUISettings['ZInfo'][0] ,\
			activefill=dicGUISettings['ZInfo'][1] )
	    except:
		pass
	    try:
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasColor.\
			itemconfig(self.oToolbar.oScanner.oImaging.MaxGrad, \
			fill=dicGUISettings['ZInfo'][0] ,\
			activefill=dicGUISettings['ZInfo'][1] )
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasColor.\
			itemconfig(self.oToolbar.oScanner.oImaging.MinGrad, \
			fill=dicGUISettings['ZInfo'][0] ,\
			activefill=dicGUISettings['ZInfo'][1] )
		self.oToolbar.oScanner.oImaging.oAppImaging.CanvasColor.\
			itemconfig(self.oToolbar.oScanner.oImaging.MeanGrad, \
			fill=dicGUISettings['ZInfo'][0] ,\
			activefill=dicGUISettings['ZInfo'][1] )
	    except:
		pass
	return


    def vGlobSettingsCB(self):
	"""
	Lauches Global Settings Dialog	
	"""
	self.oMainMaster.vUpdateGlobParam()
	return

    def vPortSettingsCB(self):
        """
        Adds a new port to the device search list 
        """
        self.oMainMaster.vAddNewPort()
        return
    
    def vAboutSiMCB(self):
	"""
	Lauches About SiM	
	"""
	self.About_Instance += 1
        if self.About_Instance > 1:
	    self.vHighlightWindow(self.winAbout)
            return 
	if self.About_Instance == 1:
		self.winAbout = Toplevel(takefocus=True)
		self.winAbout.resizable(False, False)
		oAbout = about.about(self.winAbout, self)
	return

    def vHighlightWindow(self, winObj):
	winObj.deiconify()
	winObj.lift()
	return

    def vKBSCCB(self):
	"""
	Displays the List of Keyboard Shortcuts
	"""
	self.KBSC_Instance += 1 
        if self.KBSC_Instance > 1:
	    self.vHighlightWindow(self.winKBSC)
            return 
	if self.KBSC_Instance == 1:
		self.winKBSC = Toplevel(takefocus=True)
		self.winKBSC.resizable(False, False)
		oKBSC = kbsc.kbsc(self.winKBSC, self)
	return

    def vSiMhelpCB(self):
	"""
	Lauches SiM help
	"""
	self.oToolbar.BtnHelpCB()	
	return	

    def vHowTOVideosCB(self):
	cmd = VID_PLAYER + ' ' + os.path.join(VIDEO_PATH) + ' 1> /dev/null 2> /dev/null &'
	try:
	    os.system(cmd)
	except:
	    print 'Player or video path not found'
	return

    def vMLengthCB(self):
	"""
	Lauches Length Measurement utility
	"""
	oMlength = mlength.mlength(self.oImaging, self.oToolbar.oScanner)
	return
	
    def vMAngleCB(self):
	"""
	Lauches Angle Measurement utility
	"""
	oMlength = mangle.mangle(self.oImaging)
	return

    def vIZSpectroCB(self):
	self.IZSpectro_Instance += 1
        if self.IZSpectro_Instance > 1:
	    self.vHighlightWindow(self.winIZ)
            return 
	if self.IZSpectro_Instance == 1:
		self.winIZ = Toplevel(takefocus=True)
		self.winIZ.resizable(False, False)
		self.winIZ.title('I-Z Spectroscopy')
		iz = izspectro.izspectro(self.winIZ, self.oToolbar.oStm)
		iz.vGetScanner(self.oToolbar.oScanner)
	return

    def	vLaunchQuickViewCB(self):
	self.QV_Instance += 1
        if self.QV_Instance > 1:
	    self.vHighlightWindow(self.winQV)
            return 
	if self.QV_Instance == 1:
		self.winQV = Toplevel(takefocus=True)
		self.winQV.resizable(False, False)
	        self.winQV.title('QuickView Album')
		oQV = qv.qv(None, None, self.winQV, self)
	return


if __name__ == '__main__':
    menubar()

