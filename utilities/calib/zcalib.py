from Tkinter import *
import tkMessageBox, tkSimpleDialog
import tkFileDialog
from PIL import Image
from PIL import ImageTk
import pylab
import numpy
import scipy.ndimage as im
import math
import time

import iprog
import dialogs
import import_
import scanner 	# for Z-Calibration data

import app_zcalib

canvas_font = ('Times', 24, 'bold')

SIGMA	= 2.5

FILETYPES = {	'npic':('SiM Files','*.npic'),\
		#'dat':('Old Stm Files','*.dat'), \
		}					# Stm File types 

# from scanner.py
ZMODE		= 4
TCMODE		= 5

def zcalib(f=None, oMenuBar=None, oLUT=None):
    """
    Returns object of class ZCalib
    """
    if not f:
	root = Tk()
	oAppZCalib = app_zcalib.app_zcalib()
	oAppZCalib.createZCwindow(root)
	oZCalib = ZCalib(oAppZCalib, oMenuBar, oLUT)
	root.title('Z-Calibration')
	root.mainloop()
	return
    else:
	oAppZCalib = app_zcalib.app_zcalib()
	oAppZCalib.createZCwindow(f)
	oZCalib = ZCalib(oAppZCalib, oMenuBar, oLUT)
    	return oZCalib

