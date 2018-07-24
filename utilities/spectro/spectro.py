##########################
#   I-V Spectro Class    #
##########################

import os, numpy, cPickle, time, string, pylab, math
import tkMessageBox, tkFileDialog, FileDialog, tkSimpleDialog
from PIL import Image, ImageTk

import app_spectro
import spectro_daq
import dialogs
import iprog
import offset		
import imaging 
import ivql
import stm7 as stm
import xlia

offsetlogpath = os.path.join(os.curdir, 'log')	# default directory for log files
dumppath = os.path.join(os.curdir, 'dump')	# default directory for dump files

xfilename = os.path.join(offsetlogpath, 'xlog.dat')	# Logfile containing Xoffet value
yfilename = os.path.join(offsetlogpath, 'ylog.dat')	# Logfile containing Yoffset value

IVEXT = 'nrviv'
 
sLUTFile = os.path.join(imaging.sLUTPath, 'bluemap.lut')
LUTFILETYPES = {'lut':('Look Up Table Files','*.lut'), \
		}			

NO_OF_CHANNELS = 3
MAX_IVSPEC_POINTS = stm.BUFSIZE / 2
MAX_DIDVSPEC_POINTS = MAX_IVSPEC_POINTS / NO_OF_CHANNELS 

def fReadOffsetLog(filename):
    off_log = open(filename,'r')
    prev_offset_value = int(float(off_log.read()))
    off_log.close()
    return prev_offset_value
 
canvas_font = ('Times', 24, 'bold')
grid_font = ('Helvetica', 14, 'bold')

__DEBUG__ 		= True

if __DEBUG__ == True:
	from Tkinter import *

def spectro(f = None, oStm = None, oScanner = None):
    """
    Returns Spectro object
    """
    oAppSpectro = app_spectro.app_spectro()
    oAppSpectro.createSwindow(f)
    oSpectro = Spectro(oAppSpectro, oStm, oScanner)
    return oSpectro

