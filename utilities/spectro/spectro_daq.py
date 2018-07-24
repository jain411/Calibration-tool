#############################
# Spectral Data Acquisition #
#############################

import numpy, time

import stm7 as stm
import offset		

def spectro_daq(oSpectro, oStm):
    oSpecDaq = SpectroDaq(oSpectro, oStm)
    return oSpecDaq

class SpectroDaq:
    def __init__(self, oSpectro, oStm):
	self.oSpectro = oSpectro
	self.oStm = oStm
	self.dicSpecParam = {}
	self.dicScanParam = self.oSpectro.dicScanParam
	self.nInitBias = stm.getCurrentSampleBias() * 1e3	# The Bias set before spectro experiment
	self.nCurrentBias = self.nInitBias
	self.nFramePixels = self.oSpectro.nFramePixels 	
	self.oSpectro.oScanner.vWriteAndSetGain(1)	# ADC Gain Unity
	return

    def vPreSpectrumSetUp(self):
	"""
	For Dual Ramp Method
	"""
	####
	self.oSpectro.oScanner.vWriteAndSetGain(1)
	self.oStm.set_TCmode()
	self.oStm.hold_on()
	####
	self.vGoTo(self.nLowerBiasLimit)
	time.sleep(self.nPreSpectrumDelay/1000.0)
	return

    def vSetSpectraMode(self):	
	"""
	IV Spectroscopy Acquisition Mode: Cut-off feedback and read TC values
	"""
	self.oStm.set_TCmode()
	self.oStm.hold_on()	# FB off
	return

    def vSetTopoMode(self):
	"""
	Topography Image Acquisition Mode: Feedback active and read Z error
	"""
	self.oStm.set_Zmode()
	self.oStm.hold_off()
	return

    def vPreSpectrumSetUpSR(self):
	"""
	For Single Ramp Method
	"""
	self.vGoTo(self.nLowerBiasLimit)
	#print 'Tamasam', self.nPreSpectrumDelay/1000.0
	time.sleep(self.nPreSpectrumDelay/1000.0)
	return

    def vPostSpectrumSetUp(self):
	self.vGoTo(self.nInitBias)
	self.oStm.set_Zmode()
	self.oStm.hold_off()
	time.sleep(self.nPreSpectrumDelay/100.0)	# Pre-Spectrum Delay = Post-Spectrum Delay
	return

    def vPostSpectrumSetUpSR(self):
	self.vGoTo(self.nInitBias)
	#self.oStm.set_Zmode()
	#self.oStm.hold_off()
	time.sleep(self.nPreSpectrumDelay/1000.0)	# Pre-Spectrum Delay = Post-Spectrum Delay
	return

    def vGetSpecParameters(self):
	"""
	Copy the validated entries from 
	"""
	self.nLowerBiasLimit = self.dicSpecParam['LowerBias'] = self.oSpectro.nLowerBiasLimit
	self.nUpperBiasLimit = self.dicSpecParam['UpperBias'] = self.oSpectro.nUpperBiasLimit
	self.nStepSize = self.dicSpecParam['StepSize'] = self.oSpectro.nStepSize
	self.nStepDelay = self.dicSpecParam['StepDelay'] = self.oSpectro.nStepDelay
	self.nMovAvgPoints = self.dicSpecParam['MovAvgPoints'] = self.oSpectro.nMovAvgPoints
	self.nSweeps = self.dicSpecParam['Sweeps'] = self.oSpectro.nSweeps
	self.dicSpecParam['TCSetpoint'] = stm.readCurrentSetpoint()	# in pA
	self.dicSpecParam['SampleBias'] = self.nInitBias	# in mV 

	self.arMarkerPos = self.dicSpecParam['MarkerPos'] = self.oSpectro.arMarkerPos
	self.nPreSpectrumDelay = self.oSpectro.nPreSpectrumDelay
	self.dicSpecParam['PreSpecDelay'] = self.oSpectro.nPreSpectrumDelay
	self.dicSpecParam['InterSweepDelay'] = self.oSpectro.nInterSweepDelay
	self.dicSpecParam['SpectroMode'] = self.oSpectro.spectroModeVar.get()	# IV or dI/dV
	# IV or dI/dV mode
	if self.dicSpecParam['SpectroMode'] == 'dIdV':
	    oXLIA = self.oSpectro.oScanner.oToolBar.oXLIA
	    self.dicSpecParam['XLIA_Param'] = oXLIA.getXLIA_Parameters()

	# Point / Grid Mode				
	self.dicSpecParam['Mode'] = self.oSpectro.cSpectroModeVar.get()
	if self.oSpectro.cSpectroModeVar.get() == self.oSpectro.GRID_MODE:
	    self.dicSpecParam['GridSize'] = self.oSpectro.oAppSpectro.SliderGridSize.get()
	self.dicSpecParam['RetraceSweepMode'] = self.oSpectro.RetraceSweepVar.get()
    	self.vSetDacChoice()
	return

    def vSetDacChoice(self):
	if self.dicScanParam['AreaChoice'] == self.oSpectro.oScanner.LARGE_AREA:
	    self.XPOSITIONER = offset.BIGXDAC
	    self.YPOSITIONER = offset.BIGYDAC
	else:
	    self.XPOSITIONER = offset.XDAC
	    self.YPOSITIONER = offset.YDAC

	return
	
    def pix2mv(self, x=0, y=0): 
	"""
	Method : pix2mv
		Converts offset window coordinates to x/y offsets
	Arguments :
		x : int x coordinate
		y : int y coordinate
	Returns :
		xoff : int Xoffset
		yoff : int Yoffset
	"""
	self.MV_PER_PIXEL = self.dicScanParam['StepSize'][0]
	xoff = (x - self.nFramePixels/2) * self.MV_PER_PIXEL
	yoff = (self.nFramePixels/2 - y) * self.MV_PER_PIXEL
	return [xoff, yoff]


    def vStartPointIVLogging(self):
	"""
	Kick starts I-V spectroscopy
	"""
	### Check IV-Spectro Parameters ####
	np = abs ((self.nUpperBiasLimit - self.nLowerBiasLimit) / self.nStepSize)
	self.oSpectro.bStopLoggingVar.set(False)
        bias_steps = range(self.nLowerBiasLimit, \
                           self.nUpperBiasLimit+self.nStepSize, \
                           self.nStepSize)
	#afIVlog = numpy.zeros([len(bias_steps),2],'f')
	self.afPlotsAtPos = []
	self.oSpectro.oAppSpectro.SpectroStatusBar.maximum(self.nSweeps*len(self.arMarkerPos))
	npos = 0				# no. of spatial points selected for spectra
	nPrevXoffset = nPrevYoffset = 0		# Scan DACs point at the centre of the image
	dac12bit_sp = int ((self.nLowerBiasLimit - stm.cdac[stm.BIASDAC]) / stm.mdac[stm.BIASDAC])
	dac12bit_step = int ((self.nStepSize / stm.mdac[stm.BIASDAC]))

	if self.dicSpecParam ['SpectroMode'] == 'dIdV':
	    channel_mask = 7	# First three channels of simultaneous
	else:
	    channel_mask = 1

	for spectro_pos in self.arMarkerPos:
	    self.vSetTopoMode()	
	    # Save Topography Data
	    self.vSetSpectraMode()	
	    npos += 1
	    [nXoffset, nYoffset] = self.pix2mv(spectro_pos[0], (self.nFramePixels-spectro_pos[1]))
	    #print 'Positioning Tip @', nXoffset, nYoffset
	    self.vPositionTip(nXoffset, nYoffset, nPrevXoffset, nPrevYoffset)
	    nPrevXoffset = nXoffset
	    nPrevYoffset = nYoffset
	    plots = []
	    dir_ = 1			# Increasing Bias from Lower to Upper potential
	    nSweepStartBias = self.nLowerBiasLimit
	    ### SINGLE RAMP METHOD
	    #### Start Bias Sweeps ####
	    #afIVlog[:,0] = bias_steps
	    sp = time.time()
	    for sweeps in range(self.nSweeps):
	        self.oStm.hold_on()		# Switch Off Feedback
	    	self.vPreSpectrumSetUpSR()
		### Trace Data ###
		afIVlog = self.afSpectroSweepHandler(len(bias_steps), \
					dac12bit_sp, dac12bit_step, \
					self.nStepDelay, self.nMovAvgPoints,\
					channel_mask \
					)
	    	plots.append (afIVlog)
		self.nCurrentBias = bias_steps[-1] 

		### Retrace Data ###
		if self.dicSpecParam['RetraceSweepMode'] == True:
			dac12bit_rsp = dac12bit_sp + ((len(bias_steps) - 1) * dac12bit_step)
			afIVlogRetrace = self.afSpectroSweepHandler(len(bias_steps), \
					dac12bit_rsp, dac12bit_step, \
					self.nStepDelay, self.nMovAvgPoints,\
					channel_mask, \
					retrace = True)
	    		plots.append (afIVlogRetrace)
			self.nCurrentBias = bias_steps[0] 
 
		self.vGoTo (self.nInitBias)
		self.oStm.hold_off ()
	    	#self.vPostSpectrumSetUpSR()
		self.oSpectro.oAppSpectro.SpectroStatusBar.value ( (sweeps + 1) * npos)
	        self.oSpectro.oAppSpectro.sGroup.update ()
	        #print 'Sweep No. ', sweeps
		if self.oSpectro.bStopLoggingVar.get () == True:
		    break
		time.sleep (self.oSpectro.nInterSweepDelay)		# delay between two sweeps
	    #### Bias Sweeps Over ####
	    if self.oSpectro.bStopLoggingVar.get () == True:
		self.vGoTo (self.nInitBias)
	        break
	    self.afPlotsAtPos.append (plots)
	    print 'Spectro Logging Over @', spectro_pos
	    #time.sleep(1)
	self.oSpectro.dicSpecParam ['TotalTime'] = time.time () - sp
	self.vPostSpectrumSetUp ()
	self.vPositionTip (0, 0, nPrevXoffset, nPrevYoffset)	#ScanDACs restored to Normal position
	return

    def vPositionTip(self, nXoffset, nYoffset, nPrevXoffset, nPrevYoffset):
	if nPrevXoffset < nXoffset:
	    dir_ = 1
	else:
	    dir_ = -1 
	for i in numpy.arange (nPrevXoffset, nXoffset + dir_ * self.dicScanParam['StepSize'][0], \
			dir_ * self.dicScanParam['StepSize'][0]):
	    self.oStm.set_scandacs(self.XPOSITIONER ,i)
            time.sleep(5 * self.nPreSpectrumDelay/1000.0)
	if nPrevYoffset < nYoffset:
	    dir_ = 1
	else:
	    dir_ = -1 
	for i in numpy.arange(nPrevYoffset, nYoffset + dir_ * self.dicScanParam['StepSize'][0], \
			dir_*self.dicScanParam['StepSize'][0]):
	    self.oStm.set_scandacs(self.YPOSITIONER ,i)
            time.sleep(10 * self.nPreSpectrumDelay/1000.0)
	return

    def vGoTo(self, nTargetBias):
	"""
	Sets bias to the desired level
	"""
	if self.nCurrentBias == nTargetBias:
	    return
	step = self.oSpectro.MIN_STEPSIZE 
	if self.nCurrentBias > nTargetBias:
	   step *= -1
	while (self.nCurrentBias != nTargetBias): 
	    self.nCurrentBias += step
	    self.vSetBiasHandler(self.nCurrentBias)
	    #time.sleep(self.nPreSpectrumDelay/1000.0)
	return
	
    ############ HANDLER FUNCTION ##############
    def vSetBiasHandler(self, nBias):
	"""
	Sets Bias Voltage
	"""
	self.oStm.set_bias(nBias)
	return


    def afSpectroSweepHandler(self, np, start, step, delay, mavg, channel_mask = 1, retrace = False):
	'''
	Sent out firmware command for trace/retrace spectroscopy
	'''
	if retrace == False:
		arVal = self.oStm.simul_spectro_sweep(np, start, step, delay, mavg, channel_mask)
	else:
		arVal = self.oStm.simul_spectro_retrace_sweep(np, start, step, delay, mavg, channel_mask)

	if channel_mask == 1:	
            mv = [val * -1.0 for val in arVal]  # Fix Quadrants of IV plot
	    return mv
	arVal [0] = [val * -1.0 for val in arVal [0]]  # Fix Quadrants for I values
	return arVal