class ZCalib:
    """
    """
    def __init__(self, oAppZCalib, oMenuBar, oLUT):
	self.oAppZCalib = oAppZCalib
	self.oMenuBar = oMenuBar
	self.oLUT = oLUT
	self.bImagePresentVar = BooleanVar()
	self.bImagePresentVar.set(False)

	self.ZCALIB = scanner.fGetPiezoZCalibration()	# nm/V

	self.__configureCB()
	self.colorcode = [	'blue', 'red', '#A9079C', 'black', 'cyan', \
				'#E11D13', 'magenta','green', 'yellow', '#FF4500']
	self._vKeyBindings()
	return

    def __configureCB(self):
	"""
	"""
	self.oAppZCalib.BtnAddROI.configure(command=self.vBtnAddROICB)
	self.oAppZCalib.BtnRemoveROI.configure(command=self.vBtnRemoveROICB)
	self.oAppZCalib.BtnShowHist.configure(command=self.vBtnShowHistCB)
	self.oAppZCalib.filemenu.add_command(label='Open', command=self.vOpenCB)  
	self.oAppZCalib.filemenu.add_command(label='Quit',command=self.vCloseAppZCalibCB)
	self.oAppZCalib.xaxissettingsmenu.add_command(label='Angs', \
						command=self.vSetAngsCB)
	self.oAppZCalib.xaxissettingsmenu.add_command(label='mV', \
						command=self.vSetmVCB)
	self.oAppZCalib.settingsmenu.add_command(label='Load Z-Calibration', \
						command=self.vSetZCalibCB)  
	self.oAppZCalib.zcGroup.protocol('WM_DELETE_WINDOW',self.vCloseAppZCalibCB)
	self.strPlotVar = StringVar()
	self.strPlotVar.set('Angs')
	return

    def	_vKeyBindings(self):
	self.oAppZCalib.zcGroup.bind('<Control-o>', self.vOpenCB)
	return

    def vBtnAddROICB(self):
	if not self.bImagePresentVar.get():
	    tkMessageBox.showerror('No Image..','To select ROI, please open an Image..!', 
					parent = self.oAppZCalib.zcGroup)	
	    return		
	self.vActivateCanvasSelection()
	return

    def vSetAngsCB(self):
	self.strPlotVar.set('Angs')
	return

    def vSetmVCB(self):
	self.strPlotVar.set('mV')
	return

    def vSetZCalibCB(self):
	"""
	Asks to enter Z-Calibration for the scanner piezo.
	"""
	zc = tkSimpleDialog.askfloat('Z-Calibration', \
					'Z-Calibration of Piezo \n (in nm/V):', \
					initialvalue = self.ZCALIB, \
					minvalue = 0.1, \
					parent = self.oAppZCalib.zcGroup)
	if not zc:
	    return
	else:
	    self.ZCALIB = zc
	    scanner.vSavePiezoZCalibration(self.ZCALIB)
	return 


    def vBtnRemoveROICB(self):
	sel_indices = self.oAppZCalib.ListROI.curselection()
	sel_indices = map(lambda(x):int(x), sel_indices)   # converting string values to int
	sel_indices.reverse()
	self.oAppZCalib.ListROI.delete(ANCHOR)
	for index in sel_indices:
	    self.arROI.remove(self.arROI[index])
	    self.oAppZCalib.ArrCanvas.delete(self.arROIBox[index])
	    self.oAppZCalib.ArrCanvas.delete(self.arROICount[index])
	    self.arROIBox.remove(self.arROIBox[index])
	    self.arROICount.remove(self.arROICount[index])
	    self.vUpdateListbox()
	    self.vUpdateROI()
	return

    def vBtnShowHistCB(self):
	#print 'Regions Selected', self.arROI
	if self.arROI != []:
	    self.vCalculateHist()
	    self.vDisplayHist()
	return

    def vActivateCanvasSelection(self):
	"""
	Binds mouse with ZCalib Canvas
	"""
	self.oAppZCalib.ArrCanvas.bind('<Button-1>', self.vBeginSelectionCB)
	self.oAppZCalib.ArrCanvas.bind('<B1-Motion>', self.vShowSelectionCB)
	self.oAppZCalib.ArrCanvas.bind('<ButtonRelease-1>', self.vEndSelectionCB)
	self.oAppZCalib.ArrCanvas.configure(cursor='target')
	return

    def vDeactivateCanvasSelection(self):
	"""
	Removes mouse bindings with Imaging Canvas
	"""
	self.oAppZCalib.ArrCanvas.unbind('<Button-1>')
	self.oAppZCalib.ArrCanvas.unbind('<B1-Motion>')
	self.oAppZCalib.ArrCanvas.unbind('<ButtonRelease-1>')
	self.oAppZCalib.ArrCanvas.configure(cursor='')
	return
	
    def vBeginSelectionCB(self,event):
	"""
	Records the starting location
	"""
	self.arRegion = [[0,0], [0,0]]
	self.arRegion[0] = [event.x, event.y]
	#print 'Starting point',event.x,event.y
	return

    def vShowSelectionCB(self,event):
	"""
	Records position changes
	Redraws the selection area as the mouse is moved over the image 
	"""
	self.arRegion[1]=[event.x,event.y]
	self.vLimitSelection()
	if self.bCheckRange(event)==False:
	    return
	self.vShowBox()
	return

    def vEndSelectionCB(self,event):
	"""
	When mouse button is released it displays the selected image area	
	"""
	#print 'End Point', event.x,event.y
	self.vShowSelectionCB(event)	
	if (self.arRegion[1][0] - self.arRegion[0][0])==0:
	    return
	if (self.arRegion[1][1] - self.arRegion[0][1])==0:
	    return
	self.vDeactivateCanvasSelection()
	self.arROI.append(self.arRegion)
	self.vShowBox(self.arRegion)
	self.vUpdateListbox()
	return

    def bCheckRange(self,event):
	"""
	Checks whether the selected area is greater than the image size
	"""
	if event.x <=0 or event.x > self.afScanData.shape[0]-1:
	    return False
	if event.y <=0 or event.y > self.afScanData.shape[1]-1:
	    return False 
	return True

    def vLimitSelection(self):
	"""
	Traces mouse movement to create squared selection area
	"""
	l = (self.arRegion[1][0] - self.arRegion[0][0])
	b = (self.arRegion[1][1] - self.arRegion[0][1])
	if l>b:
	    side = b
	else:
	    side = l
	self.arRegion[1] = [self.arRegion[0][0]+side, self.arRegion[0][1]+side] 
	return

    def vShowBox(self, arRegion=None):
	"""
	Displays boundary over the selected image area
	"""
	try:
	    self.oAppZCalib.ArrCanvas.delete(self.wScanDottedBox)
	except:
	    pass
	if arRegion:
	    ciROIBox = self.oAppZCalib.ArrCanvas.create_rectangle(arRegion, \
						width=2, \
						outline=self.colorcode[len(self.arROI)-1])
	    self.arROIBox.append(ciROIBox)
	    ciROICount = self.oAppZCalib.ArrCanvas.create_text(arRegion[0], \
						anchor=NW, \
						text = str(len(self.arROI)), \
						font = canvas_font, \
						fill=self.colorcode[len(self.arROI)-1])
	    self.arROICount.append(ciROICount)
	    return
	self.wScanDottedBox = self.oAppZCalib.ArrCanvas.create_rectangle(self.arRegion)
	return

    def vUpdateListbox(self):
	"""
	"""
	self.oAppZCalib.ListROI.delete(0,END)
	nROI = 0
	for region in self.arROI:
	    self.oAppZCalib.ListROI.insert(END, 'Region ' + str(nROI+1))
	    nROI += 1
	return

    def vUpdateROI(self):
	"""
	"""
	nROI = 0
	for region in self.arROIBox:
	    self.oAppZCalib.ArrCanvas.itemconfig(region, outline=self.colorcode[nROI])
	    nROI += 1
	nROI = 0
	for count in self.arROICount:
	    self.oAppZCalib.ArrCanvas.itemconfig(count, \
					text = str(nROI+1), \
					fill = self.colorcode[nROI])
	    nROI += 1
	return

    def vCalculateHist(self):
	self.arHist = []
	afGrayScanData = iprog.float2gray(self.afScanData)
	for arROI in self.arROI:
	    arData = afGrayScanData[arROI[0][1]:arROI[1][1], \
					arROI[0][0]:arROI[1][0]]
	    hist = im.histogram(arData,0,255,256) #min_val, max_val, no_of_bins
	    # Debug Code ... can be removed l8r
	    #avg_height = numpy.where(hist>=hist.max()-hist.max()/10)
	    #print avg_height
	    #val = avg_height[0][0]
	    #print val
	    #shape = arData.shape
	    #arDatabu = arData.copy()
	    #arData = map(lambda(x):int(x), arData.flat)
	    #arData = numpy.asarray(arData).resize(shape)
	    #loc = numpy.asarray(numpy.where(arData==val))
	    #print arData[loc[0][5]][loc[0]]
	    #print arDatabu[loc[0][5]][loc[0]]
	    #loc[0] += arROI[0][0]
	    #loc[1] += arROI[0][1]
	    #print 'Updated loc', loc[0], loc[1]
	    #print loc
	    #self.afScanData.take(loc)
	    self.arHist.append(hist)
	return

    def vDisplayHist(self):
	"""
	SHow the height profile in histogram
	"""
        pylab.ion()     # interactive display
	pylab.figure()
	self.ZCALIB = scanner.fGetPiezoZCalibration()	# nm/V
	# Converting into voltages (mV)
	x = (numpy.arange(256)/256.) * \
	    (self.afScanData.max() - self.afScanData.min()) + \
	    self.afScanData.min()
	if self.strPlotVar.get() == 'Angs':
	    x *= self.ZCALIB/100.0	# since ZCALIB is in nm/V and x is mV
	nROI = 0
	min_width=x[1] - x[0]
	#min_width=1
	for hist in self.arHist:
	    #x = numpy.arange(256)
	    pylab.bar(x, hist, width=(nROI+1)/3.*(min_width), color=self.colorcode[nROI])
	    pylab.grid(True)
	    nROI += 1
	if self.strPlotVar.get() == 'Angs':
	    pylab.xlabel('Z-Distance (in angs)')
	if self.strPlotVar.get() == 'mV':
	    pylab.xlabel('Feedback Signal (in mV)')
	pylab.ylabel('No. of Pixels')
	pylab.show()
 	return

    def vOpenCB(self, event=None):
	"""
	Opens and Displays a User Select File	
	"""
	filename=self.fOpenFile()
	if filename is None:
		return
	[fScanImageMatrix, fRetImageMatrix, dicScanParam, sFileType]=import_.aafReadImageFile(filename)
	nImageMatrix=iprog.float2gray(fScanImageMatrix)
	self.vAcquireImageData(fScanImageMatrix, dicScanParam)
	self.vShow(nImageMatrix)
	self.arROI = []		# To store regions selected 
	self.arROIBox = []		# To store Box 'handle' for selected region
	self.arROICount = []		# To store Text 'handle' for selected region
	self.oAppZCalib.ListROI.delete(0,END)	# clean up list
	return

    def vAcquireImageData(self, fScanImageMatrix, dicScanParam):
	if dicScanParam['DigitizationMode'] == ZMODE:
		fHVAGain = scanner.fGetHVAGain()
	    	fScanImageMatrix *= fHVAGain  
	self.afScanData = fScanImageMatrix 
	return

    def fOpenFile(self):
	"""
	Pops up a Filemenu to open ".pic" / ".dat" to be displayed
	"""
	ftype=FILETYPES.values()
	filepath =dialogs.strPathTracker()
	file = tkFileDialog.askopenfilename(title = 'Load File', \
						defaultextension = "pic", \
						filetypes = ftype, \
						initialdir = filepath, \
						parent = self.oAppZCalib.zcGroup)
	if not file:
		tkMessageBox.showerror('File not selected', 'Please open an image file first !!', \
					parent = self.oAppZCalib.zcGroup)
		return
	dialogs.strPathTracker(file)
	return file

    def vShow(self,nImageMatrix):
	"""
	Displays Image on the Image Canvas
	"""
	if nImageMatrix is None:
		print 'No Input Matrix'
		return None
	self.nImageMatrix=nImageMatrix
	nImageMatrix = iprog.min_maxfilter(nImageMatrix.copy(), SIGMA)
	self.vRenewCanvas(nImageMatrix)
	return

    def vRenewCanvas(self, nImageMatrix):
	"""
	Refreshes Image Canvas with the new Image data
	"""
	self.vCreateImage(nImageMatrix)
	try:
	    self.oAppZCalib.ArrCanvas.delete(ALL)
	except:
	    pass
	self.CanvasImage = self.oAppZCalib.ArrCanvas.create_image(0,0,image=self.ArrIm,anchor=NW)
	self.ArrIm.paste(self.im)
	self.oAppZCalib.ArrCanvas.config(width=nImageMatrix.shape[1], \
					height=nImageMatrix.shape[0] )
	self.oAppZCalib.zcGroup.update()
	return
	
    def vCreateImage(self, nImageMatrix):
	"""
	Configures Canvas for RGB Image Diaplay		
	"""
	[row, col] = nImageMatrix.shape
	nImageMatrix=iprog.float2gray(nImageMatrix)
	from PIL import Image
	self.im = Image.new("RGB",[row*1,col*1])
	self.ArrIm = ImageTk.PhotoImage(self.im)
	colmatrix=map(lambda(x):self.oLUT[int(x)],nImageMatrix.flat)
	self.im.putdata(colmatrix)
	self.bImagePresentVar.set(True)
	return

    def vCloseAppZCalibCB(self):
	if self.oMenuBar:
	    self.oMenuBar.ZC_Instance = 0
	pylab.close('all')
	self.oAppZCalib.zcGroup.destroy()

if __name__ == '__main__':
    zcalib()
