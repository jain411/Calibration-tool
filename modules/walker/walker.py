####################
#   Walker Class   #
####################

__DEBUG__ = True

import os
import cPickle
import numpy
import time
import tkMessageBox
import modules.offset.offset as offset 
import apps.dialogs as dialogs
import app_walker
import lib.stm7 as stm
import tkSimpleDialog	

if __DEBUG__ == True:
	from Tkinter import *


logpath      	 = os.path.join(os.curdir, 'log')
globlogfile  	 = os.path.join(logpath, 'glob.dat')

def dicReadGlobalParam():
    f = open(globlogfile)
    dicGlobalParam = cPickle.load(f)
    f.close()
    return dicGlobalParam 

def vWriteGlobalParam(dicGlobalParam):
    f=open(globlogfile,'w')
    cPickle.dump(dicGlobalParam,f)
    f.close()
    return

def fGetAutoWalkDelay():
    """
    Returns: Delay between two successive steps during Auto-Walk (seconds)
    """
    dicGlobalParam = dicReadGlobalParam()
    fAWD = float(dicGlobalParam['AutoWalkDelay'])/1000
    return fAWD

def fGetRunDelay():
    """
    Returns: Delay between two successive steps during Running (seconds)
    """
    dicGlobalParam = dicReadGlobalParam()
    fRD = float(dicGlobalParam['RunDelay'])/1000
    return fRD

def vSaveRunDelay(fRD):
    dicGlobalParam = dicReadGlobalParam()
    dicGlobalParam['RunDelay'] = int(fRD)       # in ms
    vWriteGlobalParam(dicGlobalParam)
    return

def vSaveAutoWalkDelay(fAWD):
    dicGlobalParam = dicReadGlobalParam()
    dicGlobalParam['AutoWalkDelay'] = int(fAWD) # in ms
    vWriteGlobalParam(dicGlobalParam)
    return

def walker(master, oStm=None):
	"""
	Function : walker
	
	Arguments :
		f    : root widget
		oStm : object of class Stm
		
	Returns :
		oWalker : object of class Walker
	"""
	oAppWalker = app_walker.app_walker()
	oAppWalker.createWSwindow(master)
	oWalker = Walker(oAppWalker, oStm)
	return oWalker

