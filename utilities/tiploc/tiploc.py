######################
#   TipLoc Class     #
######################
from Tkinter import *
import tkMessageBox
import time

import scanner

def tiploc(oImaging=None, oScanner=None ,oQlaunch=None):
	"""
	Returns object of class TipLoc
	"""
	oTipLoc=TipLoc(oImaging,oScanner,oQlaunch)
	return oTipLoc		


class TipLoc:
	
	def __init__(self, oImaging, oScanner, oQlaunch):
		"""
		Class Contructor : TipLoc
		"""
		self.oScanner = oScanner
		self.oImaging = oImaging
		self.oQlaunch = oQlaunch
		self.oOffset = self.oScanner.oOffset
		self.vInitializeTipLoc()
		self.vBindCallbacks()
		self.nImageSize = self.oScanner.nReadImageSize()
		self.nStepSize = self.oScanner.nReadStepSize()
		self.vShowInitialTipLocation()
		return

	def vInitializeTipLoc(self):
		"""
		Does Inital Checks for TipLoc
		"""
		self.vCheckImage()
		return

	def vCheckImage(self):
		"""
		Checks for image on the Imaging Canvas
		"""
		if not self.oImaging.bImagePresentVar.get():
		    tkMessageBox.showwarning('Blank','Oops !! No images on Display')
		    return
		if self.oQlaunch.bZoomVar.get() == True:
			tkMessageBox.showerror('Not Original', \
				'Need original image for re-locating tip !')
		return
	
	def vBindCallbacks(self):
		"""
		Binds mouse button with the Imaging Window
		"""
		self.oImaging.oAppImaging.CanvasScan.bind('<Button-1>',self.vRelocateTipCB)
		self.oImaging.oAppImaging.CanvasRetrace.bind('<Button-1>',self.vRelocateTipCB)
		self.oImaging.oAppImaging.CanvasScan.config(cursor = 'crosshair')
		self.oImaging.oAppImaging.CanvasRetrace.config(cursor = 'crosshair')
		return

	def vUnbindCallbacks(self):
		"""
		Removes mouse's binding with the Imaging Window
		"""
		self.oImaging.oAppImaging.CanvasScan.unbind("<Button-1>")
		self.oImaging.oAppImaging.CanvasRetrace.unbind("<Button-1>")
		self.oImaging.oAppImaging.CanvasScan.config(cursor = '')
		self.oImaging.oAppImaging.CanvasRetrace.config(cursor = '')
		return

	def vShowInitialTipLocation(self):
		if scanner.getTipParkingMode() == scanner.TIP_PARKING_MODES['center']:
			x_pos = self.nImageSize[0] / 2
			y_pos = self.nImageSize[1] / 2
		if scanner.getTipParkingMode() == scanner.TIP_PARKING_MODES['corner']:
			x_pos = 0
			y_pos = 0 
		dia = 4
		self.InitLocMarkerScan = self.oImaging.oAppImaging.CanvasScan.create_oval(\
					x_pos - dia, y_pos - dia, \
					x_pos + dia, y_pos + dia, \
					fill = 'green')
		self.InitLocMarkerRet = self.oImaging.oAppImaging.CanvasRetrace.create_oval(\
					x_pos - dia, y_pos - dia, \
					x_pos + dia, y_pos + dia, \
					fill = 'green')
		return

	def vShowFinalTipLocation(self, event):
		x_pos, y_pos = event.x, event.y
		dia = 4
		self.FinalLocMarkerScan = self.oImaging.oAppImaging.CanvasScan.create_oval(\
					x_pos - dia, y_pos - dia, \
					x_pos + dia, y_pos + dia, \
					fill = 'red')
		self.FinalLocMarkerRet = self.oImaging.oAppImaging.CanvasRetrace.create_oval(\
					x_pos - dia, y_pos - dia, \
					x_pos + dia, y_pos + dia, \
					fill = 'red')
		return

	def vShowPath(self, event):
		x0 = y0 = self.nImageSize[1]/2
		x1, y1 = event.x, event.y
		self.PathOnScan = self.oImaging.oAppImaging.CanvasScan.create_line(\
					x0, y0, x1, y1, \
					width = 2, \
					arrow = LAST, \
					fill = 'black')
		self.PathOnRet = self.oImaging.oAppImaging.CanvasRetrace.create_line(\
					x0, y0, x1, y1, \
					arrow = LAST, \
					width = 2, \
					fill = 'black')
		return

	def vClearCanvas(self):
		self.oImaging.oAppImaging.CanvasScan.delete(self.InitLocMarkerScan)
		self.oImaging.oAppImaging.CanvasScan.delete(self.FinalLocMarkerScan)
		self.oImaging.oAppImaging.CanvasScan.delete(self.PathOnScan)
		self.oImaging.oAppImaging.CanvasRetrace.delete(self.InitLocMarkerRet)
		self.oImaging.oAppImaging.CanvasRetrace.delete(self.FinalLocMarkerRet)
		self.oImaging.oAppImaging.CanvasRetrace.delete(self.PathOnRet)
		return

	def vRelocateTipCB(self, event):
		"""
		Moves tip to the location choosen by the user
		"""
		self.vShowFinalTipLocation(event)
		self.vShowPath(event)
		self.oScanner.MainMaster.update()
		self.nPixels=[event.x,self.nImageSize[1]-event.y]
		self.nX=self.oOffset.nXoffset
		self.nY=self.oOffset.nYoffset
		print 'Relocate w.r.t.(X,Y):', self.nX, self.nY
		self.nXoffset=((self.nPixels[0]-(self.nImageSize[0]/2))*self.nStepSize[0])+self.nX
		self.nYoffset=((self.nPixels[1]-(self.nImageSize[1]/2))*self.nStepSize[1])+self.nY
		[x,y]=self.oOffset.mv2pix(self.nXoffset,self.nYoffset,self.oOffset.oAppOffset.w/2,self.oOffset.oAppOffset.h/2)
		old_y = self.oOffset.arrPath[-1][1]
		self.oOffset.arrPath.append([x, old_y])
		self.oOffset.vShowMarker(self.nXoffset,self.nYoffset)
		self.oOffset.vShowPath(3)
		self.oOffset.vSetTipLocation(self.nXoffset,self.nYoffset)
		self.oOffset.vCleanPath()
		self.vUnbindCallbacks()
		time.sleep(2)	# for reading the message
		self.vClearCanvas()
		return

