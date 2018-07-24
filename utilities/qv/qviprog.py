
import os
import string
import numpy
import scipy.ndimage as im
import numpy.fft as fft

APP_PATH = '/usr/stm/SiM4.2.0'		# to run as independent module
if os.getcwd() != APP_PATH:
    sLUTPath = os.path.join('lut')	
else:
    sLUTPath = os.path.join('utilities', 'qv', 'lut')	

LUTFILE = os.path.join(sLUTPath, 'revdefault.lut')

def min_maxfilter(m, sigma=2.5):	
	"""
	It reduces the width of normal distribution.
	Min-max filter that replaces :
	  : every value which is less than minval by minval	
	  : every value which is greater then maxval by maxval	
	"""
	meanval = m.mean()
	stdval = m.std()
	minval = meanval - sigma*stdval
	maxval = meanval + sigma*stdval
	clipped = numpy.clip(m,minval,maxval)	
	return clipped

def repair(m):
	"""
	Slope-Thrasher is more saavy word ....  for Repair Filter !!
	"""
	newm = numpy.zeros((m.shape[0], m.shape[1]),'f')
	#print 'Treat X and Repair Y-slope ...'
	for i in range(m.shape[0]):
		mean = m[i].sum()/m[i].size*1.0
		newm[i] = m[i] - mean
		
	#print 'Treat Y and Repair X-slope ...'
	for i in range(m.shape[1]):
		mean = newm[:,i].sum()/newm[:,i].size*1.0
		newm[:,i] = newm[:,i] - mean
	#mean = newm[:,i].sum()/newm[i].nelements()*1.0
	#print 'new mean', mean
	return newm

def float2gray(m):
	"""
	Convert float image data into gray scale 0-255
	"""
	g = m - m.min()
	g = g*255/g.max()
	return g

def gray2rgb(graymatrix):
	"""
	Extracts data from LookUp table file
	"""
	f=open(LUTFILE,'r')
	f.readline()
	r=[]
	g=[]
	b=[]
	rgb=[]
	for i in range(256):
		tmp=f.readline()
		fPixelData=string.split(tmp," ")
		nGrayR=int(float(fPixelData[0])*255)
		nGrayG=int(float(fPixelData[1])*255)
		nGrayB=int(float(fPixelData[2])*255)
		r.append(nGrayR)
		g.append(nGrayG)
		b.append(nGrayB)
		rgb.append((nGrayR,nGrayG,nGrayB))
	try:
		ncolmatrix = map(lambda(x):rgb[int(x)],graymatrix.flat)
	except:
		print graymatrix
	return ncolmatrix

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

def correctXslope(m):
	"""
	Bring mean for each line along X to zero
	"""
	newm = numpy.zeros((m.shape[0], m.shape[1]),'f')
	#print 'Treat X and Repair Y-slope ...'
	for i in range(m.shape[0]):
		mean = m[i].sum()/m[i].size*1.0
		newm[i] = m[i] - mean
	return newm

def correctYslope(m):
	"""
	Bring mean for each line along X to zero
	"""
	newm = numpy.zeros((m.shape[0], m.shape[1]),'f')
	#print 'Treat Y and Repair X-slope ...'
	for i in range(m.shape[1]):
		mean = m[:,i].sum()/m[:,i].size*1.0
		newm[:,i] = m[:,i] - mean
	return newm

def gaussian_(m):
	"""
	Smoothens image matrix (Blur filter removes spec noise)
	"""
	# Gaussian ...
	gaussmat = im.filters.gaussian_filter(m, 1.1)
	return gaussmat

def fourierfilter(matrix, threshold, filterchoice='L'):
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
	return matrix

	return matrix

def coreHisteq(arr):
    """
    Histogram Equaluiztion
    """
    hist = vCalculateHistogram(arr)
    cum_hist = numpy.zeros(256)
    for i in range(256):
	cum_hist[i] = hist[:i+1].sum() 
    norm_hist = (255./arr.nelements()) * cum_hist
    histeqImg = numpy.take(norm_hist, arr)
    return histeqImg

def vCalculateHistogram(arr):
    """
    Real Histogram generation takes place here
    """
    hist = im.histogram(arr, 0, 256, 256)
    return hist
