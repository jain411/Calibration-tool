#####################
#   Dialogs Class   #
#####################

from Tkinter import *
import tkMessageBox
import tkFileDialog
from tkValidatingEntry import *
import tkColorChooser
import os, sys
import numpy 
import cPickle
import FileDialog		# for test purpose only
from PIL import ImageTk
import stm7 as stm

IMG_EXT = 'npic'
MOV_EXT = 'nmov'

STD_IMG_DIR = os.path.join('/', 'usr', 'share', 'nanoREV', 'images')
logpath      = os.path.join(os.curdir, 'log')
iconpath     = os.path.join('apps','icons')
lut_iconfile = os.path.join(iconpath,'lutfile.png') 
globlogfile  = os.path.join(logpath, 'glob.dat')	
guisettingsfile = os.path.join(logpath, 'gui.dat')	
autosavelog = os.path.join(logpath, 'autosave.log')
trackerlogfile = os.path.join(logpath, 'pathlog.dat')
			
FILETYPES = {}
FILETYPES[IMG_EXT] = ('SiM-5 Files','*.' + IMG_EXT)

dicDefaultGUISettings = { \
    'AreaInfo': ['blue', 'white'], \
    'RoughInfo': ['blue', 'white'], \
    'ZInfo': ['blue', 'white'], \
    'LEC': 'blue', \
    'DLC': 'blue', \
    'AL1C': 'blue', \
    'AL2C': 'blue', \
    'NaviBox': 'blue', \
    }

def dicReadGUISettings():
    try:
    	f = open(guisettingsfile)
    except:
	print 'GUI Global Settings file not found'
	return dicDefaultGUISettings
    dicGUISettings = cPickle.load(f)
    f.close()
    return dicGUISettings

def vWriteGUISettings(dicGUISettings):
    f = open(guisettingsfile, 'w')
    cPickle.dump(dicGUISettings, f)
    f.close()
    return 

def dicGetAutoSaveParam():
    try:
	f = open(autosavelog)
	dicFCParam = cPickle.load(f)
	f.close()
    except:
	print 'AutoSave Log not found'
	return ''
    return dicASParam


class GridDialog(Toplevel):
    def __init__(self, parent, title=None):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.grid(padx=5, pady=5)

        self.wait_visibility()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def cancel(self):
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    def body(self, master):
        pass

    def validate(self):
        pass
        return 1

    def destroy(self):
        '''Destroy the window'''
        self.initial_focus = None
        Toplevel.destroy(self)

    def ok(self, event=None):
        if not self.validate():
                self.initial_focus.focus_set()
                return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

