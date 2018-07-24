###################
#   iProg Class   #
###################
import tkFileDialog
import tkMessageBox
from PIL import Image as Im
from PIL import ImageTk
import os
import cPickle
import numpy
import scipy.ndimage as im
import numpy.fft as fft
import re

import dialogs
import gauss
import histeq
import unsharp
import nlt
import fourier
import bness		
import contrast		
import zoom
import app_iprog

dumppath = os.path.join(os.curdir, 'dump')	# default directory  containing ".dmp" files
sfilename = os.path.join(dumppath, 'scanimgdump.dmp')	# Scan image file path
rfilename = os.path.join(dumppath, 'retimgdump.dmp')	# Retrace image file path
invertdump = os.path.join(dumppath, 'invert.dmp')	# Inaverted image file poath	
dummydump = os.path.join(dumppath, 'dummy.dmp')	
rotatedump = os.path.join(dumppath, 'rotate.dmp')	# Rotate image file path	

checkdmp = re.compile('dmp')
checkscan = re.compile(sfilename)
checkret = re.compile(rfilename)

menu_font_type = ("Verdana", 12, 'normal')	# font description
CANVAS_FONT = 'LiberationSans-Regular'
CANVAS_FONT_SIZE = 10

FILETYPES = {	'npic':('SiM Files','*.npic'), \
		}				# Stm Image File types

def iprog(master=None, oToolBar=None, olut=None):
	"""
       	Creates I-Prog Interface
	"""
	if master:
	    oAppIProg=app_iprog.app_iprog()
	    oAppIProg.vCreateIPwindow(master)	
	    i = iProg(oAppIProg, oToolBar, olut)
	    return i
	root = Tk()
	i = iProg(root)
	root.mainloop()	
	return

def float2gray (m):
    """
    Convert float image data into gray scale 0-255
    """
    if len(m.shape) == 2:
	g = m - m.min ()
	g = g * 255 / g.max ()
    else:
	g = numpy.zeros(m.shape, 'f')
	for count in range(m.shape[0]):
	    g [count] = m [count] - m [count].min ()
	    g [count] = g [count] * 255 / g [count].max ()
    return g

def invert(matrix):
	"""
	Inverts gray scale
	"""
	newm = 255 - matrix
	return newm

FIL_LENGTH 	= 15
SD_BG 		= 3.0 
SD_FG		= 0.5

def afBgSubH(matrix):
    """
    Background subtraction for images taken in horizontal mode
    """
    afNewMatrix = matrix.copy()
    afNewMatrix = im.filters.gaussian_filter(afNewMatrix, SD_FG)

    [nRows, nColumns] = matrix.shape
    nSpread = FIL_LENGTH
    for line in range(nRows):
	for point in range(nSpread, nColumns-nSpread, 1):
	    afNewMatrix[line, point] = matrix[line, point-nSpread:point+nSpread-1].mean()
    afBgMatrix = afNewMatrix.copy()
    #afNewMatrix = matrix - im.filters.gaussian_filter(afBgMatrix, SD_BG)
    afNewMatrix = matrix - afBgMatrix
    afNewMatrix[:,:nSpread] = matrix[:,:nSpread]
    afNewMatrix[:, -nSpread:] = matrix[:, -nSpread:]
    lbandbg = numpy.zeros((nRows, nSpread), 'f')
    rbandbg = numpy.zeros((nRows, nSpread), 'f')
    for i in range(nSpread):
	lbandbg[:,i] = afBgMatrix[:,nSpread]
	rbandbg[:,i] = afBgMatrix[:,-nSpread]
    afNewMatrix[:,:nSpread] -= lbandbg
    afNewMatrix[:, -nSpread:] -= rbandbg
    #pylab.plot(range(nColumns), afBgMatrix[50], \
    #		range(nColumns), matrix[50], \
    #		range(nColumns), afNewMatrix[50])
    #pylab.show()
    #afNewMatrix = im.filters.gaussian_filter(afNewMatrix, SD_FG)
    return afNewMatrix

