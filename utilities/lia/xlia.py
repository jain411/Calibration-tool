from Tkinter import *
import tkMessageBox

import serial, time, struct, math, pylab, numpy, sys, os, cPickle, struct, functools

import app_xlia, libxlia

TIMEOUT_INTERVAL = 1.0
PRE_AMP_GAIN = ['1', '10', '100']
POST_AMP_GAIN = ['1', '10', '100']
INTG_TIME_CONST = ['2ms', '5ms', '10ms']
DECOUP_STATE = ['Disabled', 'Enabled']

xlialog = os.path.join (os.curdir, 'log', 'xlia.log')
xliastatuslog = os.path.join (os.curdir, 'log', 'xliastatus.log')

def setXLIA_On ():
	fd = open (xliastatuslog, 'w')
	fd.write ('1')
	fd.close ()	
	return

def setXLIA_Off ():
	fd = open (xliastatuslog, 'w')
	fd.write ('0')
	fd.close ()	
	return

def getXLIA_Status():
	fd = open (xliastatuslog)
	status = fd.read()
	fd.close()
	return int (status)

def getXLIA_ParametersFromFile():
	fd = open (xlialog)
	dicXLIA_Param = cPickle.load (fd) 
	fd.close ()
	return dicXLIA_Param

def xlia(master = None):
	'''
	Launch XLIA Module
	'''
	oAppXLIA = app_xlia.app_xlia(master)
	oXLIA = XLIA(oAppXLIA)
	return oXLIA

