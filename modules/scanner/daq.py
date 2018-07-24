#################
#   DAQ Class   #
#################
import scanner 
import time
import numpy
import modules.offset.offset as offset
import info
import utilities.cro.cro as cro
import lib.stm7 as stm
import utilities.lia.xlia as xlia

SCAN = 0
RETRACE = 1

def daq(oScanner):
    """
    Returns DAQ object
    """
    d = DAQ(oScanner)
    return d

class DAQ:


    def __init__(self, oScanner):
	"""
	Class Contructor : DAQ
	"""
	self.oScanner = oScanner
	self.__param = {}
	self.vSetDelay(0.001)	
	self.bHiResScan = False
	self.alter = 1
	return

    def vSetDelay(self, delay):
	"""
	Creates an attribute delay of class DAQ and assigns delay time to it
	"""
	self.delay = delay
	return

    def vGetScanParameters(self):
	"""
	Gets scan Parameters from object scanner(from scanner gui)
	"""
	self.__param['Direction'] = self.oScanner.ScanDirectionVar.get()
	self.__param['Delay'] = self.oScanner.nReadDelay()
	if self.oScanner.bXLAreaVar.get():
	    self.__param['StepSize'] = [self.oScanner.nReadStepSize()[0] / scanner.HVA_GAIN] * 2
	else:
	    self.__param['StepSize'] = self.oScanner.nReadStepSize()
	self.__param['ImageSize'] = self.oScanner.nReadImageSize()
	if self.__param['ImageSize'][0] > 256:
	    print 'HiRes Scan Mode', 
	    self.bHiResScan = True
	else:
	    self.bHiResScan = False 
	self.__param['Gain'] = self.oScanner.nReadGain()
	self.__param['AreaChoice'] = self.oScanner.AreaVar.get()
	self.__param['DigitizationMode'] = self.oScanner.DigitizationModeVar.get()
	self.__param ['NoOfChannels'] = self.oScanner.NO_OF_CHANNELS
	if self.__param ['NoOfChannels'] > 1:
	    print 'Simultaneous Scan Mode Active' 
	    self.bSimulScan = True
	    self.__param ['XLIA_Param'] = xlia.getXLIA_ParametersFromFile ()
	else:
	    self.bSimulScan = False 
	self.__param ['ChannelNames'] = self.oScanner.CHANNEL_NAMES
	self.__param ['LIA_Status'] = self.oScanner.LIA_StatusVar.get()
	self.__param['XOffset'] = self.oScanner.oOffset.fReadXoffset()
	self.__param['YOffset'] = self.oScanner.oOffset.fReadYoffset()		
	self.__param['XLArea'] = self.oScanner.bXLAreaVar.get()
	
	self.__param['XCalibration'] = scanner.fGetPiezoXCalibration()	# nm/V 
	self.__param['YCalibration'] = self.__param['XCalibration']
	self.__param['ZCalibration'] = scanner.fGetPiezoZCalibration()	# nm/V 
	self.__param['HVAGainFactor'] = scanner.fGetHVAGain()

	self.__param['TCSetpoint'] = stm.readCurrentSetpoint()	# pA
	self.__param['SampleBias'] = stm.getCurrentSampleBias()	# V

	self.__param['AC_Coupling'] = self.oScanner.getCouplingStatus()
	self.__param['PreScanSetupDelay'] = self.oScanner.getPreScanSetupDelay()

	self.__param['Date'] = time.asctime()
	self.__param['Instrument'] = stm.__INSTRUMENT__
	self.__param['Software'] = stm.__SOFTWARE__

	self.fScanImageData = numpy.zeros(self.__param['ImageSize'], 'f') 
	self.fRetImageData = numpy.zeros(self.__param['ImageSize'], 'f')
	self.fGrayScanImage = self.fScanImageData.copy() 
	self.fGrayRetImage = self.fRetImageData.copy() 
	return self.__param 

    def initializeTipLocationToCenter(self):
	self.nStartPoint = [0] * 2
	self.nStartPoint[0] = int(-(self.__param['ImageSize'][0] * self.__param['StepSize'][0])/2)
	self.nStartPoint[1] = int(-(self.__param['ImageSize'][1] * self.__param['StepSize'][1])/2)
	self.vDacSelection()
	print 'Taking Tip to Initial Postion ....'

	delay = self.__param['Delay']
	mode = self.__param['DigitizationMode']
	SCAN_SETUP_DELAY = self.__param['PreScanSetupDelay']	# in ms
	if (mode == self.oScanner.TCMODE) or (mode == self.oScanner.ZMODE):
		if delay > SCAN_SETUP_DELAY * 1e3:
	                delay = self.__param['Delay'] / 1e3     # Delay is in us
		else:
	                delay = SCAN_SETUP_DELAY     # Delay is in ms
	if (mode == self.oScanner.LDOS_MODE) or (mode == self.oScanner.LBH_MODE):
		if delay > SCAN_SETUP_DELAY:
	                delay = self.__param['Delay']     # Delay is in ms
		else:
	                delay = SCAN_SETUP_DELAY     # Delay is in ms

	delay = delay / 1e3	# in seconds

	for i in numpy.arange(0,self.nStartPoint[0]-self.__param['StepSize'][0],-self.__param['StepSize'][0]):
		self.vSetScanDacHandler(self.SweepDac, i)
               	time.sleep(delay)
	for i in numpy.arange(0,self.nStartPoint[1]-self.__param['StepSize'][1],-self.__param['StepSize'][1]):
		self.vSetScanDacHandler(self.StepDac, i)
               	time.sleep(delay)
        print "X and Y are taken to Initial Position"
	time.sleep(1)
	return

    def initializeTipLocationToCorner(self):
	self.nStartPoint = [stm.cdac[stm.XDAC]] * 2
	self.vDacSelection()
	time.sleep(1)
	return


    def vDacSelection(self):
	"""
	In Classical Horz and Vertical Scan :
	One dac sweeps the entire line - scan n retrace, 
	while another take a single step after the sweep is complete
	so we can call them as Sweep Dac and Step Dac
	Therefore, in HORZ case:
		Sweep Dac = (BIG)XDAC
		Step Dac = (BIG)YDAC
	In VERT case:
		Sweep Dac = (BIG)YDAC
		Step Dac = (BIG)XDAC
	This fuction takes this decision
	"""
	if self.__param['Direction'] == self.oScanner.HORIZONTAL:
		self.bFlip = False
		if self.__param['AreaChoice'] == self.oScanner.SMALL_AREA:
			self.SweepDac = stm.XDAC
			self.StepDac = stm.YDAC
	if self.__param['Direction'] == self.oScanner.VERTICAL:
		self.bFlip = True 
		if self.__param['AreaChoice'] == self.oScanner.SMALL_AREA:
			self.SweepDac = stm.YDAC
			self.StepDac = stm.XDAC
		self.nStartPoint.reverse()
		self.__param['ImageSize'].reverse()
		self.__param['StepSize'].reverse()
	return

    def vNewImages(self, noc = 1):
	"""
	Creates a blank new image at the background when scan has started 
	"""
	self.fScanImageData = numpy.zeros(self.__param ['ImageSize'], 'f') 
	self.fRetImageData = numpy.zeros(self.__param ['ImageSize'], 'f')
	if noc > 1:
	    self.fScanImageData = numpy.zeros( [noc] + self.__param ['ImageSize'], 'f') 
	    self.fRetImageData = numpy.zeros( [noc] + self.__param ['ImageSize'], 'f')
	    #self.fScanImageData = [self.fScanImageData] * noc
	    #self.fRetImageData = [self.fRetImageData] * noc
	self.oScanner.oImaging.vCreateNewImages(self.__param)
	return

    def vRefresh(self, step, noc = 1):
	"""
	Converts  gray the whole matrix
	Splash after every N scan lines
	"""
	if self.alter == -1:		# backward scan in movie mode scanning
	    self.vShowAltSlice(step, noc)
	else:
	    self.vShowSlice(step, noc)
	return

    def vShowSlice(self, step, noc):
	"""
	Passes the update data matrix of forward scan to imaging section 	
	"""
	bDump = False
	if (self.oScanner.bScanStatusVar.get() == scanner.OVER) or \
				(step == self.__param['ImageSize'][1]-1):
	    bDump = True
	    #print 'Dumping Now'
	if self.bFlip == True:		# VERT. SCAN
	    if noc == 1:
	    	self.fScanImageData[:,:step+1] = self.fScanImageData[:,:step+1]
	    	self.fRetImageData[:,:step+1] = self.fRetImageData[:,:step+1]
	    else:
	    	self.fScanImageData [:, :, :step + 1] = self.fScanImageData [:, :, :step + 1]
	    	self.fRetImageData [:, :, :step + 1] = self.fRetImageData [:, :, :step + 1]
	    if self.oScanner.bRecordMovie.get() == True:
		self.oScanner.oImaging.vRenewScan(self.fScanImageData,self.__param, bDump)
		self.oScanner.oImaging.vRenewRet(self.fRetImageData,self.__param, bDump)
	    else:
		if noc == 1:
		    self.oScanner.oImaging.vRenewScan(self.fScanImageData[:,:step+1],self.__param, bDump)
		    self.oScanner.oImaging.vRenewRet(self.fRetImageData[:,:step+1],self.__param, bDump)
		else:
		    self.oScanner.oImaging.vRenewScan (self.fScanImageData [:, :, :step + 1], \
								self.__param, bDump, noc)
		    self.oScanner.oImaging.vRenewRet (self.fRetImageData [:, :, :step + 1], \
								self.__param, bDump, noc)
	else: 				# HORZ. SCAN
	    if noc == 1:
	    	self.fScanImageData[:step+1] = self.fScanImageData[:step+1]
	    	self.fRetImageData[:step+1] = self.fRetImageData[:step+1]
	    else:
	    	self.fScanImageData [:, :step + 1] = self.fScanImageData [:, :step + 1]
	    	self.fRetImageData [:, :step + 1] = self.fRetImageData [:, :step + 1]
	    if self.oScanner.bRecordMovie.get()==True:
		self.oScanner.oImaging.vRenewScan(self.fScanImageData, self.__param, bDump)
		self.oScanner.oImaging.vRenewRet(self.fRetImageData, self.__param, bDump)
	    else:
		if noc == 1:
		    self.oScanner.oImaging.vRenewScan(self.fScanImageData[:step+1], self.__param, bDump)
		    self.oScanner.oImaging.vRenewRet(self.fRetImageData[:step+1], self.__param, bDump)
		else:
		    self.oScanner.oImaging.vRenewScan (self.fScanImageData [:, :step + 1], \
								self.__param, bDump, noc)
		    self.oScanner.oImaging.vRenewRet (self.fRetImageData [:, :step + 1], \
								self.__param, bDump, noc)
	return

    def vShowAltSlice(self, step, noc):
	"""
	Converts float image data into gray scale and displays it onto the image canvas
	"""
	bDump = False
	if (self.oScanner.bScanStatusVar.get() == scanner.OVER) or \
				(step == self.__param['ImageSize'][1]-1):
	    bDump = True
	if self.bFlip == True:		# VERT. SCAN
	    if noc == 1:
	    	self.fScanImageData[:,-step-1:] = self.fScanImageData[:,-step-1:]
	    	self.fRetImageData[:,-step-1:] = self.fRetImageData[:,-step-1:]
	    else:
	    	self.fScanImageData [:, :,-step-1:] = self.fScanImageData [:, :,-step-1:]
	    	self.fRetImageData [:, :,-step-1:] = self.fRetImageData [:, :,-step-1:]
	    self.oScanner.oImaging.vRenewScan(self.fScanImageData, self.__param, bDump)
	    self.oScanner.oImaging.vRenewRet(self.fRetImageData, self.__param, bDump)
	else:				# HORZ. SCAN
	    if noc == 1:
	    	self.fScanImageData[-step-1:] = self.fScanImageData[-step-1:]
	    	self.fRetImageData[-step-1:] = self.fRetImageData[-step-1:]
	    else:
	    	self.fScanImageData [:, -step-1:] = self.fScanImageData [:, -step-1:]
	    	self.fRetImageData [:, -step-1:] = self.fRetImageData [:, -step-1:]
	    self.oScanner.oImaging.vRenewScan(self.fScanImageData, self.__param, bDump)
	    self.oScanner.oImaging.vRenewRet(self.fRetImageData, self.__param, bDump)
	return

    def vRefreshDisplay(self, *args):
	"""
	Refresh image after every 10 scan lines
	"""
	self.vRefresh()
	return

    def vSingleScan(self, noc = 1):
	"""
	Scan whole image once
	"""
	self.alter = 1
	self.oScanner.oCRO.vRescaleYaxis(self.__param)	# Update CRO Y scale according to imaging mode
	acCoupling = self.__param['AC_Coupling']
	self.step_value = self.nStartPoint[1]
	start = time.time()
	if self.bHiResScan == True:
	    if noc > 1:
	        self.vNewImages (noc)
	    	self.vCoreSimultaneousScanning (noc, acCoupling)
	    else:
		self.vNewImages ()
		self.vCoreHiResScanning (acCoupling) 
	else:
	    if noc > 1:
	        self.vNewImages (noc)
		self.vCoreSimultaneousScanning (noc, acCoupling)
	    else:
	        self.vNewImages ()
	        self.vCoreScanning(acCoupling)
	self.oScanner.bScanStatusVar.set(scanner.OVER)
	interval = time.time() - start
	print '###### Time Taken ######', interval
	return

    def vCoreScanning(self, acCoupling = True):
	"""
	Scans and updates image at every 10 scan lines 
	"""
	if self.__param['DigitizationMode'] == self.oScanner.TCMODE:
		self.oScanner.oStm.set_TCmode()
		self.oScanner.oStm.hold_on()	# in CH mode, put in FB off mode just before scan

	im_size = self.__param['ImageSize'][0]
	dac16bit_sp = int ((self.nStartPoint[0] - stm.cdac[self.SweepDac]) / stm.mdac[self.SweepDac])
	dac16bit_step = int (self.__param['StepSize'][0] / stm.mdac[self.SweepDac])
	for step in range(self.__param['ImageSize'][1]):
	    #sweepline = []
	    sweepline = numpy.zeros(im_size * 2, 'f') 
	    sweepline[:] = self.afSweepScanHandler(\
				im_size, \
				dac16bit_sp, \
				dac16bit_step, \
				self.__param['Delay'], \
				self.SweepDac
				)
	    if acCoupling == True:
		sweepline[ : im_size] -= sweepline[ : im_size].mean()
		sweepline[im_size : ] -= sweepline[im_size : ].mean()
	    if self.alter == -1:
		self.vStoreAltLines(step, sweepline)
	    else:
		self.vStoreLines(step, sweepline)
	    if self.oScanner.bScanStatusVar.get() == scanner.OVER:
		break
	    self.step_value += (self.alter*self.__param['StepSize'][1])
	    self.vSetScanDacHandler(self.StepDac, self.step_value)

	    ######### Show CRO Trace ############## 
	    #if self.oScanner.oToolBar.SoftCRO_Instance:
	    self.oScanner.oCRO.vShowTrace(sweepline, self.__param)

	    ######### Show Progress Lines############## 
	    if self.bFlip:
	   	self.oScanner.oImaging.vShowVScanProgress(int(step))		# for Showing Scan Progress
	    else:
		self.oScanner.oImaging.vShowHScanProgress(int(step))		# for Showing Scan Progress

	    ######### Splash Acquired Image Slice ############## 
	    if (step%self.oScanner.nDisplaylines) == 0:	
	    	self.vRefresh(step)
	    self.oScanner.MainMaster.update()
	self.vRefresh(step)
	print 'Lines scanned: ', step
	self.oScanner.oStm.hold_off()	# After completing the scan put scanner back in FB On mode
	return

    def vCoreHiResScanning(self, acCoupling = True ):
	"""
	Scans and updates image at every 'nDisplaylines' lines 
	"""
	if self.__param['DigitizationMode'] == self.oScanner.TCMODE:
		self.oScanner.oStm.set_TCmode()
		self.oScanner.oStm.hold_on()	# in CH mode, put in FB off mode just before scan

	im_size = self.__param['ImageSize'][0]
	dac16bit_sp = int ((self.nStartPoint[0] - stm.cdac[self.SweepDac]) / stm.mdac[self.SweepDac])
	dac16bit_step = int (self.__param['StepSize'][0] / stm.mdac[self.SweepDac])
	for step in range(self.__param['ImageSize'][1]):
	    #sweepline = []
	    sweepline = numpy.zeros(im_size * 2, 'f') 
	    sweepline[ : im_size] = self.afHiResScanHandler(\
				im_size, \
				dac16bit_sp, \
				dac16bit_step, \
				self.__param['Delay'], \
				self.SweepDac,\
				0 \
				# Scan
				)
	    dac16bit_ep = dac16bit_sp + (im_size - 1) * dac16bit_step	# starts from the endpoint
	    
	    sweepline[im_size : ] = self.afHiResScanHandler(\
							im_size, \
							dac16bit_ep, \
							dac16bit_step, \
							self.__param['Delay'], \
							self.SweepDac,\
							1 \
							# Retrace 
							)
	    #sweepline.extend(retline) 
	    if acCoupling == True:
		sweepline[ : im_size] -= sweepline[ : im_size].mean()
		sweepline[im_size : ] -= sweepline[im_size : ].mean()

	    if self.alter == -1:
		self.vStoreAltLines(step, sweepline)
	    else:
		self.vStoreLines(step, sweepline)
	    if self.oScanner.bScanStatusVar.get() == scanner.OVER:
		break
	    self.step_value += (self.alter*self.__param['StepSize'][1])
	    self.vSetScanDacHandler(self.StepDac, self.step_value)

	    ######### Show CRO Trace ############## 
	    #if self.oScanner.oToolBar.SoftCRO_Instance:
	    self.oScanner.oCRO.vShowTrace(sweepline, self.__param)

	    ######### Show Progress Lines############## 
	    if self.bFlip:
	   	self.oScanner.oImaging.vShow_HR_VScanProgress(int(step))		# for Showing Scan Progress
	    else:
		self.oScanner.oImaging.vShow_HR_HScanProgress(int(step))		# for Showing Scan Progress

	    ######### Splash Acquired Image Slice ############## 
	    if (step%self.oScanner.nDisplaylines) == 0:	
	    	self.vRefresh(step)
	    self.oScanner.MainMaster.update()
	self.vRefresh(step)
	print 'Lines scanned: ', step
	self.oScanner.oStm.hold_off()	# After completing the scan put scanner back in FB On mode
	return

    def vCoreSimultaneousScanning(self, no_of_channels, acCoupling = True):
	"""
	Scans and updates image at every 'nDisplaylines' lines 
	For LDOS and LBH modes
	"""
	#no_of_channels = 3
	im_size = self.__param['ImageSize'][0]
	dac16bit_sp = int ( (self.nStartPoint [0] - stm.cdac [self.SweepDac]) / stm.mdac [self.SweepDac])
	dac16bit_step = int (self.__param['StepSize'][0] / stm.mdac [self.SweepDac])
	for step in range (self.__param ['ImageSize'] [1]):
	    sweepline = []
	    sweepline = self.simultaneousScanHandler (\
				im_size, \
				dac16bit_sp, \
				dac16bit_step, \
				self.__param ['Delay'], \
				self.SweepDac,\
				SCAN, \
				no_of_channels \
				)
	    dac16bit_ep = dac16bit_sp + (im_size - 1) * dac16bit_step	# starts from the endpoint
	    
	    retline = self.simultaneousScanHandler ( \
				im_size, \
				dac16bit_ep, \
				dac16bit_step, \
				self.__param ['Delay'], \
				self.SweepDac,\
				RETRACE, \
				no_of_channels \
				)
	    for count in range (no_of_channels):
		sweepline [count].extend (retline [count])
		sweepline[count] = numpy.asarray(sweepline[count])
	    
	    if acCoupling == True:
	    	for count in range (no_of_channels):
			sweepline[count][ : im_size] -= sweepline[count][ : im_size].mean()
			sweepline[count][im_size : ] -= sweepline[count][im_size : ].mean()

	    if self.alter == -1:
		self.vStoreAltLines (step, sweepline, no_of_channels)
	    else:
		self.vStoreLines (step, sweepline, no_of_channels)

	    if self.oScanner.bScanStatusVar.get () == scanner.OVER:
		break
	    self.step_value += (self.alter * self.__param ['StepSize'] [1])
	    self.vSetScanDacHandler (self.StepDac, self.step_value)

	    ######### Show CRO Trace ############## 
	    #if self.oScanner.oToolBar.SoftCRO_Instance:
	    self.oScanner.oCRO.vShowTrace (sweepline [0], self.__param)

	    ######### Show Progress Lines############## 
	    if self.bFlip:
	   	#self.oScanner.oImaging.vShow_HR_VScanProgress (int (step))		# for Showing Scan Progress
		pass
	    else:
		#self.oScanner.oImaging.vShow_HR_HScanProgress (int (step))		# for Showing Scan Progress
		pass

	    ######### Splash Acquired Image Slice ############## 
	    if (step % self.oScanner.nDisplaylines) == 0:	
	    	self.vRefresh (step, no_of_channels)
	    self.oScanner.MainMaster.update ()
	self.vRefresh (step, no_of_channels)
	print 'Lines scanned: ', step
	return

    def vStoreLines(self, step, sweepline, noc = 1):
	"""
	Stores scan line data while moving from top to bottom
	"""
	if self.bFlip:
	    if noc == 1:
		self.fScanImageData [:, step] = sweepline [0 : self.__param ['ImageSize'] [0]] 	
		self.fRetImageData [:, step] = sweepline [:self.__param['ImageSize'][0] - 1 : -1]
	    else:
		for count in range (noc):
		    self.fScanImageData [count, :, step] = sweepline [count] [0 : self.__param ['ImageSize'] [0]] 	
		    self.fRetImageData [count, :, step] = sweepline [count] [:self.__param ['ImageSize'] [0] - 1 : -1]
	else:	
	    if noc == 1:
		self.fScanImageData [step] = sweepline [0 : self.__param ['ImageSize'] [0]] 	
		self.fRetImageData [step] = sweepline [:self.__param ['ImageSize'] [0] - 1 : -1]
	    else:
		for count in range (noc):
		    self.fScanImageData [count, step] = sweepline [count] [0 : self.__param ['ImageSize'] [0]] 	
		    self.fRetImageData [count, step] = sweepline [count] [:self.__param ['ImageSize'] [0] - 1 : -1]
	return 

    def vStoreAltLines(self, step, sweepline, noc = 1):
	"""
	Stores scan line data while moving from bottom to top
	"""
	if self.bFlip:
	    if noc == 1:
		self.fScanImageData [:, -step - 1] = sweepline[0 : self.__param['ImageSize'][0]] 	
		self.fRetImageData [:, -step - 1] = sweepline[: self.__param['ImageSize'][0]-1:-1]
	    else:
		for count in range (noc):
		    self.fScanImageData [count, :, -step - 1] = sweepline [count] [0 : self.__param ['ImageSize'] [0]] 	
		    self.fRetImageData [count, :, -step - 1] = sweepline [count] [:self.__param ['ImageSize'] [0] - 1 : -1]
	else:	
	    if noc == 1:
		self.fScanImageData [-step - 1] = sweepline [0 : self.__param ['ImageSize'] [0]] 	
		self.fRetImageData [-step - 1] = sweepline [: self.__param['ImageSize'] [0] - 1 : -1]
	    else:
		for count in range (noc):
		    self.fScanImageData [count, -step - 1] = sweepline [count] [0 : self.__param ['ImageSize'] [0]] 	
		    self.fRetImageData [count, -step - 1] = sweepline [count] [:self.__param ['ImageSize'] [0] - 1 : -1]
	return

    def vMovieScan(self, nof=2, noc = 1):
	"""
	Create Movie frames containing both scan and retrace image data
	"""
	self.vNewImages (noc)
	self.alter = 1
	self.step_value = self.nStartPoint[1]
	start = time.time()
	self.aafFrames = []
	self.oScanner.bScanStatusVar.set(scanner.NOTOVER)
	for i in range(nof):
	    if noc > 1:
		self.vCoreSimultaneousScanning (noc)
	    else:
	        self.vCoreScanning()
	    self.aafFrames.append([self.fScanImageData.copy(), self.fRetImageData.copy()])
	    self.alter *= -1
	    self.oScanner.bRecordMovie.set(True)
	self.oScanner.bScanStatusVar.set(scanner.OVER)
	interval = time.time() - start
	print '###### Time Taken for Movie ######', interval
	return

    def restoreTipLocationToCenter(self):
	"""
	After scan brings Tip back to the Center rest position
	"""
	direc = 1
	for i in numpy.arange(self.nStartPoint[0], \
				self.__param['StepSize'][0], \
				self.__param['StepSize'][0]):
	    self.vSetScanDacHandler(self.SweepDac, i)
            time.sleep( self.delay )
	if self.step_value < 0:
	    direc = -1
	for i in numpy.arange(self.step_value, \
				0 - direc * self.__param['StepSize'][1], \
				-direc * self.__param['StepSize'][1]):
	    self.vSetScanDacHandler(self.StepDac, i)
            time.sleep( self.delay )
        print "X and Y are returned to Rest Position"
	return

    def restoreTipLocationToCorner(self):
	"""
	After scan brings Tip back to the Corner rest position
	"""
	for i in numpy.arange(self.step_value, \
				self.nStartPoint[1], \
				-1.0 * self.__param['StepSize'][1]):
	    self.vSetScanDacHandler(self.StepDac, i)
            time.sleep( self.delay )
        print "X and Y are returned to Corner Rest Position"
	return


    def afGetImageData(self):
	"""
	Return movie frames to scanner module for saving
	"""
	return [self.fScanImageData, self.fRetImageData]

    def aafGetMovieData(self):
	"""
	Return movie frames to scanner module for saving
	"""
	return self.aafFrames

    def vCalculateDisplayRefreshlines(self):
	"""
	Calculates number of scan lines to be waited before flashing scan data
	"""
	if self.oScanner.nDisplayRefreshVar.get()==1:
		self.vCalculateRefreshlines(1)
	if self.oScanner.nDisplayRefreshVar.get()==5:
		self.vCalculateRefreshlines(5)
	if self.oScanner.nDisplayRefreshVar.get()==10:
		self.vCalculateRefreshlines(10)
	if self.oScanner.nDisplayRefreshVar.get()==25:
		self.vCalculateRefreshlines(25)
	if self.oScanner.nDisplayRefreshVar.get()==50:
		self.vCalculateRefreshlines(50)
	if self.oScanner.nDisplayRefreshVar.get()==100:
		self.vCalculateRefreshlines(100)
	return

    def vCalculateRefreshlines(self, percentage):
	"""
	Real Scan line Count takes place here
	"""
	if (percentage == 1) or (self.__param ['NoOfChannels'] > 1):	
		# for Simul. 'generally LIA' scans ... single line refresh mode
		self.oScanner.nDisplaylines = 1
	else:
		self.oScanner.nDisplaylines = int((self.__param['ImageSize'][0]*percentage)/100)
	return 

    ############### HANDLER FUNCTIONS ###################
    def vSetScanDacHandler(self, dac, mV):
	"""
	Handler function for Scan dacs
	"""
	self.oScanner.oStm.set_scandacs(dac, mV)
	return

    def afSweepScanHandler(self, np, start, step, delay, dac):
	"""
	Handler function for Sweep dacs
	Arguments :
		np    : int number of scan points
		start : int scan start location
		step  : int step size
		delay : int step delay
		dac   : int dac number
	"""
	''' ON-BOARD ADC '''
	#line = self.oScanner.oStm.filter_scan(np, start, step, delay, dac)
	''' ADD_ON CARD ADC '''
	line = self.oScanner.oStm.simultaneous_scan_dual_trace (np, start, step, delay, dac, noc = 1)
	return line

    def afHiResScanHandler(self, np, start, step, delay, dac, dir_, noc = 1):
	"""
	Handler function for Sweep dacs
	Arguments :
		np    : int number of scan points
		start : int scan start location
		step  : int step size
		delay : int step delay
		dac   : int dac number
		dir_  : 0: Scan, 1: Retrace
	"""
	''' ON-BOARD ADC '''
	#line = self.oScanner.oStm.hires_scan(np, start, step, delay, dac, dir_)
	''' ADD_ON CARD ADC '''
	line = self.oScanner.oStm.simultaneous_scan_single_trace_fast (np, start, step, delay, dac, dir_, noc)
	return line


    def simultaneousScanHandler(self, np, start, step, delay, dac, dir_ ,noc = 1):
	'''	
	np    : int number of scan points
	start : int scan start location
	step  : int step size
	delay : int step delay
	dac   : int dac number
	dir_  : 0: Scan, 1: Retrace
	noc   : 1 to 4 - no. of channels to be simultaneously scanned
		- TC/Z
		- In-Phase LIA Outout
		- Quadrature LIA Output
	'''
	# Slow scan is with step delay of >=1 ms for LDOS and LBH modes
	line = self.oScanner.oStm.simultaneous_scan_single_trace_slow (np, start, step, delay, dac, dir_, noc)
	arLine = numpy.asarray(line)
	arLine = arLine.reshape((-1, noc))	# unspecified rows: (-1), columns:noc
	chlines = []
	for count in range(noc):
	    line = arLine[:,count].tolist()
	    chlines.append(line)
	return chlines