def afBgSubV(matrix):
    """
    Background subtraction for images taken in vertical mode
    """
    afNewMatrix = matrix.copy()
    [nRows, nColumns] = matrix.shape
    nSpread = FIL_LENGTH 
    for line in range(nColumns):
	for point in range(nSpread, nRows-nSpread, 1):
	    afNewMatrix[point, line] = matrix[point-nSpread:point+nSpread-1, line].mean()
    afBgMatrix = afNewMatrix.copy()
    afNewMatrix = matrix - afBgMatrix
    afNewMatrix[:nSpread] = matrix[:nSpread]
    afNewMatrix[-nSpread:] = matrix[-nSpread:]
    lbandbg = numpy.zeros((nSpread, nColumns), 'f')
    rbandbg = numpy.zeros((nSpread, nColumns), 'f')
    for i in range(nSpread):
	lbandbg[i] = afBgMatrix[nSpread]
	rbandbg[i] = afBgMatrix[-nSpread]
    afNewMatrix[:nSpread] -= lbandbg
    afNewMatrix[-nSpread:] -= rbandbg
    #pylab.plot(range(nColumns), afBgMatrix[:,50], \
    #		range(nColumns), matrix[:,50], \
    #		range(nColumns), afNewMatrix[:,50])
    #pylab.show()
    return afNewMatrix


def zeropad(m, size, anchor=0):
	"""
	Zero-padding the matrix before fourier transform	
	"""
	if len(size) == 1:
		paddedm = numpy.zeros(size[0],'f')
		start = [0, size[0] - m.shape[0]]
		for i in range(m.shape[0]):
			paddedm[start[anchor]+i] = m[i]
		return paddedm
	if len(size) == 2:
		paddedm = numpy.zeros((size[0], size[1]), 'f')
		rstart = [0, 0, size[0] - m.shape[0],size[0] - m.shape[0] ]
		cstart = [0, size[1] - m.shape[1], size[1] - m.shape[1], 0 ]
		for i in range(m.shape[0]):
			for j in range(m.shape[1]):
				paddedm[rstart[anchor]+i][cstart[anchor]+j] = m[i][j]
	return paddedm
	
def crotate(m,angle):
	"""
	Rotate image by multiple of 90 degrees
	--> designed to rotate quads by 180 degrees CCW
	"""
	turns = angle/90
	for i in range(turns):
		m = im.rotate(m,90)
	return m 

def arrange(m):
	"""
	Divides the matrix in 4 quads
	Rotates each quad by 180 degrees
	Creates the new quad
	Especially designed for displaying Fourier Transform
	"""
	rows = m.shape[0]
	cols = m.shape[1]
	print 'Quading the matrix'
	q1 = m[:rows/2,:cols/2].copy()
	q2 = m[:rows/2,cols/2:].copy()
	q3 = m[rows/2:,cols/2:].copy()
	q4 = m[rows/2:,:cols/2].copy()
	print 'Rotating each quad'
	rotq1 = crotate(q1,180).copy()
	rotq2 = crotate(q2,180).copy()
	rotq3 = crotate(q3,180).copy()
	rotq4 = crotate(q4,180).copy()
	print 'padding each quad'
	padq1 = zeropad(rotq1,(rows,cols),0)
	padq2 = zeropad(rotq2,(rows,cols),1)
	padq3 = zeropad(rotq3,(rows,cols),2)
	padq4 = zeropad(rotq4,(rows,cols),3)
	print 'adding all padded quads'	
	result = padq1 + padq2 + padq3 + padq4
	return result

def min_maxfilter(m,sigma=2.5):	
    """
    It reduces the width of normal distribution.
    Min-max filter that replaces :
	: every value which is less than minval by minval
	: every value which is greater then maxval by maxval
    """
    if len(m.shape) == 2:
	meanval = m.mean()
	stdval = m.std()
	minval = meanval - sigma*stdval
	maxval = meanval + sigma*stdval
	clipped = numpy.clip (m,minval,maxval)	
    else:
        clipped = numpy.zeros (m.shape, 'f')
	for count in range(m.shape[0]):
	    meanval = m [count].mean()
	    stdval = m [count].std()
	    minval = meanval - sigma * stdval
	    maxval = meanval + sigma * stdval
	    clipped [count] = numpy.clip(m [count], minval, maxval)	
    return clipped


def linefit(x, y):
	'''
	Returns slope and intercept using least square straight line fit algorithm
	'''
	np = x.shape[0]
	# http://mathworld.wolfram.com/LeastSquaresFitting.html
	slope = ((x * y).sum() - np * x.mean() * y.mean()) / ((x * x).sum() - np * x.mean() ** 2)
	intercept = (y.mean() * (x * x).sum() - x.mean() * (x * y).sum()) / ((x * x).sum() - np * x.mean() ** 2)
	return slope, intercept



