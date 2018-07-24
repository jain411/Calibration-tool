##################
#   LExt Class   #
##################
from Tkinter import *
import numpy
import tkMessageBox
import pylab
import scanner
import math
import dialogs

def lext(oImaging=None):
	"""
	Returns LExt object
	"""
	oLExt=LExt(oImaging)
	return oLExt
	
class LExt:
	
	def __init__(self, oImaging):
		"""
		Class Contructor : LExt
		"""
		self.oImaging = oImaging
		try:
			self.vDeleteline()
		except:
			pass
		self.vInitializeLExt()
		if not self.oImaging.bImagePresentVar.get():
			tkMessageBox.showwarning('Blank','No Images on Display')
			return
		if self.oImaging.bDumpVar.get():
			tkMessageBox.showwarning('Dump','Dumped Image on Display, Line Extraction not supported here.')
			return
		self.vLExt()
		return

	def vLExt(self):
		"""
		Gets Image Data and binds mouse with th image canvas
		"""
		self.afScanImageData = self.oImaging.afScanImageData.copy()
		self.afRetImageData = self.oImaging.afRetImageData.copy()
		if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
	    	    self.afScanImageData *= -1.0
	 	    self.afRetImageData *= -1.0
		    print 'CC Mode Image'
		    fHVAGain = scanner.fGetHVAGain()
		    self.afScanImageData *= fHVAGain 
		    self.afRetImageData *= fHVAGain 
		self.nStepSize = self.oImaging.dicScanParam['StepSize'][0]
		if self.oImaging.dicScanParam.has_key('XLArea'):
	    	    if self.oImaging.dicScanParam['XLArea']:
			self.nStepSize *= scanner.XL_GAIN
		self.nImageSize = self.oImaging.dicScanParam['ImageSize'][0]
		try:
		    self.nADCGain = self.oImaging.dicScanParam['Gain']
		except:
		    self.nADCGain = 1
		self.vActivateImageCanvas()
		dicGUISettings = dialogs.dicReadGUISettings()
		self.strLineColor = dicGUISettings['LEC']	# Line Extraction Color
		return

	def vActivateImageCanvas(self):
		"""
		Selects the scan image portion by dragging mouse with left click button pressed over the desired area
		"""
		self.oImaging.oAppImaging.CanvasScan.bind('<Button-1>', self.vBeginLineCB)
		self.oImaging.oAppImaging.CanvasRetrace.bind('<Button-1>', self.vBeginLineCB)
		self.oImaging.oAppImaging.CanvasScan.bind('<B1-Motion>', self.vShowLineCB)
		self.oImaging.oAppImaging.CanvasRetrace.bind('<B1-Motion>', self.vShowLineCB)
		self.oImaging.oAppImaging.CanvasScan.bind('<ButtonRelease-1>', self.vEndLineCB)
		self.oImaging.oAppImaging.CanvasRetrace.bind('<ButtonRelease-1>', self.vEndLineCB)
		return

	def vUnbindImageCanvas(self):
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

	def vInitializeLExt(self):
		"""
		Initalizes Line Extraction
		"""
		self.bDirection=BooleanVar()
		self.bDirection.set(False)
		return

	def vBeginLineCB(self, event):
		"""
		Gets Initial endpoint of the calibration line
		"""
		#self.vActivateImageCanvas()
		try :
			self.oImaging.oAppImaging.CanvasScan.delete(self.oImaging.ScanCanLine)
		except:
			pass
		try:
			self.oImaging.oAppImaging.CanvasRetrace.delete(self.oImaging.RetCanLine)
		except:
			pass
		self.x0 = event.x
		self.y0 = event.y
		self.initialpoint=[event.x, event.y]
		print 'starting point :', self.initialpoint
		return

	def vShowLineCB(self, event):
		"""
		Displays and Renews Calibration line with mouse movements
		"""
		if not self.bCheckRange(event):
			return
		self.x1 = event.x
		self.y1 = event.y
		try :
			self.oImaging.oAppImaging.CanvasScan.delete(self.oImaging.ScanCanLine)
		except:
			pass
		try:
			self.oImaging.oAppImaging.CanvasRetrace.delete(self.oImaging.RetCanLine)
		except:
			pass
		try:
			self.oImaging.ScanCanLine = self.oImaging.oAppImaging.CanvasScan.create_line(self.x0, self.y0,\
							 self.x1, self.y1, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
		except:
			pass
		try:
			self.oImaging.RetCanLine = self.oImaging.oAppImaging.CanvasRetrace.create_line(self.x0, self.y0,\
							 self.x1, self.y1, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
		except:
			pass
		return

	def bCheckRange(self, event):
		"""
		Checks whether the selected area is greater than the image size
		"""
		if event.x <= 0 or event.x >= self.nImageSize:
			return False
		if event.y <= 0 or event.y >= self.nImageSize:
			return False
		return True

	def vEndLineCB(self, event):
		"""
		Fetches location of final endpoint
		"""
		self.x1=event.x
		self.y1=event.y
		self.finalpoint=[event.x, event.y]
		print 'Final Point',self.finalpoint
		self.vShowLineCB(event)
		self.vCalculateZoomFactor()
		self.vLaunchBresanham()
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

	def vDeleteline(self):
		"""
		Removes Extraction line from the Imaging Canvas
		"""
		try :
			self.oImaging.oAppImaging.CanvasScan.delete(self.oImaging.ScanCanLine)
		except:
			pass
		try:
			self.oImaging.oAppImaging.CanvasRetrace.delete(self.oImaging.RetCanLine)
		except:
			pass
		return

	def vLaunchBresanham(self):
		"""
		Calulates locations of pixels lying under extraction line
		"""
		self.vInitializeBresanham()
		if self.dx==0 and self.dy>0:
			self.xmatrix.append(self.x0)
			self.ymatrix.append(self.y0)
			self.vCalculatePixelsSLine(self.x0,self.y0,self.x1,self.y1)
		if self.dx==0 and self.dy<0:
			self.xmatrix.append(self.x1)
			self.ymatrix.append(self.y1)
			self.vCalculatePixelsSLine(self.x1,self.y1,self.x0,self.y0)
		if self.dy==0 and self.dx>0:
			self.xmatrix.append(self.y0)
			self.ymatrix.append(self.x0)
			self.vCalculatePixelsSLine(self.y0,self.x0,self.y1,self.x1)
			tmp=self.xmatrix
			self.xmatrix=self.ymatrix
			self.ymatrix=tmp
		if self.dy==0 and self.dx<0:
			self.xmatrix.append(self.y1)
			self.ymatrix.append(self.x1)
			self.vCalculatePixelsSLine(self.y1,self.x1,self.y0,self.x0)
			tmp=self.xmatrix
			self.xmatrix=self.ymatrix
			self.ymatrix=tmp

		if self.dx>0 and self.dy>0 and abs(self.dx)>abs(self.dy):
			self.xmatrix.append(self.x0)
			self.ymatrix.append(self.y0)
			self.vCalculatePixelsI(self.x0,self.y0,self.dx,self.dy)
		if self.dx>0 and self.dy>0 and abs(self.dx)<abs(self.dy):
			self.xmatrix.append(self.y0)
			self.ymatrix.append(self.x0)
			self.vCalculatePixelsI(self.y0,self.x0,self.dy,self.dx)
			tmp=self.xmatrix
			self.xmatrix=self.ymatrix
			self.ymatrix=tmp
		if self.dx<0 and self.dy<0 and abs(self.dx)>abs(self.dy):
			self.vCalculatePixelsI(self.x1,self.y1,abs(self.dx),abs(self.dy))
		if self.dx<0 and self.dy<0 and abs(self.dx)<abs(self.dy):
			self.vCalculatePixelsI(self.y1,self.x1,abs(self.dy),abs(self.dx))
			tmp=self.xmatrix
			self.xmatrix=self.ymatrix
			self.ymatrix=tmp
		if self.dx>0 and self.dy<0 and abs(self.dx)>abs(self.dy):
			self.xmatrix.append(self.x0)
			self.ymatrix.append(self.y0)
			self.vCalculatePixelsIIa(self.x0,self.y0,self.dx,self.dy)
		if self.dx>0 and self.dy<0 and abs(self.dx)<abs(self.dy):
			self.xmatrix.append(self.x0)
			self.ymatrix.append(self.y0)
			self.vCalculatePixelsIIb(self.x0,self.y0,self.dx,self.dy)
		if self.dx<0 and self.dy>0 and abs(self.dx)>abs(self.dy):
			self.xmatrix.append(self.x0)
			self.ymatrix.append(self.y0)
			self.vCalculatePixelsIVa(self.x0,self.y0,self.dx,self.dy)
		if self.dx<0 and self.dy>0 and abs(self.dx)<abs(self.dy):
			self.xmatrix.append(self.x0)
			self.ymatrix.append(self.y0)
			self.vCalculatePixelsIVb(self.x0,self.y0,self.dx,self.dy)
		self.vDisplayResult()
		return

	def vInitializeBresanham(self):
		"""
		Method : vInitializeBresanham
		"""
		self.xmatrix=[]
		self.ymatrix=[]
		self.dx=float(self.x1-self.x0)
		self.dy=float(self.y1-self.y0)
		return

	def vCalculatePixelsSLine(self,x=0,y=0,x1=0,y1=0):
		"""
		Calculates pixels when dx/dy=0
		"""
		for i in range(y1-y):
			self.xmatrix.append(x)
			self.ymatrix.append(y+1+i)
		return

	def vCalculatePixelsI(self,x=0,y=0,dx=0,dy=0):
		"""
		I quardent |m|<1
		"""
		i=0
		d2y=2*dy
		d2ymd2x=d2y-(2*dx)
		p=[]
		p.append(float(d2y-dx))
		for z in range(int(dx)):
			if p[i]<0:
				p.append(p[i]+d2y)
				x=x+1
				y=y
			else:
				p.append(p[i]+d2ymd2x)
				x=x+1
				y=y+1	
			self.xmatrix.append(round(x))
			self.ymatrix.append(round(y))
			i=i+1
		return
 
	def vCalculatePixelsIIa(self,x=0,y=0,dx=0,dy=0):
		"""
		II quardent |m|<1
		"""
		i=0
		d2y=2*dy
		d2x=2*dx
		d2ymd2x=d2y-(2*dx)
		p=[]
		p.append(float(d2y-dx))
		for z in range(int(dx)):
			if p[i]<0:
				p.append(p[i]+d2y+d2x)
				x=x+1
				y=y-1
			else:
				p.append(p[i]+d2y)
				x=x+1
				y=y	
			self.xmatrix.append(round(x))
			self.ymatrix.append(round(y))
			i=i+1
		return
 
	def vCalculatePixelsIIb(self,x=0,y=0,dx=0,dy=0):
		"""
		II quardent |m|>1
		"""
		i=0
		d2y=2*dy
		d2x=2*dx
		d2ymd2x=d2y-(2*dx)
		p=[]
		p.append(float(d2x-dy))
		for z in range(abs(int(dy))):
			if p[i]<0:
				p.append(p[i]-d2y-d2x)
				x=x+1
				y=y-1
			else:
				p.append(p[i]-d2x)
				x=x
				y=y-1	
			self.xmatrix.append(round(x))
			self.ymatrix.append(round(y))
			i+=1
		return

	def vCalculatePixelsIVa(self,x=0,y=0,dx=0,dy=0):
		"""
		IV quardent |m|<1
		"""
		i=0
		d2y=2*dy
		d2x=2*dx
		d2ymd2x=d2y-(2*dx)
		p=[]
		p.append(float(d2y-dx))
		for z in range(abs(int(dx))):
			if p[i]<0:
				p.append(p[i]-d2y-d2x)
				x=x-1
				y=y+1
			else:
				p.append(p[i]-d2y)
				x=x-1
				y=y	
			self.xmatrix.append(round(x))
			self.ymatrix.append(round(y))
			i=i+1
		return

	def vCalculatePixelsIVb(self,x=0,y=0,dx=0,dy=0):
		"""
		IV quardent |m|>1
		"""
		i=0
		d2y=2*dy
		d2x=2*dx
		d2ymd2x=d2y-(2*dx)
		p=[]
		p.append(float(d2y-dx))
		for z in range(int(dy)):
			if p[i]<0:
				p.append(p[i]+d2y+d2x)
				x=x-1
				y=y+1
			else:
				p.append(p[i]+d2x)
				x=x
				y=y+1	
			self.xmatrix.append(round(x))
			self.ymatrix.append(round(y))
			i=i+1
		return


	def vDisplayResult(self):
		"""
		Pops out line Exraction result curve
		"""
		pylab.ion()
		if abs(self.dx) >= abs(self.dy):
			self.bDirection.set(False)
		else:
			self.bDirection.set(True)
		pylab.figure()
		self.vDisplayScanImageCurve()
		self.vDisplayRetImageCurve()
		pylab.show()
		return	
			
	def vDisplayScanImageCurve(self):
		"""
		Pops out Scan line Exraction result curve
		"""
		self.vUnbindImageCanvas()
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		PIEZO_Z = scanner.fGetPiezoZCalibration()
		fTheta = self.fCalculateTheta()
		self.flinexy=[]
		i=0
		j=0
		if self.bDirection.get()==False:
			for x in range(len(self.xmatrix)):
				self.flinexy.append(self.afScanImageData[int(self.xmatrix[i])][int(self.ymatrix[j])])
				i+=1
				j+=1
			tmatrix = []
			for m in range(len(self.xmatrix)):
				tmatrix.append(m) 
			lxpixel=map(lambda x:x/math.cos(fTheta),tmatrix)
			arrXpixel=numpy.asarray(lxpixel)
			self.xmatrix1=(arrXpixel*PIEZO_XY*self.nStepSize*self.nZoomFactor)/100
			pylab.subplot(211)
			fNumLineXY=numpy.asarray(self.flinexy)
			fNumLineXY /= self.nADCGain
			# Show Y-Axis is in Angstroms, Z Calibration is in nm/V
			if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
			    fNumLineXY = (fNumLineXY/1000.0)* PIEZO_Z * 10
			pylab.plot(self.xmatrix1,fNumLineXY)
		if self.bDirection.get()==True:
			for x in range(len(self.ymatrix)):
				self.flinexy.append(self.afScanImageData[int(self.xmatrix[i])][int(self.ymatrix[j])])
				i+=1
				j+=1
			tmatrix = []
			for m in range(len(self.ymatrix)):
				tmatrix.append(m) 
			lxpixel=map(lambda x:x/math.cos((math.pi/2)-fTheta),tmatrix)
			arrXpixel=numpy.asarray(lxpixel)
			self.xmatrix1=(arrXpixel*PIEZO_XY*self.nStepSize*self.nZoomFactor)/100
			pylab.subplot(211)
			fNumLineXY=numpy.asarray(self.flinexy)
			fNumLineXY /= self.nADCGain
			# Show Y-Axis is in Angstroms, Z Calibration is in nm/V
			if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
			    fNumLineXY = (fNumLineXY/1000.0)* PIEZO_Z * 10
			pylab.plot(self.xmatrix1,fNumLineXY)
		pylab.xlabel('Segment length (angs)')
		#pylab.ylabel('Vtc (mV)')
		if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
		    pylab.ylabel('Z-Motion (angs)')
		if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.TCMODE:
		    pylab.ylabel('Tunnel Current (pA)')
		pylab.title('Scan Window', horizontalalignment='right', \
				position=(0.95,0.9), color='red')
		pylab.grid(True)
		return
	
	def vDisplayRetImageCurve(self):
		"""
		Pops out Retrace line Exraction result curve
		"""
		PIEZO_XY = scanner.fGetPiezoXCalibration()
		PIEZO_Z = scanner.fGetPiezoZCalibration()
		fTheta = self.fCalculateTheta()
		self.flinexy=[]
		i=0
		j=0
		if self.bDirection.get()==False:
			for x in range(len(self.xmatrix)):
				self.flinexy.append(self.afRetImageData[int(self.xmatrix[i])][int(self.ymatrix[j])])
				i+=1
				j+=1
			tmatrix = []
			for m in range(len(self.xmatrix)):
				tmatrix.append(m) 
			lxpixel=map(lambda x:x/math.cos(fTheta),tmatrix)
			arrXpixel=numpy.asarray(lxpixel)
			self.xmatrix1=(arrXpixel*PIEZO_XY*self.nStepSize*self.nZoomFactor)/100
			pylab.subplot(212)
			fNumLineXY=numpy.asarray(self.flinexy)
			fNumLineXY /= self.nADCGain
			# Show Y-Axis is in Angstroms, Z Calibration is in nm/V
			if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
			    fNumLineXY = (fNumLineXY/1000.0)* PIEZO_Z * 10
			pylab.plot(self.xmatrix1,fNumLineXY)
		if self.bDirection.get()==True:
			for x in range(len(self.ymatrix)):
				self.flinexy.append(self.afRetImageData[int(self.xmatrix[i])][int(self.ymatrix[j])])
				i+=1
				j+=1
			tmatrix = []
			for m in range(len(self.ymatrix)):
				tmatrix.append(m) 
			lxpixel=map(lambda x:x/math.cos((math.pi/2)-fTheta),tmatrix)
			arrXpixel=numpy.asarray(lxpixel)
			self.xmatrix1=(arrXpixel*PIEZO_XY*self.nStepSize*self.nZoomFactor)/100
			pylab.subplot(212)
			fNumLineXY=numpy.asarray(self.flinexy)
			fNumLineXY /= self.nADCGain
			# Show Y-Axis is in Angstroms, Z Calibration is in nm/V
			if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
			    fNumLineXY = (fNumLineXY/1000.0)* PIEZO_Z * 10
			pylab.plot(self.xmatrix1,fNumLineXY)
		pylab.xlabel('Segment length (angs)')
		#pylab.ylabel('Vtc (mV)')
		if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.ZMODE:
		    pylab.ylabel('Z-Motion (angs)')
		if self.oImaging.dicScanParam['DigitizationMode'] == self.oImaging.oScanner.TCMODE:
		    pylab.ylabel('Tunnel Current (pA)')
		pylab.title('Retrace Window', horizontalalignment='right', 
				position=(0.95,0.9), color='red')
		pylab.grid(True)
		return
	
	def fCalculateTheta(self):
		"""
		Calculates angle between line segment & and the axis
		"""
		dx=float(self.finalpoint[0]-self.initialpoint[0])
		dy=float(self.finalpoint[1]-self.initialpoint[1])
		if dx==0:
			return 90
		if dy==0:
			return 0
		theta = abs(math.atan(dy/dx))
		print 'Theta',theta,180*theta/math.pi
		return theta
