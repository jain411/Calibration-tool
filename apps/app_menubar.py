from Tkinter import *
#menu_font_type = ("Verdana", 12, 'normal')	# font description
menu_font_type = ("Helvetica", 11, 'normal')	# font description

def app_menubar():
	"""
	Function : app_menubar
		Returns MenubarGui object

	Arguments :
		None

	Returns :
		oMenubarGui : object of class MenubarGui	
	"""
	oMenubarGui = MenubarGui()
	return oMenubarGui

class MenubarGui:

	def __init__(self):
		"""
		Class Contructor : MenubarGui

		Arguments :
			None

		Returns :
			None
		"""
		print 'Menubar created'
		return

	def createMenubar(self, master):
		"""
		Method : createMenubar

		Arguments :
			master : root widget 

		Returns :
			None
		"""
		self.master = master
		self._createMenuItems()
		return


	def _createMenuItems(self):
		"""
		Method : _createMenuItems
			Menu Contents

		Arguments :
			None

		Returns :
			None
		"""
		self.mainmenu = Menu(self.master, font=menu_font_type)
		self.mainmenu.config(borderwidth=1)
		self.master.config(menu=self.mainmenu)
	
		self.filemenu = Menu(self.mainmenu, font=menu_font_type)
		self.filemenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='File', menu=self.filemenu, underline=0)

		self.settingsmenu = Menu(self.mainmenu, font=menu_font_type)
		self.settingsmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Settings', menu=self.settingsmenu, underline=0)
		
		self.scansettingsmenu = Menu(self.settingsmenu, font=menu_font_type)
		self.scansettingsmenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Scan Settings', menu=self.scansettingsmenu, underline=1)

		self.offsetsettingsmenu = Menu(self.settingsmenu, font=menu_font_type)
		self.offsetsettingsmenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Offset Settings', menu=self.offsetsettingsmenu, underline=0)
		
		self.walkersettingsmenu = Menu(self.settingsmenu, font=menu_font_type)
		self.walkersettingsmenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Walker Settings', menu=self.walkersettingsmenu, underline=0)
		
		self.imagesettingsmenu = Menu(self.settingsmenu, font=menu_font_type)	
		self.imagesettingsmenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Display Settings', menu=self.imagesettingsmenu, underline=0)

		self.displayareamenu = Menu(self.settingsmenu, font=menu_font_type)	
		self.displayareamenu.config(tearoff=0)
		self.imagesettingsmenu.add_cascade(label='Display Area', menu=self.displayareamenu, underline=1)

		self.piezosettingsmenu = Menu(self.settingsmenu, font=menu_font_type)	
		self.piezosettingsmenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Piezo Settings', menu=self.piezosettingsmenu, underline=0)

		self.utilitiesmenu = Menu(self.mainmenu, font=menu_font_type)
		self.utilitiesmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Utilities', menu=self.utilitiesmenu, underline=0)

		self.spectromenu = Menu(self.utilitiesmenu, font=menu_font_type)
		self.spectromenu.config(tearoff=0)
		self.utilitiesmenu.add_cascade(label='Spectrocopy', menu=self.spectromenu, underline=1)
	
		self.linextmenu = Menu(self.utilitiesmenu, font=menu_font_type)
		self.linextmenu.config(tearoff=0)
		self.utilitiesmenu.add_cascade(label='Line Extraction', menu=self.linextmenu, underline=0)

		self.threedimagingmenu = Menu(self.utilitiesmenu, font=menu_font_type)
		self.threedimagingmenu.config(tearoff=0)
		self.utilitiesmenu.add_cascade(label='3D Imaging', menu=self.threedimagingmenu, underline=0)

		self.calibmenu = Menu(self.utilitiesmenu, font=menu_font_type)
		self.calibmenu.config(tearoff=0)
		self.utilitiesmenu.add_cascade(label='Calibration', menu=self.calibmenu, underline=0)

		self.helpmenu = Menu(self.mainmenu, font=menu_font_type)
		self.helpmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Help', menu=self.helpmenu, underline=0)
		
