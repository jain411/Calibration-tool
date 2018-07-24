from Tkinter import *
import tkFileDialog
import tkMessageBox
from PIL import Image, ImageTk
import os
import numpy
import cPickle

import app_qv 
import loaddir
import plugins
import qviprog
import qvquicklaunch

module_path 	= os.path.join(os.curdir, 'utilities', 'qv') 
# module_path 	= os.curdir 		# for standalone
imagepath       = os.path.join(module_path, 'images')
dumppath        = os.path.join(module_path, 'dump')
logpath         = os.path.join(module_path, 'log')
globlogfile     = os.path.join(logpath, 'glob.dat')
trackerlogfile  = os.path.join(logpath, 'pathlog.dat')

ZMODE           = 4


def strPathTracker(filename=None):
    if not filename:
        try:
            fd = open(trackerlogfile)
        except:
            return os.path.abspath(os.curdir)
        oldpath = fd.readline().strip()
        fd.close()
        return oldpath
    else:
        path = filename         # here it is dir name
        try:
            fd = open(trackerlogfile,'w')
        except:
            tkMessageBox.showerror('Path log not found', 'Cant open path-tracker logfile', parent=self.oAppQv.qvGroup)
            return
        fd.write(path)
        fd.close()
        return


def dicReadGlobalParam():
    f = open(globlogfile)
    dicGlobalParam = cPickle.load(f)
    f.close()
    return dicGlobalParam 

def fGetPiezoXCalibration():
    """
    Returns: Float Value - X-direction calibration in nm/V 
    """
    dicGlobalParam = dicReadGlobalParam()
    fXCalib = dicGlobalParam['XCalibration']
    return fXCalib

def fGetPiezoZCalibration():
    """
    Returns: Float Value - Z-direction calibration in nm/V 
    """
    dicGlobalParam = dicReadGlobalParam() 
    fZCalib = dicGlobalParam['ZCalibration']
    return fZCalib

def fGetHVAGain():
    dicGlobalParam = dicReadGlobalParam()
    if dicGlobalParam.has_key('HVAGain'):
        fHVAGain = dicGlobalParam['HVAGain']
    else:
        fHVAGain = 10.0
    return fHVAGain

def afCalculateScale(afImData, piezo_z):
    """
    Calculate the Z-scale of the image being displayed, result in angs
    """
    if not piezo_z:
        piezo_z = fGetPiezoZCalibration()       #since data is in mV and z-calib in in nm/V
    piezo_z /= 1e3      
    Zpi_min, Zpi_max = afImData.min(), afImData.max()
    Zpi_mean = Zpi_min + (Zpi_max - Zpi_min)/2
    Zpi_stddev = afImData.std()
    return piezo_z*Zpi_mean, piezo_z*Zpi_min, piezo_z*Zpi_max, piezo_z*Zpi_stddev

def fCalculateSize(dicScanParam):
        """
        Calculates Scan Image size in angs
        """
        imsize = dicScanParam['ImageSize'][0]
        stsize = dicScanParam['StepSize'][0]
        if dicScanParam.has_key('XCalibration'):
            piezo_xy = dicScanParam['XCalibration']
        else:
            piezo_xy = fGetPiezoXCalibration()
        if dicScanParam.has_key('XLArea'):
            if dicScanParam['XLArea']:
		if dicScanParam.has_key('HVAGainFactor'):
                	stsize *= dicScanParam['HVAGainFactor']
		else:
			print 'Old Data Error: Gain Factor not found...assuming it to be 10x...'
			XL_GAIN = 10.0
                	stsize *= XL_GAIN
        size = stsize/1e3 * imsize * piezo_xy           #piezo_xy is in nm/V and stsize is in mV
        if (size > 1000):
                mulfactor = 0.001 
                units = 'um' 
        if (size > 100) and (size < 1000):
                mulfactor = 1
                units = 'nm'
        if (size < 100):
                mulfactor = 10
                units = 'A' 
        return size*mulfactor, units


plugindic = {   '.npic' : plugins.picdecoder, \
                '.dat' : plugins.datdecoder, \
                '.dmp' : plugins.dmpdecoder, \
                '.ps'  : plugins.stddecoder, \
                '.png' : plugins.stddecoder, \
                '.jpg' : plugins.stddecoder \
            }

SCAN_PARAM_LIST = []

