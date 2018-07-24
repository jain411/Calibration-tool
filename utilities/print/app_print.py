#################################
#	EXPORT			#
#################################

from Tkinter import *

menu_font_type = ("Verdana", 12, 'normal')	# font description

def app_print():
	"""
	Function : app_print
		Returns PrintGui object

	Arguments :
		None

	Returns :
		pGuiObj : object of class PrintGui	
	"""
	pGuiObj = PrintGui()
	return pGuiObj

class PrintGui:

	def __init__(self):
		"""
		Class Contructor : PrintGui

		Arguments :
			None

		Returns :
			None
		"""
		print 'PrintGui object Created'
		return
	
	def vCreatePSWindow(self, master):
		"""
		Method : vCreatePSWindow

		Arguments :
			master : root widget 

		Returns :
			None
		"""
		self.psGroup = master
		self.vCreatePSwidgets()
		return

	def vCreatePSwidgets(self):
		"""
		Method : vCreatePSwidgets
			Loads Print wigets in Print Settings  Window

		Arguments :
			None

		Returns :
			None
		"""
		self.mainmenu = Menu(self.psGroup,font=menu_font_type)
		self.mainmenu.config(borderwidth=1,tearoff=0)
		self.psGroup.config(menu=self.mainmenu)
		self.filemenu = Menu(self.mainmenu,font=menu_font_type)
		self.filemenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='File',menu=self.filemenu)
		self.settingsmenu = Menu(self.mainmenu, font=menu_font_type)
		self.settingsmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Settings',menu=self.settingsmenu)
		self.opensubmenu=Menu(self.filemenu,font=menu_font_type)
		self.opensubmenu.config(tearoff=0)

		self.utilitiesmenu = Menu(self.mainmenu,font=menu_font_type)
		self.utilitiesmenu.config(tearoff=0)
		self.mainmenu.add_cascade(label='Utilities',menu=self.utilitiesmenu)

		self.filemenu.add_cascade(label='Open',menu=self.opensubmenu)
		self.colorsettingssubmenu=Menu(self.settingsmenu,font=menu_font_type)
		self.colorsettingssubmenu.config(tearoff=0)
		self.settingsmenu.add_cascade(label='Color Mode',menu=self.colorsettingssubmenu)
	
		self.ArrCanvas = Canvas(self.psGroup, \
					relief=RIDGE,\
					bg='light yellow')
		self.ArrCanvas.config(width=256,height=256)
		self.ArrCanvas.create_text(120,125,text='Open Image To Be Printed')
		self.ArrCanvas.grid(row=0,column=0, columnspan=4)
		self.btnOpen=Button(self.psGroup,text='Open')
		self.btnOpen.grid(row=1,column=0,sticky=N+W+E+S)
		self.btnPrint=Button(self.psGroup,text='Print')
		self.btnPrint.grid(row=1,column=1,sticky=N+W+E+S)
		self.btnZoom=Button(self.psGroup,text='Zoom')
		self.btnZoom.grid(row=1,column=2,sticky=N+W+E+S)
		self.btnOrig=Button(self.psGroup,text='Original')
		self.btnOrig.grid(row=1,column=3,sticky=N+W+E+S)
		return

######### Only for Testing ###########
if __name__ == "__main__":
	from Tkinter import * 
	app_print()
	
