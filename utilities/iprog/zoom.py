##################
#   Zoom Class   #
##################
from Tkinter import *
from PIL import ImageTk
import numpy
import scipy.ndimage as im
import cPickle
import time

import dialogs
import iprog 

imagepath='/usr/stm/images'

def zoom(master, matrix, dchoice, lut, dicScanParam=None):
    """
    Function : zoom
    	Creates Zoom Interface

    Arguments :
	master       : root widget 	 
	matrix       : int gray image data array
	dchoice      : variable RGB/Gray
	lut          : list LookUp Table
	dicScanParam : dictionary containing scan parameters

    Returns :
	g : object of class Zoom
    """
    g = Zoom(master, matrix, dchoice, lut, dicScanParam)
    return g

class Zoom(dialogs.GridDialog):

    def __init__(self, master, matrix, dchoice, lut, dicScanParam):
	"""
	Class Constructor : Zoom
			
	Arguments :
		master       : root widget 	 
		matrix       : int gray image data array
		dchoice      : variable RGB/Gray
		lut          : list LookUp Table
		dicScanParam : dictionary containing scan parameters

	Returns :
		None
	"""
	self.current_matrix = matrix.copy()
	self.original_matrix = matrix.copy()
	self.sDisplayChoice=dchoice
	self.lut=lut
	self.dicScanParam = dicScanParam
	dialogs.GridDialog.__init__(self, master, 'Zoom')
	return

    def body(self, master):
	"""
	Method : body
		Loads root widget with Zoom widgets

	Arguments :
		master : root widget

	Returns :
		None
	"""
	self.ZoomWindow = master
	self.vCreateZoomWidgets()
	return

    def apply(self):
	pass
	return	
	
    def vCreateZoomWidgets(self):
	"""
	Method : vCreateZoomWidgets
		Creates widgets for Zooming

	Arguments :
		None

	Returns :
		None
	"""
	from PIL import Image
	if self.sDisplayChoice=='I':
		self.imZoom = Image.new("I", self.current_matrix.shape)
	if self.sDisplayChoice=='RGB':
		self.imZoom = Image.new("RGB", self.current_matrix.shape)
	self.ArrImZoom = ImageTk.PhotoImage(self.imZoom)
	self.demoZoom = Canvas(self.ZoomWindow, width=256, height=256, scrollregion=(0,0,256,256))
	self.demoZoom.grid(row=0,column=0,rowspan=3,columnspan=4,padx=5,pady=5)
	self.demoZoom.create_image(0,0,image=self.ArrImZoom,anchor=NW)
	self.BtnZoomIn=Button(self.ZoomWindow,text='ZoomIn',command=self.CanZoomInCB)
	self.BtnZoomIn.grid(row=4,column=0,sticky=N+E+W+S)
	self.BtnShowOrig=Button(self.ZoomWindow,text='Original',command=self.vShowOriginalCB)
	self.BtnShowOrig.grid(row=4,column=1,sticky=N+E+W+S)
	self.BtnSaveZoom=Button(self.ZoomWindow,text='Save',command=self.vSaveCurrentImageCB)
	self.BtnSaveZoom.grid(row=4,column=2,sticky=N+E+W+S)
	self.BtnQuit=Button(self.ZoomWindow,text='Quit',command=self.cancelZoomCB)
	self.BtnQuit.grid(row=4,column=3,sticky=N+E+W+S)
	self.BtnShowOrig.configure(state=DISABLED)
	self.vInitializeZoom()
	return

    def vInitializeZoom(self):
	"""
	Method : vInitializeZoom
		Binds mouse with the Display Canvas and performs initial settings 
	Arguments :
		None
	Returns :
		None
	"""
	self.demoZoom.bind('<Button-1>', self.vBeginSelectionCB)
	self.demoZoom.bind('<B1-Motion>', self.vShowSelectionCB)
	self.demoZoom.bind('<ButtonRelease-1>', self.vEndSelectionCB)
	self.bSelectionVar=BooleanVar()
	self.bSelectionVar.set(0)
	self.nZoomFactor=1
	self.fZoomedImageBuffer=[]
	self.fZoomedImageBuffer.append(self.current_matrix)	
	self.vDisplayImage(self.current_matrix)	
	return
    
    def vDisplayImage(self,fImageMatrix):
	"""
	Method : vDisplayImage
		Displays image 

	Arguments :
		fImageMatrix : float image matrix
	Returns :
		None
	"""
	self.vRenewCanvas(fImageMatrix)
	return
	
    def vCreateImage(self,gImageMatrix):
	"""
	Method : vCreateImage
		Configures Canvas for Gray/RGB Image Diaplay 

	Arguments :
		fImageMatrix : float image matrix

	Returns :
		None
	"""
	if self.bSelectionVar==True:
		self.nZoomFactor=2
	[row, col] = gImageMatrix.shape
	from PIL import Image
	if self.sDisplayChoice=='I':
		self.imZoom = Image.new("I",[row,col])
	if self.sDisplayChoice=='RGB':
		self.imZoom = Image.new("RGB",[row,col])
	self.ArrImZoom = ImageTk.PhotoImage(self.imZoom)
	if self.sDisplayChoice=='I':
		self.imZoom.putdata(gImageMatrix.flat)

	if self.sDisplayChoice=='RGB':
		colmatrix=map(lambda(x):self.lut[int(x)],gImageMatrix.flat)
		self.imZoom.putdata(colmatrix)
	return
	
	
	
    def vRenewCanvas(self, fImageMatrix):
	"""
	Method : vRenewCanvas
		Refreshes Image Canvas with the new Image data 

	Arguments :
		fImageMatrix : float image matrix

	Returns :
		None
	"""
	gImageMatrix = iprog.float2gray(fImageMatrix)
	self.vCreateImage(gImageMatrix)
	try:
		self.demoZoom.delete(ALL)
	except:
		pass
	self.demoZoom.config(width=gImageMatrix.shape[1], \
			height=gImageMatrix.shape[0] )
	self.CanvasImage = self.demoZoom.create_image(0,0,image=self.ArrImZoom,anchor=NW)
	self.ArrImZoom.paste(self.imZoom)
	return	

    def vBeginSelectionCB(self,event):
	"""
	Method : vBeginSelectionCB
		Records the starting location 

	Arguments :
		event : Tkinter binding with mouse

	Returns :
		None
	"""
	self.arRegion=[[0,0],[0,0]]
	self.arRegion[0]=[event.x,event.y]
	return
		
    def vShowSelectionCB(self, event):
	"""
	Method : vShowSelectionCB
		Records position changes
		Redraws the selection area as the mouse is moved over the image 

	Arguments :
		event : Tkinter binding with mouse

	Returns :
		None
	"""
	self.arRegion[1] = [event.x, event.y]
	self.vLimitSelection()
	self.vShowBox()
	return
		
    def vShowBox(self):
	"""
	Method : vShowBox
		Displays boundary over the selected image area 

	Arguments :
		None
		
	Returns :
		None
	"""
	try:
		self.demoZoom.delete(self.wDottedBox)
	except:
		pass
	self.wDottedBox=self.demoZoom.create_rectangle(self.arRegion)
	return
	
    def vEndSelectionCB(self, event):
	"""
	Method : vEndSelectionCB
		When mouse button is released it displays the selected image area	
		
	Arguments :
		event : Tkinter binding with mouse

	Returns :
		None
	"""
	self.vShowSelectionCB(event)
	if (self.arRegion[1][0]>self.current_matrix.shape[0]) or self.arRegion[1][0]<0:
		tkMessageBox.showerror('Area Error','Too large Area Selected!!')
		self.demoZoom.delete(self.wDottedBox)
		return		
	if (self.arRegion[1][1]>self.current_matrix.shape[1]) or self.arRegion[1][1]<0:
		tkMessageBox.showerror('Area Error','Too large Area Selected!!')
		self.demoZoom.delete(self.vDottedBox)
		return		

	if (self.arRegion[1][0] - self.arRegion[0][0])==0:
		return
	if (self.arRegion[1][1] - self.arRegion[0][1])==0:
		return
	self.bSelectionVar.set(1)
	self.vGetImageData()
	return
		
    def vGetImageData(self):
	"""
	Method : vGetImageData
		Extracts image data from the selected image area 

	Arguments :
		None

	Returns :
		None
	"""
	ylen=self.arRegion[1][0]-self.arRegion[0][0]
	xlen=self.arRegion[1][1]-self.arRegion[0][1]
	fImageMatrix=numpy.zeros([abs(xlen)+1,abs(ylen)+1],'f')
	k=0
	w=0
	if xlen<=0:
		for i in range(self.arRegion[1][1],self.arRegion[0][1]+1):
			for j in range(self.arRegion[1][0],self.arRegion[0][0]+1):
				fImageMatrix[k][w]=self.current_matrix[i][j]
				w+=1
			w=0
			k+=1
	else:	
		for i in range(self.arRegion[0][1],self.arRegion[1][1]+1):
			for j in range(self.arRegion[0][0],self.arRegion[1][0]+1):
				fImageMatrix[k][w]=self.current_matrix[i][j]
				w+=1
			w=0
			k+=1
	self.current_matrix=fImageMatrix
	return
		
    def vLimitSelection(self):
	"""
	Method : vLimitSelection
		Limits selection from going out of image boundaries

	Arguments :
		None

	Returns :
		None
	"""
	l = (self.arRegion[1][0] - self.arRegion[0][0])
	b = (self.arRegion[1][1] - self.arRegion[0][1])
	if l>b:
	    side = b
	else:
	    side = l
	self.arRegion[1] = [self.arRegion[0][0]+side, self.arRegion[0][1]+side] 
	return


    def cancelZoomCB(self):
	"""
	Method : cancelZoomCB
		Quits Zooming utility

	Arguments :
		None

	Returns :
		None
	"""
	print 'Pardono ...'
	self.cancel()
	
	
    def CanZoomInCB(self):
	"""
	Method : CanZoomInCB
		Zooms the selected image portion 

	Arguments :
		None

	Returns :
		None
	"""
	starttime=time.time()
	print "Zooming in"
	self.bZoomIn=True
	self.nZoomFactor=2
	fZoomImage=self.afBartlett(self.current_matrix,self.nZoomFactor)
	self.fImageMatrix=iprog.gaussian_(fZoomImage)
	self.current_matrix=self.fImageMatrix
	self.vRenewCanvas(self.fImageMatrix)
	print "time taken",time.time()-starttime
	self.BtnShowOrig.configure(state=ACTIVE)
	return
		
    def afBartlett(self,fImageMatrix,ZoomFactor):
	"""
	Method : afBartlett
		Calculates Zoomed Image matrix 

	Arguments : 
		fImageMatrix : float image matrix
		ZoomFactor   : int Zoom Factor	

	Returns :
		zoomed : float Zoomed Image matrix
	"""
	xlen=int(fImageMatrix.shape[0]*ZoomFactor)
	padded_im=numpy.zeros([xlen,xlen],'f')
	for i in range(fImageMatrix.shape[0]):
		for j in range(fImageMatrix.shape[1]):
			padded_im[i*ZoomFactor][j*ZoomFactor]=fImageMatrix[i][j]
	row_vect=numpy.zeros([1,2*ZoomFactor-1],'f')
	col_vect=numpy.zeros([2*ZoomFactor-1,1],'f')
	result=self.arBartlettFilter(ZoomFactor)
	zoomed=im.convolve(padded_im,result)
	return zoomed
		
    def arBartlettFilter(self,ZoomFactor):
	"""
	Method : arBartlettFilter
 		Generates Bartlett filter kernel

	Arguments :
		ZoomFactor   : int Zoom Factor

	Returns :
		bartlett : int Bartlett kernel
	"""
	a=2*ZoomFactor-1
	b=2*ZoomFactor
	row_vect=numpy.zeros([1,3],'f')
	col_vect=numpy.zeros([3,1],'f')
	for y in range(1,4):
		if y <=3:
			col_vect[y-1]=3-y+1	
		else:
			col_vect[y-1]=len(col_vect)-y+1
	for x in range(1,4):
		if x <=3:
			row_vect[0][x-1]=x
		else:
			row_vect[0][x-1]=3-x+1
	tmp=col_vect*row_vect
	bartlett=float(1/float(3*3))*tmp
	return bartlett

    def vShowOriginalCB(self):
	"""
	Method : vShowOriginalCB
		Displays Original unzoomed image
			
	Arguments :
		None
		
	Returns :
		None
	"""
	fImageMatrix=self.fZoomedImageBuffer[0]
	self.current_matrix=fImageMatrix
	self.vRenewCanvas(fImageMatrix)
	self.BtnShowOrig.configure(state=DISABLED)
	return	

    def vSaveCurrentImageCB(self):
	"""
	Method : vSaveCurrentImageCB
		Saves Current image present on the imaging windowAttaches Callbacks to ExportGui widgets 

	Arguments :
		None

	Returns :
		None
	"""
	print 'Saving Zoomed Image'
	fname=tkFileDialog.asksaveasfilename(defaultextension='.pic',initialdir=imagepath)
	if fname:
		fname=open(fname,'w')
		cPickle.dump(self.current_matrix,fname)
		try:
			cPickle.dump(self.dicScanParam,fname)
		except:
			pass
	else:
		return
	return
		
if __name__ == '__main__':
    root = Tk()
    
