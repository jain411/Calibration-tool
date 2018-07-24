####################
#   Offset Class   #
####################

import numpy, os, threading, time
from Tkinter import *
import tkMessageBox, tkSimpleDialog
from PIL import ImageTk

import lib.tkValidatingEntry as tkValidatingEntry
import app_offset
import apps.dialogs as dialogs
import lib.stm7 as stm 
import scanner
import navigator

__DEBUG__ 	= True
XL_GAIN		= 10.0
OFFSET_SPAN	= 20000.0 * XL_GAIN
MAX_XOFFSET	= 10000.0 * XL_GAIN
MIN_XOFFSET	= -10000.0 * XL_GAIN
MAX_YOFFSET	= 10000.0 * XL_GAIN
MIN_YOFFSET	= -10000.0 * XL_GAIN
MAX_ZOFFSET	= 10000.0
MIN_ZOFFSET	= -10000.0
DAC_RESOLUTION  = stm.ZDAC_RESOLUTION 
OXDAC_RESOLUTION  = 5 * XL_GAIN
OYDAC_RESOLUTION  =  5 * XL_GAIN

"""
DAC Channels
"""
OXDAC   = 4			
XDAC	= 0		
OYDAC	= 5		
YDAC	= 1		
OZDAC	= 2		
BIASDAC = 3		
TC_SETP_DAC = 6

WINDOWSIZE = 10		
NP         = 20		
R          = 2		

logpath     = os.path.join(os.curdir,'log')	
xlog        = os.path.join(logpath, 'xlog.dat')
ylog        = os.path.join(logpath, 'ylog.dat')	
zlog        = os.path.join(logpath, 'zlog.dat')
globlogfile = os.path.join(logpath, 'glob.dat')
initlogfile = os.path.join(logpath, 'initlog.dat')			
tclogfile   = os.path.join(logpath, 'tcsetpoint.dat')			
tcfont = ("Helvetica", 24, 'bold')

iconpath     = os.path.join('apps','icons')
dialpot_iconfile = os.path.join(iconpath,'dialpot.png') 

def fGetZoffsetGain():
    try:
	dicGlobParam = scanner.dicReadGlobalParam()
    except:
	print 'Unable to read global Settings'
	return 10.0
    return dicGlobParam['ZoffsetGain']

if __DEBUG__ == True:
	from Tkinter import *

def offset(f=None, oStm=None):
	"""
	Creates Offset Interface
	"""
	oAppOffset = app_offset.app_offset()
	oAppOffset.createOSwindow(f)
	oOffset = Offset(oAppOffset, oStm)
	return oOffset

