from Tkinter import *
import tkMessageBox

from lib.tkValidatingEntry import *

menu_font_type   = ("Helvetica"	, 11, 'normal')	# font description
menu_font_type2 = ("Verdana"	, 12, 'normal')	# font description
option_menu_width = 16

PRE_AMP_GAIN      	= ['1', '10', '100']

POST_AMP_GAIN  	= ['1', '10', '100']

INTG_TIME_CONST 	= ['1s', '10ms', '100us']

def app_xlia(master):
	if master == None:
		return None
	oAppXLIA = XLIAGui(master)
	return oAppXLIA 

class XLIAGui:
	def __init__(self, master):
		self.master = master
		#self.master.title('Xplore Lock-in Amplifier')
		self._createWidgets()
		return

	def _createWidgets(self):
		self.master.config(padx=4,pady=4)
		
		self.mainmenu = Menu(self.master, font=menu_font_type)
		self.mainmenu.config(borderwidth=1)
		self.master.config(menu=self.mainmenu)
		
		self.filemenu = Menu(self.mainmenu, font=menu_font_type)
		self.filemenu.config(tearoff=0)
		
		self.settingmenu = Menu(self.mainmenu, font=menu_font_type)
		self.settingmenu.config(tearoff=0)
		
		self.preAmpGainMenu = Menu(self.settingmenu, font=menu_font_type)
		self.preAmpGainMenu.config(tearoff=0)
		
		self.postAmpGainMenu = Menu(self.settingmenu, font=menu_font_type)
		self.postAmpGainMenu.config(tearoff=0)
		
		self.timeConstMenu = Menu(self.settingmenu, font=menu_font_type)
		self.timeConstMenu.config(tearoff=0)
		
		### REFERENCE ###
		self.LFRef = LabelFrame(self.master, \
			padx=8, pady=6, \
			text='Reference')
		self.LFRef.grid(row=0, column=0, sticky=N+W+E+S)
		self.LFRefAmplitude = LabelFrame(self.LFRef, \
			padx=4, pady=5, \
			fg='blue', \
			text='Amplitude')
		self.LFRefAmplitude.grid(row=0, column=0, sticky=N+W+E+S)
		self.EntryRefAmplitude = IntegerEntry(self.LFRefAmplitude, \
			bg='white', \
			font=('Helvetica', 20, 'bold'), \
			justify=RIGHT, \
			width=8)
		self.EntryRefAmplitude.grid(row=0, column=0, sticky=E)
		Label(self.LFRefAmplitude, \
			text = 'mV', \
			font=('Helvetica', 20, 'bold'), \
			).grid(row=0, column=1, sticky=W)

		self.LFRefFrequency = LabelFrame(self.LFRef, \
			padx=4, pady=5, \
			fg='blue', \
			text='Frequency')
		self.LFRefFrequency.grid(row=1, column=0, sticky=N+W+E+S)
		self.EntryRefFrequency = IntegerEntry(self.LFRefFrequency, \
			bg='white', \
			font=('Helvetica', 20, 'bold'), \
			justify=RIGHT, \
			width=8)
		self.EntryRefFrequency.grid(row=0, column=0, sticky=E)
		Label(self.LFRefFrequency, \
			text = 'Hz', \
			font=('Helvetica', 20, 'bold'), \
			).grid(row=0, column=1, sticky=W)

		self.LFRefPhase = LabelFrame(self.LFRef, \
			padx=4, pady=5, \
			fg='blue', \
			text='Phase')
		self.LFRefPhase.grid(row=2, column=0, sticky=N+W+E+S)
		self.EntryRefPhase = IntegerEntry(self.LFRefPhase, \
			bg='white', \
			font=('Helvetica', 20, 'bold'), \
			justify=RIGHT, \
			width=8)
		self.EntryRefPhase.grid(row=0, column=0, sticky=E)
		Label(self.LFRefPhase, \
			text = 'o', \
			font=('Helvetica', 15, 'bold'), \
			).grid(row=0, column=1, sticky=N+W)
		
		### Settings ####
		self.LFSet = LabelFrame(self.master, \
			padx=4, pady=4, \
			text='Settings')
		self.LFSet.grid(row=0, column=1, sticky='news')
		
		### PreAmp_AC_Coupling ####
		self.LFCoupling = LabelFrame(self.LFSet, \
			padx=4, pady=4, \
			fg='blue', \
			text='Pre Amplification AC Coupling')
		self.LFCoupling.grid(row=0, column=0, sticky='news')
		self.BtnEnableCoupling = Checkbutton(self.LFCoupling, \
			#variable=self.PreAmpAC_CouplingSelected, \
			onvalue=1, offvalue=0, \
			text=' Enabled')
		self.BtnEnableCoupling.grid(row=0, column=0, sticky='news')
		
		### Set PreAmp Gain ####
		self.LFPreAmpGain = LabelFrame(self.LFSet, \
			padx=4, pady=4, text='Pre Amplification Gain', \
				fg='blue')
		self.LFPreAmpGain.grid(row = 1,column = 0, sticky=E+W)
	
		### Set PostAmp Gain ####
		self.LFPostAmpGain = LabelFrame(self.LFSet, \
			padx=4, pady=4, text='Post Amplification Gain', \
				fg='blue')
		self.LFPostAmpGain.grid(row = 2,column = 0, sticky=E+W)
				
		### Set Integrator Time Constant ####
		self.LFTimeConst = LabelFrame(self.LFSet, \
			padx=4, pady=4, text='Integrator Time Constant', \
				fg='blue')
		self.LFTimeConst.grid(row = 3,column = 0, sticky=E+W)
		
		### OUTPUT ###
		self.LFOutput = LabelFrame(self.master, \
			padx=4, pady=4, \
			text='Output')
		self.LFOutput.grid(row=1, column=0, columnspan=2, rowspan=2, sticky='news')
		self.LFInPhaseOutput = LabelFrame(self.LFOutput, \
			padx = 40, \
			fg='blue', \
			text='In-Phase Output')
		self.LFInPhaseOutput.grid(row=0, column=0, sticky='news')
		
		self.LblInPhaseOutput = Label(self.LFInPhaseOutput, \
			font=('Helvetica', 20, 'bold'), \
			justify=LEFT)
		self.LblInPhaseOutput.grid(row=0, column=0, sticky='news')
		
		self.LFQuadratureOutput = LabelFrame(self.LFOutput, \
			padx = 40, \
			fg='blue', \
			text='Quadrature Output')
		self.LFQuadratureOutput.grid(row=0, column=1, sticky='news')

		self.LblQuadratureOutput = Label(self.LFQuadratureOutput, \
			font=('Helvetica', 20, 'bold'), \
			justify=LEFT)
		self.LblQuadratureOutput.grid(row=0, column=0, sticky='news')
		self.LFAmplitudeOutput = LabelFrame(self.LFOutput, \
			padx = 40, \
			fg='blue', \
			text='Amplitude Out.')
		self.LFAmplitudeOutput.grid(row=1, column=0, sticky='news')
		
		self.LblAmplitudeOutput = Label(self.LFAmplitudeOutput, \
			font=('Helvetica', 20, 'bold'), \
			justify=LEFT)
		self.LblAmplitudeOutput.grid(row=0, column=0, sticky='news')
		
		self.LFPhaseOutput = LabelFrame(self.LFOutput, \
			padx = 40, \
			fg='blue', \
			text='Phase Out.')
		self.LFPhaseOutput.grid(row=1, column=1, sticky='news')
		
		self.LblPhaseOutput = Label(self.LFPhaseOutput, \
			font=('Helvetica', 20, 'bold'), \
			justify=LEFT)
		self.LblPhaseOutput.grid(row=0, column=0, sticky='news')
		
		return
	
	def createOptionMenus(self, varPreAG = None, varPostAG = None, varTC = None):
		self.OMPreAmpGain = OptionMenu(self.LFPreAmpGain, varPreAG, None)#, \
		#self.PreAmpGainSelected, None)
		self.OMPreAmpGain['menu'].delete(0, 'end')
		self.OMPreAmpGain.config(width=option_menu_width, anchor='w')
		self.OMPreAmpGain.grid(row=0, column=0, sticky=E+W)

		self.OMPostAmpGain = OptionMenu(self.LFPostAmpGain, varPostAG, None)#, \
		#self.PostAmpGainSelected, None)
		self.OMPostAmpGain['menu'].delete(0, 'end')
		self.OMPostAmpGain.config(width=option_menu_width, anchor='w')
		self.OMPostAmpGain.grid(row=0, column=0, sticky=E+W)

		self.OMTimeConst = OptionMenu(self.LFTimeConst, varTC, None)#, \
		#self.TimeConstSelected, None)
		self.OMTimeConst['menu'].delete(0, 'end')
		self.OMTimeConst.config(width=option_menu_width, anchor='w')
		self.OMTimeConst.grid(row=0, column=0, sticky=E+W)

		return
	
	def vConfimationPopup(self):
		return tkMessageBox.askyesno('Could not detect XLIA', 'Connection to XLIA Device lost!\n  Try Reconnecting?', default=tkMessageBox.YES, parent = self.master)

	def vCreatePlotFrame(self):
		self.LFPlotFrame = LabelFrame(self.master, \
			text='RT & IV Data Plots')
		self.LFPlotFrame.grid(row=0, column=2, rowspan=10, sticky=N+W+E+S)
		
		return self.LFPlotFrame

if __name__ == '__main__':
	root = Tk()
	oAppXLIA = app_xlia(root)
	root.mainloop()
