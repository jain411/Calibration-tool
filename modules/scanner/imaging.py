#######################
#   Imaging Class     #
#######################
import os, functools, numpy, cPickle 
import tkSimpleDialog, tkMessageBox, tkFileDialog
from PIL import ImageTk
from PIL import Image as ImagePIL 

import utilities.iprog.iprog as iprog
import apps.quicklaunch as quicklaunch
import apps.dialogs as dialogs
import scanner
import app_imaging

CANVAS_FONT = app_imaging.CANVAS_FONT 
CANVAS_FONT_SIZE = app_imaging.CANVAS_FONT_SIZE

FILETYPES = {	'lut':('Look Up Table Files','*.lut'), \
		}			
sLUTPath = os.path.join(os.curdir, 'lut')	
dumppath = os.path.join(os.curdir, 'dump')
lutfile = os.path.join(sLUTPath, 'default.lut')

__DEBUG__ = True

if __DEBUG__ == True:
	from Tkinter import *

def imaging(f = None):
	"""
	Returns Imaging object
	"""
	if not f :
		root = Tk()
		f = Frame(root).grid()
	oAppImaging = app_imaging.app_imaging()
	oAppImaging.createIWwindow(f)
	oImaging = Imaging(oAppImaging)
	if not f :
		root.title('Imaging Control')
		root.mainloop()
	return oImaging

