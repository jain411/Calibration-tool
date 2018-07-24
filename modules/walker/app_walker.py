from Tkinter import *
def app_walker():
	"""
	Returns WalkerGui object
	"""
	wGuiObj = WalkerGui()
	return wGuiObj


class WalkerGui:

	def __init__(self):
		"""
		Class Constructor
		"""
		print 'WalkerGui Object Created'
		return

	def createWSwindow(self, master):
		"""
		Creates Walker window on the frame/master provided
		"""
		self.wsGroup = master
		self._createWSwidgets()
		return

	def _createWSwidgets(self):
		"""
		Loads WalkerGui Widgets in Walker Window 
		"""
                self.LFdirection = LabelFrame(self.wsGroup, \
                                                text='Walker Direction', \
                                                padx=5, pady=5)
                self.LFdirection.grid(row=0, column=0, sticky=N+W+E+S)

                self.RBForward = Radiobutton(self.LFdirection, \
                                                text='Forward   ', \
                                                #selectcolor='red' \
						)
                self.RBForward.grid(row=0, column=0, sticky=N+W)

                self.RBBackward = Radiobutton(self.LFdirection, \
                                                text='Backward   ', \
                                                #selectcolor='blue' \
						)
                self.RBBackward.grid(row=0, column=1, sticky=N+W)

                self.LFcontrol = LabelFrame(self.wsGroup, \
                                                padx=5, pady=5, \
                                                text='Walker Control')
                self.LFcontrol.grid(row=1,column=0, sticky=N+W+S+E)

                self.BtnRun = Button(self.LFcontrol, \
                                        padx=5, pady=5, \
                                        text='Run')
                self.BtnRun.grid(row=0, column=0, sticky=N+W+S+E)

                self.BtnSingleStep = Button(self.LFcontrol, \
                                        padx=5, pady=5, \
                                        text='Single Step')
                self.BtnSingleStep.grid(row=0, column=1, sticky=N+W+S+E)

		self.BtnAutoWalk = Button(self.LFcontrol, \
                                        padx=5, pady=5, \
					width=10, \
                                        text='Auto Walk')
                self.BtnAutoWalk.grid(row=1, column=0, sticky=N+W+S+E)

                self.BtnBreakLock = Button(self.LFcontrol, \
                                        padx=5, pady=5, \
					width=11, \
                                        text='Break Lock')
                self.BtnBreakLock.grid(row=1, column=1, sticky=N+W+S+E)

                self.BtnStop = Button(self.LFcontrol, \
                                        padx=5, pady=5, \
                                        fg='red', \
                                        text='Stop')
                self.BtnStop.grid(row=2, column=0, sticky=N+W+E+S, columnspan=2)

                self.LFJunctionLED = LabelFrame(self.wsGroup, \
                                                text='Junction View', \
                                                padx=5, pady=5)
                self.LFJunctionLED.grid(row=2, column=0, sticky=N+W+E+S)

                self.RBLEDOn = Radiobutton(self.LFJunctionLED, \
                                                text='LED On   ', \
                                                #selectcolor='red' \
						)
                self.RBLEDOn.grid(row=0, column=0, sticky=N+W)

                self.RBLEDOff = Radiobutton(self.LFJunctionLED, \
                                                text='LED Off   ', \
                                                #selectcolor='blue' \
						)
                self.RBLEDOff.grid(row=0, column=1, sticky=N+W)

