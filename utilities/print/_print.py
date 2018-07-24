####################
#   _Print Class   #
####################

import numpy, cPickle, time, os
from PIL import Image,ImageTk
import tkMessageBox, tkFileDialog
from Tkinter import *

import iprog
import dialogs
import import_
import app_print
	
FTYPES={'pic':('New STM Files','*.pic'),
	'dat':('Old STM Files','*.dat')
	}					# Stm Image file types`

def _print(f=None, oMenuBar=None, olut=None):
	"""
	Creates printing interface
	"""
	if not f:
		root=Tk()
		f=Frame(root).grid()
	oAppPrint = app_print.app_print()
	oAppPrint.vCreatePSWindow(f)
	oPrint = _Print(oAppPrint, oMenuBar, olut)	
	if not f:
		root.title('Print')
		root.mainloop()
	return oPrint

class _Print:
	def __init__(self, oAppPrint, oMenuBar, olut):
		"""
		Class Contructor : _Print
		"""
		self.oAppPrint = oAppPrint
		self.oMenuBar = oMenuBar
		self.olut = olut
		self.oImaging = self.oMenuBar.oImaging
		self._configureCB()
		self._initPrint()
		return

	def _configureCB(self):
		"""
		Attaches Callbacks to PrintGui widgets 
		"""
		self.oAppPrint.opensubmenu.add_command(label='Scan Window',\
							command=self.vOpenScanCB)
		self.oAppPrint.opensubmenu.add_command(label='Retrace Window',\
							command=self.vOpenRetCB)
		self.oAppPrint.opensubmenu.add_command(label='File',\
							command=self.vOpenCB)
		self.oAppPrint.filemenu.add_command(label='Print',\
							command=self.vPrintCB)
		self.oAppPrint.filemenu.add_command(label='Quit',\
							command=self.vQuitCB)
		self.oAppPrint.colorsettingssubmenu.add_command(label='Gray Mode',\
							command=self.vGrayChoiceCB)
		self.oAppPrint.colorsettingssubmenu.add_command(label='Color Mode',\
							command=self.vRGBChoiceCB)
		self.oAppPrint.utilitiesmenu.add_command(label='Zoom',\
							command=self.vZoomCB)
		self.oAppPrint.utilitiesmenu.add_command(label='Original',\
							command=self.vOriginalCB)
		self.oAppPrint.btnOpen.configure(command=self.vOpenCB)
		self.oAppPrint.btnZoom.configure(command=self.vZoomCB)
		self.oAppPrint.btnOrig.configure(command=self.vOriginalCB)
		self.oAppPrint.psGroup.protocol('WM_DELETE_WINDOW',self.vQuitCB)
		self.oAppPrint.btnOrig.configure(state=DISABLED)
		return
	
	def _initPrint(self):
		"""
		Initial Print Settings
		"""
		self.bPrintImageVar = BooleanVar()
		self.bPrintImageVar.set(False)
		self.bOldPrintColorVar=BooleanVar()
		self.bOldPrintColorVar.set(False)	# False --> Gray & True --> RGB
		self.bPrintColorVar=BooleanVar()
		self.bPrintColorVar.set(False)		# False --> Gray & True --> RGB
		self.bRetImageVar=BooleanVar()
		self.bRetImageVar.set(False)
		self.oAppPrint.psGroup.protocol('WM_DELETE_WINDOW',self.vQuitCB)
		return

	def vOpenCB(self):
		"""
		Opens and Displays a User Select File	
		"""
		ftypes=FTYPES.values()
		filepath = dialogs.strPathTracker()
		file=tkFileDialog.askopenfilename(filetypes=ftypes,initialdir=filepath)
		if not(file):
			return
		dialogs.strPathTracker(file)
		self.fScanImageMatrix,self.fRetImageMatrix=self.fReadFile(file)
		self.fOrigScanImageMatrix=self.fScanImageMatrix
		self.fOrigRetImageMatrix=self.fRetImageMatrix
		self.vShow(self.fScanImageMatrix)
		self.oAppPrint.ArrCanvas.postscript(file='/tmp/scanpsfile.ps',\
						 height=self.fScanImageMatrix.shape[1], \
						 width=self.fScanImageMatrix.shape[0])
		try:
			self.vShow(self.fRetImageMatrix)
			self.oAppPrint.ArrCanvas.postscript(file='/tmp/retpsfile.ps',\
						height = self.fRetImageMatrix.shape[1],\
						width = self.fRetImageMatrix.shape[0])
			self.bRetImageVar.set(True)
		except:
			pass
		return

	def vOpenScanCB(self):
		"""
		Opens and Displays image present on Scan Window
		"""
		if self.oImaging.bImagePresentVar.get()==False:
			tkMessageBox.showwarning('Blank','No  Images on Display')
			return
 		f=open('/usr/stm/dump/scanimgdump.dmp')
		m=cPickle.load(f)
		fImageMatrix=numpy.asarray(m)
		self.nImageSize=fImageMatrix.shape[0]
		self.fImageMatrix = fImageMatrix
		self.fScanImageMatrix=self.fImageMatrix	
		#self.fOrigScanImageMatrix=self.fScanImageMatrix
		self.fRetImageMatrix=None
		self.fOrigRetImageMatrix=None
		self.fOrigScanImageMatrix=self.fImageMatrix	
 		self.vShow(fImageMatrix)
		self.oAppPrint.ArrCanvas.postscript(file='/tmp/scanpsfile.ps',\
							height = self.fScanImageMatrix.shape[1],\
							width = self.fScanImageMatrix.shape[0])
		return
			
	def vOpenRetCB(self):
		"""
		Opens and Displays image present on Retrace Window
		"""
		if self.oImaging.bImagePresentVar.get()==False:
			tkMessageBox.showwarning('Blank','No  Images on Display')
			return
 		f=open('/usr/stm/dump/retimgdump.dmp')
		m=cPickle.load(f)
		fImageMatrix=numpy.asarray(m)
		self.nImageSize=fImageMatrix.shape[0]
		self.fImageMatrix = fImageMatrix
		self.fScanImageMatrix=self.fImageMatrix	
		self.fOrigScanImageMatrix=self.fImageMatrix	
		#self.fOrigScanImageMatrix=self.fScanImageMatrix
		self.fRetImageMatrix=None
		self.fOrigRetImageMatrix=None
 		self.vShow(fImageMatrix)
		self.oAppPrint.ArrCanvas.postscript(file='/tmp/scanpsfile.ps',\
							height = self.fScanImageMatrix.shape[1],\
							width = self.fScanImageMatrix.shape[0])
		return

	def vPrintCB(self):
		"""
		It simplly sends ".ps" image file captured from the 
		canvas to the default printer and then deletes the ".ps" file
		"""
		if self.bPrintImageVar.get()==False:	
			tkMessageBox.showerror('Error','First select an Image!!')	
			return
		os.system('lpr /tmp/scanpsfile.ps')
		if self.bRetImageVar.get()==True:
			try:
				os.system('lpr /tmp/retpsfile.ps')
			except:
				pass
		self.bRetImageVar.set(False)	
		return

	def vQuitCB(self):
		"""
		Terminates Print utility
		"""
		self.oMenuBar.Print_Instance=0
		self.oAppPrint.psGroup.destroy()
		return

	def vGrayChoiceCB(self):
		"""
		Refreshes canvas to display Gray Image if Gray Printout mode is selected
		"""
		self.bPrintColorVar.set(False)	
		if self.bOldPrintColorVar.get()!=self.bPrintColorVar.get():
			try:
				self.vShow(self.fScanImageMatrix)
				try:
					self.oAppPrint.ArrCanvas.postscript(file='/tmp/scanpsfile.ps',\
									height = self.fScanImageMatrix.shape[1],\
									width = self.fScanImageMatrix.shape[0])
				except:
					pass
			except:
				pass
			try:
				self.vShow(self.fRetImageMatrix)	
				try:
					self.oAppPrint.ArrCanvas.postscript(file='/tmp/retpsfile.ps',\
									height = self.fRetImageMatrix.shape[1],\
									width = self.fRetImageMatrix.shape[0])
				except:
					pass
			except:
				pass
		self.bOldPrintColorVar.set(False)
		return

	def vRGBChoiceCB(self):
		"""
		Refreshes canvas to diaplay RGB Image when Color Printout mode is selected
		"""
		self.bPrintColorVar.set(True)
		if self.bOldPrintColorVar.get()!=self.bPrintColorVar.get():
			try:
				self.vShow(self.fScanImageMatrix)
				try:
					self.oAppPrint.ArrCanvas.postscript(file='/tmp/scanpsfile.ps',\
									height = self.fScanImageMatrix.shape[1],\
									width = self.fScanImageMatrix.shape[0])
				except:
					pass
			except:
				pass
			try:
				self.vShow(self.fRetImageMatrix)
				try:
					self.oAppPrint.ArrCanvas.postscript(file='/tmp/retpsfile.ps',\
									height = self.fRetImageMatrix.shape[1],\
									width = self.fRetImageMatrix.shape[0])
				except:
					pass
			except:
				pass
		self.bOldPrintColorVar.set(True)
		return

	def fReadFile(self,file):
		"""
		Extracts data from the image file to be displayed and printed
		"""
		[self.fImageMatrix,self.fRetImageMatrix,dicImageDetails,sFileType]=import_.aafReadImageFile(file)
		return self.fImageMatrix,self.fRetImageMatrix

	def vShow(self,fImageMatrix):
		"""
		Displays Image
		"""
		self.vRenewCanvas(fImageMatrix)
		self.bPrintImageVar.set(True)
		return

	def vRenewCanvas(self,fImageMatrix):
		"""
		Refreshes Image Canvas with the new Image data
		"""
		try:
			self.oAppPrint.ArrCanvas.delete(ALL)
		except:
			pass
		nImageMatrix=iprog.float2gray(fImageMatrix)
		self.vCreateImage(nImageMatrix)
		self.CanvasImage = self.oAppPrint.ArrCanvas.create_image(0,0,image=self.ArrIm,anchor=NW)
		self.ArrIm.paste(self.im)
		return

	def vCreateImage(self,nImageMatrix):
		"""
		Configures Canvas for Gray/RGB Image Display		
		"""
		[row,col]=nImageMatrix.shape
		from PIL import Image
		self.oAppPrint.ArrCanvas.config(width=row,height=col)
		if self.bPrintColorVar.get()==False:
			self.im=Image.new('I',[row,col])
			self.ArrIm=ImageTk.PhotoImage(self.im)
			self.im.putdata(nImageMatrix.flat)
		if self.bPrintColorVar.get()==True:
			self.im=Image.new('RGB',[row,col])	
			self.ArrIm=ImageTk.PhotoImage(self.im)
			colmatrix=map(lambda(x):self.olut[int(x)],nImageMatrix.flat)
			self.im.putdata(colmatrix)
		return

	def vZoomCB(self):
		"""
		ZoomIn Image		
		"""
		self.starttime=time.time()
		try:
			fScanZoomedImage = im.zoom(self.fScanImageMatrix, 2)
			self.vRenewCanvas(fScanZoomedImage)
			self.fScanImageMatrix = fScanZoomedImage
			self.oAppPrint.ArrCanvas.postscript(file='/tmp/scanpsfile.ps',\
							height = self.fScanImageMatrix.shape[1],\
							width = self.fScanImageMatrix.shape[0])
		except:
			pass	
		try:
			fRetZoomedImage = im.zoom(self.fRetImageMatrix, 2)
			self.vRenewCanvas(fRetZoomedImage)
			self.fRetImageMatrix = fRetZoomedImage
			self.oAppPrint.ArrCanvas.postscript(file='/tmp/retpsfile.ps',\
							height = self.fRetImageMatrix.shape[1],\
							width = self.fRetImageMatrix.shape[0])
		except:
			pass	
		print "time taken ",time.time()-self.starttime
		self.oAppPrint.btnOrig.configure(state=ACTIVE)
		return
	
	def vOriginalCB(self):
		"""
		Displays Original unZoomed Image		
		"""
		print "Displaying Original Image"
		self.fScanImageMatrix = self.fOrigScanImageMatrix
		self.vRenewCanvas(self.fScanImageMatrix)
		self.oAppPrint.ArrCanvas.postscript(file='/tmp/scanpsfile.ps',\
						height = self.fScanImageMatrix.shape[1],\
						width = self.fScanImageMatrix.shape[0])
		if self.fOrigRetImageMatrix != None:	
			try:	
				self.fRetImageMatrix = self.fOrigRetImageMatrix
				self.vRenewCanvas(self.fRetImageMatrix)
				self.oAppPrint.ArrCanvas.postscript(file='/tmp/retpsfile.ps',\
							height = self.fRetImageMatrix.shape[1],\
							width = self.fRetImageMatrix.shape[0])
			except:
				pass	
		self.oAppPrint.btnOrig.configure(state=DISABLED)
		return


if __name__=='__main__':
	_print()	