def correctXSlopeByLineFit(m):
	"""
	Line fit and remove slope along X
	"""
	newm = numpy.zeros (m.shape, 'f')
	if len (m.shape) == 2:
		x = numpy.arange(m.shape[1])
		for i in range (m.shape [0]):
			#m_, c = linefit(x, m[i])
			[m_, c] = numpy.polyfit(x, m[i], 1)
			line = m_ * x + c
			newm [i] = m [i] - line
	else:
		x = numpy.arange(m.shape[2])
		for count in range (m.shape [0]):
			for i in range (m.shape [1]):
				#m_, c = linefit(x, m[count][i])
				[m_, c] = numpy.polyfit(x, m[count][i], 1)
				line = m_ * x + c
				newm [count] [i] = m [count] [i] - line 
	return newm


def correctYSlopeByLineFit(m):
	"""
	Line fit and remove slope along Y
	"""
	newm = numpy.zeros (m.shape, 'f')
	if len (m.shape) == 2:
		x = numpy.arange(m.shape[0])
		for i in range (m.shape [1]):
			#m_, c = linefit(x, m[i])
			[m_, c] = numpy.polyfit(x, m[:, i], 1)
			line = m_ * x + c
			newm [:, i] = m [:, i] - line
	else:
		x = numpy.arange(m.shape[1])
		for count in range (m.shape [0]):
			for i in range (m.shape [2]):
				#m_, c = linefit(x, m[count][i])
				[m_, c] = numpy.polyfit(x, m[count][:, i], 1)
				line = m_ * x + c
				newm [count] [:, i] = m [count] [:, i] - line 
	return newm


def correctXslope (m):
    """
    Remove slope along X
    """
    newm = correctXSlopeByLineFit(m)
    return newm


def correctYslope (m):
    """
    Remove slope along Y
    """
    newm = correctYSlopeByLineFit(m)
    return newm


def correctSlope (m):
    """
    Slope-Correction is a more appropriate word ....  for Repair Filter !!        
    """
    newmx = correctXSlopeByLineFit(m)
    newmxy = correctYSlopeByLineFit(newmx)
    return newmxy


def correctZ_DriftX (m):
    '''
    Bring mean for each line along X to zero
    '''
    newm = numpy.zeros (m.shape, 'f')
    if len (m.shape) == 2:
	for i in range (m.shape [0]):
		mean = m [i].mean()
		newm [i] = m[i] - mean
    else:
	for count in range (m.shape [0]):
	    for i in range (m.shape [1]):
		mean = m [count] [i].mean()
		newm [count] [i] = m [count] [i] - mean 
    return newm


def correctZ_DriftY (m):
    '''
    Bring mean for each line along Y to zero
    '''
    newm = numpy.zeros (m.shape, 'f')
    #print 'Treat Y and Repair X-slope ...'
    if len (m.shape) == 2:
	for i in range (m.shape [1]):
		mean = m [:, i].mean()
		newm [:, i] = m [:, i] - mean
    else:
	for count in range (m.shape[0]):
	    for i in range (m.shape[2]):
		mean = m [count][:, i].mean() 
		newm [count] [:, i] = m [count] [:, i] - mean 
    return newm


def correctZ_DriftXY (m):
    ''' 
    Corrects Z drift along both X and Y Axis
    '''
    newmx = correctZ_DriftX(m) 
    newmxy = correctZ_DriftY(newmx)
    return newmxy
 

def gaussian_(m):
    """
    Smoothens image matrix (Blur filter removes spec noise)
    """
    # Gaussian ...
    if len (m.shape) == 2:
	gaussmat = im.filters.gaussian_filter(m, 1.1)
	return gaussmat
    else:
        newm = numpy.zeros (m.shape, 'f')
	for count in range (m.shape[0]):
	    newm [count] = im.filters.gaussian_filter (m [count], 1.1)
	return newm