class Spectro:
    """
    I-V Spectroscopy Tool
    """
    MIN_STEPSIZE 	= 5		# Minimum Bias Step Size is 5mV
    MAX_STEPSIZE 	= 100		# Maximum Bias Step Size in 100mV
    MIN_BIAS	 	= -9900		# mV
    MAX_BIAS	 	= 9900		# mV
    MIN_STEPDELAY 	= 1		# Minimum Stepping Delay in msec 
    MAX_STEPDELAY 	= 50000		# Maximum Stepping Dalay in msec
    MIN_PRESPECDELAY 	= 20		# Minimum Stepping Delay in msec
    MAX_PRESPECDELAY 	= 2000		# Minimum Stepping Delay in msec
    MIN_INTER_SWEEP_DELAY = 0.1		# Maximum Stepping Dalay in sec
    MAX_INTER_SWEEP_DELAY = 10		# Maximum Stepping Dalay in sec
    DELAYSTEP	  	= 1		# Delay Resolution 50usec
    MIN_MAVG 		= 4		# Minumum Moving Average
    MAX_MAVG 		= 64		# Maximum Moving Average
    MIN_SWEEPS 		= 1		# Minimum number of Sweeps
    MAX_SWEEPS 		= 50		# Maximum number of Sweeps
    BOXCAR		= 32		# Boxcar Filter Length 
    BOXCAR_FINAL	= 8		# Boxcar Filter Length 
    GRID_MODE = 'G'
    POINT_MODE = 'P'

    def __init__(self, oAppSpectro, oStm, oScanner):
	"""
	Class Contructor : Spectro
	"""
	self.oStm = oStm
	self.oScanner = oScanner
	self.nFramePixels = 256		# Pixels in the Image Canvas
	self.MAX_SPECTRO_POINTS = 10	# i.e. no. of markers that can be set

	#### Initial Values of Spectro Settings #####
	self.nLowerBiasLimit = -500	# Spectro begins at this Sample Bias(mV)
	self.nUpperBiasLimit = 500	# Spectro ends at this Sample Bias(mV)
	self.nStepSize = 5		# in mV
	self.nStepDelay = 2		# in msec
	self.nSweeps = 5 
	self.nPreSpectrumDelay = 10	# in msec
	self.nInterSweepDelay = 5	# in sec
	self.nMovAvgPoints = 4
	self.dicSpecParam = {}

	self.anStepList = range(self.MIN_STEPSIZE, self.MAX_STEPSIZE+self.MIN_STEPSIZE, self.MIN_STEPSIZE)
	self.anDelayList = range(self.MIN_STEPDELAY, self.MAX_STEPDELAY+self.DELAYSTEP, self.DELAYSTEP)
	self.anMovAvgList = range(self.MIN_MAVG, self.MAX_MAVG+self.MIN_MAVG, self.MIN_MAVG)
	self.anSweepList = range(self.MIN_SWEEPS, self.MAX_SWEEPS)
	self.bStopLoggingVar = BooleanVar()
	self.strPlotVar = StringVar()
	self.strPlotVar.set('IV')
	self.bStopLoggingVar.set(False)
	self.oAppSpectro = oAppSpectro
	self.spectroModeVar = StringVar()
	self.spectroModeVar.set('IV')
	self.cSpectroModeVar = StringVar()
	self.cSpectroModeVar.set (self.POINT_MODE)
	self.strMarkerVar = StringVar()
	self.strMarkerVar.set('o')
	self.cSpectroModeVar.set (self.POINT_MODE)
	self.strMarkerVar = StringVar()
	self.strMarkerVar.set('o')
	self.strSpectraDispVar = StringVar()
	self.strSpectraDispVar.set('') 
	self.normPlotdIdVVar = BooleanVar ()
	self.normPlotdIdVVar.set (True)
	self.RetraceSweepVar = BooleanVar ()
	self.RetraceSweepVar.set (False)
	self._configureCB()
	self.colorcode = [	'black', 'red', '#A9079C', 'blue', 'cyan', \
				'#E11D13', 'magenta','green', 'yellow', '#FF4500']
	self.vReadGridLUT(sLUTFile)
	self.strCurrentSpecFile = None
	self.vSetScanImage()	# Load default as current scan image
	self.vSelectPointMode()	# Default mode is Point Mode
	self.vShowMarker(self.nFramePixels / 2, self.nFramePixels / 2)
	return

    def _configureCB(self):
	"""
	Attaches Callbacks to SpectroGui widgets 
	"""
        self.oAppSpectro.filemenu.add_command(label='Open Spectro File', \
                                                command=self.vOpenSpectraFile)
        self.oAppSpectro.spectromapmenu.add_command(label='Scan Image', \
                                                command=self.vSetScanImage)
        self.oAppSpectro.spectromapmenu.add_command(label='Retrace Image', \
                                                command=self.vSetRetImage)
	self.oAppSpectro.filemenu.add_command(label='Save Image as JPG', \
						command=self.vSaveAsJPG)
	self.oAppSpectro.filemenu.add_command(label='Export to ASCII', \
						command=self.vExportToASCIICB)
	self.oAppSpectro.settingsmenu.add_command(label='Pre Spectrum Delay', \
						command=self.vPreSpectrumDelayCB)
	self.oAppSpectro.settingsmenu.add_command(label='Inter-Sweep Delay', \
						command=self.vInterSweepDelayCB)
	self.oAppSpectro.settingsmenu.add_checkbutton(label='Acquire on Retrace',\
						variable=self.RetraceSweepVar)
	self.oAppSpectro.settingsmenu.add_command(label='Lockin Amplifier', \
							underline=0, \
							command=self.vLaunchXLIACB)
	self.oAppSpectro.modemenu.add_command(label='Select Point(s) On Image', \
						command=self.selectPointsOnImageCB)
	'''
	self.oAppSpectro.modemenu.add_command(label='Grid Mode',\
						command=self.vSelectGridModeCB)
	'''
	self.oAppSpectro.displaymenu.add_command(label='Load Color Map ',\
							command=self.vLoadLUTCB)
	self._configureSettings()

	self.oAppSpectro.BtnStartSpectro.configure(command=self.vStartLoggerCB)
	self.oAppSpectro.BtnStopSpectro.configure(command=self.vStopLoggerCB)
	self.oAppSpectro.BtnSaveSpectro.configure(command=self.vSaveIVPlotsCB)
	self.oAppSpectro.BtnPMPlotdIdV.configure(command=self.vPlotdIdVCB)
	#self.oAppSpectro.BtnPMPlotNormdIdV.configure(command=self.vPlotNormdIdVCB)
	#self.oAppSpectro.SliderGridSize.configure(state=DISABLED)
	self.oAppSpectro.CBPlotNormdIdV.configure (variable = self.normPlotdIdVVar)
						
	self.oAppSpectro.RBIV.configure (value = 'IV', variable = self.spectroModeVar, \
					command = self.setSpectroMode, \
					)
	self.oAppSpectro.RBdIdV.configure (value = 'dIdV', variable = self.spectroModeVar, \
					command = self.setSpectroMode, \
					)
	self.oAppSpectro.EntryLowerLimit.nTrackVar.trace('w', self.updateSpectralPoints)	
	self.oAppSpectro.EntryUpperLimit.nTrackVar.trace('w', self.updateSpectralPoints)	
	self.vCreateNewImages()
	self.oAppSpectro.filemenu.entryconfig(2, state=DISABLED)
	self.oAppSpectro.filemenu.entryconfig(3, state=DISABLED)
	self.oAppSpectro.settingsmenu.entryconfig(0, state=DISABLED)
	self.oAppSpectro.displaymenu.entryconfig(1, state=DISABLED)
	self.oAppSpectro.displaymenu.entryconfig(2, state=DISABLED)
	self.oAppSpectro.SpectroStatusBar.minimum(0)
	self.vDisableAcquisitionControl()
	self.__vConfigureKBShortCuts()
	return

    def _configureSettings(self):
	"""
	Initializing Settings on the front panel
	"""
	self.oAppSpectro.ScaleStepSize.configure(values=tuple(self.anStepList))
	self.oAppSpectro.ScaleStepSize.configure(command=self.updateSpectralPoints)
	self.oAppSpectro.ScaleSteppingDelay.configure(values=tuple(self.anDelayList))
	self.oAppSpectro.ScaleMovingAvgPoints.configure(values=tuple(self.anMovAvgList))
	self.oAppSpectro.ScaleSweeps.configure(values=tuple(self.anSweepList))
	self.oAppSpectro.EntryLowerLimit.limits([self.MIN_BIAS, self.MAX_BIAS])
	self.oAppSpectro.EntryUpperLimit.limits([self.MIN_BIAS, self.MAX_BIAS])
	self.oAppSpectro.EntryLowerLimit.insert(0,int(self.nLowerBiasLimit))
	self.oAppSpectro.EntryUpperLimit.insert(0,int(self.nUpperBiasLimit))
	while self.nReadStepDelay() < self.nStepDelay:
	        self.oAppSpectro.ScaleSteppingDelay.invoke('buttonup')
	while self.nReadSweeps() < self.nSweeps:
	        self.oAppSpectro.ScaleSweeps.invoke('buttonup')
	self.oAppSpectro.SliderPMFilterLen.set(self.BOXCAR_FINAL)
	self.updateMaxSpectralPointsInfo()
	self.updateSpectralPoints(None)

	return

    def __vConfigureKBShortCuts(self):
	self.oAppSpectro.sGroup.bind('<Control-o>', self.vOpenSpectraFile)
	self.oAppSpectro.sGroup.bind('<Control-s>', self.vSaveIVPlotsCB)
	return

    def updateMaxSpectralPointsInfo(self):
	text = 'IV Mode: ' + str (MAX_IVSPEC_POINTS) + ',   '
	text += 'dIdV Mode: ' + str (MAX_DIDVSPEC_POINTS)
	self.oAppSpectro.LblMaxSpectroPointsInfo.config(text=text)
	return

    def setSpectroMode(self):
        self.updateSpectralPoints(None)
        if self.spectroModeVar.get() == 'IV':
            self.oStm.disableBiasModulation()
        if self.spectroModeVar.get() == 'dIdV':
            self.oStm.enableBiasModulation()
            self.vLaunchXLIACB()
	return


    def	vLaunchXLIACB (self, event=None):
	oXLIA = self.oScanner.oToolBar.oXLIA
	if oXLIA != None:
	    self.oScanner.oToolBar.hightlightXLIA_Window()
	    return
	else:
	    self.oScanner.oToolBar.vLaunchXLIACB()
	    oXLIA = self.oScanner.oToolBar.oXLIA
	    if oXLIA.bValidDevXLIA () == False:
		tkMessageBox.showerror ('LIA not detected !', 'Please verify USB conn. or \n Turn on the Lockin Power Supply', \
					parent = self.oAppSpectro.sGroup)
		return
	return


    def vLoadLUTCB(self):
	ftype = LUTFILETYPES.values()
	file = tkFileDialog.askopenfilename(title='LookUp Table', \
						defaultextension=".lut", \
						filetypes=ftype, \
						initialdir=imaging.sLUTPath, \
						initialfile='default', \
						parent=self.oAppSpectro.sGroup)
	if not(file):
		return
	self.vReadGridLUT(file)
	#self.oQlaunch.vOriginalCB()
	return

    def vReadGridLUT(self,fname=sLUTFile):
	f=open(fname,'r')
	f.readline()	#Comment Line
	self.RGB = []
	for i in range(256):
		asColorVal = f.readline().split()
		rgb = map(lambda(x):int(float(x)*255), asColorVal)
		self.RGB.append(tuple(rgb[:3]))
	f.close()
	return

	return
	 
    def vAddColors(self):
	FrameColor = tkColorChooser.askcolor(title='Marker Color Chooser')
	if (FrameColor[0] == None) or (FrameColor[1] == None):
	    return
	self.colorcode.append(str(FrameColor[1]))
	return

    def vCreateNewImages(self, size=[256,256]):
	"""
	Creates New scan and retrace image	
	"""
	from PIL import Image
	self.SpectroMapImage = Image.new('RGB', (size[1], size[0]))
	self.SpectroMapPhotoImage = ImageTk.PhotoImage(self.SpectroMapImage)
	self.CanRefMap = self.oAppSpectro.CanvasSpectroMap.create_image(0,0, \
					image=self.SpectroMapPhotoImage, anchor=NW)
	self.OpeningText = self.oAppSpectro.CanvasSpectroMap.create_text(self.nFramePixels/2, \
					self.nFramePixels/2, \
					text='Select Reference Map from \'File Menu\'', \
					fill='yellow', \
					)
	return


    def vSetScanImage(self):
        f = open(os.path.join(iprog.dumppath, 'scanimgdump.dmp'))
        afSpectroMap = cPickle.load(f)
        self.dicScanParam = cPickle.load(f)
        f.close()
        ''' Choosing Topography Image in case of Multi-Channel Data '''
        if self.dicScanParam.has_key('NoOfChannels'):
            noc = self.dicScanParam ['NoOfChannels']
        else:
            noc = 0
        if noc > 1:
            channel = 0 # The first channel (Topography Data)
            afSpectroMap = afSpectroMap[0]        
            print 'Spectroscopy using', self.dicScanParam['ChannelNames'][channel], 'Multi-Channel Image Data'
        self.afSpectroMap = iprog.min_maxfilter(afSpectroMap)   # clip noise spikes above std. dev.
	self.vHideSpectraDisplaySettings() 
        self.vRenewSpectroMap() 
	self.vSelectPointMode()	# Default mode is Point Mode
	self.vShowMarker(self.nFramePixels / 2, self.nFramePixels / 2)
        return

    def vSetRetImage(self):
        f = open(os.path.join(iprog.dumppath, 'retimgdump.dmp'))
        afSpectroMap = cPickle.load(f)
        self.dicScanParam = cPickle.load(f)
        f.close()
        ''' Choosing Topography Image in case of Multi-Channel Data '''
        if self.dicScanParam.has_key('NoOfChannels'):
            noc = self.dicScanParam ['NoOfChannels']
        else:
            noc = 0
        if noc > 1:
            channel = 0 # The first channel (Topography Data)
            afSpectroMap = afSpectroMap[0]        
            print 'Spectroscopy using', self.dicScanParam['ChannelNames'][channel], 'Multi-Channel Image Data'
        self.afSpectroMap = iprog.min_maxfilter(afSpectroMap)   # clip noise spikes above std. dev.
	self.vHideSpectraDisplaySettings() 
        self.vRenewSpectroMap()
	self.vSelectPointMode()	# Default mode is Point Mode
	self.vShowMarker(self.nFramePixels / 2, self.nFramePixels / 2)
        return

    def vRenewSpectroMap(self):
        try:
            self.oAppSpectro.CanvasSpectroMap.delete(self.OpeningText)
        except:
            pass
        try:
	    self.vClearMarkers()
        except:
            pass
        graymatrix = iprog.float2gray(self.afSpectroMap)
        colmatrix = map(lambda(x):self.oScanner.oImaging.RGB[int(x)], graymatrix.flat)
        self.SpectroMapImage.putdata(colmatrix)
        self.SpectroMapPhotoImage.paste(self.SpectroMapImage)
	self.oAppSpectro.filemenu.entryconfig(2, state=NORMAL)
	self.oAppSpectro.filemenu.entryconfig(3, state=NORMAL)
	self.oAppSpectro.settingsmenu.entryconfig(0, state=NORMAL)
	self.oAppSpectro.displaymenu.entryconfig(1, state=NORMAL)
	self.oAppSpectro.displaymenu.entryconfig(2, state=NORMAL)
        return

    def vEnableAcquisitionControl(self):
	self.oAppSpectro.BtnStartSpectro.configure(state=NORMAL)
	self.oAppSpectro.BtnStopSpectro.configure(state=NORMAL)
	self.oAppSpectro.BtnSaveSpectro.configure(state=NORMAL)
	return

    def vDisableAcquisitionControl(self):
	self.oAppSpectro.BtnStartSpectro.configure(state=DISABLED)
	self.oAppSpectro.BtnStopSpectro.configure(state=DISABLED)
	self.oAppSpectro.BtnSaveSpectro.configure(state=DISABLED)
	return

    ################# POINT MODE ##################
    def selectPointsOnImageCB(self):
        self.vPointModeCanvasActivate()
        self.vSelectPointMode()
        return 

    def vSelectPointMode(self):
    	#self.vGridModeDeactivate()
	self.vClearMarkers()
	self.vDisableAcquisitionControl()
	self.vHideSpectraDisplaySettings() 
	self.cSpectroModeVar.set(self.POINT_MODE)
	return

    def vPointModeCanvasActivate(self):
	self.oAppSpectro.CanvasSpectroMap.bind('<Button-1>', self.vShowMarkerCB)
	return

    def vPointModeCanvasDeactivate(self):
	self.oAppSpectro.CanvasSpectroMap.unbind('<Button-1>')
	return

    def ciMarkerCount(self,xpos=3, ypos=15):
	"""
	Create Marking for spectroscopy points
	"""	
	canItemMarker = self.oAppSpectro.CanvasSpectroMap.create_text(\
				xpos+2, ypos+2, \
				anchor=NW, \
				text=str(len(self.arMarkerPos)), \
				font=canvas_font, \
				fill=self.colorcode[len(self.arMarkerPos)-1])
	return canItemMarker

    def ciMarker(self,xpos=3, ypos=15):
	"""
	Create Marking for spectroscopy points
	"""	
	arrowbase = 11 
	arrowheight = 30
	canItemMarker = self.oAppSpectro.CanvasSpectroMap.create_polygon(\
				[xpos-arrowbase/2+1, ypos-arrowheight, \
				xpos+arrowbase/2+1, ypos-arrowheight, \
				xpos, ypos], \
				width=2, \
				fill='', \
				outline=self.colorcode[len(self.arMarkerPos)-1])
	return canItemMarker

    def vClearMarkers(self):
	try:
	    for item in self.arSpectroMarkers:
		self.oAppSpectro.CanvasSpectroMap.delete(item)
	except:
	    pass
	try:
	    for item in self.arSpectroMarkersCount:
		self.oAppSpectro.CanvasSpectroMap.delete(item)
	except:
	    pass
	try:
		self.oAppSpectro.CanvasSpectroMap.delete(self.ciGridSpectra)
	except:
	    pass
	self.arSpectroMarkers = []
	self.arSpectroMarkersCount = []
	self.arMarkerPos = []
	self.vClearGridBox()
	self.vClearGridSize()
	return

    def vShowMarkerCB(self, event):
	if len(self.arMarkerPos) >= self.MAX_SPECTRO_POINTS:
	    return
	self.vShowMarker(event.x, event.y)
	return

    def vShowMarker(self, x_pos, y_pos):
	self.vEnableAcquisitionControl()
	self.arMarkerPos.append([x_pos, y_pos])
	self.arSpectroMarkers.append(self.ciMarker(x_pos, y_pos))
	self.arSpectroMarkersCount.append(self.ciMarkerCount(x_pos, y_pos))
	return

    ################# GRID MODE ##################
    def vSelectGridModeCB(self):
    	self.vPointModeCanvasDeactivate()
	self.vClearMarkers()
	self.vHideSpectraDisplaySettings() 
	self.cSpectroModeVar.set(self.GRID_MODE)
        self._vConfigureGridModeSettings()
	self.vEnableAcquisitionControl()
	return

    def _vConfigureGridModeSettings(self):
	self.arRegion = [[0,0], [0,0]]
	self.oAppSpectro.SliderGridSize.configure(state=NORMAL)
	self.oAppSpectro.SliderGridSize.configure(command=self.vShowGridCB)
	self.nStepDelay = self.anDelayList[1]		# in msec
	if self.nStepDelay > self.nReadStepDelay() :
	    dir = 'buttonup'
	else:
	    dir = 'buttondown'
	while self.nReadStepDelay() > self.nStepDelay:
	    self.oAppSpectro.ScaleSteppingDelay.invoke(dir)
	self.vShowGridCB(None)
	return

    def vGridModeDeactivate(self):
	self.oAppSpectro.SliderGridSize.configure(state=DISABLED)
	return

    def vShowGridCB(self, event):
	nGridSize = self.oAppSpectro.SliderGridSize.get()
	self.arRegion[0] = [(self.nFramePixels-nGridSize)/2, (self.nFramePixels-nGridSize)/2]
	self.arRegion[1] = [(self.nFramePixels+nGridSize)/2, (self.nFramePixels+nGridSize)/2]
	self.vShowGridBox()
	self.vShowGridSize()
	return

    def vShowGridBox(self):
    	self.vClearGridBox()
	self.ciGridBox = self.oAppSpectro.CanvasSpectroMap.create_rectangle(self.arRegion,\
				width=2)
	return

    def vClearGridBox(self):
	try:
	    self.oAppSpectro.CanvasSpectroMap.delete(self.ciGridBox)
	except:
	    pass
	return

    def vShowGridSize(self):
	self.vClearGridSize()
	nGridSize = self.oAppSpectro.SliderGridSize.get()
	self.ciGridSize = self.oAppSpectro.CanvasSpectroMap.create_text(\
		self.nFramePixels/2, (self.nFramePixels-nGridSize)/2,\
		text='Grid Size: ' + str(nGridSize) + 'x' + str(nGridSize),\
		anchor=S,\
		font=grid_font,\
		)
	return

    def vClearGridSize(self):
	try:
	    self.oAppSpectro.CanvasSpectroMap.delete(self.ciGridSize)
	except:
	    pass
	return

    def vSpectraDispSettings(self):
	if self.dicSpecParam['Mode'] == self.GRID_MODE:
	    #self.oAppSpectro.LFGridSpectraDisp.grid(row=0, column=2, sticky=N+S)
	    self.oAppSpectro.LFPointSpectraDisp.grid_forget()
	if self.dicSpecParam['Mode'] == self.POINT_MODE:
	    self.oAppSpectro.LFPointSpectraDisp.grid(row=0, column=2, sticky=N+S)
	    #self.oAppSpectro.LFGridSpectraDisp.grid_forget()
	self.vUpdateInfobox ()
	#self.oAppSpectro.sGroup.update()
	return

    def vUpdateInfobox (self):
	self.oAppSpectro.TextInfoBox.delete (1.0, END)
	if self.dicSpecParam.has_key ('XLIA_Param'):
	    self.oAppSpectro.TextInfoBox.insert (INSERT, self.dicSpecParam['XLIA_Param'].__repr__() + '\n')	
	self.oAppSpectro.TextInfoBox.insert (INSERT, self.dicSpecParam.__repr__())	
	return

    def vPreSpectrumDelayCB(self):
	"""
	Sets Pre Spectrum delay
		--> 1-100 msec
	"""
	self.nPreSpectrumDelay = tkSimpleDialog.askinteger('Pre-Spectrum Delay',\
		'Enter Delay (in msec): \n Range (' + str(self.MIN_PRESPECDELAY) + '<PSD<' + str(self.MAX_PRESPECDELAY) + ')',\
 		initialvalue = self.nPreSpectrumDelay,\
 		minvalue = self.MIN_PRESPECDELAY,\
 		maxvalue = self.MAX_PRESPECDELAY , \
 		parent=self.oAppSpectro.sGroup)
	if self.nPreSpectrumDelay == None:
	    self.nPreSpectrumDelay = 10
	    print 'Pre-Spectrum Delay', self.nPreSpectrumDelay, 'ms'
	return

    def vInterSweepDelayCB(self):
	"""
	Sets delay between two consecutive sweeps
		--> 0.1-10 sec
	"""
	self.nInterSweepDelay = tkSimpleDialog.askinteger('Inter Sweep Delay',\
		'Enter Delay (in sec): \n Range (' + str(self.MIN_INTER_SWEEP_DELAY) + '<ISD<' + str(self.MAX_INTER_SWEEP_DELAY) + ')',\
 		initialvalue = self.nInterSweepDelay, \
 		minvalue = self.MIN_INTER_SWEEP_DELAY, \
 		maxvalue = self.MAX_INTER_SWEEP_DELAY, \
 		parent=self.oAppSpectro.sGroup)
	if self.nInterSweepDelay == None:
	    self.nInterSweepDelay = 5 
	    print 'Inter-Sweep Delay', self.nInterSweepDelay , 'sec'
	return

    def vCloseAppSpectroCB(self):
	"""
	Callback for closing Spectroscopy
		--> Saves I-V plots and mean I-V plot
		--> Brings back Bias to initial value
	"""
	pylab.close('all')
	self.oAppSpectro.sGroup.destroy()
	return

    def nReadUpperLimit(self):
	"""
	Reads Upper bias limit of the ramp, entered by the user
	"""
	ul = self.oAppSpectro.EntryUpperLimit.get()
	return float(ul)

    def nReadLowerLimit(self):
	"""
	Reads Lower bias of the ramp limit, entered by the user
	"""
	ll = self.oAppSpectro.EntryLowerLimit.get()
	return float(ll)

    def vHideSpectraDisplaySettings(self):
	self.oAppSpectro.LFPointSpectraDisp.grid_forget()
	#self.oAppSpectro.LFGridSpectraDisp.grid_forget()
	return


    ################# DATA ACQUISITION ##################

    def vStartLoggerCB(self):
	"""
	KickStart I-V Spectroscopy
	"""
	self.oAppSpectro.BtnStartSpectro.configure(state=DISABLED)
	self.vHideSpectraDisplaySettings() 
	self.vPointModeCanvasDeactivate()
	self.vStartIVAcquisition()
	#self.vPointModeCanvasActivate()
	### After Acquisition is over ###
	#print 'Acquisition Over !!'
	#self.vStopIVLogging()
	return

    def bValidateInputs(self):
	"""
	Gets from the user
		--> step size
		--> steping delay
		--> moving average points
		--> sweeps
	and than checks whether bias range lies within permissible  values
	"""
	self.nStepSize = self.nReadStepSize() 
	self.nStepDelay = self.nReadStepDelay()
	self.nMovAvgPoints = self.nReadMovAvgPoints()
	self.nSweeps = self.nReadSweeps()
	return self.bCheckBiasRange()

    def bCheckBiasRange(self):
	"""
	Checks whether Bias range is:
	  ** not -ve 
	  ** not lesser than 50
	  ** not more than 1024 points
	"""
	nLowerBiasLimit = self.nReadUpperBiasLimit()
	nUpperBiasLimit = self.nReadLowerBiasLimit()
	if (nUpperBiasLimit - nLowerBiasLimit) < 50:
	    return False
	nStepSize = self.nReadStepSize()
	np = abs ((nUpperBiasLimit - nLowerBiasLimit) / nStepSize)
	#print 'No. of Spectral Points', np
	if self.spectroModeVar.get() == 'IV':
		if np > MAX_IVSPEC_POINTS:
	    		tkMessageBox.showerror('NP Overflow', 'More than ' + str(MAX_IVSPEC_POINTS) + \
				' spectral points.. \n Reduce range or Increase StepSize', parent=self.oAppSpectro.sGroup)
	    		return False
	if self.spectroModeVar.get() == 'dIdV':
		if np > MAX_DIDVSPEC_POINTS:
	    		tkMessageBox.showerror('NP Overflow', 'More than ' + str(MAX_DIDVSPEC_POINTS) + \
				' spectral points.. \n Reduce range or Increase StepSize', parent=self.oAppSpectro.sGroup)
	    		return False
	self.nLowerBiasLimit = nLowerBiasLimit
	self.nUpperBiasLimit = nUpperBiasLimit
	return True

    def updateSpectralPoints(self, *event):
	nLowerBiasLimit = self.nReadUpperBiasLimit()
	nUpperBiasLimit = self.nReadLowerBiasLimit()
	nStepSize = self.nReadStepSize()
	np = abs ((nUpperBiasLimit - nLowerBiasLimit) / nStepSize)
	text = 'Total Spectral Points: ' + str (np)
	self.oAppSpectro.LblSpectralPointsInfo.configure(text=text)

	if self.spectroModeVar.get() == 'IV':
		if np > MAX_IVSPEC_POINTS:
		    self.oAppSpectro.LblSpectralPointsInfo.configure(fg='red')
		else:
		    self.oAppSpectro.LblSpectralPointsInfo.configure(fg='blue')
	if self.spectroModeVar.get() == 'dIdV':
		if np > MAX_DIDVSPEC_POINTS:
		    self.oAppSpectro.LblSpectralPointsInfo.configure(fg='red')
		else:
		    self.oAppSpectro.LblSpectralPointsInfo.configure(fg='blue')
	return

    def vStartIVAcquisition(self):
	if not self.bValidateInputs():
	    tkMessageBox.showerror('Settings Invalid', 'Acquisition failed, verify settings validity... ', parent=self.oAppSpectro.sGroup)
    	    self.vEnableAcquisitionControl()
	    return
	print 'Inputs are valid'

	''' Stop LIA auto-update while logging in dIdV Mode '''
	if self.spectroModeVar.get() == 'dIdV':
		if xlia.getXLIA_Status() == 1:		# XLIA is connected
		    print '@@@ Stopping AutoUpdate'
	    	    oXLIA = self.oScanner.oToolBar.oXLIA
	    	    oXLIA.stopAutoUpdater() 

	self.oSpectroDaq = spectro_daq.spectro_daq(self, self.oStm)
	self.oSpectroDaq.vGetSpecParameters()
	self.strCurrentSpecFile = None
	self.dicSpecParam = self.oSpectroDaq.dicSpecParam.copy()
	if self.cSpectroModeVar.get() == self.GRID_MODE:
	    self.oSpectroDaq.vStartGridIVLogging()
	    self.afPlotsAtPos = self.oSpectroDaq.afPlotsAtPos
	    self.afTopoImage = self.oSpectroDaq.afTopoImage
	    self.vPostAcquisitionState()
	    self.vSpectraDispSettings()
	    self.vPlotGridModeData()
	    return
	if self.cSpectroModeVar.get() == self.POINT_MODE:
	    self.oSpectroDaq.vStartPointIVLogging()
	    self.afPlotsAtPos = self.oSpectroDaq.afPlotsAtPos
	    self.vPostAcquisitionState()
	    self.vSpectraDispSettings()
	    self.vPlotPointModeData()
	''' Restart LIA auto-update while logging in dIdV Mode '''
	if self.spectroModeVar.get() == 'dIdV':
		if xlia.getXLIA_Status() == 1:		# XLIA is connected
	    	    oXLIA = self.oScanner.oToolBar.oXLIA
	    	    oXLIA.startAutoUpdater() 
	return

    def vStopLoggerCB(self):
	"""
	Halts I-V measurements	
	"""
	self.vStopIVLogging()
	return

    def vStopIVLogging(self):
	"""
	Stops I-V spectroscopy
	"""
	self.bStopLoggingVar.set(True)
	#self.vPostAcquisitionState()
	return

    def vPostAcquisitionState(self):
	self.oAppSpectro.BtnStartSpectro.configure(state=NORMAL)
	self.oAppSpectro.BtnStopSpectro.configure(state=NORMAL)
	self.oAppSpectro.BtnSaveSpectro.configure(state=NORMAL)
	self.oAppSpectro.sGroup.update()
	return

    def vSaveIVPlotsCB(self, events=None):
	self.oAppSpectro.sGroup.update()
	self.vAskToSaveSpectroData()
	return

    def vAskToSaveSpectroData(self):
	filename = dialogs.SaveImageDialog('.'+IVEXT, 'Do you want to \n save spectro data?' \
					, parent=self.oAppSpectro.sGroup)
	if not filename:
	    return
	self.vSaveSpectroData(filename)
	return

    def nReadUpperBiasLimit(self):
	return int(self.oAppSpectro.EntryLowerLimit.get())	

    def nReadLowerBiasLimit(self):
	return int(self.oAppSpectro.EntryUpperLimit.get())

    def nReadStepDelay(self):
	return int(self.oAppSpectro.ScaleSteppingDelay.get())	

    def nReadMovAvgPoints(self):
	return int(self.oAppSpectro.ScaleMovingAvgPoints.get())	

    def nReadSweeps(self):
	return int(self.oAppSpectro.ScaleSweeps.get())

    def nReadStepSize(self):
	return int(self.oAppSpectro.ScaleStepSize.get())

    def vSaveSpectroData(self, filename):
	try:
	    fd = open(filename, 'w')
	except:
	    tkMessageBox.showerror('Cannot Create File','Please check if you have permissions \n or other filesystem error', parent=self.oAppSpectro.sGroup)
	    return
	cPickle.dump(self.dicSpecParam, fd)
	cPickle.dump(self.afPlotsAtPos, fd)
	cPickle.dump(self.afSpectroMap, fd)
	cPickle.dump(self.dicScanParam, fd)
	if self.cSpectroModeVar.get() == self.GRID_MODE:
	    cPickle.dump(self.afTopoImage, fd)
	fd.close()
	print 'Saving Spectro Data as:', filename
	return

    def vOpenSpectraFile(self, event=None):
    	spectrofilepath = dialogs.strPathTracker()
	oFD = FileDialog.LoadFileDialog(self.oAppSpectro.sGroup, title='Load IV Spectroscopy File')
	filename = oFD.go(dir_or_file=spectrofilepath, key='track', pattern='*.'+IVEXT)
	if filename == None:
	    return
	self.strCurrentSpecFile = filename
	print 'Spectra data file:', filename
	fd = open(filename)
	self.dicSpecParam = cPickle.load(fd)
	print 'Spec Params: ', self.dicSpecParam
	self.afPlotsAtPos = cPickle.load(fd)
	self.afSpectroMap = cPickle.load(fd)	
	self.dicScanParam = cPickle.load(fd)
	if self.dicSpecParam.has_key('Mode'):
	    if self.dicSpecParam['Mode'] == self.GRID_MODE:
		try:
		    self.afTopoImage = cPickle.load(fd)
		except:
		    print 'Grid Mode Spectra is taken without Topographic Image'
	fd.close()
	self.vAdjustSpectraSettings()
	if self.dicSpecParam.has_key('Mode'):
	    if self.dicSpecParam['Mode'] == self.GRID_MODE:
		self.vSpectraDispSettings()
		self.vRenewSpectroMap()
		self.vPlotGridModeData()
		return
	    if self.dicSpecParam['Mode'] == self.POINT_MODE:
		if self.dicSpecParam.has_key ('SpectroMode'):
		    if self.dicSpecParam.has_key ('XLIA_Param'):
			print self.dicSpecParam ['XLIA_Param']
		    else:
			print 'Lock-In Parameters not found...'	
		self.vSpectraDispSettings()
		self.vRenewSpectroMap()
		self.vPlotPointModeData()
	    else:
		### Historic Data with no grid mode key is assumed to be Point Mode ###
		print 'Pre-Historic IV Data'
		self.dicSpecParam['Mode'] = self.POINT_MODE
		self.vSpectraDispSettings()
		self.vRenewSpectroMap()
		self.vPlotPointModeData()
	return

    def vAdjustSpectraSettings(self):
	self.oAppSpectro.EntryLowerLimit.delete(0, END)
	self.oAppSpectro.EntryLowerLimit.insert(0, str(int(self.dicSpecParam['LowerBias']))) 
	self.oAppSpectro.EntryUpperLimit.delete(0, END)
	self.oAppSpectro.EntryUpperLimit.insert(0, str(int(self.dicSpecParam['UpperBias']))) 
	self.vAdjustParamDisplay(self.oAppSpectro.ScaleStepSize, self.dicSpecParam['StepSize']) 
	self.vAdjustParamDisplay(self.oAppSpectro.ScaleSteppingDelay, self.dicSpecParam['StepDelay']) 
	self.vAdjustParamDisplay(self.oAppSpectro.ScaleMovingAvgPoints, self.dicSpecParam['MovAvgPoints']) 
	self.vAdjustParamDisplay(self.oAppSpectro.ScaleSweeps, self.dicSpecParam['Sweeps']) 
	if self.dicSpecParam.has_key('SpectroMode') == True:
		self.spectroModeVar.set(self.dicSpecParam ['SpectroMode'])
	return

    def vAdjustParamDisplay(self, appWidget, nValue):
	"""
	Updates the Spectroscopy Settings on the main window according 
	to the current file being displayed
	"""
	if int(appWidget.get()) == nValue:
	    return
	if int(appWidget.get()) > nValue:
	    dir = 'buttondown'
	else:
	    dir = 'buttonup'
	while(1):
	        appWidget.invoke(dir)
	    	if int(appWidget.get()) == nValue:
		    break
	return

    ### POINT MODE DATA DISPLAY ###
    def vPlotPointModeData (self):
        self.anBiasRange = range(self.dicSpecParam['LowerBias'],\
			self.dicSpecParam['UpperBias'] + self.dicSpecParam['StepSize'],\
			self.dicSpecParam['StepSize'])
	nFL = self.oAppSpectro.SliderPMFilterLen.get()
	self.vClearMarkers()
	for pos in self.dicSpecParam['MarkerPos']:
	    self.arMarkerPos.append(pos)
	    self.arSpectroMarkers.append(self.ciMarker(pos[0], pos[1]))
	    self.arSpectroMarkersCount.append(self.ciMarkerCount(pos[0], pos[1]))
	aafI = []	# Current sweeps @ position
	if self.dicSpecParam.has_key('RetraceSweepMode'):
	    if self.dicSpecParam['RetraceSweepMode'] == True:
		aafI_Retrace = []	# Current sweeps @ position

	if self.dicSpecParam.has_key('SpectroMode'):
	    if self.dicSpecParam['SpectroMode'] == 'dIdV':
		aafLIA_Out1 = []	# LIA Output channel 1
		aafLIA_Out2 = []	# LIA Output channel 2
		multiChannelSpectra = True
		if self.dicSpecParam.has_key('RetraceSweepMode'):
		    if self.dicSpecParam['RetraceSweepMode'] == True:
			aafLIA_Out1_Retrace = []	# LIA Output channel 1
			aafLIA_Out2_Retrace = []	# LIA Output channel 2
	    else:
		multiChannelSpectra = False
	else:
	    multiChannelSpectra = False

	for plots in self.afPlotsAtPos:
	    afI = []
	    if self.dicSpecParam.has_key('RetraceSweepMode'):
		if self.dicSpecParam['RetraceSweepMode'] == True:
	    	    afI_Retrace = []
	    if multiChannelSpectra == True:
		afLIA_Out1 = []	# LIA Output channel 1
		afLIA_Out2 = []	# LIA Output channel 2
		if self.dicSpecParam.has_key('RetraceSweepMode'):
		    if self.dicSpecParam['RetraceSweepMode'] == True:
			afLIA_Out1_Retrace = []	# LIA Output channel 1
			afLIA_Out2_Retrace = []	# LIA Output channel 2
	    sweep_count = 0
	    for sweep in plots:
	        if multiChannelSpectra == True:
		    rawI = numpy.asarray(sweep [0])		# First Channel is TC
		    lia_out1 = numpy.asarray(sweep [1])	# In Phase or Amplitude
		    lia_out2 = numpy.asarray(sweep [2])	# Quadrature or Phase
		else:
                    rawI = numpy.asarray(sweep)
		w = numpy.ones(nFL,'f')
                I = numpy.convolve(w/w.sum(), rawI.copy(), \
                                   mode='valid')	# Filter Current Data
		if self.dicSpecParam.has_key('RetraceSweepMode'):
		    if self.dicSpecParam['RetraceSweepMode'] == True:
			if sweep_count % 2 == 0:		# Even sweep : Trace
			    afI.append(I/1000.0)		# Converting TC value to mV/1000->pA/1000=nA
			else:					# Odd sweep : Retrace
			    afI_Retrace.append(I/1000.0)	
		    else:			# No retrace sweep 
			afI.append(I/1000.0)	
		else:				# Old Data before Retrace got implemented
		    afI.append(I/1000.0)
			
	        if multiChannelSpectra == True:
		    amplitude = numpy.sqrt ((lia_out1 ** 2) + (lia_out2 ** 2))
		    phase = 180 * numpy.arctan2 (lia_out2, lia_out1) / math.pi
		    # Normalized against LIA Reference Amplitude
		    if self.dicSpecParam.has_key ('XLIA_Param'):
			amplitude /= self.dicSpecParam ['XLIA_Param'] ['RefAmplitude']
		    if self.normPlotdIdVVar.get () == True:
			conductance = abs (self.dicScanParam ['TCSetpoint'] / self.dicScanParam ['SampleBias'] )
			# Normalized by Conductance
			amplitude /= conductance
		    if self.dicSpecParam.has_key('RetraceSweepMode'):
			if self.dicSpecParam['RetraceSweepMode'] == True:
			    if sweep_count % 2 == 0:		# Even sweep : Trace
				afLIA_Out1.append (amplitude)
				afLIA_Out2.append (phase)
			    else:				# Odd sweep : Retrace
				afLIA_Out1_Retrace.append (amplitude)
				afLIA_Out2_Retrace.append (phase)
			else:	# No retrace Sweep
			    afLIA_Out1.append (amplitude)
			    afLIA_Out2.append (phase)

		    else:		# Old Data before Retrace got implemented
			afLIA_Out1.append (amplitude)
			afLIA_Out2.append (phase)
		sweep_count += 1
	    aafI.append(afI)
	    if self.dicSpecParam.has_key('RetraceSweepMode'):
		if self.dicSpecParam['RetraceSweepMode'] == True:
		    aafI_Retrace.append(afI_Retrace) 
	    if multiChannelSpectra == True:
		aafLIA_Out1.append (afLIA_Out1)
		aafLIA_Out2.append (afLIA_Out2)
		if self.dicSpecParam.has_key('RetraceSweepMode'):
		    if self.dicSpecParam['RetraceSweepMode'] == True:
			aafLIA_Out1_Retrace.append (afLIA_Out1_Retrace)
			aafLIA_Out2_Retrace.append (afLIA_Out2_Retrace)
	#afV = sweep[:,0]
	#self.vPlotIV(aafI, self.anBiasRange)
	print 'Plot IV...'
	self.vPlotIV(aafI, self.anBiasRange[int(nFL/2):-1*int((nFL-1)/2)])
	if multiChannelSpectra == True:
	    print 'Plot dI/dV (Amplitude) ...'
	    if self.normPlotdIdVVar.get () == True:
		ylabel = '(dI / dV) / (I / V) Amplitude (arb. units)'
	    else:
		ylabel = '(dI / dV) Amplitude (arb. units)'
	    self.vPlotIV (aafLIA_Out1, self.anBiasRange ,\
				title = 'dI / dV Spectra ', \
				ylabel = ylabel, \
				xlabel = 'Sample Bias (mV)' \
				)
	    print 'Plot dI/dV (Phase) ...'
	    if self.normPlotdIdVVar.get () == True:
		ylabel = '(dI / dV) / (I / V) Phase (deg)'
	    else:
		ylabel = '(dI / dV) Phase (deg)'
	    self.vPlotIV (aafLIA_Out2, self.anBiasRange, \
				title = 'dI / dV Spectra ', \
				ylabel = ylabel, \
				xlabel = 'Sample Bias (mV)' \
				)

	### Retrace Plot ###
	if self.dicSpecParam.has_key('RetraceSweepMode'):
	    if self.dicSpecParam['RetraceSweepMode'] == True:
		print 'Plot Retrace IV...'
		bias_range = self.anBiasRange[::-1]
		title = 'I-V Spectra (Retrace) '
		self.vPlotIV(aafI_Retrace, bias_range[int(nFL/2):-1*int((nFL-1)/2)], title)
		if multiChannelSpectra == True:
		    print 'Plot dI/dV Retrace (Amplitude) ...'
		    if self.normPlotdIdVVar.get () == True:
			ylabel = '(dI / dV) / (I / V) Amplitude (arb. units)'
		    else:
			ylabel = '(dI / dV) Amplitude (arb. units)'
		    self.vPlotIV (aafLIA_Out1_Retrace, bias_range,\
					title = 'dI / dV Spectra (Retrace) ', \
					ylabel = ylabel, \
					xlabel = 'Sample Bias (mV)' \
					)
		    print 'Plot dI/dV Retrace (Phase) ...'
		    if self.normPlotdIdVVar.get () == True:
			ylabel = '(dI / dV) / (I / V) Phase (deg)'
		    else:
			ylabel = '(dI / dV) Phase (deg)'
		    self.vPlotIV (aafLIA_Out2_Retrace, bias_range, \
					title = 'dI / dV Spectra (Retrace) ', \
					ylabel = ylabel, \
					xlabel = 'Sample Bias (mV)' \
					)
	return


    ### GRID MODE DATA DISPLAY ###
    def vPlotGridModeData(self):
	self.vClearMarkers()
	self.vCreateNewGridImage()
	self._confGridSpectraDispSettings()
	self.oIVQL = ivql.IVQL(self)		# Quicklaunch functions for Grid Spectra
	self.vRenewGridImage()
	return

    def _confGridSpectraDispSettings(self):
	self.anBiasRange = range(self.dicSpecParam['LowerBias'],\
			self.dicSpecParam['UpperBias'] + self.dicSpecParam['StepSize'],\
			self.dicSpecParam['StepSize'])
	self.oAppSpectro.SliderBias.configure(values=tuple(self.anBiasRange)) 
	self.oAppSpectro.SliderBias.configure(command=self.vShowBiasSlice)
	sweep_list = map(lambda(x):'Sweep '+str(x), range(1,self.dicSpecParam['Sweeps']+1))
	sweep_list.insert(0, 'Avg. all Sweeps')	
	self.oAppSpectro.SBoxSweepNo.configure(values=tuple(sweep_list))
	self.oAppSpectro.SBoxXPos.configure(values=tuple(range(self.dicSpecParam['GridSize']))) 
	self.oAppSpectro.SBoxYPos.configure(values=tuple(range(self.dicSpecParam['GridSize']))) 
	self.oAppSpectro.RBIV.configure(variable=self.strPlotVar, value='IV')
	self.oAppSpectro.RBdIdV.configure(variable=self.strPlotVar, value='dIdV')
	self.oAppSpectro.RBTopoImage.configure(variable=self.strPlotVar, value='Topo', \
				command=self.vRenewGridImage)
	self.oAppSpectro.BtnGMPlotCurve.configure(command=self.vGMPlotCurvesCB)
	self.oAppSpectro.BtnGMAddPoint.configure(command=self.vGMAddPointCB)
	self.oAppSpectro.BtnGMClearPoint.configure(command=self.vGMClearPointCB)
	self.oAppSpectro.BtnGMSelectLine.configure(command=self.vGMSelectLineCB)
	self.arRegion = [[0,0], [0,0]]
	#self.oAppSpectro.SliderGridSize.configure(state=NORMAL)
	#self.oAppSpectro.SliderGridSize.set(self.dicSpecParam['GridSize'])
	#self.oAppSpectro.SliderGridSize.configure(state=DISABLED)
	self.vShowGridCB(None)
	self.GMPoints = []
	return

    def vCreateNewGridImage(self):
	"""
	Creates New Grid Spectra Image on the Canvas	 
	"""
	from PIL import Image
	self.GridSpectraImage = Image.new('RGB', [self.dicSpecParam['GridSize']]*2)
	self.GridSpectraPhotoImage = ImageTk.PhotoImage(self.GridSpectraImage)
	self.ciGridSpectra = self.oAppSpectro.CanvasSpectroMap.create_image(\
					(self.nFramePixels - self.dicSpecParam['GridSize'])/2,
					(self.nFramePixels - self.dicSpecParam['GridSize'])/2,
					image=self.GridSpectraPhotoImage, anchor=NW)
	return

    def vRenewGridImage(self, nBias=0, nSweep=0):
	if nSweep == 0 and self.dicSpecParam['Sweeps'] > 1:	# Averaging over all the sweeps
	    aafPlotsAtPos = self.aafCalculateGridAvgI().copy()
	else:
	    aafPlotsAtPos = self.afPlotsAtPos.copy()
	if self.strPlotVar.get() == 'IV':
	    self.vPlotGridIV(aafPlotsAtPos, nBias)
	if self.strPlotVar.get() == 'dIdV':
	    self.vPlotGriddIdV(aafPlotsAtPos, nBias)
	if self.strPlotVar.get() == 'Topo':
	    self.vPlotGridTopoImage(self.afTopoImage.copy())
	return

    def vPlotGridIV(self, aafPlotsAtPos, nBias):
	try:
	    nSlice = self.anBiasRange.index(nBias)
	except:
	    nSlice = len(self.anBiasRange)
        afGridI = aafPlotsAtPos[:, :, 0, nSlice]
	self.oIVQL.vAcquireData(afGridI)	# pass the current image data on the grid to ivql
	self.vSplashGridImage(afGridI)
	return

    def vPlotGriddIdV(self, aafPlotsAtPos, nBias):
	nFL = int(self.oAppSpectro.SliderGMFilterLen.get())
	try:
	    nSlice = self.anBiasRange.index(nBias)
	except:
	    nSlice = nFL 				# that many slices above the Lower Bias Limit 
	if len(self.anBiasRange) - nSlice <= nFL:	# that many slices below the upper limit
	    nSlice = len(self.anBiasRange) - nFL - 1
	if nSlice < nFL:
	    nSlice = nFL 				# that many slices above the Lower Bias Limit 
	afGriddIdV = self.afCalculateGriddIdV(aafPlotsAtPos, nSlice) 
	self.oIVQL.vAcquireData(afGriddIdV)	# pass the current image data on the grid to ivql
	self.vSplashGridImage(afGriddIdV)
        return

    def vPlotGridTopoImage(self, afTopoImage):
	self.oIVQL.vAcquireData(afTopoImage)	# pass the current image data on the grid to ivql
	self.vSplashGridImage(afTopoImage)
	return

    def vSplashGridImage(self, afGridData):
	#self.afCurrentGridData = afGridData.copy()	
        clipped_afGridData = iprog.min_maxfilter(afGridData)
        graymatrix = iprog.float2gray(clipped_afGridData)
        colmatrix = map(lambda(x):self.RGB[int(x)], graymatrix.flat)
        self.GridSpectraImage.putdata(colmatrix)
        self.GridSpectraPhotoImage.paste(self.GridSpectraImage)
	return

    def afCalculateGriddIdV(self, aafPlotsAtPos, nSlice):
	nFL = int(self.oAppSpectro.SliderGMFilterLen.get())
        afLAvg = aafPlotsAtPos[:, :, 0, nSlice]
        afUAvg = aafPlotsAtPos[:, :, 0, nSlice+1]
	for i in range(1, nFL):
	    afLAvg += aafPlotsAtPos[:, :, 0, nSlice-i]
	    afUAvg += aafPlotsAtPos[:, :, 0, nSlice+i+1]
	#print 'Slice Kudicho', nSlice, (afUAvg/nFL - afLAvg/nFL) / self.dicSpecParam['StepSize']
	return (afUAvg/nFL - afLAvg/nFL) / self.dicSpecParam['StepSize']

    def aafCalculateGridAvgI(self):
	aafPlotsAtPosRaw = self.afPlotsAtPos.copy()
	lShape = list(aafPlotsAtPosRaw.shape)
	lShape[2] = 1	# Average of all sweeps, so sweeps dimension is now 1  
	aafPlotsAtPosFil = numpy.zeros(tuple(lShape), 'f') 
	nFL = int(self.oAppSpectro.SliderGMFilterLen.get())
	afSweep = numpy.zeros(len(self.anBiasRange), 'f')
	for y in range(self.dicSpecParam['GridSize']):
	    for x in range(self.dicSpecParam['GridSize']):
		for ns in range(self.dicSpecParam['Sweeps']):
		    w = numpy.ones(nFL,'f')
		    afSweep += numpy.convolve(w/w.sum(), aafPlotsAtPosRaw[y, x, ns, :], \
                                              mode='same')
		aafPlotsAtPosFil[y, x, 0, :] = afSweep / self.dicSpecParam['Sweeps']
	return aafPlotsAtPosFil

	return

    def vShowBiasSlice(self):
	nBias = int(self.oAppSpectro.SliderBias.get())
	self.vRenewGridImage(nBias)
	self.oAppSpectro.sGroup.update()
	return

    def vGMAddPointCB(self):
	nXPos = int(self.oAppSpectro.SBoxXPos.get())
	nYPos = int(self.oAppSpectro.SBoxYPos.get())
	self.GMPoints.append([nXPos, nYPos])
	return

    def vGMClearPointCB(self):
	self.GMPoints = []
	return

    def vGMSelectLineCB(self):
	nXPos = int(self.oAppSpectro.SBoxXPos.get())
	tkMessageBox.showinfo('Line Selected', \
			'Plotting Curves along line ' + str(nXPos), parent=self.oAppSpectro.sGroup)
	self.GMPoints = []
	for y in range(self.dicSpecParam['GridSize']):
	    self.GMPoints.append([nXPos, y])
	return

    def vGMPlotCurvesCB(self):
	if self.strPlotVar.get() == 'IV':
	    self.vGMPlotIVCurves()
	return

    def vGMPlotIVCurves(self):
	if self.GMPoints == []:
	    tkMessageBox.showinfo('No Selection', \
			'Please select a add point/line', parent=self.oAppSpectro.sGroup)
	    return
	nFL = int(self.oAppSpectro.SliderGMFilterLen.get())
	aafI = []
	for point in self.GMPoints:
	    afI = []
	    for sweep in range(self.dicSpecParam['Sweeps']):
		# Filter Current Data
		w = numpy.ones(nFL,'f')
		I = numpy.convolve(w/w.sum(), self.afPlotsAtPos[point[0], point[1], sweep, :], \
                                       mode='same')
		afI.append(I/1000.0)	# Converting TC value to mV/1000->pA/1000=nA
	    aafI.append(afI)
	afV = self.anBiasRange
	self.vPlotIV(aafI, afV)
	return

    def vSetIVCB(self):
	self.strPlotVar.set('IV')
	return

    def vSetdIdVCB(self):
	self.strPlotVar.set('dIdV')
	return

    def vSetdIdVIVCB(self):
	self.strPlotVar.set('dIdVIV')
	return

    def vPlotdIdVCB(self):
	self.vPlotdIdV()
	return
    '''
    def vPlotNormdIdVCB(self):
	self.vPlotNormdIdV()
	return
    '''
    def vPlotIV(self, aafI, afV, \
			title = 'I-V Spectra : ', \
			xlabel = 'Bias Voltage (mV)', \
			ylabel = 'Tunneling Current (nA)'):
	"""
	Earlier Plots I vs V... now generalized for LIA Outputs also 
	"""
	pos = 0
	pylab.ion()
	pylab.figure()
	for loc in aafI:
	    nos = 0
	    for sweep in loc: 
		mstyle = self.strMarkerVar.get()
		pylab.plot(afV, sweep, c = self.colorcode[pos%10])
		nos +=1 
	    pylab.xlabel (xlabel)
	    pylab.ylabel (ylabel)	
	    if self.strCurrentSpecFile:
		spec_file = self.strCurrentSpecFile.rsplit(os.sep,1)[-1]
	    else:
		spec_file = time.asctime() 
	    pylab.title (title + spec_file + '\n'+ 'No. of Sweeps: ' + str(nos))
	    pylab.grid(True)
	    pos+=1
	pylab.show()
	return

    def vPlotdIdV(self):
	"""
	Plots dI/dV vs V
	"""
	biasRange, aafdIdV = self.aafCalculatePointdIdV()
	
	if self.normPlotdIdVVar.get () == True:
	    ylabel = '(dI / dV) / (I / V) (arb. units)'
	else:
	    ylabel = 'dI / dV' 
	self.vPlotIV (aafdIdV, biasRange, \
				title = 'Conductance Plots (Numerical) ', \
				ylabel = ylabel, \
				xlabel = 'Sample Bias (mV)' \
				)
	'''
	afV, aafdIdV = self.aafCalculatePointdIdV()
	pylab.figure()
	for i in range (len (aafdIdV)):
	    pylab.plot (afV, aafdIdV[i], c = self.colorcode[i])
	pylab.xlabel('Bias Voltage (mV)')
	pylab.ylabel('dI/dV (Conductance)')
	if self.strCurrentSpecFile:
	    pylab.title(self.strCurrentSpecFile.rsplit(os.sep,1)[-1])
	pylab.grid(True)
	'''
	return
	
    def aafCalculatePointdIdV(self):
	nFL = self.oAppSpectro.SliderPMFilterLen.get()
	dV = self.dicSpecParam['StepSize']
	#aafAvgSpectraAtPos = self.aafCalculateAvgSpectra()	# Averaging sweeps at each position
	#afdIdV = [0]*len(aafAvgSpectraAtPos)
	#pos = 0


	multiChannel = False
	if self.dicSpecParam.has_key('SpectroMode'):
	    if self.dicSpecParam['SpectroMode'] == 'dIdV':
		multiChannel = True
	    else:
		multiChannel = False

	if self.normPlotdIdVVar.get () == True:
	    conductance = abs (self.dicScanParam ['TCSetpoint'] / self.dicScanParam ['SampleBias'])
	aafdIdVPlotsAtPos = []
	for plots in self.afPlotsAtPos:
	    afPlots = []
	    for sweep in plots:
		if multiChannel == True:
                    rawI = numpy.asarray (sweep [0])	# First data set is T.C.
		else:
                    rawI = numpy.asarray (sweep)
		w = numpy.ones(nFL,'f')
		I = numpy.convolve(w/w.sum(), rawI.copy(), mode='valid')	# Averaging filter of length nFL
		dIdV = (I[1:] - I[:-1]) / dV    # dI/dV
		dIdV.resize (I.shape)		# Since one value in both the arrays is omitted,
		dIdV [-1] = dIdV [-2] 		# penultimate value is copied to the last value
		if self.normPlotdIdVVar.get () == True:
		    dIdV /= conductance
		afPlots.append (dIdV)
	    aafdIdVPlotsAtPos.append (afPlots)

	afBias = self.anBiasRange [int (nFL / 2) : -1 * int((nFL - 1) / 2)]

	return afBias, aafdIdVPlotsAtPos 
	'''
	for afAvgPlot in aafAvgSpectraAtPos:
	    afdIdV[pos] = (afAvgPlot[1:] - afAvgPlot[:-1])/dV    # dI/dV
	    w = numpy.ones(2*nFL,'f')
	    afdIdV[pos] = numpy.convolve(w/w.sum(), afdIdV[pos].copy(), mode='valid')
	    pos += 1
	return self.anBiasRange[int(nFL)+1:-1*int((2*nFL-1)/2)], afdIdV		# All bias voltage values except the first one
	#return self.anBiasRange[1:], afdIdV
	'''
    '''
    def aafCalculateAvgSpectra(self):
	aafAvgSpectra = [0]*len(self.dicSpecParam['MarkerPos'])
	nFL = self.oAppSpectro.SliderPMFilterLen.get()
	pos = 0
	for plots in self.afPlotsAtPos:
	    for sweep in plots:
                rawI = numpy.asarray(sweep)
		w = numpy.ones(nFL,'f')
		I = numpy.convolve(w/w.sum(), rawI.copy(), mode='same')	# Averaging filter of length nFL
		I /= 1000.0	# pA (mV) to nA
		aafAvgSpectra[pos] += I
	    aafAvgSpectra[pos] /= len(plots)	# Average over all sweeps at a point
	    pos += 1
	return aafAvgSpectra 
    '''

    '''
    def vPlotNormdIdV(self):
	"""
	Plots (dI/dV)/(I/V) vs V
	"""
	afV, aafNormdIdV = self.aafCalculatePointNormdIdV()
	pylab.figure()
	for i in range(len(aafNormdIdV)):
	    pylab.plot(afV, aafNormdIdV[i], c = self.colorcode[i])
	pylab.xlabel('Bias Voltage (mV)')
	pylab.ylabel('(dI/dV)/(I/V)')
	if self.strCurrentSpecFile:
	    pylab.title(self.strCurrentSpecFile.rsplit(os.sep,1)[-1])
	pylab.grid(True)
	return

    def aafCalculatePointNormdIdV(self):
	afV, aafdIdV = self.aafCalculatePointdIdV()
	aafAvgIAtPos = self.aafCalculateAvgSpectra()	# Averaging sweeps at each position
	nFL = self.oAppSpectro.SliderPMFilterLen.get()
	aafNormdIdV = [0]*len(aafdIdV)
	#sp = abs(afV).argmin()
	pos = 0
	for Iavg in aafAvgIAtPos:
	    afVbyI = self.anBiasRange / Iavg 
	    aafNormdIdV[pos] = aafdIdV[pos] * afVbyI[1:]
	    pos += 1
	return afV, aafNormdIdV
    '''

    def vSaveAsJPG(self):
	"""
	Method: vSaveAsJPG
	    Converts a spectroscopy image currently displayed
	    on the Canvas into a JPG image.
	Aguments: None
	Return: None
	"""
	filepath=dialogs.strPathTracker()
	fname = tkFileDialog.asksaveasfilename(initialdir=filepath,initialfile='untitled',\
				title='Load File', parent=self.oAppSpectro.sGroup)
	if not fname:
	    return
	dialogs.strPathTracker(fname)
	try:
	    self.oAppSpectro.CanvasSpectroMap.postscript(file=fname+'spec.ps')
	except:
	    tkMessageBox.showerror('Cannot Create File','Please check if you have permissions \n or other filesystem error', parent=self.oAppSpectro.sGroup)
	    return
	from PIL import Image
	specps = Image.open(fname+'spec.ps')
	SpecIm = Image.new('RGB', (248,248))	# this happens 256 down to 248 in jpg
	SpecIm.paste(specps,(0,0))
	SpecIm.save(fname+'spec.jpg','JPEG', quality=100)
	os.remove(fname+'spec.ps')
	print 'Spectro Map JPG file saved as:', fname+'spec.jpg'
	return

    def vExportToASCIICB(self):
	if self.strCurrentSpecFile == None:
	    tkMessageBox.showwarning('IV Data not Saved!!', \
			'Please save the current data before exporting', parent=self.oAppSpectro.sGroup)
	    return
	self.vExportToASCII()	
	return

    def vHighlightWindow(self, winObj):
	winObj.deiconify()
	winObj.lift()
	return

    def vExportToASCII(self):
	"""
	Save spectra plots in a .txt file with same name.txt
	"""
	print 'File exported to ASCII: ', self.strCurrentSpecFile
	strASCIIfilename = os.path.split(self.strCurrentSpecFile)[1] + '.csv'
	filepath = dialogs.strPathTracker()
	strFile = tkFileDialog.asksaveasfilename(title='Save ASCII file as', defaultextension=".csv", \
			initialdir=filepath, initialfile=strASCIIfilename, parent=self.oAppSpectro.sGroup)
	if strFile == None:
	    return
	try:
	    asciifd = open(strFile, 'w')
	except:
	    tkMessageBox.showerror('Cannot Open File', 'Write permission denied \n Please try another folder', parent=self.oAppSpectro.sGroup)
	    return
	fd = open(self.strCurrentSpecFile)
	dicSpecParam = cPickle.load(fd)
	#print 'Spec Params: ', dicSpecParam
	afPlotsAtPos = cPickle.load (fd)
	afSpectroMap = cPickle.load (fd)
	dicScanParam = cPickle.load (fd)
	fd.close()
	
	for key in dicSpecParam:
	    if key != 'XLIA_Param':	# avoid XLIA Parameters currently
	        asciifd.write(str(key) + ': ' + str(dicSpecParam[key]) + '\n')
	
	if self.dicSpecParam.has_key ('SpectroMode'):
	    if self.dicSpecParam.has_key ('XLIA_Param'):
		dicXLIA_Param = self.dicSpecParam ['XLIA_Param']
		asciifd.write('\n### Lock-In Parameters ### \n')
		for key in dicXLIA_Param :
		    asciifd.write(str(key) + ': ' + str(dicXLIA_Param [key]) + '\n')
	    else:
		print 'Lock-In Parameters not found...'

	nLowerBiasLimit = dicSpecParam['LowerBias']
	nUpperBiasLimit = dicSpecParam['UpperBias']
	nStepSize = dicSpecParam['StepSize']
	nSweeps = dicSpecParam['Sweeps']

	if dicSpecParam.has_key('RetraceSweepMode'):
	    if dicSpecParam['RetraceSweepMode'] == True:
		nSweeps *= 2	# Retrace Sweeps doubles the no. of sweeps

        bias_steps = range(nLowerBiasLimit, \
                           nUpperBiasLimit+nStepSize, \
                           nStepSize)
	strHeader = 'V(mV)'+ ',' 
	for i in range(nSweeps):
	    if dicSpecParam.has_key('RetraceSweepMode'):
		if dicSpecParam['RetraceSweepMode'] == True:
		    if (i % 2) != 0:		# Odd Sweeps is retrace
	    		strHeader += 'I(pA) ReSwp' + str(i+1) + ','
		    else:
			strHeader += 'I(pA) Swp' + str(i+1) + ','
		else:
		    strHeader += 'I(pA) Swp' + str(i+1) + ','
	    else:
		strHeader += 'I(pA) Swp' + str(i+1) + ','
	    
	# A Matrix formed with first row as Bias Values and successive rows as sweeps
	# for each position. This matrix is then written to text file 
	afSweeps = numpy.zeros((len(bias_steps), nSweeps + 1),'f')
	multichannel_spectra = False 
	if self.dicSpecParam.has_key ('SpectroMode'):
	    if self.dicSpecParam['SpectroMode'] == 'dIdV':
		multichannel_spectra = True
		afSweeps = numpy.zeros ((len (bias_steps), NO_OF_CHANNELS * nSweeps + 1), 'f')
		strHeader = 'V(mV)' + ',' 
		for i in range (nSweeps):
		    if dicSpecParam.has_key('RetraceSweepMode'):
			if dicSpecParam['RetraceSweepMode'] == True:
			    if (i % 2) != 0:		# Odd Sweeps is retrace
		    		strHeader += 'I(pA) ReSwp' + str(i+1) + ',' + \
						'AM(mV) ReSwp' + str(i+1) + ',' + \
						'PH(dg) ReSwp' + str(i+1) + ','
			    else:
				strHeader += 'I(pA) Swp' + str(i+1) + ',' + \
						'AM(mV) Swp' + str(i+1) + ',' + \
						'PH(dg) Swp' + str(i+1) + ','
			else:
			    strHeader += 'I(pA) Swp' + str(i+1) + ',' + \
					'AM(mV) Swp' + str(i+1) + ',' + \
					'PH(dg) Swp' + str(i+1) + ','
		    else:
			strHeader += 'I(pA) Swp' + str(i+1) + ',' + \
					'AM(mV) Swp' + str(i+1) + ',' + \
					'PH(dg) Swp' + str(i+1) + ','
	afSweeps[:,0] = bias_steps
	for pos in range(len(dicSpecParam['MarkerPos'])):
	    asciifd.write('Sweeps at Position: ' + str(dicSpecParam['MarkerPos'][pos]) + '\n')
	    asciifd.write(strHeader + '\n')
	    for sweep in range(nSweeps):
		if multichannel_spectra == False:
		    sweep_data = afPlotsAtPos[pos][sweep]
		    if dicSpecParam.has_key('RetraceSweepMode'):
			if dicSpecParam['RetraceSweepMode'] == True:
			    if (sweep % 2) != 0:		# Odd Sweeps is retrace
				sweep_data = sweep_data[::-1]	# Reversed data as per first column bias_steps
	            afSweeps[:, sweep+1] = numpy.asarray(sweep_data)
		else:
		    rawI_data = afPlotsAtPos[pos][sweep][0]
		    lia_out1_data = afPlotsAtPos[pos][sweep][1]
		    lia_out2_data = afPlotsAtPos[pos][sweep][2]
		    if dicSpecParam.has_key('RetraceSweepMode'):
			if dicSpecParam['RetraceSweepMode'] == True:
			    if (sweep % 2) != 0:		# Odd Sweeps is retrace
				rawI_data = rawI_data[::-1]
				lia_out1_data = lia_out1_data[::-1]	# Reversed data as per first column bias_steps
				lia_out2_data = lia_out2_data[::-1]	# Reversed data as per first column bias_steps
		    rawI = numpy.asarray (rawI_data)
		    lia_out1 = numpy.asarray (lia_out1_data)
		    lia_out2 = numpy.asarray (lia_out1_data)
		    amplitude = numpy.sqrt ((lia_out1 ** 2) + (lia_out2 ** 2))
		    # Normalized against LIA Reference Amplitude
		    amplitude /= dicXLIA_Param ['RefAmplitude']
		    if self.normPlotdIdVVar.get () == True:
			conductance = abs (dicScanParam ['TCSetpoint'] / dicScanParam ['SampleBias'])
			# Normalized by Conductance
			amplitude /= conductance
		    phase = 180 * numpy.arctan2 (lia_out2, lia_out1) / math.pi
		    afPlotsAtPos[pos][sweep][0] = rawI 
		    afPlotsAtPos[pos][sweep][1] = amplitude
		    afPlotsAtPos[pos][sweep][2] = phase
		    for count in range (NO_OF_CHANNELS):
	        	afSweeps[:, (NO_OF_CHANNELS * sweep) + count + 1] = numpy.asarray (afPlotsAtPos [pos] [sweep] [count])
	    # Writing Matrix to text file	
	    for i in range(len(bias_steps)):
		row = map(lambda(x):asciifd.write(str(x)+','), afSweeps[i].tolist())
		asciifd.write('\n')
	asciifd.close()    
	tkMessageBox.showinfo('Export Done!!', \
		'ASCII data saved in file:\n' + strASCIIfilename, parent=self.oAppSpectro.sGroup)
	return


if __name__ == '__main__':
    spectro()


