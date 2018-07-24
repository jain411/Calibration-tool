from Tkinter import *
from PIL import Image, ImageTk
import tkMessageBox
import tkColorChooser
import os
import cPickle

import apps.dialogs as dialogs 
import utilities.iprog.iprog as iprog
import scanner
import app_navigator

"""
########### SCAN PARAMETERS RECORDED IN THE DICTIONARY ARE: ##########
1. LocXY: [x,y]
2. LocMV: [x,y]
3. Area: No.OfPixels * StepSize (selected from the slider)
#####################################################################
"""

def navigator(f=None, oScanner=None, oOffset=None):
	"""
	Creates Navigator Interface
	"""
	title = 'Navigator'
	if not f :
		root = Tk()
		#f = Frame(root).grid()
		oAppNavigator = app_navigator.app_navigator()
		oAppNavigator.createNVwindow(root)
		oNavigator = Navigator(oAppNavigator)
		root.title(title)
		root.mainloop()
	else:
		oAppNavigator = app_navigator.app_navigator()
		oAppNavigator.createNVwindow(f)
		oNavigator = Navigator(oAppNavigator, oScanner, oOffset)
	return oNavigator

class Navigator:
    """
    """
    def __init__(self, oAppNavigator, oScanner, oOffset):
	self.oAppNavigator = oAppNavigator
	self.oScanner = oScanner
	self.oOffset = oOffset
	self.dicMappedZones = {}
	self.dicSliderParam = {}	# from_, to, resolution 
	self.nFramePixels = 256
	dicGUISettings = dialogs.dicReadGUISettings()
	self.strFrameColor = dicGUISettings['NaviBox']
	self.__configureCB()
	self.vCreateNewImages()
	self.vSetScanImage()
	#self.vAskForRefMap()
	return

    def __configureCB(self):
	"""
	"""
	print "CallBacks Attached"
	self.oAppNavigator.BtnUp.configure(command=self.BtnUpCB)
	self.oAppNavigator.BtnDown.configure(command=self.BtnDownCB)
	self.oAppNavigator.BtnLeft.configure(command=self.BtnLeftCB)
	self.oAppNavigator.BtnRight.configure(command=self.BtnRightCB)
	self.oAppNavigator.BtnHome.configure(command=self.BtnHomeCB)
	self.oAppNavigator.BtnDropAnchor.configure(command=self.BtnDropAnchorCB, state=DISABLED)
	self.oAppNavigator.SliderArea.configure(command=self.vSliderAreaCB)
	self.oAppNavigator.settingsmenu.add_command(label='Grid Color Settings', \
						command=self.vChooseGridColor)
	self.oAppNavigator.refmapmenu.add_command(label='Scan Image', \
						command=self.vSetScanImage)
	self.oAppNavigator.refmapmenu.add_command(label='Retrace Image', \
						command=self.vSetRetImage)
	self.__vConfigureKBShortCuts()
	return

    def __vConfigureKBShortCuts(self):
	"""
	Keyboard bindings for different functions
	"""
	self.oAppNavigator.navigatorGroup.bind('<Up>', self.BtnUpCB)
	self.oAppNavigator.navigatorGroup.bind('<Down>', self.BtnDownCB)
	self.oAppNavigator.navigatorGroup.bind('<Left>', self.BtnLeftCB)
	self.oAppNavigator.navigatorGroup.bind('<Right>', self.BtnRightCB)
	self.oAppNavigator.navigatorGroup.bind('<Home>', self.BtnHomeCB)
	return


    def vCreateNewImages(self, size=[256,256]):
	"""
	Creates New scan and retrace image	
	"""
	from PIL import Image
	self.RefMapImage = Image.new('RGB', (size[1], size[0]))
	self.RefMapPhotoImage = ImageTk.PhotoImage(self.RefMapImage)
	self.CanRefMap = self.oAppNavigator.CanvasRefMap.create_image(0,0, \
					image=self.RefMapPhotoImage, anchor=NW)
	self.OpeningText = self.oAppNavigator.CanvasRefMap.create_text(self.nFramePixels/2, \
					self.nFramePixels/2, \
					text='Select Reference Map from \'File Menu\'', \
					fill='blue', \
					)
	return

    def vChooseGridColor(self):
	FrameColor = tkColorChooser.askcolor(title='Frame Box Color Chooser', parent=self.oAppNavigator.navigatorGroup)
	if (FrameColor[0] == None) or (FrameColor[1] == None):
	    return
	self.strFrameColor = str(FrameColor[1])
	dicGUISettings = dialogs.dicReadGUISettings()
	dicGUISettings['NaviBox'] = self.strFrameColor
	dialogs.vWriteGUISettings(dicGUISettings)
	self.oAppNavigator.CanvasRefMap.itemconfig(self.FrameBox, outline=self.strFrameColor)
	return

    def vSetScanImage(self):
	f = open(os.path.join(iprog.dumppath, 'scanimgdump.dmp'))
	afRefMap = cPickle.load(f)
        self.dicScanParam = cPickle.load(f)
        f.close()
        ''' Choosing Topography Image in case of Multi-Channel Data '''
        if self.dicScanParam.has_key('NoOfChannels'):
            noc = self.dicScanParam ['NoOfChannels']
        else:
            noc = 0
        if noc > 1:
            channel = 0 # The first channel (Topography Data)
            afRefMap = afRefMap[0]        
            print 'Navigator using', self.dicScanParam['ChannelNames'][channel], 'Multi-Channel Image Data'

	self.afRefMap = iprog.min_maxfilter(afRefMap)	# clip noise spikes above std. dev.
	self.vRenewRefMap(self.afRefMap) 
	self._configureNavigator()
	self.vSaveRefMap()
	return

    def vSetRetImage(self):
	f = open(os.path.join(iprog.dumppath, 'retimgdump.dmp'))
	afRefMap = cPickle.load(f)
        self.dicScanParam = cPickle.load(f)
        f.close() 
        ''' Choosing Topography Image in case of Multi-Channel Data '''
        if self.dicScanParam.has_key('NoOfChannels'):
            noc = self.dicScanParam ['NoOfChannels']
        else:
            noc = 0
        if noc > 1:
            channel = 0 # The first channel (Topography Data)
            afRefMap = afRefMap[0]        
            print 'Navigator using', self.dicScanParam['ChannelNames'][channel], 'Multi-Channel Image Data'

	self.afRefMap = iprog.min_maxfilter(afRefMap)	# clip noise spikes above std. dev.
	self.vRenewRefMap(self.afRefMap)
	self._configureNavigator()
	self.vSaveRefMap()
	return

    def _configureNavigator(self):
	self.vUpdateInfo(self.dicScanParam)
	self._configureSlider()
	self.vShowFrame()
	return 

    def _configureSlider(self):
	try:
	    self.vGetStepList()
	except:
	    tkMessageBox.showerror('Reference Map Error', 'Image Parameters not enough', parent=self.oAppNavigator.navigatorGroup)
	    return
	self.vGetMaxStepSize()
	self.oAppNavigator.SliderArea.configure(to=self.dicSliderParam['to'], \
						from_=self.dicSliderParam['from_'], \
						resolution=self.dicSliderParam['resolution'])
	self.oAppNavigator.SliderArea.set(self.dicSliderParam['from_'])	# Initial Value
	return

    def vSaveRefMap(self):
	f = open(os.path.join(iprog.dumppath, 'refmap.dmp'), 'w')
	cPickle.dump(self.afRefMap, f)
	cPickle.dump(self.dicScanParam, f)
	cPickle.dump(self.dicMappedZones, f)
	f.close()
	return

    def vRenewRefMap(self, afImageMatrix):
	try:
	    self.oAppNavigator.CanvasRefMap.delete(self.OpeningText)
	except:
	    pass
	try:
	    self.vClearFrame()
	except:
	    pass
	graymatrix = iprog.float2gray(afImageMatrix)
        colmatrix = map(lambda(x):self.oScanner.oImaging.RGB[int(x)], graymatrix.flat)
        self.RefMapImage.putdata(colmatrix)
        self.RefMapPhotoImage.paste(self.RefMapImage)
	self.oAppNavigator.navigatorGroup.update()
	return

    def vSliderAreaCB(self, event):
	try:
	    self.vShowFrame() 
	except:
	    #print 'Global Map not selected'
	    return
	self.oAppNavigator.BtnDropAnchor.configure(state=NORMAL)
	return

    def vShowFrame(self):
	fl = self.fGetFrameEdge()
	loc = self.arGetFrameLoc()
	if self.bCheckTransgress(loc, fl):
	    return	
	self.vRenewFrameInfo()
	self.vDisplayFrame(loc, fl) 
	return

    def fGetFrameEdge(self):
	frame_edge = float(self.oAppNavigator.SliderArea.get())
	fFrameLength = (self.nFramePixels * frame_edge) / self.MV2PIXELS
	return fFrameLength 

    def arGetFrameLoc(self):
	try:
	    location = [0]*2
	    coords= self.oAppNavigator.CanvasRefMap.coords(self.FrameBox)
	    location[0] = coords[0] + (coords[2] - coords[0])/2 
	    location[1] = coords[1] + (coords[3] - coords[1])/2
	except:
	    location = [self.nFramePixels/2]*2		#By Default: Locate Frame in the center
	return location

    def arGetFrameCoords(self, location, nFrameLength):
	frame_coords = [location[0] - nFrameLength/2, \
			location[1] - nFrameLength/2, \
			location[0] + nFrameLength/2, \
			location[1] + nFrameLength/2, \
			]
	return frame_coords

    def bCheckTransgress(self, loc, fl, dir=None):
	"""
	Function: If the Frame spills out of the frame,
		transgression is resported.
	Return:
		True: Yes, there is a violation
		False: Safe in the limits.
	"""
	coords = self.arGetFrameCoords(loc, fl)
	if dir == 'Left':
	    if coords[0] <= 2:
		return True 
	if dir == 'Right':
	    if coords[2] >= 256:
		return True
	if dir == 'Up':
	    if coords[1] <= 2:
		return True 
	if dir == 'Down':
	    if coords[3] >= 256:
		return True 
	if (coords[0] <= 2) or (coords[1] <= 2) or (coords[2] <= 2) or (coords[3] <= 2):
	    return True 
	if (coords[0] >= 256) or (coords[1] >= 256) or (coords[2] >= 256) or (coords[3] >= 256):
	    return True
	self.dicMappedZones['LocXY'] = loc
	self.dicMappedZones['Edge'] = fl
	return False
	
    def vRenewFrameInfo(self):
	frame_edge = float(self.oAppNavigator.SliderArea.get())
	fArea, units = self.oScanner.fCalculateSize(self.nFramePixels, \
					frame_edge)
	self.oAppNavigator.LblFrameInfo.configure(text=str(round(fArea,1)) + units + \
							' x ' + \
						str(round(fArea,1)) + units)
	return

    def vClearFrame(self):
	try:
	    self.oAppNavigator.CanvasRefMap.delete(self.FrameBox)
	except:
	    pass
	return

    def vDisplayFrame(self, loc, fl):
	self.vClearFrame()
	frame_coords = self.arGetFrameCoords(loc, fl)
	self.FrameBox = self.oAppNavigator.CanvasRefMap.create_rectangle(frame_coords, \
						outline=self.strFrameColor, \
						width=2, \
						dash=(2,2))
	return

    def BtnUpCB(self, event=None):
	"""
	"""
	newloc = [0]*2
	newloc[0] = self.dicMappedZones['LocXY'][0]
	newloc[1] = self.dicMappedZones['LocXY'][1] - 1
	if self.bCheckTransgress(newloc, self.dicMappedZones['Edge'], 'Up' ):
	    return
	self.oAppNavigator.CanvasRefMap.move(self.FrameBox, 0, -1)
	return

    def BtnDownCB(self, event=None):
	"""
	"""
	newloc = [0]*2
	newloc[0] = self.dicMappedZones['LocXY'][0]
	newloc[1] = self.dicMappedZones['LocXY'][1] + 1
	if self.bCheckTransgress(newloc, self.dicMappedZones['Edge'], 'Down' ):
	    return
	self.oAppNavigator.CanvasRefMap.move(self.FrameBox, 0, 1)
	return

    def BtnLeftCB(self, event=None):
	"""
	"""
	newloc = [0]*2
	newloc[0] = self.dicMappedZones['LocXY'][0] - 1
	newloc[1] = self.dicMappedZones['LocXY'][1]
	if self.bCheckTransgress(newloc, self.dicMappedZones['Edge'], 'Left' ):
	    return
	self.oAppNavigator.CanvasRefMap.move(self.FrameBox, -1, 0)
	return

    def BtnRightCB(self, event=None):
	"""
	"""
	newloc = [0]*2
	newloc[0] = self.dicMappedZones['LocXY'][0] + 1
	newloc[1] = self.dicMappedZones['LocXY'][1]
	if self.bCheckTransgress(newloc, self.dicMappedZones['Edge'], 'Right' ):
	    return
	self.oAppNavigator.CanvasRefMap.move(self.FrameBox, 1, 0)
	return

    def BtnHomeCB(self, event=None):
	"""
	"""
	try:
	    self.oAppNavigator.CanvasRefMap.delete(self.FrameBox)
	except:
	    pass
	self.vShowFrame()
	return

    def BtnDropAnchorCB(self):
	PIEZO_XY = scanner.fGetPiezoXCalibration()	#nm/V
	fRefMapXoffset = (self.dicMappedZones['LocXY'][0] - self.dicScanParam['ImageSize'][0]/2) * self.MV2PIXELS
	fRefMapYoffset = (self.dicScanParam['ImageSize'][0]/2 - self.dicMappedZones['LocXY'][1]) * self.MV2PIXELS
	fNewXoffset = (self.dicScanParam['XOffset'] * 1000. / PIEZO_XY) + fRefMapXoffset 
	fNewYoffset = (self.dicScanParam['YOffset'] * 1000. / PIEZO_XY) + fRefMapYoffset
	#print 'jo', self.dicScanParam['XOffset'], self.dicScanParam['YOffset'], fNewXoffset, fNewYoffset
	[x,y]=self.oOffset.mv2pix(fNewXoffset, fNewYoffset, self.oOffset.oAppOffset.w/2,self.oOffset.oAppOffset.h/2)
	old_y = self.oOffset.arrPath[-1][1]
	self.oOffset.arrPath.append([x, old_y])
	self.oOffset.vShowMarker(fNewXoffset, fNewYoffset)
	self.oOffset.vShowPath(3)
	self.oOffset.vSetTipLocation(fNewXoffset, fNewYoffset)
	self.oOffset.vCleanPath()
	self.vUpdateImageInfoOnMainWindow()
	tkMessageBox.showinfo('Scan Parameters Updated', \
			'Scan Settings updated for the selected frame.', parent=self.oAppNavigator.navigatorGroup)
			
	return

    def vUpdateImageInfoOnMainWindow(self):
	dicNewScanParam = self.dicScanParam.copy()
	if dicNewScanParam['XLArea']:
	    mul_factor = 0.1	# As the slider previously was configured for 10x
	else:
	    mul_factor = 1
	dicNewScanParam['ImageSize'] = [self.nFramePixels]*2
	dicNewScanParam['StepSize'] = [int(self.oAppNavigator.SliderArea.get() * mul_factor)]*2
	self.oScanner.dicScanParam = dicNewScanParam.copy()
	self.oScanner.vDisplayImageInfo()	
	return

    def vUpdateInfo(self, dicparam=None):
	"""
	"""
	if not dicparam:
	    return
	self.PIEZO_XY = scanner.fGetPiezoXCalibration()
	if not dicparam.has_key('XOffset'):
	    xoff = 0
	    dicScanParam['XOffset'] = 0.0
	    print 'Image Parameters not enough..XOffset Missing'
	else:
	    xoff = dicparam['XOffset'] * self.PIEZO_XY/1000
	if not dicparam.has_key('YOffset'):
	    yoff = 0
	    dicScanParam['YOffset'] = 0.0
	    print 'Image Parameters not enough..YOffset Missing'
	else:
	    yoff = dicparam['YOffset'] * self.PIEZO_XY/1000
	if not dicparam.has_key('XLArea'):
	    dicparam['XLArea'] = False
	if dicparam['XLArea']:	
	    self.MV2PIXELS = dicparam['StepSize'][0] * scanner.XL_GAIN
	else:
	    self.MV2PIXELS = dicparam['StepSize'][0]

	size, units = self.oScanner.fCalculateSize(dicparam['ImageSize'][0], \
			dicparam['StepSize'][0], dicparam['XLArea'])
	strRefMapStats = 'Area: ' + str(round(size,1)) + units + \
			' x ' + \
			str(round(size,1))+ units + ', '\
			'Offsets: ' + \
			str(round(xoff,1)) + 'nm' + \
			', ' + \
			str(round(yoff,1)) + 'nm ' #+ \
	self.oAppNavigator.LblImageFile.configure(text=strRefMapStats)
	return

    def vGetStepList(self):
	"""
        Method : vGetStepList
        If Small area is selected then enter 1mV in StepSize 
        else if Large area is selected then enter 5mV.
        If XL then XL_GAIN times (1mV or 5mV) 
        Arguments :
            None
        Returns :
            None
        """
        if self.dicScanParam.has_key('XLArea'):
            #print 'Reference Map Dictionary gas \'XLArea\' key'
	    pass
        else:
            print 'XLArea Key missing ... so considering it a be set false'
	    self.dicScanParam['XLArea'] = False

        if self.dicScanParam['AreaChoice'] == self.oScanner.SMALL_AREA:
            if self.dicScanParam['XLArea']:
                self.arStepList = self.oScanner.xsa_steplist
                self.VoltageSpan = scanner.MAX_SA_SPAN * scanner.XL_GAIN
            else:
                self.arStepList = self.oScanner.sa_steplist
                self.VoltageSpan = scanner.MAX_SA_SPAN
        if self.dicScanParam['AreaChoice'] == self.oScanner.LARGE_AREA:
            if self.dicScanParam['XLArea']:
                self.arStepList = self.oScanner.xla_steplist
                self.VoltageSpan = scanner.MAX_LA_SPAN * scanner.XL_GAIN
            else:
                self.arStepList = self.oScanner.la_steplist
                self.VoltageSpan = scanner.MAX_LA_SPAN
	self.dicSliderParam['from_'] = self.arStepList[0]
	self.dicSliderParam['resolution'] = int(self.arStepList[1]-self.arStepList[0])
        return

    def vGetMaxStepSize(self):
        imsize = self.dicScanParam['ImageSize'][0]
        ss = int(self.VoltageSpan/imsize)
        if self.dicScanParam['AreaChoice'] == self.oScanner.SMALL_AREA:
            if self.dicScanParam['XLArea']:
                #ss -= (ss%scanner.XL_GAIN)
		temp_xsa_steplist = self.oScanner.xsa_steplist + [ss]
		temp_xsa_steplist.sort() 
		i = temp_xsa_steplist.index(ss)
                self.dicSliderParam['to'] = self.oScanner.xsa_steplist[i - 1]
            else:
		temp_sa_steplist = self.oScanner.sa_steplist + [ss]
		temp_sa_steplist.sort() 
		i = temp_sa_steplist.index(ss)
                self.dicSliderParam['to'] = self.oScanner.sa_steplist[i - 1]
        return
 
if __name__ == '__main__':
    navigator()