class Walker:
	
	BACKWARD = 0
	FORWARD	 = 1
	N_POL = 1
	P_POL = 2 	
	def __init__(self, oAppWalker, oStm):
		"""
		Class Contructor : Walker
		"""
		self.oAppWalker = oAppWalker
		self.oStm = oStm
		self.bStop = True
		self.nSteps = 0
		#self.fAutoWalkDelay = 0.002
		self.DirVar = IntVar()
		self.PiezoVar = IntVar()	
		self.PiezoVar.set(self.N_POL)
		#self.RunDelayVar = StringVar() 
                self.bLEDStatusVar = BooleanVar() 
		self.bStopWalkerVar = BooleanVar()
		self.bBreakLockVar = BooleanVar()
		self.bBreakLockVar.set(True)
		self.TC_SET_POINT = stm.readCurrentSetpoint()
		self._configureCB()
		if self.oStm.fd != None:
                    self._initWalker()
                    self.DirVar.trace('w', self.vSetWalkerDirectionCB)
		return

	def _configureCB(self):
		"""
		Attaches Callbacks to WalketGui widgets 
		"""
		self.oAppWalker.BtnRun.configure(command=self.BtnRunWalkerCB)
		self.oAppWalker.BtnSingleStep.configure(command=self.BtnSingleStepCB)
		self.oAppWalker.BtnAutoWalk.configure(command=self.BtnAutoWalkCB)
		self.oAppWalker.BtnBreakLock.configure(command=self.BtnBreakLockCB)
		self.oAppWalker.BtnStop.configure(command=self.BtnStopWalkerCB)
		self.oAppWalker.RBForward.configure(variable=self.DirVar, \
						command=self.vSetWalkerDirectionCB, \
						value=self.FORWARD)
		self.oAppWalker.RBBackward.configure(variable=self.DirVar, \
						command=self.vSetWalkerDirectionCB, \
						value=self.BACKWARD)
                self.oAppWalker.RBLEDOn.configure(variable=self.bLEDStatusVar, \
						command=self.vLEDStatusCB, \
						value=True)
		self.oAppWalker.RBLEDOff.configure(variable=self.bLEDStatusVar, \
						command=self.vLEDStatusCB, \
						value=False)
		return

	def _initWalker(self):
		"""
		Performs initial walker settings	
		"""
		self.oAppWalker.RBBackward.invoke()
                self.oAppWalker.RBLEDOn.invoke()
		#self.DirVar.set(self.BACKWARD)
		#self.RunDelayVar.set(str(RUN_DELAY))
		self.bStopWalkerVar.set(True)
		return

	def vGetScanner(self,oScanner):
		"""
		Links scanner object to Walker class
		"""
		self.oScanner = oScanner
		return

	def vGetOffset(self, oOffset):
		"""
		Links Offset object to Walker class
		"""
		self.oOffset = oOffset
		return

	def vGetToolBar(self, oToolBar):
		"""
		Links ToolBar object to Walker class
		"""
		self.oToolBar = oToolBar
		return

	def vGetMenuBar(self, oMenuBar):
		"""
		Links MenuBar object to Walker class
		"""
		self.oMenuBar = oMenuBar
		return

	def vGetMainMaster(self, oMainMaster):
		"""
		Links Main Window to Walker class
		"""
		self.oMainMaster = oMainMaster
		return

	def BtnRunWalkerCB(self):
		"""
		Walker Run Handler ... keeps on recursively calling single step
		"""
		if self.DirVar.get() == self.FORWARD:
		    if not self.vEnsureInitWarning():
			return
		self.vDisableRun()
		self.vDisableSingleStep()
		self.vDisableAutoWalk()
		self.vDisableBreakLock()
		self.vBasicWalkerSettings()
		self.oOffset.vDisableOsGroup()
		self.oToolBar.vDisableTbGroup()	
		self.oMenuBar.vDisableMbGroup()
		self.oScanner.vDisableSsGroup()	
		self.bStopWalkerVar.set(False) 
		self.vRunWalkerHandler()
		return

	def BtnStopWalkerCB(self):
		"""
		Stops the walker ... both while Running and Auto-Walking
		"""
		self.vEnableRun()
		self.vEnableSingleStep()
		self.vEnableBreakLock()
		self.vEnableAutoWalk()
		print 'Walker Stopped'
		self.bStopWalkerVar.set(True)
		self.oMenuBar.vEnableMbGroup()
		self.oOffset.vEnableOsGroup()
		self.oToolBar.vEnableTbGroup()
		self.oScanner.vEnableSsGroup()	
		self.vEnableWsGroup()
		return

	def BtnAutoWalkCB(self):
		"""
                Following a search pattern similar to urs ... when u r blindfolded
                        1. Stretch out slowly to sense if any tunneling current is there,
                        2. If not found, then take a step forward, else stop there.
		"""
		self.vBasicWalkerSettings()
		print 'Auto Walk begins ...'
		self.vDisableAutoWalk()
		self.vDisableRun()
		self.vDisableSingleStep()
		self.vDisableBreakLock()
		self.oOffset.vDisableOsGroup()
		self.oToolBar.vDisableTbGroup()
		self.oMenuBar.vDisableMbGroup()
		self.oScanner.vDisableSsGroup()

		self.bBreakLockVar.set(False)
		self.DirVar.set(self.FORWARD)
		self.vSetWalkerDirection(self.FORWARD)	
		self.vDisableForward()
		self.vDisableBackward()
		self.vCoreAutoWalkHandler()
                self.vPostAutoWalkActions()
		"""
		if self.PiezoVar.get() == self.N_POL:
			self.vNPolAutoWalkHandler()
		if self.PiezoVar.get() == self.P_POL:
			self.vPPolAutoWalkHandler()
		"""
		return


	def BtnSingleStepCB(self):
		"""
		Take a single step and displays the tunneling current sensed with each step
		"""
		self.vBasicWalkerSettings()
		self.vSingleStepHandler()
		self.oStm.set_Zmode()
		self.oStm.hold_off()
		#self.oScanner.DigitizationModeVar.set(self.oScanner.ZMODE) 
		return

	def BtnBreakLockCB(self):
		"""
		Gracefully coming out of the lock. In the follwing manner:
                    1. Retracts the tip fully.
                    2. Takes ten steps backward
                    3. Brings the tip to rest position again 
		"""
		print 'Coming out of Lock .. '
		self.oAppWalker.BtnBreakLock.configure(fg='red', text='Pls. Wait..')
		self.oAppWalker.wsGroup.update()
		self.vBreakLockHandler()
		self.oAppWalker.BtnBreakLock.configure(text='Break Lock', fg='black')
		self.oStm.set_Zmode()
		self.oStm.hold_off()
		#self.oScanner.DigitizationModeVar.set(self.oScanner.ZMODE) 
		return

	def vEnsureInitWarning(self):
		return tkMessageBox.askyesno('Ensuring System Initialization', \
			'\'Init\' Setting applied...??')

	def vSetWalkerDirectionCB(self, *args):
		"""
		Sets Walker Direction Forward / Backward
		"""
		nDir = self.DirVar.get()
		self.vSetWalkerDirection(nDir)
		return

	def vLEDStatusCB(self, *args):
		"""
		Junction View LED switched On/Off
		"""
		bStatus = self.bLEDStatusVar.get()
		self.vLEDStatus(bStatus)
		return

	def vBasicWalkerSettings(self):
		"""
		Sets 
                    --> Scanning Mode: TC Mode
                    --> Gain: 1
		""" 
		self.oStm.set_TCmode()
		self.oStm.hold_off()	# Feedback is active
		self.oScanner.vWriteAndSetGain(2)
		self.oScanner.vWriteAndSetGain(1)
		self.oMainMaster.update()
		return


	##################### HANDLER FUNCTIONS #########################

	def vRunWalkerHandler(self):
		"""
		Moves walker in run mode
		"""
		self.bBreakLockVar.set(False)
		tc = self.oStm.read_spi_adc () [stm.ADC_CHANNEL_TCZ]
		set_point = stm.readCurrentSetpoint()
		print 'T.C. Set Point', set_point, 'pA'
		delay = float(fGetRunDelay())
		bGotTC = False
                self.oStm.reset_on()        # Reset FB circuit
		while (not bGotTC) and (self.bStopWalkerVar.get() == False):
			if abs(tc) < abs(set_point):
			  tc = self.vSingleStepHandler()
			  time.sleep(delay)
			else:
			  tc_dash = self.fNoiseDetector()
			  if abs(tc_dash) > abs(set_point):
				bGotTC = True
			  tc = tc_dash
			self.oAppWalker.wsGroup.update()
		print "Final TC : ", tc
                self.oStm.reset_off()        # Removed Reset on FB circuit
		self.bBreakLockVar.set(True)
		self.oMenuBar.vEnableMbGroup()
		self.oOffset.vEnableOsGroup()
		self.oToolBar.vEnableTbGroup()
		self.oScanner.vEnableSsGroup()	
		#self.oScanner.DigitizationModeVar.set(self.oScanner.ZMODE)
		self.oStm.set_Zmode()
                self.oStm.hold_off()
		return

	def vCalculatedRunHandler(self, nos):	
		"""
		Moves walker only by the given no. of steps specified in run mode
		"""
		self.bBreakLockVar.set(False)
		self.bStopWalkerVar.set(False)
		self.oStm.set_TCmode()
		#self.oScanner.DigitizationModeVar.set(self.oScanner.TCMODE) 
		delay = float(fGetRunDelay())
		# Keep on running for that many no. of steps
		print 'No. of Steps to Run:', nos
                self.oStm.reset_on()        # Reset FB circuit
		while (self.bStopWalkerVar.get() == False) and (nos):
			tc = self.vSingleStepHandler()
			time.sleep(delay)
			print nos, 'TC: ', tc
			self.oAppWalker.wsGroup.update()
			nos -= 1
		print "final tc : ", tc
                self.oStm.reset_off()        # Removed Reset on FB circuit
		self.bBreakLockVar.set(True)
		self.oMenuBar.vEnableMbGroup()
		self.oOffset.vEnableOsGroup()
		self.oToolBar.vEnableTbGroup()
		self.oScanner.vEnableSsGroup()
		self.oStm.set_Zmode()
                self.oStm.hold_off()
		#self.oScanner.DigitizationModeVar.set(self.oScanner.ZMODE) 
		return


	def vSetWalkerDirection(self, nDir):
		"""
		Sets Walker Direction according to the given dir as Forward/Backward
		"""
		if nDir == self.FORWARD:
			self.oStm.set_walker_forward()
		if nDir == self.BACKWARD:
			self.oStm.set_walker_backward()
		return

        def vLEDStatus(self, bStatus):
		"""
		Junction View LED control
		"""
		if bStatus == True:
			self.oStm.led_on()
		if bStatus == False:
			self.oStm.led_off()
		return

	def vSingleStepHandler(self):
		"""
		Moves walker by a Single Step and returns TC after each step
		"""
		tc = self.oStm.single_step()
		print tc, 'pA'
		return tc

	def vNPolAutoWalkHandler(self):
		"""
		Moves walker in Autowalk mode
                    --> walker streches a little to sense the T.C. Setpoint,
                    --> If actual T.C. >= set point, then it stops, 
                            -else the Z-piezo shrinks back, and takes a step forward.
                    --> Records Z-offset in the log file 
		"""
		#self.vBasicWalkerSettings()
		self.bBreakLockVar.set(False)
		#self.oAppWalker.RBForward.invoke()
		self.DirVar.set(self.FORWARD)
		self.vDisableForward()
		self.vDisableBackward()
		delay = fGetAutoWalkDelay()     #AUTOWALK_DELAY
		full_stretch = 0
		full_back = -10000
		Vref = stm.readCurrentSetpoint()
		#Vref = self.VrefVar.get()
		print 'TC Set Point: ', Vref, 'pA' 
		stretch = full_back
		tc = self.oStm.read_spi_adc () [stm.ADC_CHANNEL_TCZ]
		#Vtc = self.oStm.read_voltage()
		self.oStm.set_voltage(offset.OZDAC,full_back)	
		self.bStopWalkerVar.set(False)
		bGotTC = False
		while (not bGotTC) and (self.bStopWalkerVar.get() == False):
			if abs(Vtc) < abs(Vref):
			  self.oStm.set_voltage(offset.OZDAC,stretch)	
			  tc = self.oStm.read_spi_adc () [stm.ADC_CHANNEL_TCZ]
			  #Vtc = self.oStm.read_voltage()
			  time.sleep(delay)
			  stretch = stretch + 100
			  self.oOffset.vWriteZoffset(stretch)	
			  if stretch >= full_stretch:
				print 'full stretch'
				print Vtc
				stretch = full_back
				self.oStm.set_voltage(offset.OZDAC,full_back)	
				self.oStm.single_step()
				time.sleep(delay)#*10)
   			else:
			  print 'Spike or TC??'
			  Vtc_dash = self.fNoiseDetector()
			  if abs(Vtc_dash) > abs(Vref):
				bGotTC = True
			  print "Vtc(avg)", Vtc_dash
		 	  Vtc = Vtc_dash
	     		#self.oAppWalker.wsGroup.update()
			#self.oOffset.oAppOffset.osGroup.update()
		print 'Final TC value is: ', Vtc
		print 'Vref Value: ', Vref
		self.oOffset.vWriteZoffset(stretch)	
		zlog = open(offset.zlog,'w')
		zlog.write(str(stretch))
		zlog.close()
		self.bBreakLockVar.set(True)
		self.oMenuBar.vEnableMbGroup()
		self.oOffset.vEnableOsGroup()
		self.oToolBar.vEnableTbGroup()
		self.oScanner.vEnableSsGroup()	
		self.vEnableWsGroup()
		self.oStm.set_Zmode()
		self.oStm.hold_off()
		return
			   
	def vPPolAutoWalkHandler(self):
		self.vCoreAutoWalkHandler()
		return 

	def vCoreAutoWalkHandler(self):
		"""
		Moves walker in Autowalk mode
                    --> walker streches a little to sense the T.C. Setpoint,
                    --> If actual T.C. >= set point, then it stops, 
                            -else the Z-piezo shrinks back, and takes a step forward.
                    --> Records Z-offset in the log file 
		"""
		fAWD = fGetAutoWalkDelay()  # AUTOWALK_DELAY
		fZSamDelay = 0.01	    # 10ms
                nAW_TCSamples = 10          # TC sampled before FB saturates
                fSafeLimit = 0.9            # Vtc upto 90% of Vref considered valid
		VZ_SAT = 8500		    # Feedback Saturation Voltage

		Vref = fSafeLimit * stm.readCurrentSetpoint()
		Vtc = self.fNoiseDetector()
		self.bStopWalkerVar.set(False)
		bGotTC = False
		if self.bConfirmTC(Vref) == True:
                    bGotTC = True
                    tkMessageBox.showwarning('Careful', 'Already in Lock Mode!')
		    return
                
		self.oStm.set_voltage(stm.OZDAC, 0)	# Clear Zoffset
		self.oOffset.vWriteZoffset(0)
                self.oStm.reset_on()        # Reset FB circuit

		while (not bGotTC) and (self.bStopWalkerVar.get() == False):
                    self.oStm.reset_off()       # Activate FB circuit
		    bFBSaturate = False
		    time.sleep(0.05)	# Wait to avoid spike immediately after  reset
		    while (bFBSaturate == False):
                        if self.bConfirmTC(Vref) == True:
			    ## Check Again to confirm ##
		    	    time.sleep(0.05)
                            if self.bConfirmTC(Vref) == True:
		    	        Vtc = self.fNoiseDetector()
                        	bGotTC = True
                        	print 'Final TC value is: ', Vtc, 'pA'
                        	break
		    	Vtc = self.fNoiseDetector()
			self.oStm.set_Zmode()
		    	time.sleep(0.005)
			Vz = self.oStm.read_spi_adc () [stm.ADC_CHANNEL_TCZ]
			self.oOffset.vWriteZpi(Vz)	# Update Feedback (Zpi) voltage in Offset Window
			self.oOffset.oAppOffset.osGroup.update()
			if abs(Vz) >= abs(VZ_SAT):
			    bFBSaturate = True
                    if (bGotTC == False) and (bFBSaturate == True):
                        self.oStm.reset_on()        # Reset FB circuit
                        self.oStm.single_step()
                        time.sleep(fAWD)
			print 'TC: ', Vtc, ' pA'
                    self.oAppWalker.wsGroup.update()
                self.oStm.reset_off()       # Activate FB circuit
                self.vPostAutoWalkActions()
		return

	def bConfirmTC(self, Vref):
	    """
	    return True if TC is greater than the Setpoint, otherwise False
	    """
	    bGotTC = False
	    self.oStm.set_TCmode()
	    Vtc = self.fNoiseDetector()
            if abs(Vtc) > abs(Vref):
                bGotTC = True
	    return bGotTC

        def vPostAutoWalkActions(self):
            self.bBreakLockVar.set(True)
            self.oMenuBar.vEnableMbGroup()
            self.oOffset.vEnableOsGroup()
            self.oToolBar.vEnableTbGroup()
            self.oScanner.vEnableSsGroup()	
            self.vEnableWsGroup()
            self.oStm.set_Zmode()
            self.oStm.hold_off()
            #self.oScanner.DigitizationModeVar.set(self.oScanner.ZMODE) 
            return
        
	def vBreakLockHandler(self):
		"""
		Retracts the tip back and than move back by 10 steps
		"""
		if self.bBreakLockVar.get()==False:
			return
		self.bBreakLockVar.set(False)
		#self.oAppWalker.RBBackward.invoke()
		self.DirVar.set(self.BACKWARD)
		self.vSetWalkerDirection(self.BACKWARD)	
		self.vBasicWalkerSettings()
		if self.PiezoVar.get()==self.N_POL:
			self.oOffset.vSetZoffset(offset.MIN_ZOFFSET)
		if self.PiezoVar.get()==self.P_POL:
			self.oOffset.vSetZoffset(offset.MAX_ZOFFSET)
		print 'Moving 15 steps back'
		self.oStm.walk(15)
		print 'Making Z offset zero again ...'	
		self.oStm.set_voltage(stm.OZDAC, 0)	# Clear Zoffset
		self.oOffset.vWriteZoffset(0)
                self.oStm.hold_off()        # FB activated
                self.oStm.reset_off()
		time.sleep(0.1)	
		self.bBreakLockVar.set(True)
		return

	def fNoiseDetector(self, np=10, delay=1000):
		"""
                Returns an average of 'np' TC readings each taken
                after 'delay' microseconds to filter out spurious
                noise spikes
		"""
		#data = numpy.asarray(self.oStm.read_block(np, delay))	# np , delay in us
		#print "Avg TC Data", data
		#avg = data[:,1].sum()/np*1.0
		#return avg 
		tc = self.oStm.read_spi_adc () [stm.ADC_CHANNEL_TCZ]
		return tc

	def vDisableWsGroup(self):
		"""
		Disables Walker widgets	
		"""
		self.vDisableForward()
		self.vDisableBackward()
		self.vDisableRun()
		self.vDisableSingleStep()
		self.vDisableAutoWalk()
		self.vDisableBreakLock()
		self.vDisableStop()
		return

	def vDisableForward(self):
		"""
		Disables Foward RadioButton
		"""
		self.oAppWalker.RBForward.config(state=DISABLED)
		return

	def vDisableBackward(self):
		"""
		Disables Backward RadioButton
		"""
		self.oAppWalker.RBBackward.config(state=DISABLED)
		return

	
	def vDisableRun(self):
		"""
		Disables Run Button
		"""
		self.oAppWalker.BtnRun.config(state=DISABLED)
		return

	def vDisableSingleStep(self):
		"""
		Disables SingleStep Button
		"""
		self.oAppWalker.BtnSingleStep.config(state=DISABLED)
		return

	def vDisableAutoWalk(self):
		"""
		Disables AutoWalk Button
		"""
		self.oAppWalker.BtnAutoWalk.config(state=DISABLED)
		return

	def vDisableBreakLock(self):
		"""
		Disables BreakLock Button
		"""
		self.oAppWalker.BtnBreakLock.config(state=DISABLED)
		return

	def vDisableStop(self):
		"""
		Disables Stop Button
		"""
		self.oAppWalker.BtnStop.config(state=DISABLED)
		return


	def vEnableWsGroup(self):
		"""
		Enables Walker widgets
		"""
		self.vEnableForward()
		self.vEnableBackward()
		self.vEnableRun()
		self.vEnableSingleStep()
		self.vEnableAutoWalk()
		self.vEnableBreakLock()
		self.vEnableStop()
		return

	def vEnableForward(self):
		"""
		Enables Forward RadioButton
		"""
		self.oAppWalker.RBForward.config(state=NORMAL)
		return

	def vEnableBackward(self):
		"""
		Enables Backward RadioButton	
		"""
		self.oAppWalker.RBBackward.config(state=NORMAL)
		return

	def vEnableRun(self):
		"""
		Enables Run Button
		"""
		self.oAppWalker.BtnRun.config(state=NORMAL)
		return

	def vEnableSingleStep(self):
		"""
		Enables Single Step Button
		"""
		self.oAppWalker.BtnSingleStep.config(state=NORMAL)
		return

	def vEnableAutoWalk(self):
		"""
		Enables AutoWalk Button
		"""
		self.oAppWalker.BtnAutoWalk.config(state=NORMAL)
		return

	def vEnableBreakLock(self):
		"""
		Enables BreakLock Button
		"""
		self.oAppWalker.BtnBreakLock.config(state=NORMAL)
		return

	def vEnableStop(self):
		"""
		Enables Stop Button
		"""
		self.oAppWalker.BtnStop.config(state=NORMAL)
		return

	def vSetPiezoChoice(self):
		"""
		Piezo Choice based on Zpolarity (positive, negative)
		"""
		PiezoChoiceDialog(self.oMainMaster, self.PiezoVar)
		if self.PiezoVar.get() == self.N_POL:
			print "Scanner Piezo fully streches at max. negative voltage"
		if self.PiezoVar.get() == self.P_POL:
			print "Scanner Piezo fully streches at max. positive voltage"
		return
		
class PiezoChoiceDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, PiezoVar):
	self.PiezoVar = PiezoVar
	self.N_POL = 1
	self.P_POL = 2
	tkSimpleDialog.Dialog.__init__(self, master, 'Z Polarity')
	return

    def body(self, master):
	self.master = master
	Label(text='Piezo Selection')
	self.RBQOld = Radiobutton(self.master, \
				text='Negative')#, \
				#selectcolor='blue')	
	self.RBQOld.pack(fill=BOTH)	
	self.RBQNew = Radiobutton(self.master, \
				text='Positive ')#, \
				#selectcolor='red')
	self.RBQNew.pack(fill=BOTH)
	self._configureCB()
	return
	
    def _configureCB(self):
	self.RBQOld.configure(variable=self.PiezoVar, \
				value=self.N_POL)
	self.RBQNew.configure(variable=self.PiezoVar, \
				value=self.P_POL)
	return

######### Only for Testing ###########
if __name__ == "__main__":
	walker()

