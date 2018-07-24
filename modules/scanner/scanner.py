#####################
#   Scanner Class   #
#####################

__DEBUG__ 	= True
OVER 		= True
NOTOVER 	= False

import os 
import math
import cPickle
import time
import numpy
from PIL import ImageTk
import tkMessageBox
import tkSimpleDialog

import lib.tkValidatingEntry as tkValidatingEntry
import lib.tkStatusBar as tkStatusBar
import apps.dialogs as dialogs
from utilities.iprog import iprog
import import_
import lib.stm7 as stm
from utilities.lia import xlia
import app_scanner
import daq

im_size_list	= [256, 512]
im_size_list.extend(range(300,800, 50))
im_size_list.sort()

IMAGE_SIZES	= tuple(im_size_list)
MIN_IMAGESIZE 	= IMAGE_SIZES[0]	#256
MAX_IMAGESIZE 	= IMAGE_SIZES[-1]	#750
#ATTENUATION     = 5.0
MAX_LA_SPAN     = 20000.0
RESOLUTION      = MAX_LA_SPAN / 65535.0
MAX_SA_SPAN     = MAX_LA_SPAN #/ATTENUATION
SA_MAX_STEPSIZE = MAX_SA_SPAN / MIN_IMAGESIZE
LA_MAX_STEPSIZE = MAX_LA_SPAN / MIN_IMAGESIZE
#LA_MAX_STEPSIZE -= (LA_MAX_STEPSIZE % RESOLUTION)
SA_MIN_STEPSIZE = round (RESOLUTION, 4)
LA_MIN_STEPSIZE = SA_MIN_STEPSIZE 

FRAME_DELAY     = 1
SIGMA           = 2.5
XL_GAIN		= 10.0		#The final PA443s has gain of 10
HVA_GAIN	= 10.0

TIP_PARKING_MODES = {'center' : 'center', 'corner' : 'corner'}

logpath      	 = os.path.join(os.curdir, 'log')
globlogfile  	 = os.path.join(logpath, 'glob.dat')	
iconpath	 = os.path.join('apps', 'icons')		
play_iconfile	 = os.path.join(iconpath, 'play.jpeg')	
rec_iconfile	 = os.path.join(iconpath, 'record.jpg')	
quit_iconfile	 = os.path.join(iconpath, 'cuttu.jpg')	
btn_font_type = ('verdana', 10, 'normal')		

if __DEBUG__ == True:
	from Tkinter import *

def scanner(f=None, oStm=None):
	"""
	Returns Scanner object
	"""
	oAppScanner = app_scanner.app_scanner()
	oAppScanner.createSSwindow(f)
	oScanner = Scanner(oAppScanner, oStm)
	return oScanner

def dicReadGlobalParam():
    f = open(globlogfile)
    dicGlobalParam = cPickle.load(f)
    f.close()
    return dicGlobalParam 

def vWriteGlobalParam(dicGlobalParam):
    f = open(globlogfile, 'w')
    cPickle.dump(dicGlobalParam, f)
    f.close()
    return

def fGetPiezoXCalibration():
    """
    Returns: Float Value - X-direction calibration in nm/V 
    """
    dicGlobalParam = dicReadGlobalParam()
    fXCalib = dicGlobalParam['XCalibration']
    return fXCalib

def fGetPiezoZCalibration():
    """
    Returns: Float Value - Z-direction calibration in nm/V 
    """
    dicGlobalParam = dicReadGlobalParam() 
    fZCalib = dicGlobalParam['ZCalibration']
    return fZCalib

def getZ_Polarity():
    dicGlobalParam = dicReadGlobalParam() 
    zPol = dicGlobalParam['ZPolarity']
    return zPol

def vSavePiezoXCalibration(piezo_x):
    dicGlobalParam = dicReadGlobalParam()
    dicGlobalParam['XCalibration'] = piezo_x
    dicGlobalParam['YCalibration'] = piezo_x	# Considering both X and Y movements to be the same.
    vWriteGlobalParam(dicGlobalParam)
    return

def vSavePiezoZCalibration(piezo_z):
    dicGlobalParam = dicReadGlobalParam()
    dicGlobalParam['ZCalibration'] = piezo_z
    vWriteGlobalParam(dicGlobalParam)
    return

def fGetHVAGain():
    dicGlobalParam = dicReadGlobalParam()
    if dicGlobalParam.has_key('HVAGain'):
	fHVAGain = dicGlobalParam['HVAGain']
    else:
	fHVAGain = 10.0
    return fHVAGain

def vSaveHVAGain(fHVAGain):
    dicGlobalParam = dicReadGlobalParam()
    dicGlobalParam['HVAGain'] = fHVAGain
    vWriteGlobalParam(dicGlobalParam)
    return

def arGetAreaRanges():
    piezo_xy = fGetPiezoXCalibration()
    arAreaRanges = [ \
    [MIN_IMAGESIZE*SA_MIN_STEPSIZE*piezo_xy*1e-3, \
		MIN_IMAGESIZE*SA_MAX_STEPSIZE*piezo_xy*1e-3], \
    [MIN_IMAGESIZE*LA_MIN_STEPSIZE*piezo_xy*1e-3, \
		MIN_IMAGESIZE*LA_MAX_STEPSIZE*piezo_xy*1e-3], \
    [MIN_IMAGESIZE*LA_MIN_STEPSIZE*piezo_xy*XL_GAIN*1e-3, \
		MIN_IMAGESIZE*LA_MAX_STEPSIZE*piezo_xy*XL_GAIN*1e-3], \
    ]		#The ranges are in nm
    return arAreaRanges

def getTipParkingMode():
	dicGlobalParam = dicReadGlobalParam()
	if dicGlobalParam.has_key('TipParkingMode'):
		tipParkingMode = dicGlobalParam['TipParkingMode']
	else:
		tipParkingMode = TIP_PARKING_MODES['center']
	return tipParkingMode

def setTipParkingMode(tipParkingMode):
	dicGlobalParam = dicReadGlobalParam()
	dicGlobalParam['TipParkingMode'] = tipParkingMode
	vWriteGlobalParam(dicGlobalParam)
	return


