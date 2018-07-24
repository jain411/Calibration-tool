#######################
#   MLength Class     #
#######################
from Tkinter import *
import scanner
import tkMessageBox
import math
import dialogs

def mlength(oImaging=None, oScanner=None):
	"""
	Function : mlength
		Returns MLength object

	Arguments :
		oImaging : object of class Imaging
		oScanner : object of class Scanner

	Returns :
		oMlength : object of class MLength
	"""
	oMlength = MLength(oImaging, oScanner)
	return oMlength

class MLength:

	def __init__(self, oImaging, oScanner):
		"""
		Class Contructor : MLength

		Arguments :
			oImaging : object of class Imaging
			oScanner : object of class Scanner

		Returns :
			None
		"""
		self.oImaging = oImaging
		self.oAppImaging=oImaging.oAppImaging
		self.oScanner = oScanner
		self.vInitMLength()
		return

	def vInitMLength(self):
		"""
		Method : vInitMLength
			Initial Setups for MLength
		
		Arguments :
			None
	
		Returns :
			None
		"""
		if self.bCheckImage() == False:
		    tkMessageBox.showwarning('Blank','Oops !! No images on Display')
		    return
		self.vClearCanvas()
		self.bImageChoiceVar = BooleanVar()	
		self.vBindImages()
		dicGUISettings = dialogs.dicReadGUISettings()
		self.strDLColor = dicGUISettings['DLC']
		return

	def bCheckImage(self):
		"""
		Method : bCheckImages
			Checks for image on the Imaging Canvas
				
		Arguments :
			None
	
		Returns :
			None
		"""
		if self.oImaging.bImagePresentVar.get()==False:
			return False
		else:
			return True

	def vClearCanvas(self):
		"""
		Method : vClearCanvas
			Removes Drawn lines from Canvas
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.vDeleteLExtLines()
		self.vDeleteLines()
		self.vDeleteLengthInfo()
		return

	def vBindImages(self):
		"""
		Method : bBindImages
			Binds mouse with Scan  and Retrace Canvas
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.oAppImaging.CanvasScan.bind('<Enter>',self.vScanSelectionCB)
		self.oAppImaging.CanvasRetrace.bind('<Enter>',self.vRetraceSelectionCB)
		return

	def vScanSelectionCB(self,event):
		"""
		Method : vScanSelectionCB
			Checks for mouse's entry in Scan Canvas
				
		Arguments :
			event : Tkiner event for binded mouse
	
		Returns :
			None
		"""
		self.bImageChoiceVar.set(False)
		self.vBindScanCanvas()
		return

	def vRetraceSelectionCB(self,event):
		"""
		Method : vRetraceSelectionCB
			Checks for mouse's entry in Retrace Canvas
				
		Arguments :
			event : Tkiner event for binded mouse
	
		Returns :
			None
		"""
		self.bImageChoiceVar.set(True)
		self.vBindRetraceCanvas()
		return

	def vBindScanCanvas(self):
		"""
		Method : vBindScanCanvas
			Performs mouse bindings with Scan Canvas
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.oAppImaging.CanvasScan.bind('<Button-1>',self.vBeginLineCB)
		self.oAppImaging.CanvasScan.bind('<B1-Motion>',self.vShowLineCB)
		self.oAppImaging.CanvasScan.bind('<ButtonRelease-1>',self.vEndLineCB)
		return

	def vBindRetraceCanvas(self):
		"""
		Method : vBindRetraceCanvas
			Performs mouse bindings with Retrace Canvas
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.oAppImaging.CanvasRetrace.bind('<Button-1>',self.vBeginLineCB)
		self.oAppImaging.CanvasRetrace.bind('<B1-Motion>',self.vShowLineCB)
		self.oAppImaging.CanvasRetrace.bind('<ButtonRelease-1>',self.vEndLineCB)
		return

	def vBeginLineCB(self,event):
		"""
		Method : vBeginLine
			Gets Initial endpoint of the line segment

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		self.x0 = event.x
		self.y0 = event.y
		self.lInitialPoint = [event.x, event.y]
		#print 'starting point',self.lInitialPoint
		return

	def vShowLineCB(self,event):
		"""
		Method : vShowLine
			Displays and Renews line segment with mouse movements

		Arguments :
			None

		Returns :
			None
		"""
		if not self.bCheckRange(event):
			return
		self.x1 = event.x
		self.y1 = event.y
		self.vDeleteLines()
		if self.bImageChoiceVar.get() == False:
			self.ScanMlengthLine = self.oAppImaging.CanvasScan.create_line( \
						self.x0, self.y0,\
						self.x1, self.y1,\
						fill = self.strDLColor,\
						arrow = BOTH,\
						width = 2)
		else: 
			self.RetraceMlengthLine = self.oAppImaging.CanvasRetrace.create_line( \
						self.x0, self.y0,\
						self.x1, self.y1,\
						fill = self.strDLColor,\
						arrow = BOTH,\
						width = 2)
		dXdYDU = self.afCalculateLengthInfo(self.lInitialPoint, [self.x1, self.y1])
		self.vDisplayLengthInfo(dXdYDU)
		return

	def vEndLineCB(self,event):
		"""
		Method : vEndLineCB
			Fetches location of final endpoint

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		self.x1 = event.x
		self.y1 = event.y
		self.lFinalPoint = [event.x, event.y]
		#print 'Final Point', self.lFinalPoint
		self.vUnbindImageCanvas()
		dXdYDU = self.afCalculateLengthInfo(self.lInitialPoint, self.lFinalPoint)
		self.vDisplayLengthInfo(dXdYDU, 'over')
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
		if event.x <= 0 or event.x >= self.oImaging.dicScanParam['ImageSize'][0]:
			return False
		if event.y <= 0 or event.y >= self.oImaging.dicScanParam['ImageSize'][1]:
			return False
		return True

	def vDeleteLines(self):
		"""
		Method : vDeleteLines
			Removes Line segment from the Canvas
			
		Arguments :
			None
				
		Returns :
			None
		"""
		try:
			self.oAppImaging.CanvasScan.delete(self.ScanMlengthLine)
		except:
			pass
		try:
			self.oAppImaging.CanvasRetrace.delete(self.RetraceMlengthLine)
		except:
			pass
		return

	def vDeleteLExtLines(self):
		"""
		Method : vDeleteLExtLines
			Removes Calibration Lines from the Canvas drawn by Line Extraction utility
			
		Arguments :
			None
				
		Returns :
			None
		"""
		try:
			self.oAppImaging.CanvasScan.delete(self.oImaging.ScanCanLine)
		except:
			pass
		try:
			self.oAppImaging.CanvasRetrace.delete(self.oImaging.RetCanLine)
		except:
			pass
		return

	def afCalculateLengthInfo(self,Initialp, Finalp):
		"""
		Method : afCalculateLengthInfo
			Calculates and Displays line segment info
			
		Arguments :
			Initialp : list initial endpoint
			Finalp   : list final endpoint
				
		Returns :
			dX : Displacement along X
			dY : Displacement along Y
			D  : Total Displacement	
		"""
		PIEZO_XY = scanner.fGetPiezoXCalibration()	# nm/V
		fZfactor = self.fCalculateZoomFactor()
		#print '@@@', fZfactor
		if self.oImaging.dicScanParam.has_key('XLArea'):
		    if self.oImaging.dicScanParam['XLArea']:
			nStepSize = self.oImaging.dicScanParam['StepSize'][0] * scanner.XL_GAIN
			strUnits = 'nm'
			fMulFactor = 1000.0
		    else:
			nStepSize = self.oImaging.dicScanParam['StepSize'][0]
			strUnits = 'A'
			fMulFactor = 100.0
		# to keep dX, dY and D in 'angs' PIEZO_XY is divided by 100
		dX = (abs(Finalp[0]-Initialp[0])+1) * \
			(nStepSize / fZfactor) * \
			(PIEZO_XY / fMulFactor) 
		dY = (abs(Finalp[1]-Initialp[1])+1) * \
			(nStepSize / fZfactor) * \
			(PIEZO_XY / fMulFactor) 
		D  = math.sqrt(dX**2 + dY**2)
		#print 'Line Length', D
		return [dX, dY, D, strUnits]

	def vDeleteLengthInfo(self):
	    try:
		self.oAppImaging.CanvasScan.delete(self.ciTextLengthScan[0])
		self.oAppImaging.CanvasScan.delete(self.ciTextLengthScan[1])
		self.oAppImaging.CanvasScan.delete(self.ciTextLengthScan[2])
	    except:
		pass
	    try:
	        self.oAppImaging.CanvasRetrace.delete(self.ciTextLengthRet[0])
	        self.oAppImaging.CanvasRetrace.delete(self.ciTextLengthRet[1])
	        self.oAppImaging.CanvasRetrace.delete(self.ciTextLengthRet[2])
	    except:
	   	pass
	    try:
		self.oAppImaging.CanvasScan.delete(self.ciTextLengthScan[0])
		self.oAppImaging.CanvasScan.delete(self.ciTextLengthScan[1])
		self.oAppImaging.CanvasScan.delete(self.ciTextLengthScan[2])
	    except:
		pass
	    try:
	        self.oAppImaging.CanvasRetrace.delete(self.ciTextLengthRet[0])
	        self.oAppImaging.CanvasRetrace.delete(self.ciTextLengthRet[1])
	        self.oAppImaging.CanvasRetrace.delete(self.ciTextLengthRet[2])
	    except:
	   	pass
	    return

	def vDisplayLengthInfo(self, dXdYDU, status=None):
	    """
	    Argument: array [dX, dY, D, strUnits]
	    """
	    self.vDeleteLengthInfo()
	    text_color = self.strDLColor
	    act_text_color = 'white'	# when mouse pointer is over it
	    strUnits = dXdYDU[-1]
	    self.ciTextLengthScan = [None]*3
	    self.ciTextLengthScan[0] = self.oAppImaging.CanvasScan.create_text(2,225, \
				text='dX: '+ str(round(dXdYDU[0], 2)) + strUnits, \
				anchor=SW, \
				fill=text_color , activefill=act_text_color )
	    self.ciTextLengthScan[1] = self.oAppImaging.CanvasScan.create_text(2,239, \
				text='dY: '+ str(round(dXdYDU[1], 2)) + strUnits, \
				anchor=SW, \
				fill=text_color , activefill=act_text_color )
	    self.ciTextLengthScan[2] = self.oAppImaging.CanvasScan.create_text(2,254, \
				text='D:  '+ str(round(dXdYDU[2], 2)) + strUnits, \
				anchor=SW, \
				fill=text_color , activefill=act_text_color )
	    if self.oImaging.bDumpVar.get()==False:
	        self.ciTextLengthRet = [None]*3
	        self.ciTextLengthRet[0] = self.oAppImaging.CanvasRetrace.create_text(2,225, \
				text='dX: '+ str(round(dXdYDU[0], 2)) + strUnits, \
				anchor=SW, \
				fill=text_color , activefill=act_text_color )
	        self.ciTextLengthRet[1] = self.oAppImaging.CanvasRetrace.create_text(2,239, \
				text='dY: '+ str(round(dXdYDU[1], 2)) + strUnits, \
				anchor=SW, \
				fill=text_color , activefill=act_text_color )
	        self.ciTextLengthRet[2] = self.oAppImaging.CanvasRetrace.create_text(2,254, \
				text='D:  '+ str(round(dXdYDU[2], 2)) + strUnits, \
				anchor=SW, \
				fill=text_color , activefill=act_text_color )
	    if status == 'over':
		    tkMessageBox.showinfo(title='Measure Length',\
				message='Displacement D: ' + str(round(dXdYDU[2], 2)) + strUnits\
				+'\nAlong X: ' + str(round(dXdYDU[0], 2)) + strUnits\
				+'\nAlong Y: ' + str(round(dXdYDU[1], 2)) + strUnits)
		    self.vClearCanvas()
	    return

	def fCalculateZoomFactor(self):
		"""
		Method : fCalculateZoomFactor
			Calculates image's zoom factro
			
		Arguments :
			None
				
		Returns :
			Zfactor : float Zoom factor
		"""
		try:
			fZFactor=self.oImaging.dicScanParam['ImageSize'][0] / self.oImaging.oQlaunch.oCZoom.nInfoImageSize
		except:
			fZFactor=1
		return fZFactor

	def vUnbindImageCanvas(self):
		"""
		Method : vUnbindImageCanvas
			Removes mouse bindings with Scan & Retrace canvases
			
		Arguments :
			None
				
		Returns :
			None
		"""
		self.oAppImaging.CanvasScan.unbind('<Enter>')
		self.oAppImaging.CanvasRetrace.unbind('<Enter>')
		self.oAppImaging.CanvasScan.unbind('<Button-1>')
		self.oAppImaging.CanvasScan.unbind('<B1-Motion>')
		self.oAppImaging.CanvasScan.unbind('<ButtonRelease-1>')
		self.oAppImaging.CanvasRetrace.unbind('<Button-1>')
		self.oAppImaging.CanvasRetrace.unbind('<B1-Motion>')
		self.oAppImaging.CanvasRetrace.unbind('<ButtonRelease-1>')
		return
