from Tkinter import *
from tkValidatingEntry import *
import os

def app_litho():
	"""
	Returns LithoGui object
	"""
	lGuiObj = LithoGui()
	return lGuiObj


class LithoGui:
	def __init__(self):
		"""
		Class Contructor : LithoGui
		"""
		print 'Litho Gui created'
		return

	def createLSwindow(self, master):
		"""
		Creates Widgets on Litho Window
		"""
		self.lsGroup = master
		self._createLSwidgets()
		return

	def _createLSwidgets(self):
		"""
		Loads Lithography widgets in Lithography Settings Window
		"""	
		self.LFsettings = LabelFrame(self.lsGroup, text='Lithography Control')
		self.LFsettings.grid(row=0, column=0, padx=3, pady=3, stick=N+W+E+S)
		i = 0		
		w = 10
		Label(self.LFsettings, text='Pulse Height (in V):')\
			.grid(row=i, column=0, sticky=W)
		self.EntryV1 = FloatEntry(self.LFsettings, \
					bg='white', \
                                        width=w, \
                                        )
		self.EntryV1.grid(row=i, column=1, sticky=N+W)
		i += 1
		Label(self.LFsettings, text='Pulse Width: ')\
			.grid(row=i, column=0, sticky=W)
		self.EntryD1 = IntegerEntry(self.LFsettings, \
					bg='white', \
                                        width=w, \
                                        )
		self.EntryD1.grid(row=i, column=1, sticky=N+W)

		i += 1
                self.RBms = Radiobutton(self.LFsettings, \
                                                text='ms', \
                                                #selectcolor='light blue'\
						)
                self.RBms.grid(row=i, column=0, sticky=N+W)

                self.RBus = Radiobutton(self.LFsettings, \
                                                text='us', \
                                                #selectcolor='pink' \
						)
                self.RBus.grid(row=i, column=1, sticky=N+W)

		i += 1
		Label(self.LFsettings, text='No. Of Pulses: ')\
			.grid(row=i, column=0, sticky=W)
		self.EntryNoOfPulses = IntegerEntry(self.LFsettings, \
					bg='white', \
                                        width=w, \
                                        )
		self.EntryNoOfPulses.grid(row=i, column=1, sticky=N+W)

		i += 1
		self.CB_FeedbackOff = Checkbutton(self.LFsettings, \
					text='Feedback-Off Mode', \
					#selectcolor='blue' \
					)
		self.CB_FeedbackOff.grid(row=i, column=0, columnspan=2, sticky=N+E+W+S)
		i += 1
		self.BtnPuncture = Button(self.LFsettings, text='Apply Pulse', fg='red')
		self.BtnPuncture.grid(row=i, column=0, columnspan=2, sticky=N+W+E+S)
		
		i += 1
		self.LF_FB = LabelFrame(self.lsGroup, text='Feedback-Off Mode Settings')
		self.LF_FB.grid(row=i, column=0, padx=3, pady=3, sticky=N+W+E+S)
		w = 6
		Label(self.LF_FB, text='Pre-Pulse Delay (in ms):')\
			.grid(row=0, column=0, sticky=W)
		self.EntryPrePulseDelay = IntegerEntry(self.LF_FB, \
					bg='white', \
                                        width=w, \
                                        )
		self.EntryPrePulseDelay.grid(row = 0, column = 1, sticky = W)
		Label(self.LF_FB, text='Post-Pulse Delay (in ms):')\
			.grid(row=1, column=0, sticky=W)
		self.EntryPostPulseDelay = IntegerEntry(self.LF_FB, \
					bg='white', \
                                        width=w, \
                                        )
		self.EntryPostPulseDelay.grid(row = 1, column = 1, sticky = W)
	
		return