OXDAC   = 0
XDAC    = 1
OYDAC   = 2
YDAC    = 3
OZDAC   = 4
BIASDAC = 5
BIGXDAC = 6
BIGYDAC = 7 

ImageType = 'RGB'
khali = numpy.zeros((256,256),'f')
khaliim = Image.new(ImageType, (256,256))

def qv(picfile=None, pwd=None, f=None, oMenuBar=None):
        """
        Creates Qv Interface
        """
        if not f :
                root = Tk()
                #f = Frame(root).grid()
                oAppQv = app_qv.app_qv()
                oAppQv.createQVwindow(root)
                oQv = Qv(oAppQv, picfile, pwd)
                root.title('Quick View Album for nanoREV STM (www.quazartech.com)')
                root.mainloop()
        else:
                oAppQv = app_qv.app_qv()
                oAppQv.createQVwindow(f)
                oQv = Qv(oAppQv, picfile, pwd, oMenuBar)
                return oQv

class Qv:
    """
    """
    def __init__(self, oAppQv, picfile, pwd, oMenuBar=None):
        self.oAppQv = oAppQv
        self.__configureCB()
        self.vCreateNewImages()
        self.oMenuBar = oMenuBar
        self.strCurrentFilename = ''
        #print 'Image file arg', picfile
        #print 'Exe path', pwd
        if picfile:
            #print pwd, picfile
            fullfilename = os.path.join(pwd,picfile)
            #print fullfilename
            self.vCreateFileList(os.path.split(fullfilename)[0])
            self.files.insert(0,fullfilename)
            self.vMakeImageHandler(fullfilename)
        else: 
            self.vCreateFileList(os.curdir)
	self.bImagePresentVar = BooleanVar()
	self.bImagePresentVar.set(False)
	self.bDumpVar = BooleanVar()
	self.bDumpVar.set(False)
	self.oQLaunch = qvquicklaunch.quicklaunch(self)
        self._vKeyBindings()
        return

    def __configureCB(self):
            """
            """
            #print "CallBacks Attached"
            self.oAppQv.BtnBrowse.configure(command=self.BtnBrowseCB)
            self.oAppQv.BtnPrev.configure(command=self.BtnPrevCB)
            self.oAppQv.BtnNext.configure(command=self.BtnNextCB)
            self.oAppQv.BtnFirst.configure(command=self.BtnFirstCB)
            self.oAppQv.BtnLast.configure(command=self.BtnLastCB)
            self.oAppQv.BtnSave.configure(command=self.BtnSaveCB)
            self.oAppQv.BtnSaveRemark.configure(command=self.BtnSaveRemarkCB)
            self.oAppQv.qvGroup.protocol('WM_DELETE_WINDOW',self.vCloseAppQvCB)
            return

    def _vKeyBindings(self):
        self.oAppQv.qvGroup.bind('<Prior>', self.BtnPrevCB)
        self.oAppQv.qvGroup.bind('<Next>', self.BtnNextCB)
        self.oAppQv.qvGroup.bind('<Shift-Prior>', self.BtnFirstCB)
        self.oAppQv.qvGroup.bind('<Shift-Next>', self.BtnLastCB)
        self.oAppQv.qvGroup.bind('<Control-o>', self.BtnBrowseCB)
        self.oAppQv.qvGroup.bind('<Control-s>', self.BtnSaveCB)
        return


    def vCreateNewImages(self):
        """
        Creates New scan and retrace image      
        """
        self.nDisplayCount = 0
        self.nFileCounter = 0
        self.ScanImage = Image.new(ImageType, (256,256))
        self.RetImage = Image.new(ImageType, (256,256))
        self.ScanPhotoImage = ImageTk.PhotoImage(self.ScanImage)
        self.RetPhotoImage = ImageTk.PhotoImage(self.RetImage)
        self.CanScan = self.oAppQv.CanvasScan.create_image(0,0, image=self.ScanPhotoImage, anchor=NW)
        self.CanRet = self.oAppQv.CanvasRetrace.create_image(0,0, image=self.RetPhotoImage, anchor=NW)
        return

    def imMakeImage(self, filename=None):
        """
        """
        global khali
        #print 'Data File: ', filename
        ext = os.path.splitext(filename)[1]
        if ext == '.pic':
            self.oAppQv.TBRemark.delete(1.0,END)
            self.vActivateRemark(filename) 
        srd = plugindic[ext](filename)
        try:
            srd = plugindic[ext](filename)
        except:
            tkMessageBox.showerror('Unknow file format: ', ext, parent=self.oAppQv.qvGroup) 
            srd = [khali, khali, None]
        return srd 

    def vActivateRemark(self, filename):
        self.strCurrentFilename = filename
        self.oAppQv.TBRemark.config(state=NORMAL)
        return

    def vSaveRemark(self):
        ext = os.path.splitext(self.strCurrentFilename)[1]
        srd = plugindic[ext](self.strCurrentFilename)
        srd[2]['Remarks'] = self.oAppQv.TBRemark.get(1.0,END)
        tkMessageBox.showinfo('Remark saved with the image', srd[2]['Remarks'], parent=self.oAppQv.qvGroup)
        self.vSaveImages(srd)
        return

    def vSaveImages(self, srd, fname=None):
        if fname == None:
            fname = self.strCurrentFilename
        try:
            f = open(fname, 'w')
        except:
            tkMessageBox.showerror('Cannot Open', 'Failed to open the image and save remark in it', parent=self.oAppQv.qvGroup)
            return
        cPickle.dump(srd[0], f)
        cPickle.dump(srd[1], f)
        cPickle.dump(srd[2], f)
        f.close()
        return

    def BtnBrowseCB(self, event=None):
        self.vBtnBrowseHandler()
        return

    def vBtnBrowseHandler(self):
        oLoadDir = loaddir.LoadDirDialog(self.oAppQv.qvGroup)
        filepath = strPathTracker()
        self.directory = oLoadDir.godir(dir_or_file=filepath, key='track')
        #print self.directory
