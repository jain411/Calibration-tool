##################
#   LExt Class   #
##################
from Tkinter import *
import numpy
import tkMessageBox
import pylab
import math

import qvquicklaunch
import qv


def lext(oQv=None):
	"""
	Function : lext
		Returns LExt object
	Arguments :
		oQv : object of class Qv
	Returns :
		oLExt : object of class LExt
	"""
	oLExt=LExt(oQv)
	return oLExt
	
class LExt:
	def __init__(self, oQv):
            """
            Class Contructor : LExt
            """
            self.oQv = oQv
            self.oQL = self.oQv.oQLaunch
            try:
                    self.vDeleteline()
            except:
                    pass
            self.vInitializeLExt()
            if not self.oQv.bImagePresentVar.get():
                    tkMessageBox.showwarning('Blank','No Images on Display')
                    return
            if self.oQv.bDumpVar.get():
                    tkMessageBox.showwarning('Dump','Dumped Image on Display, Line Extraction not supported here.')
                    return
            self.vLExt()
            return

	def vLExt(self):
		"""
                Gets Image Data and binds mouse with th image canvas
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
		self.nImageSize = self.oQL.dicScanParam['ImageSize'][0]
		try:
		    self.nADCGain = self.oQL.dicScanParam['Gain']
		except:
		    self.nADCGain = 1
		self.strLineColor = 'blue'	# Line Extraction Color
		self.vActivateImageCanvas()
		return

	def vActivateImageCanvas(self):
		"""
                Selects the scan image portion by dragging mouse with left click button pressed over the desired area
		"""
		self.oQv.oAppQv.CanvasScan.bind('<Button-1>', self.vBeginLineCB)
		self.oQv.oAppQv.CanvasRetrace.bind('<Button-1>', self.vBeginLineCB)
		self.oQv.oAppQv.CanvasScan.bind('<B1-Motion>', self.vShowLineCB)
		self.oQv.oAppQv.CanvasRetrace.bind('<B1-Motion>', self.vShowLineCB)
		self.oQv.oAppQv.CanvasScan.bind('<ButtonRelease-1>', self.vEndLineCB)
		self.oQv.oAppQv.CanvasRetrace.bind('<ButtonRelease-1>', self.vEndLineCB)
		return

	def vUnbindImageCanvas(self):
		"""
		Method : vUnbindImageCanvas
			Removes mouse bindings with the Qv Canvas
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.oQv.oAppQv.CanvasScan.unbind('<Button-1>')
		self.oQv.oAppQv.CanvasRetrace.unbind('<Button-1>')
		self.oQv.oAppQv.CanvasScan.unbind('<B1-Motion>')
		self.oQv.oAppQv.CanvasRetrace.unbind('<B1-Motion>')
		self.oQv.oAppQv.CanvasScan.unbind('<ButtonRelease-1>')
		self.oQv.oAppQv.CanvasRetrace.unbind('<ButtonRelease-1>')
		return

	def vInitializeLExt(self):
		"""
		Method : vInitializeLExt
			Initalizes Line Extraction
		
		Arguments :
			None
	
		Returns :
			None
		"""
		self.bDirection=BooleanVar()
		self.bDirection.set(False)
		return

	def vBeginLineCB(self, event):
		"""
		Method : vBeginLine
			Gets Initial endpoint of the calibration line

		Arguments :
			event : Tkiner event for mouse binding

		Returns :
			None
		"""
		try :
			self.oQv.oAppQv.CanvasScan.delete(self.oQv.ScanCanLine)
		except:
			pass
		try:
			self.oQv.oAppQv.CanvasRetrace.delete(self.oQv.RetCanLine)
		except:
			pass
		self.x0 = event.x
		self.y0 = event.y
		self.initialpoint=[event.x, event.y]
		#print 'starting point :', self.initialpoint
		return

	def vShowLineCB(self, event):
		"""
		Method : vShowLine
			Displays and Renews Calibration line with mouse movements

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		if not self.bCheckRange(event):
			return
		self.x1 = event.x
		self.y1 = event.y
		try :
			self.oQv.oAppQv.CanvasScan.delete(self.oQv.ScanCanLine)
		except:
			pass
		try:
			self.oQv.oAppQv.CanvasRetrace.delete(self.oQv.RetCanLine)
		except:
			pass
		try:
			self.oQv.ScanCanLine = self.oQv.oAppQv.CanvasScan.create_line(self.x0, self.y0,\
							 self.x1, self.y1, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
		except:
			pass
		try:
			self.oQv.RetCanLine = self.oQv.oAppQv.CanvasRetrace.create_line(self.x0, self.y0,\
							 self.x1, self.y1, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
		except:
			pass
		return

	def bCheckRange(self, event):
		"""
		Method : bCheckRange
			Checks whether the selected area is greater than the image size
			
		Arguments :
			event : Tkinter binding with mouse
				
		Returns :
			None
		"""
		if event.x <= 0 or event.x >= self.nImageSize:
			return False
		if event.y <= 0 or event.y >= self.nImageSize:
			return False
		return True

	def vEndLineCB(self, event):
		"""
		Method : vEndLineCB
			Fetches location of final endpoint

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		self.x1=event.x
		self.y1=event.y
		self.finalpoint=[event.x, event.y]
		#print 'Final Point',self.finalpoint
		self.vShowLineCB(event)
		self.vCalculateZoomFactor()
		self.vLaunchBresanham()
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
			self.nZoomFactor=(self.oQv.oQlaunch.oCZoom.nInfoImageSize/self.afScanImageData.shape[0])
		except:
			self.nZoomFactor=1
		return

	def vDeleteline(self):
		"""
		Method : vDeleteline
			Removes Extraction line from the Qv Canvas
		Arguments :
			None
	
		Returns :
			None
		"""
		try :
			self.oQv.oAppQv.CanvasScan.delete(self.oQv.ScanCanLine)
		except:
			pass
		try:
			self.oQv.oAppQv.CanvasRetrace.delete(self.oQv.RetCanLine)
		except:
			pass
		return

	def vLaunchBresanham(self):
		"""
		Method : vLaunchBresanham
			Calulates locations of pixels lying under extraction line

		Arguments :
			None

		Returns :
			None
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

		Arguments :
			None

		Returns :
			None
		"""
		self.xmatrix=[]
		self.ymatrix=[]
		self.dx=float(self.x1-self.x0)
		self.dy=float(self.y1-self.y0)
		return

	def vCalculatePixelsSLine(self,x=0,y=0,x1=0,y1=0):
		"""
		Method : vCalculatePixelsSLine
			Calculates pixels when dx/dy=0
			
		Arguments :
			x  : int initial x-coordinate
			y  : int initial y-coordinate
			x1 : int final x-coordinate
			y1 : int final y-coordinate

		Returns :
			None
		"""
		for i in range(y1-y):
			self.xmatrix.append(x)
			self.ymatrix.append(y+1+i)
		return

	def vCalculatePixelsI(self,x=0,y=0,dx=0,dy=0):
		"""
		Method : vCalculatePixelsI
			I quardent |m|<1

		Arguments :
			x  : int
			y  : int
			dx : int
			dy : int

		Returns :
			None
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
		Method : vCalulatePixelsIIa
			II quardent |m|<1

		Arguments :
			x  : int
			y  : int
			dx : int
			dy : int

		Returns :
			None
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
		Method : vCalculatePixelsIIb
			II quardent |m|>1

		Arguments :
			x  : int
			y  : int
			dx : int
			dy : int

		Returns :
			None
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
		Method : vCalculatePixelsIVa
			IV quardent |m|<1

		Arguments :
			x  : int
			y  : int
			dx : int
			dy : int

		Returns :
			None
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
		Method : vCalculatePixelsIVb
			IV quardent |m|>1

		Arguments :
			x  : int
			y  : int
			dx : int
			dy : int

		Returns :
			None
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
		Method : vDisplayResult
			Pops out line Exraction result curve

		Arguments :
			None

		Returns :
			None
		"""
		pylab.ion()     # interactive display
		if abs(self.dx) >= abs(self.dy):
			self.bDirection.set(False)
		else:
			self.bDirection.set(True)
                pylab.ion()     # interactive mode on
		pylab.figure()
		self.vDisplayScanImageCurve()
		self.vDisplayRetImageCurve()
		pylab.show()
		return	
			
	def vDisplayScanImageCurve(self):
		"""
		Method : vDisplayScanImageCurve
			Pops out Scan line Exraction result curve

		Arguments :
			None

		Returns :
			None
		"""
		self.vUnbindImageCanvas()
		PIEZO_XY = qv.fGetPiezoXCalibration()
		PIEZO_Z = qv.fGetPiezoZCalibration()
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
			fNumLineXY = (fNumLineXY/1000.0)* PIEZO_Z * 10
			pylab.plot(self.xmatrix1,fNumLineXY)
		pylab.xlabel('Segment length (angs)')
		#pylab.ylabel('Vtc (mV)')
		pylab.ylabel('Z-Motion (angs)')
		pylab.title('Scan Window', horizontalalignment='right', \
				position=(0.95,0.9), color='red')
		pylab.grid(True)
		return
	
	def vDisplayRetImageCurve(self):
		"""
		Method : vDisplayRetImageCurve
			Pops out Retrace line Exraction result curve

		Arguments :
			None

		Returns :
			None
		"""
		PIEZO_XY = qv.fGetPiezoXCalibration()
		PIEZO_Z = qv.fGetPiezoZCalibration()
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
			fNumLineXY = (fNumLineXY/1000.0)* PIEZO_Z * 10
			pylab.plot(self.xmatrix1,fNumLineXY)
		pylab.xlabel('Segment length (angs)')
		#pylab.ylabel('Vtc (mV)')
		pylab.ylabel('Z-Motion (angs)')
		pylab.title('Retrace Window', horizontalalignment='right', 
				position=(0.95,0.9), color='red')
		pylab.grid(True)
		return
	
	def fCalculateTheta(self):
		"""
		Method : fCalculateTheta
			Calculates angle between line segment & and the axis

		Arguments :
			None

		Returns :
			None
		"""
		dx=float(self.finalpoint[0]-self.initialpoint[0])
		dy=float(self.finalpoint[1]-self.initialpoint[1])
		if dx==0:
			return 90
		if dy==0:
			return 0
		theta = abs(math.atan(dy/dx))
		#print 'Theta',theta,180*theta/math.pi
		return theta
