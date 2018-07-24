#!/usr/bin/python2
########################
#   MainWindow Class   #
########################   
#########################################
# This code for nanoREV User interface  #
# is written completely at              #
# Quazar Technologies Pvt. Limited      #
# Special Thanks to:                    #
# Dr. Ajith B.P.(IUAC, New Delhi) for   #
# introducing me to the beautiful world #
# of python.                            #
# This code is proprietary of :         #
# M/s Quazar Technologies Pvt. Ltd. It  #
# cannot be used/modified/copied w/o    #
# permission from them.                 #
# Quazar Technologies aims to provide a #
# user-friendly, collaborative and open #
# environment for software development  #
# in sync with the Open Source spirit.  #
#########################################

import os, time
import tkMessageBox, tkSimpleDialog

menu_font_type = ("Verdana", 12, 'normal')

defaultlut   = os.path.join(os.curdir, 'lut', 'default.lut')
dicDefaultGlobalParam = { \
    ## WALKER ##
    'RunDelay' : 50, \
    'AutoWalkDelay' : 500, \
    'ZPolarity' : 'Negative', \
    ## OFFSET ##
    'TipMotionSpeed' : 2.5, \
    'ZoffsetGain' : 10.0, \
    ## SCANNER ##
    'XCalibration'  : 13.5, \
    'YCalibration'  : 13.5, \
    'ZCalibration'  : 5.0, \
    'HVAGain' : 10.0, \
    'TipParkingMode' : 'center', \
    ## IMAGING ##
    'Color' : 'RGB', \
    'lutfile' : defaultlut, \
    ## DEVICE LIST ##
    'DeviceList':['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',\
		'/dev/tts/USB0','/dev/tts/USB1',\
		'COM2','COM3','COM4','COM5','COM6',\
                'COM7','COM8','COM9','COM10','COM11','COM12',1,2,3],\
    'CamMode':'IN SIM CAMERA'
    }

def main():
    """
    Kick starts the main application
    """
    print 'Loading Application Window...'
    root = Tk()
    #with splash.SplashScreen(root):
    m = MainWindow(root)
    root.mainloop()
    return

def addpath():
    """
    Adds iprog to system paths
    """
    add_libs()
    add_apps()
    add_modules()
    add_utilities()
    #add_logger()    
    return

def add_libs():
    """
    Add apps's members  to system paths
    """
    lib = os.path.join(os.getcwd(),'lib')
    sys.path.append(lib)
    return

def add_apps():
    """
    Add apps's members  to system paths
    """
    apps = os.path.join(os.getcwd(),'apps')
    sys.path.append(apps)
    return

def add_modules():
    """
    Add modules's members to system paths
    """
    module_dir = os.path.join(os.getcwd(), 'modules')
    modules_list = os.listdir(module_dir)
    for module in modules_list:
        if module[0] != '.':                #skip hidden files
            full_filename = os.path.join(module_dir, module)
            sys.path.append(full_filename)
    return

def add_utilities():
    """
    Add utilities's members to system paths
    """
    utilities_dir = os.path.join(os.getcwd(), 'utilities')
    utilities_list = os.listdir(utilities_dir)
    for utility in utilities_list:
        if utility[0] != '.':               #skip hidden files
            full_filename = os.path.join(utilities_dir, utility)
            sys.path.append(full_filename)
    return

def add_logger():
    """
    Add logger's members to system paths
    """
    log = os.path.join(os.getcwd(),'logger')
    sys.path.append(log)
    return

