######################
#   MAngle Class     #
######################

from Tkinter import *
import tkMessageBox
import math
import dialogs

def mangle(oImaging=None):
	"""
	Function : mangle
		Returns MAngle object

	Arguments :
		oImaging : object of class Imaging

	Returns :
		oMAnle : object of class MAngle
	"""
	oMAngle=MAngle(oImaging)
	return oMAngle
	
class MAngle:
	
	def __init__(self, oImaging):
		"""
		Class Contructor : MAngle

		Arguments :
			oImaging : object of class Imaging

		Returns :
			None
		"""
		self.oImaging = oImaging
		self.oAppImaging = oImaging.oAppImaging
		self.vInitMAngle()
		return

	def vInitMAngle(self):
		"""
		Method : vInitMAngle
			Initial Setups for MAngle
		
		Arguments :
			None
	
		Returns :
			None
		"""
		if self.bCheckImage() == False:
		    tkMessageBox.showwarning('Blank','Oops !! No images on Display')
		    return
		self.bImageChoiceVar = BooleanVar()	
		self.lPosition=[]
		self.vBindImages()
		self.vClearCanvas()
		dicGUISettings = dialogs.dicReadGUISettings()
		self.strAL1Color = dicGUISettings['AL1C']
		self.strAL2Color = dicGUISettings['AL2C']
		return
	
	def bCheckImage(self):
		"""
		Method : bCheckImage
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
	
	def vReBindScanCanvas(self):
		"""
		Method : vReBindScanCanvas
			Performs mouse bindings with Scan Canvas for angle line segment
	
		Arguments :
			None
	
		Returns :
			None
		"""
		self.oAppImaging.CanvasScan.bind('<Button-1>',self.vBeginNewLineCB)
		self.oAppImaging.CanvasScan.bind('<B1-Motion>',self.vShowNewLineCB)
		self.oAppImaging.CanvasScan.bind('<ButtonRelease-1>',self.vEndNewLineCB)
		return

	def vReBindRetraceCanvas(self):
		"""
		Method : vReBindRetraceCanvas
			Performs mouse bindings with Retrace Canvas for angle line segment
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.oAppImaging.CanvasRetrace.bind('<Button-1>',self.vBeginNewLineCB)
		self.oAppImaging.CanvasRetrace.bind('<B1-Motion>',self.vShowNewLineCB)
		self.oAppImaging.CanvasRetrace.bind('<ButtonRelease-1>',self.vEndNewLineCB)
		return
	

	def vBeginLineCB(self,event):
		"""
		Method : vBeginLineCB
			Gets Initial endpoint of refrence line segment

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		self.vDeleteLines()
		self.x0 = event.x
		self.y0 = event.y
		self.lInitialPoint = [event.x, event.y]
		self.lPosition.append(self.lInitialPoint)
		#print 'starting point',self.lInitialPoint
		return

	
	def vBeginNewLineCB(self,event):
		"""
		Method : vBeginNewLineCB
			Draws angle line segment from the inital endpoint of refrence line segment

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		self.vCreateRotateLine(event)
		#print 'starting point',self.lInitialPoint
		return
	

	def vShowLineCB(self,event):
		"""
		Method : vShowLineCB
			Displays and Renews refrence line segment with mouse movements

		Arguments :
			None

		Returns :
			None
		"""
		self.x1 = event.x
		self.y1 = event.y
		if self.bCheckRange(event) == False:
		    return
		self.vDeleteLines()
		if self.bImageChoiceVar.get() == False:
			self.oAppImaging.ScanMlengthLine = \
				self.oAppImaging.CanvasScan.create_line(self.x0, self.y0,\
					self.x1, self.y1,\
					fill = self.strAL1Color,\
					#arrow = BOTH,\
					width = 2)
		else: 
			self.oAppImaging.RetraceMlengthLine = \
				self.oAppImaging.CanvasRetrace.create_line(self.x0, self.y0,\
					self.x1, self.y1,\
					fill = self.strAL1Color,\
					#arrow = BOTH,\
					width = 2)
		return
		
	
	def vShowNewLineCB(self,event):
		"""
		Method : vShowNewLineCB
			Displays and angle refrence line segment with mouse movements

		Arguments :
			None

		Returns :
			None
		"""
		self.x1 = event.x
		self.y1 = event.y
		self.vDeleteNewLines()
		if self.bImageChoiceVar.get() == False:
			self.oAppImaging.RScanMlengthLine = \
				self.oAppImaging.CanvasScan.create_line(self.x0, self.y0,\
					self.x1, self.y1,\
					fill = self.strAL2Color,\
					width = 2)
		else: 
			self.oAppImaging.RRetraceMlengthLine = \
				self.oAppImaging.CanvasRetrace.create_line(self.x0, self.y0,\
					self.x1, self.y1,\
					fill = self.strAL2Color,\
					width = 2)
		if self.bCheckRange(event) == False:
			tkMessageBox.showerror('Error','Cannt go further') 
			self.vDeleteNewLines()
		return
		
	
	def vEndLineCB(self,event):
		"""
		Method : vEndLineCB
			Fetches location of final endpoint of refrence line segment

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		self.x1 = event.x
		self.y1 = event.y
		self.lFinalPoint = [event.x, event.y]
		self.lPosition.append(self.lFinalPoint)
		self.vReBindScanCanvas()
		self.vReBindRetraceCanvas()
		return
	
	def vCreateRotateLine(self,event):
		"""
		Method : vCreateRotateLine
			Draws Angle line segment onto image canvas

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		if self.bImageChoiceVar.get() == False:
			self.oAppImaging.RScanMlengthLine = \
				self.oAppImaging.CanvasScan.create_line(self.x0, self.y0,\
					event.x,event.y,\
					fill = self.strAL1Color,\
					width = 2)
		else: 
			self.oAppImaging.RRetraceMlengthLine = \
				self.oAppImaging.CanvasRetrace.create_line(self.x0, self.y0,\
					event.x,event.y,\
					fill = self.strAL1Color,\
					width = 2)
		return
		
	
	def vEndNewLineCB(self,event):
		"""
		Method : vEndNewLineCB
			Fetches location of final endpoint of angle line segment

		Arguments :
			event : Tkiner event for binded mouse

		Returns :
			None
		"""
		self.x1 = event.x
		self.y1 = event.y
		self.lFinalPoint = [event.x, event.y]
		self.lPosition.append(self.lFinalPoint)
		self.vUnbindImageCanvas()
		self.vCalculateAngle()
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
	
	def vClearCanvas(self):
		"""
		Method : vClearCanvas
			Removes Drawn lines from image canvas
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.vDeleteLines()
		self.vDeleteNewLines()
		self.vDeleteLExtLines()
		return

	def vDeleteLines(self):
		"""
		Method : vDeleteLines
			Removes refrence line segment from the image canvas
			
		Arguments :
			None
				
		Returns :
			None
		"""
		try:
			self.oAppImaging.CanvasScan.delete(self.oAppImaging.ScanMlengthLine)
		except:
			pass
		try:
			self.oAppImaging.CanvasRetrace.delete(self.oAppImaging.RetraceMlengthLine)
		except:
			pass
		return
	
	
	def vDeleteNewLines(self):
		"""
		Method : vDeleteNewLines
			Removes angle line segment from the image canvas
			
		Arguments :
			None
				
		Returns :
			None
		"""
		try:
			self.oAppImaging.CanvasScan.delete(self.oAppImaging.RScanMlengthLine)
		except:
			pass
		try:
			self.oAppImaging.CanvasRetrace.delete(self.oAppImaging.RRetraceMlengthLine)
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
		
	
	def vCalculateAngle(self):
		"""
		Method : vCalculateAngle
			Calculates and Displays Angle 
			
		Arguments :
			None
		
		Returns :
			None
		"""
		fTheta1 = self.fCalculateTheta(self.lPosition[0],self.lPosition[1])
		fTheta2 = self.fCalculateTheta(self.lPosition[0],self.lPosition[2])
		fAngle = abs(fTheta2-fTheta1)
		if fAngle > 180:
			#print 'Measured Angle: ',360-fAngle
			fAngle = 360-fAngle
		tkMessageBox.showinfo(title='Measure Angle', \
			message='Angle: ' + str(round(fAngle, 2)) + ' deg')
		self.vClearCanvas()
		return
	
	def fCalculateTheta(self, lInitialp, lFinalp):
		"""
		Method : fCalculateTheta
			Calculates Angle between the line segment
			
		Arguments :
			lInitialp : list Initial endpoint
			lFinalp   : list Final endpoint
		
		Returns :
			fTheta : float angle
		"""
		dx = float(lFinalp[0] - lInitialp[0])
		dy = float(lFinalp[1] - lInitialp[1])
		if dx == 0:
			return 90
		if dy == 0:
			return 0
		fTheta = (math.atan(dy/dx))*180/math.pi
		if dx>0 and dy<0:
			return abs(fTheta)
		if dx<0 and dy>0:
			return 180+abs(fTheta)
		if dx<0 and dy<0:
			return 180-abs(fTheta)
		if dx>0 and dy>0:
			return 360 - abs(fTheta)
		return fTheta
