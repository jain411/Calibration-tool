from Tkinter import *
def app_scanner():
	"""
	Returns ScannerGui object
	"""
	oScannerGui = ScannerGui()
	return oScannerGui

class ScannerGui:


	def __init__(self):
		"""
		Class Contructor : ScannerGui
		"""
		print 'Scanner Gui created'
		return

	def createSSwindow(self, master):
		"""
		Launched from outside provided a frame to create window is given
		"""
		self.ssGroup = master
		self._createSSwidgets()
		return

	def _createSSwidgets(self):
		"""
		Loads Scanner widgets in Scanner Settings Window
		"""
		self.LFdirection = LabelFrame(self.ssGroup, \
                                                text='Scan Orientation', \
                                                padx=3, pady=3)
                self.LFdirection.grid(row=0, column=0, sticky=N+W+E+S)

                self.RBHorz = Radiobutton(self.LFdirection, \
                                                text='Horizontal   ', \
                                                #selectcolor='light blue'\
						)
                self.RBHorz.grid(row=0, column=0, sticky=N+W)

                self.RBVert = Radiobutton(self.LFdirection, \
                                                text='Vertical   ', \
                                                #selectcolor='pink' \
						)
                self.RBVert.grid(row=0, column=1, sticky=N+W)

		self.LFsettings = LabelFrame(self.ssGroup, \
                                                text='Scan Settings', \
                                                padx=3, pady=3)
                self.LFsettings.grid(row=1, column=0, sticky=N+W+E+S)

		Label(self.LFsettings, text='Image Size (pix)  ').grid(row=0, column=0, sticky=W)
		self.EntryImageSize = Spinbox(self.LFsettings, \
					readonlybackground='white', \
					bg='white', \
                                        width=9, \
					state='readonly', \
					repeatinterval=80, \
					repeatdelay=80, \
                                        borderwidth=2, \
                                        justify=LEFT)
		self.EntryImageSize.grid(row=0, column=1, sticky=N+E+W+S)

		self.LabelDelay = Label(self.LFsettings, text='Delay/Step(us)')
		self.LabelDelay.grid(row=1, column=0, sticky=W)
		self.EntryDelay = Spinbox(self.LFsettings, \
					readonlybackground='white', \
					bg='white', \
                                        width=9, \
					state='readonly', \
					repeatinterval=80, \
					repeatdelay=80, \
                                        borderwidth=2, \
                                        justify=LEFT)
		self.EntryDelay.grid(row=1, column=1, sticky=N+E+S+W)

		self.LabelStepSize = Label(self.LFsettings, text='X/Y Step(mV)')
		self.LabelStepSize.grid(row=2, column=0, sticky=W)
		self.EntryStepSize = Spinbox(self.LFsettings, \
					readonlybackground='white', \
					bg='white', \
                                        width=9, \
					state='readonly', \
					repeatinterval=80, \
					repeatdelay=80, \
                                        borderwidth=2, \
                                        justify=LEFT)
		self.EntryStepSize.grid(row=2, column=1, sticky=N+E+S+W)

		self.LabelGain = Label(self.LFsettings, text='ADC Gain')
		self.LabelGain.grid(row=3, column=0, sticky=W)
		self.EntryGain = Spinbox(self.LFsettings, \
					readonlybackground='white', \
					bg='white',\
                                        width=9, \
					state='readonly', \
                                        borderwidth=2, \
                                        justify=LEFT)
		self.EntryGain.grid(row=3, column=1, sticky=N+E+S+W)
		self.LabelInfo = Label(self.LFsettings, \
					text='', \
					justify=CENTER, \
					fg='blue')
		self.LabelInfo.grid(row=4, column=0, columnspan=2, pady=2, sticky=N+E+W+S)
		self.LFmodes = LabelFrame(self.ssGroup, \
                                                text='Digitization Modes', \
                                                padx=3, pady=3)
                self.LFmodes.grid(row=2, column=0, sticky=N+W+E+S)

                self.RBTC = Radiobutton(self.LFmodes, \
                                                text='CH', \
                                                #selectcolor='blue'\
						)
                self.RBTC.grid(row=0, column=0, sticky=N+W)

                self.RBZ= Radiobutton(self.LFmodes, \
                                                text='CC', \
                                                #selectcolor='red' \
						)
                self.RBZ.grid(row=0, column=1, sticky=N+W)

                self.RB_LDOS = Radiobutton(self.LFmodes, \
                                                text='LDOS', \
                                                #selectcolor='red' \
						)
                self.RB_LDOS.grid(row=0, column=2, sticky=N+W)

                self.RB_LBH= Radiobutton(self.LFmodes, \
                                                text='LBH', \
                                                #selectcolor='red' \
						)
                self.RB_LBH.grid(row=0, column=3, sticky=N+W)

		self.LFaction= LabelFrame(self.ssGroup, \
                                                text='Actions', \
                                                padx=3, pady=3)
                self.LFaction.grid(row=3, column=0, sticky=N+W+E+S)

                self.BtnStartScan = Button(self.LFaction, \
					padx=5, pady=5, \
					fg='red', \
					text='   Start Scan   ')
                self.BtnStartScan.grid(row=1, column=0, sticky=W+E)
		self.BtnStopScan = Button(self.LFaction, \
					padx=5, pady=5, \
					fg='blue', \
					text='   Stop Scan   ')
                self.BtnStopScan.grid(row=1, column=1, sticky=W+E)
		return
