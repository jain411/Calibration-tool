############################
#   Horz. Line Ext Class   #
############################
from Tkinter import *
import numpy
import tkMessageBox
import pylab

import qvquicklaunch
import qv

HORIZONTAL	= 'H'
VERTICAL	= 'V'

def hvlext(oQv=None, mode='H'):
    """
    Function : hvlext
	Returns HVLExt object
    Arguments :
	oQv : object of class Qv
    Returns :
	oHVLExt : object of class LExt
    """
    oHVLExt=HVLExt(oQv, mode)
    return oHVLExt
	
class HVLExt:
	
    def __init__(self, oQv, mode):
	"""
	Class Contructor : HVLExt
	"""
	self.oQv = oQv
	self.oQL = self.oQv.oQLaunch
	self.cScanOrientation = mode	# 'H' or 'V'
	try:
	    self.vDeleteline()
	except:
	    pass
	if not self.oQv.bImagePresentVar.get():
	    tkMessageBox.showwarning('Blank','No Images on Display')
	    return
	if self.oQv.bDumpVar.get():
	    tkMessageBox.showwarning('Dump','Dumped Image on Display, Line Extraction not supported here.')
	    return
	self.vHVLExt()
	return

    def vHVLExt(self):
	"""
	Gets Image Data and binds mouse with the image canvas
        """
	self.afScanImageData = self.oQL.afScanImage.copy() * -1.0
	self.afRetImageData = self.oQL.afRetImage.copy() * -1.0
	if self.oQL.dicScanParam['DigitizationMode'] == qvquicklaunch.ZMODE:
	    fHVAGain = qvquicklaunch.XL_GAIN
	    self.afScanImageData *= fHVAGain 
	    self.afRetImageData *= fHVAGain
	self.nStepSize = self.oQL.dicScanParam['StepSize'][0]
	if self.oQL.dicScanParam.has_key('XLArea'):
	    if self.oQL.dicScanParam['XLArea']:
		self.nStepSize *= qvquicklaunch.XL_GAIN
	self.nImageSize = self.oQL.dicScanParam['ImageSize']
	try:
	    self.nADCGain = self.oQL.dicScanParam['Gain']
	except:
	    self.nADCGain = 1
	self.vActivateImageCanvas()
	self.strLineColor = 'blue'
	return

    def vActivateImageCanvas(self):
	"""
	Make the Canvas ready to show the horz. line below the mouse pointer, and display result on left click.
	"""
	self.oQv.oAppQv.CanvasScan.bind('<Button-1>', self.vShowLineCB)
	self.oQv.oAppQv.CanvasRetrace.bind('<Button-1>', self.vShowLineCB)
	self.oQv.oAppQv.CanvasScan.bind('<B1-Motion>', self.vShowLineCB)
	self.oQv.oAppQv.CanvasRetrace.bind('<B1-Motion>', self.vShowLineCB)
	self.oQv.oAppQv.CanvasScan.bind('<ButtonRelease-1>', self.vDisplayLinePlotCB)
	self.oQv.oAppQv.CanvasRetrace.bind('<ButtonRelease-1>', self.vDisplayLinePlotCB)
	return

    def vDeactivateImageCanvas(self):
	"""
	Removes mouse bindings with the Qv Canvas
	"""
	self.oQv.oAppQv.CanvasScan.unbind('<Button-1>')
	self.oQv.oAppQv.CanvasRetrace.unbind('<Button-1>')
	self.oQv.oAppQv.CanvasScan.unbind('<B1-Motion>')
	self.oQv.oAppQv.CanvasRetrace.unbind('<B1-Motion>')
	self.oQv.oAppQv.CanvasScan.unbind('<ButtonRelease-1>')
	self.oQv.oAppQv.CanvasRetrace.unbind('<ButtonRelease-1>')
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
	Displays and Renews Calibration line with mouse movements
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
	    self.ciScanCanLine = self.oQv.oAppQv.CanvasScan.create_line(0, self.y,\
                                            self.nImageSize[0]-1, self.y, \
                                            fill=self.strLineColor, \
                                            arrow=BOTH, \
                                            width=2)
	except:
	    pass
	try:
	    self.ciRetCanLine = self.oQv.oAppQv.CanvasRetrace.create_line(0, self.y,\
                                            self.nImageSize[0]-1, self.y, \
                                            fill=self.strLineColor, \
                                            arrow=BOTH, \
                                            width=2)
	except:
	    pass
	self.nLineSelected = self.y
	return

    def vShowVertLine(self):
	try:
	    self.ciScanCanLine = self.oQv.oAppQv.CanvasScan.create_line(self.x, 0,\
                                            self.x, self.nImageSize[0]-1, \
                                            fill=self.strLineColor, \
                                            arrow=BOTH, \
                                            width=2)
	except:
	    pass
	try:
	    self.ciRetCanLine = self.oQv.oAppQv.CanvasRetrace.create_line(self.x, 0,\
                                            self.x, self.nImageSize[0]-1, \
                                            fill=self.strLineColor, \
                                            arrow=BOTH, \
                                            width=2)
	except:
	    pass
	self.nLineSelected = self.x
	return


    def vClearCanvas(self):
	try :
	    self.oQv.oAppQv.CanvasScan.delete(self.ciScanCanLine)
	except:
	    pass
	try:
	    self.oQv.oAppQv.CanvasRetrace.delete(self.ciRetCanLine)
	except:
	    pass
	return

    def vCalculateZoomFactor(self):
	"""
	Method : vCalculateZoomFactor
		Calculates Zoom Factor 
				
	Arguments :
		None
	
	Returns :
		None
	"""
	try:
	    self.nZoomFactor=(self.oQL.oCZoom.nInfoImageSize/self.afScanImageData.shape[0])
	except:
	    self.nZoomFactor=1
	return


    def vDisplayLinePlotCB(self, event):
	"""
	"""
	self.vDeactivateImageCanvas()
	self.vClearCanvas()
	PIEZO_XY = qv.fGetPiezoXCalibration()	#nm/V
	PIEZO_Z = qv.fGetPiezoZCalibration()
    	self.vCalculateZoomFactor()
	if self.cScanOrientation == HORIZONTAL:
	    arPlotYDataScan = self.afScanImageData[self.nLineSelected]
	    arPlotYDataRet = self.afRetImageData[self.nLineSelected]
	    arPlotXData = self.nStepSize * self.nZoomFactor * numpy.asarray(range(self.nImageSize[0])) * PIEZO_XY/100.0	# /100.0 because PIEZO_XY is nm/V and StepSize is in mV
	    #arPlotXData = self.nStepSize * self.nZoomFactor * numpy.asarray(range(self.nImageSize[0]))
	else:
	    arPlotYDataScan = self.afScanImageData[:, self.nLineSelected]
	    arPlotYDataRet = self.afRetImageData[:, self.nLineSelected]
	    
	    arPlotXData = self.nStepSize * self.nZoomFactor * numpy.asarray(range(self.nImageSize[1])) * PIEZO_XY/100.0	# /100.0 because PIEZO_Z is nm/V and YData is in mV
	    #arPlotXData = self.nStepSize * self.nZoomFactor * numpy.asarray(range(self.nImageSize[1]))
	#print 'Line No: ', self.nLineSelected 
	#print 'Line Raw Data in mV (Min, Max): ', arPlotYDataScan.min() , arPlotYDataScan.max() 
	arPlotYDataScan *= PIEZO_Z/100.0	# /100.0 because PIEZO_XY is nm/V and StepSize is in mV
	arPlotYDataRet *= PIEZO_Z/100.0		# /100.0 because PIEZO_XY is nm/V and StepSize is in mV
        pylab.ion()     # interactive mode on
	pylab.figure()
	pylab.subplot(211)
	pylab.plot(arPlotXData, arPlotYDataScan)
	pylab.xlabel('Segment length (angs)')
	pylab.ylabel('Z-Motion (angs)')
	pylab.title('Scan Window', horizontalalignment='right', \
		position=(0.95,0.9), color='red')
	pylab.grid(True)
	pylab.subplot(212)
	pylab.plot(arPlotXData, arPlotYDataRet)
	pylab.xlabel('Segment length (angs)')
	pylab.ylabel('Z-Motion (angs)')
	pylab.title('Retrace Window', horizontalalignment='right', \
		position=(0.95,0.9), color='red')
	pylab.grid(True)
	pylab.show()
	return

