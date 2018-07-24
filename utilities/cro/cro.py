#######################
#   CRO Class         #
#######################
import numpy
import app_cro
import stm7 as stm

VOLTS_RES	= 10

__DEBUG__ 	= True
if __DEBUG__ == True:
	from Tkinter import *

def cro(f=None, oStm = None):
    """
    Returns cro object
    """
    if not f:
	root = Tk()
	oAppCRO = app_cro.app_cro()
	oAppCRO.createCROwindow(root)
	oCRO = CRO(oAppCRO, oStm)
	root.title('Oscilloscope')
	root.mainloop()
	return
    else:
	oAppCRO = app_cro.app_cro()
	oAppCRO.createCROwindow(f)
	oCRO = CRO(oAppCRO, oStm)
    	return oCRO

class CRO:

    def __init__(self, oAppCRO, oStm):
	"""
	Class Contructor : CRO 
	"""
	self.oAppCRO = oAppCRO
	self.oStm = oStm
	self.MIN_VOLTS_PER_DIV = 10	# mV
	self.MAX_VOLTS_PER_DIV = 3500	# mV

	self.TURNS = 200
	self.dicScanParam = None
	self.acCouplingVar = BooleanVar()
	self.acCouplingVar.set (True)
	self.fineSlopeAdjustVar = BooleanVar()
	self.fineSlopeAdjustVar.set (True)
	self.correctSlopeFlag = False 
	self.slopeAdjustQualityDisplayFlag = True 
	self.selectSlopePot(stm.XSLOPE_POT)
	self.vRescaleYaxis()
	self._configureCB()
	return


    def _configureCB(self):
	"""
	Attaches Callbacks to CROGui widgets 
	"""
	self._initConfigure()
	self.Xrange = self.oAppCRO.nGraphArea[2] - self.oAppCRO.nGraphArea[0]	
	self.Yrange = self.oAppCRO.nGraphArea[3] - self.oAppCRO.nGraphArea[1]	
	return

    def _initConfigure(self):
	"""
	Performs initial Specroscopy Settings
	"""
	self.oAppCRO.ScaleVoltsPerDiv.configure (from_ = self.MIN_VOLTS_PER_DIV, \
						to = self.MAX_VOLTS_PER_DIV, \
						resolution = VOLTS_RES, \
						command = self.vRescaleYaxisCB)
	'''
	self.oAppCRO.CBCouplingAC.configure (variable = self.acCouplingVar)
	'''
	self.oAppCRO.ScaleXSlope.configure(to=self.TURNS)
	self.oAppCRO.ScaleYSlope.configure(to=self.TURNS)

	prevPotValues = stm.readPotLog()
	pot = stm.XSLOPE_POT
	prevVal = prevPotValues[pot]
	turns = self.TURNS * \
			prevVal / stm.POT_VALUES[pot]
	self.oAppCRO.ScaleXSlope.set(turns)
	if self.oStm.bValidDevice():
		self.oStm.set_pot(pot, prevVal)
	# Default Mode is Horizontal, so update Dial w.r.t XSlope Pot
	self.updatePotDial(prevVal)

	pot = stm.YSLOPE_POT
	prevVal = prevPotValues[pot]
	turns = self.TURNS * \
			prevVal / stm.POT_VALUES[pot]
	self.oAppCRO.ScaleYSlope.set(turns)
	if self.oStm.bValidDevice():
		self.oStm.set_pot(pot, prevVal)

	self._KeyBindings()

	for i in range(19):	# initialize to 200mV/div
	    self.vChangeVoltsPerDiv('up')
	self.oAppCRO.ScaleXSlope.configure(command=self.setPotCB)
	self.oAppCRO.ScaleYSlope.configure(command=self.setPotCB)
	self.oAppCRO.BtnSlopeAdjustQuality.config(command = self.showSlopeAdjustQualityCB)
	self.oAppCRO.CB_SlopeAdjustQuality.configure (variable = self.fineSlopeAdjustVar, \
							command = self.fineSlopeAdjustCB)
	return

    def _KeyBindings(self):
	"""
	Keyboard bindings for different functions
	"""
	self.oAppCRO.croGroup.bind('<Right>', self.vIncVoltage)
	self.oAppCRO.croGroup.bind('<Left>', self.vDecVoltage)
	return

    def vShowTrace(self, sweepline, dicScanParam):
	imageSize = dicScanParam['ImageSize'][0]
	stepDelay = dicScanParam['Delay']		# in us
	arrTrace = numpy.zeros ((imageSize, 2), 'f')
	arrRetrace = numpy.zeros ((imageSize, 2), 'f')
	arrTrace [:, 0] = range (imageSize) 
	arrTrace [:, 0] *= stepDelay / 1e3		# time axis (now in ms)
	arrRetrace [:, 0] = arrTrace [:, 0]
	arrTrace [:, 1]= sweepline [ :imageSize] 	# voltage axis (in mV)
	arrRetrace [:, 1]= sweepline [ : imageSize -1 : -1] 	# voltage axis (in mV)
	if self.acCouplingVar.get() == True:
		arrTrace [:, 1] = self.acCoupling(arrTrace [:, 1])
		arrRetrace [:, 1] = self.acCoupling(arrRetrace [:, 1])
	if self.correctSlopeFlag == True:
		self.correctSlope(arrTrace, arrRetrace)
	xyTrace = self.vt2xy(arrTrace)
	xyRetrace = self.vt2xy(arrRetrace)
	self.vPlotSignal(xyTrace, xyRetrace)
	return

    def acCoupling(self, trace):
	trace -= trace.mean() 	# ac coupling 
	return trace

    def vt2xy(self, vt):
	vt[:, 1] -= self.yll*1.0
        vt[:, 0] -= vt[:, 0].min()
        vt[:, 1] = (vt[:, 1] * -self.Yrange) / (self.yul*1.0-self.yll) + self.oAppCRO.nGraphArea[3]
        vt[:, 0] = (vt[:, 0] * self.Xrange) / (vt[:, 0].max()+0.0001) + self.oAppCRO.nGraphArea[0]
	vt[:, 1] = numpy.clip(vt[:,1], self.oAppCRO.nGraphArea[1], self.oAppCRO.nGraphArea[3])
	return vt

    def vPlotSignal(self, xyTrace, xyRetrace = None):
	try:
	    self.oAppCRO.CanGraph.delete(self.lineTrace)
	    self.oAppCRO.CanGraph.delete(self.lineRetrace)
	except:
	    pass
	self.lineTrace = self.oAppCRO.CanGraph.create_line(xyTrace.tolist(), fill='yellow', width=2)
	self.lineRetrace = self.oAppCRO.CanGraph.create_line(xyRetrace.tolist(), fill='pink', width=2, dash = (3,1))
	self.oAppCRO.croGroup.update()
	return


    def getSelectedPotVal(self):
	if self.selectedPot == stm.XSLOPE_POT:
		val = float(self.oAppCRO.ScaleXSlope.get())
	if self.selectedPot == stm.YSLOPE_POT:
		val = float(self.oAppCRO.ScaleYSlope.get())
	return val

    def vRescaleYaxisCB(self, event):
	self.vRescaleYaxis()
	return


    def setPotCB(self, event):
	val = self.getSelectedPotVal()
	self.setPot(val)
	self.updatePotDial(val)
	return


    def updatePotDial(self, val):
	# Since Dial Had 10 turns
	dial_turns = 10 
	majorno = int (val / dial_turns)
	minorno = int ((val % dial_turns) * 10)
	text = 'SL: ' + str(majorno) + ':' + str(minorno)
	self.updateDialDisplay(text)
	return


    def vRescaleYaxis(self, dicScanParam = None):
	if dicScanParam != None:
		self.dicScanParam = dicScanParam 
	nVoltsPerDiv = int(self.oAppCRO.ScaleVoltsPerDiv.get())
	self.yul = self.oAppCRO.nYDiv/2 * nVoltsPerDiv 
	self.yll = -self.yul
	self.vUpdateYText(nVoltsPerDiv)
	return

    '''
    def vRescaleXaxis(self):
	fMsecPerDiv = int(self.oAppCRO.ScaleMsecPerDiv.get())
	self.xul = self.oAppCRO.nXDiv/2 * fMsecPerDiv 
	self.xll = 0 
	self.vUpdateXText(fMsecPerDiv)
	return
    '''
    def vIncVoltage(self, *args):
	self.vChangeVoltsPerDiv('up')
	return

    def vDecVoltage(self, *args):
	self.vChangeVoltsPerDiv('down')
	return

    def vChangeVoltsPerDiv(self, dir):
	nVoltsPerDiv = int(self.oAppCRO.ScaleVoltsPerDiv.get())
	if dir == 'up':
	    if nVoltsPerDiv == self.MAX_VOLTS_PER_DIV:
		return
	    else:
		self.oAppCRO.ScaleVoltsPerDiv.set(nVoltsPerDiv + VOLTS_RES)
	if dir == 'down':
	    if nVoltsPerDiv == self.MIN_VOLTS_PER_DIV:
		return
	    else:
		self.oAppCRO.ScaleVoltsPerDiv.set(nVoltsPerDiv - VOLTS_RES)
	return

    def vUpdateYText(self, nVoltsPerDiv):
	value, units = self.calibrate(nVoltsPerDiv)
	if value == None:
		return
	#self.oAppCRO.LblVoltsPerDiv.configure (text = value + units + '/Div')
	text = value + units + '/Div'
	self.vUpdateYScale(text)
	return

    def calibrate(self, nVoltsPerDiv):
	if self.dicScanParam == None:
		return str(nVoltsPerDiv), 'mV' 
	if self.dicScanParam['ChannelNames'][0] == 'CH Mode':
		value = str(nVoltsPerDiv) 
		return value, 'pA'
	if self.dicScanParam['ChannelNames'][0] == 'CC Mode' or \
		self.dicScanParam['ChannelNames'][0] == 'Topography':
		value = (nVoltsPerDiv / 1e3) * self.dicScanParam['HVAGainFactor'] * \
				self.dicScanParam['ZCalibration'] / self.dicScanParam['Gain']
		value = '%.2f' % value 
		return value, 'nm'
	
	return

    def vUpdateYScale(self, text):
	try:
	    self.oAppCRO.CanGraph.delete(self.TextYscale)
	except:
	    pass
	self.TextYscale = self.oAppCRO.CanGraph.create_text(\
				self.oAppCRO.arrYTextLoc, \
				text=text, \
				fill='yellow', anchor=SE)
	#self.oAppCRO.croGroup.update()
	return


    def updateDialDisplay(self, text):
	try:
	    self.oAppCRO.CanGraph.delete(self.TextDial)
	except:
	    pass
	self.TextDial = self.oAppCRO.CanGraph.create_text(\
				self.oAppCRO.arrDialTextLoc, \
				text=text, \
				fill='yellow', anchor=SW)
	#self.oAppCRO.croGroup.update()
	return


    def selectSlopePot(self, pot):
	self.selectedPot = pot
	self.updateSlopeDisplay()
	val = self.getSelectedPotVal()
	self.updatePotDial(val)
	return

    def updateSlopeDisplay(self):
	if self.selectedPot == stm.XSLOPE_POT:
		self.oAppCRO.showXSlopeControl()
	if self.selectedPot == stm.YSLOPE_POT:
		self.oAppCRO.showYSlopeControl()
	return


    def setPot(self, val, pot = None):
	val = val * stm.POT_VALUES[self.selectedPot] / self.TURNS
	self.oStm.set_pot(self.selectedPot, val)
	return

    def calculateSlope(self, dataxy):
	x = dataxy[:, 0]
	y = dataxy[:, 1]
	# Slope calculation from http://faculty.cs.niu.edu/~hutchins/csci230/best-fit.htm
	slope = ((x * y).sum() - x.sum() * y.mean()) / ((x * x).sum() - x.sum() * x.mean())
	return slope


    def correctSlope(self, arrTrace, arrRetrace):
	tslope = self.calculateSlope(arrTrace)
	rslope = self.calculateSlope(arrRetrace)
	#print '@@@ Trace Slope: ', tslope, ' Retrace Slope: ', rslope
	self.slopeRecord.append(tslope)
	if len(self.slopeRecord) > 1:
		self.changeSlope()
	return


    def changeSlope(self):
	if abs(self.slopeRecord[-1]) < 0.1:
		print 'Slope with acceptable limit'
		return
	if abs(self.slopeRecord[-1]) > abs(self.slopeRecord[-2]):
		pass
	return

    def adjustSlope(self, dir_):
	if dir_ == 1:
		dir_ = 'up'
	if dir_ == -1:
		dir_ = 'down'
	if self.selectedPot == stm.XSLOPE_POT:
		self.oAppCRO.ScaleXSlope.invoke(dir_)
	if self.selectedPot == stm.YSLOPE_POT:
		self.oAppCRO.ScaleYSlope.invoke(dir_)
	return

    def enableAutoCorrectSlope(self):
	self.slopeRecord = []
	self.correctSlopeFlag = True
	return


    def disableAutoCorrectSlope(self):
	self.correctSlopeFlag = False 
	return


    def showSlopeAdjustQualityCB(self):
	print 'Suuksham pole...'
	if self.slopeAdjustQualityDisplayFlag == True:
		self.showSlopeAdjustQuality()
		self.slopeAdjustQualityDisplayFlag = False
	else:
		self.selectSlopePot(self.selectedPot)
		self.slopeAdjustQualityDisplayFlag = True 

    def showSlopeAdjustQuality(self):
	self.oAppCRO.showFineSlopeAdjustControl()
	

    def fineSlopeAdjustCB(self, *args):
	if self.fineSlopeAdjustVar.get() == True:
	    self.oStm.fine_slope_adj()
	else:
	    self.oStm.coarse_slope_adj()
	return


if __name__ == '__main__':
    cro()
