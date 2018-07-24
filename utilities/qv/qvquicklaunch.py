###########################
#   QuickLaunch Class     #
###########################

import cPickle
import os
from Tkinter import *
import tkFileDialog
import tkMessageBox

import qviprog
import qvcanvaszoom
import qv
import qvlext
import qvhvlext
import dialogs

module_path 	= os.path.join(os.curdir, 'utilities', 'qv')
# module_path 	= os.curdir 		# for standalone  
dumppath         = os.path.join(module_path, 'dump')	# default directory  containing ".dmp" files
sfilename	 = os.path.join(dumppath, 'scanimgdump.dmp')	# Scan image file path
rfilename	 = os.path.join(dumppath, 'retimgdump.dmp')	# Retrace image file path

HORZ 		= 2
VERT 		= 3
ZMODE           = 4
XL_GAIN         = 10.0

def quicklaunch(oQv):
	"""
	Returns QuickLaunch object
	"""
	oQL=QuickLaunch(oQv)
	return oQL

class QuickLaunch:

    def __init__(self, oQv):
        #print 'QLMenu object formed'
        self.oQv = oQv	
        self.oAppQv = oQv.oAppQv
        self.vCreateQLMenu()
        self.vConfigureCB()
        self.vInitQLaunch()
        return

    def vCreateQLMenu(self):
        """
        Pops up the menu on the right click
        """
        self.QLaunchMenu = Menu(self.oAppQv.qvGroup,tearoff=0)
        return
            
    def vConfigureCB(self):
        """
        Binds mouse button to the Qv window
        """
        self.oAppQv.CanvasScan.bind('<Button-3>', self.vQLaunchMenuCB)
        self.oAppQv.CanvasRetrace.bind('<Button-3>', self.vQLaunchMenuCB)
        self.vConfigureQLMenu()
        return
    
    def vInitQLaunch(self):
        """
        Initializes Zoom and QuickLaunch status (i.e. which is
        used to  check if there exists an unzoomed image on the canvas)
        variables.
        """
        self.bQLaunchVar=BooleanVar()
        self.bQLaunchVar.set(False)
        self.bZoomVar = BooleanVar()
        self.bZoomVar.set(False)
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
        self.QLaunchMenu.add_command(label='Zoom', command=self.vZoomCB)
        self.QLaunchMenu.add_command(label='Save Current', command=self.vSaveCB)
        self.QLaunchMenu.add_command(label='Save As JPG', command=self.vSaveAsJPGCB)
        self.QLaunchMenu.add_command(label='Original', command=self.vOriginalCB)
        self.QLaunchMenu.add_command(label='Roughness Level', command=self.vIRoughCB)

        self.LineExtMenu = Menu(self.QLaunchMenu, tearoff=0)
        self.QLaunchMenu.add_cascade(label='Line Profile', menu=self.LineExtMenu)
        self.LineExtMenu.add_command(label='Horizontal', command=self.vHorzLineExtractionCB)
        self.LineExtMenu.add_command(label='Vertical', command=self.vVertLineExtractionCB)
        self.LineExtMenu.add_command(label='Between Any Two Points', command=self.vLineExtractionCB)
        return

    def vQLaunchMenuCB(self,event):
        """
        Display menu on the poisition where clicked
        """
        if self.oQv.bImagePresentVar.get() == True:
                try:
                        self.QLaunchMenu.tk_popup(event.x_root, event.y_root,0)
                finally:
                        self.QLaunchMenu.grab_release()
                self.bQLaunchVar.set(False)
        return

    def vAcquireImageData(self, afScanImageData, afRetImageData, dicScanParam):
        """
        Acquire data only once when quick launched is invoked for a particular image
        """
        f = open(sfilename)
        self.afOrigScanData = cPickle.load(f)
        f.close()
        f = open(rfilename)
        self.afOrigRetData = cPickle.load(f)
        f.close()
        if self.bQLaunchVar.get() == True:
                self.afScanImage = afScanImageData
                try:
                        self.afRetImage = afRetImageData
                except:
                        self.afRetImage = None
        self.vAcquireImageParam(dicScanParam)	
        return

    def vAcquireImageParam(self, dicScanParam):
        self.dicScanParam = dicScanParam
        try:
                self.nImageSize = dicScanParam['ImageSize'][0]
                self.nStepSize = dicScanParam['StepSize'][0]
                self.nDelay = dicScanParam['Delay']
                self.nADCGain = dicScanParam['Gain']
        except:
                print 'Parameter Error'
                pass
        if dicScanParam.has_key('XLArea'):
                if dicScanParam['XLArea']:
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
        self.afScanImage = qviprog.min_maxfilter(self.afScanImage)
        self.oQv.vUpdateScanWindow(self.afScanImage)
        if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.min_maxfilter(self.afRetImage)
                self.oQv.vUpdateRetWindow(self.afRetImage)
        self.vUpdateInfo()
        return

    def vCorrectXCB(self):
        """
        Corrects the Vertical(Top to Bottom) Gradient 
        """
        #print 'Fix Vertical(Top to Bottom) Gradient' 
        self.afScanImage = qviprog.correctXslope(self.afScanImage)
        self.oQv.vUpdateScanWindow(self.afScanImage)
        if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.correctXslope(self.afRetImage)
                self.oQv.vUpdateRetWindow(self.afRetImage)
        self.vUpdateInfo()
        return

    def vCorrectYCB(self):
        """
        Corrects the Horizontal(Left to Right) Gradient
        """
        #print 'Fix Horizontal(Left to Right) Gradient' 
        self.afScanImage = qviprog.correctYslope(self.afScanImage)
        self.oQv.vUpdateScanWindow(self.afScanImage)
        if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.correctYslope(self.afRetImage)
                self.oQv.vUpdateRetWindow(self.afRetImage)
        self.vUpdateInfo()
        return

    def vRepairCB(self):
        """
        Corrects the both Horizontal(Left to Right) Gradient 
        and Vertical(Top to Bottom) Gradient 
        """
        self.afScanImage = qviprog.repair(self.afScanImage)
        self.oQv.vUpdateScanWindow(self.afScanImage)
        if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.repair(self.afRetImage)
                self.oQv.vUpdateRetWindow(self.afRetImage)
        self.vUpdateInfo()
        return

    def vSmoothenCB(self):
        """
        Invokes Gaussian Blurring for image smoothening
        """
        self.afScanImage = qviprog.gaussian_(self.afScanImage)
        self.oQv.vUpdateScanWindow(self.afScanImage)
        if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.gaussian_(self.afRetImage)
                self.oQv.vUpdateRetWindow(self.afRetImage)
        self.vUpdateInfo()
        return

    def vContrastCB(self):
        """
        Does Contrast alteration Using Histogram Equalization
        hist works fine with gray data only , so float
        image matrix isnt updated with hist filtered data
        """
        newscan = qviprog.coreHisteq(qviprog.float2gray(self.afScanImage))
        self.oQv.vUpdateScanWindow(newscan)
        if self.oQv.bDumpVar.get()==False:
                newret  = qviprog.coreHisteq(qviprog.float2gray(self.afRetImage))
                self.oQv.vUpdateRetWindow(newret)
        self.vUpdateInfo()
        return	

    def vInvertCB(self):
        """
        Inverts image pixels
        """
        self.afScanImage = qviprog.invert(self.afScanImage)
        self.oQv.vUpdateScanWindow(qviprog.float2gray(self.afScanImage))
        if self.oQv.bDumpVar.get()== False:
                self.afRetImage = qviprog.invert(self.afRetImage)
                self.oQv.vUpdateRetWindow(qviprog.float2gray(self.afRetImage))
                self.vUpdateInfo()
        return

    def vFourierFilterCB(self):
        """
        Invokes Fourier LPF for image smoothening
        """
        threshold = 1.0#2.0
        self.afScanImage = qviprog.fourierfilter(self.afScanImage, threshold)
        self.oQv.vUpdateScanWindow(self.afScanImage)
        if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.fourierfilter(self.afRetImage, threshold)
                self.oQv.vUpdateRetWindow(self.afRetImage)
        self.vUpdateInfo()
        return

    def vBgSubCB(self):
        """
        Remove the slow variations in the background 
        to extact finer details of atomic resolution
        """
        tkMessageBox.showinfo( 'Busy', 'Please click OK and wait for \n 4-5 sec for the results', parent=self.oAppQv.qvGroup)
        if self.dicScanParam['Direction'] == HORZ:
            self.afScanImage = qviprog.afBgSubH(self.afScanImage)
            self.oQv.vUpdateScanWindow(self.afScanImage)
            if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.afBgSubH(self.afRetImage)
                self.oQv.vUpdateRetWindow(self.afRetImage)
        if self.dicScanParam['Direction'] == VERT:
            self.afScanImage = qviprog.afBgSubV(self.afScanImage)
            self.oQv.vUpdateScanWindow(self.afScanImage)
            if self.oQv.bDumpVar.get()==False:
                self.afRetImage  = qviprog.afBgSubV(self.afRetImage)
                self.oQv.vUpdateRetWindow(self.afRetImage)
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
        self.oQv.vSaveImages([self.afScanImage, self.afRetImage, self.dicScanParam], filename)
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

	if len(self.afScanImage.shape) == 2:
	    self.oAppQv.CanvasScan.postscript (file = fname + 'scan.ps')
            if self.oQv.bDumpVar.get()==False:
                self.oAppQv.CanvasRetrace.postscript(file=fname+'ret.ps')
	    else:
		for count in range (self.oQv.dicScanParam['NoOfChannels']):
			self.oQv.CanChannelScanFloat [count].postscript (file = fname + str (count) + 'scan.ps')
			self.oQv.CanChannelRetFloat [count].postscript (file = fname + str (count) + 'ret.ps')
	if len(self.afScanImage.shape) == 2:
	    cmd = 'convert -density 400' + ' "' + fname+'scan.ps' + '" -resize 25% -quality 92 "' + fname+'scan.jpg"'
	    os.popen (cmd)
	    cmd = 'convert -density 400' + ' "' + fname+'ret.ps' + '" -resize 25% -quality 92 "' + fname+'ret.jpg"'
	    os.popen (cmd)
	    # Removing the temp. ps file
	    os.remove (fname + 'scan.ps')
	    os.remove (fname + 'ret.ps')
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

      
    def vOriginalCB(self):
        """
        Displays unfiltered original scan and retrace images
        """
        self.afScanImage = self.afOrigScanData
        self.oQv.vUpdateScanWindow(qviprog.float2gray(self.afScanImage))
        if self.oQv.bDumpVar.get()==False:
                self.afRetImage = self.afOrigRetData
                self.oQv.vUpdateRetWindow(qviprog.float2gray(self.afRetImage))
        try:
                self.oQv.afScanImageData=self.afOrigScanData
                self.oQv.afRetImageData=self.afOrigRetData
        except:
                pass
        self.vAcquireImageParam(self.dicScanParam)
        ### Image Size from previous zoom is clear below ### 
        try:
                self.oCZoom.nInfoImageSize = self.nImageSize
        except:
                pass
        self.vUpdateInfo()
        self.bZoomVar.set(False)
        return

    def vIRoughCB(self):
        """
        Displays Image Roughness
        """
        afNormScanImageData = self.afScanImage / self.dicScanParam['Gain']
        afNormRetImageData = self.afRetImage / self.dicScanParam['Gain']
        ### Actual Z-Piezo Movement is XL_GAIN times Zpi recorded through ADC ### 
        if self.dicScanParam['DigitizationMode'] == ZMODE:
	    if dicScanParam.has_key('HVAGainFactor'):
		fHVAGain = dicScanParam['HVAGainFactor']
	    else:
               	fHVAGain = fGetHVAGain()
	    
            afNormScanImageData *= fHVAGain 
            afNormRetImageData *= fHVAGain 
        fMeanS = afNormScanImageData.mean() * self.dicScanParam['ZCalibration'] / 1e3
        fMeanR = afNormRetImageData.mean() * self.dicScanParam['ZCalibration'] / 1e3
        fStdDevS = afNormScanImageData.stddev() * self.dicScanParam['ZCalibration'] / 1e3
        fStdDevR = afNormRetImageData.stddev() * self.dicScanParam['ZCalibration'] / 1e3
        
        tkMessageBox.showinfo( 'Ra Values', 'Scan Image\n' \
                                'Mean: ' + str('%3.2f'%fMeanS) +' nm' + '\n' + \
                                'StdDev: ' + str('%3.2f'%fStdDevS) +' nm' + '\n' + \
                                '\n Retrace Image\n' \
                                'Mean: ' + str('%3.2f'%fMeanR) +' nm' + '\n' + \
                                'StdDev: ' + str('%3.2f'%fStdDevR) +' nm' + '\n')
        return
    
    def vLineExtractionCB(self, event=None):
	oLExt = qvlext.lext(self.oQv)
	return

    def vHorzLineExtractionCB(self, event=None):
	oHVLExt = qvhvlext.hvlext(self.oQv, 'H')
	return

    def vVertLineExtractionCB(self, event=None):
	oHVLExt = qvhvlext.hvlext(self.oQv, 'V')
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
            self.oQv.vUpdateAreaInfo(self.dicScanParam)
        except:
            print 'Info Display Error'
        return