##        if self.directory == None:
##            tkMessageBox.showinfo( 'No directory selected', 'Please select a folder with image files')
##            return
        strPathTracker(self.directory)
        self.vCreateFileList(self.directory)
        self.nFileCounter = -1
        tkMessageBox.showinfo('View Files', 'Now click on the arrow buttons to \n open image files', parent=self.oAppQv.qvGroup)
	self.oAppQv.BtnNext.configure(state=NORMAL)
	self.oAppQv.BtnPrev.configure(state=DISABLED)
        return

    def vCreateFileList(self, directory):
        self.files = [] 
        for items in os.listdir(directory):
            fullname = os.path.join(os.path.expanduser(directory), items)
            if os.path.isfile(fullname):        # name of a file not a dir
                if os.path.splitext(fullname)[-1] in plugindic.keys():
                    self.files.append(fullname)
        self.files.sort()
        #print 'files list', self.files
        return

    def BtnPrevCB(self, event=None):
        """
        """
        if self.nFileCounter > 0: 
            self.nFileCounter -= 1
	    self.oAppQv.BtnNext.configure(state=NORMAL)
            self.vMakeImageHandler()
	else:
	    self.oAppQv.BtnPrev.configure(state=DISABLED)
        return

    def BtnNextCB(self, event=None):
        """
        """
        if self.nFileCounter < len(self.files) - 1:
            self.nFileCounter += 1
	    self.oAppQv.BtnPrev.configure(state=NORMAL)
            self.vMakeImageHandler()
	else:
	    self.oAppQv.BtnNext.configure(state=DISABLED)
        return

    def BtnFirstCB(self, event=None):
        """
        """
        self.nFileCounter = 0
        self.vMakeImageHandler()
	self.oAppQv.BtnNext.configure(state=NORMAL)
	self.oAppQv.BtnPrev.configure(state=DISABLED)
        return

    def BtnLastCB(self, event=None):
        """
        """
        self.nFileCounter = len(self.files) - 1 
        self.vMakeImageHandler()
	self.oAppQv.BtnNext.configure(state=DISABLED)
	self.oAppQv.BtnPrev.configure(state=NORMAL)
        return

    def BtnSaveCB(self, event=None):
        """
        """
        self.vSaveAsPS()
        return

    def vSaveAsPS(self):
        """
        Saves Current Image Present on the ImageCanvas as .ps file
                --> filenames : *mat.ps 
        """
        import platform
        if platform.system() == 'Windows':
            tkMessageBox.showerror('Not supported', 'Ghostscript utility not \n supported in Win* platforms', parent=self.oAppQv.qvGroup)
            return
        filepath = strPathTracker()
        fname = tkFileDialog.asksaveasfilename(initialdir=filepath,initialfile='untitled',title='Load File')
        if not fname:
            return
        filepath = strPathTracker(fname)
        self.oAppQv.CanvasScan.postscript(file=fname+'scan.ps')
        self.oAppQv.CanvasRetrace.postscript(file=fname+'ret.ps')
        # Convert the dirty rectangle into ps files
        from PIL import Image
        scanps = Image.open(fname+'scan.ps')
        retps = Image.open(fname+'ret.ps')
        # Create empty images to be save as jpg
        ScanIm = Image.new('RGB', (256,256))	# this happens 256 down to 248 in jpg
        RetIm = Image.new('RGB', (256,256))	# this happens 256 down to 248 in jpg
        # Add lut band also to the images
        ScanIm.paste(scanps,(0,0))
        RetIm.paste(retps,(0,0))
        # Save images in JPEG format
        ScanIm.save(fname+'scan.jpg','JPEG', quality=100)
        RetIm.save(fname+'ret.jpg','JPEG', quality=100)
        # Removing the temp. ps file
        os.remove(fname+'scan.ps')
        os.remove(fname+'ret.ps')
        os.remove(fname+'lut.ps')
        #print 'JPG file saved'
        return

    def BtnSaveRemarkCB(self):
        bRem = True
        if self.strCurrentFilename == '':
            bRem = False
            tkMessageBox.showerror('No Image Present', 'Open an image file and then use it to save remarks', parent=self.oAppQv.qvGroup)
        if os.path.splitext(self.strCurrentFilename)[1] != '.pic' and bRem == True:
            bRem = False
            tkMessageBox.showerror('Cannot Save Remark', 'Open a nanoREV image file and then use it to save remarks', parent=self.oAppQv.qvGroup)
        if self.oAppQv.TBRemark.get(1.0,END) == '\n' and bRem == True:
            bRem = False
            tkMessageBox.showerror('No Remark', 'Please write a remark that is \n to be saved for the curent image', parent=self.oAppQv.qvGroup)
        if bRem == True:
            self.vSaveRemark()
        return

    def vUpdateWindows(self, srd):
        """
        """
        self.vUpdateScanWindow(srd[0])  
        self.vUpdateRetWindow(srd[1])
       	self.bImagePresentVar.set(True)
        self.vUpdateInfo(srd[2])
        self.vUpdateAreaInfo(srd[2])
        self.vUpdateRawDataInfo(srd[1], srd[2])
        # Dump in a temporary location
        fd = open(os.path.join(dumppath, 'scanimgdump.dmp'),'w')	
        cPickle.dump(srd[0], fd)
        cPickle.dump(srd[2], fd)
        fd.close()
        fd = open(os.path.join(dumppath, 'retimgdump.dmp'),'w')		
        cPickle.dump(srd[1], fd)
        cPickle.dump(srd[2], fd)
        fd.close()
        self.oQLaunch.bQLaunchVar.set(True)
        self.oQLaunch.vAcquireImageData(srd[0], srd[1], srd[2]) # for Quicklaunch
        self.oAppQv.qvGroup.update()
        return

    def vUpdateScanWindow(self, smatrix):
        """
        """
        clipped = qviprog.min_maxfilter (smatrix)
        graymatrix = qviprog.float2gray(clipped)
        colormatrix = qviprog.gray2rgb(graymatrix)
        self.ScanImage.putdata(colormatrix)
        self.ScanPhotoImage.paste(self.ScanImage)

        	
        return

    def vUpdateRetWindow(self, rmatrix):
        """
        """
        clipped = qviprog.min_maxfilter(rmatrix)
        graymatrix = qviprog.float2gray(clipped)
        colormatrix = qviprog.gray2rgb(graymatrix)
        self.RetImage.putdata(colormatrix)
        self.RetPhotoImage.paste(self.RetImage)	
        return

    def vUpdateInfo(self, dicparam=None):
        """
        """
        if not dicparam:
            return
        if dicparam.has_key('Remarks'):
            strRemark = dicparam.pop('Remarks')
            self.oAppQv.TBRemark.delete(1.0, END)
            self.oAppQv.TBRemark.insert(END, strRemark)
        self.oAppQv.LInfoBox.delete(0, END)
        self.oAppQv.LInfoBox.insert(END, os.path.basename(self.files[self.nFileCounter]))
        self.oAppQv.LInfoBox.insert(END, os.path.dirname(self.files[self.nFileCounter]))
        for item in dicparam:
            self.oAppQv.LInfoBox.insert(END,str(item) + " : " + str(dicparam[item]))
            #print str(dicparam[item])
        #self.oAppQv.LblImageFile.configure(text = )
        return

    def vUpdateRawDataInfo(self, afRetImageData, dicScanParam):
        """
        Prints min/max and deviations in scan and retrace data in mv
        """
        normImageData = afRetImageData/dicScanParam['Gain']
        ### Actual Z-Piezo Movement is XL_GAIN times Zpi recorded through ADC ### 
        if dicScanParam['DigitizationMode'] == ZMODE:
		if dicScanParam.has_key('HVAGainFactor'):
			fHVAGain = dicScanParam['HVAGainFactor']
		else:
                	fHVAGain = fGetHVAGain()
                normImageData *= fHVAGain  
        if dicScanParam.has_key('ZCalibration'):
            piezo_z = dicScanParam['ZCalibration']
        else:
            piezo_z = None
        mean, min, max, stddev = afCalculateScale(normImageData, piezo_z)
        #self.txtImageInfo.append('Stats: '+ 'Min: ' + str(round(min,2)) + 'nm, ' \
        #                                + 'Mean: ' + str(round(mean,2)) + 'nm, ' \
        #                                + 'Max: ' + str(round(max,2)) + 'nm, ' \
        #                                + 'StdDev: ' + str(round(stddev,2)) + 'nm, ' \
        #                       )
        #print 'Image Stats: '
        #print 'Min: ', round(min,2), 'nm'
        #print 'Mean: ', round(mean,2), 'nm'
        #print 'Max: ', round(max,2), 'nm'
        #print 'StdDev: ', round(stddev,2), 'nm'
        return

    def vUpdateAreaInfo(self, dicScanParam):
        size, units = fCalculateSize(dicScanParam)
        try:
            self.oAppQv.CanvasScan.delete(self.ciScanAreaInfo)
            self.oAppQv.CanvasRetrace.delete(self.ciRetAreaInfo)
        except:
            pass
        self.ciScanAreaInfo = self.oAppQv.CanvasScan.create_text(2,2, \
                                    text=str(round(size,2))+units, \
                                    anchor=NW, fill='blue', activefill='white')
        self.ciRetAreaInfo = self.oAppQv.CanvasRetrace.create_text(2,2, \
                                    text=str(round(size,2))+units, \
                                    anchor=NW, fill='blue', activefill='white')
        return

    def vRenewSize(self, size=None, units=None):
	"""
	Prints image size on the scan image canvas
	"""
	try:
	    self.oAppQv.CanvasScan.delete(self.ciScanAreaInfo)
	except:
	    pass
	try:
	    self.oAppQv.CanvasRetrace.delete(self.ciRetAreaInfo)
	except:
	    pass
	#print 'Kando', size, units
	self.ciScanAreaInfo = self.oAppQv.CanvasScan.create_text(2,2, \
                text=str(round(size,2))+units, \
                anchor=NW, 
                fill='blue', \
                activefill='white')
	if self.bDumpVar.get()==False:
		self.ciRetAreaInfo = self.oAppQv.CanvasRetrace.create_text(2,2, \
                text=str(round(size,2))+units, \
                anchor=NW, fill='blue', \
                activefill='white')
	else:
		pass
	return

    def vMakeImageHandler(self, picfile=None):
        """
        """
        if picfile:
            srd = self.imMakeImage(picfile)
        else:
            srd = self.imMakeImage(self.files[self.nFileCounter])
	if srd[0] is None:
	    print 'Not an Image'
	    return
        if len(srd) < 3:
            self.vStdUpdateWindows(srd)
        else:
            self.vUpdateWindows(srd)
        return

    def vStdUpdateWindows(self, srd):
        global khaliim
        self.ScanPhotoImage.paste(khaliim)
        self.RetPhotoImage.paste(khaliim)
        self.ScanPhotoImage.paste(srd[0])
        self.vUpdateInfo(srd[1])        
        return

    def vCloseAppQvCB(self):
        if self.oMenuBar:
            self.oMenuBar.QV_Instance = 0
        self.oAppQv.qvGroup.destroy()
        return

if __name__ == '__main__':
        import sys
        if len(sys.argv) == 3: 
            qv(picfile=sys.argv[1], pwd=sys.argv[2])
        else:
            qv()
