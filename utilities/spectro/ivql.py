###########################
#   QuickLaunch Class     #
###########################

from Tkinter import *
import tkFileDialog
import os

import iprog
import histeq
import tiploc

HORZ 		= 2
VERT 		= 3

def ivql(oSpectro):
	"""
	Function : quicklaunch
		Returns QuickLaunch object

	Arguments :
 		oSpectro : object of class IVSpectroscopy

	Returns :
		oql : object of class quicklaunch
	"""
	oQL=QuickLaunch(oSpectro)
	return oQL

class IVQL:

    def __init__(self, oSpectro):
	"""
	Class Contructor
	"""
	#print 'QLMenu object formed'
	self.oSpectro = oSpectro
	self.oAppSpectro = oSpectro.oAppSpectro
	self.vCreateQLMenu()
	self.vConfigureCB()
	return

    def vCreateQLMenu(self):
	"""
	Creates Quicklaunch menu widget
	"""
	self.QLaunchMenu = Menu(self.oAppSpectro.sGroup,tearoff=0)
	return
		

    def vConfigureCB(self):
	"""
	Binds mouse button to the Imaging window
	"""
	self.oAppSpectro.CanvasSpectroMap.bind('<Button-3>', self.vQLaunchMenuCB)
	self.vConfigureQLMenu()
	return
	
    def vAcquireData(self, afGridData):
	"""
	Get the latest data splashed in the grid box of the IV spectroscopy main window
	"""
	# Acquire Grid Data
	self.afGridData = afGridData.copy()
	self.afOrigGridData = afGridData.copy()
	self.nImageSize = self.oSpectro.dicSpecParam['GridSize']
	return

    def vConfigureQLMenu(self):
	"""
	Populates Quicklaunch menu
	"""
	self.QLaunchMenu.add_command(label='Min-Max Filter', command=self.vFilterCB)
	self.QLaunchMenu.add_command(label='Correct XSlope ', command=self.vCorrectXCB)
	self.QLaunchMenu.add_command(label='Correct YSlope', command=self.vCorrectYCB)
	self.QLaunchMenu.add_command(label='Correct XYSlope', command=self.vRepairCB)
	self.QLaunchMenu.add_command(label='Smoothen', command=self.vSmoothenCB)
	self.QLaunchMenu.add_command(label='Contrast', command=self.vContrastCB)
	self.QLaunchMenu.add_command(label='Invert', command=self.vInvertCB)
	self.QLaunchMenu.add_command(label='FourierLPF', command=self.vFourierFilterCB)
	self.QLaunchMenu.add_command(label='Background Sub', command=self.vBgSubCB)
	self.QLaunchMenu.add_command(label='Save Current', command=self.vSaveCB)
	self.QLaunchMenu.add_command(label='Save As JPG', command=self.vSaveAsJPGCB)
	self.QLaunchMenu.add_command(label='Original', command=self.vOriginalCB)
	return

    def vQLaunchMenuCB(self, event):
	"""
	Display QuickLaunch Menu
	"""
	try:
	    self.QLaunchMenu.tk_popup(event.x_root, event.y_root,0)
	finally:
	    self.QLaunchMenu.grab_release()
	return

    def vFilterCB(self):
        """
        Invokes iprog to perform min-max image filtering
        """
        self.afGridData = iprog.min_maxfilter(self.afGridData)
        self.oSpectro.vSplashGridImage(self.afGridData)
        return

    def vCorrectXCB(self):
        """
        Corrects the Vertical(Top to Bottom) Gradient 
        """
        #print 'Fix Vertical(Top to Bottom) Gradient' 
        self.afGridData = iprog.correctXslope(self.afGridData)
        self.oSpectro.vSplashGridImage(self.afGridData)
        return

    def vCorrectYCB(self):
        """
        Corrects the Horizontal(Left to Right) Gradient
        """
        #print 'Fix Horizontal(Left to Right) Gradient' 
        self.afGridData = iprog.correctYslope(self.afGridData)
        self.oSpectro.vSplashGridImage(self.afGridData)
        return

    def vRepairCB(self):
        """
        Corrects the both Horizontal(Left to Right) Gradient 
        and Vertical(Top to Bottom) Gradient 
        """
        self.afGridData = iprog.correctSlope(self.afGridData)
        self.oSpectro.vSplashGridImage(self.afGridData)
        return

    def vSmoothenCB(self):
        """
        Invokes Gaussian Blurring for image smoothening
        """
        self.afGridData = iprog.gaussian_(self.afGridData)
        self.oSpectro.vSplashGridImage(self.afGridData)
        return

    def vContrastCB(self):
        """
        Does Contrast alteration Using Histogram Equalization
        hist works fine with gray data only , so float
        image matrix isnt updated with hist filtered data
        """
        newscan = histeq.coreHisteq(iprog.float2gray(self.afGridData))
        self.oSpectro.vSplashGridImage(newscan)
        return	

    def vInvertCB(self):
        """
        Inverts image pixels
        """
        self.afGridData = iprog.invert(self.afGridData)
        self.oSpectro.vSplashGridImage(iprog.float2gray(self.afGridData))
        return

    def vFourierFilterCB(self):
        """
        Invokes Fourier LPF for image smoothening
        """
        threshold = 1.0#2.0
        self.afGridData = iprog.fourierfilter(self.afGridData, threshold)
        self.oSpectro.vSplashGridImage(self.afGridData)
        return

    def vBgSubCB(self):
        """
        Remove the slow variations in the background 
        to extact finer details of atomic resolution
        """
        tkMessageBox.showinfo( 'Busy', 'Please click OK and wait for \n 4-5 sec for the results')
        self.afGridData = iprog.afBgSubH(self.afGridData)
        self.oSpectro.vSplashGridImage(self.afGridData)
        self.vUpdateInfo()
        return

    def vZoomCB(self):
        """
        Enables image zoom in	
        """
	if self.bZoomVar.get() == True:
            tkMessageBox.showerror('Zoom Warning', 'For accurate results, please use original image for zooming again')
            return
        self.oCZoom=qvcanvaszoom.canvaszoom(self)
        self.vUpdateInfo()
        return

    def vSaveCB(self):
        """
        Saves Current Image Present on the ImageCanvas
        """
        try: 
            fZoomFactor = self.oCZoom.nInfoImageSize / self.nImageSize
            self.dicScanParam['StepSize'] = [int(self.nStepSize * fZoomFactor)] * 2 
        except:
            self.dicScanParam['StepSize'] = [self.nStepSize] * 2    # X n Y steps
        if tkMessageBox.askyesno('Save', 'Do you want to save the current image?'):
            filepath = qv.strPathTracker()
            filename = tkFileDialog.asksaveasfilename(defaultextension='.pic', initialdir=filepath)
            qv.strPathTracker(filename)
        self.oSpectro.vSaveImages([self.afGridData, self.afRetImage, self.dicScanParam], filename)
        return
            
    def vSaveAsJPGCB(self):
        """
        Saves Current Image Present on the ImageCanvas as .jpg file
                --> filenames : *scan.jpg , *ret.jpg
        """
        import platform
        if platform.system() == 'Windows':
            tkMessageBox.showerror('Cannot Export', 'Ghostscript utility is not currently supported on Win* platforms ')
            return
        filepath=dialogs.strPathTracker()
        fname = tkFileDialog.asksaveasfilename(initialdir=filepath,initialfile='untitled',title='Load File')
        if not fname:
            return
        dialogs.strPathTracker(fname)
        self.oAppSpectro.CanvasScan.postscript(file=fname+'scan.ps')
        self.oAppSpectro.CanvasColor.postscript(file=fname+'lut.ps')
        # Convert the dirty rectangle into ps files
        from PIL import Image
        scanps = Image.open(fname+'scan.ps')
        retps = Image.open(fname+'ret.ps')
        lutps = Image.open(fname+'lut.ps')
        # Create empty images to be save as jpg
        ScanIm = Image.new('RGB', (281,248))	# this happens 256 down to 248 in jpg
        RetIm = Image.new('RGB', (281,248))	# this happens 256 down to 248 in jpg
        # Add lut band also to the images
        ScanIm.paste(scanps,(0,0))
        ScanIm.paste(lutps,(248,0))
        RetIm.paste(retps,(0,0))
        RetIm.paste(lutps,(248,0))
        # Save images in JPEG format
        ScanIm.save(fname+'scan.jpg','JPEG', quality=100)
        RetIm.save(fname+'ret.jpg','JPEG', quality=100)
        # Removing the temp. ps file
        os.remove(fname+'scan.ps')
        os.remove(fname+'ret.ps')
        os.remove(fname+'lut.ps')
        print 'JPG file saved'
        return

    def vOriginalCB(self):
        """
        Displays unfiltered original scan and retrace images
        """
        self.afGridData = self.afOrigGridData.copy()
        self.oSpectro.vSplashGridImage(iprog.float2gray(self.afGridData))
        return
