from Tkinter import *

menu_font_type = ("Verdana", 12, 'normal')	# font description

def app_iprog():
	"""
	Returns IProgGui object
	"""
	iGuiObj = IProgGui()
	return iGuiObj

class IProgGui:
	
	def __init__(self):
		"""
		Class Contructor : IProgGui
		"""
		print "IProg Window created"	
		return

	def vCreateIPwindow(self, master):
		"""
		Create widgets on the window
		"""
		self.ipGroup = master
		self.ipGroup.title('iProG-Gimp Spirit')
		self.vCreateIPwidgets()
		return

	def vCreateIPwidgets(self):
		"""
		Loads IProgGui Widgets in IProg Window
		"""
		self.mainmenu = Menu(self.ipGroup,font=menu_font_type)
		self.mainmenu.config(borderwidth=1,tearoff=0)
		self.ipGroup.config(menu=self.mainmenu)
		self.filemenu = Menu(self.mainmenu,font=menu_font_type)
		self.filemenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='File',menu=self.filemenu)
		self.toolsmenu = Menu(self.mainmenu, font=menu_font_type)
		self.toolsmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Tools',menu=self.toolsmenu)
		self.opensubmenu=Menu(self.filemenu)
		self.filemenu.add_cascade(label='Load',menu=self.opensubmenu)
		self.opensubmenu.config(tearoff=0)
		self.colortoolssubmenu=Menu(self.toolsmenu)
		self.toolsmenu.add_cascade(label='Color Tools',menu=self.colortoolssubmenu)
		self.colortoolssubmenu.config(tearoff=0)
		self.filtersubmenu=Menu(self.toolsmenu)
		self.toolsmenu.add_cascade(label='Filter',menu=self.filtersubmenu)
		self.filtersubmenu.config(tearoff=0)
		self.utilitiesmenu = Menu(self.mainmenu, font=menu_font_type)
		self.utilitiesmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Utilities',menu=self.utilitiesmenu)
		self.transformsubmenu = Menu(self.utilitiesmenu, font=menu_font_type)
		self.transformsubmenu.config(tearoff=0)
		self.utilitiesmenu.add_cascade(label='Rotate',menu=self.transformsubmenu)
		#............... Loading of Matrix .........................................

		self.fsgroup = LabelFrame(self.ipGroup, text='File Selection', padx=5, pady=5)
		self.fsgroup.grid(row=0,column=0,sticky=N+E+W+S,padx=10, pady=10,columnspan=4)
		list = ('Scan Window', 'Retrace Window', 'From Dump','File')
		self.fileselect = Spinbox(self.fsgroup, values=list, state='readonly', width=15)
		self.fileselect.grid(row=0,column=0,sticky=N+E+W+S)
		self.BtnLoad = Button(self.fsgroup, text='LOAD',fg='blue')#, command=self.loadCB,fg='blue')
		self.BtnLoad.grid(row=0,column=1,sticky=N+E+W+S, padx=5 )

		#............... Filter Operations ...........................................
		self.BtnGauss = Button(self.ipGroup, text='G Blur', )#command = self.vGaussianCB)
		self.BtnGauss.grid(row=1,column=0,sticky=N+E+W+S,padx=2,pady=2)

		self.BtnUnsharp = Button(self.ipGroup, text='U Masking')#command = self.unsharpCB, )
		self.BtnUnsharp.grid(row=1,column=1,sticky=N+E+W+S,padx=2,pady=2)
		
		self.BtnHE = Button(self.ipGroup, text='Hist Eq')#command = self.vHistEqCB)
		self.BtnHE.grid(row=1,column=2,padx=2,pady=2, sticky=N+E+W+S)
		
		self.BtnBnC = Button(self.ipGroup, text='Brightness')# command = self.bnessCB)
		self.BtnBnC.grid(row=2,column=0, padx=2, pady=2, sticky=N+E+W+S)
		
		self.BtnContrast = Button(self.ipGroup, text='Contrast')# command=self.contrastCB)	
		self.BtnContrast.grid(row=2,column=1, padx=2, pady=2, sticky=N+E+W+S)

		self.BtnInvert = Button(self.ipGroup, text='Invert')# command = self.invertCB)
		self.BtnInvert.grid(row=2,column=2, padx=2, pady=2, sticky=N+E+W+S)

		self.BtnFourier = Button(self.ipGroup, text='Fourier')# command = self.fourierCB)
		self.BtnFourier.grid(row=3,column=0, padx=2, pady=2, sticky=N+E+W+S)

		self.BtnNLT = Button(self.ipGroup, text='NLT')# command = self.nltCB)
		self.BtnNLT.grid(row=3,column=1, padx=2, pady=2, sticky=N+E+W+S)

		self.BtnRotate = Button(self.ipGroup, text='Rotate')# command = self.rotateCB)
		self.BtnRotate.grid(row=3,column=2, padx=2, pady=2, sticky=N+E+W+S)

	
		i = 4
		#............... Save As Operations .......................................... 
		self.BtnSavePS = Button(self.ipGroup, text='Create PS')# command = self.savepsCB)
		self.BtnSavePS.grid(row=i,column=0, padx=2,pady=2, sticky=N+E+W+S)
		self.BtnZoom = Button(self.ipGroup, text='Zoom')# command = self.ZoomCB)
		self.BtnZoom.grid(row=i,column=1, padx=2,pady=2, sticky=N+E+W+S)
		self.BtnQuit = Button(self.ipGroup, text='Quit', fg='red')# command = self.quitCB)
		self.BtnQuit.grid(row=i,column=2, padx=2,pady=2, sticky=N+E+W+S)
		return
		
if __name__=="__main__":
	app_iprog()	