def fourierfilter(matrix, threshold, filterchoice='L'):
    """
    Fourier Filter, default is low pass filter
    """
    if len (matrix.shape) == 2:
	fftric = fft.fft2(matrix) 
	#### Thresholding ####
	#threshold = 2.0
	amp = numpy.sqrt(fftric.real**2 + fftric.imag**2)	
	phase_matrix = numpy.arctan2(fftric.imag , fftric.real)
	if filterchoice == 'L':
	    bin_mask = numpy.where(amp > amp.mean()+threshold*amp.std(), 1, 0)
	if filterchoice == 'H':
	    bin_mask = numpy.where(amp > amp.mean()+threshold*amp.std(), 0, 1)
	amp *= bin_mask
	fil_transform = numpy.zeros(matrix.shape, 'D')
	fil_transform.real = amp*numpy.cos(phase_matrix) 
	fil_transform.imag = amp*numpy.sin(phase_matrix) 
	ifftric = fft.ifft2(fil_transform)
	matrix = ifftric.real
    else:
        fftric = numpy.zeros (matrix.shape, 'D')
        ifftric = numpy.zeros (matrix.shape, 'D')
	for count in range (matrix.shape[0]):
	    fftric [count] = fft.fft2 (matrix [count]) 
	    #### Thresholding ####
	    #threshold = 2.0
	    amp = numpy.sqrt(fftric [count].real ** 2 + fftric [count].imag ** 2)	
	    phase = numpy.arctan2(fftric [count].imag , fftric [count].real)
	    if filterchoice == 'L':
	        bin_mask = numpy.where (amp > amp.mean () + threshold * amp.std (), 1, 0)
	    if filterchoice == 'H':
	        bin_mask = numpy.where(amp > amp.mean () + threshold * amp.std (), 0, 1)
	    amp *= bin_mask
	    fil_transform = numpy.zeros (matrix.shape [-2:], 'D')
	    fil_transform.real = amp * numpy.cos (phase) 
	    fil_transform.imag = amp * numpy.sin (phase) 
	    ifftric [count] = fft.ifft2(fil_transform)
	    matrix [count] = ifftric [count].real
    return matrix

def convert2polar(imageData):
    polarData = imageData.copy()

    topo = imageData[0, :, :]
    ip = imageData[1, :, :]
    qp = imageData[2, :, :]

    amplitude = numpy.sqrt(ip * ip + qp * qp)
    phase = numpy.arctan2(ip, qp)

    polarData[0, :, :] = topo
    polarData[1, :, :] = amplitude
    polarData[2, :, :] = phase

    return polarData


def ps2jpg(filename):
    """
    Not very happy to use system commands... breaking
    platform independence rules
    """
    pass
    return


def scratchRemoval(m, axis = 'H'):
    newm = m.copy()
    sigma = 1.1
    size = 5
    if len (m.shape) == 2:
	    newm = im.filters.median_filter(newm, size)
    else:
	for count in range (m.shape[0]):
	    newm[count] = im.filters.median_filter(newm[count], size)

    return newm


