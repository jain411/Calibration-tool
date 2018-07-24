######################
#   Contrast Class   #
######################
from Tkinter import *
from PIL import ImageTk
import numpy
import os
import cPickle

import iprog 
import dialogs

dumppath = os.path.join(os.curdir, 'dump')			# defult directory for ".dmp" files
contrastdump	= os.path.join(dumppath, 'contrast.dmp')	# deault processed filename

def contrast(master, matrix, dchoice, lut, dicScanParam):
    """
    Creates Contrast Interface
    """
    c = Contrast(master, matrix, dchoice, lut, dicScanParam)
    return c

class Contrast(dialogs.GridDialog):


    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	Class Constructor : Contrast
	"""
	self.current_matrix = matrix.copy()
	self.contrast_matrix = matrix.copy()
	self.sDisplayChoice = dchoice
	self.lut = lut
	self.dicScanParam=dicScanParam
	dialogs.GridDialog.__init__(self, master, 'Contrast')
	return

    def body(self, master):
	"""
	Loads root widget with Contrast widgets
	"""
	self.ContrastWindow = master
	self._vCreateContrastWidgets()
	return
	
    def _vCreateContrastWidgets(self):
	"""
	Creates widgets for Contrast Filter
	"""
	from PIL import Image
	if self.sDisplayChoice=='I':
		self.imContrast = Image.new("I", self.current_matrix.shape)
	if self.sDisplayChoice=='RGB':
		self.imContrast = Image.new("RGB", self.current_matrix.shape)
	self.ArrImContrast = ImageTk.PhotoImage(self.imContrast)
	self.demoContrast = Canvas(self.ContrastWindow, width=100, height=100, scrollregion=(0,0,256,256))
	self.demoContrast.grid(row=0,column=0,rowspan=3,columnspan=4,padx=5,pady=5)
	self.demoContrast.create_image(0,0,image=self.ArrImContrast,anchor=NW)
	self.contrastdisplay(self.contrast_matrix)
	self.demoContrast.config(scrollregion=self.demoContrast.bbox(ALL))
	self.xscroll = Scrollbar(self.ContrastWindow, orient=HORIZONTAL, command=self.demoContrast.xview)
	self.xscroll.grid(row=3,column=0, sticky=E+W, columnspan=4)
	self.yscroll = Scrollbar(self.ContrastWindow, orient=VERTICAL, command=self.demoContrast.yview)
	self.yscroll.grid(row=0,column=4, sticky=N+S, rowspan=3)
	self.demoContrast["xscrollcommand"] = self.xscroll.set
	self.demoContrast["yscrollcommand"] = self.yscroll.set
	Label(self.ContrastWindow, text='Contrast: ').grid(row=5,column=0, sticky=W )
	self.SliderC = Scale(self.ContrastWindow, orient=HORIZONTAL, from_=0, to=100,showvalue=0, sliderlength=15, resolution=5, command = self.contrastCB)
	self.SliderC.grid(row=5,column=2, sticky=W)
	self.BtnCancel = Button(self.ContrastWindow, command=self.cancelContrastCB, text='CANCEL')
	self.BtnCancel.grid(row=6,column=2,padx=5,pady=5, sticky=N+E+W+S, columnspan=2)
	self.BtnOk = Button(self.ContrastWindow, command=self.okContrastCB, text='DONE',fg='red')
	self.BtnOk.grid(row=6,column=0, sticky=N+E+W+S,padx=5,pady=5, columnspan=2)
	self.max_val = self.contrast_matrix.max()
	self.min_val = self.contrast_matrix.min()
	return

    def apply(self):
	pass
	return	

    def contrastdisplay(self, arr):
	"""
	Displays processed image
	"""
	self.contrast_matrix = arr.copy()
	if self.sDisplayChoice=='I':
		self.imContrast.putdata(arr.flat)
	if self.sDisplayChoice=='RGB':
		colmatrix=map(lambda(x):self.lut[int(x)],arr.flat)
		self.imContrast.putdata(colmatrix)
	self.ArrImContrast.paste(self.imContrast)
	self.demoContrast.config(width=arr.shape[1],height=arr.shape[0] )
	return

    def contrastCB(self,event):
	"""
	--> gets contrast value from the user
	--> modify image contrast
	--> display processed image
	"""
	contrast = float(self.SliderC.get())
	result = coreContrast(contrast, self.current_matrix, self.min_val, self.max_val)
	self.contrastdisplay(result)
	return

    def cancelContrastCB(self):
	"""
	Quits Contrast Filter
	"""
	self.cancel()
	
    def okContrastCB(self):
	"""
	Saves processed image
	"""
	print 'Dumping File as ....', contrastdump
	f = open(contrastdump,'w')
	cPickle.dump(self.contrast_matrix,f)
	cPickle.dump(self.dicScanParam,f)
	f.close()
	self.ok()

def coreContrast(cval, matrix, min_val, max_val):
	"""
	Real modification of image contrast takes place here
	"""
	new_min = min_val + cval
	new_max = max_val - cval
	newm = numpy.clip(matrix, new_min, new_max )
	newm = iprog.float2gray(newm)
	return newm