class Offset:

	nXoffset = None
	nYoffset = None
	nZoffset = None
	arrPath = []

	def __init__(self, oAppOffset, oStm):
		"""
		Class Contructor : Offset
		"""
		self.oAppOffset = oAppOffset
		self.oStm = oStm
		self.vLoadPreviousOffsets()
		self.bMotionOverVar = BooleanVar()
		self.bMotionOverVar.set(True)
		self.bDisplayZpiVar = BooleanVar()
		self.bDisplayZpiVar.set(False)
		self.bRefreshZpiVar = BooleanVar()
		self.bRefreshZpiVar.set(False)
		self.enableGlobalTipLocatorVar = BooleanVar()
		self.abortCorrectZ_Var = BooleanVar()
		self.abortCorrectZ_Var.set(True)
		self.enableGlobalTipLocatorVar.set (False)
		self._configureCB()
		if self.oStm.fd != None:
                    self._initOffsetParameters()
		self.MV2PIXELS = OFFSET_SPAN / self.oAppOffset.w
		self.ResetVar=BooleanVar()
		self.ResetVar.set(0)
		self.HoldVar=BooleanVar()
		self.HoldVar.set(0) 
		[x, y] = self.mv2pix(self.nXoffset, self.nYoffset, self.oAppOffset.w/2, self.oAppOffset.h/2)
		for i in range(2):		
			self.arrPath.append([x,y])
		self.vShowMarker(self.nXoffset, self.nYoffset)
		self.nNavigatorInstance = 0
		self.winNavigator = None
		self.bInitInstanceVar = BooleanVar()
		self.bInitInstanceVar.set(False)
		self.bApplyVar = BooleanVar()
		self.bApplyVar.set(False)
		#self.Lock = threading.Lock()
		return
		
	def _configureCB(self):
		"""
		Attaches Callbacks to OffsetGui widgets 
		"""		
		self.oAppOffset.EntryXoffset.bind('<Return>', self.vSetXoffsetCB)
		self.oAppOffset.EntryYoffset.bind('<Return>', self.vSetYoffsetCB)
		self.oAppOffset.EntryZoffset.bind('<Return>', self.vSetZoffsetCB)
		self.oAppOffset.EntryZoffset.limits([MIN_ZOFFSET, MAX_ZOFFSET])
		self.oAppOffset.BtnCorrectZoffset.configure(command=self.vCorrectZoffsetCB)
		self.oAppOffset.BtnStopCorrectZoffset.configure(command=self.stopCorrectZoffsetCB)
		self.oAppOffset.BtnResetTipLocation.configure(command=self.vResetTipLocation)
		self.oAppOffset.CBEnableGlobalTipLocator.configure (\
						command = self.enableGlobalTipLocator, \
						variable = self.enableGlobalTipLocatorVar)
		#self.oAppOffset.CanTipLocation.bind('<Button-1>', self.vSetTipLocationCB)
		self.oAppOffset.BtnNavigator.configure(command=self.vNavigatorCB)
		self.oAppOffset.CBFBMonitor.configure(variable=self.bDisplayZpiVar)
		self.oAppOffset.LblDisplayZpi.bind('<Enter>', self.vRefreshZpiDisplay)
		self.oAppOffset.LblDisplayZpi.bind('<Leave>', self.vFreezeZpiDisplay)
		self.abortCorrectZ_Var.trace('w', self.stopCorrectZoffset)
		return

	def _initOffsetParameters(self):
		"""
		Initializes X,Y and Z offsets 
		"""	
		self.vWriteXoffset(self.nXoffset)
		self.vSetXoffsetHandler(self.nXoffset)
		self.vWriteYoffset(self.nYoffset)
		self.vSetYoffsetHandler(-self.nYoffset)
		self.vWriteZoffset(self.nZoffset)
		self.vSetZoffsetHandler(self.nZoffset)
		return

	def vLoadPreviousOffsets(self):
		"""
		Loads previous X,Y, and Z offsets
		"""
		f = open(xlog)
		self.nXoffset = float(f.read()) * XL_GAIN 
		f.close()
		f = open(ylog)
		self.nYoffset = -1.0 * float(f.read()) * XL_GAIN
		f.close()
		f = open(zlog)
		self.nZoffset = float(f.read())
		f.close()
		return

	def mv2pix(self, xoff=0, yoff=0, xorig=0 , yorig=0): 
		"""
		Converts X/Y offsets to window dimensions 
		"""
		x = xorig + xoff/self.MV2PIXELS
		y = yorig - yoff/self.MV2PIXELS	
		return [x, y]

	def pix2mv(self, x=0, y=0): 
		"""
		Converts offfset window coordinates to x/y offsets
		"""
		xoff = (x - self.oAppOffset.w/2) * self.MV2PIXELS
		if xoff > MAX_XOFFSET:
		    xoff = MAX_XOFFSET
		yoff = (y - self.oAppOffset.h/2) * self.MV2PIXELS
		if yoff > MAX_YOFFSET:
		    yoff = MAX_YOFFSET
		return [xoff, yoff]

	def vGetCore(self, oStm):
		"""
		Links Stm object to Offset class
		"""
		self.oStm = oStm
		return

	def vGetScanner(self, oScanner):
		"""
		Links Scanner object to Offset class
		"""
		self.oScanner = oScanner
		return

	def vGetMainMaster(self, MainMaster):
		"""
		Links MainWindow to Offset class
		"""
		self.MainMaster = MainMaster
		self.__vConfigureKBShortcuts()
		return

	def vGetWalker(self,oWalker):
		"""
		Links Walker to Offset class			
		"""
		self.oWalker = oWalker
		return

	def vGetToolBar(self, oToolBar):
		"""
		Links Toolbar to Offset class			
		"""
		self.oToolBar = oToolBar
		return

	def vGetMenuBar(self, oMenuBar):
		"""
		Links Menubar to Offset class			
		"""
		self.oMenuBar=oMenuBar
		return

	def vWriteXoffset(self, nXoffset):
		"""
		Updates Xoffset entry with a new value
		"""
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		self.oAppOffset.EntryXoffset.delete(0, END)
		self.oAppOffset.EntryXoffset.insert(0, round(nXoffset*PIEZO_XY/1000, 1))
		return

	def vWriteYoffset(self, nYoffset):
		"""
		Updates Yoffset entry with a new value
		"""
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		self.oAppOffset.EntryYoffset.delete(0, END)
		self.oAppOffset.EntryYoffset.insert(0, round(nYoffset * PIEZO_XY/1000, 1))
		return

	def vWriteZoffset(self, nZoffset):
		"""
		Updates Zoffset entry with a new value
		"""
		self.oAppOffset.EntryZoffset.delete(0, END)
		self.oAppOffset.EntryZoffset.insert(0, int(nZoffset))
		return

	def vWriteZpi(self, fZpi):
		"""
		Updates Feedback Zpi entry with a new value
		"""
		self.oAppOffset.LblDisplayZpi.configure(text = str(round(fZpi,1)))
		return

	def vRefreshZpiDisplay(self, event=None):
		#print 'Idinaat Wannu ..'
		if self.bDisplayZpiVar.get() == False:
		    return
		# Manual Correction Activated for Zpi display
		self.bRefreshZpiVar.set(True)
		while self.bRefreshZpiVar.get() == True:
		    self.oAppOffset.LblDisplayZpi.configure(bg = 'yellow')
		    current_Zpi  = self.fReadVoltageHandler()
		    self.vWriteZpi(current_Zpi)
		    self.oAppOffset.osGroup.update()
		    time.sleep(0.3)	# 300ms
		return

	def vFreezeZpiDisplay(self, event=None):
		if self.bDisplayZpiVar.get() == False:
		    return
		self.bRefreshZpiVar.set(False)
		self.oAppOffset.LblDisplayZpi.configure(bg = 'white')
		return

	def vSetXoffsetCB(self, event=None):
		"""
		Set the Xoffset as the value entered in the entry box ... bound with Return key
		"""
		if not self.oStm.bValidDevice():
			return
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		try:
			if self.fReadXoffset() == None:
				tkMessageBox.showerror('XOffset Error', 'Can`t go Further')
				return	
			fXoffset = self.fReadXoffset()
			nXoffset = (fXoffset * 1000) / PIEZO_XY
		except ValueError:
			return
		self.vShowMarker(nXoffset, self.nYoffset)
		self.vShowPath()
		self.arrPath[-3] = self.arrPath[-2]
		self.vSetXoffset(nXoffset)
		self.vCleanPath()
		return

	def vSetXoffset(self, nXoffset):
		"""
		Real Implementation of X offset takes place here
		"""
		if not self.oStm.bValidDevice():
			return
		if nXoffset == self.nXoffset:
			return 
		self.nXoffset = nXoffset
		print 'Xoffset(V) = ', nXoffset/1000.
		self.vMotionStart('x')
		self.vSetXoffsetHandler(nXoffset)
		self.vMotionStop()
		time.sleep(0.05)
		return
	
	def fReadXoffset(self):
		"""
		Returns the current value of X offset seen in the entry box
		"""
		xoff = float(self.oAppOffset.EntryXoffset.get())
		if self.bCheckXOffset() == True:
			return None
		return xoff

	def bCheckXOffset(self):
		"""
		Check whether Xoffset is lying in the range ( +-10000mV )  or not 
		"""
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		xoff = float(self.oAppOffset.EntryXoffset.get())	
		if (xoff >(PIEZO_XY*10*XL_GAIN)) or (xoff < (-(PIEZO_XY*10*XL_GAIN))):
			return True
		else:
			return False
	
	def bCheckYOffset(self):
		"""
		Check whether Yoffset is lying in the range ( +-10000mV )  or not 
		"""
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		yoff = float(self.oAppOffset.EntryYoffset.get())
		if (yoff >(PIEZO_XY*10*XL_GAIN)) or (yoff < (-(PIEZO_XY*10*XL_GAIN))):
			return True
		else:
			return False	

	def vSetYoffsetCB(self, event=None):
		"""
		Set the Yoffset as the value entered in the entry box ... bound with Return key
		"""
		if not self.oStm.bValidDevice():
			return
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		try:
			if self.fReadYoffset() == None:
				tkMessageBox.showerror('YOffset Error', 'Can`t go Further')
				return
			fYoffset = self.fReadYoffset()
			nYoffset = (fYoffset * 1000) / PIEZO_XY 
		except ValueError:
			return
		self.vShowMarker(self.nXoffset, nYoffset)
		self.vShowPath()
		self.vSetYoffset(nYoffset)
		self.vCleanPath()
		time.sleep(0.05)
		return

	def vSetYoffset(self, nYoffset):
		"""
		Real Implementation of Y offset takes place here
		"""
		if not self.oStm.bValidDevice():
			return
		if nYoffset == self.nYoffset:
			return  
		self.nYoffset = nYoffset 
		self.vMotionStart('y')
		self.vSetYoffsetHandler(-nYoffset)
		print 'Yoffset(V) = ', -nYoffset/1000.
		self.vMotionStop()
		return
	
	def fReadYoffset(self):
		"""
		Returns the current value of Y offset seen in the entry box
		"""
		if self.bCheckYOffset()==True:
			return None
		yoff = float(self.oAppOffset.EntryYoffset.get())
		return yoff

	def vSetZoffsetCB(self, event=None):
		"""
		Set the Zoffset as the value entered in the entry box ... bound with Return key
		"""
		if not self.oStm.bValidDevice():
			return
		try:
			nZoffset = int(float(self.nReadZoffset()))
		except ValueError:
			return
		self.vSetZoffset(nZoffset)
		return
	
	def vSetZoffset(self, nZoffset):
		"""
		Real Implementation of Zoffset takes place here
		"""
		if not self.oStm.bValidDevice():
			return
		if nZoffset == self.nZoffset:
			return  
		self.nZoffset = nZoffset 
		#self.oAppOffset.OffsetStatusBar.start()
		print 'Zoffset(mV) = ', nZoffset
		self.vSetZoffsetHandler(int(nZoffset))
		#self.oAppOffset.OffsetStatusBar.stop()
		return
	
	def nReadZoffset(self):
		"""
		Returns the current value of Zoffset seen in the entry box
		"""
		zoff = int(float(self.oAppOffset.EntryZoffset.get()))
		return zoff

	def stopCorrectZoffsetCB(self, event=None):
		self.abortCorrectZ_Var.set(True)
		return

	def stopCorrectZoffset(self, *args):
		if self.abortCorrectZ_Var.get() == False:
			self.oAppOffset.activateStopCorrectZ_Control()
		if self.abortCorrectZ_Var.get() == True:
			self.oAppOffset.activateCorrectZ_Control()
		return

	def vCorrectZoffsetCB(self, event=None):
		"""
		Correct the Zoffset inside the Window Size Specified
		"""
		if not self.oStm.bValidDevice():
			return
		
		self.abortCorrectZ_Var.set(False)
		#prev_digitization_mode = self.oScanner.DigitizationModeVar.get()
		prev_delay = self.oScanner.nReadDelay()
                if self.oWalker.PiezoVar.get() == self.oWalker.N_POL:
                    if stm.getCurrentSampleBias() < 0:
                        self.vCorrectZoffsetNPOL()
                    else:
                        self.vCorrectZoffsetPPOL()
                if self.oWalker.PiezoVar.get() == self.oWalker.P_POL:
                    if stm.getCurrentSampleBias() < 0:
                        self.vCorrectZoffsetPPOL()
                    else:
                        self.vCorrectZoffsetNPOL()
		self.abortCorrectZ_Var.set(True)

		'''
		if prev_digitization_mode == self.oScanner.TCMODE:
		    self.oScanner.DigitizationModeVar.set (self.oScanner.ZMODE)
		    while int (self.oScanner.nReadDelay ()) < int (prev_delay):
			self.oScanner.oAppScanner.EntryDelay.invoke('buttonup')
		else:
		    self.oScanner.vSetDigitizationModeHandler (prev_digitization_mode)
		'''
		return

	def vCorrectZoffsetNPOL(self):
		"""
		Corrects the Zoffset inside the Window Size Specified	
		"""
		UpperLimit = WINDOWSIZE
		LowerLimit = -WINDOWSIZE
		self.oStm.set_Zmode()
                self.oStm.hold_off()
		#self.oScanner.vSetDigitizationModeHandler (self.oScanner.ZMODE)	
		current_Zpi  = self.fReadVoltageHandler()	
		current_Zoff = self.nReadZoffset() 
		if (current_Zpi < UpperLimit) and (current_Zpi > LowerLimit):
			tkMessageBox.showinfo('Already Fine !!', 'Z offset is already in the Range')
			return
		
		#step_size = 100	# mV
		
		step_size = 150 * stm.ZDAC_RESOLUTION / fGetZoffsetGain()
		if current_Zpi  < LowerLimit:
			direction = 1
			while current_Zpi < UpperLimit:
		  	    current_Zoff += step_size*direction
			    if abs(current_Zoff) > MAX_ZOFFSET - UpperLimit:
				tkMessageBox.showerror('Out of Limit', 'Cannot correct Zoffset any further')
				return
			    current_Zpi = self.nCorrectZoffsetCore(current_Zoff)
			    self.nZoffset = current_Zoff
			    if self.abortCorrectZ_Var.get() == True:
				break
			print 'Zpi after correction: ', current_Zpi
			return	
		if current_Zpi  > UpperLimit:
			direction = -1
			while current_Zpi > LowerLimit:
		  	    current_Zoff += step_size*direction
			    if abs(current_Zoff) > MAX_ZOFFSET - UpperLimit:
				tkMessageBox.showerror('Out of Limit', 'Cannot correct Zoffset any further')
				return
			    current_Zpi = self.nCorrectZoffsetCore(current_Zoff)
			    #print current_Zpi
			    self.nZoffset = current_Zoff	
			    if self.abortCorrectZ_Var.get() == True:
				break
			print 'Zpi after correction: ', current_Zpi
		return
			    	
	def vCorrectZoffsetPPOL(self):
		"""
		Corrects the Zoffset inside the Window Size Specified	
		"""
		UpperLimit = WINDOWSIZE
		LowerLimit = -WINDOWSIZE
		self.oStm.set_Zmode()
                self.oStm.hold_off()
		#self.oScanner.vSetDigitizationModeHandler (self.oScanner.ZMODE)	
		current_Zpi  = self.fReadVoltageHandler()	
		current_Zoff = self.nReadZoffset() 
		if (current_Zpi < UpperLimit) and (current_Zpi > LowerLimit):
			tkMessageBox.showinfo('Already Fine !!', 'Z offset is already in the Range')
			return

		#step_size = 100	# mV
		step_size = 150 * stm.ZDAC_RESOLUTION / fGetZoffsetGain()
		if current_Zpi  < LowerLimit:
			direction = 1
			while current_Zpi < UpperLimit:
		  	    current_Zoff += step_size*direction
			    if abs(current_Zoff) > MAX_ZOFFSET - UpperLimit:
				tkMessageBox.showerror('Out of Limit', 'Cannot correct Zoffset any further')
				return
			    current_Zpi = self.nCorrectZoffsetCore(current_Zoff)
			    self.nZoffset = current_Zoff	
			    if self.abortCorrectZ_Var.get() == True:
				break
			return	
		if current_Zpi  > UpperLimit:
			direction = -1
			while current_Zpi > LowerLimit:
		  	    current_Zoff += (step_size * direction)
			    if abs(current_Zoff) > MAX_ZOFFSET - UpperLimit:
				tkMessageBox.showerror('Out of Limit', 'Cannot correct Zoffset any further')
				return
			    current_Zpi = self.nCorrectZoffsetCore(current_Zoff)
			    self.nZoffset = current_Zoff	
			    if self.abortCorrectZ_Var.get() == True:
				break
			#print 'Zpi after correction: ', current_Zpi
		return	

	def nCorrectZoffsetCore(self, current_Zoff):
		"""
		Returns Current Zpi value	
		"""
		self.vSetZoffsetHandler(current_Zoff)
		self.vWriteZoffset(current_Zoff)
		current_Zpi  = self.fReadVoltageHandler()
		self.vWriteZpi(current_Zpi)
		self.MainMaster.update()
	        return current_Zpi
	
	def vShowPath(self, np=2):
		"""
		Graphically shows the path for the marker movement
		"""
		self.vCleanPath()
		try:
			self.hpath = self.oAppOffset.CanTipLocation.create_line(self.arrPath[-np:], \
						dash=(4,2), fill='yellow')
			self.vpath = self.oAppOffset.CanTipLocation.create_line(self.arrPath[-np:], \
						dash=(4,2), fill='yellow')
		except:
			pass
		return

	def vShowMarker(self, xoff, yoff):
		"""
		Graphically places the Marker on the canvas according to the values of X & Y offs 
		"""
		if scanner.getTipParkingMode() == scanner.TIP_PARKING_MODES['corner']:
			restx = stm.cdac[stm.XDAC]	# mV
			resty = stm.cdac[stm.YDAC]	# mV
		if scanner.getTipParkingMode() == scanner.TIP_PARKING_MODES['center']:
			restx = 0	# mV
			resty = 0	# mV
		
		[x, y] = self.mv2pix(xoff + restx, yoff + -1.0 * resty, self.oAppOffset.w / 2, self.oAppOffset.h / 2)
		# Since yoff is inverted in mv2pix function, bad implementation
		self.arrPath.append([x,y])
		self.vCleanMarker()
		self.marker = self.oAppOffset.CanTipLocation.create_oval(x-R, y-R, \
					x+R, y+R, fill='yellow')
		return

	def vShowMotionMarker(self, x, y):
		"""
		Redraws marker
		"""
		self.mmarker = self.oAppOffset.CanTipLocation.create_oval(x-R, y-R, \
					x+R, y+R, fill='red')
		return

	def vCleanMarker(self):
		"""
		Clean previous marker after replacing it
		"""
		try:
			self.oAppOffset.CanTipLocation.delete(self.marker)
		except:
			pass
		return

	def vCleanPath(self):
		"""
		Cleans marker path
		"""
		try:
			self.oAppOffset.CanTipLocation.delete(self.hpath, self.vpath)
			self.oAppOffset.CanTipLocation.delete(self.mmarker)
		except:
			pass
		return

	def enableGlobalTipLocator (self, *args):
		if self.enableGlobalTipLocatorVar.get() == True:
			self.oAppOffset.CanTipLocation.bind('<Button-1>', self.vSetTipLocationCB)
		else:
			self.oAppOffset.CanTipLocation.unbind('<Button-1>')
		return

	def vSetTipLocationCB(self, event):
		"""
		Callback for resetting tip location
		"""
		self.enableGlobalTipLocatorVar.set (False)	# Disables the GTLocator
		old_y = self.arrPath[-1][1]
		self.arrPath.append([event.x, old_y])
		[nXoffset, nYoffset] = self.pix2mv(event.x, (self.oAppOffset.w-event.y))
		self.vShowMarker(nXoffset, nYoffset)
		self.vShowPath(3)
		self.vSetTipLocation(nXoffset, nYoffset)
		#self.oAppOffset.CanTipLocation.bind('<Button-1>', self.vSetTipLocationCB)
		self.vCleanPath()
		return

	def vSetTipLocation(self, xoff, yoff):
		"""
		Places the tip at the desired location
		"""
		xoff = round(xoff,1)
		yoff = round(yoff,1)
		self.vSetXoffset(xoff)
		self.vSetYoffset(yoff)
		self.vWriteXoffset(xoff)
		self.vWriteYoffset(yoff)
		return

	def vResetTipLocation(self, xoff=0, yoff=0):
		"""
		Removes the X and Y offset and places the tip at the origin		
		"""
		if not self.oStm.bValidDevice():
			return
		tip_delay = 40*5./(stm.TIP_VELOCITY*1000)	
		self.vWriteXoffset(xoff)
		self.vSetXoffsetCB()
		time.sleep(tip_delay)
		self.vWriteYoffset(yoff)
		self.vSetYoffsetCB()
		return

	def vMotionStart(self,direc='x'):
		"""
		Kickstarts Marker motion
		"""
		self.vDisableOsGroup()
		self.oWalker.vDisableWsGroup()
		self.oToolBar.vDisableTbGroup()
		self.oMenuBar.vDisableMbGroup()
		self.oScanner.vDisableSsGroup()		
		self.bMotionOverVar.set(False)
		self.vMoveMarker(direc)
		return

	def vMoveMarker(self, direc='x'):
		"""
		Real Marker movement takes place here
		"""
		tip_delay = 40* 5./(stm.TIP_VELOCITY*1000)
		if direc == 'x':
		    self.vShowMotionMarker(self.arrPath[-3][0], self.arrPath[-3][1])
		    x = int(abs(self.arrPath[-3][0]))
		    xEnd = int(abs(self.arrPath[-1][0]))
		    if x < xEnd:
			step = 1
		    else:
			step = -1
		    while ((x - xEnd)!=0) and self.bMotionOverVar.get() == False:
		        self.oAppOffset.CanTipLocation.move(self.mmarker,step,0)
		        x+=step
			time.sleep(tip_delay)
		        self.oAppOffset.osGroup.update()
		    self.oAppOffset.CanTipLocation.delete(self.mmarker)
		if direc == 'y':
		    self.vShowMotionMarker(self.arrPath[-2][0], self.arrPath[-2][1])
		    y = int(abs(self.arrPath[-2][1]))
		    yEnd = int(abs(self.arrPath[-1][1]))
		    if y < yEnd:
			step = 1
		    else:
			step = -1
		    while ((y - yEnd)!=0) and self.bMotionOverVar.get() == False:
		        self.oAppOffset.CanTipLocation.move(self.mmarker,0,step)
		        y+=step
			time.sleep(tip_delay)
		        self.oAppOffset.osGroup.update()
		    self.oAppOffset.CanTipLocation.delete(self.mmarker)
		return

	def vMotionStop(self):
		"""
		Stops Marker movement
		"""
		self.bMotionOverVar.set(True)
		self.oScanner.vEnableSsGroup()
		self.oMenuBar.vEnableMbGroup()
		self.oToolBar.vEnableTbGroup()
		self.oWalker.vEnableWsGroup()
		self.vEnableOsGroup()
		return

	def vInitialSTMSetup(self, MainMaster):
		"""
		Get X, Y and Z Offset values from log files or from the INIT dialog at Initialization
		"""
	        if self.bInitInstanceVar.get():
		    self.winInit.deiconify()
		    self.winInit.lift()
		    return 
		self.bApplyVar.set(False)
		self.bInitInstanceVar.set(True)
		self.winInit = Toplevel(takefocus=True)
		self.winInit.geometry('+60+60')
		self.winInit.title('Initial Setup')
		self.winInit.resizable(False, False)
		InitialSTMSettingsDialog(self, self.winInit, self.bInitInstanceVar)

	def vInitSettingsApplied(self):
		"""
		Update the Offset Window and Log Window as the 
		Initial STM Settings are applied.
		"""
		xoff = stm.readLogOffsetX()
		yoff = stm.readLogOffsetY()
		zoff = stm.readLogOffsetZ()
		sampleBias = stm.getCurrentSampleBias() 
		self.vWriteXoffset(xoff)
		self.vWriteYoffset(yoff)
		self.vWriteZoffset(zoff)
		self.nXoffset = xoff
		self.nYoffset = yoff
		self.nZoffset = zoff 
		[x, y] = self.mv2pix(xoff, yoff, self.oAppOffset.w/2, self.oAppOffset.h/2)
		self.arrPath.append([x,y])
		self.vShowMarker(xoff, yoff)
		self.oStm.set_scanx(0)
		self.oStm.set_scany(0)
		if self.oStm.bValidDevice():
		    self.vClearHoldHandler()	# Feedback On
		    self.vResetOffHandler()	# Reset Off
		    #self.oScanner.vClearXLAreaHandler() 	# XLArea option is disabled in initial conditions
		    self.oScanner.prepareSystemForTipParking(delay = 0)

	def vRenewAreaBox(self, size):		
		"""
		As the scan size is changed it modifies the area markers on the sample area canvas
		"""
		[x, y] = self.mv2pix(size, size)
		[x0, y0] = self.arrPath[-1]
		if scanner.getTipParkingMode() == scanner.TIP_PARKING_MODES['center']:
			line_coords = [  [x0-x/2, y0-y/2], \
				[x0+x/2, y0-y/2], \
				[x0+x/2, y0+y/2], \
				[x0-x/2, y0+y/2], \
				[x0-x/2, y0-y/2]  ]
		if scanner.getTipParkingMode() == scanner.TIP_PARKING_MODES['corner']:
			line_coords = [  [x0, y0], \
				[x0 + x, y0], \
				[x0 + x, y0 - y], \
				[x0, y0 - y], \
				[x0, y0]  ]
		self.vShowAreaBox(line_coords) 
		return

	def vShowAreaBox(self, coords):
		"""
		When a new scan size is selected erase previous scan area boundary and create new ones
		"""
		try:
		    self.oAppOffset.CanTipLocation.delete(self.iAreaBox)
		except:
		    pass
		self.iAreaBox = self.oAppOffset.CanTipLocation.create_line(coords, \
						fill='green', \
						dash=(2,3))
		return

	def vSetFeedbackControl(self, oMenubar = None):
		"""
		Hold  1 --> FeedBack Off
		Reset 1	--> Reset Off 
		"""
		FeedbackControlDialog(self.MainMaster, self, oMenubar)
		return
	
	def vChangeSampleBias(self, nPrevBias, nCurrentBias):
		"""
		Changes the Sample Bias to the specified value(Gradual)
		"""
		step = 5
		delay = 0.01		# 10ms
		if nPrevBias > nCurrentBias:
		    step *= -1
		#self.MainMaster.config(cursor='wait')	
		while nPrevBias	!= nCurrentBias:
		    nPrevBias += step
		    self.vSetBiasHandler(nPrevBias)
		    time.sleep(delay)
		#self.MainMaster.config(cursor='')
		print 'Current Bias: ', nCurrentBias, 'mV'
		# Update Bias Voltage in the log ...
		arrDacValues = stm.readInitLog()
		arrDacValues[BIASDAC] = nCurrentBias
		vWriteInitLog(arrDacValues)
		return

	def vNavigatorCB(self, event=None):
	    """
	    Sample Surface traversing using the navigator
	    """
	    if self.nNavigatorInstance > 0:
	    	self.winNavigator.deiconify()
	    	self.winNavigator.lift()
		return 
	    #print 'Launch Navigator Tool'
	    self.nNavigatorInstance += 1	
	    if self.nNavigatorInstance == 1: 
		self.winNavigator = Toplevel(takefocus=True)
		self.winNavigator.resizable(False, False)
		self.winNavigator.title('Sample Navigation Assistant')
		self.winNavigator.protocol('WM_DELETE_WINDOW', self.vCloseNavigatorCB)
		oNavigator = navigator.navigator(self.winNavigator, self.oScanner, self)
	    return

	def vCloseNavigatorCB(self):
	    self.nNavigatorInstance = 0
	    self.winNavigator.destroy()
	    return

	def __vConfigureKBShortcuts(self):
	    self.MainMaster.bind('<Control-n>', self.vNavigatorCB)
	    self.MainMaster.bind('<Control-z>', self.vCorrectZoffsetCB)
	    return

	############### HANDLER FUNCTIONS #################
	def vSetHoldHandler(self):
		"""
		Feedback Off
		"""
		self.oStm.hold_on()
		#print "Hold On"	
		return	

	def vClearHoldHandler(self):
		"""
		FeedBack On
		"""
		self.oStm.hold_off()
		#print "Hold Off"
		return

	def vResetOnHandler(self):
		"""
		Feedback output clamped to zero
		"""
		self.oStm.reset_on()
		#print "Reset On"	
		return	

	def vResetOffHandler(self):
		"""
		FeedBack Ouput released from Zero clamp
		"""
		self.oStm.reset_off()
		#print "Reset Off"
		return

	def vSetXoffsetHandler(self, nXoffset):
		"""
		Sets X offset
		"""
		nXoffset /= (XL_GAIN*1.0)
		self.oStm.set_offsetx(nXoffset)
		return

	def vSetYoffsetHandler(self, nYoffset):
		"""
		Sets Y offset
		"""
		nYoffset /= (XL_GAIN*1.0)
		self.oStm.set_offsety(nYoffset)
		return

	def vSetZoffsetHandler(self, nZoffset):
		"""
		Sets Z offset
		"""
		self.oStm.set_offsetz(nZoffset)
		return

	def vSetBiasHandler(self, nBias):
		"""
		Sets Bias voltage
		"""
		self.oStm.set_bias(nBias)
		return

	def fReadVoltageHandler(self):
		"""
		Reads adc voltage	
		"""
		return self.oStm.read_spi_adc() [0]

	def lReadBlockHandler(self, np, delay):
		"""
		Reads adc block data
		"""
		return self.oStm.read_spi_adc() [0] 

	def vDisableOsGroup(self):
		"""
		Disables OffsetGui widgets
		"""
		self.oAppOffset.CanTipLocation.unbind ('<Button-1>')
		self.oAppOffset.CBEnableGlobalTipLocator.config (state = DISABLED)
		self.oAppOffset.BtnResetTipLocation.config (state = DISABLED)
		self.oAppOffset.BtnCorrectZoffset.config (state = DISABLED)
		self.oAppOffset.EntryXoffset.config (state = DISABLED)
		self.oAppOffset.EntryYoffset.config (state = DISABLED)
		self.oAppOffset.BtnNavigator.config (state = DISABLED)
		self.oAppOffset.CBFBMonitor.config (state = DISABLED)
		self.oAppOffset.LblDisplayZpi.unbind ('<Enter>')
		self.oAppOffset.LblDisplayZpi.unbind ('<Leave>')
		return

	def vEnableOsGroup(self):
		"""
		Enables OffsetGui widgets 
		"""
		self.oAppOffset.CBEnableGlobalTipLocator.config (state = NORMAL)
		self.oAppOffset.LblDisplayZpi.bind ('<Enter>', self.vRefreshZpiDisplay)
		self.oAppOffset.LblDisplayZpi.bind ('<Leave>', self.vFreezeZpiDisplay)
		self.oAppOffset.BtnResetTipLocation.config (state = NORMAL)
		self.oAppOffset.BtnCorrectZoffset.config (state = NORMAL)
		self.oAppOffset.EntryXoffset.config (state = NORMAL)
		self.oAppOffset.EntryYoffset.config (state = NORMAL)
		self.oAppOffset.CBFBMonitor.config (state = NORMAL)
		self.oAppOffset.BtnNavigator.config (state = NORMAL)
		return

   