class XLIA:

	def __init__(self, oAppXLIA = None):
		"""
		Searches for XLIA hardware on RS232 ports and the USB-to-Serial adapters. Presence of the
		device is done by reading the version string.
		"""
		self.oAppXLIA = oAppXLIA
		self.xliaDevID = None
		self.TimeConstSelected = StringVar()
		self.TimeConstSelected.set (INTG_TIME_CONST[0])
		self.PostAmpGainSelected = StringVar()
		self.PostAmpGainSelected.set (POST_AMP_GAIN[0])
		self.PreAmpGainSelected = StringVar()
		self.PreAmpGainSelected.set (PRE_AMP_GAIN[0])
		self.PreAmpAC_CouplingSelected = BooleanVar()
		self.PreAmpAC_CouplingSelected.set(True)
		self.EnableRelativeMeasurement = IntVar()
		self.EnableRelativeMeasurement.set(1)
		self.enableAutoUpdateVar = BooleanVar()
		self.enableAutoUpdateVar.set(False)
		self.autoUpdater = None 
		self.loadXLIA_Parameters ()
		if self.oAppXLIA != None:
			self._vConfigureWidgets()
		self.vUpdateXLIAWindow (0, 0, 0, 0)
		self.vConnectDevice()
		self.vUpdateRefGenParameters()
		self.LIA_CHANNELS = ['In-Phase', 'Quad-Phase', 'Amplitude', 'Phase']
		return

	def loadXLIA_Parameters (self):
		''' Load Initial Settings from log file '''
		dicXLIA_Param = getXLIA_ParametersFromFile()
		self.RefAmplitude = dicXLIA_Param ['RefAmplitude'] #1e-3 V
		self.RefFrequency = dicXLIA_Param ['RefFrequency'] #100	 Hz
		self.RefPhase = dicXLIA_Param ['RefPhase']
		state_string = dicXLIA_Param ['PreAmpAC_CouplingState'] 
		acCouplingState = DECOUP_STATE.index (state_string)
		if acCouplingState == 0: 
			self.PreAmpAC_CouplingSelected.set(False)
		else:
			self.PreAmpAC_CouplingSelected.set(True)
		preAG_string = dicXLIA_Param ['PreAmpGain'] 
		self.PreAmpGain = PRE_AMP_GAIN.index (preAG_string)
		postAG_string = dicXLIA_Param ['PostAmpGain'] 
		self.PostAmpGain = POST_AMP_GAIN.index (postAG_string)
		tc_string = dicXLIA_Param ['IntgTimeConst']
		self.IntgTimeConst = INTG_TIME_CONST.index (tc_string) 
		return

	def saveXLIA_Parameters (self):
		''' Dump XLIA Settings in a log file '''
		dicXLIA_Param = self.getXLIA_Parameters()
		fd = open (xlialog, 'w')
		cPickle.dump (dicXLIA_Param, fd)
		fd.close()
		return

	def getXLIA_Parameters (self):
		dicXLIA_Param = {}
		dicXLIA_Param ['RefAmplitude'] = self.RefAmplitude
		dicXLIA_Param ['RefAmplitudeUnit'] = 'mV'
		dicXLIA_Param ['RefFrequency'] = self.RefFrequency
		dicXLIA_Param ['RefFrequencyUnit'] = 'Hz'
		dicXLIA_Param ['RefPhase'] = self.RefPhase
		dicXLIA_Param ['RefPhaseUnit'] = 'deg'
		if self.PreAmpAC_CouplingSelected.get() == False:
			dicXLIA_Param ['PreAmpAC_CouplingState'] = DECOUP_STATE [0]
		else:
			dicXLIA_Param ['PreAmpAC_CouplingState'] = DECOUP_STATE [1]
		dicXLIA_Param ['PreAmpGain'] = PRE_AMP_GAIN [self.PreAmpGain]
		dicXLIA_Param ['PostAmpGain'] = POST_AMP_GAIN [self.PostAmpGain]
		dicXLIA_Param ['IntgTimeConst'] = INTG_TIME_CONST [self.IntgTimeConst]
		return dicXLIA_Param

	def _vConfigureWidgets(self):
		
		#Configure File Menu
		self.oAppXLIA.mainmenu.add_cascade(label='File', \
			menu=self.oAppXLIA.filemenu, underline=0)
		
		#File -> Connect to Device / Disconnect Device
		self.oAppXLIA.filemenu.add_command(\
			label='Connect to Device', underline=0,\
			command=self.vConnectDeviceCB)
		
		#Configure Settings Menu
		self.oAppXLIA.mainmenu.add_cascade(label='Settings', \
			menu=self.oAppXLIA.settingmenu, underline=0)
		'''
		#Settings -> Enable Relative Measurement
		self.oAppXLIA.settingmenu.add_checkbutton(\
			label='Enable Relative Measurement', underline=0,\
			variable=self.EnableRelativeMeasurement, \
			onvalue=1, offvalue=0, \
			command=self.vEnableRelativeMeasurementCB)
		'''
                #Settings -> Auto-Correct Phase Offset
                self.oAppXLIA.settingmenu.add_command(\
                        label='Auto-Correct Phase Offset', underline=0,\
                        command=self.autoCorrectPhaseOffsetCB)

		self.oAppXLIA.settingmenu.add_checkbutton(\
			label='Enable Auto Update', underline=1,\
			variable=self.enableAutoUpdateVar, \
			command=self.enableAutoUpdateCB)
		
		#Configure Referance Entries under main window
		self.oAppXLIA.EntryRefAmplitude.bind(\
			'<Return>', self.vSetRefAmplitudeCB)
		self.oAppXLIA.EntryRefAmplitude.bind(\
			'<Key>', self.vClearHighlightRefAmplitudeCB)
		self.oAppXLIA.EntryRefFrequency.bind(\
			'<Return>', self.vSetRefFrequencyCB)
		self.oAppXLIA.EntryRefFrequency.bind(\
			'<Key>', self.vClearHighlightRefFrequencyCB)
		self.oAppXLIA.EntryRefPhase.bind(\
			'<Return>', self.vSetRefPhaseCB)
		self.oAppXLIA.EntryRefPhase.bind(\
			'<Key>', self.vClearHighlightRefPhaseCB)
		
		#Configure Settings under main window
		self.oAppXLIA.BtnEnableCoupling.config(command=self.vEnableCouplingCB, variable = self.PreAmpAC_CouplingSelected)

		# Fill out the options in the Option menu
		self.oAppXLIA.createOptionMenus(\
						self.PreAmpGainSelected, \
						self.PostAmpGainSelected, \
						self.TimeConstSelected, \
						)	
		#Configure Drop Down Bar for Pre Amp Gain Selection
		for index in range(len(PRE_AMP_GAIN)):
			self.oAppXLIA.OMPreAmpGain["menu"].add_command( \
				label = PRE_AMP_GAIN[index] ,\
				command = functools.partial(self.vSelectPreAmpGainCB, index))
		self.PreAmpGainSelected.set(\
			PRE_AMP_GAIN[self.PreAmpGain])
		
		#Configure Drop Down Bar for Post Amp Gain Selection
		for index in range(len(POST_AMP_GAIN)):
			self.oAppXLIA.OMPostAmpGain["menu"].add_command( \
				label = POST_AMP_GAIN[index], \
				command = functools.partial(self.vSelectPostAmpGainCB, index))
		self.PostAmpGainSelected.set(\
			POST_AMP_GAIN[self.PostAmpGain])
		
		#Configure Drop Down Bar for Integrator Time Constant Selection
		for index in range (len (INTG_TIME_CONST)):
			self.oAppXLIA.OMTimeConst["menu"].add_command( \
				label = INTG_TIME_CONST [index] ,\
				command = functools.partial(self.vSelectIntgTimeConstCB, index))
		self.TimeConstSelected.set(\
			INTG_TIME_CONST [self.IntgTimeConst])
		return
		

	def vConnectDeviceCB(self):
		self.oAppXLIA.filemenu.entryconfig(0,state = DISABLED)
		self.vConnectDevice()
		if self.bValidDevXLIA() == True:
			self.oAppXLIA.filemenu.entryconfig(0, \
				command = self.vDisconnectDeviceCB,label='Disconnect Device')
		self.oAppXLIA.filemenu.entryconfig(0,state = NORMAL)
		return
		
	def vConnectDevice(self):
		self.vDetectXLIA()
		if self.bValidDevXLIA() == True:
			self.vInitXLIA()
			setXLIA_On ()
			# Read outputs and update window once
			outIP, outQP, amplitude, phase = self.CoreGetXLIA_Output()
			self.vUpdateXLIAWindow (outIP, outQP, amplitude, phase)
		return
		
	def vDisconnectDeviceCB(self):
		self.oAppXLIA.filemenu.entryconfig(0, state = DISABLED)
		self.vDisconnectDevice()
		self.oAppXLIA.filemenu.entryconfig(0, \
			command = self.vConnectDeviceCB, label='Connect Device')
		self.oAppXLIA.filemenu.entryconfig(0, state = NORMAL)
		return
		
	def vDisconnectDevice(self):
		if self.bValidDevXLIA() == True:
			libxlia.close_device(self.xliaDevID)
		self.xliaDevID = None
		setXLIA_Off ()
		return

	def bValidDevXLIA(self):
		if self.xliaDevID != None:
			return True
		setXLIA_Off ()
		return False

	def vDetectXLIA(self):
		no_of_dev = libxlia.scan()
		if no_of_dev == 0:
			print '### No XLIA hardware detected ###'
			return
		# if no_of_dev > 1 ... Select which xlia to open
		print 'Found ', no_of_dev, ' XLIA device(s) connected'
		serialNo = libxlia.serialNo(0)
		deviceID, goodID, rem_time = libxlia.open_device(serialNo, TIMEOUT_INTERVAL)
		print goodID, rem_time, '#####'
		if (self.bCheckTimeOut(rem_time) == True) and (goodID):
			self.xliaDevID = deviceID
		else:
			libxlia.close_device(deviceID)
		return

	def vInitXLIA(self):
		self.vSelectPreAmpGain(self.PreAmpGain)
		self.vSelectPostAmpGain(self.PostAmpGain)
		self.vSelectIntgTimeConst(self.IntgTimeConst)
		self.vEnableCouplingCB()
		self.CoreSetRefAmplitude(self.RefAmplitude)
		self.CoreSetRefFrequency(self.RefFrequency)
		self.CoreSetRefPhase(self.RefPhase)
		return

	def vSetRefAmplitudeCB(self, event):
		set_ra = self.oAppXLIA.EntryRefAmplitude.get()
		try:
			set_ra = float(set_ra) / 1e3	# mV to V
		except:
			return
		self.vSetRefAmplitude(set_ra)
		return 

	def vSetRefAmplitude(self, set_ra):
		self.oAppXLIA.EntryRefAmplitude.configure(bg='yellow')
		self.CoreSetRefAmplitude(set_ra)
		self.vUpdateRefGenParameters()
		self.saveXLIA_Parameters()
		return

	def vSetRefFrequencyCB(self, event):
		set_rf = self.oAppXLIA.EntryRefFrequency.get()
		try:
			set_rf = float(set_rf)
		except:
			return
		self.vSetRefFrequency(set_rf)
		return 

	def vSetRefFrequency(self, set_rf):
		self.oAppXLIA.EntryRefFrequency.configure(bg='yellow')
		self.CoreSetRefFrequency(set_rf)
		self.vUpdateRefGenParameters()
		self.saveXLIA_Parameters()
		return

	def vSetRefPhaseCB(self, event):
		set_rph = self.oAppXLIA.EntryRefPhase.get()
		try:
			set_rph = float(set_rph)
		except:
			return
		self.vSetRefPhase(set_rph)
		return

	def vSetRefPhase(self, set_rph):
		self.oAppXLIA.EntryRefPhase.configure(bg='yellow')
		self.CoreSetRefPhase(set_rph)
		self.vUpdateRefGenParameters()
		self.saveXLIA_Parameters()
		return


	def autoCorrectPhaseOffsetCB(self):
                '''
                Nullify Steady Phase Offset in LIA
                '''
                setpoint = 0.0
                
                channel_outs = self.CoreGetXLIA_Output()
                if channel_outs is None:
                    print 'Invalid LIA output...'
		    return
                phaseChannel = self.LIA_CHANNELS.index('Phase') 
                currentPhase  = channel_outs[phaseChannel] * 180 / numpy.pi
                sign = -1.0
                if currentPhase < 0 :         # negative (0 to -180)
                    sign = 1.0
                phaseOffset = setpoint + (sign * currentPhase)
                correctedPhase = self.RefPhase - (sign * phaseOffset)
		print 'Sheri Aaki...', correctedPhase 
                self.vSetRefPhase(correctedPhase)
		return


	def enableAutoUpdateCB(self):
		print 'XLIA output display active'
		if self.enableAutoUpdateVar.get() == True:
			if self.bValidDevXLIA() == True:
				self.startAutoUpdater()
		else:
			self.stopAutoUpdater()
		self.oAppXLIA.master.update()
		return


	def vEnableRelativeMeasurement(self):
		if self.bValidDevXLIA() == False:
			print 'Unable to auto correct offset...'
			return
		control, rem_time = \
			libxlia.enableRelativeMeasurement (self.xliaDevID, \
								self.EnableRelativeMeasurement.get(), \
								TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Timeout Occured while auto correcting offset...'
			return
		print "Lock-in amplifier offset corrected."
		return

	def vEnableCouplingCB(self):
		if self.PreAmpAC_CouplingSelected.get() == True:
			self.oAppXLIA.BtnEnableCoupling.config(state=DISABLED)
			acCouplingState = self.vEnableCoupling()
			self.oAppXLIA.BtnEnableCoupling.config(state=NORMAL)
		else:
			self.oAppXLIA.BtnEnableCoupling.config(state=DISABLED)
			acCouplingState = self.vDisableCoupling()
			self.oAppXLIA.BtnEnableCoupling.config(state=NORMAL)
		if acCouplingState == 0:
			self.PreAmpAC_CouplingSelected.set(False)
			print 'Pre Amp AC Coupling Disabled...'
		else:
			self.PreAmpAC_CouplingSelected.set(True)
			print 'Pre Amp AC Coupling Enabled...'
		self.saveXLIA_Parameters()
		self.oAppXLIA.master.update()
		return


	def vEnableCoupling(self):
		if self.bValidDevXLIA() == False:
			print 'Unable to turn on AC Coupling mode...'
			return
		acCouplingState, rem_time = \
			libxlia.enablePreAmp_AC_Coupling(self.xliaDevID, 1, TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Timeout Occured while enabling AC coupling...'
		return acCouplingState

	def vDisableCoupling(self):
		if self.bValidDevXLIA() == False:
			print 'Unable to turn off AC Coupling mode...'
			return
		acCouplingState, rem_time = \
			libxlia.enablePreAmp_AC_Coupling(self.xliaDevID, 0, TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Timeout Occured while disabling AC coupling...'
		return acCouplingState
		
	def vSelectPreAmpGainCB(self, index):
		self.PreAmpGainSelected.set (PRE_AMP_GAIN [index])
		self.vSelectPreAmpGain(index)
		self.saveXLIA_Parameters()
		return
		
	def vSelectPreAmpGain(self, index):
		if self.bValidDevXLIA() == False:
			print 'Unable to set pre amp gain...'
			print 'Present Pre amp gain: ', PRE_AMP_GAIN [self.PreAmpGain]
			return
		self.PreAmpGain, rem_time = \
			libxlia.setPreAmpGain(self.xliaDevID, index, TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Timeout Occured while setting pre amp gain...'
		print 'Pre amp gain set at : ', PRE_AMP_GAIN [self.PreAmpGain]
		return
	
	def vSelectPostAmpGainCB(self, index):
		self.PostAmpGainSelected.set(POST_AMP_GAIN[index])
		self.vSelectPostAmpGain(index)
		self.saveXLIA_Parameters()
		return
		
	def vSelectPostAmpGain(self, index):
		if self.bValidDevXLIA() == False:
			print 'Unable to set post amp gain...'
			print 'Present Post amp gain: ', POST_AMP_GAIN [self.PostAmpGain]
			return
		self.PostAmpGain, rem_time = \
			libxlia.setPostAmpGain(self.xliaDevID, index, TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Timeout Occured while setting post amp gain...'
		print 'Post amp gain set at : ', POST_AMP_GAIN [self.PostAmpGain]
		return

	def vSelectIntgTimeConstCB(self, index):
		self.TimeConstSelected.set (INTG_TIME_CONST[index])
		self.vSelectIntgTimeConst(index)
		self.saveXLIA_Parameters()
		return
		
	def vSelectIntgTimeConst(self, index):
		if self.bValidDevXLIA() == False:
			print 'Unable to set integrator time constant...'
			print 'Integrator Time Constant set at : ', INTG_TIME_CONST [self.IntgTimeConst]
			return
		self.IntgTimeConst, rem_time = \
			libxlia.setIntegratorTimeConstant(self.xliaDevID, index, TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Timeout Occured while setting Integrator time constant...'
		print 'Integrator Time Constant set at : ', INTG_TIME_CONST [self.IntgTimeConst]
		return

	def bCheckTimeOut(self, rem_time):
		if rem_time == 0:
			print 'Comm time out...'
			self.vDisconnectDevice()
			return False
		return True
 
	def CoreSetRefFrequency(self, rf):
		if self.bValidDevXLIA() == False:
			print 'Unable to set ref. freq...'
			print 'Reference Freq. is set at : ',self.RefFrequency
			return 
		self.RefFrequency, rem_time = \
			libxlia.setReferenceFrequency(self.xliaDevID, rf, TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Unable to set ref. freq...'
		print 'Reference Freq. is set at : ',self.RefFrequency
		return
 
	def CoreSetRefAmplitude(self, ra):
		if self.bValidDevXLIA() == False:
			print 'Unable to set ref. amplitude...'
			print 'Reference Amplitude is set at : ',self.RefAmplitude
			return 
		self.RefAmplitude, rem_time = \
			libxlia.setReferenceAmplitude(self.xliaDevID, ra, TIMEOUT_INTERVAL)
		if self.bCheckTimeOut(rem_time) == False:
			print 'Unable to set ref. amplitude...'
		print 'Reference Amplitude is set at : ',self.RefAmplitude
		return

	def CoreSetRefPhase(self, rph):
		if self.bValidDevXLIA() == False:
			print 'Unable to set ref. phase...'
			print 'Reference Phase is set at : ',self.RefPhase
			return
		rph_rad = rph * math.pi / 180.0 
		phase, rem_time = \
			libxlia.setReferencePhase(self.xliaDevID, rph_rad, TIMEOUT_INTERVAL)
                self.RefPhase = 180 * phase / math.pi
		if self.bCheckTimeOut(rem_time) == False:
			print 'Unable to set ref. phase...'
		print 'Reference Phase is set at : ',self.RefPhase
		return

	def CoreGetXLIA_Output(self):
		if self.bValidDevXLIA() == False:
			print 'Unable to read XLIA output...'
			return
		outIP, outQP, amplitude, phase, rem_time = \
			libxlia.doMeasurement(self.xliaDevID, TIMEOUT_INTERVAL)	
		if self.bCheckTimeOut(rem_time) == False:
			print 'Unable to read XLIA outputs...'
			outIP = 0.0
			outQP = 0.0
			amplitude = 0.0
			phase = 0.0
		return outIP, outQP, amplitude, phase

	def vUpdateRefGenParameters(self, ra=None, rf=None, rph=None):
		if ra == None:
			self.vUpdateEntryBox(self.oAppXLIA.EntryRefAmplitude, \
				int(self.RefAmplitude * 1e3)) #Display is in mV	
		if rph == None:
			self.vUpdateEntryBox(self.oAppXLIA.EntryRefPhase, \
				int(round(self.RefPhase, 1)))		
		if rf == None:
			self.vUpdateEntryBox(self.oAppXLIA.EntryRefFrequency, \
				int(round(self.RefFrequency)))		
		return
 
	def vClearHighlightRefAmplitudeCB(self, event):
		self.oAppXLIA.EntryRefAmplitude.configure(bg='white')
		return

	def vClearHighlightRefPhaseCB(self, event):
		self.oAppXLIA.EntryRefPhase.configure(bg='white')
		return

	def vClearHighlightRefFrequencyCB(self, event):
		self.oAppXLIA.EntryRefFrequency.configure(bg='white')
		return

	def vUpdateEntryBox(self, EntryBox, val):
		EntryBox.delete(0, END)
		EntryBox.insert(0, val)
		self.oAppXLIA.master.update()
		return

	def vUpdateXLIAWindow(self, ip, qp, amplitude, phase):
		self.vUpdateIP(ip)
		self.vUpdateQP(qp)
		self.vUpdateAmplitude(amplitude)
		self.vUpdatePhase(phase)
		self.oAppXLIA.master.update()
		return

	def startAutoUpdater(self):
		self.autoUpdater = self.oAppXLIA.master.after (1000, self.autoUpdateXLIA_Window)
		return

	def autoUpdateXLIA_Window (self):
		if self.enableAutoUpdateVar.get() == False:
			return
		outIP, outQP, amplitude, phase = self.CoreGetXLIA_Output()
		self.vUpdateXLIAWindow (outIP, outQP, amplitude, phase)
		self.autoUpdater = self.oAppXLIA.master.after (1000, self.autoUpdateXLIA_Window)
		return

	def stopAutoUpdater(self):
		if self.autoUpdater == None:
			return
		self.enableAutoUpdateVar.set(False)
		self.oAppXLIA.master.after_cancel (self.autoUpdater)
		self.autoUpdater = None
		print 'XLIA output display disabled'
		return

	def vUpdateIP(self, ip):
		ip *= 1e3
		self.oAppXLIA.LblInPhaseOutput.config(text='%3.3f mV' % ip)
		return

	def vUpdateQP(self, qp):
		qp *= 1e3
		self.oAppXLIA.LblQuadratureOutput.config(text='%3.3f mV' % qp)
		return

	def vUpdateAmplitude(self, amplitude):
		amplitude *= 1e3
		self.oAppXLIA.LblAmplitudeOutput.config(text='%3.3f mV' % amplitude)
		return

	def vUpdatePhase(self, phase):
		phase = phase * 180.0 / math.pi
		self.oAppXLIA.LblPhaseOutput.config(text='%3.1f Deg' % phase)
		return

	def vCloseXLIA(self):
		self.stopAutoUpdater()
		self.saveXLIA_Parameters()
		self.vDisconnectDevice()
		return

if __name__ == '__main__':
	root = Tk()
	oXLIA = xlia(root)
	root.mainloop()
