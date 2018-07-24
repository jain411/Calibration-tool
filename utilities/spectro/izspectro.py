#######################
#  I-Z Spectro Class  #
#######################
import os, numpy, cPickle, time, string, pylab
import tkMessageBox, tkFileDialog, tkSimpleDialog, FileDialog
from PIL import Image, ImageTk

from apps import dialogs
from modules.offset import offset
from modules.scanner import scanner
from utilities.iprog import iprog
from lib import stm7 as stm
from utilities.lia import xlia
import app_izspectro

logpath         = os.path.join(os.curdir, 'log')
globlogfile     = os.path.join(logpath, 'glob.dat')

IZEXT = 'nrviz'

canvas_font = ('Times', 24, 'bold')

__DEBUG__ 		= True

if __DEBUG__ == True:
	from Tkinter import *

def izspectro(f=None, oStm=None):
    """
    Returns IZSpectro object
    """
    if not f:
	oStm = stm.stm()
	root = Tk()
    oAppIZSpectro = app_izspectro.app_izspectro()
    oAppIZSpectro.createIZSwindow(f)
    oIZSpectro = IZSpectro(oAppIZSpectro, oStm)
    if not f :
	root.title('I-Z Spectroscopy')
	root.mainloop()
    return oIZSpectro


class IZSpectro:
    """
    I-Z Spectroscopy Tool
    """
    TC_UPPER_LIMIT	= 10000		# Z motion stops when T.C. reaches upper limit
    MIN_ZOFFSET		= offset.MIN_ZOFFSET
    MAX_ZOFFSET		= offset.MAX_ZOFFSET
    ZDAC_RES		= stm.ZDAC_RESOLUTION
    # min ZDAC resolution  = 5mV, Zhi gain = 10
    #MIN_STEPSIZE 	= offset.XL_GAIN * ZDAC_RES	# Minimum Z-Offset StepSize 10 * 5mV = 50mV
    #MIN_STEPSIZE 	= ZDAC_RES	# Minimum Z-Offset StepSize 5mV	(The 10x gain on Zoffset is removed)
    MIN_STEPSIZE	= ZDAC_RES * offset.fGetZoffsetGain()
    MIN_STEPS 		= 800		# No. of steps taken in Z dir (each of fixed span) 
    MAX_STEPS 		= 8500
    STEP_RES		= 200		# Jumps in no. of steps
    MIN_PRESPECDELAY 	= 1		# Waiting time (in msec) before taking IZ spectra
    MAX_PRESPECDELAY 	= 20
    MIN_MAVG 		= 4		# No. of T.C. readings (from ADC) averaged 
    MAX_MAVG 		= 64
    MIN_SWEEPS 		= 1		# Number of Sweeps
    MAX_SWEEPS 		= 10
    
    def __init__(self, oAppIZSpectro, oStm):
	"""
	Class Contructor
	"""
	self.oStm=oStm						
	self.nFramePixels = 256		# Pixels in the Image Canvas
	self.MAX_SPECTRO_POINTS = 10	# i.e. no. of markers that can be set
	self.vFindScannerPolarity()	# Determine Polarity of Scanner Piezo 
	self.vFindCurrentSetPoint()
	#### Initial Values of Sprectro Settings #####
	# Scanner Polarity determines what is the state(Stretched/Retracted) at a given volatge.
	if self.strScannerPolarity == 'Negative':
	    self.nFullStretch = self.MAX_ZOFFSET	
	    self.nRetractDir = -1
	else:
	    self.nFullStretch = self.MIN_ZOFFSET
	    self.nRetractDir = 1
	self.nFullRetract = -1.0 * self.nFullStretch

	self.nNoOfSteps = 50
	self.nStepDelay = 100		# in usec
	self.nPreSpectrumDelay = 1	# in msec
	self.nMovAvgPoints = 4
	self.dicSpecParam = {}

	self.anStepList = numpy.arange (self.MIN_STEPS, \
			self.MAX_STEPS + self.STEP_RES, \
			self.STEP_RES)
	self.anMovAvgList = range (self.MIN_MAVG, self.MAX_MAVG, self.MIN_MAVG)
	self.anSweepList = range (self.MIN_SWEEPS, self.MAX_SWEEPS)
	self.bStopLoggingVar = BooleanVar ()
	self.strPlotVar = StringVar ()
	self.strPlotVar.set ('IZ')
	self.bStopLoggingVar.set (False)
	self.oAppIZSpectro = oAppIZSpectro
	self.cSpectroModeVar = StringVar ()
	self._configureCB()
	self.colorcode = [	'black', '#2F4F4F', 'blue', 'red', 'cyan', \
				'white', 'magenta','green', 'yellow', '#FF4500']
	self.strCurrentSpecFile = None
	return

    def vGetScanner(self, oScanner):
	"""
	Links object Scanner to Spectro class
	"""
	self.oScanner = oScanner
	return


    def _configureCB(self):
	"""
	Attaches Callbacks to IZSpectroGui widgets 
	"""
        self.oAppIZSpectro.filemenu.add_command(label='Open I-Z Spectro File', \
                                                command=self.vOpenSpectroFile)
        self.oAppIZSpectro.filemenu.add_command(label='Export to ASCII', \
                                                command=self.vExportToASCII)
	#self.oAppIZSpectro.settingsmenu.add_command(label='Set Sample Bias', \
	#					command=self.vSetSampleBiasCB)
	self.oAppIZSpectro.plotsettingsmenu.add_command(label='I vs Z', \
						command=self.vSetIZCB)
	self.oAppIZSpectro.plotsettingsmenu.add_command(label='log10(I) vs Z', \
						command=self.vSetlog10IZCB)
	self.oAppIZSpectro.plotsettingsmenu.add_command(label='Conductance vs Z', \
						command=self.vSetSZCB)
	self._configureSettings()
	self.oAppIZSpectro.BtnStartSpectro.configure(command=self.vStartLoggerCB)
	self.oAppIZSpectro.BtnStopSpectro.configure(command=self.vStopLoggerCB)
	self.oAppIZSpectro.BtnPlotIZ.configure(command=self.vPlotIZCurvesCB)
	self.oAppIZSpectro.BtnSaveSpectro.configure(command=self.vSaveIZPlotsCB)
	self.oAppIZSpectro.ScaleNoOfSteps.configure(command=self.vShowZmotionInfoCB)
	self.oAppIZSpectro.sGroup.protocol('WM_DELETE_WINDOW',self.vCloseAppIZSpectroCB)
	self.oAppIZSpectro.ScaleNoOfSteps.invoke('buttondown')	# to display info with callback
	self.vEnableAcquisitionControl()
	return

    def _configureSettings(self):
	"""
	Initializing Settings on the front panel
	"""
	piezo_z = scanner.fGetPiezoZCalibration()		# it is in nm/V
	self.zResolution_mV = self.ZDAC_RES * offset.fGetZoffsetGain()
	self.zResolutionAngs = piezo_z * self.zResolution_mV / 1e2
	#print self.zResolutionAngs  
	strZresAngs = '%.2f' % self.zResolutionAngs  
	strZres_mV = '%.3f' % self.zResolution_mV
	strZres = strZresAngs + u' \u00C5' + ' (' + strZres_mV + ' mV)'
	self.oAppIZSpectro.LabelInfoZ_Resolution.configure (text = \
						'Z Resolution: ' + strZres)
	self.oAppIZSpectro.ScaleNoOfSteps.configure(values=tuple(self.anStepList))
	# step list is now in angs 
	#self.oAppIZSpectro.ScaleSteppingDelay.configure(values=tuple(self.anDelayList))
	self.oAppIZSpectro.ScaleMovingAvgPoints.configure(values=tuple(self.anMovAvgList))
	self.oAppIZSpectro.ScaleNoOfSweeps.configure(values=tuple(self.anSweepList))
	return
	
    def vEnableAcquisitionControl(self):
	self.oAppIZSpectro.BtnStartSpectro.configure(state=NORMAL)
	self.oAppIZSpectro.BtnStopSpectro.configure(state=DISABLED)
	self.oAppIZSpectro.BtnPlotIZ.configure(state=DISABLED)
	self.oAppIZSpectro.BtnSaveSpectro.configure(state=DISABLED)
	return

    def vFindScannerPolarity(self):
	"""
	If the Scanner Polarity is Negative/Positive it means 
	the scanner piezo stretches forward at -110Vdc/+110Vdc resp.
	"""
	dicGlobParam = scanner.dicReadGlobalParam()
	self.strScannerPolarity = dicGlobParam['ZPolarity']
	return

    def vFindCurrentSetPoint(self):
	"""
	The Actual Set-point (Current Reference in the Feedback Ckt)
	from global settings.
	"""
	self.fCurrentSetPoint = stm.readCurrentSetpoint()
	return

    def vSetIZCB(self):
	self.strPlotVar.set('IZ')
	return

    def vSetlog10IZCB(self):
	self.strPlotVar.set('log10IZ')
	return

    def vSetSZCB(self):
	self.strPlotVar.set('SZ')
	return

    def vStartLoggerCB(self):
	"""
	KickStart I-Z Spectroscopy
	"""
	self.strCurrentSpecFile = None
	self.vGetIZSpecParam()
	self.vEnableAcquisitionControl()
	self.oAppIZSpectro.BtnStartSpectro.configure(state=DISABLED)
	self.oAppIZSpectro.BtnStopSpectro.configure(state=NORMAL)
	self.vStartIZLogging()
	return

    def vPlotIZCurvesCB(self):
	"""
	Plots IZ curves as per user-specific x/y styles
	"""
	self.vPlotIZCurves()
	return

    def vStopLoggerCB(self):
	self.bStopLoggingVar.set(True)
	return

    def vShowZmotionInfoCB(self):
	nos = self.nReadNoOfSteps()
	zMotionAngs = self.zResolutionAngs * nos 
	str_zMotionAngs = '%.2f' % zMotionAngs
	#self.oAppIZSpectro.LabelInfoZ_MotionAngs.configure(text = \
	#						'Z Span for ' + str (nos) + ' steps = ' + str_zMotionAngs + u' \u00C5')
	zMotion_mV = self.zResolution_mV * self.nReadNoOfSteps()
	str_zMotion_mV = '%.3f' % zMotion_mV 
	infoSpanZ = 'Z Movement: ' + str_zMotionAngs + u' \u00C5' + ' (' + str_zMotion_mV + ' mV)'
	self.oAppIZSpectro.LabelInfoZ_MotionAngs.configure(text = infoSpanZ) 
	return

    def nReadNoOfSteps(self):
	return int(self.oAppIZSpectro.ScaleNoOfSteps.get())	

    def nReadMovAvgPoints(self):
	return int(self.oAppIZSpectro.ScaleMovingAvgPoints.get())	

    def nReadSweeps(self):
	return int(self.oAppIZSpectro.ScaleNoOfSweeps.get())	

    def vGetIZSpecParam(self):
	self.dicSpecParam['ZPolarity'] =  self.strScannerPolarity
	self.dicSpecParam['Setpoint'] =  self.fCurrentSetPoint
	self.dicSpecParam['SampleBias']  = stm.getCurrentSampleBias ()
	self.dicSpecParam['ZCalibration'] =  scanner.fGetPiezoZCalibration()	# it is in nm/V
	self.nStepSize = self.dicSpecParam['StepSize'] = self.MIN_STEPSIZE	# in mV
	self.nNoOfSteps = self.dicSpecParam['NoOfSteps'] = self.nReadNoOfSteps()
	self.nSweeps = self.dicSpecParam['Sweeps'] = self.nReadSweeps()
	self.nMovAvgPoints = self.dicSpecParam['MovAvgPoints'] = self.nReadMovAvgPoints()
	self.dicSpecParam['ZoffsetGain'] = offset.fGetZoffsetGain()
	return

    def vStartIZLogging(self):
	"""
	1. Switch Off the Feedback Loop
	2. Set T.C. Read Out Mode.
	3. Vary Z-Offset in Steps and record T.C. from ADC output.
	"""
	self.bStopLoggingVar.set(False)
	nTAT = 1	# turn-around-time = 1s
	dir_ = self.nRetractDir
	self.oScanner.vWriteAndSetGain(1)
	self.oStm.set_TCmode()
	self.oScanner.oOffset.vSetHoldHandler()
	self.afSweeps = []
	nZoff = self.oScanner.oOffset.nReadZoffset()
	for nSweep in range(self.nSweeps):
	    afIZData = []
	    for nStep in range(self.nNoOfSteps):
		fTC = self.fGetAvgTC(self.nMovAvgPoints)
		afIZData.append([nZoff, fTC])
		nZoff += (self.ZDAC_RES * dir_)
	        self.oAppIZSpectro.sGroup.update()
	        self.oStm.set_voltage(stm.OZDAC, nZoff)
	    # Compensation for hysteresis while approaching the sample back
	    if (nSweep % 2 != 0) and fTC < 0.95 * self.fCurrentSetPoint:	# till 95% of TC
		while fTC < self.fCurrentSetPoint:
		    fTC = self.fGetAvgTC(self.nMovAvgPoints)
		    afIZData.append([nZoff, fTC])
		    nZoff += (self.ZDAC_RES * dir_)
	            self.oStm.set_voltage(stm.OZDAC, nZoff)
		    self.nNoOfSteps += 1
		    #print 'Inni Venamme...', 
	    self.afSweeps.append(afIZData)
	    dir_ *= -1		# Reverse Z motion direction
	    time.sleep(nTAT)	# Wait before reversing the Z motion
	    if self.bStopLoggingVar.get():
		break
	self.dicSpecParam['NoOfSteps'] = self.nNoOfSteps
	self.oScanner.oOffset.vClearHoldHandler()	#Feedback On
	self.oStm.set_Zmode()
	self.oScanner.oOffset.vCorrectZoffsetCB(None)
	self.vPlotIZCurves()
	return

    def fGetAvgTC(self, np):
	"""
	Get Avg TC Value over np no. of points.
	"""
	#tc = self.oStm.read_block(np,self.nStepDelay)
	#avg_tc = numpy.asarray(tc)[:,1].sum()/np
	avg_tc = self.oStm.read_spi_adc () [0]	# First Data item is TC/Z channel
	return avg_tc

    def vPlotIZCurves(self):
	self.oAppIZSpectro.BtnStartSpectro.configure(state=NORMAL)
	self.oAppIZSpectro.BtnSaveSpectro.configure(state=NORMAL)
	self.oAppIZSpectro.BtnPlotIZ.configure(state=NORMAL)
        pylab.ion()     # interactive display
	oPlot = pylab.figure()
	pos = 0
	sweep = 0
        hva_gain = offset.fGetZoffsetGain()
	for plots in self.afSweeps:
	    iz_plots = numpy.asarray(plots)
	    #print iz_plots
	    iz_plots[:,0] -= iz_plots[:,0].min()
	    iz_plots[:,0] *= (hva_gain * self.dicSpecParam['ZCalibration'] / 1e3) #nm
	    if self.strPlotVar.get() == 'SZ':
		s = iz_plots[:,1] / abs(self.dicSpecParam['SampleBias']) # pA/mV = nS
		s /= 1e3 # uS
	        pylab.semilogy(iz_plots[:,0], s, marker='o')
		pylab.ylabel('Conductance (uS)')
	    if self.strPlotVar.get() == 'log10IZ':
	        pylab.semilogy(iz_plots[:,0], iz_plots[:,1], marker='o')
		pylab.ylabel('Tunneling Current (pA)')
	    if self.strPlotVar.get() == 'IZ':
		pylab.plot(iz_plots[:,0], iz_plots[:,1], marker='o')
		pylab.ylabel('Tunneling Current (pA)')
	    sweep += 1
	pylab.grid(True)
	pylab.xlabel('Z Movement (nm)')
	if self.strCurrentSpecFile:
	    spec_file = self.strCurrentSpecFile.rsplit(os.sep,1)[-1]
	else:
	    spec_file = time.asctime() 
	pylab.title('I-Z Spectra : ' + spec_file)
	pylab.grid(True)
	pylab.show()
	return

    def vSaveIZPlotsCB(self, events=None):
	self.oAppIZSpectro.sGroup.update()
	self.vAskToSaveSpectroData()
	return

    def vAskToSaveSpectroData(self):
	filename = dialogs.SaveImageDialog('.'+IZEXT, 'Do you want to \n save spectro data?', parent=self.oAppIZSpectro.sGroup)
	if not filename:
	    return
	self.vSaveSpectroData(filename)
	return

    def vSaveSpectroData(self, filename):
	fd = open(filename, 'w')
	cPickle.dump(self.dicSpecParam, fd)
	cPickle.dump(self.afSweeps, fd)
	fd.close()
	print 'Saving Spectro Data as:', filename
	return

    def vOpenSpectroFile(self, event=None):
    	spectrofilepath = dialogs.strPathTracker()
	oFD = FileDialog.LoadFileDialog(self.oAppIZSpectro.sGroup, title='Load IZ Spectroscopy File')
	filename = oFD.go(dir_or_file=spectrofilepath, key='track', pattern='*.'+IZEXT)
	if filename == None:
	    return
	self.strCurrentSpecFile = filename
	print 'Spectra data file:', filename
	fd = open(filename)
	self.dicSpecParam = cPickle.load(fd)
	print 'Spec Params: ', self.dicSpecParam
	self.afSweeps = cPickle.load(fd)
	fd.close()
	#self.vAdjustSpectraSettings()
	self.vPlotIZCurves()
	return

    def vExportToASCII(self):
	"""
	Save spectra plots in a .txt file with same name.txt
	"""
	if self.strCurrentSpecFile == None:
	    tkMessageBox.showerror('File not found', 'Please save I-Z data first or \n open an existing file', parent=self.oAppIZSpectro.sGroup)
	    return
	print 'File exported to ASCII: ', self.strCurrentSpecFile
	fd = open(self.strCurrentSpecFile)
	dicSpecParam = cPickle.load(fd)
	afSweeps = cPickle.load(fd)
	fd.close()
	strASCIIfilename = self.strCurrentSpecFile.rsplit(os.extsep,1)[0] + '.txt'
	asciifd = open(strASCIIfilename, 'w')
	for key in dicSpecParam:
	    asciifd.write(str(key) + ': ' + str(dicSpecParam[key]) + '\n')
	nZoffBase = afSweeps[0][0][0]	# Initial Zoffset Value
	asciifd.write('Z(nm)'+ '\t' + 'I(pA)' + '\n')
	i = 1
        hva_gain = offset.fGetZoffsetGain()
	for plots in afSweeps:
	    asciifd.write('Sweep' + str(i) + '\n')
	    iz_plots = numpy.asarray(plots)
	    iz_plots[:,0] -= nZoffBase	# removing offset
	    iz_plots[:,0] *= (hva_gain * \
	    			(dicSpecParam['ZCalibration']/1e3)) #nm
	    s = iz_plots[:,1] / abs(dicSpecParam['SampleBias']) # pA/mV = nS
	    s /= 1e3 # uS
	    np = iz_plots.shape[0]	# no. of points in the spectra
	    for n in range(np):
		asciifd.write(str(iz_plots[n,0])+ '\t' + str(iz_plots[n,1]) + '\n')
	    i += 1
	asciifd.close()    
	tkMessageBox.showwarning('Export Done!!', \
		'ASCII data saved in file:\n' + strASCIIfilename, parent=self.oAppIZSpectro.sGroup)
	return

    def vCloseAppIZSpectroCB(self):
	"""
	--> Brings back Bias to initial value
	"""
	pylab.close('all')
	self.oAppIZSpectro.sGroup.destroy()
	self.oScanner.oMenuBar.IZSpectro_Instance = 0	
	return

    def afIZSpectroSweepHandler(self, limit, start, step, delay, mavg):
	arVal = self.oStm.izspectro_sweep(limit, start, step, delay, mavg)
	return arVal