class Scanner:
	gain_list = stm.ADC_GAIN 
	tc_gain_list = gain_list 

	delay_list = stm.step_delay_list
	lia_delay_list = stm.lia_step_delay_list

	size_list = IMAGE_SIZES			#range(MIN_IMAGESIZE, MAX_IMAGESIZE + 1)		
	sa_steplist = numpy.arange(SA_MIN_STEPSIZE, SA_MAX_STEPSIZE, SA_MIN_STEPSIZE)
	sa_steplist = map(lambda(x):round(x,4), sa_steplist.tolist())
	#print 'SA STEPLIST', sa_steplist
	xsa_steplist = map (lambda (x) : round((XL_GAIN * x), 3), sa_steplist)
	la_steplist = numpy.arange(LA_MIN_STEPSIZE, LA_MAX_STEPSIZE, LA_MIN_STEPSIZE)
	xla_steplist = map (lambda (x) : round((XL_GAIN * x), 3), la_steplist)
	#nDisplaylines = 200								
	bStopScanner = None
	oAppScanner = None	
	nImageSize = None
	nGain = None
	nStepSize = None
	nDelay = None
	HORIZONTAL	= 2
	VERTICAL	= 3 
	ZMODE		= 4
	TCMODE		= 5
	SMALL_AREA	= 6
	LARGE_AREA	= 7
	LDOS_MODE	= 8
	LBH_MODE	= 9

	def __init__(self, oAppScanner, oStm):
		"""
		Class Contructor : Scanner
		Arguments :
			oAppScanner : object of class ScannerGui
			oStm        : object of class Stm
		"""
		self.oAppScanner = oAppScanner
		self.oStm = oStm
		self.nImageSize = 256 
		self.nGain = 1 
		self.nStepSize = 15 
		self.nDelay = 500 
		self.NO_OF_CHANNELS = 1

                self.DelayUnitVar = StringVar()
                self.DelayUnitVar.set(u'\u00B5s')

		self.bApplyMinMaxVar = BooleanVar () 
		self.bScanStatusVar = BooleanVar () 
		self.bRecordMovie = BooleanVar ()
		self.bXLAreaVar = BooleanVar ()
		self.bSimulScanVar = BooleanVar ()
		self.nRefreshVar = IntVar ()
		self._configureCB ()
		# Initialization of Scan parameters is done after Offset object is also created
		# So the initilization function is moved in vGetOffset function
		#self.Lock = threading.Lock()
		self.nDisplayRefreshVar = IntVar ()	
		self.nDisplayRefreshVar.set (5)
		self.bXLAreaVar.set (False)
		self.vClearXLAreaHandler()
		self.bSimulScanVar.set (False)
		self.LIA_StatusVar = BooleanVar ()
		self.LIA_StatusVar.set (False)
		self.LIA_ModeVar = BooleanVar ()
		self.LIA_ModeVar.set (False)
		self.tipParkingModeVar = StringVar()
		self.tipParkingModeVar.set(getTipParkingMode())
		self.systemTipParkingReadyVar = BooleanVar()
		xlia.setXLIA_Off ()
		return
	
	def _configureCB (self):
		"""
		Attaches Callbacks to ScannerGui widgets 
		"""
		self.bAskEveryTime = BooleanVar()
		self.AreaVar = IntVar()
		self.AreaVar.trace('w',self.vShowArea)
		self.bXLAreaVar.trace('w',self.vShowArea)
		self.ScanDirectionVar = IntVar() 
		self.DigitizationModeVar = IntVar()
		if self.oStm.fd != None:
                    self.DigitizationModeVar.trace('w', self.vSetDigitizationMode)
		self.oAppScanner.RBHorz.configure(variable=self.ScanDirectionVar, \
					command=self.vSetScanDirection, \
					value=self.HORIZONTAL)
		self.oAppScanner.RBVert.configure(variable=self.ScanDirectionVar, \
					command=self.vSetScanDirection, \
					value=self.VERTICAL)
		self.oAppScanner.RBTC.configure(
					variable=self.DigitizationModeVar, \
					command=self.vSetDigitizationMode, \
					value=self.TCMODE)
		self.oAppScanner.RBZ.configure( \
					variable=self.DigitizationModeVar, \
					command=self.vSetDigitizationMode, \
					value=self.ZMODE)
		self.oAppScanner.RB_LDOS.configure(\
					variable=self.DigitizationModeVar, \
					command=self.vSetDigitizationMode, \
					value=self.LDOS_MODE)
		self.oAppScanner.RB_LBH.configure (
					variable=self.DigitizationModeVar, \
					command=self.vSetDigitizationMode, \
					value=self.LBH_MODE)
		self.oAppScanner.EntryDelay.configure(values=tuple(self.delay_list))
		self.oAppScanner.EntryDelay.configure(command=self.vShowInfoCB)

		self.oAppScanner.EntryImageSize.configure(values=tuple(self.size_list))
		self.oAppScanner.EntryImageSize.configure(command=self.nGetMaxStepSize)

		self.oAppScanner.EntryStepSize.configure(command=self.vDisplaySizeCB)

		self.oAppScanner.EntryGain.configure(values=tuple(self.gain_list))
		self.oAppScanner.EntryGain.configure(command=self.vSetGainCB)

		self.oAppScanner.BtnStartScan.configure(command=self.BtnStartScanCB)
		self.oAppScanner.BtnStopScan.configure(command=self.BtnStopScanCB)
		return

	def _initScanParameters(self):

		"""
		Performs initial Scan settings
		"""
		self.vInitScanDirection()
		self.vInitDigitizationMode()
		self.vInitScanArea()
		index = self.delay_list.index(self.nDelay)
		for i in range(index):
			self.oAppScanner.EntryDelay.invoke('buttonup')
		index = self.size_list.index(self.nImageSize)
		for i in range(index):
			self.oAppScanner.EntryImageSize.invoke('buttonup')
		temp_sa_steplist = self.sa_steplist + [self.nStepSize]
		temp_sa_steplist.sort() 
		index = temp_sa_steplist.index(self.nStepSize)
		for i in range(index):
			self.oAppScanner.EntryStepSize.invoke('buttonup')
		self.vRenewAreaBox()
		self.bScanStatusVar.set(OVER)
		self.bRecordMovie.set(False)
		self.vInitAskEveryTime(True)
		self.bApplyMinMaxVar.set(True)
		self.dicScanParam = None
		self.diMovieSettings = {'bPlay':False, 'bRec':False, 'framedelay':1, 'nof':2}
		self.vShowInfo()
		return

	def vGetMain(self, MainMaster):
		"""
		Links MainWindow to Scanner class
		"""
		self.MainMaster = MainMaster
		self.__vConfigureKBShortcuts()
		return

	def vGetImaging(self, oImaging):
		"""
		Links Imaging object to Scanner class
		"""
		self.oImaging = oImaging
		return

	def vGetOffset(self, oOffset):
		"""
		Links Offset object to the Scanner class
		"""
		self.oOffset = oOffset
		self._initScanParameters()
		return

	def vGetCRO (self, oCRO):
		''' Links to the CRO object created in main.py '''
		self.oCRO = oCRO
		return

	def vGetWalker(self, oWalker):
		"""
	        Links Walker to the Scanner class
		"""
		self.oWalker = oWalker
		return

	def vGetToolBar(self, oToolBar):
		"""
	        Links Toolbar to the Scanner class
		"""
		self.oToolBar = oToolBar
		return

	def vGetMenuBar(self, oMenuBar):
		"""
	        Links Menubar to the Scanner class
		"""
		self.oMenuBar = oMenuBar
		return
 
	def vInitAskEveryTime(self, mode=True):
		"""
		Sets AskEveryTime mode 
		"""
		self.bAskEveryTime.set(mode)
		return

	def vInitScanDirection(self):
		"""
		Sets Scan Direction Horizontal / Vertical
		"""
		self.ScanDirectionVar.set(self.HORIZONTAL)
		self.vSetScanDirection()
		return

	def vInitDigitizationMode(self):
		"""
		Sets Digitization Mode CC / CH
		"""
		#self.DigitizationModeVar.set(self.TCMODE)
		self.DigitizationModeVar.set(self.ZMODE)
		#self.vSetDigitizationMode()
		return

	def vInitScanArea(self):
		"""
		Sets Scan Area Small / Large
		"""
		self.AreaVar.set(self.SMALL_AREA)
		self.vClearXLAreaHandler()
		return

	def vShowArea(self, *args):
		"""
		if Small area is selected than enter 1 in Step Size entry widget
		else if Large area is selected than enter 5
		"""
		if self.AreaVar.get() == self.SMALL_AREA:
		    if self.bXLAreaVar.get():
			self.oAppScanner.EntryStepSize.configure(values=tuple(self.xsa_steplist))
			self.VoltageSpan = MAX_SA_SPAN*XL_GAIN
		    else:
			self.oAppScanner.EntryStepSize.configure(values=tuple(self.sa_steplist))
			self.VoltageSpan = MAX_SA_SPAN
		if self.AreaVar.get() == self.LARGE_AREA:
		    if self.bXLAreaVar.get():
			self.oAppScanner.EntryStepSize.configure(values=tuple(self.xla_steplist))
			self.VoltageSpan = MAX_LA_SPAN*XL_GAIN
		    else:
			self.oAppScanner.EntryStepSize.configure(values=tuple(self.la_steplist))
			self.VoltageSpan = MAX_LA_SPAN
		return

	def nReadImageSize(self):
		"""
		Reads Image size entered by the user
		"""
		nImageSize = [0]*2
		nImageSize[0] = int(self.oAppScanner.EntryImageSize.get())
		nImageSize[1] = nImageSize[0]	
		return nImageSize				
		

	def nReadDelay(self):
		"""
		Reads Delay time entered by the user
		"""
		nDelay= int(self.oAppScanner.EntryDelay.get())
		return nDelay

	def nReadStepSize(self):
		"""
		Reads Step Size entered by the user
		"""
		nStepSize = [0]*2
		nStepSize[0] = round(float(self.oAppScanner.EntryStepSize.get()), 4)
		nStepSize[1] = nStepSize[0]
		return nStepSize
		

	def nReadGain(self):
		"""
		Read ADC gain entered by the user
		"""
		nGain= int(self.oAppScanner.EntryGain.get())
		return nGain


	def vSetScanDirection(self):
		"""
		Sets scan direction Horizontal / Vertical 
		"""
		if self.ScanDirectionVar.get() == self.HORIZONTAL:
		    slopePot = stm.XSLOPE_POT 
		    print 'Horizontal'
		if self.ScanDirectionVar.get() == self.VERTICAL:
		    print 'Vertical'
		    slopePot = stm.YSLOPE_POT 
		try:
			self.oCRO.selectSlopePot(slopePot)
		except:
			pass
		return

	def vSetDigitizationMode(self, *args):
		"""
		Sets Digitization Mode CC / CH / LDOS / LBH
		"""
		nMode = self.DigitizationModeVar.get()
		if nMode == self.TCMODE:
			if self.LIA_ModeVar.get() == True:
				self.oAppScanner.EntryDelay.configure(values=tuple(self.delay_list))
				self.oAppScanner.LabelDelay.configure(text='Delay/Step(us)')
				self.DelayUnitVar.set(u'\u00B5s')
				self.LIA_ModeVar.set (False)
		if nMode == self.ZMODE:
			if self.LIA_ModeVar.get() == True:
				self.oAppScanner.EntryDelay.configure(values=tuple(self.delay_list))
				self.oAppScanner.LabelDelay.configure(text='Delay/Step(us)')
				self.DelayUnitVar.set(u'\u00B5s')
				self.LIA_ModeVar.set (False)
		if nMode == self.LDOS_MODE:
			if self.LIA_ModeVar.get() == False:
				self.oAppScanner.EntryDelay.configure(values=tuple(self.lia_delay_list))
				self.oAppScanner.LabelDelay.configure(text='Delay/Step(ms)')
				self.DelayUnitVar.set('ms')
				self.LIA_ModeVar.set (True)
			if xlia.getXLIA_Status() != 1:
			    message = 'Please power-up the LIA and click LIA button in the toolbar'
			    tkMessageBox.showinfo ('To Launch Lockin Amplifier', message)
			else:
			    dicXLIA_Param = xlia.getXLIA_ParametersFromFile()
	    		    self.oToolBar.hightlightXLIA_Window()

		if nMode == self.LBH_MODE:
			if self.LIA_ModeVar.get() == False:
				self.oAppScanner.EntryDelay.configure(values=tuple(self.lia_delay_list))
				self.oAppScanner.LabelDelay.configure(text='Delay/Step(ms)')
				self.DelayUnitVar.set('ms')
				self.LIA_ModeVar.set (True)
			if xlia.getXLIA_Status() != 1:
			    message = 'Please power-up the LIA and click LIA button in the toolbar'
			    tkMessageBox.showinfo ('To Launch Lockin Amplifier', message)
			else:
			    dicXLIA_Param = xlia.getXLIA_ParametersFromFile()
	    		    self.oToolBar.hightlightXLIA_Window()

		self.vSetDigitizationModeHandler(nMode)
		return
 
	def vSetGainCB(self):
		"""
		Sets ADC Gain
		"""
		gain = int(self.oAppScanner.EntryGain.get())
		self.vSetGain(gain)
		return

	def vShowInfoCB(self):
		"""
		Callback for displaying image size in angs, step size and delay 	
		"""
		self.vShowInfo()
		return


	def vShowInfo(self, imsize=None, stepsize=None, delay=None, showonimage=False, \
				gain=None, bXLArea=False):
		"""
		Displays Blue Info line (in scan-settings frame), showing area scanned @ time taken per line.
		Arguments :
			imsize   : list Image Size
			stepsize : int Step Size
			delay    : int Step Delay
			gain     : int ADC Gain
		"""
		if not stepsize:
		    stepsize = self.nReadStepSize()[0]
		size, units = self.fCalculateSize(imsize, stepsize, bXLArea)
		rate = int(self.fCalculateScanRate(imsize, delay))
		try:
		    self.oImaging.vRenewSize(size, units, self.dicScanParam['NoOfChannels'])
		except:
		    pass
		piezo_xy = fGetPiezoXCalibration()
		stsize = stepsize/1e3 * piezo_xy
		self.oAppScanner.LabelInfo.configure(text= 'L: ' + str('%3.3f' % size) + units + \
						', ' + str('%1.3f' % stsize) + 'nm/step')#\
						#' at '+ str(rate) + 'ms/line'+ ' *')
		return

	def vDisplaySizeCB(self):
		"""
		Displays Image Size	
		"""
		self.vShowInfo()
		return

	def afCalculateScale(self, afImData):
	    """
	    Calculate the Z-scale of the image being displayed in the colorbar on the right, result in angs
	    """
	    mode = self.dicScanParam['DigitizationMode']
	    if self.dicScanParam.has_key('NoOfChannels'):
	      channels = self.dicScanParam['NoOfChannels']
	    else:
	      channels = 1
	    if (mode == self.ZMODE) or (channels > 1):
	    	calibFactor = fGetPiezoZCalibration() / 1.0e3	#since data is in mV and z-calib in in nm/V
		units = 'nm'
	    if mode == self.TCMODE:
		tcaGain	= 1		
	    	calibFactor = tcaGain / 1e3 	# since data is in mV and tca gain is 1pA/mV
		units = 'nA'
	    Zpi_min, Zpi_max = afImData.min(), afImData.max()
	    Zpi_amax = abs(Zpi_max - Zpi_min)
	    Zpi_amean = abs((Zpi_max + Zpi_min) / 2.0 - Zpi_min)
	    Zpi_amin = 0
	    
	    return calibFactor * Zpi_amean, calibFactor * Zpi_amin, calibFactor * Zpi_amax, units 

	def fCalculateSize(self, imsize=None, stsize=None, bXLArea=False):
		"""
		Calculates Scan Image size in angs
		"""
		if not imsize:
		    imsize = self.nReadImageSize()[0]
		    stsize = self.nReadStepSize()[0]
		piezo_xy = fGetPiezoXCalibration()
		if bXLArea:
		    stsize *= XL_GAIN
		size = stsize/1e3 * imsize * piezo_xy		#piezo_xy is in nm/V and stsize is in mV
		if (size >= 1000):
		    mulfactor = 0.001 
		    units = u'\u00B5m' 
		if (size >= 10) and (size < 1000):
		    mulfactor = 1
		    units = 'nm'
		if (size < 10):
		    mulfactor = 10
		    units = u'\u00C5' 
		try:
		    self.vRenewAreaBox()
		except:
		    pass
		return size*mulfactor, units

	def vRenewAreaBox(self):
		imsize = self.nReadImageSize()[0]
		stsize = self.nReadStepSize()[0]
		self.oOffset.vRenewAreaBox(imsize*stsize)		
		return

	def fCalculateScanRate(self, imsize=None, delay=None):
		"""
		Calculates Scan Rate in ms/scanline
		"""
		if not imsize:
		    delay = self.nReadDelay()
		    imsize = self.nReadImageSize()[0]
		rate = delay*imsize/1.0e3		
		return rate

	def vWriteAndSetGain(self, nGain):
		"""
		Reads and adjusts adc gain in the widget to permissible values
		"""
		curr_gain = int(self.oAppScanner.EntryGain.get())
		if curr_gain == nGain:
			return
		if curr_gain < nGain:
			move = 'buttonup'
		if curr_gain > nGain:
			move = 'buttondown'
		while 1:
			if curr_gain == nGain:
				break
			else:
				self.oAppScanner.EntryGain.invoke(move)
			curr_gain = int(self.oAppScanner.EntryGain.get())
		return

	def vSetGain(self, nGain):	
		"""
		Sets ADC Gain
		"""
		#nGain = int(math.log(nGain, 2))
		self.vSetGainHandler(nGain)	
		return

	def selectTipParkingModeCB(self):
		TipParkingModesDialog(self.MainMaster, self.tipParkingModeVar)
		if self.tipParkingModeVar.get() != getTipParkingMode():
			self.systemTipParkingReadyVar.set(False)
			self.prepareSystemForTipParkingCB()
		return

	def prepareSystemForTipParkingCB(self):
		self.oWalker.vDisableWsGroup()
		self.oOffset.vDisableOsGroup()
		self.oToolBar.vDisableTbGroup()
		self.oMenuBar.vDisableMbGroup()
		self.vDisableSsGroup()
		self.MainMaster.update()
	
		self.prepareSystemForTipParking()

		self.vEnableSsGroup()
		self.oMenuBar.vEnableMbGroup()
		self.oWalker.vEnableWsGroup()
		self.oOffset.vEnableOsGroup()
		self.oToolBar.vEnableTbGroup()
		self.MainMaster.update()
		return

	def prepareSystemForTipParking(self, delay = 1):	# delay in ms
		if self.tipParkingModeVar.get() == TIP_PARKING_MODES['corner']:
			present_position = 0	# mV
			rest_position = stm.cdac[stm.XDAC]	# mV
			if delay == 0:
				self.oStm.set_scandacs(stm.XDAC, rest_position)
				self.oStm.set_scandacs(stm.YDAC, rest_position)
				setTipParkingMode(self.tipParkingModeVar.get())
				self.systemTipParkingReadyVar.set(True)
				print 'System Ready for Corner Parking....'
				return
			print 'Preparing System for Corner Parking....'
			step = 10 * stm.mdac[stm.XDAC]
			dac_value = present_position 
			while dac_value >= rest_position:
				self.oStm.set_scandacs(stm.XDAC, dac_value)
				self.oStm.set_scandacs(stm.YDAC, dac_value)
				dac_value -= step
				time.sleep(delay / 1e3)
			print 'System Ready for Corner Parking....'
		if self.tipParkingModeVar.get() == TIP_PARKING_MODES['center']:
			rest_position = 0	# mV
			present_position = stm.cdac[stm.XDAC]	# mV
			if delay == 0:
				self.oStm.set_scandacs(stm.XDAC, rest_position)
				self.oStm.set_scandacs(stm.YDAC, rest_position)
				setTipParkingMode(self.tipParkingModeVar.get())
				self.systemTipParkingReadyVar.set(True)
				print 'System Ready for Center Parking....'
				return
			print 'Preparing System for Center Parking....'
			step = 10 * stm.mdac[stm.XDAC]
			dac_value = present_position 
			while dac_value <= rest_position:
				self.oStm.set_scandacs(stm.XDAC, dac_value)
				self.oStm.set_scandacs(stm.YDAC, dac_value)
				dac_value += step 
				if delay != 0:
					time.sleep(delay / 1e3)
			print 'System Ready for Center Parking....'
		setTipParkingMode(self.tipParkingModeVar.get())
		self.systemTipParkingReadyVar.set(True)
		return

	def initializeTipLocation(self):
		if self.tipParkingModeVar.get() == TIP_PARKING_MODES['center']:
			self.oDaq.initializeTipLocationToCenter()
		if self.tipParkingModeVar.get() == TIP_PARKING_MODES['corner']:
			self.oDaq.initializeTipLocationToCorner()
		return

	def restoreTipLocation(self):
		if self.tipParkingModeVar.get() == TIP_PARKING_MODES['center']:
			self.oDaq.restoreTipLocationToCenter()
		if self.tipParkingModeVar.get() == TIP_PARKING_MODES['corner']:
			self.oDaq.restoreTipLocationToCorner()
		return

	def BtnStartScanCB(self, event=None):
		"""
		KickStarts Scanning
		"""
		if self.checkImagePixelLimit () == False:
			return	

		''' Stop LIA auto-update while scanning in LDOS or LBH Mode '''
		nMode = self.DigitizationModeVar.get()
		if (nMode == self.LDOS_MODE) or (nMode == self.LBH_MODE):
			print 'Stopping XLIA Auto Update for the scan'
			if xlia.getXLIA_Status() == 1:		# XLIA is connected
	    		    self.oToolBar.oXLIA.stopAutoUpdater() 
		self.oWalker.vDisableWsGroup()
		self.oOffset.vDisableOsGroup()
		self.oToolBar.vDisableTbGroup()
		self.oMenuBar.vDisableMbGroup()
		self.vDisableSsGroup()
		self.oAppScanner.BtnStopScan.config(state=NORMAL)
		self.oImaging.vRefreshImageCanvas()
		self.vRenewAreaBox()		
		if self.bScanStatusVar.get() == NOTOVER:
		    return				
		self.bScanStatusVar.set(NOTOVER)
		self.oDaq = daq.daq(self)
		self.nRefreshVar.trace('w', self.oDaq.vRefreshDisplay)
		self.dicScanParam = self.oDaq.vGetScanParameters()
		self.oDaq.vCalculateDisplayRefreshlines()
		self.initializeTipLocation()
		#self.oDaq.vInitializeTipLocation()
		if self.diMovieSettings['bRec'] == True:
		    print 'Cinema Todangii'
		    self.vMovieRecording(self.oDaq)
		else:
		    print 'Cinema Todangit illa'
		    self.vSingleScanRecording(self.oDaq)
		self.restoreTipLocation()
		#self.oDaq.vRestoreTipLocation()
		self.vShowInfo(showonimage=True)
		self.vShowScaleInfo()
		self.bScanStatusVar.set(OVER)
		self.vEnableSsGroup()
		self.oMenuBar.vEnableMbGroup()
		self.oWalker.vEnableWsGroup()
		self.oOffset.vEnableOsGroup()
		self.oToolBar.vEnableTbGroup()
		''' Save Images/Movie '''
		if self.diMovieSettings['bRec'] == True:
			self.vSaveMoviePrompt ()
			self.diMovieSettings['bRec'] = False 
			self.bRecordMovie.set(False)
		else:
			self.vSaveImagesPrompt ()

		return

	def BtnStopScanCB(self, event=None):
		"""
		Halts Scanning
		"""
		print "Nirthu"
		self.bScanStatusVar.set(OVER)
		self.vEnableSsGroup()
		self.oMenuBar.vEnableMbGroup()
		self.oWalker.vEnableWsGroup()
		self.oOffset.vEnableOsGroup()
		self.oToolBar.vEnableTbGroup()
		return

	def vMovieRecording(self, oDaq):
		"""
		Movie Recording
		"""
		#self.bRecordMovie.set(True)
		nof = self.diMovieSettings['nof']
		print 'No. of Frames Selected = ', nof
		oDaq.vMovieScan(nof, self.NO_OF_CHANNELS)
		self.aafMovieFrames = oDaq.aafGetMovieData()
		return

	def vSaveMoviePrompt (self):
		if self.bAskEveryTime.get() == True:
			self.vSaveMovie()
		return

	def vSingleScanRecording(self, oDaq):
		"""
		Scan Recording
		"""
		oDaq.vSingleScan (self.NO_OF_CHANNELS)
		[self.afScanImageData, self.afRetImageData] = oDaq.afGetImageData()
		return

	def vSaveImagesPrompt (self):
		if self.bAskEveryTime.get() == True:
			self.vSaveImages()
		return

	def checkImagePixelLimit (self):
		imsize = self.nReadImageSize()[0]
		if self.NO_OF_CHANNELS > 1:
			if imsize > 550:
		    		tkMessageBox.showwarning('Image Size Limit', \
						'For LDOS mode scans, please keep max image size (pixels) <= 550')
				return False
		else:
			return True

        def nGetMaxStepSize(self):
		"""
		Change the permissible Step Size depending on area choice
			for small area : step =1    max step size =100 
			for large area : step =5    max step size =20	
		"""
		imsize = self.nReadImageSize()[0]
		self.checkImagePixelLimit ()
		ss = round(self.VoltageSpan / imsize, 1)

		if self.AreaVar.get() == self.SMALL_AREA:
		    if self.bXLAreaVar.get():
			#ss -= (ss%XL_GAIN)
			temp_xsa_steplist = self.xsa_steplist + [ss]
			temp_xsa_steplist.sort() 
			i = temp_xsa_steplist.index(ss)
			self.oAppScanner.EntryStepSize.configure(values=tuple(self.xsa_steplist[:i]))
		    else:
			temp_sa_steplist = self.sa_steplist + [ss]
			temp_sa_steplist.sort() 
			i = temp_sa_steplist.index(ss)
			self.oAppScanner.EntryStepSize.configure(values=tuple(self.sa_steplist[:i]))
		self.vShowInfo()
		return		
	
	def vSaveMovie(self):
		"""
		Saves Movie file
		"""
		filename = dialogs.SaveImageDialog('.'+dialogs.MOV_EXT,'Do you want to \n save movie frames?')
		if not filename:
		    return	
		fd = open(filename, 'w')
		cPickle.dump(self.aafMovieFrames, fd)
		cPickle.dump(self.dicScanParam, fd)
		fd.close()
		return

	def vDisplayImages(self, afScanImageData=None, afRetImageData=None):
		"""
		Displays Scan and Retrace Images
		"""
		self.oImaging.vCreateNewImages (self.dicScanParam)	
		try:
		    if self.bApplyMinMaxVar.get() == True:
                        afScanImageData = iprog.min_maxfilter(afScanImageData.copy(), SIGMA)
                    print "Opening Scan Image"
		    self.oImaging.vRenewScan(iprog.min_maxfilter(afScanImageData),self.dicScanParam)
                except:
                    pass
		try:
		    if self.bApplyMinMaxVar.get() == True:
		    	afRetImageData = iprog.min_maxfilter(afRetImageData.copy(), SIGMA)
		    print "Opening Ret Image"	
		    self.oImaging.vRenewRet(iprog.min_maxfilter(afRetImageData),self.dicScanParam)
		except:
		    self.oImaging.vInitializeRetImage(self.dicScanParam['ImageSize'])	
		    self.oImaging.afRetImageData = None		
		    pass
		self.vDisplayImageInfo()
		return

	def vDisplayImageInfo(self):
		"""
		Displays Scan Parameters
		"""
		try:
			self.vAdjustDirection()	
		except:
			pass
		try:
			self.vAdjustImageSize()
		except:
			pass
		try:
			self.vAdjustAreaChoice()
		except:
			pass
		#try:
		self.vAdjustXLAreaChoice()
		#except:
		#	pass
		try:
			self.vAdjustDelay()
		except:
			pass
		try:
			gain_list=self.gain_list
		except:
			pass
		try:
			pass
			#self.vAdjustDigitizationMode()	
			### commented as Image display during scans unknowingly
			### changes mode to CH which is not good while locking.
		except:
			pass
		try:	
			self.vAdjustGain(gain_list)
		except:
			pass
		try:				
			self.nGetMaxStepSize()	
		except:				
			pass			
		#try:
		self.vAdjustStepSize()
		#except:
		#	pass
		return
		
	def vAdjustDirection(self):
		"""
		Method : vAdjustDirection
			Displays opened image's Scan Direction

		Arguments :
			None

		Returns :
			None
		"""
		if self.dicScanParam['Direction']==self.HORIZONTAL:
			print 'Horizontal'
			self.oAppScanner.RBHorz.invoke()
			
		if self.dicScanParam['Direction']==self.VERTICAL:
			print 'Vertical'
			self.oAppScanner.RBVert.invoke()
		return
		
	def vAdjustXLAreaChoice(self):
		try:
			XLAreaChoice = self.dicScanParam['XLArea']
			self.bXLAreaVar.set(XLAreaChoice)
		except:
			self.bXLAreaVar.set(False)
		'''
		if self.bXLAreaVar.get():
                    self.vSetXLAreaHandler()
                else:
                    self.vClearXLAreaHandler()
                '''
		return

	def vAdjustImageSize(self):
		"""
		Displays opened image's Size
		"""
		while int(self.oAppScanner.EntryImageSize.get()) < self.dicScanParam['ImageSize'][0]:
			self.oAppScanner.EntryImageSize.invoke('buttonup')

		while int(self.oAppScanner.EntryImageSize.get()) > self.dicScanParam['ImageSize'][0]:
			self.oAppScanner.EntryImageSize.invoke('buttondown')
		return

	def vAdjustAreaChoice(self):
		"""
		Adjusts Scan Area choice according to the opened image
		"""
		if self.dicScanParam['AreaChoice']==self.SMALL_AREA:
			self.AreaVar.set(self.SMALL_AREA) 
		if self.dicScanParam['AreaChoice']==self.LARGE_AREA:
			self.AreaVar.set(self.LARGE_AREA)
		return

	def vAdjustStepSize(self):
		"""
		Displays opened image's Step Size
		"""
		new_stepsize = self.dicScanParam['StepSize'][0]
		if self.bXLAreaVar.get():
		    new_stepsize *= 10	
		while float(self.oAppScanner.EntryStepSize.get()) < new_stepsize:
		    self.oAppScanner.EntryStepSize.invoke('buttonup')
		    self.MainMaster.update()
		return

	def vAdjustDelay (self):
		"""
		Displays opened image's Step Delay
		"""
		if self.dicScanparam.haskey ('LIA_Status'):
		    if self.dicScanparam ['LIA_Status'] == True:
			step_delay_list = self.lia_delay_list
		    else:
			step_delay_list = self.delay_list
		else:
		    step_delay_list = self.delay_list
		for i in range(len(step_delay_list)):
			if int(self.oAppScanner.EntryDelay.get()) > int(self.dicScanParam['Delay']):
				self.oAppScanner.EntryDelay.invoke('buttondown')
			if int(self.oAppScanner.EntryDelay.get()) < int(self.dicScanParam['Delay']):
				self.oAppScanner.EntryDelay.invoke('buttonup')
		return
		
	def vAdjustGain(self, gain_list):
		"""
		Displays opened image's ADC Gain
		"""
		for i in range(len(gain_list)):
			if int(self.oAppScanner.EntryGain.get()) < int(self.dicScanParam['Gain']):
				self.oAppScanner.EntryGain.invoke('buttonup')
			if int(self.oAppScanner.EntryGain.get()) > int(self.dicScanParam['Gain']):
				self.oAppScanner.EntryGain.invoke('buttondown')
		return

	def vAdjustDigitizationMode(self):
		"""
		Displays opened image's Digitization Mode CC/CH
		"""
		if self.dicScanParam['DigitizationMode']==self.TCMODE:
			self.oAppScanner.RBTC.invoke()
		if self.dicScanParam['DigitizationMode']==self.ZMODE:
			self.oAppScanner.RBZ.invoke()
		return
	 


	################# CALLED FROM TOOLBAR #####################
	def vSetScanArea(self):
		"""
		Sets  Scan Area Large / Small
		"""
		bApplyVar = BooleanVar()
		bApplyVar.set(False)
		ScanAreaDialog(self.MainMaster, self.AreaVar, self.bXLAreaVar, bApplyVar)
		#if not bApplyVar.get():
		#    return
		if self.AreaVar.get()== 6:
			self.vClearXLAreaHandler()
		if self.bXLAreaVar.get():
			self.vSetXLAreaHandler()
		else:
			self.vClearXLAreaHandler()
		self.nGetMaxStepSize()
		return

	def vSaveImages(self, afScanImageData=None, afRetImageData=None, dicScanParam=None):
		"""
		Save nanoREV Image dialog		
		"""
		if not self.oImaging.bImagePresentVar.get():
		    tkMessageBox.showwarning('Blank','Oops !! No images on Display')
		    return
		filename = dialogs.SaveImageDialog()
		if not filename:
		    return
		try:
		    fd = open(filename, 'w')
		except:
		    tkMessageBox.showerror('Cannot Create File','Please check if you have permissions \n or other filesystem error')
		    return
		
		if (afScanImageData is not None) or (afRetImageData is not None):
		    print 'Idum onde...'
		    cPickle.dump(afScanImageData, fd)
		    cPickle.dump(afRetImageData, fd)
		    try:
			if dicScanParam:
			    cPickle.dump(dicScanParam, fd)		
			else:
			    cPickle.dump(self.dicScanParam, fd)		
		    except:
			pass
		    fd.close()
		    return

		if self.afScanImageData is not None:
		    cPickle.dump(self.afScanImageData, fd)
		if self.afRetImageData is not None:
		    cPickle.dump(self.afRetImageData, fd)
		if self.dicScanParam is not None:
		    cPickle.dump(self.dicScanParam, fd)
		fd.close()
		return

	def vOpenImages(self):
		"""
		Open  Images dialog
		"""
		filename = dialogs.OpenImageDialog()
		if not filename:
		    return
		[self.afScanImageData, self.afRetImageData, self.dicScanParam, self.sFileType] = import_.aafReadImageFile(filename)
		self.oImaging.sGetFileType(self.sFileType)
		print filename
		#Scan Parameters Display
		print self.dicScanParam
		if self.dicScanParam.has_key('XLArea'):
		    pass
		else:
		    self.dicScanParam['XLArea'] = False
		self.vDisplayImages(self.afScanImageData, self.afRetImageData)
		### Show Area Info at Left Top Corner ###
	   	try:
		    self.vShowInfo(self.dicScanParam['ImageSize'][0], \
					self.dicScanParam['StepSize'][0], \
					self.dicScanParam['Delay'], \
					showonimage=True, \
					bXLArea=self.dicScanParam['XLArea'], \
					)
		except:
		    pass
		#### Show Scale Info on the Color Strip ####
		self.vShowScaleInfo()
		return

	def vShowScaleInfo(self):
	    """
	    Displays the minma and maxima height values on the LUT Color Strip on the right 
	    according to the image data in Retrace Window
	    """
	    afNormImageData = self.afCalculateNormalizedImageData()  
	    mean, min, max, units = self.afCalculateScale(afNormImageData)
	    zPolarity = getZ_Polarity()
	    if zPolarity == 'Positive':
		    self.oImaging.vShowScale(mean, min, max, units)
	    else:
		    self.oImaging.vShowScale(mean, max, min, units)
	    return

	def afCalculateNormalizedImageData(self, SR=0):
	    if not SR:
	        afNormImageData = self.oImaging.afRetImageData/self.dicScanParam['Gain']
	    else:
	        afNormImageData = self.oImaging.afScanImageData/self.dicScanParam['Gain']
	    ### Actual Z-Piezo Movement is XL_GAIN times Zpi recorded through ADC ### 
	    if self.dicScanParam['DigitizationMode'] == self.ZMODE:
		fHVAGain = fGetHVAGain()
	    	afNormImageData *= fHVAGain  
	    return afNormImageData


	def vPlayMovie(self):
		"""
		Play Movie files dialog
		"""
		filename = dialogs.OpenImageDialog(ext=dialogs.MOV_EXT)
		if not filename:
		    return	
		fd = open(filename)
		aafFrames = cPickle.load(fd)
		self.dicScanParam = cPickle.load(fd)
		print  self.dicScanParam	
		self.vDisplayImageInfo()
		fd.close()
		nof = len(aafFrames)
		FRAME_DELAY = self.diMovieSettings['framedelay']
		self.MainMaster.update()
		for i in range(nof):
		    self.vDisplayImages(aafFrames[i][0], aafFrames[i][1])
		    self.MainMaster.update()
		    time.sleep(FRAME_DELAY)
		return

	def getCouplingStatus(self):
	    status = self.oMenuBar.acCoupledScanningVar.get()
	    return status


	def getPreScanSetupDelay(self):
	    delay = self.oMenuBar.preScanSetupDelayVar.get()	# in ms
	    return delay


	def vSetXLAreaHandler(self):
	    """
	    The scan voltages are jacked up by XL_GAIN factor.
	    """
	    self.oStm.ela_on()
	    return

	def vClearXLAreaHandler(self):
	    """
	    Disables XL Area Scan Mode.
	    """
	    self.oStm.ela_off()
	    return

	def vSetGainHandler(self, nGain):
		"""
		Set Adc gain
		"""
		self.oStm.set_gain(nGain)
		return

	def vSetDigitizationModeHandler(self, nMode):
		"""
		Sets Digitization Mode
		"""
		if nMode == self.TCMODE:
			self.oStm.set_TCmode()
			#self.oStm.hold_on()
			#self.vWriteAndSetGain(2)
			#self.vWriteAndSetGain(1)
			self.NO_OF_CHANNELS = 1
			self.bSimulScanVar.set (False)
			self.LIA_StatusVar.set (False)
			self.CHANNEL_NAMES = ['CH Mode']
			self.LIA_StatusVar.set (False)
			self.oStm.disableBiasModulation()
			self.oStm.disableZ_Modulation()
			#print 'Digitization Mode: TC'

		if nMode == self.ZMODE:
			self.oStm.set_Zmode()
			self.oStm.hold_off()
			#self.vWriteAndSetGain(2)
			#self.vWriteAndSetGain(1)
			self.NO_OF_CHANNELS = 1
			self.bSimulScanVar.set (False)
			self.LIA_StatusVar.set (False)
			self.CHANNEL_NAMES = ['CC Mode']
			self.LIA_StatusVar.set (False)
			self.oStm.disableBiasModulation()
			self.oStm.disableZ_Modulation()
			#print 'Digitization Mode: Z'

		if nMode == self.LDOS_MODE:
			self.oStm.set_Zmode()
			self.oStm.hold_off()
			#self.vWriteAndSetGain(2)
			#self.vWriteAndSetGain(1)
			self.NO_OF_CHANNELS = 3
			self.bSimulScanVar.set (True)
			self.LIA_StatusVar.set (True)
			self.CHANNEL_NAMES = ['Topography', 'LDOS In-Phase', 'LDOS Quad-Phase']
			self.LIA_StatusVar.set (True)
			self.oStm.enableBiasModulation()
			self.oStm.disableZ_Modulation()
			#print 'Digitization Mode: LDOS'

		if nMode == self.LBH_MODE:
			self.oStm.set_Zmode()
			self.oStm.hold_off()
			self.NO_OF_CHANNELS = 3
			self.bSimulScanVar.set (True)
			self.LIA_StatusVar.set (True)
			self.CHANNEL_NAMES = ['Topography', 'LBH In-Phase', 'LBH Quad-Phase']
			self.LIA_StatusVar.set (True)
			self.oStm.disableBiasModulation()
			self.oStm.enableZ_Modulation()
			#print 'Digitization Mode: LBH'
		return

	def vSetXScanHandler(self, nXScan):
		"""
		Sets X scan DAC
		"""
		self.oStm.set_scanx(nXScan)

	def vSetYScanHandler(self, nYScan):
		"""
		Sets Y scan DAC			
		"""
		self.oStm.set_scany(nYScan)

	def vDisableSsGroup(self):
		"""
		Disable ScannerGui widgets
		"""
		self.oAppScanner.RBHorz.config(state=DISABLED)
		self.oAppScanner.RBVert.config(state=DISABLED)
		self.oAppScanner.RBTC.config(state=DISABLED)
		self.oAppScanner.RBZ.config(state=DISABLED)
		self.oAppScanner.RB_LDOS.config(state=DISABLED)
		self.oAppScanner.RB_LBH.config(state=DISABLED)
		self.oAppScanner.EntryImageSize.config(state=DISABLED)
		self.oAppScanner.EntryDelay.config(state=DISABLED)
		self.oAppScanner.EntryStepSize.config(state=DISABLED)
		self.oAppScanner.EntryGain.config(state=DISABLED)
		self.oAppScanner.BtnStartScan.config(state=DISABLED)
		self.oAppScanner.BtnStopScan.config(state=DISABLED)
		return

	def vEnableSsGroup(self):
		"""
		Enables ScannerGui widgets
		"""
		self.oAppScanner.RBHorz.config(state=NORMAL)
		self.oAppScanner.RBVert.config(state=NORMAL)
		self.oAppScanner.RBTC.config(state=NORMAL)
		self.oAppScanner.RBZ.config(state=NORMAL)
		self.oAppScanner.RB_LDOS.config(state=NORMAL)
		self.oAppScanner.RB_LBH.config(state=NORMAL)
		self.oAppScanner.EntryImageSize.config(state=NORMAL)
		self.oAppScanner.EntryDelay.config(state=NORMAL)
		self.oAppScanner.EntryStepSize.config(state=NORMAL)
		self.oAppScanner.EntryGain.config(state=NORMAL)
		self.oAppScanner.BtnStartScan.config(state=NORMAL)
		self.oAppScanner.BtnStopScan.config(state=NORMAL)
		return
	
	def __vConfigureKBShortcuts(self):
	    """
	    Keyboard Shortcuts added
	    """
	    self.MainMaster.bind('<Control-t>', self.BtnStartScanCB)
	    self.MainMaster.bind('<Control-p>', self.BtnStopScanCB)
	    self.MainMaster.bind('<Control-k>', self.oAppScanner.RBTC.invoke)
	    self.MainMaster.bind('<Control-h>', self.oAppScanner.RBZ.invoke)
	    return

