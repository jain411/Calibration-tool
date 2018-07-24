######################
#   Gaussian Class   #
######################
from Tkinter import *
from PIL import ImageTk
import scipy.ndimage as im
import pickle
import os

import dialogs
import iprog

dumppath = os.path.join(os.curdir, 'dump')	# default directory for ".dmp" files
gaussdump = os.path.join(dumppath, 'gdump.dmp')	# default processed filename

def gauss(master, matrix, dchoice, lut,dicScanParam):
    """
    Creates Gauusian Interface
    """
    g = Gaussian(master, matrix, dchoice, lut, dicScanParam)
    return g

class Gaussian(dialogs.GridDialog):

    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	"""
	self.current_matrix = matrix.copy()
	self.gauss_matrix = matrix.copy()
	self.sDisplayChoice=dchoice
	self.lut=lut
	self.dicScanParam = dicScanParam
	dialogs.GridDialog.__init__(self, master, 'Gaussian Filter')
	return

    def body(self, master):
	"""
	Loads root widget with Gaussian widgets
	"""
	self.GaussWindow = master
	self._vCreateGaussWidgets()
	return

    def apply(self):
	pass
	return	
	
    def _vCreateGaussWidgets(self):
	"""
	Creates widgets for Gaussian Filter
	"""
	from PIL import Image
	if self.sDisplayChoice=='I':
		self.imGauss = Image.new("I", self.current_matrix.shape)
	if self.sDisplayChoice=='RGB':
		self.imGauss = Image.new("RGB", self.current_matrix.shape)
	self.ArrImGauss = ImageTk.PhotoImage(self.imGauss)
	self.demoGauss = Canvas(self.GaussWindow, width=256, height=256, scrollregion=(0,0,256,256))
	self.demoGauss.grid(row=0,column=0,rowspan=3,columnspan=4,padx=5,pady=5)
	self.demoGauss.create_image(0,0,image=self.ArrImGauss,anchor=NW)
	self.gaussdisplay(self.gauss_matrix)
	self.xscroll = Scrollbar(self.GaussWindow, orient=HORIZONTAL, command=self.demoGauss.xview)
	self.xscroll.grid(row=3,column=0, sticky=E+W, columnspan=4)
	self.yscroll = Scrollbar(self.GaussWindow, orient=VERTICAL, command=self.demoGauss.yview)
	self.yscroll.grid(row=0,column=4, sticky=N+S, rowspan=3)
	self.demoGauss["xscrollcommand"] = self.xscroll.set
	self.demoGauss["yscrollcommand"] = self.yscroll.set
	self.siggrp = LabelFrame(self.GaussWindow, text='Sigma', padx=5, pady=5)
	self.siggrp.grid(row=4,column=0,sticky=N+E+W+S,padx=10, pady=10, columnspan=3)
	self.sigma = Spinbox(self.siggrp,from_=0.1, to=10, increment=0.1, repeatinterval=80)
	self.sigma.grid(row=0, column=0, sticky=N+E+W+S,padx=5,pady=5)
	self.sigma.delete(0,END)
	self.sigma.insert(0,str(2.5))
	self.BtnApply = Button(self.GaussWindow, command=self.applyGaussCB, text='APPLY')
	self.BtnApply.grid(row=6,column=0,padx=5,pady=5, sticky=N+E+W+S)
	self.BtnCancel = Button(self.GaussWindow, command=self.cancelGaussCB, text='CANCEL')
	self.BtnCancel.grid(row=6,column=1,padx=5,pady=5, sticky=N+E+W+S)
	self.BtnOk = Button(self.GaussWindow, command=self.okGaussCB, text='DONE',fg='red')
	self.BtnOk.grid(row=6,column=2,columnspan=2, sticky=N+E+W+S,padx=5,pady=5)
	return

    def applyGaussCB(self):
	"""
	Performs Gaussian filtering
	"""
	self.applyGauss()

    def applyGauss(self):
	"""
	Gets gauss sigma value from the user
	performs gaussian blurring
	displays processed image
	"""
	sigma = float(self.sigma.get())
	result = coreGaussian(self.current_matrix , sigma)
	self.gaussdisplay(result)

    def gaussdisplay(self,arr):
	"""
	Displays processed image
	"""
	arr = iprog.float2gray(arr)		
	self.gauss_matrix= arr.copy()		
	if self.sDisplayChoice=='I':
		self.imGauss.putdata(arr.flat)
	if self.sDisplayChoice=='RGB':
		colmatrix=map(lambda(x):self.lut[int(x)],arr.flat)
		self.imGauss.putdata(colmatrix)
	self.ArrImGauss.paste(self.imGauss)
	self.demoGauss.config(width=arr.shape[1],height=arr.shape[0] )
	return

    def cancelGaussCB(self):
	"""
	Quits Gaussian Blurring utility
	"""
	print 'Pardono ...'
	self.cancel()

    def okGaussCB(self):
	"""
	Saves processed image
	"""
	print 'Dumping File as ....', gaussdump
	f = open(gaussdump,'w')
	cPickle.dump(self.gauss_matrix,f)
	try:
		cPickle.dump(self.dicScanParam,f)
	except:
		pass
	f.close()
	self.ok()
	return	

def coreGaussian(arr, sigma):
    """
    Real implementation of image Gaussian Filter takes place here
    """
    result = im.filters.gaussian_filter(arr, sigma)
    print 'Gracias .. Mucchhaas Gracias'
    return result

if __name__ == '__main__':
    root = Tk()
    
