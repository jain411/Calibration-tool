from Tkinter import *
from tkValidatingEntry import *
from tkStatusBar import *

menu_font_type = ("Verdana", 12, 'normal')	# font description

def app_spectro():
	"""
	Returns IVSpectroGui object
	"""
	oIVSpectroGui = IVSpectroGui()
	return oIVSpectroGui

class IVSpectroGui:

    w = h = 256		# width and height of spectro ref image canvas
    def __init__(self):
	"""
	Class Contructor
	"""
	print 'Spectro Gui created'
	return

    def createSwindow(self, master):
	"""
	"""
	self.sGroup = master
	self._vCreateSwidgets()
	return

    def _vCreateSwidgets(self):
	"""
	Creates Spectroscopy wigets in Spectroscopy Window
	"""
	self.mainmenu = Menu(self.sGroup, font=menu_font_type)
	self.mainmenu.config(borderwidth=1)
	self.sGroup.config(menu=self.mainmenu)
	self.filemenu = Menu(self.mainmenu, font=menu_font_type)
	self.filemenu.config(tearoff=0)	
	self.mainmenu.add_cascade(label='File', menu=self.filemenu, font=menu_font_type)
	self.spectromapmenu = Menu(self.filemenu, font=menu_font_type)
        self.spectromapmenu.config(tearoff=0)
        self.filemenu.add_cascade(label='Select Spectro Map', menu=self.spectromapmenu, font=menu_font_type)
	self.settingsmenu = Menu(self.mainmenu, font=menu_font_type)
	self.settingsmenu.config(tearoff=0)
	self.mainmenu.add_cascade(label='Settings', menu=self.settingsmenu, font=menu_font_type)
	self.modemenu = Menu(self.settingsmenu, font=menu_font_type)
	self.modemenu.config(tearoff=0)
	self.settingsmenu.add_cascade(label='Selection Mode', menu=self.modemenu, font=menu_font_type)

	self.displaymenu = Menu(self.mainmenu, font=menu_font_type)
	self.displaymenu.config(tearoff=0)
	self.mainmenu.add_cascade(label='Display', menu=self.displaymenu, font=menu_font_type)
	self.plotsettingsmenu = Menu(self.displaymenu, font=menu_font_type)
	self.plotsettingsmenu.config(tearoff=0)
	#self.displaymenu.add_cascade(label='Plots', menu=self.plotsettingsmenu, font=menu_font_type)
	#self.pointplotsettingsmenu = Menu(self.plotsettingsmenu, font=menu_font_type)
	#self.pointplotsettingsmenu.config(tearoff=0)
	#self.plotsettingsmenu.add_cascade(label='Point Mode', menu=self.pointplotsettingsmenu, font=menu_font_type)

	self.LFSpectroMap = LabelFrame(self.sGroup, \
				padx=4, pady=4, \
				text='Spectroscopy Image Map')
	self.LFSpectroMap.grid(row=0, column=0, sticky=N+E+W+S)

	self.CanvasSpectroMap = Canvas(self.LFSpectroMap, \
				width=self.w, height=self.h, \
				relief=RIDGE, \
				bg = "light yellow")
	self.CanvasSpectroMap.grid(sticky=N+E+W+S)

	self.SpectroStatusBar = StatusBar(self.LFSpectroMap, \
				width=self.w,\
				height=self.h/10,\
				bg='white')
	self.SpectroStatusBar.grid(row=1, column=0, sticky=N+E+W+S)

	Label(self.LFSpectroMap, \
		fg = 'blue', \
		text = 'Max. Spectral Points:'
		).grid(row=2, column=0, sticky=W)

	self.LblMaxSpectroPointsInfo = Label(self.LFSpectroMap, \
				fg = 'blue', \
				text = ''
				)
	self.LblMaxSpectroPointsInfo.grid(row=3, column=0, sticky=W)

	self.LFSettings = LabelFrame(self.sGroup, \
				padx=4, pady=4, \
				text='Spectroscopy Settings')
	self.LFSettings.grid(row=0, column=1, sticky=N+S)
	self.LFBiasRange = LabelFrame(self.LFSettings, \
				padx=3, pady=3, \
				text='Bias Ramp')
	self.LFBiasRange.grid(row=0, column=0, sticky=N+E+W+S)
	Label(self.LFBiasRange, text='Initial Bias(mV)').grid(row=0,column=0,sticky=W)
	w=11
	self.EntryLowerLimit = IntegerEntry(self.LFBiasRange, \
				bg='white', \
				#state='readonly', \
				#repeatdelay=80, \
				#repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=w)
	self.EntryLowerLimit.grid(row=0,column=1,sticky=W)
	Label(self.LFBiasRange, text='Final Bias (mV)').grid(row=1,column=0,sticky=W)
	self.EntryUpperLimit = IntegerEntry(self.LFBiasRange, \
				bg='white', \
				#state='readonly', \
				#repeatdelay=80, \
				#repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=w)
	self.EntryUpperLimit.grid(row=1,column=1,sticky=W)

	self.LblSpectralPointsInfo = Label(self.LFBiasRange, \
				fg = 'blue', \
				text='')
	self.LblSpectralPointsInfo.grid(row=2, column=0, columnspan=2, sticky=W)

	self.LFOtherSettings = LabelFrame(self.LFSettings, \
				text='Other Settings', \
				padx=3, pady=3)
	self.LFOtherSettings.grid(row=1, column=0, sticky=E+W)

	Label(self.LFOtherSettings, text='Step Size (mV)').grid(row=0, column=0, sticky=W)
	self.ScaleStepSize = Spinbox(self.LFOtherSettings, \
				bg='white', \
				state='readonly', \
				repeatdelay=80, \
				repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=w, \
				)
	self.ScaleStepSize.grid(row=0, column=1, sticky=W)
	Label(self.LFOtherSettings, text='Step Delay (ms)').grid(row=1, column=0, sticky=W)
	self.ScaleSteppingDelay = Spinbox(self.LFOtherSettings, \
				bg='white', \
				state='readonly', \
				repeatdelay=80, \
				repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=w, \
				)
	self.ScaleSteppingDelay.grid(row=1, column=1, sticky=W)
	Label(self.LFOtherSettings, text='Mov. Avg. Points').grid(row=2, column=0, sticky=W)
	self.ScaleMovingAvgPoints = Spinbox(self.LFOtherSettings, \
				bg='white', \
				state='readonly', \
				repeatdelay=80, \
				repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=w, \
				)
	self.ScaleMovingAvgPoints.grid(row=2, column=1, sticky=W)
	Label(self.LFOtherSettings, text='No. Of Sweeps').grid(row=3, column=0, sticky=W)
	self.ScaleSweeps = Spinbox(self.LFOtherSettings, \
				bg='white', \
				state='readonly', \
				repeatdelay=80, \
				repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=w)
	self.ScaleSweeps.grid(row=3, column=1, sticky=W)

	self.LFSpecModes = LabelFrame(self.LFSettings, \
				padx=3, pady=3, \
				text='Spectroscopy Modes')
	self.LFSpecModes.grid (row=2, column=0, sticky=N+E+W+S)
	self.RBIV = Radiobutton (self.LFSpecModes, \
				text = 'IV             ', \
				)
	self.RBIV.grid (row = 0, column = 0, sticky=W)
	self.RBdIdV = Radiobutton (self.LFSpecModes, \
				text = 'dI/dV          ', \
				)
	self.RBdIdV.grid (row = 0, column = 1, sticky=W)
	'''
	self.nMinGridSize = 20
	self.nMaxGridSize = 200
	Label(self.LFOtherSettings, text='Grid Size').grid(row=4, column=0, sticky=W)
	self.SliderGridSize = Scale(self.LFOtherSettings, \
				orient=HORIZONTAL, \
				from_=20, to=200,resolution=10, 
				sliderlength=15, \
				length=95, \
				showvalue=0, \
				)
	self.SliderGridSize.grid(row=4,column=1, sticky=W)
	'''
	self.LFControl = LabelFrame(self.LFSettings, \
				padx=3, pady=3, \
				)
	self.LFControl.grid (row=3, column=0, sticky=N+E+W+S)
	self.BtnStartSpectro = Button(self.LFControl, \
				fg='blue', \
				text='Start Sweeps')
	self.BtnStartSpectro.grid(row=0, column=0, sticky=E+W)
	self.BtnStopSpectro = Button(self.LFControl, \
				fg='red', \
				text='Stop Sweeps')
	self.BtnStopSpectro.grid(row=0, column=1, sticky=E+W)
	self.BtnSaveSpectro = Button(self.LFControl, \
				fg='red', \
				text='Save Spectroscopy Data')
	self.BtnSaveSpectro.grid(row=1, column=0, sticky=E+W, columnspan=2)
	'''
	self.LFGridSpectraDisp = LabelFrame(self.sGroup, \
				padx=4, pady=4, \
				text='Grid Spectra Display Settings')
	#self.LFGridSpectraDisp.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S)
	self.LabelSweepNo = Label(self.LFGridSpectraDisp, text='Sweep No.')
	self.LabelSweepNo.grid(row=0, column=0, sticky=W)
	self.SBoxSweepNo = Spinbox(self.LFGridSpectraDisp, \
				readonlybackground='white', \
				bg='white',\
				width=9, \
				state='readonly', \
				borderwidth=2, \
				justify=LEFT)
	self.SBoxSweepNo.grid(row=0, column=1, sticky=N+E+S+W)
	Label(self.LFGridSpectraDisp, text='Filter Length').grid(row=1, column=0, sticky=W)
 	self.SliderGMFilterLen = Scale(self.LFGridSpectraDisp, \
				orient=HORIZONTAL, \
				from_=4, to=32,resolution=1,\
				sliderlength=15, \
				length=95, \
				showvalue=1, \
				)
	self.SliderGMFilterLen.grid(row=1,column=1, sticky=E+W)
	Label(self.LFGridSpectraDisp, text='Sample Bias').grid(row=2, column=0, sticky=W)
 	self.SliderBias = Spinbox(self.LFGridSpectraDisp, \
				#orient=HORIZONTAL, \
				#sliderlength=15, \
				#length=95, \
				#showvalue=1, \
				)
	self.SliderBias.grid(row=2,column=1, sticky=W)
	

	self.LFPointSpectraFromGrid = LabelFrame(self.LFGridSpectraDisp, \
				padx=4, pady=4, \
				text='Point Spectra from Grid')
	self.LFPointSpectraFromGrid.grid(row=3, column=0, columnspan=2, sticky=N+E+W+S)
	i = 0
	self.RBIV = Radiobutton(self.LFPointSpectraFromGrid, text='IV')
	self.RBIV.grid(row=i,column=0, sticky=E+W)
	self.RBdIdV = Radiobutton(self.LFPointSpectraFromGrid, text='dI/dV')
	self.RBdIdV.grid(row=i,column=1, sticky=E+W)
	self.RBTopoImage = Radiobutton(self.LFPointSpectraFromGrid, text='Topographic Image')
	self.RBTopoImage.grid(row=i,column=2, columnspan=2, sticky=E+W)
	i+=1
	Label(self.LFPointSpectraFromGrid, text=' X Pos: ').grid(row=i, column=0, sticky=W)
 	self.SBoxXPos = Spinbox(self.LFPointSpectraFromGrid, width=5)
	self.SBoxXPos.grid(row=i,column=1, sticky=W)
	Label(self.LFPointSpectraFromGrid, text=' Y Pos: ').grid(row=i, column=2, sticky=W)
 	self.SBoxYPos = Spinbox(self.LFPointSpectraFromGrid, width=5)
	self.SBoxYPos.grid(row=i,column=3, sticky=W)
	i+=1
	self.BtnGMAddPoint = Button(self.LFPointSpectraFromGrid, \
				fg='blue', \
				text='Add Point')
	self.BtnGMAddPoint.grid(row=i, column=0, columnspan=4, sticky=N+E+W+S)
	i+=1
	self.BtnGMClearPoint = Button(self.LFPointSpectraFromGrid, \
				fg='red', \
				text='Clear Point List')
	self.BtnGMClearPoint.grid(row=i, column=0, columnspan=4, sticky=N+E+W+S)
	i+=1
	self.BtnGMSelectLine = Button(self.LFPointSpectraFromGrid, \
				fg='red', \
				text='Select Line')
	self.BtnGMSelectLine.grid(row=i, column=0, columnspan=4, sticky=N+E+W+S)
	i+=1
	self.BtnGMPlotCurve = Button(self.LFPointSpectraFromGrid, \
				#height=8,\
				fg='blue', \
				text='Plot Curve')
	self.BtnGMPlotCurve.grid(row=i, column=0, columnspan=4, sticky=N+E+W+S)
	'''
	self.LFPointSpectraDisp = LabelFrame(self.sGroup, \
				padx=4, pady=4, \
				text='Point Spectra Display Settings')
	#self.LFPointSpectraDisp.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S)
	Label(self.LFPointSpectraDisp, text='Filter Length').grid(row=0, column=0)
 	self.SliderPMFilterLen = Scale(self.LFPointSpectraDisp, \
				orient=HORIZONTAL, \
				from_=4, to=32,resolution=1, \
				sliderlength=15, \
				length=95, \
				showvalue=1, \
				)
	self.SliderPMFilterLen.grid(row=0,column=1, sticky=W)
	self.BtnPMPlotdIdV = Button(self.LFPointSpectraDisp, \
				height=6,\
				fg='blue', \
				text='Plot dI / dV')
	self.BtnPMPlotdIdV.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S)

	self.CBPlotNormdIdV = Checkbutton(self.LFPointSpectraDisp, \
				text='Normalize dI/dV')
	self.CBPlotNormdIdV.grid(row=2, column=0, columnspan=2, sticky=N+E+W+S)

	self.LFInfobox = LabelFrame(self.LFPointSpectraDisp, \
				#padx=4, pady=4, \
				text='Spectral Settings')
	self.LFInfobox.grid(row=3, column=0, columnspan=2, sticky=N+E+W+S)

	self._createInfobox ()
	return

    def _createInfobox(self):
	"""
	Loads Infobox widgets in  InfoBox Window
	"""
	self.ScrollbarInfo = Scrollbar(self.LFInfobox, orient = VERTICAL)
	self.TextInfoBox = Text (self.LFInfobox, \
				height = 7, \
				width = 25, \
				yscrollcommand = self.ScrollbarInfo.set, \
				bg = 'light blue')
	self.ScrollbarInfo.config (command = self.TextInfoBox.yview)
	self.ScrollbarInfo.pack(side = RIGHT,fill = BOTH, expand = 1)
	self.TextInfoBox.pack(side = LEFT,fill = BOTH, expand = 1)
	return

if __name__ == "__main__":
    root = Tk()
    oAppSpectro = app_spectro()
    oAppSpectro.createSwindow(root)
    root.mainloop()
