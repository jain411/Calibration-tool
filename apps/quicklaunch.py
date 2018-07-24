###########################
#   QuickLaunch Class     #
###########################

import tkFileDialog, tkMessageBox
from Tkinter import *
import cPickle
import os

import iprog
import histeq
import tiploc
import canvaszoom
import irough
import dialogs

dumppath 	 = os.path.join(os.curdir, 'dump')	# default directory  containing ".dmp" files
sfilename	 = os.path.join(dumppath, 'scanimgdump.dmp')	# Scan image file path
rfilename	 = os.path.join(dumppath, 'retimgdump.dmp')	# Retrace image file path

HORZ 		= 2
VERT 		= 3

def quicklaunch (oImaging):
	"""
	Returns QuickLaunch object
	"""
	oQL=QuickLaunch(oImaging)
	return oQL

class QuickLaunch:

	def __init__(self, oImaging):
		"""
		Class Contructor : QuickLaunch
		"""
		#print 'QLMenu object formed'
		self.oImaging = oImaging	
		self.oAppImaging = oImaging.oAppImaging
		self.vCreateQlMenu ()
		self.vConfigureCB ()
		self.vInitQLaunch ()
		return

	def vCreateQlMenu(self):
		"""
		Creates Quicklaunch menu widget
		"""
		self.QlaunchMenu = Menu(self.oAppImaging.iwGroup,tearoff=0)
		return
		

	def vConfigureCB(self):
		"""
		Binds mouse button to the Imaging window
		"""
		self.oAppImaging.CanvasScan.bind('<Button-3>', self.vQlaunchMenuCB)
		self.oAppImaging.CanvasRetrace.bind('<Button-3>', self.vQlaunchMenuCB)
		self.vConfigureQLMenu()
		# ConvertTo Polar deactivated  
		self.QlaunchMenu.entryconfig(15, state = DISABLED) 
		return
	
	def vInitQLaunch(self):
		"""
		Initializes Zoom and QuickLaunch status (i.e. which is
		used to  check if there exists an unzoomed image on the canvas)
		variables.
		"""
		self.bQlaunchVar = BooleanVar ()
		self.bQlaunchVar.set (False)
		self.bZoomVar = BooleanVar ()
		self.bZoomVar.set (False)
		self.bPolarizedVar = BooleanVar()
		self.bPolarizedVar.trace('w', self.polarMenuConfig)
		self.bPolarizedVar.trace('r', self.polarMenuConfig)
		self.bPolarizedVar.set(False)
		return

	def vConfigureQLMenu(self):
		"""
		Populates Quicklaunch menu
		"""
		self.QlaunchMenu.add_command(label='Min-Max Filter', command=self.vFilterCB)

		self.CorrectSlopeMenu = Menu(self.QlaunchMenu, tearoff = 0)
		self.QlaunchMenu.add_cascade(label='Correct Slope', menu=self.CorrectSlopeMenu)
		self.CorrectSlopeMenu.add_command(label='Along X (Horz)', command=self.vCorrectXCB)
		self.CorrectSlopeMenu.add_command(label='Along Y (Vert)', command=self.vCorrectYCB)
		self.CorrectSlopeMenu.add_command(label='Along X & Y', command=self.vRepairCB)

		self.CorrectZ_DriftMenu = Menu(self.QlaunchMenu, tearoff = 0)
		self.QlaunchMenu.add_cascade(label='Correct Z-Drift', menu=self.CorrectZ_DriftMenu)
		self.CorrectZ_DriftMenu.add_command(label='Along X (Horz)', command=self.correctZ_DriftX_CB)
		self.CorrectZ_DriftMenu.add_command(label='Along Y (Vert)', command=self.correctZ_DriftY_CB)
		self.CorrectZ_DriftMenu.add_command(label='Along X & Y', command=self.correctZ_DriftXY_CB)

		self.QlaunchMenu.add_command(label='Smoothen', command=self.vSmoothenCB)
		self.QlaunchMenu.add_command(label='Scratch Removal', command=self.vScratchRemovalCB)
		self.QlaunchMenu.add_command(label='Contrast', command=self.vContrastCB)
		self.QlaunchMenu.add_command(label='Invert', command=self.vInvertCB)
		self.QlaunchMenu.add_command(label='FourierLPF', command=self.vFourierFilterCB)
		self.QlaunchMenu.add_command(label='Background Sub', command=self.vBgSubCB)
		self.QlaunchMenu.add_command(label='Zoom', command=self.vZoomCB)
		self.QlaunchMenu.add_command(label='Save Current', command=self.vSaveCB)
		
		self.SaveAsMenu = Menu(self.QlaunchMenu, tearoff = 0)
		self.QlaunchMenu.add_cascade(label='Save As', menu=self.SaveAsMenu)
		self.SaveAsMenu.add_command(label='Save As JPG', command = self.vSaveAsJPGCB)
		self.SaveAsMenu.add_command(label='Save As PS', command = self.vSaveAsPSCB)

		self.QlaunchMenu.add_command(label='Original', command=self.vOriginalCB)
		self.QlaunchMenu.add_command(label='Roughness Level', command=self.vIRoughCB)
		self.QlaunchMenu.add_command(label='Relocate Tip', command=self.vRelocateTipCB)
		self.QlaunchMenu.add_command(label = 'Convert To Polar', \
						command = self.vConvertToPolarCB)
		return

	def polarMenuConfig(self, *args):
		if self.bPolarizedVar.get() == False:
			try:
				if self.NoOfChannels > 1:
					self.QlaunchMenu.entryconfig(15, state = NORMAL) 
			except:
				self.QlaunchMenu.entryconfig(15, state = DISABLED) 
		else:
			self.QlaunchMenu.entryconfig(15, state = DISABLED) 
			
		return

	def vQlaunchMenuCB (self,event):
		"""
		Callback for QuickLaunch Menu
		"""
		if self.oImaging.bImagePresentVar.get()==True:
			try:
				self.QlaunchMenu.tk_popup(event.x_root, event.y_root,0)
			finally:
				self.QlaunchMenu.grab_release()
			self.vAcquireImageData()
			self.bPolarizedVar.get()
			self.bQlaunchVar.set(False)
		return

	def vAcquireImageData(self):
		"""
		Acquire data only once when quick launched is invoked for a particular image
		"""
		f = open(sfilename)
		self.afOrigScanData = cPickle.load(f)
		f.close()
		f = open(rfilename)
		self.afOrigRetData = cPickle.load(f)
		f.close()
		if self.bQlaunchVar.get() == True:
			self.afScanImage = self.oImaging.afScanImageData
			try:
				self.afRetImage = self.oImaging.afRetImageData
			except:
				self.afRetImage = None
		self.vAcquireImageParam()	
		return

	def vAcquireImageParam(self):
		"""
		Get image parameters from the images
		"""
		try:
			self.nImageSize = self.oImaging.dicScanParam['ImageSize'][0]
			self.nStepSize = self.oImaging.dicScanParam['StepSize'][0]
			self.nDelay =self.oImaging.dicScanParam['Delay']
			self.nADCGain = self.oImaging.dicScanParam['Gain']
		except:
			print 'Parameter Error'
			pass
		if self.oImaging.dicScanParam.has_key('NoOfChannels'):
			self.NoOfChannels = self.oImaging.dicScanParam['NoOfChannels'] 
		else:
			self.NoOfChannels = 1
		if self.oImaging.dicScanParam.has_key('XLArea'):
			if self.oImaging.dicScanParam['XLArea']:
				self.bXLArea = True
			else:
				self.bXLArea = False
		else:
			self.bXLArea = False
		return

	def vFilterCB(self):
		"""
		Invokes iprog to perform min-max image filtering
		"""
		self.afScanImage = iprog.min_maxfilter(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.min_maxfilter(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return

	def vCorrectXCB(self):
		"""
		Corrects the Vertical(Top to Bottom) Gradient 
		"""
		print 'Fix Vertical(Top to Bottom) Gradient' 
		self.afScanImage = iprog.correctXslope(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.correctXslope(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return

	def vCorrectYCB(self):
		"""
		Corrects the Horizontal(Left to Right) Gradient 
		"""
		print 'Fix Horizontal(Left to Right) Gradient' 
		self.afScanImage = iprog.correctYslope(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.correctYslope(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return

	def vRepairCB(self):
		"""
		Corrects the both Horizontal(Left to Right) Gradient 
		and Vertical(Top to Bottom) Gradient 
		"""
		self.afScanImage = iprog.correctSlope(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.correctSlope(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return


	def correctZ_DriftX_CB(self):
		"""
		Corrects offsets due to Z drifts along X: Horizontal(Left to Right)
		"""
		self.afScanImage = iprog.correctZ_DriftX(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.correctZ_DriftX(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return


	def correctZ_DriftY_CB(self):
		"""
		Corrects offsets due to Z drifts along Y: Vertical(Top to Bottom)
		"""
		self.afScanImage = iprog.correctZ_DriftY(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.correctZ_DriftY(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return


	def correctZ_DriftXY_CB(self):
		"""
		Corrects offsets due to Z drifts in both Horizontal(Left to Right) & 
		and Vertical(Top to Bottom) i.e X & Y directions
		"""
		self.afScanImage = iprog.correctZ_DriftXY(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.correctZ_DriftXY(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return


	def vSmoothenCB(self):
		"""
		Invokes Gaussian Blurring for image smoothening
		"""
		self.afScanImage = iprog.gaussian_(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.gaussian_(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return

	def vContrastCB(self):
		"""
		Does Contrast alteration Using Histogram Equalization
		"""
		"""hist works fine with gray data only , so float image matrix isnt updated with hist filtered data """
		newscan = histeq.coreHisteq(iprog.float2gray(self.afScanImage))
		self.oImaging.vRenewScanImage(newscan)
		if self.oImaging.bDumpVar.get()==False:
			newret  = histeq.coreHisteq(iprog.float2gray(self.afRetImage))
			self.oImaging.vRenewRetImage(newret)
		self.vUpdateInfo()
		return	

	def vScratchRemovalCB(self):
		"""
		Removes Scratch along the direction of the scan
		"""
		if self.oImaging.dicScanParam['Direction'] == self.oImaging.oScanner.HORIZONTAL:
			axis = 'H'
		else: 
			axis = 'V'
		self.afScanImage = iprog.scratchRemoval(self.afScanImage, axis)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage = iprog.scratchRemoval(self.afRetImage, axis)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return


	def vInvertCB(self):
	    """
	    Inverts image pixels
	    """
	    if len (self.afScanImage.shape) == 2:
		self.afScanImage = iprog.invert(self.afScanImage)
		#self.oImaging.RGB.reverse()
		#self.oImaging.vInsertColorStrip()
		self.oImaging.vRenewScanImage(iprog.float2gray(self.afScanImage))
		if self.oImaging.bDumpVar.get()==False:
		    self.afRetImage = iprog.invert(self.afRetImage)
		    self.oImaging.vRenewRetImage(iprog.float2gray(self.afRetImage))
		self.vUpdateInfo()
	    else:
		self.oImaging.vRenewScan (iprog.invert (self.afScanImage), self.oImaging.dicScanParam, \
						bDump = False, noc = self.afScanImage.shape [0])
		self.oImaging.vRenewRet (iprog.invert (self.afRetImage), self.oImaging.dicScanParam, \
						bDump = False, noc = self.afScanImage.shape [0])
		self.vUpdateInfo()
	    return


	def vFourierFilterCB(self):
		"""
		Invokes Fourier LPF for image smoothening
		"""
		threshold = 1.0#2.0
		self.afScanImage = iprog.fourierfilter(self.afScanImage, threshold)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.fourierfilter(self.afRetImage, threshold)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return

	def vBgSubCB(self):
		"""
		Remove the slow variations in the background 
		to extact finer details of atomic resolution
		"""
		if self.oImaging.dicScanParam['Direction'] == HORZ:
		    self.afScanImage = iprog.afBgSubH(self.afScanImage)
		    self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		    if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.afBgSubH(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		if self.oImaging.dicScanParam['Direction'] == VERT:
		    self.afScanImage = iprog.afBgSubV(self.afScanImage)
		    self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		    if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.afBgSubV(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		return



	def vZoomCB(self):
		"""
		Enables image zoom in	
		"""
		self.oCZoom=canvaszoom.canvaszoom(self)
		self.vUpdateInfo()
		return

	def vSaveCB(self):
		"""
		Saves Current Image Present on the ImageCanvas
		"""
		dicScanParam = self.oImaging.dicScanParam.copy()
		try: 
		    fZoomFactor = self.oCZoom.nInfoImageSize/self.nImageSize
		    dicScanParam['StepSize'] = [int(self.nStepSize*fZoomFactor)]*2 
	    	except:
		    dicScanParam['StepSize'] = [self.nStepSize]*2
		self.oImaging.oScanner.vSaveImages(self.afScanImage,self.afRetImage, dicScanParam)
		return


	def strGetSaveAsFilename(self, initialfile = 'untitled'):
		filepath = dialogs.strPathTracker()
		fname = tkFileDialog.asksaveasfilename(initialdir=filepath, initialfile=initialfile, title='Load File')
		if not fname:
		    return None
		dialogs.strPathTracker(fname)
		return fname

	
	def vSaveAsPSCB(self):
		fname =self.strGetSaveAsFilename()
		if fname == None:
			return

		self.vSaveAsPS(fname)
		return

	def vSaveAsJPGCB(self):
		"""
		Saves Current Image Present on the ImageCanvas as .jpg file
			--> filenames : *scan.jpg , *ret.jpg
		"""
		fname = self.strGetSaveAsFilename()
		if fname == None:
			return

		self.vSaveAsPS(fname)

		if len(self.afScanImage.shape) == 2:
	    	    cmd = 'convert -density 400' + ' "' + fname+'scan.ps' + '" -resize 25% -quality 92 "' + fname+'scan.jpg"'
		    os.popen (cmd)
	    	    cmd = 'convert -density 400' + ' "' + fname+'ret.ps' + '" -resize 25% -quality 92 "' + fname+'ret.jpg"'
		    os.popen (cmd)
	    	    cmd = 'convert -density 400' + ' "' + fname+'lut.ps' + '" -resize 25% -quality 92 "' + fname+'lut.jpg"'
		    os.popen (cmd)
		    # Removing the temp. ps file
		    os.remove (fname + 'scan.ps')
		    os.remove (fname + 'ret.ps')
		    os.remove (fname + 'lut.ps')
		else:
		    for count in range (self.oImaging.dicScanParam['NoOfChannels']):
			cmd = 'convert -density 400' + ' "' + fname + str (count) + 'scan.ps' + '" -resize 25% -quality 92 "' + fname + str (count) + 'scan.jpg"'
			os.popen (cmd)
			cmd = 'convert -density 400' + ' "' + fname + str (count) + 'ret.ps' + '" -resize 25% -quality 92 "' + fname + str (count) + 'ret.jpg"'
			os.popen (cmd)
			# Removing the temp. ps file
			os.remove (fname + str (count) + 'scan.ps')
			os.remove (fname + str (count) + 'ret.ps')

		print 'JPG file saved'
		return


	def vSaveAsPS(self, fname):

		if len(self.afScanImage.shape) == 2:
		    self.oAppImaging.CanvasScan.postscript (file = fname + 'scan.ps')
		    self.oAppImaging.CanvasColor.postscript (file = fname + 'lut.ps')
		    if self.oImaging.bDumpVar.get () == False:
			self.oAppImaging.CanvasRetrace.postscript (file = fname + 'ret.ps')
		else:
		    for count in range (self.oImaging.dicScanParam['NoOfChannels']):
			self.oImaging.CanChannelScanFloat [count].postscript (file = fname + str (count) + 'scan.ps')
			self.oImaging.CanChannelRetFloat [count].postscript (file = fname + str (count) + 'ret.ps')

		print 'Postscript Image files saved...'
		return


	def vOriginalCB(self):
		"""
		Displays unfiltered original scan and retrace images
		"""
		self.afScanImage = self.afOrigScanData
		
		if len(self.afScanImage.shape) == 2:
		    self.oImaging.vRenewScanImage(iprog.float2gray(self.afScanImage))
		    if self.oImaging.bDumpVar.get()==False:
			self.afRetImage = self.afOrigRetData
			self.oImaging.vRenewRetImage(iprog.float2gray(self.afRetImage))
		    try:
			self.oImaging.afScanImageData=self.afOrigScanData
			self.oImaging.afRetImageData=self.afOrigRetData
		    except:
			pass
		else:
		    self.oImaging.vRenewScan (self.afOrigScanData, self.oImaging.dicScanParam, \
						bDump = False, noc = self.afScanImage.shape [0])
		    self.oImaging.vRenewRet (self.afOrigRetData, self.oImaging.dicScanParam, \
						bDump = False, noc = self.afScanImage.shape [0])
		    self.afScanImage = self.afOrigScanData
		    self.afRetImage = self.afOrigRetData
		    try:
			self.oImaging.afScanImageData = self.afOrigScanData
			self.oImaging.afRetImageData = self.afOrigRetData
		    except:
			pass

		self.vAcquireImageParam ()
		### Image Size from previous zoom is clear below ### 
		try:
			self.oCZoom.nInfoImageSize = self.nImageSize
		except:
			pass
		self.vUpdateInfo ()
		self.bZoomVar.set (False)
		self.bPolarizedVar.set(False)
		return

	def vIRoughCB(self):
		"""
		Displays Image Roughness
		"""
		try:
		    if self.nADCGain == None:
			self.nADCGain = 1
		except:
		    self.nADCGain = 1
		oIRough=irough.irough(self,self.oImaging, self.nADCGain)
		return

	def vRelocateTipCB(self):
		"""
		Moves Tip to location Specified by the user by clicking on the desired area over the image
		"""
		tiploc.tiploc(self.oImaging,self.oImaging.oScanner,self)
		return

	def vConvertToPolarCB(self):
		"""
		Invokes iprog to perform min-max image filtering
		"""
		self.afScanImage = iprog.convert2polar(self.afScanImage)
		self.oImaging.vRenewScan(self.afScanImage, self.oImaging.dicScanParam, False)
		if self.oImaging.bDumpVar.get()==False:
			self.afRetImage  = iprog.convert2polar(self.afRetImage)
			self.oImaging.vRenewRet(self.afRetImage, self.oImaging.dicScanParam, False)
		self.vUpdateInfo()
		self.bPolarizedVar.set(True)
		return

	def vUpdateInfo(self):
	    """
	    Update Image Info after quick-launch image processing.
	    """
	    try: 
		nImageSize = self.oCZoom.nInfoImageSize 
	    except:
		nImageSize = self.nImageSize
	    try:
	        self.oImaging.oScanner.vShowInfo(nImageSize, self.nStepSize, self.nDelay, bXLArea=self.bXLArea)
	    except:
		print 'Info Display Error'
		pass
	    self.oImaging.oScanner.vShowScaleInfo()
	    return
	


