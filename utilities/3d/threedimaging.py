####################
#   ThreeD Class   #
####################

from Tkinter import *
import os
import tkFileDialog
import numpy
try:
    import enthought.mayavi as mayavi
except:
    import mayavi
try:
    from enthought.mayavi import mlab
except:
    from mayavi import mlab
import tkMessageBox
import iprog
import dialogs
import scanner
import import_

SCAN = 0
RET = 1
FILE = 2

# from scanner.py
ZMODE	= 4
TCMODE	= 5

FILETYPES = {	'npic':('SiM Files','*.npic'), \
		}					# Stm Image file types

class ThreeD:

	def __init__(self,oImaging):
		"""
		Class Contructor
		"""
		self.oImaging=oImaging
		return

	def vOpenImage(self, nImgType):
		"""
		Open up a file for 3D viewing
		"""
		if nImgType == SCAN:
			self.vOpenScanImage()
		if nImgType == RET:
			self.vOpenRetImage()
		if nImgType == FILE:
			self.vOpenFile()
		return

	def vOpenScanImage(self):
		"""
		Displays image pressent on Scan Window
		"""
		if self.bCheckImage()==False:
			return
		fname = os.path.join(os.curdir, 'dump', 'scanimgdump.dmp')
		[s, d, blank] = import_.aafReadPicFile(fname)
		#nImageMatrix=iprog.float2gray(s)
		self.dicScanParam = d
		if self.dicScanParam.has_key('NoOfChannels'):
			noc = self.dicScanParam ['NoOfChannels']
		else:
			noc = 0
		if noc > 1:
			channel = 0
			s = s[0]	# The first channel (Topography Data)
			print '3D plot of', d['ChannelNames'][channel], 'Multi-Channel Image Data'
			print 'Multi-Channel Image Data', s.shape

		self.vShow(s)	
		return

	def vOpenRetImage(self):
		"""
		Displays image present on Retrace Window
		"""
		if self.bCheckImage()==False:
			return
		fname = os.path.join(os.curdir, 'dump', 'retimgdump.dmp')
		[r, d, blank] = import_.aafReadPicFile(fname)
		#nImageMatrix=iprog.float2gray(r)
		self.dicScanParam = d
		self.vShow(r)
		return

	def vOpenFile(self):
		"""
		Displays a User Selsct File
		"""
		ftype = FILETYPES.values()
		filepath = dialogs.strPathTracker()
		fname = tkFileDialog.askopenfilename(filetypes=ftype,initialdir=filepath)
		if fname == None:
		    return
		dialogs.strPathTracker(filepath)
		[s, r, d, type_] = import_.aafReadImageFile(fname)
		self.nImageSize = d['ImageSize'][0]
		self.dicScanParam = d
		#nImageMatrix = iprog.float2gray(s)
		if dicScanParam.has_key('NoOfChannels'):
			noc = dicScanParam ['NoOfChannels']
		if noc > 1:
			channel = 0
			s = s[0]	# The first channel (Topography Data)
			print '3D plot of', d['ChannelNames'][channel], 'Multi-Channel Image Data'
		self.vShow(s)
		return


	def vShow(self, nImageMatrix):
		"""
		Convets pic/dat image file to .vtk format
		Launches 3d tool mayavi and displays .vtk file
		"""
		mlab.figure(bgcolor=(0.5,0.5,0.5), fgcolor=(1,1,1))
		x, y = numpy.mgrid[0:nImageMatrix.shape[0], 0:nImageMatrix.shape[1]]
		x = x * (scanner.fGetPiezoXCalibration() / 1.0e3)
		y = y * (scanner.fGetPiezoXCalibration() / 1.0e3)
		z = (nImageMatrix - nImageMatrix.min()) * scanner.fGetPiezoZCalibration() / 1.0e3
		if self.dicScanParam['DigitizationMode'] == ZMODE:
		    print 'CC-Mode Image, scaled by HVA Gain'
		    z *= scanner.fGetHVAGain()
		zspan = nImageMatrix.max() - nImageMatrix.min()
		warp_ratio = zspan / nImageMatrix.shape[1]
		#if warp_ratio > 0.6:
		#    print 'Scaling Z view ...'
		#    mlab.contour_surf(x, y, z, contours=80, colormap='autumn', warp_scale=0.3)
		#else:
		mlab.contour_surf(x, y, z, contours=80, colormap='autumn')
		mlab.xlabel('X (nm)')
		mlab.ylabel('Y (nm)')
		mlab.zlabel('Z (nm)')
		#mlab.title('nanoREV 3D STM Images')
		mlab.show()
		return

	def bCheckImage(self):
		"""
		Checks Whether image is present on Scan and Retrace window or not
		"""
		if self.oImaging.bImagePresentVar.get()==False:
			tkMessageBox.showerror('Error','No Image to Display')
			return False	
		else:
			return True