class InitGlobalSettingsDialog(GridDialog):
    def __init__(self, parent, oMainMaster): 
	self.oMainMaster = oMainMaster
	self.bApplyVar = BooleanVar()
	self.bApplyVar.set(False)	
	self.dicGlobParam = {}
	GridDialog.__init__(self, parent ,'Global Settings')
	return

    def body(self, master):
	global lutim
	lutim =ImageTk.PhotoImage(file=lut_iconfile)
	self.master=master
	self._loadranges()
	self.vFillGlobValues()
	textwidth = 12
	header = Label(master, text ='STM Global Settings', fg='blue')
	header.grid(row=0 ,column=0, columnspan=3, sticky=N+E+W+S)	
	self.LabelSettings = LabelFrame(master)
	self.LabelSettings.grid(padx=5, pady=5, columnspan=2)
	i = 1
	self.LabelRun = Label(self.LabelSettings, text='Run Delay(ms)')
	self.LabelRun.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryRun = Entry(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			#repeatdelay=75,\
			#repeatinterval=75,\
			#values=tuple(self.nRunList),\
			#state='readonly',\
			justify=CENTER)
	self.EntryRun.grid(row=i, column=1, sticky=W)	
	i += 1 
	self.LabelAutoWalk = Label(self.LabelSettings, text='AutoWalk Delay(ms)')
	self.LabelAutoWalk.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryAutoWalk = Entry(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			#repeatdelay=75,\
			#repeatinterval=75,\
			#values=tuple(self.nAutoWalkList),\
			#state='readonly',\
			justify=CENTER)
	self.EntryAutoWalk.grid(row=i, column=1, sticky=W)	
	i += 1 
	self.LabelTipMo = Label(self.LabelSettings, text='Tip Motion Speed(V/s)')
	self.LabelTipMo.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryTipMo = Entry(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			#repeatdelay=75,\
			#repeatinterval=75,\
			#values=tuple(self.fTipMoList),\
			#state='readonly',\
			justify=CENTER)
	self.EntryTipMo.grid(row=i, column=1, sticky=W)
	i += 1 
	self.LabelPiezoXY = Label(self.LabelSettings, text='X/Y Calibration(nm/V)')
	self.LabelPiezoXY.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryPiezoXY = Entry(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			#repeatdelay=75,\
			#repeatinterval=75,\
			#values=tuple(self.arfXYCalibrationRange),\
			#state='readonly',\
			justify=CENTER)
	self.EntryPiezoXY.grid(row=i, column=1, sticky=W)
	i += 1 
	self.LabelPiezoZ = Label(self.LabelSettings, text='Z Calibration(nm/V)')
	self.LabelPiezoZ.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryPiezoZ = Entry(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			#repeatdelay=75,\
			#repeatinterval=75,\
			#values=tuple(self.arfZCalibrationRange),\
			#state='readonly',\
			justify=CENTER)
	self.EntryPiezoZ.grid(row=i, column=1, sticky=W)
	i += 1 
	self.LabelHVAGain = Label(self.LabelSettings, text='HVA Gain')
	self.LabelHVAGain.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryHVAGain = Entry(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			#repeatdelay=75,\
			#repeatinterval=75,\
			#values=tuple(self.arfHVAGainRange),\
			#state='readonly',\
			justify=CENTER)
	self.EntryHVAGain.grid(row=i, column=1, sticky=W)
	i += 1 
	self.LabelColor = Label(self.LabelSettings, text='Color Mode')
	self.LabelColor.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryColor = Spinbox(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			repeatdelay=75,\
			repeatinterval=75,\
			values=tuple(self.sColorList),\
			state='readonly',\
			justify=CENTER)
	self.EntryColor.grid(row=i, column=1, sticky=W)
	i += 1 	
	self.LabelZPol = Label(self.LabelSettings, text='Z Polarity')
	self.LabelZPol.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryZPol = Spinbox(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			repeatdelay=75,\
			repeatinterval=75,\
			values=tuple(self.sZList),\
			state='readonly',\
			justify=CENTER)
	self.EntryZPol.grid(row=i, column=1, sticky=W)
	i += 1 	
	self.LabelZoffsetGain = Label(self.LabelSettings, text='Z-Offset Gain')
	self.LabelZoffsetGain.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryZoffsetGain = Entry(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			justify=CENTER)
	self.EntryZoffsetGain.grid(row=i, column=1, sticky=W)
	i += 1 	
	self.LabelLUT = Label(self.LabelSettings, text='Look Up Table')
	self.LabelLUT.grid(row=i, column=0, sticky=W, padx=3)
	self.ButLUT = Button(self.LabelSettings, \
				image = lutim,\
				relief= FLAT,\
				bg='light gray',\
				overrelief=RAISED,\
				command=self.vLoadLUT)
	self.ButLUT.grid(row=i, column=1, sticky=N+W+E+S)	
	i += 1 	
	self.LabelCamMode = Label(self.LabelSettings, text='Camera Mode')
	self.LabelCamMode.grid(row=i, column=0, sticky=W, padx=3)
	self.EntryCamMode = Spinbox(self.LabelSettings, \
			bg='light gray',\
			width=textwidth,\
			relief=FLAT,\
			repeatdelay=75,\
			repeatinterval=75,\
			values=tuple(self.sCamList),\
			state='readonly',\
			justify=CENTER)
	self.EntryCamMode.grid(row=i, column=1, sticky=W)

	self.BtnApply = Button(master, text='Apply', width=7, command=self.vOkCB)
	self.BtnApply.grid(row=10, column=0, padx=3, pady=3, sticky=N+E+W+S)
	self.BtnCancel = Button(master, text='Cancel', command=self.vCancelCB)
	self.BtnCancel.grid(row=10, column=1, padx=3, pady=3, sticky=N+E+W+S)
	self.vPopulateEntries()
	return

    def _loadranges(self):
	#self.nRunList = range(10,201,1)
	#self.nAutoWalkList= range(1,21,1)
	#self.fTipMoList = numpy.arange(0.5,5.1,0.1)
	#self.arfXYCalibrationRange = numpy.arange(5.0,50.1,0.1)	
	#self.arfZCalibrationRange = numpy.arange(1.0,50.1,0.1)	
	#self.arfHVAGainRange = numpy.arange(5.0,20.1,0.1)	
	self.sColorList = ['Gray', 'RGB']
	self.sZList = ['Negative', 'Positive']
	self.sCamList = ['IN SIM CAMERA', 'THIRD PARTY']
	return

    def vLoadLUT(self):
	oFDialog=FileDialog.LoadFileDialog(self.oMainMaster.master)
	sLUTPath = os.path.split(self.dicGlobParam['lutfile'])[0]
	sLUTFile = FileDialog.LoadFileDialog.go(oFDialog, sLUTPath, '*.lut')
	if sLUTFile == None:
	    return
	self.dicGlobParam['lutfile'] = sLUTFile
	return 


    def vOkCB(self):
	self.dicGlobParam['RunDelay'] = int(self.EntryRun.get())
	self.dicGlobParam['AutoWalkDelay'] = int(self.EntryAutoWalk.get())
	self.dicGlobParam['TipMotionSpeed'] = float(self.EntryTipMo.get())
	self.dicGlobParam['XCalibration'] = float(self.EntryPiezoXY.get())
	self.dicGlobParam['YCalibration'] = self.dicGlobParam['XCalibration'] 
	self.dicGlobParam['ZCalibration'] = float(self.EntryPiezoZ.get())
	self.dicGlobParam['Color'] = self.EntryColor.get()
	self.dicGlobParam['ZPolarity'] = self.EntryZPol.get()
	self.dicGlobParam['ZoffsetGain'] = float(self.EntryZoffsetGain.get())
	self.dicGlobParam['HVAGain'] = float(self.EntryHVAGain.get())
	self.dicGlobParam['CamMode'] = self.EntryCamMode.get()
	print self.dicGlobParam
	f = open(globlogfile, 'w')
	cPickle.dump(self.dicGlobParam, f)
	f.close()
	self.bApplyVar.set(True)
	self.ok()

    def vPopulateEntries(self):
        self.EntryRun.delete(0, END)
	self.EntryRun.insert(0, int(self.dicGlobParam['RunDelay']))
        self.EntryAutoWalk.delete(0, END)
	self.EntryAutoWalk.insert(0, int(self.dicGlobParam['AutoWalkDelay']))
	self.EntryTipMo.delete(0, END)
	self.EntryTipMo.insert(0, round(self.dicGlobParam['TipMotionSpeed'], 1))
	self.EntryPiezoXY.delete(0, END)
	self.EntryPiezoXY.insert(0, round(self.dicGlobParam['XCalibration'], 1))
	self.EntryPiezoZ.delete(0, END)
	self.EntryPiezoZ.insert(0, round(self.dicGlobParam['ZCalibration'], 1))
	while self.EntryColor.get() != self.dicGlobParam['Color']:
		self.EntryColor.invoke('buttonup')
	while self.EntryZPol.get() != self.dicGlobParam['ZPolarity']:
		self.EntryZPol.invoke('buttonup')
        self.EntryHVAGain.delete(0, END)
	self.EntryHVAGain.insert(0, round(self.dicGlobParam['HVAGain'], 1))
        self.EntryZoffsetGain.delete(0, END)
	self.EntryZoffsetGain.insert(0, round(self.dicGlobParam['ZoffsetGain'], 1))
	while self.EntryCamMode.get() != self.dicGlobParam['CamMode']:
		self.EntryCamMode.invoke('buttonup')
	return

    def vFillGlobValues(self):
	try:
		f=open(globlogfile)	
		dicPrevParam = cPickle.load(f)
		f.close()
		self.dicGlobParam = dicPrevParam.copy()
	except:
		pass	
	return

    def vCancelCB(self):
	self.cancel()

    def apply(self):
	pass

