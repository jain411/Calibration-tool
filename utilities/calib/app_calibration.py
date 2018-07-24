#!/usr/bin/python

from Tkinter import *

menu_font_type = ("Verdana", 12, 'normal')	# font description

def app_calibration():
	"""
	Returns CalibGui object
	"""
	wGuiObj = CalibGui() 
	return wGuiObj			

class CalibGui:	
	
	def __init__(self):
		"""
		Class Contructor : CalibGui
		"""
		print 'Calib gui created'
		return

	def createCSwindow(self,master):
		"""
		Method : createCSwindow
		"""
		self.csGroup = master
		self._createCSwidgets()
		return

	def _createCSwidgets(self):
		"""
		Loads  Caliberation wigets in Calibration Window
		"""
		self.mainmenu = Menu(self.csGroup,font=menu_font_type)
		self.mainmenu.config(borderwidth=1,tearoff=0)
		self.csGroup.config(menu=self.mainmenu)
		self.filemenu = Menu(self.mainmenu,font=menu_font_type)
		self.filemenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='File',menu=self.filemenu)
		self.settingsmenu=Menu(self.mainmenu,font=menu_font_type)
		self.settingsmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Settings',menu=self.settingsmenu)
		self.calibrationmodemenu=Menu(self.settingsmenu,font=menu_font_type)
		self.calibrationmodemenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Calibration Mode', menu=self.calibrationmodemenu	)
		self.utilitiesmenu = Menu(self.mainmenu, font=menu_font_type)
		self.utilitiesmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Utilities',menu=self.utilitiesmenu)
		self.colorsettingssubmenu=Menu(self.settingsmenu,font=menu_font_type)
		self.colorsettingssubmenu.config(tearoff=0)
		#self.settingsmenu.add_cascade(label='Display Choice', menu=self.colorsettingssubmenu)

		self.ArrCanvas = Canvas(self.csGroup, \
					relief=RIDGE,\
					bg='light yellow',\
					cursor='target')
		self.ArrCanvas.config(width=256,height=256)
		self.ArrCanvas.create_text(120,125,text='Open an Image For Display')
		self.ArrCanvas.grid(row=0,column=0, columnspan=4)
		'''
		self.btnOpen=Button(self.csGroup,text='Open')
		self.btnOpen.grid(row=1,column=0,sticky=N+W+E+S)
		self.btnZoom=Button(self.csGroup,text='Zoom')
		self.btnZoom.grid(row=1,column=1,sticky=N+W+E+S)
		self.btnOrig=Button(self.csGroup,text='Original')
		self.btnOrig.grid(row=1,column=2,sticky=N+W+E+S)
		self.btnQuit=Button(self.csGroup,text='Quit')
		self.btnQuit.grid(row=1,column=3,sticky=N+W+E+S)
		'''
		self.LFgridViewDisp = LabelFrame(self.csGroup, \
				padx=4, pady=4, \
				text='Grid View Display Settings')
		self.CBShowGrid = Checkbutton(self.LFgridViewDisp, \
				text='Show Grid', anchor = 'w')
		
		self.CBShowGrid.grid(row=0, column=0, columnspan=2, sticky=N+E+W+S)
		
		self.CBShowImage = Checkbutton(self.LFgridViewDisp, \
				text='Show Image', anchor = 'w')
		self.CBShowImage.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S)
		
		
		
		
		
		self.LFmaskLen = LabelFrame(self.LFgridViewDisp, \
				padx=3, pady=3, \
				text='Mask Settings')
		self.LFmaskLen.grid(row=2, column=0, sticky=N+E+W+S)
		
		Label(self.LFmaskLen, text='Mask Size').grid(row=0, column=0)
		self.SliderMaskLen = Scale(self.LFmaskLen, \
				orient=HORIZONTAL, \
				from_=1, to=10,resolution=1, \
				sliderlength=15, \
				length=95, \
				showvalue=0)
		self.SliderMaskLen.grid(row=0,column=1, sticky=W)
		
		self.BtnAddLine = Button(self.LFgridViewDisp, \
				height=1,\
				fg='blue', \
				text='Add Line')
		self.BtnAddLine.grid(row=3, column=0, columnspan=2, sticky=N+E+W+S)
		
		self.BtnRemoveLine = Button(self.LFgridViewDisp, \
				height=1,\
				fg='blue', \
				text='Remove Line')
		self.BtnRemoveLine.grid(row=4, column=0, columnspan=2, sticky=N+E+W+S)
		self.BtnAnalyze = Button(self.LFgridViewDisp, \
				height=2,\
				fg='blue', \
				text='Analysis')
		self.BtnAnalyze.grid(row=5, column=0, rowspan = 2, sticky = N+E+W+S)
		
		self.BtnExport = Button(self.LFgridViewDisp, \
				height=2,\
				fg='blue', \
				text='Export to CSV')
		self.BtnExport.grid(row=7, column=0, rowspan = 2, sticky = N+E+W+S)


		self.LFInfoGroup = LabelFrame(self.csGroup, \
					    padx=3, pady=3,\
					      )
					     
		self.SBXInfoBar = Scrollbar(self.LFInfoGroup, \
					orient=HORIZONTAL, \
					)
		self.SBXInfoBar.grid(row=1,column=0, sticky=E+W)
                
		self.SBYInfoBar = Scrollbar(self.LFInfoGroup, \
					orient=VERTICAL, \
					)
		self.SBYInfoBar.grid(row=0,column=1, sticky=N+S)
		self.ListLine = Listbox(self.LFInfoGroup, \
					height=10, \
				        width = 50, \
					bg = 'light blue', \
					selectmode=EXTENDED, \
					yscrollcommand=self.SBYInfoBar.set, \
					xscrollcommand=self.SBXInfoBar.set \
					)
		self.ListLine.grid(row=0, column=0, sticky=E+W)
		self.SBXInfoBar.config(command=self.ListLine.xview)
		self.SBYInfoBar.config(command=self.ListLine.yview)
		self.ListLine.insert(END, 'Line\tTotal Line Length\tBond length in pixel units\tCalibration Constant')

		
		return

if __name__ == "__main__":
	oCalib()