class ScanAreaDialog(tkSimpleDialog.Dialog):
    """
    Selection between different area ranges
    """
    def __init__(self, master, AreaVar, bXLAreaVar, bApplyVar):
	self.AreaVar = AreaVar
	self.bXLAreaVar = bXLAreaVar
	self.bApplyVar = bApplyVar
	self.arAreaRanges = arGetAreaRanges()
	self.SMALL_AREA = 6
	tkSimpleDialog.Dialog.__init__(self, master, 'Scan Area Settings')
	#dialogs.GridDialog.__init__(self, master, 'Scan Area Settings')
	return

    def body(self, master):
	self.master = master
	Label(text='Scan Area Selection')
	self.RBSmallArea = Radiobutton(self.master, \
				text='Area ( ' + \
				str( '%3.3f' % self.arAreaRanges[0][0]) + '-' + \
				str('%3.3f' % self.arAreaRanges[0][1]) + ' nm )'\
				)
	self.RBSmallArea.pack()
	'''
	self.RBLargeArea = Radiobutton(self.master, \
				text='Large Area ( '+str(self.arAreaRanges[1][0])+'-'+str(self.arAreaRanges[1][1])+' nm )', \
				# selectcolor='blue'
				)
	self.RBLargeArea.pack(fill=BOTH)
	'''
	xla_min = self.arAreaRanges[0][0] * XL_GAIN
	xla_max = self.arAreaRanges[1][1] * XL_GAIN
	self.CBXLargeArea = Checkbutton(self.master, \
				text='XL Area   ( ' + \
				str('%3.3f' % xla_min) + '-' + \
				str('%3.3f' % xla_max) + ' nm )' \
				)
	self.CBXLargeArea.pack()
	self._configureCB()
	return
	
    def _configureCB(self):
	self.RBSmallArea.configure(variable=self.AreaVar, \
				value=self.SMALL_AREA)
	#self.RBLargeArea.configure(variable=self.AreaVar, \
	#			value=self.LARGE_AREA)
	self.CBXLargeArea.configure(variable=self.bXLAreaVar)
	return
	