class MainWindow:
    def __init__(self, master):
        """
        Class Contructor : MainWindow
        """
        self.master = master
        self.master.title('SIM-Stm IMproved')
	self.master.resizable(False, False)
	#self.master.wm_iconbitmap('sim.ico')
        self._glob_settings()
        self._openStm()
        self.vCheckSTMDriver()
        #self._glob_settings()
        self._create_widgets()
        self._create_links()
        self.vLoadGlobParameters()
        return

    def _openStm(self):
        """
        Links Stm object to MainWindow class
        """
        self.oStm = stm.stm()
        return
 
    def _create_widgets(self):
        """
        Fits SiM widgets in the Main Window
        """
        self._CRO ()
        self._ScanSettings()
        self._ToolBar() 
        self._OffsetSettings()
        self._WalkerSettings()
        self._MainMenubar()
        self._ImagingWindow()
        return

    def _MainMenubar(self):
        """
        Forms Main SiM window
        """ 
        self._createMainMenubar()
        return

    def _ScanSettings(self):
        """
        Packs Scanner Window 
        """
        self._createSSwidgets()
        return

    def _WalkerSettings(self):
        """
        Packs Walker Window
        """
        self._createWSwidgets()
        return

    def _ImagingWindow(self):
        """
        Packs Imaging Window 
        """
        self._createIWwidgets()
        return

    def _ColormapWindow(self):
        """
        Packs Colormap Window 
        """
        self._createCwidgets()
        return

    def _CRO(self):
        """
        Packs Infobox Window
        """
        self._createCROwidgets ()
	self.oCRO = cro.cro (self.FrameCRO, self.oStm)
        return

    def _OffsetSettings(self):
        """
        Packs Offset Window
        """
        self._createOSwidgets()
        return

    def _LithoSettings(self):
        """
        Packs Lithography Window
        """
        self._createLSwidgets()
        return

    def _ToolBar(self):
        """
        Packs Toolbar Window
        """
        self._createTBwidgets()
        return

    def _createMainMenubar(self):
        """
        Packs MenuBar Window
        """
        self.oMenubar = menubar.menubar(self.master, self.oToolBar)
        return

    def _createTBwidgets(self):
        """
        Loads Toolar Widgets in ToolBar Window
        """
        self.FrameToolBar = Frame(self.master, relief=RAISED, borderwidth=1)
        self.FrameToolBar.grid(row=0, column=0, sticky=N+W+E+S, columnspan=4)
        self.oToolBar = toolbar.toolbar(self.FrameToolBar)
        self.oToolBar.vGetStm(self.oStm)
        self.oToolBar.vGetMain(self.master)
        self.master.protocol('WM_DELETE_WINDOW',self.oToolBar.BtnExitCB)
        return

    def oToolBar(self):
        """
        Returns toolbar object
        """
        return self.oToolBar
    
    def _createWSwidgets(self):
        """
        Loads Walker widgets in Walker Window
        """
        self.WalkerFrame = Frame(self.master, borderwidth=3) 
        self.WalkerFrame.grid(row=2, column=0, sticky=N+W)
        self.oWalker = walker.walker(self.WalkerFrame, self.oStm)
        return

    def _createSSwidgets(self):
        """
        Loads Scanner widgets in Scanner Window
        """
        self.ScannerFrame = Frame(self.master, borderwidth=3)
        self.ScannerFrame.grid(row=1, column=0, sticky=N+W)
        self.oScanner = scanner.scanner(self.ScannerFrame, self.oStm)
        return

    def _createIWwidgets(self):
        """
        Loads Imaging widgets in Imaging Window
        """
        self.ImagingFrame = Frame(self.master)
        self.ImagingFrame.grid(row=1, column=1, \
                    columnspan=2, sticky=N+S, pady=3)
        self.oImaging = imaging.imaging(self.ImagingFrame)
        return
    
    def oImaging(self):
        """
        Returns Imaging object
        """
        return self.imObj

    def _createOSwidgets(self):
        """
        Loads Offset widgets in Offset Window
        """
        self.OffsetFrame = Frame(self.master, borderwidth=3)
        self.OffsetFrame.grid(row=2, column=1, sticky=N+W)
        self.oOffset = offset.offset(self.OffsetFrame, self.oStm)
        return

    def _createCROwidgets(self):
        """
        Loads CRO widgets in CRO frame 
        """
        self.FrameCRO = Frame(self.master, borderwidth=3)
        self.FrameCRO.grid(row=2, column=2, sticky=W, columnspan=2)
        return

    def _create_links(self):
        """
        Forms Links between different classes by passing class objects
        """ 
        self.oToolBar.vGetMain(self.master)
        self.oToolBar.vGetWalker(self.oWalker)  
        self.oToolBar.vGetScanner(self.oScanner)
        self.oToolBar.vGetOffset(self.oOffset)
        self.oToolBar.vGetImaging(self.oImaging)    
        self.oWalker.vGetScanner(self.oScanner)
        self.oWalker.vGetOffset(self.oOffset)
        self.oWalker.vGetToolBar(self.oToolBar) 
        self.oWalker.vGetMenuBar(self.oMenubar)
        self.oWalker.vGetMainMaster(self.master)
        self.oOffset.vGetScanner(self.oScanner)
        self.oOffset.vGetMainMaster(self.master)
        self.oOffset.vGetWalker(self.oWalker)
        self.oOffset.vGetToolBar(self.oToolBar)
        self.oOffset.vGetMenuBar(self.oMenubar)
        self.oScanner.vGetOffset(self.oOffset)
        self.oScanner.vGetMain(self.master) 
        self.oScanner.vGetImaging(self.oImaging)
        self.oScanner.vGetWalker(self.oWalker)
        self.oScanner.vGetToolBar(self.oToolBar)
        self.oScanner.vGetMenuBar(self.oMenubar)
        self.oScanner.vGetCRO (self.oCRO)
        self.oImaging.vGetScanner(self.oScanner)
        self.oImaging.vGetMain(self.master)
        self.oMenubar.vGetImaging(self.oImaging)
        self.oMenubar.vGetWalker(self.oWalker)
        self.oMenubar.vGetMain(self)
        return

    def _glob_settings(self):
        """
        Reads Global Settings file and updates user select global parameters
        """
        try:
            self.dicGlobParam = scanner.dicReadGlobalParam()
	    for key in dicDefaultGlobalParam.keys():
		# This length comparision is to update make the new key 
		if not self.dicGlobParam.has_key(key):
			print 'Yepp..new key', key
			self.dicGlobParam[key] = dicDefaultGlobalParam[key]
	    scanner.vWriteGlobalParam(self.dicGlobParam)
        except:
            self.dicGlobParam = dicDefaultGlobalParam
            scanner.vWriteGlobalParam(self.dicGlobParam)
            return
        return

    def vLoadGlobParameters(self):
        """
        Updates Global Parameters   
        """
        walker.RUN_DELAY = self.dicGlobParam['RunDelay']/1000.
        walker.AUTOWALK_DELAY = self.dicGlobParam['AutoWalkDelay']/1000.
        #stm.TIP_VELOCITY = self.dicGlobParam['TipMotionSpeed']
        #scanner.PIEZO_XY = self.dicGlobParam['XCalibration']
        #scanner.PIEZO_Z = self.dicGlobParam['ZCalibration']
        if self.dicGlobParam['Color']=='Gray':
            self.oImaging.strModeVar.set('I')
        if self.dicGlobParam['Color']=='RGB':
            self.oImaging.strModeVar.set('RGB')
        if self.dicGlobParam['ZPolarity']=='Negative':
            self.oWalker.PiezoVar.set(self.oWalker.N_POL)
        if self.dicGlobParam['ZPolarity']=='Positive':
            self.oWalker.PiezoVar.set(self.oWalker.P_POL)
        lutfile=self.dicGlobParam['lutfile']
        self.oImaging.vDisplaylutFile(lutfile)
        if self.oImaging.bImagePresentVar.get()==True:      # if image is present then update it 
            self.oImaging.oQlaunch.vOriginalCB()    
        return

    def vUpdateGlobParam(self):
        """
        Pops out Global Settings Dialog
        """
        d = dialogs.InitGlobalSettingsDialog(self.master, self)
        if d.bApplyVar.get() == True:
            self._glob_settings()
            self.vLoadGlobParameters()
        return

    def vAddNewPort(self):
        portname = tkSimpleDialog.askstring('Any Other Port', 'Enter Port Name:')
        if portname != None:    
            self.dicGlobParam = scanner.dicReadGlobalParam()
            self.dicGlobParam['DeviceList'].append(portname)
            scanner.vWriteGlobalParam(self.dicGlobParam)
            tkMessageBox.showinfo('New Port Added','Please Restart Application')
        return
    
    def vCheckSTMDriver(self):
        """
        Checks whether stm driver has been in the kernel space or not
        """
        if self.oStm.fd == None:
	    print 'Trying again ... '
	    #self.oStm.vDetectSTM()
	    if self.oStm.bValidDevice() == False:
		print 'Still could not detect nanoREV ... '
        return

if __name__ == "__main__":
   import os
   os.chdir (os.path.dirname (__file__))
   import sys
   addpath()
   from Tkinter import *
   print 'Loading STM modules. .', 
   import stm7 as stm
   print '.', 
   import cro 
   import scanner
   import toolbar
   import menubar
   import imaging
   import offset
   import walker
   import litho
   import dialogs
   import splash
   main()