class Imaging:

    def __init__(self, oAppImaging):
	"""
	Class Contructor : Imaging
	"""
	self.oAppImaging = oAppImaging
	self.oQlaunch = quicklaunch.quicklaunch(self)
        self.strModeVar = StringVar()
	self.strModeVar.set('I')	
	self.bImagePresentVar = BooleanVar()
	self.bImagePresentVar.set(False)
	self.bDumpVar = BooleanVar()
	self.bDumpVar.set(False)	
	self.nDisplayCount = 0
	self.vGetNewGUIColorSettings()
	self.vDisplaylutFile()
	self.ScanArray = None
	self.RetArray = None
	self.winScanFloat = None
	self.winRetFloat = None
	self.winChannelFloat = [None] * 3
	self.TextScale = [None, None, None]
	return

    def vGetScanner(self, oScanner):
	"""
	Links scanner object to Imaging class
	"""
	self.oScanner = oScanner
	return

    def vGetMain(self, MainMaster):
	"""
	Links Main Window to Imaging class
	"""
	self.MainMaster = MainMaster
	return
    
    def vSetDisplayChoice(self):
	"""
	Configure Image Color Mode
		--> RGB
		--> Gray
	"""
	DisplayChoiceDialog(self.MainMaster, self.strModeVar)
	return

    def vGetNewGUIColorSettings(self):
	"""
	Different label colors changed dynamically
	"""
	dicGUISettings = dialogs.dicReadGUISettings()
	self.strAreaInfoColor = dicGUISettings['AreaInfo'][0]
	self.strAreaInfoColorActive = dicGUISettings['AreaInfo'][1]
	self.strScaleColor = dicGUISettings['ZInfo'][0]
	self.strScaleColorActive = dicGUISettings['ZInfo'][1]
	return
	
    def vCreateNewImages(self, dicScanParam):
	"""
	Creates New scan and retrace image of specified image size	
	"""
	self.nDisplayCount = 0
	size = dicScanParam ['ImageSize']
	if dicScanParam.has_key('NoOfChannels'):
	    noc = dicScanParam ['NoOfChannels']
	    if (noc > 1):
		self.vCreateChannelFloatWin (dicScanParam)
	    else:	# Create Separate windows for Single Channel HiRes Scan
		if (size [0] > 256):
		    self.vCreateScanFloatWin (size)
		    self.vCreateRetFloatWin (size)
	return

    def vCreateScanFloatWin (self, size, noc = 1):
	if self.winScanFloat != None:
	    return
	self.winScanFloat = Toplevel(self.MainMaster)
	self.winScanFloat.resizable(False, False)
	self.winScanFloat.title('HiRes Display: Scan')
	self.winScanFloat.protocol('WM_DELETE_WINDOW', self.vScanFloatCancelCB)
	self.CanScanFloat = Canvas(self.winScanFloat, \
				width=size[1], height=size[0], \
				relief=RIDGE, \
				bg = "light yellow")
	self.CanScanFloat.grid(sticky=N+E+W+S)
	return

    def vCreateRetFloatWin(self, size, noc = 1):
	if self.winRetFloat != None:
	    return
	self.winRetFloat = Toplevel(self.MainMaster)
	self.winRetFloat.resizable(False, False)
	self.winRetFloat.title('HiRes Display: Retrace')
	self.winRetFloat.protocol('WM_DELETE_WINDOW', self.vRetFloatCancelCB)
	self.CanRetFloat = Canvas(self.winRetFloat, \
				width=size[1], height=size[0], \
				relief=RIDGE, \
				bg = "light yellow")
	self.CanRetFloat.grid (sticky=N+E+W+S)
	return

    def vCreateChannelFloatWin (self, dicScanParam):
	size = dicScanParam ['ImageSize']
	noc = dicScanParam ['NoOfChannels']
	channel_names = dicScanParam ['ChannelNames']
	if self.winChannelFloat.count (None) == 0:
		# If Windows exist, then only their title updated 
		self.refreshChannelLabels(size, noc, channel_names)
		for count in range (noc):
			self.winChannelFloat [count].title (channel_names [count] + ' Channel')
		return
	for window in self.winChannelFloat:	# existing windows closed
	    if window != None:
		window.destroy()
	self.winChannelFloat = [None] * noc
	self.CanChannelScanFloat = [None] * noc
	self.CanChannelRetFloat = [None] * noc

	scale_bar_h = 15
	scale_bar_color = 'light blue'
	for count in range (noc):
	    self.winChannelFloat [count] = Toplevel (self.MainMaster)
	    self.winChannelFloat [count].resizable (False, False)
	    self.winChannelFloat [count].title (channel_names [count] + ' Channel')
	    self.winChannelFloat [count].protocol ('WM_DELETE_WINDOW', \
						functools.partial (self.vChannelFloatCancelCB, count))
	    self.CanChannelScanFloat [count] = Canvas(self.winChannelFloat [count], \
						width=size[1], height=size[0] + scale_bar_h, \
						relief=RIDGE, \
						bg = "light yellow")
	    self.CanChannelScanFloat [count].grid(row = 0, column = 0, sticky=N+E+W+S, padx = 2, pady = 2)
	    self.CanChannelRetFloat [count] = Canvas (self.winChannelFloat [count], \
				width=size [1], height=size [0] + scale_bar_h, \
				relief=RIDGE, \
				bg = "light yellow")
	    self.CanChannelRetFloat [count].grid (row = 0, column = 1, sticky=N+E+W+S, padx = 2, pady = 2)
	    self.CanChannelScanFloat [count].create_rectangle(0, size [0], size [1] + scale_bar_h, size [0] + scale_bar_h, \
					width=0, fill=scale_bar_color)
	    self.CanChannelRetFloat [count].create_rectangle(0, size [0], size [1] + scale_bar_h, size [0] + scale_bar_h, \
					width=0, fill=scale_bar_color)
	self.refreshChannelLabels(size, noc, channel_names)
	return

    def refreshChannelLabels(self, size, noc, channel_names):
	for count in range (noc):
		try:
	    		self.CanChannelScanFloat[count].delete(self.ciChnTextScan[count])
		except:
			pass
		try:
	    		self.CanChannelRetFloat[count].delete(self.ciChnTextRet[count])
		except:
			pass
	self.ciChnTextScan = [None] * noc
	self.ciChnTextRet = [None] * noc

	for count in range (noc):
	    stext = channel_names [count][:6] + '(S)'
	    self.ciChnTextScan[count] = self.CanChannelScanFloat [count].create_text(size [1], \
			size [0] , \
			text=stext, \
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			anchor=NE, 
			fill='blue')
	    rtext = channel_names [count][:6] + '(R)'
	    self.ciChnTextRet[count] = self.CanChannelRetFloat [count].create_text(size [1], size [0], \
			text=rtext, \
			anchor=NE, \
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill='blue')

	return
	
    def vRefreshScanFloatImage(self, tkImScanImage):
	if self.winScanFloat == None:
	    return
	self.iCanScanFloat = self.CanScanFloat.create_image(0,0, \
				image=tkImScanImage, anchor=NW)
	return

    def vRefreshRetFloatImage(self, tkImRetImage):
	if self.winRetFloat == None:
	    return
	self.iCanRetFloat = self.CanRetFloat.create_image(0,0, \
				image=tkImRetImage, anchor=NW)
	#self.MainMaster.update()
	return

    def vScanFloatCancelCB(self):
	self.winScanFloat.destroy ()
	self.winScanFloat = None
	return

    def vRetFloatCancelCB(self):
	self.winRetFloat.destroy()
	self.winRetFloat = None
	return

    def vChannelFloatCancelCB(self, noc):
	self.winChannelFloat [noc].destroy ()
	self.winChannelFloat [noc] = None
	return

    def vInitializeScanImage(self, size, noc = 1):
	"""
	Prepares a fresh scan canvas with a blank image
	"""
	if noc == 1:
	    self.ScanArray = ImagePIL.new (self.strModeVar.get (), (size [1], size [0]))
	    self.ScanImage = ImageTk.PhotoImage(self.ScanArray)
	    self.CanScan = self.oAppImaging.CanvasScan.create_image(0, 0, image = self.ScanImage, anchor = NW)
	else:
	    self.ScanArray = []
	    self.ScanImage = []
	    self.CanScan = [] 
	    for count in range (noc):
		self.ScanArray.append (ImagePIL.new (self.strModeVar.get (), (size [1], size [0])))
		self.ScanImage.append (ImageTk.PhotoImage(self.ScanArray [count]))
		self.CanScan.append (self.oAppImaging.CanvasScan.create_image (0, 0, \
					image = self.ScanImage [count], anchor = NW))
 	return

    def vInitializeRetImage(self, size, noc = 1):
	"""
	Prepares a fresh retrace canvas with a blank image
	"""
	if noc == 1:
	    self.RetArray = ImagePIL.new(self.strModeVar.get(), (size[1],size[0]))
	    self.RetImage = ImageTk.PhotoImage(self.RetArray)
	    self.CanRet = self.oAppImaging.CanvasRetrace.create_image(0,0, image=self.RetImage, anchor=NW)
	else:
	    self.RetArray = []
	    self.RetImage = []
	    self.CanRet = [] 
	    for count in range (noc):
	        self.RetArray.append (ImagePIL.new(self.strModeVar.get(), (size[1],size[0])))
	        self.RetImage.append (ImageTk.PhotoImage(self.RetArray [count]))
	        self.CanRet.append (self.oAppImaging.CanvasRetrace.create_image(0, 0, \
					image=self.RetImage [count], anchor=NW))
 	return

    def vRenewScan(self, fmatrix, dicScanParam=None, bDump=True, noc = 1):
	"""
	Displays a given float matrix as an image on the Scan Window
	"""
	if bDump:	# Finally when scan is over
	    fd = open(os.path.join(dumppath, 'scanimgdump.dmp'),'w')	
	    cPickle.dump(fmatrix, fd)	
	    cPickle.dump(dicScanParam, fd)	
	    fd.close()	
	self.dicScanParam = dicScanParam
	self.oQlaunch.afOrigScanData = fmatrix	# Data for right click image filters
	self.afScanImageData = fmatrix
	if dicScanParam != None:
	    if dicScanParam.has_key('NoOfChannels'):
		noc = dicScanParam ['NoOfChannels']
	if noc == 1:
	    graymatrix = iprog.float2gray(fmatrix)
	else:
	    graymatrix = []
	    for count in range (noc):
		graymatrix.append (iprog.float2gray (fmatrix [count]))
	self.vRenewScanImage (graymatrix, noc)
	self.oQlaunch.bQlaunchVar.set(True)
	return

    def vRenewRet(self, fmatrix, dicScanParam=None, bDump=True, noc = 1):
	"""
	Displays a given float matrix as an image on the Retrace Window
	"""
	#if self.oScanner.bScanStatusVar.get() == True:
	if bDump:
       	    fd=open(os.path.join(dumppath, 'retimgdump.dmp'),'w')	
	    cPickle.dump(fmatrix, fd)	
	    cPickle.dump(dicScanParam, fd)
	    fd.close()
	    print 'Dumping..'			
	self.oQlaunch.afOrigRetData = fmatrix			# for transffering data to Qlaunch when
	self.afRetImageData = fmatrix					# for line extraction
	
	if dicScanParam != None:
	    if dicScanParam.has_key('NoOfChannels'):
		noc = dicScanParam ['NoOfChannels']
	if noc == 1:
	    graymatrix = iprog.float2gray (fmatrix)
	else:
	    graymatrix = []
	    for count in range (noc):
		graymatrix.append (iprog.float2gray (fmatrix [count]))
	self.vRenewRetImage (graymatrix, noc)
	return

    def vRenewScanImage(self, graymatrix, noc = 1):
	"""
	Renews and displays scan image with image data
	"""
	try:
		self.vRemoveRoughnessDisplay()
	except:
		pass
	if self.strModeVar.get()=='I':
		self.vRenewGrayScanImage(graymatrix, noc)
	if self.strModeVar.get()=='RGB':
		self.vRenewRGBScanImage(graymatrix, noc)
	return

    def vRenewRGBScanImage (self, graymatrix, noc):
	"""
	Renews and displays scan image with the RGB image data
	"""
	if noc == 1:
	    im_size = graymatrix.shape
	    self.vInitializeScanImage (graymatrix.shape)
	    # Added to handle saturated ADC outputs ..
	    lNaNIndices = numpy.isnan (graymatrix)
	    graymatrix [lNaNIndices] = 0
	    colmatrix = map (lambda (x) : self.RGB [int (x)], graymatrix.flat)
	    self.ScanArray.putdata (colmatrix)
	    self.ScanImage.paste (self.ScanArray)
	    if (im_size[0] > 256) or (im_size[1] > 256):	# HiRes Scan
		self.vRefreshScanFloatImage (self.ScanImage)
	    	#self.ScanImage.subsample(256,256)
	else:
	    self.vInitializeScanImage (graymatrix [0].shape, noc)
	    for count in range (noc):
		im_size = graymatrix [count].shape
		# Added to handle saturated ADC outputs ..
		lNaNIndices = numpy.isnan (graymatrix [count])
		graymatrix [count] [lNaNIndices] = 0
		colmatrix = map (lambda (x) : self.RGB [int (x)], graymatrix [count].flat)
		self.ScanArray [count].putdata (colmatrix)
		self.ScanImage [count].paste (self.ScanArray [count])
		self.CanChannelScanFloat [count].create_image(0, 0, \
				image = self.ScanImage [count], anchor=NW)
		self.winChannelFloat [count].update() 
	self.bImagePresentVar.set (True)
	return
 
    def vRenewRetImage (self, graymatrix, noc = 1):
	"""
	Renews the retrace image with gray image data
	"""
	if self.strModeVar.get()=='I':
		self.vRenewGrayRetImage(graymatrix, noc)
	if self.strModeVar.get()=='RGB':
		self.vRenewRGBRetImage(graymatrix, noc)
	return

    def vRenewRGBRetImage(self, graymatrix, noc):	
	"""
	Renews the retrace image with RGB image data
	"""
	if noc == 1:
	    im_size = graymatrix.shape
	    self.vInitializeRetImage (graymatrix.shape)
	    # Added to handle saturated ADC outputs ..
	    lNaNIndices = numpy.isnan (graymatrix)
	    graymatrix [lNaNIndices] = 0
	    colmatrix = map (lambda (x) : self.RGB [int (x)], graymatrix.flat)
	    self.RetArray.putdata (colmatrix)
	    self.RetImage.paste (self.RetArray)
	    if (im_size[0] > 256) or (im_size[1] > 256):	# HiRes Scan
		self.vRefreshRetFloatImage (self.RetImage)
	    	#self.RetImage.subsample(256./im_size[0])
	else:
	    self.vInitializeRetImage (graymatrix [0].shape, noc)
	    for count in range (noc):
		im_size = graymatrix[count].shape
		# Added to handle saturated ADC outputs ..
		lNaNIndices = numpy.isnan (graymatrix [count])
		graymatrix [count] [lNaNIndices] = 0
		colmatrix = map (lambda (x) : self.RGB [int (x)], graymatrix [count].flat)
		self.RetArray [count].putdata (colmatrix)
		self.RetImage [count].paste (self.RetArray [count])
		self.CanChannelRetFloat [count].create_image(0, 0, \
				image = self.RetImage [count], anchor=NW)
		self.winChannelFloat [count].update() 
	self.bImagePresentVar.set(True)
	return

    def vRenewGrayScanImage(self, graymatrix):
	"""
	Renews and displays scan image with the gray image data
	"""
	[row,col] = graymatrix.shape
	self.vInitializeScanImage(graymatrix.shape)
	self.ScanArray.putdata(graymatrix.flat)	
	self.ScanImage.paste(self.ScanArray)	
	self.bImagePresentVar.set(True)
	self.nDisplayCount += 1
	return

    def vRenewGrayRetImage(self, graymatrix):
	"""
	Renews the retrace image with gray image data
	"""
	[row,col] = graymatrix.shape
	self.vInitializeRetImage(graymatrix.shape)
	self.RetArray.putdata(graymatrix.flat)
	self.RetImage.paste(self.RetArray)	
	self.bImagePresentVar.set(True)
	self.nDisplayCount += 1
	return	

    def vRenewSize (self, size=None, units=None, noc=1):
	"""
	Prints image size on the scan image canvas
	"""
	self.vGetNewGUIColorSettings()
	try:
	    self.oAppImaging.CanvasScan.delete(self.TextScanSize)
	except:
	    pass
	try:
	    self.oAppImaging.CanvasRetrace.delete(self.TextRetSize)
	except:
	    pass
	h = 256
	size_txt = ('%3.3f' % size) + units
	self.TextScanSize = self.oAppImaging.CanvasScan.create_text (1, 1 + h , \
			text = size_txt, \
                        font = (CANVAS_FONT, CANVAS_FONT_SIZE), \
			anchor = NW,
			fill = self.strAreaInfoColor)#, \
			#activefill=self.strAreaInfoColorActive)
	if self.bDumpVar.get()==False:
		self.TextRetSize = self.oAppImaging.CanvasRetrace.create_text(1,1 + h, \
			text = size_txt, \
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			anchor=NW, fill=self.strAreaInfoColor)#, \
			#activefill=self.strAreaInfoColorActive)
	else:
		pass
	if noc > 1:
		self.vRenewSizeFloat(size, units, noc)
	self.vRenewScaleBar(size, units, noc)
	return


    def vRenewSizeFloat(self, size, units, noc):
	for count in range (noc):
		try:
			self.CanChannelScanFloat[count].delete(self.TextScanSizeFloat[count])
		except:
		    pass
		try:
			self.CanChannelRetFloat[count].delete(self.TextRetSizeFloat[count])
		except:
		    pass
	self.TextScanSizeFloat = []
	self.TextRetSizeFloat = []

	for count in range (noc):
		h = 256
		size_txt = '%3.3f' % size
		scan_text = self.CanChannelScanFloat[count].create_text (1, 1 + h , \
			text = size_txt + units, \
			anchor = NW,
			font = (CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill = self.strAreaInfoColor)#, \
			#activefill=self.strAreaInfoColorActive)
		self.TextScanSizeFloat.append(scan_text)

		if self.bDumpVar.get()==False:
			ret_text = self.CanChannelRetFloat[count].create_text (1, 1 + h , \
				text = size_txt + units, \
				font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
				anchor=NW, fill=self.strAreaInfoColor)#, \
				#activefill=self.strAreaInfoColorActive)
			self.TextRetSizeFloat.append(ret_text)
		else:
			pass
	return

    def vRenewScaleBar(self, size=None, units=None, noc = 1):
	try:
	    self.oAppImaging.CanvasScan.delete(self.TextScanSB)
	    self.oAppImaging.CanvasScan.delete(self.ciScanSBLine)
	except:
	    pass
	try:
	    self.oAppImaging.CanvasRetrace.delete(self.TextRetSB)
	    self.oAppImaging.CanvasRetrace.delete(self.ciRetSBLine)
	except:
	    pass
	if units == u'\u00B5m':
		if size < 5:
		    size *= 1e3
		    units = 'nm'
		else:
		    units = u'\u00B5m'
	if int(size)/5 > 5:	# this is to get scale bar in multiples of 5
	    nScaleBarLen = int ((size / 5) - ((size / 5) % 5))
	else:
	    nScaleBarLen = int (size / 5)
	im_pix = self.dicScanParam['ImageSize'][0]
	SBTextLoc = 145
	SBLineLoc = 140
	nSB_PixLen = (im_pix/size) * nScaleBarLen  
	self.TextScanSB = self.oAppImaging.CanvasScan.create_text(SBTextLoc, im_pix + 1 , \
			text=str(nScaleBarLen) + units, \
			anchor=NW, 
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill=self.strAreaInfoColor)#, \
			#activefill=self.strAreaInfoColorActive)
	if self.bDumpVar.get()==False:
		self.TextRetSB = self.oAppImaging.CanvasRetrace.create_text(SBTextLoc, im_pix + 1, \
			text=str(nScaleBarLen) + units, \
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			anchor=NW, fill=self.strAreaInfoColor)#, \
			#activefill=self.strAreaInfoColorActive)
	else:
		pass
	self.ciScanSBLine = self.oAppImaging.CanvasScan.create_line(SBLineLoc - nSB_PixLen, im_pix + 8 , SBLineLoc, im_pix + 8 ,\
			fill=self.strAreaInfoColor, \
			width = 2)
	if self.bDumpVar.get()==False:
		self.ciRetSBLine = self.oAppImaging.CanvasRetrace.create_line(SBLineLoc - nSB_PixLen, im_pix + 8, SBLineLoc, im_pix + 8, \
			fill=self.strAreaInfoColor, \
			width = 2)
	else:
		pass
	
	if noc > 1:
		self.vRenewScaleBarFloat(nSB_PixLen, nScaleBarLen, units, noc)
	return

    def vRenewScaleBarFloat(self, nSB_PixLen, nScaleBarLen, units, noc):
	for count in range (noc):
		try:
		    self.CanChannelScanFloat[count].delete(self.TextScanSBFloat[count])
		    self.CanChannelScanFloat[count].delete(self.ciScanSBLineFloat[count])
		except:
		    pass
		try:
		    self.CanChannelRetFloat[count].delete(self.TextRetSBFloat[count])
		    self.CanChannelRetFloat[count].delete(self.ciRetSBLineFloat[count])
		except:
		    pass
	self.TextScanSBFloat = []
	self.TextRetSBFloat = []
	self.ciScanSBLineFloat = []
	self.ciRetSBLineFloat = []

	im_pix = self.dicScanParam['ImageSize'][0]
	SBTextLoc = 145
	SBLineLoc = 140

	for count in range (noc):
		textScanSB = self.CanChannelScanFloat[count].create_text(SBTextLoc, im_pix + 1 , \
			text=str(nScaleBarLen) + units, \
			anchor=NW, 
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill=self.strAreaInfoColor)#, \
			#activefill=self.strAreaInfoColorActive)
		self.TextScanSBFloat.append(textScanSB)
		if self.bDumpVar.get()==False:
			textRetSB = self.CanChannelRetFloat[count].create_text(SBTextLoc, im_pix + 1 , \
				text=str(nScaleBarLen) + units, \
				font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
				anchor=NW, fill=self.strAreaInfoColor)#, \
				#activefill=self.strAreaInfoColorActive)
			self.TextRetSBFloat.append(textRetSB)
		else:
			pass

		ciScanSBLine = self.CanChannelScanFloat[count].create_line(SBLineLoc - nSB_PixLen, \
			im_pix + 8 , SBLineLoc, im_pix + 8 ,\
			fill=self.strAreaInfoColor, \
			width = 2)
		self.ciScanSBLineFloat.append(ciScanSBLine)

		if self.bDumpVar.get()==False:
			ciRetSBLine = self.CanChannelRetFloat[count].create_line(\
				SBLineLoc - nSB_PixLen, \
				im_pix + 8, SBLineLoc, im_pix + 8, \
				fill=self.strAreaInfoColor, \
				width = 2)
			self.ciRetSBLineFloat.append(ciScanSBLine)
		else:
			pass
	return


    def vShowScale(self, mean, min, max, units = 'nm'):
	try:
	    self.oAppImaging.CanvasColor.delete(self.TextScale[0])
	    self.oAppImaging.CanvasColor.delete(self.TextScale[1])
	    self.oAppImaging.CanvasColor.delete(self.TextScale[2])
	except:
	    pass
	scale_bar_h = 15
	self.TextScale[0] = self.oAppImaging.CanvasColor.create_text(0,0,\
			anchor=NW, \
			text=str(round(max,1)) + units, \
			#width=4,
			activefill=self.strScaleColorActive, \
                        font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill=self.strScaleColor)
	self.TextScale[1] = self.oAppImaging.CanvasColor.create_text(0,127,\
			anchor=NW, \
			text=str(round(mean,1)) + units, \
			#width=4,
			activefill=self.strScaleColorActive, \
                        font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill=self.strScaleColor)
	self.TextScale[2] = self.oAppImaging.CanvasColor.create_text(0,255,\
			anchor=NW, \
			text=str(round(min,1)) + units, \
			#width=4,
			activefill=self.strScaleColorActive, \
                        font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill=self.strScaleColor)
	return

    def sGetFileType(self, sFileType):
	"""
	Checks whether open image`s format is .dmp if it is than 
	line extraction utility is disables since it cannt work on gray data 
	provided by the iprog generated dmp file
	"""
	if sFileType == "dmp":
		self.bDumpVar.set(True)
	else:
		self.bDumpVar.set(False)
	return
    
    def vRefreshImageCanvas(self):
	try:
		self.oAppImaging.CanvasScan.delete(self.sScanMean)
		self.oAppImaging.CanvasScan.delete(self.sScanStddev)
	except:
		pass
	try:
		self.oAppImaging.CanvasRetrace.delete(self.sRetMean)
		self.oAppImaging.CanvasRetrace.delete(self.sRetStddev)
	except:
		pass
	try:
		self.oAppImaging.CanvasScan.delete(self.ScanCanLine)
	except:
		pass
	try:
		self.oAppImaging.CanvasRetrace.delete(self.RetCanLine)
	except:
		pass
	return	
	
#######################LookUp Table #################################################	
    def vDisplaylutFile(self,fname=lutfile):
	"""
	Loads LookUp Table
	"""
	self.vReadLUTFile(fname)
	self.vInsertColorStrip()
	self.vShowScaleGraduation()
	try:
	    self.oScanner.vShowScaleInfo()		
	except:
	    pass
	return	

    def vReadLUTFile(self,fname):
	"""
	Extracts data from LookUp table file
	"""
	try:
	    f = open(fname)
	except:
	    print 'Lookup table is not in its usual place, trying default'
	    sDefaultLUTFile = os.path.join(os.curdir, sLUTPath, 'revdefault.lut')
	    f = open(sDefaultLUTFile)
	    # Save the default LUT File location 
	    dicGlobParam = scanner.dicReadGlobalParam()
	    dicGlobParam['lutfile'] = sDefaultLUTFile
	    scanner.vWriteGlobalParam(dicGlobParam)
	f.readline()	# Comment Line in the LUT file
	self.RGB=[]
	for i in range(256):
		asColorVal = f.readline().split()
		rgb = map(lambda(x):int(float(x)*255), asColorVal)
		self.RGB.append(tuple(rgb[:3]))
	f.close()
	return
	
    def vLoadNewlutFile(self):
	"""
	Pops up a file dialog to load a new LookUp table file
	"""
	ftype = FILETYPES.values()
	file = tkFileDialog.askopenfilename(title='LookUp Table',defaultextension=".lut",filetypes=ftype,initialdir=sLUTPath,initialfile='default')
	if not(file):
		#tkMessageBox.showerror('Error','No File Selected !!')
		return
	self.vDisplaylutFile(file)
	self.strModeVar.set('RGB')
	#print self.bImagePresentVar.get()
	if self.bImagePresentVar.get()==True:
		self.oQlaunch.vOriginalCB()
	return
	
    def vInsertColorStrip(self):
	"""
	Insert Color gradient strip to the Color canvas 
	"""
	#data = numpy.zeros([256,256],'Int')
	data = numpy.zeros([256,35],'i')
	for i in range(data.shape[1]):
	    data[:,i] = range(255, -1, -1)
	ncolmatrix = map(lambda(x):self.RGB[int(x)],data.flat)
	from PIL import Image
	self.lutim = ImagePIL.new('RGB', [35,256])
	self.ArrlutIm = ImageTk.PhotoImage(self.lutim)
	self.lutim.putdata(ncolmatrix)
	self.ArrlutIm.paste(self.lutim)
	self.oAppImaging.ColorArray = self.oAppImaging.CanvasColor.create_image(0,0,\
					image=self.ArrlutIm, \
					anchor=NW)
	return

    def vShowScaleGraduation(self):
	self.vGetNewGUIColorSettings()
	self.MinGrad = 	self.oAppImaging.CanvasColor.create_line(25,255,35,255,\
					width=2,\
					fill=self.strScaleColor)
	self.MaxGrad = 	self.oAppImaging.CanvasColor.create_line(25,1,35,1,\
					width=2,\
					fill=self.strScaleColor)
	self.MeanGrad = self.oAppImaging.CanvasColor.create_line(25,127,35,127,\
					width=2,\
					fill=self.strScaleColor)
	return

###############################Scan Progress###########################################	
    def vShowHScanProgress(self, step):
	"""
	Displays Horizontal Scan Progress 
	"""
	try:
		self.oAppImaging.CanvasScan.delete(self.Scanline)
	except:
		pass
	try:
		self.oAppImaging.CanvasRetrace.delete(self.Retline)
	except:
		pass
	if self.oScanner.oDaq.alter == 1:
		self.Scanline = self.oAppImaging.CanvasScan.create_line(0,step,\
				int(self.oScanner.dicScanParam['ImageSize'][0]),\
					int(step),fill='red')
		self.Retline = self.oAppImaging.CanvasRetrace.create_line(0,step,\
					int(self.oScanner.dicScanParam['ImageSize'][0]),\
					int(step),fill='red')
	else:
		self.Scanline = self.oAppImaging.CanvasScan.create_line(0,self.oScanner.dicScanParam['ImageSize'][0]-step,\
					int(self.oScanner.dicScanParam['ImageSize'][0]),\
					self.oScanner.dicScanParam['ImageSize'][0]-int(step),fill='red')
		self.Retline = self.oAppImaging.CanvasRetrace.create_line(0,self.oScanner.dicScanParam['ImageSize'][0]-step,\
					int(self.oScanner.dicScanParam['ImageSize'][0]),\
					self.oScanner.dicScanParam['ImageSize'][0]-int(step),fill='red')

	return

    def vShowVScanProgress(self, step):
	"""
	Displays Vertical Scan Progress 
	"""
	try:
		self.oAppImaging.CanvasScan.delete(self.Scanline)
	except:
		pass
	try:
		self.oAppImaging.CanvasRetrace.delete(self.Retline)
	except:
		pass
	if self.oScanner.oDaq.alter == 1:
		self.Scanline = self.oAppImaging.CanvasScan.create_line(step,0,\
					int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
					fill='blue')
		self.Retline = self.oAppImaging.CanvasRetrace.create_line(step,0,\
					int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
					fill='blue')
	else:
		self.Scanline = self.oAppImaging.CanvasScan.create_line(self.oScanner.dicScanParam['ImageSize'][0]-step,0,\
					self.oScanner.dicScanParam['ImageSize'][0]-int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
					fill='blue')
		self.Retline = self.oAppImaging.CanvasRetrace.create_line(self.oScanner.dicScanParam['ImageSize'][0]-step,0,\
					self.oScanner.dicScanParam['ImageSize'][0]-int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
					fill='blue')
	return

    def vShow_HR_HScanProgress(self, step):
	"""
	Displays Horizontal Scan Progress 
	"""
	try:
		self.CanScanFloat.delete(self.iScanFloatLine)
	except:
		pass
	try:
		self.CanRetFloat.delete(self.iRetFloatLine)
	except:
		pass
	if self.oScanner.oDaq.alter == 1:
	  if self.winScanFloat != None:
	    self.iScanFloatLine = self.CanScanFloat.create_line(0,step,\
		int(self.oScanner.dicScanParam['ImageSize'][0]),\
		int(step),fill='red')
	  if self.winRetFloat != None:
	    self.iRetFloatLine = self.CanRetFloat.create_line(0,step,\
		int(self.oScanner.dicScanParam['ImageSize'][0]),\
		int(step),fill='red')
	else:
	  if self.winScanFloat != None:
	    self.iScanFloatLine = self.CanScanFloat.create_line(0,self.oScanner.dicScanParam['ImageSize'][0]-step,\
		int(self.oScanner.dicScanParam['ImageSize'][0]),\
		self.oScanner.dicScanParam['ImageSize'][0]-int(step),\
		fill='red')
	  if self.winRetFloat != None:
	    self.iRetFloatLine = self.CanRetFloat.create_line(0,self.oScanner.dicScanParam['ImageSize'][0]-step,\
		int(self.oScanner.dicScanParam['ImageSize'][0]),\
		self.oScanner.dicScanParam['ImageSize'][0]-int(step),\
		fill='red')
	return

    def vShow_HR_VScanProgress(self, step):
	"""
	Displays Vertical Scan Progress 
	"""
	try:
		self.CanScanFloat.delete(self.iScanFloatLine)
	except:
		pass
	try:
		self.CanRetFloat.delete(self.iRetFloatLine)
	except:
		pass
	if self.oScanner.oDaq.alter == 1:
	  if self.winScanFloat != None:
	    self.iScanFloatLine = self.CanScanFloat.create_line(step,0,\
		int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
		fill='blue')
	  if self.winRetFloat != None:
	    self.iRetFloatLine = self.CanRetFloat.create_line(step,0,\
		int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
		fill='blue')
	else:
	  if self.winScanFloat != None:
	    self.iScanFloatLine = self.CanScanFloat.create_line(self.oScanner.dicScanParam['ImageSize'][0]-step,0,\
		self.oScanner.dicScanParam['ImageSize'][0]-int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
		fill='blue')
	  if self.winRetFloat != None:
	    self.iRetFloatLine = self.CanRetFloat.create_line(self.oScanner.dicScanParam['ImageSize'][0]-step,0,\
		self.oScanner.dicScanParam['ImageSize'][0]-int(step),int(self.oScanner.dicScanParam['ImageSize'][0]),\
		fill='blue')
	return
    
##########################Display Choice Dialog###########################################

class DisplayChoiceDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, DisplayVar):
	self.DisplayVar = DisplayVar
	self.GRAY = 'I'
	self.RGB = 'RGB'
	tkSimpleDialog.Dialog.__init__(self, master, 'Display Settings')
	return

    def body(self, master):
	self.master = master
	Label(text='Display Selection')
	self.RBGray = Radiobutton(self.master, \
				text='Gray', \
				selectcolor='blue')	
	self.RBGray.pack()	
	self.RBRGB = Radiobutton(self.master, \
				text='RGB', \
				selectcolor='red')
	self.RBRGB.pack()
	self._configureCB()
	return
	
    def _configureCB(self):
	self.RBGray.configure(variable=self.DisplayVar, \
				value=self.GRAY)
	self.RBRGB.configure(variable=self.DisplayVar, \
				value=self.RGB)
	return