class MovieSettingsDialog:
    def __init__ (self, master, oScanner):
	self.oScanner = oScanner
	self.master = master
	self.master.title ('Movie Settings')
	self.diMovieSettings = self.oScanner.diMovieSettings
	self._create_icons ()
	self.body ()
	self.movieFilename = None
	return

    def _create_icons(self):
	global playim, recim, quitim
	playim		= ImageTk.PhotoImage(file=play_iconfile)
	recim		= ImageTk.PhotoImage(file=rec_iconfile)
	quitim		= ImageTk.PhotoImage(file=quit_iconfile)
	return

    def body(self):
	LF_Action = LabelFrame (self.master)
	LF_Action.grid (row = 0, column = 0)
	BtnPlay = Button(LF_Action, compound=TOP, \
			text='Play', image=playim, \
			font=btn_font_type,
			command=self.vPlayCB)
	BtnPlay.grid(row=0,column=0)
	BtnRecord = Button(LF_Action, compound=TOP, \
			text='Rec', image=recim, \
			font=btn_font_type,
			command=self.vRecordCB)
	BtnRecord.grid(row=0,column=1)
	'''
	BtnQuit = Button(LF_Action, compound=TOP, \
			text='Quit', image=quitim, \
			font=btn_font_type,
			command=self.cancel)
	BtnQuit.grid(row=0,column=2)
	'''
	LF_Processing = LabelFrame (self.master, \
					padx = 2, pady = 2, \
					text = 'Split Movie')
	LF_Processing.grid (row = 1, column = 0)
	self.btnBrowseMovie = Button (LF_Processing, \
					fg = 'blue', \
					command = self.browseMovieCB, \
					text = 'Browse')
	self.btnBrowseMovie.grid (row = 0, column = 0, sticky = 'news')
	self.btnSplitMovie = Button (LF_Processing, \
					fg = 'red', \
					command = self.splitMovieCB, \
					text = 'Split ')
	self.btnSplitMovie.grid (row = 0, column = 1, sticky = 'news')

	self.SplitStatusBar = tkStatusBar.StatusBar (LF_Processing, \
							width = 150, \
							height = 20, \
							bg = 'white')
	self.SplitStatusBar.grid (row = 1, column=0, columnspan = 2, sticky = 'w')
	self.SplitStatusBar.minimum (0)
	self.SplitStatusBar.maximum (10)
	return

    def vPlayCB(self):
	fd = tkSimpleDialog.askfloat('Frame Delay', \
				'Enter Frame Delay (in s)', \
				initialvalue=1, \
				minvalue=0.1,\
				maxvalue=10)
	self.diMovieSettings['framedelay'] = fd 
	self.diMovieSettings['bPlay'] = True 
	self.diMovieSettings['bRec'] = False
	self.oScanner.vPlayMovie ()
	return

    def vRecordCB(self):
	nof = tkSimpleDialog.askinteger('Frame Count', \
				'Enter no. of frames [2-32]', \
				initialvalue=2, \
				minvalue=2,\
				maxvalue=100)
	self.diMovieSettings['nof'] = nof
	self.diMovieSettings['bRec'] = True 
	self.diMovieSettings['bPlay'] = False 
	if self.diMovieSettings['bRec'] == True:
	    if self.diMovieSettings['nof'] == None:
		return		 
	    tkMessageBox.showinfo('Record Movie',\
					'Click on Start Scan to start recording !!', \
					parent = self.master)
	return

    def browseMovieCB (self):
	filename = dialogs.OpenImageDialog (ext = dialogs.MOV_EXT, parent = self.master)
	if not filename:
	    return
	self.movieFilename = filename
	tkMessageBox.showinfo('Split', \
				'Now Please click on \'Split\'...',\
				parent = self.master)
	self.SplitStatusBar.value (0)
	return

    def splitMovieCB (self):
	if self.movieFilename == None:
		tkMessageBox.showwarning('File not selected', \
					'Please browse the movie file to be split !!',\
					parent = self.master)
		return
	self.splitMovieToFrames (self.movieFilename)
	tkMessageBox.showinfo('Success', \
				'Movie file\n' + self.movieFilename + '\nsuccessfully split !!',\
				parent = self.master)
	return

    def splitMovieToFrames (self, fileName):
	movieFrames, dicMovieParam = self.readMovieFile (fileName)
	self.SplitStatusBar.maximum (len (movieFrames))
	noOfFrames = 0
	frameFileName = os.path.splitext (fileName) [0] + '_'
	for frame in movieFrames:
		print 'Saving frame...', (noOfFrames + 1) 
		self.saveSplitMovieFrames (frame [0], frame [1], dicMovieParam, \
					(frameFileName + str (noOfFrames)) )
		noOfFrames += 1
		self.SplitStatusBar.value (noOfFrames)
	return

    def saveSplitMovieFrames (self, scanImage, retImage, dicScanParam, fileName):
	try:
		fd = open (fileName + '.npic', 'w')
	except:
		print 'Write permission denied', fileName
		tkMessageBox.showerror('Write Permission Denied', \
					'Please move the movie file to a writable folder',\
					parent = self.master)
		return

	cPickle.dump (scanImage, fd)
	cPickle.dump (retImage, fd)
	cPickle.dump (dicScanParam, fd)
	fd.close ()
	return

    def readMovieFile (self, movieFileName):
	fd = open (movieFileName)
	movieFrames = cPickle.load (fd)
	dicMovieParam = cPickle.load (fd)
	fd.close ()
	print 'No. of frames: ', len (movieFrames)
	print dicMovieParam
	return movieFrames, dicMovieParam 

    def closeAppMovie (self):
	self.master.destroy ()
	return

