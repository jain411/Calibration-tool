from Tkinter import *
from tkValidatingEntry import *
import tkStatusBar
menu_font_type = ("Verdana", 12, 'normal')	# font description

def app_izspectro():
	"""
	Returns IZSpectroGui object
	"""
	oIZSpectroGui = IZSpectroGui()
	return oIZSpectroGui

class IZSpectroGui:


    w = h = 256		# width and height of spectro ref image canvas
    def __init__(self):
	"""
	Class Contructor : IZSpectroGui
	"""
	print 'IZ Spectro Gui created'
	return

    def createIZSwindow(self, master):
	"""
	"""
	self.sGroup = master
	self._vCreateIZSwidgets()
	return

    def _vCreateIZSwidgets(self):
	"""
	Creates Spectroscopy wigets in Spectroscopy Window
	"""
	self.mainmenu = Menu(self.sGroup, font=menu_font_type)
	self.mainmenu.config(borderwidth=1)
	self.sGroup.config(menu=self.mainmenu)
	self.filemenu = Menu(self.mainmenu, font=menu_font_type)
	self.filemenu.config(tearoff=0)	
	self.mainmenu.add_cascade(label='File', menu=self.filemenu, font=menu_font_type)
	self.settingsmenu = Menu(self.mainmenu, font=menu_font_type)
	self.settingsmenu.config(tearoff=0)
	self.mainmenu.add_cascade(label='Settings', menu=self.settingsmenu, font=menu_font_type)
	self.plotsettingsmenu = Menu(self.settingsmenu, font=menu_font_type)
	self.plotsettingsmenu.config(tearoff=0)
	self.settingsmenu.add_cascade(label='Plot Settings', menu=self.plotsettingsmenu, font=menu_font_type)

	self.LFSettings = LabelFrame(self.sGroup, \
				padx=4, pady=4, \
				text='I-Z Spectro. Settings')
	self.LFSettings.grid(row=0, column=1, sticky=N+E+W+S)

	textbox_width = 12

	setting_no = 0
	self.LabelInfoZ_Resolution = Label(self.LFSettings, text='',fg='blue')
	self.LabelInfoZ_Resolution.grid(row=setting_no, column=0, sticky=E+W, columnspan=2)

	setting_no += 1
	Label(self.LFSettings, text='No. of Steps').grid(row=setting_no, column=0, sticky=W)
	self.ScaleNoOfSteps = Spinbox(self.LFSettings, \
				bg='white', \
				state='readonly', \
				repeatdelay=80, \
				repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=textbox_width, \
				)
	self.ScaleNoOfSteps.grid(row=setting_no, column=1, sticky=W)

	setting_no += 1
	self.LabelInfoZ_MotionAngs = Label(self.LFSettings, text='',fg='red')
	self.LabelInfoZ_MotionAngs.grid(row=setting_no, column=0, sticky=W, columnspan=2)

	#setting_no += 1
	#self.LabelInfoZ_Motion_mV = Label(self.LFSettings, text='',fg='red')
	#self.LabelInfoZ_Motion_mV.grid(row=setting_no, column=0, sticky=W, columnspan=2)

	setting_no += 1
	Label(self.LFSettings, text='MovAvgPoints').grid(row=setting_no, column=0, sticky=W)
	self.ScaleMovingAvgPoints = Spinbox(self.LFSettings, \
				bg='white', \
				state='readonly', \
				repeatdelay=80, \
				repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=textbox_width, \
				)
	self.ScaleMovingAvgPoints.grid(row=setting_no, column=1, sticky=W)

	setting_no += 1
	Label(self.LFSettings, text='No.OfSweeps').grid(row=setting_no, column=0, sticky=W)
	self.ScaleNoOfSweeps = Spinbox(self.LFSettings, \
				bg='white', \
				state='readonly', \
				repeatdelay=80, \
				repeatinterval=80, \
				borderwidth=2, \
				justify=LEFT, \
				width=textbox_width)
	self.ScaleNoOfSweeps.grid(row=setting_no, column=1, sticky=W)

	#setting_no += 1
	#self.BtnFullRetract = Button(self.LFSettings, \
	#			fg='red', \
	#			text='Full Retract')
	#self.BtnFullRetract.grid(row=setting_no, column=0, sticky=E+W, columnspan=2)

	setting_no += 1
	self.BtnStartSpectro = Button(self.LFSettings, \
				fg='red', \
				text='Start Sweep(s)')
	self.BtnStartSpectro.grid(row=setting_no, column=0, sticky=E+W)

	#setting_no += 1
	self.BtnStopSpectro = Button(self.LFSettings, \
				fg='red', \
				text='Stop Sweep(s)')
	self.BtnStopSpectro.grid(row=setting_no, column=1, sticky=E+W)

	setting_no += 1
	self.BtnPlotIZ = Button(self.LFSettings, \
				fg='blue', \
				text='Re-Plot I-Z Data')
	self.BtnPlotIZ.grid(row=setting_no, column=0, sticky=E+W, columnspan=2)
	
	setting_no += 1
	self.BtnSaveSpectro = Button(self.LFSettings, \
				fg='blue', \
				text='Save Spectroscopy Data')
	self.BtnSaveSpectro.grid(row=setting_no, column=0, sticky=E+W, columnspan=2)

	self.LFStatus = LabelFrame(self.sGroup, \
				padx=4, pady=4, \
				text='Z-Approach Status')
	self.LFStatus.grid(row=1, column=1, columnspan=2, sticky=N+S+E+W)
	self.ApproachStatusBar = tkStatusBar.FreeStatusBar(self.LFStatus, \
				barlength=15, \
				height=20, width=180, \
				bg='white')	
	self.ApproachStatusBar.grid(row=0, column=0, sticky=N+W, padx=2, pady=2)
 	return

if __name__ == "__main__":
    root = Tk()
    oAppSpectro = app_izspectro()
    oAppSpectro.createIZSwindow(root)
    root.mainloop()
