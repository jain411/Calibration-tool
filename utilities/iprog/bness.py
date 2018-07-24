###################
#   Bness Class   #
###################
from Tkinter import *
from PIL import ImageTk
import numpy
import cPickle
import os

import dialogs

dumppath = os.path.join(os.curdir, 'dump')	# default directory for ".dmp" files
bnessdump = os.path.join(dumppath, 'bness.dmp')	# default processed filename

def bness(master, matrix, dchoice, lut, dicScanParam):
    """
    Creates Brightness Interface
    """
    b = Bness(master, matrix, dchoice, lut, dicScanParam)
    return b

class Bness(dialogs.GridDialog):

    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	Class Constructor : Bness
	"""
	self.current_matrix = matrix.copy()
	self.bness_matrix = matrix.copy()
	self.sDisplayChoice=dchoice
	self.lut=lut
	self.dicScanParam =dicScanParam
	dialogs.GridDialog.__init__(self, master, 'Brightness')
	return

    def body(self, master):
	"""
	Loads root widget with Bness widgets
	"""
	self.BnessWindow = master
	self._vCreateBnessWidgets()
	return
	
    def _vCreateBnessWidgets(self):
	"""
	Creates widgets for Brightness Filter
	"""
	from PIL import Image
	if self.sDisplayChoice=='I':
		self.imBness = Image.new("I", self.current_matrix.shape)
	if self.sDisplayChoice=='RGB':
		self.imBness = Image.new("RGB", self.current_matrix.shape)
	self.ArrImBness = ImageTk.PhotoImage(self.imBness)
	self.demoBness = Canvas(self.BnessWindow, width=100, height=100, scrollregion=(0,0,256,256))
	self.demoBness.grid(row=0,column=0,rowspan=3,columnspan=4,padx=5,pady=5)
	self.demoBness.create_image(0,0,image=self.ArrImBness,anchor=NW)
	self.max_val = self.bness_matrix.max()
	self.min_val = self.bness_matrix.min()
	self.bnessdisplay(self.bness_matrix)
	self.demoBness.config(scrollregion=self.demoBness.bbox(ALL))
	self.xscroll = Scrollbar(self.BnessWindow, orient=HORIZONTAL, command=self.demoBness.xview)
	self.xscroll.grid(row=3,column=0, sticky=E+W, columnspan=4)
	self.yscroll = Scrollbar(self.BnessWindow, orient=VERTICAL, command=self.demoBness.yview)
	self.yscroll.grid(row=0,column=4, sticky=N+S, rowspan=3)
	self.demoBness["xscrollcommand"] = self.xscroll.set
	self.demoBness["yscrollcommand"] = self.yscroll.set
	Label(self.BnessWindow, text='Brightness: ').grid(row=4,column=0, sticky=W)
	self.SliderB = Scale(self.BnessWindow, orient=HORIZONTAL, from_=1, to=50,resolution=1, showvalue=0, sliderlength=15, command = self.brightCB)
	self.SliderB.grid(row=4,column=2, sticky=W)
	self.BtnCancel = Button(self.BnessWindow, command=self.cancelBnessCB, text='CANCEL')
	self.BtnCancel.grid(row=6,column=2,padx=5,pady=5, sticky=N+E+W+S, columnspan=2)
	self.BtnOk = Button(self.BnessWindow, command=self.okBnessCB, text='DONE',fg='red')
	self.BtnOk.grid(row=6,column=0, sticky=N+E+W+S,padx=5,pady=5, columnspan=2)
	return

    def bnessdisplay(self, arr):
	"""
	Displays processed image
	"""
	arr=numpy.clip(arr,self.min_val,self.max_val)
	self.bness_matrix = arr.copy()
	if self.sDisplayChoice=='I':
		self.imBness.putdata(arr.flat)
	if self.sDisplayChoice=='RGB':
		colmatrix=map(lambda(x):self.lut[int(x)],arr.flat)
		self.imBness.putdata(colmatrix)
	self.ArrImBness.paste(self.imBness)
	self.demoBness.config(width=arr.shape[1],height=arr.shape[0] )
	return

    def apply(self):
	pass
	return

    def brightCB(self, event):
	"""
	--> get brightness value from the user
	--> modify image brightness
	--> display processed image
	"""
	brightness = float(self.SliderB.get())
	result = coreBrightness(brightness, self.current_matrix)   
	self.bnessdisplay(result)
	return

    def cancelBnessCB(self):
	"""
	Quits Brightness Filter
	"""
	self.cancel()
	
    def okBnessCB(self):
	"""
	Saves processed image
	"""
	print 'Dumping File as ....', bnessdump
	f = open(bnessdump,'w')
	cPickle.dump(self.bness_matrix,f)
	cPickle.dump(self.dicScanParam,f)
	f.close()
	self.ok()
	return

def coreBrightness(bval, matrix):
	"""
	Real modification of image brightness takes place here
	"""
	newm = matrix + bval		
	return newm