class iProg:
	def __init__(self, oAppIProg, oToolBar, olut):
		"""
		Class Contructor : iProg
		"""
		self.oAppIProg = oAppIProg
		self.oToolBar=oToolBar
		self.olut = olut
		self.vConfigureIProgWidgets()
		return

	def vConfigureIProgWidgets(self):
		"""
		Creates Iprog widgets
		"""			
		self.oAppIProg.opensubmenu.add_command(label='Scan Window',\
						command=self.vOpenScanWindow,\
						font=menu_font_type)
		self.oAppIProg.opensubmenu.add_command(label='Retrace Window',\
						command=self.vOpenRetraceWindow,\
						font=menu_font_type)
		self.oAppIProg.opensubmenu.add_command(label='From Dump',\
						command=self.vOpenDumpImage,\
						font=menu_font_type)
		self.oAppIProg.opensubmenu.add_command(label='File',\
						command=self.vOpenFileImage,\
						font=menu_font_type)
		self.oAppIProg.filemenu.add_command(label='Create PS',\
						command=self.savepsCB,\
						font=menu_font_type)

		self.oAppIProg.filemenu.add_command(label='Quit',\
						command=self.quitCB,\
						font=menu_font_type)
		self.oAppIProg.colortoolssubmenu.add_command(label='Display Choice',\
						command=self.vDisplayChoice,\
						font=menu_font_type)
		self.oAppIProg.colortoolssubmenu.add_command(label='Brightness',\
						command=self.bnessCB,\
						font=menu_font_type)
		self.oAppIProg.colortoolssubmenu.add_command(label='Contrast',\
						command=self.contrastCB,\
						font=menu_font_type)
		self.oAppIProg.filtersubmenu.add_command(label='G Blur',\
						command=self.vGaussianCB,\
						font=menu_font_type)
		self.oAppIProg.filtersubmenu.add_command(label='U Masking',\
						command=self.unsharpCB,\
						font=menu_font_type)
		self.oAppIProg.filtersubmenu.add_command(label='Hist Eq',\
						command=self.vHistEqCB,\
						font=menu_font_type)
		self.oAppIProg.filtersubmenu.add_command(label='Fourier',\
						command=self.fourierCB,\
						font=menu_font_type)
		self.oAppIProg.filtersubmenu.add_command(label='NLT',\
						command=self.nltCB,\
						font=menu_font_type)
		self.oAppIProg.utilitiesmenu.add_command(label='Invert',\
						command=self.invertCB,\
						font=menu_font_type)
		self.oAppIProg.transformsubmenu.add_command(label='Rotate 90 Degrees CCW',\
						command=self.rotate90CCWCB,\
						font=menu_font_type)
		self.oAppIProg.transformsubmenu.add_command(label='Rotate 90 Degrees CW',\
						command=self.rotate90CWCB,\
						font=menu_font_type)
		self.oAppIProg.transformsubmenu.add_command(label='Rotate 180 Degrees',\
						command=self.rotate180CB,\
						font=menu_font_type)
		

		#............... Loading of Matrix .........................................

		self.oAppIProg.BtnLoad.configure(command=self.loadCB)

		#............... Filter Operations ...........................................

		self.oAppIProg.BtnGauss.configure(command = self.vGaussianCB)

		self.oAppIProg.BtnUnsharp.configure(command = self.unsharpCB)
	
		self.oAppIProg.BtnHE.configure(command = self.vHistEqCB)

		self.oAppIProg.BtnBnC.configure(command = self.bnessCB)
		
		self.oAppIProg.BtnContrast.configure(command=self.contrastCB)	


		self.oAppIProg.BtnInvert.configure(command = self.invertCB)


		self.oAppIProg.BtnFourier.configure(command = self.fourierCB)


		self.oAppIProg.BtnNLT.configure(command = self.nltCB)


		self.oAppIProg.BtnRotate.configure(command = self.rotateCB)


		i = 4
		#............... Save As Operations .......................................... 
		self.oAppIProg.BtnSavePS.configure(command = self.savepsCB)

		self.oAppIProg.BtnZoom.configure(command = self.ZoomCB)

		self.oAppIProg.BtnQuit.configure(command = self.quitCB)

		self.ImWindow = None
		self.ImWindowCount = 0
		self.itsdump = False	
		self.sColorModeVar = StringVar()
		self.sColorModeVar.set(self.oToolBar.oImaging.strModeVar.get())
		self.vSetColorMode()
		self.nRotationVar=IntVar()		
		self.nRotationVar.set(0)
		self.oAppIProg.ipGroup.protocol('WM_DELETE_WINDOW',self.quitCB)	
		return


	def loadCB(self):
		"""
		Creates a window showing image
		Prompts user whether image has to be reapired or not
		"""
		try:
			[imat, fname] = self.readfromfile()
		except:
			return
		if fname:
			if re.findall(checkdmp, fname) and ((not(re.findall(checkscan,fname))) and (not(re.findall(checkret,fname)))):
				self.display(imat)
				return
		else:
			return
		if tkMessageBox.askyesno('Correct Slope', 'Do you want to correct slope?', parent=self.oAppIProg.ipGroup):
			repaired_imat = correctSlope(imat)
		else:
			repaired_imat = imat
		self.display(repaired_imat)
		return

	def vOpenScanWindow(self):
		"""
		Opens and Displays Image present on Scan Window 
		"""
		while self.oAppIProg.fileselect.get()!='Scan Window':
			self.oAppIProg.fileselect.invoke('buttondown')
		self.oAppIProg.BtnLoad.invoke()
		return

	def vOpenRetraceWindow(self):
		"""
		Opens and Displays Image present on Retrace Window 
		"""
		try:
			while self.oAppIProg.fileselect.get()!='Scan Window':
				self.oAppIProg.fileselect.invoke('buttondown')
		except:
			while self.oAppIProg.fileselect.get()!='Scan Window':
				self.oAppIProg.fileselect.invoke('buttonup')
		self.oAppIProg.BtnLoad.invoke()
		return

	def vOpenDumpImage(self):
		"""
		Prompts user to select ".dmp" image files located at "/usr/stm/dump" folder 
		"""
		try:
			while self.oAppIProg.fileselect.get()!='From Dump':
				self.oAppIProg.fileselect.invoke('buttonup')
		except:
			while self.oAppIProg.fileselect.get()!='From Dump':
				self.oAppIProg.fileselect.invoke('buttondown')
		self.oAppIProg.BtnLoad.invoke()
		return

	def vOpenFileImage(self):
		"""
		Opens and Displays a user select Image file 
		"""
		while self.oAppIProg.fileselect.get()!='File':
			self.oAppIProg.fileselect.invoke('buttonup')
		self.oAppIProg.BtnLoad.invoke()	
		return

	def vDisplayChoice(self):
		"""
		Selects Image Display mode RGB / Gray. 
		Default : Gray mode  
		"""
		self.oToolBar.oScanner.oMenuBar.oAppMenubar.imagesettingsmenu.invoke(1)
		self.vSetColorMode()
		return

	def vSetColorMode(self):
		"""
		If refreshes Image with new Color mode when changed
		"""
		if self.oToolBar.oImaging.strModeVar.get()=='I':
			self.sDisplayChoice='I'
		if self.oToolBar.oImaging.strModeVar.get()=='RGB':
			self.sDisplayChoice='RGB'
		if self.sColorModeVar.get()!=self.sDisplayChoice:
			self.display(self.current_matrix)
		self.sColorModeVar.set(self.sDisplayChoice)
		return

	def vCreateWindow(self, (row, col)):
		"""
		Creates an Image Window for displaying image 
		"""
		if not self.ImWindowCount:
			self.ImWindow = Toplevel(self.oAppIProg.ipGroup)
			self.ImWindow.title('Image Display')
			self.ArrCanvas = Canvas(self.ImWindow,width=row, height=col)
			self.ImWindow.protocol('WM_DELETE_WINDOW', self.cancelCB)
			self.ArrIm.paste(self.im)
	                self.ArrCanvas.create_image(0,0,image=self.ArrIm,anchor=NW)
			self.ArrCanvas.pack(side=TOP,anchor=NW)
			self.ImWindowCount += 1
		return

	def cancelCB(self):
		"""
		Destroys imaging window 
		"""
		self.ImWindow.destroy()
		self.ImWindowCount -=1
		return
		
	def quitCB(self):
		"""
		Quits I-Prog utility
		"""
		print 'Sayonara ... Mademoiselle'
		self.oAppIProg.ipGroup.destroy()
		self.oToolBar.iprog_Instance=0	
		return
		
	def readfromfile(self): 
		"""
		Selects file to be loaded
			--> Scan Window
			--> Retrace Window
			--> From dump folder
			--> From File
		"""
		choice = self.oAppIProg.fileselect.get() 
		if choice == 'From Dump':
		    (matrix, filename) = self.vOpenDump()
		if choice == 'Scan Window':
		    if self.vCheckImageWindow()==False:
				return 	
		    (matrix, filename) = self.vOpenScanDump(sfilename)
		if choice == 'Retrace Window':
		    if self.vCheckImageWindow()==False:
				return 	
		    (matrix, filename) = self.vOpenRetDump(rfilename)
		if choice == 'File':
		    (matrix, filename) = self.vOpenFile()
		return (matrix,filename)


	def vOpenDump(self):
		"""
		Extracts data from a ".dmp" file 
		"""
		fname = tkFileDialog.askopenfilename(defaultextension='.dmp', \
				initialdir=dumppath, title='Pick from Dump')
		if fname:
			f = open(fname) 
			self.current_file = fname
			print 'Curent file opened is: ', self.current_file
			imgmatrix = numpy.asarray(cPickle.load(f))
			try:
				self.dicImageDetails=cPickle.load(f)
			except:
				pass
			f.close()
			return (imgmatrix, fname)
		else:
			print 'Cant open file'
			tkMessageBox.showerror('File Error','Open a File', parent=self.oAppIProg.ipGroup)
			return (0,0)

	def vOpenScanDump(self, sfilename):
		"""
		Extracts data of image present on the Scan Window 
		"""
		f = open(sfilename)
		self.current_file = sfilename
		if f:
			try:						
				scanmat = numpy.asarray(cPickle.load(f))	
				self.dicImageDetails=cPickle.load(f)		
			except:							
				scanmatr=numpy.asarray(f.read())			
				scanmat=numpy.resize(scanmatr,[256,256])	
			f.close()						
			return (scanmat, sfilename)				
		else:
			tkMessageBox.showerror('File Error','Open Another File', parent=self.oAppIProg.ipGroup)
			return (0,0)


	def vOpenRetDump(self, rfilename):
		"""
		Extracts data of image present on the Retrace Window 
		"""
		f = open(rfilename)
		self.current_file = rfilename					
		if f:
			try:							
				retmat = numpy.asarray(cPickle.load(f))	
				try:
					self.dicImageDetails=cPickle.load(f)
				except:
					pass	
			except:							
				retmatr=numpy.asarray(f.read())			
				retmat=numpy.resize(retmatr,[256,256])		
			f.close()						
			return (retmat, rfilename)
		else:
			tkMessageBox.showerror('File Error','Open a File', parent=self.oAppIProg.ipGroup)
			return (0,0)

	def vOpenFile(self):
		"""
		Extracts data from a user select file 
		"""
		ftype=FILETYPES.values()
		filepath=dialogs.strPathTracker()
		fname = tkFileDialog.askopenfilename(initialdir=filepath, filetypes=ftype,title='Load File')
		if fname:
			f = open(fname) 
			self.current_file = fname
			print 'Curent file opened is: ', self.current_file
			dialogs.strPathTracker(fname)
			try:
				imgmatrix = numpy.asarray(cPickle.load(f))
				try:
					self.dicImageDetails=cPickle.load(f)
					print self.dicImageDetails
				except:
					pass
				try:
					self.dicImageDetails=cPickle.load(f)
					print self.dicImageDetails
				except:
					pass	
			except:
				i=0
				j=0
				self.dicImageDetails={}
				self.dicImageDetails['ImageSize']=int(f.readline())
				self.dicImageDetails['StepSize']=int(f.readline())
				nImageSize=int(f.readline())
				self.dicImageDetails['Delay']=int(f.readline())
				self.dicImageDetails['Gain']=int(f.readline())
				imgmatrix=numpy.zeros([nImageSize,nImageSize],'f')
				for i in range(nImageSize):
					for j in range(nImageSize):
						imgmatrix[i][j]=float(f.readline())
						f.readline()
				print self.dicImageDetails
			f.close()
			return (imgmatrix, fname)
		else:
			print 'Cant open file'
			tkMessageBox.showerror('File Error','Open a File', \
						parent=self.oAppIProg.ipGroup)
			return (0,0)

	def checkImWindow(self):
		"""
		Checks whether image is present on Imaging windows or not 
		"""
		if not self.ImWindowCount:
			tkMessageBox.showerror('Error','No Canvas Window present !!', \
						parent=self.oAppIProg.ipGroup)
			return False
		return True
		
	def vCheckImageWindow(self):
		"""
		Checks whether images are present on Scan & Retrace windows or not 
		"""
		if self.oToolBar.oImaging.bImagePresentVar.get()==False:
			tkMessageBox.showerror('Error','No Image present !!', parent=self.oAppIProg.ipGroup)
			return False
		else:
			return True	

	def savepsCB(self):
		"""
		Saves ".ps" file 
		"""
		if not self.checkImWindow():
			return
		fname = dialogs.SaveImageDialog('.ps', 'Do you want to save processoed image?', \
					parent = self.oAppIProg.ipGroup)
		if fname == None:
			return
		self.ArrCanvas.postscript(file = fname)
		return


	def display(self, arr, graychoice=True):
		"""
		Choice Between Gray or colored images
		"""
		if self.sDisplayChoice=='I':
			self.im = Im.new("I", arr.shape)
		if self.sDisplayChoice=='RGB':
			self.im = Im.new("RGB", arr.shape)
		self.ArrIm = ImageTk.PhotoImage(self.im)
		self.afImageMatrix = arr.copy()
		self.vCreateWindow(arr.shape)
		arr = float2gray(arr)		
		self.current_matrix = arr.copy()
	        self.ArrCanvas.create_image(0,0,image=self.ArrIm,anchor=NW)
		if self.sDisplayChoice=='I':
			self.im.putdata(arr.flat)
		if self.sDisplayChoice=='RGB':
			colmatrix=map(lambda(x):self.olut[int(x)],arr.flat)
			self.im.putdata(colmatrix)
		self.ArrIm.paste(self.im)
		self.ArrCanvas.config(width=arr.shape[1],height=arr.shape[0])
		self.ImWindow.update()
		return


	def invertCB(self):
		"""
		Inverts image matrix 
		"""
		if not self.checkImWindow():
			return
		self.invert_matrix = self.current_matrix.copy()
		result = invert(self.invert_matrix)
		self.display(result)
		if tkMessageBox.askyesno('Dump','Want to dump inversion result ?', parent=self.oAppIProg.ipGroup):
			f = open(invertdump,'w')
			cPickle.dump(result, f)
			cPickle.dump(self.dicImageDetails,f)	
			f.close()
		return
		
	def vGaussianCB(self):
		"""
		Launches Gaussian Blurring 
		"""
		if not self.checkImWindow():
			return
		oglur = gauss.gauss(self.oAppIProg.ipGroup,self.current_matrix,self.sDisplayChoice,self.olut,self.dicImageDetails)
		return

	def unsharpCB(self):
		"""
		Launches Unsharp Filtering 
		"""
		if not self.checkImWindow():
			return
		ounsharp = unsharp.unsharp(self.oAppIProg.ipGroup, self.current_matrix,self.sDisplayChoice,self.olut, self.dicImageDetails)
		return

	def vHistEqCB(self):
		"""
		Launches Histogram Equalization 
		"""
		if not self.checkImWindow():
			return
		ohisteq = histeq.histeq(self.oAppIProg.ipGroup, self.current_matrix, self.sDisplayChoice,self.olut, self.dicImageDetails)
		return     

	def bnessCB(self):
		"""
		 Launches Brightness filter 
		"""
		if not self.checkImWindow():
			return
		obness = bness.bness(self.oAppIProg.ipGroup, self.current_matrix, self.sDisplayChoice,self.olut,self.dicImageDetails)
		return

	def fourierCB(self):
		"""
		Launches Fourier Transform Filter 
		"""
		if not self.checkImWindow():
			return
		ofourier = fourier.fourier(self.oAppIProg.ipGroup, self.afImageMatrix, self.sDisplayChoice,self.olut,self.dicImageDetails)
		return

	def nltCB(self):
		"""
		Launches NLT Filter 
		"""
		if not self.checkImWindow():
			return
		onlt = nlt.nlt(self.oAppIProg.ipGroup, self.current_matrix, self.sDisplayChoice,self.olut, self.dicImageDetails)
		return

	def rotate90CCWCB(self):
		"""
		Rotates image 90 degree CCW 
		"""
		print 'Rotated 90 degrees CCW'
		self.nRotationVar.set(0)		# for 90 degrees CCW
		self.rotateCB()
		return	
		
	def rotate90CWCB(self):
		"""
		Rotates image 90 degree CW 
		"""
		print 'Rotated 90 degrees CW'
		self.nRotationVar.set(1)		# for 90 degrees CCW
		self.rotateCB()
		return	
		
	def rotate180CB(self):
		"""
		Rotates image 180 degree
		"""
		print 'Rotated 180 degrees'
		self.nRotationVar.set(2)		# for 90 degrees CCW
		self.rotateCB()
		return	
	
	def rotateCB(self):
		"""
		Rotates image matrix in step og 90 degrees 
		"""
		if not self.checkImWindow():
			return
		self.rot_matrix = self.current_matrix.copy()
		if self.nRotationVar.get()==0:	
			result = self.corerotate(self.rot_matrix)
		if self.nRotationVar.get()==1:	
			result = self.corerotate(self.rot_matrix)
			result = self.corerotate(result)
			result = self.corerotate(result)
		if self.nRotationVar.get()==2:	
			result = self.corerotate(self.rot_matrix)
			result = self.corerotate(result)
		self.display(result)
		if tkMessageBox.askyesno('Dump', 'Do you want to dump the rotated window ??', parent=self.oAppIProg.ipGroup):
			f = open(rotatedump,'w')
			cPickle.dump(self.current_matrix,f)
			cPickle.dump(self.dicImageDetails,f)
			f.close()
		self.nRotationVar.set(0)	
		return

	def corerotate(self,matrix,angle=90):
		"""
		Rotates image matrix by the specified angle  
		"""
		rotatedmatrix = crotate(matrix,angle)
		return rotatedmatrix

	def contrastCB(self):
		"""
		Launches Contrast filter
		"""
		if not self.checkImWindow():
			return
		oContrast = contrast.contrast(self.oAppIProg.ipGroup,self.current_matrix, self.sDisplayChoice,self.olut, \
					self.dicImageDetails)
		return

	def ZoomCB(self):
		"""
		Launches Image Zoom utility 
		"""
		if not self.checkImWindow():
			return
		oZoom = zoom.zoom(self.oAppIProg.ipGroup,self.current_matrix, self.sDisplayChoice,self.olut,self.dicImageDetails)
		return

from Tkinter import *
if __name__ == "__main__":
	iprog()