class TipParkingModesDialog(dialogs.GridDialog):
    def __init__(self, master, tipParkingMode):
	self.tipParkingMode = tipParkingMode
	self.tipParkingModeLocalVar = StringVar()
	dialogs.GridDialog.__init__(self, master, 'Tip Parking Modes')
	return

    def body(self, master):
	self._mainBody(master)
	self._dialogButtonBody(master)
	self._configureCB()
	return

    def _mainBody(self, master):
	mainBody = LabelFrame(master)
	mainBody.grid(row=0, column=0, sticky = 'news')

	self.RB_Center = Radiobutton(mainBody, \
				text='Center (middle of X & Y spans)')#, \
				#selectcolor='blue')	
	self.RB_Center.grid(row = 0, column = 0, sticky = 'news')	
	self.RB_Corner = Radiobutton(mainBody, \
				text='Corner (top-left corner of scan)')#, \
				#selectcolor='red')
	self.RB_Corner.grid(row = 1, column = 0, sticky = 'news')	
	return

    def _dialogButtonBody(self, master):
	dialogButtonBody = LabelFrame(master)
	dialogButtonBody.grid(row = 1, column = 0, sticky = 'news')
	self.BtnApply = Button(dialogButtonBody, text = 'Apply', width = 10, command = self.okCB)
	self.BtnApply.grid(row = 0, column = 0, padx = 3, pady = 3, sticky = 'news')
	self.BtnCancel = Button(dialogButtonBody, text='Cancel', width = 10, command = self.cancelCB)
	self.BtnCancel.grid(row = 0, column = 1, padx = 3, pady = 3, sticky = 'news')
	return

    def _configureCB(self):
	self.tipParkingModeLocalVar.set(self.tipParkingMode.get())
	self.RB_Center.configure(variable = self.tipParkingModeLocalVar, \
				value = TIP_PARKING_MODES['center'])
	self.RB_Corner.configure(variable = self.tipParkingModeLocalVar, \
				value = TIP_PARKING_MODES['corner'])
	#self.BtnApply.config()
	#self.BtnCancel.config()
	return

    def apply(self):
	pass

    def okCB(self):
	self.tipParkingMode.set(self.tipParkingModeLocalVar.get())
	self.ok()
	return

    def cancelCB(self):
	self.cancel()
	return

