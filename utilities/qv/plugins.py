from PIL import Image, ImageTk
import numpy
import os
import cPickle

import qviprog 

OXDAC   = 0
XDAC	= 1
OYDAC	= 2
YDAC	= 3
OZDAC	= 4
BIASDAC = 5
BIGXDAC	= 6
BIGYDAC	= 7 


def picdecoder(filename):
	return aafReadPicFile(filename)

def datdecoder(filename):
	return aafReadDatFile(filename)

def dmpdecoder(filename):
	return aafReadPicFile(filename)
		
def stddecoder(filename):
	return aafReadStdFile(filename)	

def aafReadPicFile(filename):
	"""
	Reads .pic files and returns scan image data, retrace image data and dictionary containing scan parameters
	"""
	fd = open(filename)
	try:
	    s = cPickle.load(fd)
	except:
	    s = None
	    pass
	try:
	    r = cPickle.load(fd)
	except:
	    r = None
	    pass
	try:
	    p = cPickle.load(fd)
	    #print 'Scan Param', p 
	except:
	    p = None
	    pass
	fd.close()
	return [s, r, p]

def aafReadDatFile(filename):
	"""
	Reads .dat files and returns scan image data, retrace image data and scan parameters 
	"""
	p = {}
	scan_pixel_list = []
	ret_pixel_list = []
	fd = open(filename,'r')

	isize = fd.readline()
	if isize.find('#') == 0:
	    fd.close()
	    srd = aafReadOldDatFile(filename)
	    return [srd[0], srd[1], srd[2]]	    
	ImageSize = p['ImageSize'] = [int(isize)]
	ssize = fd.readline()
	p['StepSize'] = [int(ssize)] * 2
	isize = fd.readline()
	p['ImageSize'].append(int(isize))
	delay = fd.readline()	
	p['Delay'] = float(delay)
	area =  fd.readline()
	dac_choice = p['Area'] = int(float(area))
	ImageSize = p['ImageSize'][0]
	CurrentImageSize = p['ImageSize'][1]
	for pixel in range(ImageSize*CurrentImageSize):
		scan_pixel_list.append(float(fd.readline()))
		ret_pixel_list.append(float(fd.readline()))
	fd.close()
	if dac_choice == XDAC or dac_choice == BIGXDAC:
		ScanImg = []
		RetImg = []
		arr = numpy.array(scan_pixel_list)
		ScanImg = numpy.reshape(arr, (CurrentImageSize,ImageSize))
		arr = numpy.array(ret_pixel_list)
		RetImg = numpy.reshape(arr, (CurrentImageSize,ImageSize))
		RetImg = RetImg[:,::-1].copy()
		print RetImg.shape
	if dac_choice == YDAC or dac_choice == BIGYDAC:
		ScanImg = []
		RetImg = []
		arr = numpy.array(scan_pixel_list)
		ScanImg = numpy.reshape(arr, (CurrentImageSize, ImageSize))
		arr = numpy.array(ret_pixel_list)
		RetImg = numpy.reshape(arr, (CurrentImageSize, ImageSize))
		RetImg = RetImg[:,::-1].copy()
		print RetImg.shape 
	return [qviprog.float2gray(ScanImg), qviprog.float2gray(RetImg), p]

def aafReadOldDatFile(filename):
	"""
	Plugin for Old gnuplot compatible dat files
	"""
	p = {}
	fd = open(filename,'r')
	isize = fd.readline()
	isize = isize.replace('#','')				#getting rid of comment for gnuplots
	ImageSize = p['ImageSize'] = [int(isize)]

	ssize = fd.readline()
	ssize = ssize.replace('#','')
	p['StepSize'] = [int(ssize)] * 2
	
	isize = fd.readline()
	isize = isize.replace('#','')
	p['ImageSize'].append(int(isize))

	delay = fd.readline()	
	delay = delay.replace('#','')
	p['Delay'] = float(delay)

	area =  fd.readline()
	area = area.replace('#','')
	dac_choice = p['Area'] = int(float(area))
	ImageSize = p['ImageSize'][0]
	CurrentImageSize = p['ImageSize'][1]
	
	fd.close()
	return [s, r, d]

def aafReadStdFile(filename):
	dicparam = {}
	im = Image.open(filename)
	dicparam['ImageSize'] = im.size
	if dicparam['ImageSize'][0] > 256 or dicparam['ImageSize'][1] > 256: 
	    im = im.resize((256,256))
	return [im, dicparam]