class GuiSettingsDialog(GridDialog):
#class GuiSettingsDialog:
    def __init__(self, parent): 
	self.bApplyVar = BooleanVar() 
	self.bApplyVar.set(False)
	#self.master=parent
	#self.__initConfigure()
	GridDialog.__init__(self, parent ,'GUI Settings')
	#self.master.title('GUI Settings')
	return

    def body(self, master):
	self.master=master
	self.__initConfigure()
	return

    def __initConfigure(self):
	self.dicGUISettings = dicReadGUISettings()
	header = Label(self.master, text ='GUI Color Settings', fg='blue')
	header.grid(row=0 ,column=0, sticky=N+E+W+S, columnspan=2)	
	self.LabelSettings = LabelFrame(self.master)
	self.LabelSettings.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
	i = 0
	self.LabelAreaInfo = Label(self.LabelSettings , text='Area Info (Top-Left): ')
	self.LabelAreaInfo.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnAreaInfo = Button(self.LabelSettings , text='', bg=self.dicGUISettings['AreaInfo'][0], \
					command=self.vSelAreaInfoColor ,\
					activebackground=self.dicGUISettings['AreaInfo'][0])
	self.BtnAreaInfo.grid(row=i, column=1, sticky=W, padx=3)
	self.BtnAreaInfoActive = Button(self.LabelSettings , text='', bg=self.dicGUISettings['AreaInfo'][1], \
					command=self.vSelAreaInfoActiveColor  ,\
					activebackground=self.dicGUISettings['AreaInfo'][1])
	self.BtnAreaInfoActive.grid(row=i, column=2, sticky=W, padx=3)
	i+=1
	self.LabelRoughInfo = Label(self.LabelSettings , text='Roughness Info: ')
	self.LabelRoughInfo.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnRoughInfo = Button(self.LabelSettings , text='', bg=self.dicGUISettings['RoughInfo'][0], \
					command=self.vSelRoughInfoColor ,\
					activebackground=self.dicGUISettings['RoughInfo'][0])
	self.BtnRoughInfo.grid(row=i, column=1, sticky=W, padx=3)
	self.BtnRoughInfoActive = Button(self.LabelSettings , text='', bg=self.dicGUISettings['RoughInfo'][1], \
					command=self.vSelRoughInfoActiveColor  ,\
					activebackground=self.dicGUISettings['RoughInfo'][1])
	self.BtnRoughInfoActive.grid(row=i, column=2, sticky=W, padx=3)
	
	i+=1
	self.LabelZInfo = Label(self.LabelSettings , text='Z-Info on Color Map: ')
	self.LabelZInfo.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnZInfo = Button(self.LabelSettings , text='', bg=self.dicGUISettings['ZInfo'][0], \
					command=self.vSelZInfoColor ,\
					activebackground=self.dicGUISettings['ZInfo'][0])
	self.BtnZInfo.grid(row=i, column=1, sticky=W, padx=3)
	self.BtnZInfoActive = Button(self.LabelSettings , text='', bg=self.dicGUISettings['ZInfo'][1], \
					command=self.vSelZInfoActiveColor ,\
					activebackground=self.dicGUISettings['ZInfo'][1])
	self.BtnZInfoActive.grid(row=i, column=2, sticky=W, padx=3)
	
	i+=1
	self.LabelLEC = Label(self.LabelSettings , text='Line Ext. Color: ')
	self.LabelLEC.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnLEC = Button(self.LabelSettings , text='', bg=self.dicGUISettings['LEC'] ,\
					command=self.vSelLEColor,\
					activebackground=self.dicGUISettings['LEC'])
	self.BtnLEC.grid(row=i, column=1, sticky=W, padx=3)

	i+=1
	self.LabelDLC = Label(self.LabelSettings , text='Distance Line Color: ')
	self.LabelDLC.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnDLC = Button(self.LabelSettings , text='', bg=self.dicGUISettings['DLC'], \
					command=self.vSelDLColor,\
					activebackground=self.dicGUISettings['DLC'])
	self.BtnDLC.grid(row=i, column=1, sticky=W, padx=3)

	i+=1
	self.LabelAL1C = Label(self.LabelSettings , text='Angle Line 1: ')
	self.LabelAL1C.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnAL1C = Button(self.LabelSettings , text='', bg=self.dicGUISettings['AL1C'], \
					command=self.vSelAL1Color ,\
					activebackground=self.dicGUISettings['AL1C'])
	self.BtnAL1C.grid(row=i, column=1, sticky=W, padx=3)
	i+=1
	self.LabelAL2C = Label(self.LabelSettings , text='Angle Line 2: ')
	self.LabelAL2C.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnAL2C = Button(self.LabelSettings , text='', bg=self.dicGUISettings['AL2C'], \
					command=self.vSelAL2Color ,\
					activebackground=self.dicGUISettings['AL2C'])
	self.BtnAL2C.grid(row=i, column=1, sticky=W, padx=3)

	i+=1
	self.LabelNBC = Label(self.LabelSettings , text='Resizable Box: ')
	self.LabelNBC.grid(row=i, column=0, sticky=W, padx=3)
	self.BtnNBC = Button(self.LabelSettings , text='', bg=self.dicGUISettings['NaviBox'], \
					command=self.vSelNaviBoxColor ,\
					activebackground=self.dicGUISettings['NaviBox'])
	self.BtnNBC.grid(row=i, column=1, sticky=W, padx=3)

	i+=1
	self.BtnDefault = Button(self.LabelSettings , text='Set Default Settings', \
				command=self.vSetDefaultCB \
				)
	self.BtnDefault.grid(row=i, column=0, columnspan=3, sticky=N+E+W+S, padx=3)

	self.BtnApply = Button(self.master, text='Apply', width=7, command=self.vOkCB)
	self.BtnApply.grid(row=3, column=0, padx=3, pady=3, sticky=N+E+W+S)
	self.BtnCancel = Button(self.master, text='Cancel', command=self.vCancelCB)
	self.BtnCancel.grid(row=3, column=1, padx=3, pady=3, sticky=N+E+W+S)
	return

    def nSelColor(self):
	color = tkColorChooser.askcolor(title='Color Chooser')
        if (color[0] == None) or (color[1] == None):
            return None
	return color[1]

    def vSelAreaInfoColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['AreaInfo'][0] = str(color)
	self.BtnAreaInfo.config(bg=color, activebackground=color) 
        return

    def vSelAreaInfoActiveColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['AreaInfo'][1] = str(color)
	self.BtnAreaInfoActive.config(bg=color, activebackground=color) 
	return

    def vSelRoughInfoColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['RoughInfo'][0] = str(color)
	self.BtnRoughInfo.config(bg=color, activebackground=color) 
	return

    def vSelRoughInfoActiveColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['RoughInfo'][1] = str(color)
	self.BtnRoughInfoActive.config(bg=color, activebackground=color) 
	return

    def vSelZInfoColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['ZInfo'][0] = str(color)
	self.BtnZInfo.config(bg=color, activebackground=color) 
	return

    def vSelZInfoActiveColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['ZInfo'][1] = str(color)
	self.BtnZInfoActive.config(bg=color, activebackground=color) 
	return

    def vSelDLColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['DLC'] = str(color)
	self.BtnDLC.config(bg=color, activebackground=color) 
	return

    def vSelLEColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['LEC'] = str(color)
	self.BtnLEC.config(bg=color, activebackground=color) 
	return

    def vSelAL1Color(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['AL1C'] = str(color)
	self.BtnAL1C.config(bg=color, activebackground=color) 
	return

    def vSelAL2Color(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['AL2C'] = str(color)
	self.BtnAL2C.config(bg=color, activebackground=color) 
	return

    def vSelNaviBoxColor(self):
	color = self.nSelColor()
	if not color:
	    return
        self.dicGUISettings['NaviBox'] = str(color)
	self.BtnNBC.config(bg=color, activebackground=color) 
        #self.oAppNavigator.CanvasRefMap.itemconfig(self.FrameBox, outline=self.strFrameColor)
	return

    def vSetDefaultCB(self):
	self.dicGUISettings = dicDefaultGUISettings 
	self.BtnAreaInfo.config(bg=dicDefaultGUISettings['AreaInfo'][0] , activebackground=dicDefaultGUISettings['AreaInfo'][0] ) 
	self.BtnAreaInfoActive.config(bg=dicDefaultGUISettings['AreaInfo'][1] , activebackground=dicDefaultGUISettings['AreaInfo'][1] ) 
	self.BtnRoughInfo.config(bg=dicDefaultGUISettings['RoughInfo'][0] , activebackground=dicDefaultGUISettings['RoughInfo'][0] ) 
	self.BtnRoughInfoActive.config(bg=dicDefaultGUISettings['RoughInfo'][1] , activebackground=dicDefaultGUISettings['RoughInfo'][1] ) 
	self.BtnZInfo.config(bg=dicDefaultGUISettings['ZInfo'][0] , activebackground=dicDefaultGUISettings['ZInfo'][0] ) 
	self.BtnZInfoActive.config(bg=dicDefaultGUISettings['ZInfo'][1] , activebackground=dicDefaultGUISettings['ZInfo'][1] ) 
	self.BtnDLC.config(bg=dicDefaultGUISettings['DLC'] , activebackground=dicDefaultGUISettings['DLC'] ) 
	self.BtnLEC.config(bg=dicDefaultGUISettings['LEC'] , activebackground=dicDefaultGUISettings['LEC'] ) 
	self.BtnAL1C.config(bg=dicDefaultGUISettings['AL1C'] , activebackground=dicDefaultGUISettings['AL1C'] ) 
	self.BtnAL2C.config(bg=dicDefaultGUISettings['AL2C'] , activebackground=dicDefaultGUISettings['AL2C'] ) 
	self.BtnNBC.config(bg=dicDefaultGUISettings['NaviBox'] , activebackground=dicDefaultGUISettings['NaviBox'] ) 
	return

    def vOkCB(self):
	#print self.dicGUISettings
	vWriteGUISettings(self.dicGUISettings)
	self.bApplyVar.set(True)
	self.ok()

    def apply(self):
	pass

    def vCancelCB(self):
	self.cancel()

def SaveImageDialog(ext='.npic', message='Do you want to \n save current Image...', parent=None):
    """
    dicASParam = dicGetAutoSaveParam()
    if dicASParam == '':
    	filepath = dialogs.strPathTracker()
        if tkMessageBox.askyesno('Save', message):
	    filename = tkFileDialog.asksaveasfilename(defaultextension=ext, initialdir=filepath)
	    strPathTracker(filename)
	    return filename
	else:
	    return None
    else:
	filepath = dicASParam['Path']
	filename = str
    """
    filepath = strPathTracker()
    if filepath.find('usr') > 1:	# staying away from default images/install directory
	filepath = os.getenv('HOME')
    if tkMessageBox.askyesno('Save', message, parent=parent):
	filename = tkFileDialog.asksaveasfilename(parent=parent, defaultextension=ext, initialdir=filepath)
	strPathTracker(filename)
	return filename
    else:
	return None

def OpenImageDialog(ext=None, parent = None):
    filepath = strPathTracker()
    if ext == MOV_EXT:
        ftype=[('Movie Files','*.' + MOV_EXT)]
        filename = tkFileDialog.askopenfilename(defaultextension=ext, \
                                        filetypes=ftype, \
                                        initialdir=filepath, \
					parent = parent)
        if filename != None:
            strPathTracker(filename)
        return filename
    if ext == None:
        ftype = FILETYPES.values()
    else:
        ftype = [FILETYPES[ext]]
    filename = tkFileDialog.askopenfilename(defaultextension=ext, \
                                        filetypes=ftype, \
                                        initialdir=filepath)
    if filename != None:
        strPathTracker(filename)
    return filename

def strPathTracker(filename=None):
    if not filename:
	try:
	    fd = open(trackerlogfile)
	except:
	    return os.getenv('HOME')
	oldpath = fd.readline().strip()	# removes newline
	fd.close()
	if (oldpath.find('/usr') > 1) or (os.path.isdir(oldpath) == False):	# staying away from install or invalid directories
	    if sys.platform == 'linux2':
		oldpath = STD_IMG_DIR
	    else:
		oldpath = os.getenv('HOME')
	return oldpath
    else:
	path = os.path.split(filename)[0]
	#path = string.join(path, os.sep)
	try:
	    fd = open(trackerlogfile,'w')
	except:
	    print 'Cant open path-tracker logfile'
	    return
	fd.write(path+'\n')		# logging path ...yeah kept for historic reasons
	fd.write(filename)		# logging filename
	fd.close()
	return

def astrFileCount(path):
    """
    Opens file counter log file and gives the new count
    in the specified directory (using AutoSaveSettings).
    """
    file_list = os.listdir(path)
    file_list.sort()
    k = []
    for file in file_list:
        if file.split(os.extsep)[-1] == IMG_EXT:
	    try:
		int(file.split(os.extsep)[0])
	    except:
	        k.append(file)
    strLastFile = files[-1].split(os.sep)
    try:
        nLastCount = int(strLastFile.split(os.extsep))
    except:
	pass
    strFileCount = '0' * (len(str(maxcount)) - len(str(index))) + str(index) 
    return [strDir, strFileCount]
	
### Only for testing #####
if __name__ == '__main__':
	root = Tk()
	InitalSTMSettingsDialog(root)
	root.mainloop()
