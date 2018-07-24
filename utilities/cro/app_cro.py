#####################
#   CRO Gui Class   #
#####################

from Tkinter import *
import os
from PIL import ImageTk

iconpath	 	= os.path.join('apps', 'icons')		#  path for icons folder containing thumbimages for toolbar 
quality_iconfile	= os.path.join(iconpath, 'down.png')	

def app_cro():
	"""
	Returns CROGui object
	"""
	oCROGui = CROGui()
	return oCROGui

class CROGui:


    def __init__(self):
	"""
	Class Contructor
	"""
	print 'Soft CRO Window created'
	return

    def createCROwindow(self, master):
	"""
	Create CRO GUI
	"""
	self.croGroup = master
	self.qualityTkImage = ImageTk.PhotoImage(file = quality_iconfile)
	self._vCreateCROwidgets()
	return

    def _vCreateCROwidgets(self):
	"""
	Creates CRO wigets in CRO Window
	"""
	#self.nGraphWidth = 520
	#self.nGraphHeight = 285 
	self.nGraphWidth = 285 
	self.nGraphHeight = 190 
	self.arrYTextLoc = [self.nGraphWidth, self.nGraphHeight]
	self.arrDialTextLoc = [10, self.nGraphHeight]
	self.CanGraph = Canvas(self.croGroup, \
				bg='black', \
				relief=SUNKEN, \
				bd=3, \
				width=self.nGraphWidth, height=self.nGraphHeight)	
	self.CanGraph.grid(row=0,column=0, columnspan=2, sticky='w')
	self.vShowGridlines()

	self.frameSlope = Frame(self.croGroup)
	self.frameSlope.grid(row=1, column=0, sticky='news')

	self.LblSlope = Label (self.frameSlope, text = 'XSL:')
	self.LblSlope.grid (row=0, column=0, sticky=W)

	self.ScaleXSlope = Scale(self.frameSlope, \
				width = 20, \
				sliderlength = 15, \
				#label='X', \
				showvalue=0, \
				orient=HORIZONTAL, \
				)
	self.ScaleXSlope.grid(row=0, column=1, sticky=N+W+S)

	self.ScaleYSlope = Scale(self.frameSlope, \
				width = 20, \
				sliderlength = 15, \
				#label='X', \
				showvalue=0, \
				orient=HORIZONTAL, \
				)
	self.CB_SlopeAdjustQuality = Checkbutton (self.frameSlope, \
				text = 'Fine Adjust Slope', \
				)
	
	frameControlCRO = Frame(self.croGroup)
	frameControlCRO.grid(row=1, column=1, sticky='news')

	Label (frameControlCRO, text = 'CRO:').grid (row=0, column=0, sticky=W)
	self.ScaleVoltsPerDiv = Scale(frameControlCRO, \
				width = 20, \
				sliderlength = 15, \
				#label='Volts/Div:', \
				showvalue=0, \
				orient=HORIZONTAL, \
				)
	self.ScaleVoltsPerDiv.grid(row=0, column=1, sticky=W)
	self.BtnSlopeAdjustQuality = Button (frameControlCRO, \
				compound = CENTER, \
				image = self.qualityTkImage, \
				)
	self.BtnSlopeAdjustQuality.grid(row=0, column=2, sticky=W)
 	return


    def showXSlopeControl(self):
	self.LblSlope.config(text='XSL:')
	self.ScaleXSlope.grid(row=0, column=1, sticky=N+W+S)
	self.ScaleYSlope.grid_forget()
	self.CB_SlopeAdjustQuality.grid_forget()
	return


    def showYSlopeControl(self):
	self.LblSlope.config(text='YSL:')
	self.ScaleYSlope.grid(row=0, column=1, sticky=N+W+S)
	self.ScaleXSlope.grid_forget()
	self.CB_SlopeAdjustQuality.grid_forget()
	return


    def showFineSlopeAdjustControl(self):
	self.ScaleXSlope.grid_forget()
	self.ScaleYSlope.grid_forget()
	self.CB_SlopeAdjustQuality.grid(row = 0, column = 0) 
	return


    def vShowGridlines(self):
	"""
	Shows grid lines in spectography window
	"""

	grid = 23	
	xoff = 7 
	yoff = 5
	xtextoff = 3
	ytextoff = 5
	yspacing = range(0, self.nGraphHeight, grid)
	xspacing = range(0, self.nGraphWidth-5, grid)
	self.nXDiv = len(xspacing)
	self.nYDiv = len(yspacing)
	for i in range(self.nXDiv):
	    self.CanGraph.create_line(xspacing[i]+xoff,yoff,xspacing[i]+xoff,yspacing[-1]+yoff, \
				dash=(4,2), \
				fill='white')
	self.CanGraph.create_line(xspacing[self.nXDiv/2]+xoff,yoff,xspacing[self.nXDiv/2]+xoff,yspacing[-1]+yoff, \
			width=2, \
			fill='white')
	for i in range(self.nYDiv):
	    self.CanGraph.create_line(xoff,yspacing[i]+yoff,xspacing[-1]+xoff,yspacing[i]+yoff, \
				dash=(4,2), \
				fill='white')
	self.CanGraph.create_line(xoff,yspacing[self.nYDiv/2]+yoff,xspacing[-1]+xoff,yspacing[self.nYDiv/2]+yoff, \
			width=2, \
			fill='white')
	self.nGraphArea = [xoff, yoff, xspacing[-1]+xoff, yspacing[-1]+yoff]
	return

'''
    def vShowScaleTextBars(self):
	textbarwidth = 17
	textbarlength = 50
	self.CanGraph.create_text(self.nGraphWidth-textbarlength, 3, text='mV/Div: ', fill='white', anchor=NE)
	self.CanGraph.create_rectangle(self.nGraphWidth-textbarlength,3,self.nGraphWidth,textbarwidth+3, \
					fill='light yellow')
	self.CanGraph.create_text(self.nGraphWidth-textbarlength, self.nGraphHeight-textbarwidth+3, text='mSec/Div: ', fill='white', anchor=NE)
	self.CanGraph.create_rectangle(self.nGraphWidth-textbarlength,self.nGraphHeight-textbarwidth,self.nGraphWidth,self.nGraphHeight, \
					fill='light yellow')
	self.arrXTextLoc = [self.nGraphWidth-textbarlength, self.nGraphHeight-textbarwidth+3]
	self.arrYTextLoc = [self.nGraphWidth-textbarlength+2, 4]
	self.CanGraph.create_text(3, 3, text='Use right & left arrow keys to adjust Volts/Div slider', fill='yellow', anchor=NW)
	return
'''