class InitialSTMSettingsDialog:
    def __init__(self, oOffset, master, bInitInstanceVar):
	self.oOffset = oOffset
	self.bInitInstanceVar = bInitInstanceVar
	self.valid = True
	self.master = master
	self._getInitSettings()
	self.body()
	
	return

    def _getInitSettings(self):
	self.setpointTC = stm.readCurrentSetpoint()
	self.sampleBias = stm.getCurrentSampleBias()
	return

    def body(self):
	self._getInitSettings()
	textwidth = 5 
	self.LabelSettings = LabelFrame(self.master)
	self.LabelSettings.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
	lblTC = Label(self.LabelSettings, text='Reference Tunneling Current:')
	lblTC.grid(row=0, column=0, columnspan=2, sticky=N+E+W+S, padx=3)
	self.EntryCurrentSetpoint = tkValidatingEntry.IntegerEntry(self.LabelSettings, \
		#bg='light gray', \
                width=textwidth, \
		text=' ', \
                borderwidth=2, \
		#relief=FLAT, \
		font=tcfont, \
                justify=CENTER)
	self.EntryCurrentSetpoint.grid(row=1, column=0, sticky=N+E+W+S)
	self.EntryCurrentSetpoint.limits([stm.MIN_TC, stm.MAX_TC])
	lblTCUnit = Label(self.LabelSettings, text='pA', font=tcfont)
	lblTCUnit.grid(row=1, column=1, sticky=W, padx=3)

	lblBias = Label(self.LabelSettings, text='Sample Bias:')
	lblBias.grid(row=2, column=0, columnspan=2, sticky=N+E+W+S, padx=3)
	self.EntryBias = tkValidatingEntry.FloatEntry(self.LabelSettings, \
		#bg='light gray', \
                width=textwidth, \
		text=' ', \
                borderwidth=2, \
		#relief=FLAT, \
		font=tcfont, \
                justify=CENTER)
	self.EntryBias.grid(row=3, column=0, sticky=N+E+W+S)
	self.EntryBias.limits([stm.MIN_BIAS, stm.MAX_BIAS])
	lblBiasUnit = Label(self.LabelSettings, text='V', font=tcfont)
	lblBiasUnit.grid(row=3, column=1, sticky=W, padx=3)

	self.BtnDetectSTM = Button(self.LabelSettings, \
				fg = 'red',\
				text='Detect nanoREV',\
				bg='light gray', \
				command=self.vDetectSTMCB, \
				)
	self.BtnDetectSTM.grid(row=9, column=0, columnspan=2, sticky=N+W+E+S)	
	
	self.BtnApply = Button(self.master, text='Apply', width=7, \
				relief=GROOVE, \
				takefocus=1, \
				borderwidth=2, \
				command=self.vOkCB)
	self.BtnApply.grid(row=9, column=0, padx=3, pady=3, sticky=N+E+W+S)
	self.BtnCancel = Button(self.master, text='Cancel', \
				command=self.vCancelCB)
	self.BtnCancel.grid(row=9, column=1, padx=3, pady=3, sticky=N+E+W+S)
	self._vPopulateEntries()
	self.master.bind('<Return>', self.vOkCB)
	self.master.bind('<Escape>', self.vCancelCB)
	self.BtnApply.focus_set()
	self.master.protocol('WM_DELETE_WINDOW', self.vCancelCB)
	return

    def updateSampleBias(self):
	sb = '%3.3f' % self.sampleBias
	self.EntryBias.delete(0, END)
	self.EntryBias.insert(0, sb)
	return

    def updateSetpointTC(self):
	tc = self.setpointTC #'%2.3f' % self.setpointTC
	self.EntryCurrentSetpoint.delete(0, END)
	self.EntryCurrentSetpoint.insert(0, tc)
	return

    def _vPopulateEntries(self):
	self.updateSampleBias()
	self.updateSetpointTC()
	self.master.update()
	if self.oOffset.oStm.bValidDevice() == True:		# When it is already detected ... 
	    self.BtnDetectSTM.configure(state=DISABLED)
	else:
	    tkMessageBox.showerror('No Hardware Found','*) Supply is switched off or, \n*) USB Cable not connected or, \n*) Try other ports in Settings Menu \nand then try detecting again !!', parent=self.master)
	self.master.lift()
	return

    def validate(self):
	self.getSampleBias()
	''' Non- Zero Bias Check '''
        if self.sampleBias == 0:
            tkMessageBox.showwarning('Entries Incorrect', \
                                'Bias should have a non-zero value !!', \
				parent=self.master)
	    return False
	''' Non- Zero Bias Check '''
        self.getSetpointTC()
        if self.setpointTC == 0:
            tkMessageBox.showwarning('Entries Incorrect', \
                                'Tunneling Current should have a non-zero value !!', \
				parent=self.master)
	    return False
	''' Valid Tunneling Condition  Check '''
	if ((self.setpointTC > 0) and (self.sampleBias > 0)) or \
                ((self.setpointTC < 0) and (self.sampleBias < 0)):
            tkMessageBox.showwarning('Invalid Tunnel Condition', \
                                'TC setpoint and bias should have\n different polarities !!', \
				parent=self.master)
	    return False

	return True

    def validateDevice(self):
	if self.oOffset.oStm.bValidDevice() == True:		# If it is detected ... 
	    self.BtnDetectSTM.configure(state=DISABLED)
	    tkMessageBox.showinfo('Success', \
				'Found nanoREV Hardware ! \n Please Apply and continue...', \
				parent=self.master)
	    return True
	else:
	    tkMessageBox.showerror('Device Not Found', \
				'Please check connections \n and try detecting again...', \
				parent=self.master)
	    return False
	
    def getSampleBias(self):
        sampleBias = self.EntryBias.get()
	if (sampleBias == '')  or (sampleBias == '-'):
	    self.updateSampleBias()
	else:
	    self.sampleBias = float(sampleBias)

    def getSetpointTC(self):
        setpointTC = self.EntryCurrentSetpoint.get()
	if (setpointTC == '')  or (setpointTC == '-'):
	    self.updateSetpointTC()
	else:
	    self.setpointTC = int(float(setpointTC))

    def apply(self):
	self.vSetVoltageHandler(stm.OXDAC, 0)
	self.vSetVoltageHandler(stm.OYDAC, 0)
	self.vSetVoltageHandler(stm.OZDAC, 0)

	self.oOffset.oStm.set_bias_slow(self.sampleBias, delay = 0)	# Quick Setting
	print 'Sample Bias: ', self.sampleBias, 'V'

	self.oOffset.oStm.set_tc(self.setpointTC, delay = 0)	# Quick Setting
	print 'TC Setpoint: ', self.setpointTC, 'pA'
	
	self.oOffset.oStm.fine_slope_adj()

    def vDetectSTMCB(self):
	self.oOffset.oStm.vDetectSTM()
	self.validateDevice()
	return


    def vOkCB(self, event=None):
	self.BtnApply.configure(state=ACTIVE)
	self.master.update()
	if self.validate() == False:
	    print 'Incorrect Init Settings...'
	    tkMessageBox.showwarning('Entries Incorrect', \
				'Init Settings not applied.. Try Again !!', parent=self.master)
	    return
	else:	
	    #if self.validateDevice() == False:
	    #	return
    	    self.apply()
	    self.oOffset.vInitSettingsApplied()
	    self.vCancelCB()

    def vCancelCB(self, event=None):
	self.bInitInstanceVar.set(False)  
	self.master.destroy()


    ########## HANDLER FUNCTIONS ###########

    def vSetVoltageHandler(self, dac, val):
	self.oOffset.oStm.set_voltage(dac, val)
	return

########### Only for Testing ###########
if __name__ == '__main__':
	offset()
