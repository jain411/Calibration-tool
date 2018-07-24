import os
import numpy
import cPickle
import offset	

def aafReadPicFile(filename):
	"""
	Function : aafReadPicFile
		Reads ".pic" files and returns scan image data, retrace image data and dictionary containing scan parameters

	Arguments :
		filename : string image filename

	Returns :
		s : float scan image data
		r : float retrace image data
		p : dictionary containing scan parameters
	"""
	fd = open(filename)
	try:
	    s = cPickle.load(fd)
	except:
	    s=None
	try:
	    r = cPickle.load(fd)
	except:
	    r=None	
	try:
	    p = cPickle.load(fd)
	    #print 'Scan Param', p
	except:
	    p=None		
	fd.close()
	return [s, r, p]

def aafReadDatFile(filename):
	"""
	Function : aafReadDatFile
		Reads ".dat" files and returns scan image data, retrace image data and scan parameters 

	Arguments :
		filename : string filename

	Returns :
		ScanImg : float scan image data
		RetImg  : float retrace image data
		p       : dictionary containing scan parameters
	"""
	p = {}
	scan_pixel_list = []
	ret_pixel_list = []
	fd = open(filename,'r')
	ImageSize = p['ImageSize'] = [int(float(fd.readline()))]
	p['StepSize'] = [int(fd.readline())] * 2
	p['ImageSize'].append(int(float(fd.readline())))
	p['Delay'] = int(float(fd.readline()))
	dac_choice = p['Area'] = int(float(fd.readline()))
	ImageSize = p['ImageSize'][0]
	CurrentImageSize = p['ImageSize'][1]
	for pixel in range(ImageSize*CurrentImageSize):
		scan_pixel_list.append(float(fd.readline()))
		ret_pixel_list.append(float(fd.readline()))
	fd.close()
	if dac_choice == offset.XDAC or dac_choice == offset.BIGXDAC:
		ScanImg = []
		RetImg = []
		arr = numpy.array(scan_pixel_list)
		ScanImg = numpy.reshape(arr, (CurrentImageSize,ImageSize))
		arr = numpy.array(ret_pixel_list)
		RetImg = numpy.reshape(arr, (CurrentImageSize,ImageSize))
		RetImg = RetImg[:,::-1].copy()
	if dac_choice == offset.YDAC or dac_choice == offset.BIGYDAC:
		ScanImg = []
		RetImg = []
		arr = numpy.array(scan_pixel_list)
		ScanImg = numpy.reshape(arr, (CurrentImageSize, ImageSize))
		arr = numpy.array(ret_pixel_list)
		RetImg = numpy.reshape(arr, (CurrentImageSize, ImageSize))
		RetImg = RetImg[:,::-1].copy()
	return [ScanImg, RetImg, p]

def aafReadImageFile(filename):
	"""
	Function : aafReadImageFile
		Checks for ".pic", ".dat" and ".dmp" files and returns scan image data, retrace image data and scan parameters

	Arguments :
		filename : string filename

	Returns :
		s : float scan image data
		r : float retrace image data
		p : dictionary containing scan parameters
	"""
	ext = os.path.splitext(filename)[1]
	if ext == '' or ext == None:
		print 'Unrecognized format ... '
		return None
	if ext == '.npic':
		[s, r ,p] = aafReadPicFile(filename)
		return [s, r, p, "npic"]
	if ext == 'pic':
		[s, r ,p] = aafReadPicFile(filename)
		if p is None:
			return[s,p,r,"dmp"]
		return [s, r, p, "pic"]
	if ext == 'dmp':
		[s, p ,r] = aafReadPicFile(filename)
		return [s, r, p, "dmp"]
	if ext == 'dat':
		[s, r, p] = aafReadDatFile(filename)
		if r.sum()==0:
			return[s,r,p,'dmp']
		return [s, r, p, "dat"]
	return None

