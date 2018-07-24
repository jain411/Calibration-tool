#!/usr/bin/python

from Tkinter import *

menu_font_type = ("Verdana", 12, 'normal')	# font description

def app_zcalib():
	"""
	Returns ZCalibGui object
	"""
	oZCalibGui = ZCalibGui()
	return oZCalibGui

class ZCalibGui:	
	
	def __init__(self):
		"""
		Class Contructor : ZCalibGui
		"""
		print 'Z-Calib Interface'
		return

	def createZCwindow(self,master):
		"""
		"""
		self.zcGroup = master
		self.zcGroup.title('Z-Calibration Tool')
		self.createZCwidgets()
		return

	def createZCwidgets(self):
		"""
		Loads  Caliberation wigets in Calibration Window
		"""
		self.mainmenu = Menu(self.zcGroup,font=menu_font_type)
		self.mainmenu.config(borderwidth=1,tearoff=0)
		self.zcGroup.config(menu=self.mainmenu)
		self.filemenu = Menu(self.mainmenu,font=menu_font_type)
		self.filemenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='File',menu=self.filemenu)
		self.settingsmenu=Menu(self.mainmenu,font=menu_font_type)
		self.settingsmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Settings',menu=self.settingsmenu)
		self.xaxissettingsmenu=Menu(self.settingsmenu,font=menu_font_type)
		self.xaxissettingsmenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Select X-Axis', menu=self.xaxissettingsmenu)
		self.utilitiesmenu = Menu(self.mainmenu, font=menu_font_type)
		self.utilitiesmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Utilities',menu=self.utilitiesmenu)
		self.colorsettingssubmenu=Menu(self.settingsmenu,font=menu_font_type)
		self.colorsettingssubmenu.config(tearoff=0)
		self.FrameCanvas = LabelFrame(self.zcGroup)
		self.FrameCanvas.grid(row=0, column=0, sticky=N+E+W+S)
		self.ArrCanvas = Canvas(self.FrameCanvas, \
					relief=RIDGE,\
					bg='light yellow',\
					)
		self.ArrCanvas.config(width=256,height=256)
		self.ArrCanvas.create_text(120,125,text='Open an Image For Display')
		self.ArrCanvas.grid(row=0,column=0)
		self.FrameControl = LabelFrame(self.zcGroup, \
					padx=1, pady=1,\
					#text= 'Test', \
					)
		self.FrameControl.grid(row=1, column=0, sticky=N+W+E+S)
		self.BtnAddROI = Button(self.FrameControl, \
					fg='blue', \
					text='Add ROI', width=29)
		self.BtnAddROI.grid(row=0,column=0, sticky=N+E+W+S)
		self.BtnRemoveROI = Button(self.FrameControl, \
					fg='red', \
					text='Remove ROI')
		self.BtnRemoveROI.grid(row=1,column=0, sticky=N+E+W+S)
		self.BtnShowHist = Button(self.FrameControl,text='Show Histogram')
		self.BtnShowHist.grid(row=2,column=0,sticky=W+E)
		#self.BtnQuit = Button(self.FrameControl, \
		#			fg='red'
		#			text='Quit')
		#self.BtnQuit.grid(row=3,column=0,sticky=W+E)
		self.LFInfoGroup = LabelFrame(self.zcGroup, \
					)
		self.LFInfoGroup.grid(row=0,column=1, rowspan=2, sticky=N+S)

		self.SBXInfoBar = Scrollbar(self.LFInfoGroup, \
					orient=HORIZONTAL, \
					)
		self.SBXInfoBar.grid(row=1,column=0, sticky=E+W)

		self.SBYInfoBar = Scrollbar(self.LFInfoGroup, \
					orient=VERTICAL, \
					)
		self.SBYInfoBar.grid(row=0,column=1, sticky=N+S)
		self.ListLine = Listbox(self.LFInfoGroup, \
					height=20, \
					bg = 'light blue', \
					selectmode=EXTENDED, \
					xscrollcommand=self.SBXInfoBar.set, \
					yscrollcommand=self.SBYInfoBar.set, \
					)
		self.ListLine.grid(row=0, column=0, sticky=N+S)
		self.SBXInfoBar.config(command=self.ListLine.xview)
		self.SBYInfoBar.config(command=self.ListLine.yview)

		return
