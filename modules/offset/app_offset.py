#######################
#   OffsetGui Class   #
#######################
from Tkinter import *
from tkValidatingEntry import *
import tkStatusBar

def app_offset():
	"""
	Returns OffsetGui object
	"""
	offGuiObj = OffsetGui()
	return offGuiObj

class OffsetGui:

	w = 100					
	h = 100					

	def __init__(self):
		"""
		Class Contructor : OffsetGui
		"""
		print 'Offset Window created'
		return
	
	def createOSwindow(self, master):
		"""
		Creates widgets for offset control on the given frame
		"""
		self.osGroup = master
		self._createOSwidgets()	
		return
	
	def _createOSwidgets(self):
		"""
		Loads Offset widgets in Offset Window 
		"""
		self.LFoffset= LabelFrame(self.osGroup, \
                                                text='Offset Settings', \
                                                padx=3, pady=3)
                self.LFoffset.grid(row=0, column=0, sticky=N+W+E+S)

		self.BtnResetTipLocation = Button(self.LFoffset, \
						text=' Reset Tip Location', \
						fg='blue')
		self.BtnResetTipLocation.grid(row=0, column=0,columnspan=2, pady=2, sticky=N+E+S+W)

		self.LabelTipLocator = Label(self.LFoffset, text='Global Tip \n Locator')
		self.LabelTipLocator.grid(row=0, column=2, sticky=N+E+W+S)
		self.CBEnableGlobalTipLocator = Checkbutton (self.LFoffset, \
								fg = 'blue', \
								text='Enable')
		self.CBEnableGlobalTipLocator.grid (row=1, column=2, sticky=N+E+W+S)
		textwidth = 10
		self.LabelXoffset = Label(self.LFoffset, text='Xoff(nm)')
		self.LabelXoffset.grid(row=1, column=0, sticky=W)
		self.EntryXoffset = Entry(self.LFoffset, \
					bg='white', \
                                        width=textwidth, \
                                        borderwidth=2, \
                                        justify=LEFT)				
		self.EntryXoffset.grid(row=1, column=1, sticky=W)

		self.LabelYoffset = Label(self.LFoffset, text='Yoff(nm)')
		self.LabelYoffset.grid(row=2, column=0, sticky=W)
		self.EntryYoffset = Entry(self.LFoffset, \
					bg='white', \
                                        width=textwidth, \
                                        borderwidth=2, \
                                        justify=LEFT)				
		self.EntryYoffset.grid(row=2, column=1, sticky=W)

		self.LabelZoffset= Label(self.LFoffset, text='Zoff(mV)')
		self.LabelZoffset.grid(row=3, column=0, sticky=W)
		self.EntryZoffset = IntegerEntry(self.LFoffset, \
					bg='white', \
                                        width=textwidth, \
                                        borderwidth=2, \
                                        justify=LEFT)
		self.EntryZoffset.grid(row=3, column=1, sticky=W)

		self.BtnCorrectZoffset = Button(self.LFoffset, \
						text='Correct Z-Offset', \
						fg='blue')
		self.BtnCorrectZoffset.grid(row=4, column=0,columnspan=2, pady=2, stick=N+E+W+S)

		self.BtnStopCorrectZoffset = Button(self.LFoffset, \
						text='Stop Correction', \
						fg='red')

		self.LabelZpi = Label(self.LFoffset, text='FB-Z(mV)')
		self.LabelZpi.grid(row=5, column=0, sticky=W)
		self.LblDisplayZpi = Label(self.LFoffset, \
					relief= SUNKEN,\
					width=textwidth, \
					borderwidth=2, \
					bg='white',\
                                        justify=LEFT)
		self.LblDisplayZpi.grid(row=5, column=1, sticky=W, pady=5)

		self.CBFBMonitor = Checkbutton(self.LFoffset, \
						text='FB Monitor (Zpi)', \
						fg='blue')
		self.CBFBMonitor.grid(row=6, column=0,columnspan=2, pady=5, stick=N+E+W+S)

		self.CanTipLocation = Canvas(self.LFoffset, \
						width=self.w, \
						height=self.h, \
						bg='black')
		self.CanTipLocation.grid(row=2, column=2, rowspan=4, padx=4)
		self.CanTipLocation.create_line(self.w/2,0,self.w/2,self.h, fill='white', dash=(4,2))
		self.CanTipLocation.create_line(0,self.h/2,self.w,self.h/2, fill='white', dash=(4,2))

		"""
		self.OffsetStatusBar = tkStatusBar.FreeStatusBar(self.LFoffset, \
					barlength=15, \
					#height=20, width=248, \
					height=20, width=140, \
					bg='white')	
		self.OffsetStatusBar.grid(row=6, column=0, columnspan=2, sticky=N+W, padx=2, pady=2)
		"""
		self.BtnNavigator = Button(self.LFoffset, \
						text='Navigator', \
						fg='red')
		self.BtnNavigator.grid(row=6, column=2, stick=N+E+W+S, padx=3)

		return

	def activateStopCorrectZ_Control(self):
		self.BtnCorrectZoffset.grid_forget()
		self.BtnStopCorrectZoffset.grid(row=4, column=0,columnspan=2, pady=2, stick=N+E+W+S)
		return

	def activateCorrectZ_Control(self):
		self.BtnStopCorrectZoffset.grid_forget()
		self.BtnCorrectZoffset.grid(row=4, column=0,columnspan=2, pady=2, stick=N+E+W+S)
		return
