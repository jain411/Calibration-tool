from Tkinter import *

def app_Import():
	"""
	Function : app_Import
		Returns ImportGui object

	Arguments :
		None

	Returns :
		iGuiObj : object of class ImportGui	
	"""
	iGuiObj = ImportGui()
	return iGuiObj

class ImportGui:

	def __init__(self):
		"""
		Class Contructor : ImportGui

		Arguments :
			None

		Returns :
			None
		"""
		return	

	def vCreateIWindow(self, master):
		"""
		Method : createIWwindow

		Arguments :
			master : root widget 

		Returns :
			None
		"""
		self.imGroup = master
		self.vCreateIWidgets()
		return

	def vCreateIWidgets(self):
		"""
		Method : vCreateIWwidgets
			Forms Import gui wigets 

		Arguments :
			None

		Returns :
			None
		"""
		self.LFImporttoPic=LabelFrame(self.imGroup,\
					text='Import To Pic:',\
					padx=15)
		self.LFImporttoPic.grid(row=0,column=0,sticky=N+W+E+S)
		self.LFImporttoDat=LabelFrame(self.imGroup,\
					text='Import To Dat:',\
					padx=15)
		self.LFImporttoDat.grid(row=0,column=1,sticky=N+W+E+S)

		self.RBnctopic=Radiobutton(self.LFImporttoPic,\
					text='Gxsm',\
					selectcolor='blue')
		self.RBnctopic.grid(row=0,column=0,sticky=N+W)
		self.RBnctodat=Radiobutton(self.LFImporttoDat,\
					text='Gxsm',\
					selectcolor='blue')
		self.RBnctodat.grid(row=0,column=0,sticky=N+W)

		self.RBjpgtopic=Radiobutton(self.LFImporttoPic,\
					text='jpg',\
					selectcolor='pink')
		self.RBjpgtopic.grid(row=1,column=0,sticky=N+W)
		self.RBjpgtodat=Radiobutton(self.LFImporttoDat,\
					text='jpg',\
					selectcolor='pink')
		self.RBjpgtodat.grid(row=1,column=0,sticky=N+W)

		self.RBpstopic=Radiobutton(self.LFImporttoPic,\
					text='ps',\
					selectcolor='yellow')
		self.RBpstopic.grid(row=2,column=0,sticky=N+W)
		self.RBpstodat=Radiobutton(self.LFImporttoDat,\
					text='ps',\
					selectcolor='yellow')
		self.RBpstodat.grid(row=2,column=0,sticky=N+W)

		self.LFInputFile=LabelFrame(self.imGroup,\
						padx=5,\
						pady=5,\
						text='Input Filename')
		self.LFInputFile.grid(row=1,column=0,columnspan=2,sticky=N+W+E+S)
		self.LInputFile=Label(self.LFInputFile)
		self.LInputFile.grid(row=0,column=0,sticky=N+E+W+S)
		self.LFOutputFile=LabelFrame(self.imGroup,\
						padx=5,\
						pady=5,\
						text='Import as')
		self.LFOutputFile.grid(row=2,column=0,columnspan=2,sticky=N+W+E+S)
		self.LOutputFile=Label(self.LFOutputFile)
		self.LOutputFile.grid(row=0,column=0,sticky=N+E+W+S)
		self.LFImportControl=LabelFrame(self.imGroup,\
						padx=5,\
						pady=5)
		self.LFImportControl.grid(row=3,column=0,columnspan=2,sticky=N+W+E+S)
		self.BtnImport=Button(self.LFImportControl,\
					padx=5,\
					text='Import')
		self.BtnImport.grid(row=0, column=0, sticky=N+E+W+S)
		self.BtnQuit=Button(self.LFImportControl,\
					padx=5,\
					text='Quit')
		self.BtnQuit.grid(row=0, column=1, sticky=N+E+W+S)
		
if __name__=="__main__":
	_import()


