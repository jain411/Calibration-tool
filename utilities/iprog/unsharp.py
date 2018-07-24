##############################
#   UnsharpFiltering Class   #
##############################
from Tkinter import *
from PIL import ImageTk
import os
import cPickle

import dialogs
import gauss
import iprog 

dumppath = os.path.join(os.curdir, 'dump')	# default directory for ".dmp" files
usdump = os.path.join(dumppath, 'usdmp.dmp')	# default processed filename
 
def unsharp(master, matrix, dchoice, lut, dicScanParam):
    """
    Creates Unsharp Filter Interface
    """
    u = UnsharpFiltering(master, matrix, dchoice, lut, dicScanParam)
    return u

class UnsharpFiltering(dialogs.GridDialog):

    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	Class Constructor : UnsharpFiltering
	"""
	self.current_matrix = matrix.copy()
	self.unsharp_matrix = matrix.copy()
	self.sDisplayChoice=dchoice
	self.lut=lut
	self.dicScanParam = dicScanParam
	dialogs.GridDialog.__init__(self, master, 'Unsharp Filter')
	return

    def body(self, master):		
	"""
	Loads root widget with UnsharpFiltering widgets
	"""
	self.UnsharpWindow = master
	self._vCreateUnsharpWidgets()
	return

    def _vCreateUnsharpWidgets(self):
	"""
	Creates widgets for UnsharpFiltering
	"""
	from PIL import Image
	if self.sDisplayChoice=='I':
		self.imUnsharp = Image.new("I", self.current_matrix.shape)
	if self.sDisplayChoice=='RGB':
		self.imUnsharp = Image.new("RGB", self.current_matrix.shape)
	self.ArrImUnsharp = ImageTk.PhotoImage(self.imUnsharp)
	self.demoUnsharp = Canvas(self.UnsharpWindow, width=100, height=100, scrollregion=(0,0,256,256))
	self.demoUnsharp.grid(row=0,column=0,rowspan=3,columnspan=4,padx=5,pady=5)
	self.demoUnsharp.create_image(0,0,image=self.ArrImUnsharp,anchor=NW)
	self.unsharpdisplay(self.unsharp_matrix)
	self.demoUnsharp.config(scrollregion=self.demoUnsharp.bbox(ALL))
	self.xscroll = Scrollbar(self.UnsharpWindow, orient=HORIZONTAL, command=self.demoUnsharp.xview)
	self.xscroll.grid(row=3,column=0, sticky=E+W, columnspan=4)
	self.yscroll = Scrollbar(self.UnsharpWindow, orient=VERTICAL, command=self.demoUnsharp.yview)
	self.yscroll.grid(row=0,column=4, sticky=N+S, rowspan=3)
	self.demoUnsharp["xscrollcommand"] = self.xscroll.set
	self.demoUnsharp["yscrollcommand"] = self.yscroll.set
	self.pradiusgrp = LabelFrame(self.UnsharpWindow, text='Pseudo-Radius', padx=5, pady=5)
        self.pradiusgrp.grid(row=4,column=0,sticky=N+E+W+S,padx=10, pady=10, columnspan=3)
        self.pradius = Spinbox(self.pradiusgrp,from_=0.5, to=10, increment=0.5)
        self.pradius.grid(row=0, column=0, sticky=N+E+W+S,padx=5,pady=5)
        self.pradius.delete(0,END)
        self.pradius.insert(0,str(2.5))
	self.amountgrp = LabelFrame(self.UnsharpWindow, text='Amount', padx=5, pady=5)
        self.amountgrp.grid(row=5,column=0,sticky=N+E+W+S,padx=10, pady=10, columnspan=3)
        self.amount = Spinbox(self.amountgrp,from_=0.5, to=10, increment=0.5)
        self.amount.grid(row=0, column=0, sticky=N+E+W+S,padx=5,pady=5)
        self.amount.delete(0,END)
        self.amount.insert(0,str(2.5))
	self.BtnApply = Button(self.UnsharpWindow, command=self.applyUnsharpCB, text='APPLY')
	self.BtnApply.grid(row=6,column=0,padx=5,pady=5, sticky=N+E+W+S)
	self.BtnCancel = Button(self.UnsharpWindow, command=self.cancelUnsharpCB, text='CANCEL')
	self.BtnCancel.grid(row=6,column=1,padx=5,pady=5, sticky=N+E+W+S)
	self.BtnOk = Button(self.UnsharpWindow, command=self.okUnsharpCB, text='DONE',fg='red')
	self.BtnOk.grid(row=6,column=2,columnspan=2, sticky=N+E+W+S,padx=5,pady=5)
	return

    def unsharpdisplay(self, arr):
	"""
	Displays processed image
	"""
	arr=iprog.float2gray(arr)
	self.unsharp_matrix = arr.copy()
	if self.sDisplayChoice=='I':
		self.imUnsharp.putdata(arr.flat)
	if self.sDisplayChoice=='RGB':
		colmatrix=map(lambda(x):self.lut[int(x)],arr.flat)
		self.imUnsharp.putdata(colmatrix)
	self.ArrImUnsharp.paste(self.imUnsharp)
	self.demoUnsharp.config(width=arr.shape[1],height=arr.shape[0] )
	return

    def applyUnsharpCB(self):
	"""
	Performs Unsharp Filtering
	"""
	self.apply()
	return

    def apply(self):	
	"""
	Fetches paradius & amout value from the user
	Performs Unsharp Filtering on image matrix
	Displays processed image	
	"""
	prad = float(self.pradius.get())
	amount = float(self.amount.get())	
	result = coreUnsharp(self.current_matrix ,prad,amount)
	self.unsharpdisplay(result)
	return

    def cancelUnsharpCB(self):
	"""
	Quits Unsharp Filtering
	"""
	print 'Pardonos ... '
	self.cancel()

    def okUnsharpCB(self):
	"""
	Saves processed image
	"""
	print 'Dumping File as ....', usdump
	f = open(usdump,'w')
	cPickle.dump(self.unsharp_matrix,f)
	cPickle.dump(self.dicScanParam, f)
	f.close()
	self.ok()

def coreUnsharp(arr,pradius,amount):
	"""
	Real implementaion of Unsharp Filter takes place here
	"""
	blurimg = gauss.coreGaussian(arr, pradius)
	edges = arr - blurimg
	sharpimg = arr + amount*edges
	return sharpimg
