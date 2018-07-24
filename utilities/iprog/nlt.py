################################
#   NonLinearTransform Class   #
################################
from Tkinter import *
from PIL import ImageTk
import os
import cPickle

import dialogs
import iprog 

dumppath = os.path.join(os.curdir, 'dump')	# default directory for ".dmp" files
nltdump = os.path.join(dumppath, 'nlt.dmp')	# default processed filename

def nlt(master, matrix, dchoice, lut, dicScanParam):
    """
    Creates Non Linear Transform Interface
    """
    n = NonLinearTransform(master, matrix, dchoice, lut, dicScanParam)
    return n

class NonLinearTransform(dialogs.GridDialog):

    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	Class Constructor : NonLinearTransform
	"""
	self.current_matrix = matrix.copy()
	self.nlt_matrix = matrix.copy()
	self.sDisplayChoice=dchoice
	self.lut=lut
	self.dicScanParam = dicScanParam
	dialogs.GridDialog.__init__(self, master, 'NonLinear Transforms')
	return

    def body(self, master):
	"""
	Loads root widget with NonLinearTransform widgets
	"""
	self.NLTWindow = master
	self._vCreateNLTWidgets()
	return

    def apply(self):
	pass
	return
	
    def _vCreateNLTWidgets(self):
	"""
	Creates widgets for NLT Filter
	"""
	from PIL import Image
	if self.sDisplayChoice=='I':
		self.imNLT = Image.new("I", self.current_matrix.shape)
	if self.sDisplayChoice=='RGB':
		self.imNLT = Image.new("RGB", self.current_matrix.shape)
	self.ArrImNLT = ImageTk.PhotoImage(self.imNLT)
	self.demoNLT = Canvas(self.NLTWindow, width=self.nlt_matrix.shape[1], height=self.nlt_matrix.shape[0])
	self.demoNLT.grid(row=0,column=0,rowspan=3,columnspan=4,padx=5,pady=5)
	self.demoNLT.create_image(0,0,image=self.ArrImNLT,anchor=NW)
	self.nltdisplay(self.nlt_matrix)
	self.demoNLT.config(scrollregion=self.demoNLT.bbox(ALL))
	self.xscroll = Scrollbar(self.NLTWindow, orient=HORIZONTAL, command=self.demoNLT.xview)
	self.xscroll.grid(row=3,column=0, sticky=E+W, columnspan=4)
	self.yscroll = Scrollbar(self.NLTWindow, orient=VERTICAL, command=self.demoNLT.yview)
	self.yscroll.grid(row=0,column=4, sticky=N+S, rowspan=3)
	self.demoNLT["xscrollcommand"] = self.xscroll.set
	self.demoNLT["yscrollcommand"] = self.yscroll.set
	Label(self.NLTWindow, text='Gamma: ').grid(row=4,column=0, sticky=W)
	self.SliderG = Scale(self.NLTWindow, orient=HORIZONTAL, from_=0.1, to=5,resolution=0.01, showvalue=0, sliderlength=15, command = self.gammaCB)
	self.SliderG.grid(row=4,column=2, sticky=W)
	self.SliderG.set(1)
	Label(self.NLTWindow, text='Scaling Factor: ').grid(row=5,column=0, sticky=W )
	self.SliderS = Scale(self.NLTWindow, orient=HORIZONTAL, from_=1, to=10,showvalue=0, sliderlength=15, resolution=0.1, command = self.gammaCB)
	self.SliderS.grid(row=5,column=2, sticky=W)
	self.BtnCancel = Button(self.NLTWindow, command=self.cancelNLTCB, text='CANCEL')
	self.BtnCancel.grid(row=6,column=2,padx=5,pady=5, sticky=N+E+W+S, columnspan=2)
	self.BtnOk = Button(self.NLTWindow, command=self.okNLTCB, text='DONE',fg='red')
	self.BtnOk.grid(row=6,column=0, sticky=N+E+W+S,padx=5,pady=5, columnspan=2)
	return

    def nltdisplay(self, arr):
	"""
	Displays processed image
	"""
	arr = iprog.float2gray(arr)
	self.nlt_matrix = arr.copy()
	if self.sDisplayChoice=='I':
		self.imNLT.putdata(arr.flat)
	if self.sDisplayChoice=='RGB':
		colmatrix=map(lambda(x):self.lut[int(x)],arr.flat)
		self.imNLT.putdata(colmatrix)
	self.ArrImNLT.paste(self.imNLT)
	self.demoNLT.config(width=arr.shape[1],height=arr.shape[0] )
	return

    def gammaCB(self, event):
	"""
	--> gets gamma value from the user
	--> performs NLT on image matrix
	--> displays processed image
	"""
	scalefactor = float(self.SliderS.get()) 
	gamma = float(self.SliderG.get())
	result = coregammaNLT(self.current_matrix, gamma, scalefactor)
	self.nltdisplay(result)
	return

    def cancelNLTCB(self):
	"""
	Quits NLT Filter
	"""
	self.cancel()
	
    def okNLTCB(self):
	"""
	Saves processed image
	"""
	print 'Dumping File as ....', nltdump
	f = open(nltdump,'w')
	cPickle.dump(self.nlt_matrix,f)
	cPickle.dump(self.dicScanParam,f)
	f.close()
	self.ok()

def coregammaNLT(matrix,power, scalefactor):
    """
    Real Non linear Trasformation takes place here
    """
    correctedm = scalefactor * (matrix**power - 1)
    return correctedm 
