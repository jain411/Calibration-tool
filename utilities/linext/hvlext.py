############################
#   Horz. Line Ext Class   #
############################
from Tkinter import *
import numpy
import tkMessageBox
import pylab
import modules.scanner.scanner as scanner
import modules.scanner.imaging as imaging
import apps.dialogs as dialogs

HORIZONTAL	= 'H'
VERTICAL	= 'V'

canvas_font = (imaging.CANVAS_FONT, imaging.CANVAS_FONT_SIZE)

def hvlext(oImaging=None, mode='H'):
    """
    Returns HVLExt object
    """
    oHVLExt=HVLExt(oImaging, mode)
    return oHVLExt
	
class HVLExt:
	
    def __init__(self, oImaging, mode):
	"""
	Class Contructor : HVLExt
	"""
	self.oImaging = oImaging
	self.cScanOrientation = mode	# 'H' or 'V'
	try:
	    self.vDeleteline()
	except:
	    pass
	if not self.oImaging.bImagePresentVar.get():
	    tkMessageBox.showwarning('Blank','No Images on Display')
	    return
	if self.oImaging.bDumpVar.get():
	    tkMessageBox.showwarning('Dump','Dumped Image on Display, Line Extraction not supported here.')
	    return
	self.vHVLExt()
	return

    def vHVLExt(self):
	"""
	Gets Image Data and binds mouse with the image canvas
	"""
	self.afScanImageData = self.oImaging.afScanImageData.copy()
	self.afRetImageData = self.oImaging.afRetImageData.copy()
	self.nStepSize = self.oImaging.dicScanParam['StepSize'][0]
	if self.oImaging.dicScanParam.has_key('XLArea'):
	    if self.oImaging.dicScanParam['XLArea']:
		self.nStepSize *= scanner.XL_GAIN
	self.nImageSize = self.oImaging.dicScanParam['ImageSize']
	try:
	    self.nADCGain = self.oImaging.dicScanParam['Gain']
	except:
	    self.nADCGain = 1
	self.vActivateImageCanvas()
	dicGUISettings = dialogs.dicReadGUISettings()
	self.strLineColor = dicGUISettings['LEC']
	return

    def vActivateImageCanvas(self):
	"""
	Make the Canvas ready to show the horz. line below the mouse pointer, and display result on left click.
	"""
	self.oImaging.oAppImaging.CanvasScan.bind('<Button-1>', self.vShowLineCB)
	self.oImaging.oAppImaging.CanvasRetrace.bind('<Button-1>', self.vShowLineCB)
	self.oImaging.oAppImaging.CanvasScan.bind('<B1-Motion>', self.vShowLineCB)
	self.oImaging.oAppImaging.CanvasRetrace.bind('<B1-Motion>', self.vShowLineCB)
	self.oImaging.oAppImaging.CanvasScan.bind('<ButtonRelease-1>', self.vDisplayLinePlotCB)
	self.oImaging.oAppImaging.CanvasRetrace.bind('<ButtonRelease-1>', self.vDisplayLinePlotCB)
	return

    def vDeactivateImageCanvas(self):
	"""
	Removes mouse bindings with the Imaging Canvas
	"""
	self.oImaging.oAppImaging.CanvasScan.unbind('<Button-1>')
	self.oImaging.oAppImaging.CanvasRetrace.unbind('<Button-1>')
	self.oImaging.oAppImaging.CanvasScan.unbind('<B1-Motion>')
	self.oImaging.oAppImaging.CanvasRetrace.unbind('<B1-Motion>')
	self.oImaging.oAppImaging.CanvasScan.unbind('<ButtonRelease-1>')
	self.oImaging.oAppImaging.CanvasRetrace.unbind('<ButtonRelease-1>')
	return

    def bCheckHorzRange(self, event):
	if event.x < 0 or event.x > self.nImageSize[0]:
	    return False
	if event.y < 0 or event.y >  self.nImageSize[1]-1:
	    return False
	return True
 
    def bCheckVertRange(self, event):
	if event.x < 0 or event.x > self.nImageSize[0]-1:
	    return False
	if event.y < 0 or event.y >  self.nImageSize[1]:
	    return False
	return True
 
    def vShowLineCB(self, event):
	"""
	Displays and Renews line on the image with mouse movements
	"""
	if self.cScanOrientation == HORIZONTAL:
	    if not self.bCheckHorzRange(event):
		return
	    self.y = event.y
	    self.vClearCanvas()
	    self.vShowHorzLine()
	if self.cScanOrientation == VERTICAL:
	    if not self.bCheckVertRange(event):
		return
	    self.x = event.x
	    self.vClearCanvas()
	    self.vShowVertLine()
	return

    def vShowHorzLine(self):
	try:
	    self.oImaging.ScanCanLine = self.oImaging.oAppImaging.CanvasScan.create_line(0, self.y,\
							self.nImageSize[0]-1, self.y, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
	except:
	    pass
	try:
	    self.oImaging.RetCanLine = self.oImaging.oAppImaging.CanvasRetrace.create_line(0, self.y,\
							self.nImageSize[0]-1, self.y, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
	except:
	    pass
	self.nLineSelected = self.y
	self.showLineNo(self.nLineSelected)
	return

    def vShowVertLine(self):
	try:
	    self.oImaging.ScanCanLine = self.oImaging.oAppImaging.CanvasScan.create_line(self.x, 0,\
							self.x, self.nImageSize[0]-1, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
	except:
	    pass
	try:
	    self.oImaging.RetCanLine = self.oImaging.oAppImaging.CanvasRetrace.create_line(self.x, 0,\
							self.x, self.nImageSize[0]-1, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
	except:
	    pass
	self.nLineSelected = self.x
	self.showLineNo(self.nLineSelected)
	return


    def showLineNo(self, lineNo):
	try:
	    self.textLineNoScan = self.oImaging.oAppImaging.CanvasScan.create_text(3, 3,\
							anchor = NW, \
							text = str(lineNo + 1), \
							fill = self.strLineColor, \
							font = canvas_font, \
							)
	except:
	    pass
	try:
	    self.textLineNoRet = self.oImaging.oAppImaging.CanvasRetrace.create_text(3, 3,\
							anchor = NW, \
							text = str(lineNo + 1), \
							fill = self.strLineColor, \
							font = canvas_font, \
							)
	except:
	    pass

	return

    def vClearCanvas(self):
	try :
	    self.oImaging.oAppImaging.CanvasScan.delete(self.oImaging.ScanCanLine)
	except:
	    pass
	try:
	    self.oImaging.oAppImaging.CanvasRetrace.delete(self.oImaging.RetCanLine)
	except:
	    pass
	self.clearLineNo()
	return

    def clearLineNo(self):
	try :
	    self.oImaging.oAppImaging.CanvasScan.delete(self.textLineNoScan)
	except:
	    pass
	try:
	    self.oImaging.oAppImaging.CanvasRetrace.delete(self.textLineNoRet)
	except:
	    pass
	return

    def vCalculateZoomFactor(self):
	"""
	Calculates Zoom Factor 
	"""
	try:
	    self.nZoomFactor=(self.oImaging.oQlaunch.oCZoom.nInfoImageSize/self.afScanImageData.shape[0])
	except:
	    self.nZoomFactor=1
	return

    def vDisplayLinePlotCB(self, event):
	"""
	"""
	if len(self.afScanImageData.shape) == 2:
		self.displayLinePlotSingleChannel()
	else:
		self.displayLinePlotMultiChannel()
	self.clearLineNo()
	return

    def displayLinePlotSingleChannel(self):
	self.vDeactivateImageCanvas()
	#self.vClearCanvas()
	PIEZO_XY = scanner.fGetPiezoXCalibration()	#nm/V
	PIEZO_Z = scanner.fGetPiezoZCalibration()
	HVA_GAIN = scanner.fGetHVAGain()

    	self.vCalculateZoomFactor()
	if self.cScanOrientation == HORIZONTAL:
	    	arPlotYDataScan = self.afScanImageData[self.nLineSelected]
		arPlotYDataRet = self.afRetImageData[self.nLineSelected]
		arPlotXData = self.nStepSize * \
					self.nZoomFactor * \
					numpy.asarray(range(self.nImageSize[0])) * \
					PIEZO_XY/1000.0	
	else:
		arPlotYDataScan = self.afScanImageData[:, self.nLineSelected]
		arPlotYDataRet = self.afRetImageData[:, self.nLineSelected]
		arPlotXData = self.nStepSize * \
					self.nZoomFactor * \
					numpy.asarray(range(self.nImageSize[1])) * \
					PIEZO_XY/1000.0

	# ADC Gain Normalization
	adc_gain = self.oImaging.dicScanParam['Gain']
	arPlotYDataScan /= adc_gain
	arPlotYDataRet /= adc_gain

	print 'Profile Line No: ', self.nLineSelected + 1  
	print 'Line Raw Data in mV (Min, Max): ', arPlotYDataScan.min() , arPlotYDataScan.max() 
	if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
	    arPlotYDataScan *= (HVA_GAIN * PIEZO_Z / 1000.0)
	    arPlotYDataRet *= (HVA_GAIN * PIEZO_Z / 1000.0)

	# Calculating Slopes
	m1, c_ = self.calculateSlope(arPlotXData, arPlotYDataScan)
	[slopeScan, interceptScan] = numpy.polyfit(arPlotXData, arPlotYDataScan, 1)
	arPlotYFitDataScan = slopeScan * arPlotXData + interceptScan
	m2, c_ = self.calculateSlope(arPlotXData, arPlotYDataRet)
	print '!!! Slope in Scan and Retrace are: ', m1, m2
	[slopeRet, interceptRet] = numpy.polyfit(arPlotXData, arPlotYDataRet, 1)
	arPlotYFitDataRet = slopeRet * arPlotXData + interceptRet
	#print '@@@ Slope in Scan and Retrace are: ', slopeScan, slopeRet

	print 'Profile Line No: ', self.nLineSelected + 1  
        pylab.ion()
	pylab.figure()
	pylab.subplot(211)
	pylab.plot(arPlotXData, arPlotYDataScan) #, '-', arPlotXData, arPlotYFitDataScan)
	pylab.xlabel('Distance (nm)')
	if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
	    pylab.ylabel('Z (nm)')
	if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.TCMODE:
	    pylab.ylabel('Tunnel Current (pA)')
	pylab.title('Scan Window', horizontalalignment='right', \
		position=(0.95,0.9), color='red')
	pylab.grid(True)
	pylab.subplot(212)
	pylab.plot(arPlotXData, arPlotYDataRet) #, '-', arPlotXData, arPlotYFitDataRet)
	pylab.xlabel('Distance (nm)')
	if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
	    pylab.ylabel('Z (nm)')
	if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.TCMODE:
	    pylab.ylabel('Tunnel Current (pA)')
	pylab.title('Retrace Window', horizontalalignment='right', \
		position=(0.95,0.9), color='red')
	pylab.grid(True)
	pylab.show()
	return


    def calculateSlope(self, x, y):
	np = x.shape[0]
	# http://mathworld.wolfram.com/LeastSquaresFitting.html
	slope = ((x * y).sum() - np * x.mean() * y.mean()) / ((x * x).sum() - np * x.mean() ** 2)
	intercept = (y.mean() * (x * x).sum() - x.mean() * (x * y).sum()) / ((x * x).sum() - np * x.mean() ** 2)
	return slope, intercept



    def displayLinePlotMultiChannel(self):
	self.vDeactivateImageCanvas()
	PIEZO_XY = scanner.fGetPiezoXCalibration()	#nm/V
	PIEZO_Z = scanner.fGetPiezoZCalibration()
	HVA_GAIN = scanner.fGetHVAGain()
    	self.vCalculateZoomFactor()
	if self.cScanOrientation == HORIZONTAL:
	    	arPlotYDataScan = self.afScanImageData[:, self.nLineSelected]
		arPlotYDataRet = self.afRetImageData[:, self.nLineSelected]
		arPlotXData = self.nStepSize * \
				self.nZoomFactor * \
				numpy.asarray(range(self.nImageSize[0])) * \
				PIEZO_XY/1000.0	
	else:
		arPlotYDataScan = self.afScanImageData[:, :, self.nLineSelected]
		arPlotYDataRet = self.afRetImageData[:, :, self.nLineSelected]
		arPlotXData = self.nStepSize * \
				self.nZoomFactor * \
				numpy.asarray(range(self.nImageSize[1])) * \
				PIEZO_XY/1000.0
	print 'Profile Line No: ', self.nLineSelected + 1 
	# Fixing Topography Scale
	arPlotYDataScan[0] *= (HVA_GAIN * (PIEZO_Z / 1000.0) / self.nADCGain)
	arPlotYDataRet[0] *= (HVA_GAIN * (PIEZO_Z / 1000.0) / self.nADCGain)
        pylab.ion()
	yScale = ['nm', 'arb. units', 'arb. units']
	for count in range(self.afScanImageData.shape[0]):
		self.plotData(arPlotXData, arPlotYDataScan[count], arPlotYDataRet[count], \
				title = self.oImaging.dicScanParam['ChannelNames'][count], 
				yScale = yScale[count])
	pylab.show()
	
	return

    def plotData(self, xdata, scanLineData, retraceLineData, **kwargs):
	pylab.figure()
	pylab.subplot(211)
	pylab.plot(xdata, scanLineData)
	title = kwargs['title']
	yScale = kwargs['yScale']
	pylab.xlabel('Distance (nm)')
	pylab.ylabel(title + ' ('+ yScale + ')')
	pylab.title('Scan Window - ' + title, horizontalalignment='right', \
		position=(0.95,0.9), color='red')
	pylab.grid(True)
	pylab.subplot(212)
	pylab.plot(xdata, retraceLineData)
	pylab.xlabel('Distance (nm)')
	pylab.ylabel(title + ' ('+ yScale + ')')
	pylab.title('Retrace Window - ' + title, horizontalalignment='right', \
		position=(0.95,0.9), color='red')
	pylab.grid(True)
	
	return

