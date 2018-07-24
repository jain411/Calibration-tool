##############################
#   FourierTransform Class   #
##############################
from Tkinter import *
import tkFileDialog
import tkMessageBox
from PIL import ImageTk
import numpy
import scipy.ndimage as im
from scipy import fftpack
import cPickle
import pylab
#import numpy.fft as fft
import math
import os

import dialogs
import iprog

dumppath = os.path.join(os.curdir, 'dump')	# default directory for ".dmp" files
fourierdump = os.path.join(dumppath, 'fourier.dmp')	# default processed filename
debugdump = os.path.join(dumppath, 'debug.dmp')

def fourier(master, matrix, dchoice, lut, dicScanParam):
    """
    Creates Fourier Interface
    """
    f = FourierTransform(master, matrix, dchoice, lut, dicScanParam)
    return f

class FourierTransform(dialogs.GridDialog):

    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	Class Constructor : FourierTransform
	"""
	self.current_matrix = matrix.copy()
	self.fourier_matrix = matrix.copy()
	self.sDisplayChoice=dchoice
	self.lut = lut
	self.dicScanParam = dicScanParam
	self.strLineColor = 'yellow'
	self.arrZoomBuffer=[]
	self.zoomFactor = 1
	dialogs.GridDialog.__init__(self, master, 'Fourier Transform')
	return

    def body(self, master):
	"""
	Loads root widget with FourierTransform widgets
	"""
	self.FourierWindow = master
	self._vCreateFourierWidgets()
	return
 

    def _vCreateFourierWidgets(self):
	"""
	Creates widgets for Fourier Transform
	"""
	from PIL import Image
	self.fourierCanvas = Canvas(self.FourierWindow, width=self.fourier_matrix.shape[1], height=self.fourier_matrix.shape[0],bg='beige')
	self.fourierCanvas.grid(row=0, column=0, rowspan=4, columnspan=4, sticky=N+E+W+S)
	self.BtnPSD = Button(self.FourierWindow,command=self.psdCB, text='PSD')
	self.BtnPSD.grid(row=4,column=0, sticky=N+E+W+S, columnspan=1)
	self.BtnMask = Button(self.FourierWindow, command=self.showFilterMaskCB, text='Mask')
	self.BtnMask.grid(row=4,column=1,sticky=N+W+E+S,columnspan=1)
	self.BtnApply = Button(self.FourierWindow, command=self.applyCB, text='Apply',fg='red')
	self.BtnApply.grid(row=4,column=2,  sticky=N+W+E+S, columnspan=1)
	self.BtnSave = Button(self.FourierWindow, command=self.saveCB, text='Save')
	self.BtnSave.grid(row=4,column=3,sticky=N+W+E+S,columnspan=1)
	self.QlaunchMenu = Menu(self.FourierWindow,tearoff=0)
	self.QlaunchMenu.add_command(label='Zoom', command=self.zoomCB)
	self.QlaunchMenu.add_command(label='Original', command=self.originalCB)
	self.QlaunchMenu.add_command(label='Measure Length', command=self.bindCanvasLength)
	Label (self.FourierWindow, text = 'Threshold:').grid (row = 5, column=0, sticky=S)
	self.ScaleThreshold = Scale(self.FourierWindow, \
				width = 20, \
				sliderlength = 25, \
				command = self.showFilterMaskCB, \
				showvalue=1, \
				orient=HORIZONTAL, \
				)
	self.ScaleThreshold.grid(row = 5, column = 2, columnspan = 3, sticky = N+W+S)
	self.ScaleThreshold.configure (from_ = 0.0, to = 10, resolution = 0.1)
	self.ScaleThreshold.set(0)
	Label (self.FourierWindow, text = 'Gaussian:').grid (row = 6, column=0, sticky=S)
	self.ScaleSigma = Scale(self.FourierWindow, \
				width = 20, \
				sliderlength = 25, \
				command = self.showFilterMaskCB, \
				showvalue=1, \
				orient=HORIZONTAL, \
				)
	self.ScaleSigma.grid(row = 6, column = 2, columnspan = 3, sticky = N+W+S)
	self.ScaleSigma.configure (from_ = 0.0, to = 10, resolution = 0.1)
	self.ScaleSigma.set(0)
	
	self.BtnMask.config(state=DISABLED)
	self.BtnApply.config(state=DISABLED)
	self.BtnSave.config(state=DISABLED)
	
	self.BtnPSD.invoke()
	return


    def fourierdisplay(self, arr, size=[256,256]):
	"""
	Displays processed image
	"""
	arr = iprog.float2gray(arr)
	self.fourier_matrix = arr.copy()
	if self.sDisplayChoice=='I':
		from PIL import Image
		self.imFourier = Image.new("I", size)
		self.ArrImFourier= ImageTk.PhotoImage(self.imFourier)
		self.imFourier.putdata((arr.ravel()).tolist())
	if self.sDisplayChoice=='RGB':
		from PIL import Image
		self.imFourier = Image.new("RGB", size)
		self.ArrImFourier= ImageTk.PhotoImage(self.imFourier)
		colmatrix=map(lambda(x):self.lut[int(x)], arr.flat)
		self.imFourier.putdata(colmatrix)
	self.fourierCanvas.create_image(0,0,image=self.ArrImFourier,anchor=NW)
	self.ArrImFourier.paste(self.imFourier)
	self.fourierCanvas.config(width=arr.shape[1],height=arr.shape[0] )
	return


    def vConfigureCB(self):
	"""
	Binds popup menu with fourier canvas
	"""
	self.fourierCanvas.bind('<Button-3>',self.vQlaunchMenuCB)
	return

    def vQlaunchMenuCB(self, event):
	"""
	"""
	try:
		self.QlaunchMenu.tk_popup(event.x_root,event.y_root,0)
	finally:
		self.QlaunchMenu.grab_release()	
	return

		
    def coreFourier(self, matrix):
	"""
	Calculate 2-dimensional FFT of image
	"""
	imFFT = fftpack.fft2(matrix)
	return imFFT


    def psdCB(self):
	"""
	Calculate and display magnitude image
	"""
	imFFT = self.coreFourier(self.current_matrix)
	centeredImFFT = fftpack.fftshift(imFFT)
	psd2D = numpy.log10(numpy.abs(centeredImFFT) ** 2)
	self.sDisplayChoice = 'I'
	self.fourierdisplay(psd2D, psd2D.shape)
	self.BtnMask.config(state=ACTIVE)
	self.arrZoomBuffer.append(psd2D)
	self.vConfigureCB()
	return


    def showFilterMaskCB(self, *events):
	"""
	Calculate band pass/stop image
	"""
	self.zoomFactor = 1
	threshold = self.ScaleThreshold.get()
	sigma = self.ScaleSigma.get()
	#filterType = self.
	self.BtnApply.config(state = ACTIVE)
	if threshold > 0:
	  self.showFilterMask(threshold, sigma)
	return


    def showFilterMask(self, threshold, sigma):
	"""
	Calculate band pass/stop image
	"""
	imFFT = self.coreFourier(self.current_matrix)
	centeredImFFT = fftpack.fftshift(imFFT)
	psd2D = numpy.log10(numpy.abs(centeredImFFT) ** 2)
	if threshold > 0:
	    psdThreshold = psd2D.mean() + threshold * psd2D.std()
	    bin_mask = numpy.where(psd2D > psdThreshold, 1, 0)
	else:
	    bin_mask = 1
	grayMask = bin_mask * numpy.ones(self.current_matrix.shape, 'f')
	if sigma > 0:
	    grayMask = im.gaussian_filter(grayMask, sigma)
	self.sDisplayChoice = 'I'
	self.fourierdisplay(grayMask, grayMask.shape)
	self.filterMask = fftpack.ifftshift(grayMask)
	return

    def applyCB(self):
        imFFT = self.coreFourier(self.current_matrix)
        amplitude = numpy.sqrt(imFFT.real ** 2 + imFFT.imag ** 2)
        phase = numpy.arctan2(imFFT.imag, imFFT.real)
        filAmplitude = self.filterMask * amplitude
        filImFFT_Real = filAmplitude * numpy.cos(phase)
        filImFFT_Imag = filAmplitude * numpy.sin(phase)
        filImFFT = filImFFT_Real + 1j * filImFFT_Imag
        filImage = fftpack.ifft2(filImFFT)
        self.sDisplayChoice = 'RGB'
        self.fourierdisplay(filImage.real, filImage.shape)
        self.BtnSave.config(state = ACTIVE)
        return


    def zoomCB(self):
	"""
	Kickstarts Zoom utility
	"""
	self.vBindCanvas()
	return		


    def vBindCanvas(self):
	"""
	Performs mouse bindings for zoom area selection
	"""
	self.fourierCanvas.bind('<Button-1>', self.vBeginSelectionCB)
	self.fourierCanvas.bind('<B1-Motion>', self.vShowSelectionCB)
	self.fourierCanvas.bind('<ButtonRelease-1>', self.vEndSelectionCB)
	return

    def vUnBindCanvas(self):
	"""
	Removes mouse bindings for zoom area selection
	"""
	self.fourierCanvas.unbind('<Button-1>')
	self.fourierCanvas.unbind('<B1-Motion>')
	self.fourierCanvas.unbind('<ButtonRelease-1>')
	return

    def vBeginSelectionCB(self, event):
	"""
	Records the starting location
	"""
	self.arRegion = [[0,0],[0,0]]
	self.arRegion[0] = [event.x, event.y]
	return

    def vShowSelectionCB(self, event):
	"""
	Records position changes
	"""
	self.arRegion[1]=[event.x, event.y]
	self.vLimitSelection()
	self.vShowBox()
	if self.bCheckRange(event)==False:
		tkMessageBox.showerror('Error','Too Large Area Selected')
		self.fourierCanvas.delete(self.wDottedBox)
		return
	return

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

    def vShowBox(self):
	"""
	Displays boundary over the selected image area
	"""
	try:
		self.fourierCanvas.delete(self.wDottedBox)
	except:
		pass
	self.wDottedBox = self.fourierCanvas.create_rectangle(self.arRegion, \
	  outline = self.strLineColor)
	return

    def bCheckRange(self,event):
	"""
	Checks whether the selected area is greater than the image size
	"""
	if event.x <=0 or event.x >= self.current_matrix.shape[0]:
		return False
	if event.y <=0 or event.y >= self.current_matrix.shape[1]:
		return False
	return True

    def vEndSelectionCB(self,event):
	"""
	When mouse button is released it displays the selected image area	
	"""
	self.vShowSelectionCB(event)
	if (self.arRegion[1][0]-self.arRegion[0][0])==0:
		return
	if (self.arRegion[1][1]-self.arRegion[0][1])==0:
		return
	self.vZoomIn(self.arRegion)
	return	


    def bindCanvasLength(self):
	"""
	Performs mouse bindings for zoom area selection
	"""
	self.fourierCanvas.bind('<Button-1>', self.beginLineCB)
	self.fourierCanvas.bind('<B1-Motion>', self.showLineCB)
	self.fourierCanvas.bind('<ButtonRelease-1>', self.endLineCB)
	self.fourierCanvas.config(cursor = 'target')
	return

    def unBindCanvasLength(self):
	"""
	Removes mouse bindings for zoom area selection
	"""
	self.fourierCanvas.unbind('<Button-1>')
	self.fourierCanvas.unbind('<B1-Motion>')
	self.fourierCanvas.unbind('<ButtonRelease-1>')
	self.fourierCanvas.config(cursor = '')
	return


    def beginLineCB(self, event):
        """
        Gets Initial endpoint of the calibration line
        """
        self.startPoint = [0, 0]
        self.startPoint[0] = event.x
        self.startPoint[1] = event.y
        return

    def showLineCB(self, event):
        """
        Displays and Renews Calibration line with mouse movements
        """
        try :
                self.fourierCanvas.delete(self.CanLine)
        except:
                pass
        self.endPoint = [0, 0]
        self.endPoint[0] = event.x
        self.endPoint[1] = event.y
        self.CanLine = self.fourierCanvas.create_line(\
            self.startPoint[0], self.startPoint[1], self.endPoint[0], self.endPoint[1], \
            fill = self.strLineColor, arrow = BOTH, width = 2)
        dXdYDU = self.calculateLengthInfo(self.startPoint, self.endPoint)
        self.displayLengthInfo(dXdYDU)
        return

    def endLineCB(self, event):
        """
        Fetches location of final endpoint
        """
        if not self.CanLine:
                return
        self.unBindCanvasLength()
        return


    def calculateLengthInfo(self,startPoint, endPoint):
        """
        Calculates and Displays line segment info
        """
        if self.dicScanParam.has_key('XCalibration'):
            PIEZO_XY = self.dicScanParam['XCalibration']	# nm/V
        else:
            #print 'Using Default XY Calibration of 10nm/V'
            PIEZO_XY = 10.0	# nm/V
        fZfactor = self.zoomFactor
        if self.dicScanParam.has_key('HVAGainFactor'):
            hvaGain = self.dicScanParam['HVAGainFactor']
        else:
            #print 'Using Default HVA Gain of 10x'
            hvaGain = 10.0
        if self.dicScanParam.has_key('XLArea'):
            if self.dicScanParam['XLArea']:
                nStepSize = self.dicScanParam['StepSize'][0] * hvaGain
                strUnits = 'nm'
                fMulFactor = 1000.0
            else:
                nStepSize = self.dicScanParam['StepSize'][0]
                strUnits = 'A'
                fMulFactor = 100.0
        # to keep dX, dY and D in 'angs' PIEZO_XY is divided by 100
        dX = (abs(endPoint[0] - startPoint[0]) + 1) * \
                (nStepSize / fZfactor) * \
                (PIEZO_XY / fMulFactor) 
        dY = (abs(endPoint[1] - startPoint[1]) + 1) * \
                (nStepSize / fZfactor) * \
                (PIEZO_XY / fMulFactor) 
        D  = math.sqrt(dX**2 + dY**2)
        #print 'Line Length', D
        return [dX, dY, D, strUnits]


    def vDeleteLengthInfo(self):
        try:
            self.fourierCanvas.delete(self.ciTextLength)
        except:
            pass
        return

    def displayLengthInfo(self, dXdYDU):
        """
        Argument: array [dX, dY, D, strUnits]
        """
        self.vDeleteLengthInfo()
        text_color = self.strLineColor
        act_text_color = 'white'    # when mouse pointer is over it
        strUnits = dXdYDU[-1]
        self.ciTextLength = self.fourierCanvas.create_text(2,255, \
                            text='D: '+ str(round(dXdYDU[2], 2)) + strUnits, \
                            anchor=SW, \
                            font=(iprog.CANVAS_FONT, iprog.CANVAS_FONT_SIZE), \
                            fill=text_color , activefill=act_text_color )
        return


    def originalCB(self):
	"""
	Displays unzoomed image
	"""
	try:
		self.fourierdisplay(self.arrZoomBuffer[-1],self.arrZoomBuffer[-1].shape)
	except:
		pass
        self.zoomFactor = 1
        self.vDeleteLengthInfo()
	return


    def saveCB(self):
	"""
	Saves processed image
	"""
	print 'Saving Processed File as ....', fourierdump
	f = open(fourierdump,'w')
	cPickle.dump(self.fourier_matrix,f)
	cPickle.dump(self.dicScanParam,f)
	f.close()
	self.arrZoomBuffer.append(self.fourier_matrix)
	return

    def savePSD_CB(self):
	"""
	Save canvas image as ".ps"
	"""
	
	fname = dialogs.SaveImageDialog('.ps', 'Do you want to save PSD image?', \
					parent = self.FourierWindow)
	if fname:
		self.fourierCanvas.postscript(file = fname)
	return

    def vZoomIn(self, Region):
	"""
	Zooms the selected area to [256,256] pixels
	"""
	ylen = Region[1][0]-Region[0][0]
	xlen = Region[1][1]-Region[0][1]
	FrameBuffer = numpy.zeros([abs(xlen)+1,abs(ylen)+1],'f')
	k = 0
	w = 0
	if xlen<=0:
		for i in range(Region[1][1],Region[0][1]+1):
			for j in range(Region[1][0],Region[0][0]+1):
				FrameBuffer[k][w]=self.fourier_matrix[i][j]
				w += 1
			w = 0
			k += 1
	else:
		for i in range(Region[0][1],Region[1][1]+1):
			for j in range(Region[0][0],Region[1][0]+1):
				FrameBuffer[k][w] = self.fourier_matrix[i][j]
				w+=1
			w = 0
			k += 1
	zFactor = float(self.current_matrix.shape[0])/FrameBuffer.shape[0]
	self.zoomFactor *= zFactor
	fZoomedImage = im.zoom(FrameBuffer,zFactor)
	self.fourierdisplay(fZoomedImage, fZoomedImage.shape)
	self.vUnBindCanvas()
	return	