class FeedbackControlDialog:
    SET_HOLD = 1
    CLR_HOLD = 2
    RESET_ON = 3
    RESET_OFF = 4

    def __init__(self, master, oStm):
	self.master = master
	self.oStm = oStm
	self.nHoldVar = IntVar()
	self.nResetVar = IntVar()
	self.body()
	return
		
    def body(self):
	row = 0
	self.LFPI = LabelFrame(self.master,text='FB Settings')
	self.LFPI.grid(row=row,column=0, padx=3, pady=3, sticky=N+E+W+S,columnspan=2)
	Label(self.LFPI, text='P Gain (kOhms)').grid(row=0, column=0, sticky=W)
	self.EntryP = tkValidatingEntry.FloatEntry(self.LFPI, \
					bg='white', \
					justify=LEFT, width=12)
	self.EntryP.grid(row=0, column=1, sticky=W)
	self.LblP = Label(self.LFPI, text='- x')
	self.LblP.grid(row=1, column=1, sticky=W)
	Label(self.LFPI, text='Time K. (kOhms)').grid(row=2, column=0, sticky=W)
	self.EntryI = tkValidatingEntry.FloatEntry(self.LFPI, \
					bg='white', \
					justify=LEFT, width=12)
	self.EntryI.grid(row=2, column=1, sticky=W)
	self.LblTimeK = Label(self.LFPI, text='- ms')
	self.LblTimeK.grid(row=3, column=1, sticky=W)

	row += 1
	self.LFFeedBack = LabelFrame(self.master,text='FeedBack Control')
	self.LFFeedBack.grid(row=row,column=0, padx=3, pady=3,sticky=N+E+W+S,columnspan=2)
	self.RBFeedBackOn = Radiobutton(self.LFFeedBack, \
				text='Feedback On', \
				)	
	self.RBFeedBackOn.grid(row=0, column=0,sticky=W)
	self.RBFeedBackOff = Radiobutton(self.LFFeedBack, \
				text='Feedback Off', \
				)	
	self.RBFeedBackOff.grid(row=0, column=1, sticky=E)

	row += 1
	self.LFResetCtrl = LabelFrame(self.master,text='Reset Control')
	self.LFResetCtrl.grid(row=row,column=0, padx=3, pady=3,sticky=N+E+W+S,columnspan=2)
	self.RBResetOn = Radiobutton(self.LFResetCtrl, \
				text='Reset FB      ', \
				)	
	self.RBResetOn.grid(row=0, column=0,sticky=W)
	self.RBResetOff = Radiobutton(self.LFResetCtrl, \
				text='Normal FB      ', \
				)	
	self.RBResetOff.grid(row=0, column=1, sticky=E)

	self._configureCB()
	self.nResetVar.set(self.RESET_OFF)
	self.nHoldVar.set(self.CLR_HOLD)
	return

    def _configureCB(self):
	self.RBFeedBackOn.configure(command=self.oStm.hold_off, \
				variable = self.nHoldVar, \
				value=self.CLR_HOLD)
	self.RBFeedBackOff.configure(command=self.oStm.hold_on, \
				variable = self.nHoldVar, \
				value=self.SET_HOLD)
	self.RBResetOn.configure(command=self.oStm.reset_on, \
				variable = self.nResetVar, \
				value=self.RESET_ON)
	self.RBResetOff.configure(command=self.oStm.reset_off, \
				variable = self.nResetVar, \
				value=self.RESET_OFF)

	GAIN_POT_MAX = int(stm.POT_VALUES[stm.GAIN_POT] / 1e3)		# in kOhms
 	self.EntryP.limits([0, GAIN_POT_MAX])
 	self.EntryP.bind('<Return>', self.setPCB)
 	self.EntryP.bind('<Key>', self.vClearHighlightP)
	TIMEK_POT_MAX = int(stm.POT_VALUES[stm.TIMEK_POT] / 1e3)	# in kOhms
 	self.EntryI.limits([0, TIMEK_POT_MAX])
 	self.EntryI.bind('<Return>', self.setICB)
 	self.EntryI.bind('<Key>', self.vClearHighlightI)
	self.populatePotEntries()
	return


    def populatePotEntries(self):
	prevPotValues = stm.readPotLog()
	pval = prevPotValues[stm.GAIN_POT] / 1e3 	# in kOhms
	ival = prevPotValues[stm.TIMEK_POT] / 1e3 	# in kOhms
 	self.EntryP.delete(0, END)
	pval = round(pval, 1)
 	self.EntryP.insert(0, pval)
	self.showP(pval)
 	self.EntryI.delete(0, END)
	pval = round(ival, 1)
 	self.EntryI.insert(0, ival)
	self.showTimeK(ival)
	return


    def setPCB(self, event):
 	if self.EntryP.get() == '':
	    return
 	self.EntryP.configure(bg='yellow')
 	ko = float(self.EntryP.get())
	self.setP(ko)
	self.showP(ko)
	return


    def setP(self, ko):
	#print 'P Gain: ', ko, 'kOhms'
	self.oStm.set_pot(stm.GAIN_POT, (ko * 1e3))
	return


    def setICB(self, event):
 	if self.EntryI.get() == '':
	    return
 	self.EntryI.configure(bg='yellow')
 	ko = float(self.EntryI.get())
	self.setI(ko)
	self.showTimeK(ko)
	return


    def setI(self, ko):
	#print 'Time K: ', ko, 'kOhms'
	self.oStm.set_pot(stm.TIMEK_POT, (ko * 1e3))
	return


    def showTimeK(self, ko):
	capI = 0.1e-6	# 0.1 uF
	timeK = (ko * 1e3 * capI)
	timeKms = timeK * 1e3
	textt = '%.1f' % timeKms 
	textf = '%.1f' % (1 / timeK)
	text = textt + ' ms, ' + textf + ' Hz'
	self.LblTimeK.config(text=text)
	return


    def showP(self, ko):
	gain = (ko / 10.0)
	textg = '%.1f' % gain 
	text = textg + ' x'
	self.LblP.config(text=text)
	return


    def vClearHighlightP(self, event):
 	self.EntryP.configure(bg='white')
	return


    def vClearHighlightI(self, event):
 	self.EntryI.configure(bg='white')
	return


    def closeAppFB(self):
	self.master.destroy()
			
 
######### Only for Testing ###########
if __name__ == "__main__":
	scanner()
