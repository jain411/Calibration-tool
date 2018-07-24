##########################
#   CanvasZoom Class     #
##########################
import numpy
import iprog
import math
import tkMessageBox
from Tkinter import *

def canvaszoom(oQlaunch):
	"""
	Function : canvaszoom
		Returns CanvasZom object

	Arguments :
		oQlaunch : object of class QuickLaunch

	Returns :
		ocz : object of class CanvasZoom
	"""
	ocz=CanvasZoom(oQlaunch)
	return ocz


class CanvasZoom:

	def __init__(self,oQlaunch):
		"""
		Class Contructor : CanvasZoom
	
		Arguments :
			oQlaunch : object of class CanvasZoom
				
		Returns :
			None
		"""
		self.oQlaunch = oQlaunch
		self.oImaging = oQlaunch.oImaging
		self.oAppImaging = oQlaunch.oImaging.oAppImaging
		self.vInitCZoom()
		return

	def vInitCZoom(self):
		"""
		Method : vInitCZoom
			Does Initial Settings for Canvas Zoom
				
		Arguments :
			None
				
		Returns :
			None
		"""
		self.vActivateCanvasSelection()
		self.vAquireImageData()
		return

	def vActivateCanvasSelection(self):
		"""
		Method : vActivateCanvasSelection
			Binds mouse with Imaging Canvas
			
		Arguments :
			None
				
		Returns :
			None
		"""
		self.oAppImaging.CanvasScan.bind('<Button-1>', self.vBeginSelectionCB)
		self.oAppImaging.CanvasRetrace.bind('<Button-1>', self.vBeginSelectionCB)
		self.oAppImaging.CanvasScan.bind('<B1-Motion>', self.vShowSelectionCB)
		self.oAppImaging.CanvasRetrace.bind('<B1-Motion>', self.vShowSelectionCB)
		self.oAppImaging.CanvasScan.bind('<ButtonRelease-1>', self.vEndSelectionCB)
		self.oAppImaging.CanvasRetrace.bind('<ButtonRelease-1>', self.vEndSelectionCB)
		return
	
	def vReleaseCanvas(self):
		"""
		Method : vReleaseCanvas
			Removes mouse bindings with Imaging Canvas
			
		Arguments :
			None
				
		Returns :
			None
		"""
		self.oAppImaging.CanvasScan.unbind('<Button-1>')
		self.oAppImaging.CanvasRetrace.unbind('<Button-1>')
		self.oAppImaging.CanvasScan.unbind('<B1-Motion>')
		self.oAppImaging.CanvasRetrace.unbind('<B1-Motion>')
		self.oAppImaging.CanvasScan.unbind('<ButtonRelease-1>')
		self.oAppImaging.CanvasRetrace.unbind('<ButtonRelease-1>')
		return
		
	def vAquireImageData(self):
		"""
		Method : vAquireImageData
			Acquires image data for Zooming in
			
		Arguments :
			None
				
		Returns :
			None
		"""
		self.afScanData = self.oQlaunch.afScanImage
		self.afRetData = self.oQlaunch.afRetImage
		self.nInfoImageSize = self.oQlaunch.nImageSize	
		self.nStepSize = self.oQlaunch.nStepSize
		self.nDelay = self.oQlaunch.nDelay	
		self.bXLArea = self.oQlaunch.bXLArea	
		return

	def vBeginSelectionCB(self,event):
		"""
		Method : vBeginSelectionCB
			Records the starting location
			
		Arguments :
			event : Tkinter binding with mouse
			'	
		Returns :
			None
		"""
		self.arRegion = [[0,0], [0,0]]
		self.arRegion[0] = [event.x, event.y]
		#print 'Starting point',event.x,event.y
		return

	def vShowSelectionCB(self,event):
		"""
		Method : vShowSelectionCB
			Records position changes
			Redraws the selection area as the mouse is moved over the image 
			
		Arguments :
			event : Tkinter binding with mouse
				
		Returns :
			None
		"""
		self.arRegion[1] = [event.x,event.y]
		self.vLimitSelection()
		if self.bCheckRange(event) == False:
			return
		self.vShowBox()
		self.vShowBoxSize()
		return

	def vEndSelectionCB(self,event):
		"""
		Method : vEndSelectionCB
			When mouse button is released it displays the selected image area	
			
		Arguments :
			event : Tkinter binding with mouse
				
		Returns :
			None
		"""
		#print 'End Point', event.x,event.y
		self.vShowSelectionCB(event)	
		if (self.arRegion[1][0] - self.arRegion[0][0])==0:
			return
		if (self.arRegion[1][1] - self.arRegion[0][1])==0:
			return
		self.fZoomIn(self.arRegion)	
		self.vClearBoxSize()
		self.vClearDottedBox()
		return

	def vLimitSelection(self):
		"""
		Method : vLimitSelection
			Traces mouse movement to create squared selection area
			
		Arguments :
			None
				
		Returns :
			None
		"""
		l = (self.arRegion[1][0] - self.arRegion[0][0])
		b = (self.arRegion[1][1] - self.arRegion[0][1])
		if l>b:
			side = b
		else:
			side = l
		self.arRegion[1] = [self.arRegion[0][0]+side, self.arRegion[0][1]+side] 
		return

	def vShowBox(self):
		"""
		Method : vShowBox
			Displays boundary over the selected image area
			
		Arguments :
			None
				
		Returns :
			None
		"""
		try:
		    self.vClearDottedBox()
		except:
			pass
		self.wScanDottedBox = self.oAppImaging.CanvasScan.create_rectangle(self.arRegion)
		self.wRetDottedBox = self.oAppImaging.CanvasRetrace.create_rectangle(self.arRegion)
		return

	def vClearDottedBox(self):
	    self.oAppImaging.CanvasScan.delete(self.wScanDottedBox)
	    self.oAppImaging.CanvasRetrace.delete(self.wRetDottedBox)
	    return

	def vClearBoxSize(self):
	    self.oAppImaging.CanvasScan.delete(self.wScanBoxSize)
	    self.oAppImaging.CanvasRetrace.delete(self.wRetBoxSize)
	    return

	def vShowBoxSize(self):
	    try:
		self.vClearBoxSize()
	    except:
		pass
	    size, units = self.oImaging.oScanner.fCalculateSize(abs(self.arRegion[1][0]-self.arRegion[0][0])+1, self.nStepSize, bXLArea=self.bXLArea)
	    offset = 2
	    self.wScanBoxSize = self.oAppImaging.CanvasScan.create_text(\
			self.arRegion[0][0]+offset, self.arRegion[0][1]+offset,\
			text=str(round(size,2))+units, \
			anchor=NW, \
			)
	    self.wRetBoxSize = self.oAppImaging.CanvasRetrace.create_text(\
			self.arRegion[0][0]+offset, self.arRegion[0][1]+offset,\
			text=str(round(size,2))+units, \
			anchor=NW, \
			)
	    return

	def bCheckRange(self,event):
		"""
		Method : bCheckRange
			Checks whether the selected area is greater than the image size
			
		Arguments :
			event : Tkinter binding with mouse
				
		Returns :
			None
		"""
		if event.x <=0 or event.x > self.afScanData.shape[0]-1:
			return False
		if event.y <=0 or event.y > self.afScanData.shape[1]-1:
			return False 
		return True

	def fZoomIn(self, Region):
		"""
		Method : fZoomIn
			Zooms the selected area to [256,256] pixels
			
		Arguments :
			Region : list containing zoom region coordinates 
				
		Returns :
			None
		"""
		self.nInfoImageSize=abs(float(self.nInfoImageSize*abs(self.arRegion[1][0]-self.arRegion[0][0]+1)))/256.
		xcoords = [self.arRegion[0][1], self.arRegion[1][1]]
		ycoords = [self.arRegion[0][0], self.arRegion[1][0]]
		xcoords.sort()
		ycoords.sort()
		afScanFrameBuffer = self.afScanData[xcoords[0]:xcoords[1]+1, ycoords[0]:ycoords[1]+1]
		afRetFrameBuffer = self.afRetData[xcoords[0]:xcoords[1]+1, ycoords[0]:ycoords[1]+1]
		arScanZoomedImage=self.arCalculateZoomedMatrix(afScanFrameBuffer)
		arRetZoomedImage=self.arCalculateZoomedMatrix(afRetFrameBuffer)
		self.vDisplayZoomedImage(arScanZoomedImage,arRetZoomedImage)
		return
					
	def arCalculateZoomedMatrix(self,arFrameBuffer):
		"""
		Method : arCalculateZoomedMatrix
			Calculates Zoomed image matrix
			
		Arguments :
			arFrameBuffer : float array containing image slice to be zoomed
				
		Returns :
			arZoomedImage : float array containing zoomed image data
		"""
		arZoomedImage=numpy.zeros([256,256],'f')
		off=float(arFrameBuffer.shape[0]-1)/float(arZoomedImage.shape[0])
		for i in range(arZoomedImage.shape[0]):
			for j in range(arZoomedImage.shape[1]):
				offx=off*i
				offy=off*j
				a=int(math.ceil(offx))
				b=int(math.floor(offx))
				c=int(math.ceil(offy))
				d=int(math.floor(offy))
				x1=arFrameBuffer[a][c]
				x2=arFrameBuffer[a][d]
				y1=arFrameBuffer[b][c]
				y2=arFrameBuffer[b][d]
				amp=(x1+x2+y1+y2)/4
				arZoomedImage[i][j]=amp
		return arZoomedImage
			
	def vDisplayZoomedImage(self,arScanZoomedImage,arRetZoomedImage):
		"""
		Method : vDisplayZoomedImage
			Diaplays Zoomed Image
			
		Arguments :
			arScanZoomedImage : float Zoowed Scan image matrix 
			arRetZoomedImage  : float Zoowed Retrace image matrix
		Returns :
			None
		"""
		arScanZoomedImage=iprog.gaussian_(arScanZoomedImage)
		try:
			arRetZoomedImage=iprog.gaussian_(arRetZoomedImage)
		except:
			pass
	
		self.vRenewBoth(arScanZoomedImage,arRetZoomedImage)
		self.oAppImaging.CanvasScan.delete(self.wScanDottedBox)
		self.oAppImaging.CanvasRetrace.delete(self.wRetDottedBox)		
		self.vReleaseCanvas()
		return
				
	def vRenewBoth(self,afScanData,afRetData):
		"""
		Method : vRenewBoth
			Refreshes Image Canvas with Zoomed Scan and Retrace images Canvas
			
		Arguments :
			afScanData : float Scan Image matrix
			afRetData  : float Ret Image matrix
				
		Returns :
			None
		"""
		self.afScanData=afScanData
		self.afRetData=afRetData
		self.oQlaunch.afScanImage=afScanData
		self.oQlaunch.afRetImage=afRetData
		self.oImaging.afScanImageData = afScanData
		self.oImaging.afRetImageData = afRetData		
		self.oImaging.vRenewScanImage(iprog.float2gray(afScanData))	
		if self.oQlaunch.oImaging.bDumpVar.get()==False:
			self.oImaging.vRenewRetImage(iprog.float2gray(afRetData))
		
	        size, units = self.oImaging.oScanner.fCalculateSize(abs(self.arRegion[1][0]-self.arRegion[0][0])+1, self.nStepSize, bXLArea=self.bXLArea)
		self.oImaging.vRenewSize(size, units)
		self.oQlaunch.nImageSize=self.nInfoImageSize
		self.oQlaunch.bZoomVar.set(True)
		return
