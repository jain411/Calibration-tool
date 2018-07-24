####################
#   HistEq Class   #
####################
from Tkinter import *
from PIL import Image
from PIL import ImageTk
import cPickle
import pylab
import numpy
import scipy.ndimage as im
import os

import dialogs

dumppath = os.path.join(os.curdir, 'dump')	# default directory for ".dmp" files
histeqdump = os.path.join(dumppath, 'histeq.dmp')	# default processed filename

def histeq(master, matrix, dchoice, lut, dicScanParam):
    """
    Creates Histogram Equalization Interface
    """
    h = HistEq(master, matrix, dchoice, lut, dicScanParam)
    return h

class HistEq(dialogs.GridDialog):

    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	Class Constructor : HistEq
	"""
	self.current_matrix = matrix.copy()
	self.histeq_matrix = matrix.copy()
	self.sDisplayChoice=dchoice
	self.lut=lut
	self.dicScanParam=dicScanParam
	dialogs.GridDialog.__init__(self, master, 'Histogram Equalization')
	return
 
    def body(self, master):
	"""
	Loads root widget with HistEq widgets
	"""
	self.HisteqWindow = master
	self._vCreateHisteqWidgets()
	return
	
    def _vCreateHisteqWidgets(self):		
	"""
	Creates widgets for Histogram Equalization Filter
	"""
	from PIL import Image			
	if self.sDisplayChoice=='I':
		self.imHisteq = Image.new("I", self.current_matrix.shape)
	if self.sDisplayChoice=='RGB':
		self.imHisteq = Image.new("RGB", self.current_matrix.shape)
	self.ArrImHisteq = ImageTk.PhotoImage(self.imHisteq)
	self.demoHisteq = Canvas(self.HisteqWindow, width=100, height=100, scrollregion=(0,0,256,256))
	self.demoHisteq.grid(row=0,column=0,rowspan=3,columnspan=4,padx=5,pady=5)
	self.demoHisteq.create_image(0,0,image=self.ArrImHisteq,anchor=NW)
	self.histeqdisplay(self.histeq_matrix)
	self.demoHisteq.config(scrollregion=self.demoHisteq.bbox(ALL))
	self.xscroll = Scrollbar(self.HisteqWindow, orient=HORIZONTAL, command=self.demoHisteq.xview)
	self.xscroll.grid(row=3,column=0, sticky=E+W, columnspan=4)
	self.yscroll = Scrollbar(self.HisteqWindow, orient=VERTICAL, command=self.demoHisteq.yview)
	self.yscroll.grid(row=0,column=4, sticky=N+S, rowspan=3)
	self.demoHisteq["xscrollcommand"] = self.xscroll.set
	self.demoHisteq["yscrollcommand"] = self.yscroll.set
	self.BtnApply = Button(self.HisteqWindow, command=self.applyHisteqCB, text='APPLY')
	self.BtnApply.grid(row=6,column=0,padx=5,pady=5, sticky=N+E+W+S)
	self.BtnCancel = Button(self.HisteqWindow, command=self.cancelHisteqCB, text='CANCEL')
	self.BtnCancel.grid(row=6,column=1,padx=5,pady=5, sticky=N+E+W+S)
	self.BtnShowHist = Button(self.HisteqWindow, command=self.vShowHistCB, text='HIST',fg='green')
	self.BtnShowHist.grid(row=6,column=2, sticky=N+E+W+S,padx=5,pady=5)
	self.BtnOk = Button(self.HisteqWindow, command=self.okHisteqCB, text='DONE',fg='red')
	self.BtnOk.grid(row=6,column=3, sticky=N+E+W+S,padx=5,pady=5)
	vCalculateHistogram(self.current_matrix)
	return

    def histeqdisplay(self, arr):
	"""
	Displays processed image
	"""
	self.histeq_matrix = arr.copy()
	if self.sDisplayChoice=='I':
		self.imHisteq.putdata(arr.flat)
	if self.sDisplayChoice=='RGB':
		colmatrix=map(lambda(x):self.lut[int(x)],arr.flat)
		self.imHisteq.putdata(colmatrix)
	self.ArrImHisteq.paste(self.imHisteq)
	self.demoHisteq.config(width=arr.shape[1],height=arr.shape[0] )
	return


    def vShowHistCB(self):
	"""
	Displays Image histogram
	"""
	self.vShowHist(self.histeq_matrix)
	return

    def vShowHist(self, arr):
	"""
	Generates and displays image histogram
	"""
	hist = vCalculateHistogram(arr)
	pylab.figure()
	x = numpy.arange(256)
	pylab.bar(x, hist, width=0.5, color='b')
	pylab.show()
	return


    def applyHisteqCB(self):
	"""
	Performs Histogram Equalization on Image data
	"""
	self.apply()
	return

    def apply(self):
	"""
	Performs Histogram Equalization on Image data
	Displays processed image	
	"""
	print 'Beauty of Monotonic Transform ...'
	histeqImg = coreHisteq(self.current_matrix)
	self.histeqdisplay(histeqImg)
	return
	
    def cancelHisteqCB(self):
	"""
	Quits Brightness Filter
	"""
	pylab.close('all')
	self.cancel()
	
    def okHisteqCB(self):
	"""
	Saves processed image
	"""
	print 'Dumping File as ....', histeqdump
	f = open(histeqdump,'w')
	cPickle.dump(self.histeq_matrix,f)
	cPickle.dump(self.dicScanParam,f)
	f.close()
	pylab.close('all')
	self.ok()


def vCalculateHistogram(arr):
    """
    Function : vCalculateHistogram
	Real Histogram generation takes place here

    Arguments :
	arr : int gray Image matrix

    Returns :
	hist : int image histogram array
    """
    hist = im.histogram(arr, 0, 255, 256)
    return hist

def coreHisteq(arr):
    """
    Function : coreHisteq
	Histogram Equaluiztion

    Arguments :
	matrix : int gray Image matrix

    Returns :
	histeqImg : float Histogram Equalized Image matrix
    """
    #hist = vCalculateHistogram(arr.ravel)
    #narr = numpy.asarray(arr)
    hist, bins = numpy.histogram(arr, range(256))
    cdf = hist.cumsum()
    cdf = 255 * cdf / cdf[-1]

    histeqImg = numpy.interp(arr, bins[:-1], cdf)
    #cum_hist = numpy.zeros(256, numpy.uint8)
    #for i in range(256):
    #	cum_hist[i] = hist[:i+1].sum() 
    #norm_hist = 255./arr.size * cum_hist
    #print 'Array Shapes:', arr.shape, norm_hist.shape
    #filt_data = numpy.take(arr.flat, norm_hist)
    #histeqImg = filt_data.reshape(arr.shape)
    return histeqImg.reshape(arr.shape)

