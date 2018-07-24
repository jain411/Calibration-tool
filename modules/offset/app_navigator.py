from Tkinter import *
from PIL import ImageTk
import os

menu_font_type = ("Helvetica", 11, 'normal')      # font description

iconpath = os.path.join(os.curdir, 'apps', 'icons')
#iconpath = os.path.join(os.curdir, 'icons')
up_iconfile = os.path.join(iconpath, 'up.png')
down_iconfile = os.path.join(iconpath, 'down.png')
left_iconfile = os.path.join(iconpath, 'left.png')
right_iconfile = os.path.join(iconpath, 'right.png')
home_iconfile = os.path.join(iconpath, 'go-home.png')
anchor_iconfile = os.path.join(iconpath, 'anchor.png')

def app_navigator():
	"""
	Create navigator object  
	"""
	navigatorObj = NavigatorGui()
	return navigatorObj 

class NavigatorGui:

	w = h = 256	# width and height of image canvas
	def __init__(self):
		print 'navigator window created'
		return

	def createNVwindow(self, master):
		self.navigatorGroup = master
		self.__createImages()
		self._createNVwidgets()
		self._createNVmenu()
		return

	def __createImages(self):
		global upim, downim, leftim, rightim, homeim, anchorim
		upim = ImageTk.PhotoImage(file=up_iconfile)
		downim = ImageTk.PhotoImage(file=down_iconfile)
		leftim = ImageTk.PhotoImage(file=left_iconfile)
		rightim = ImageTk.PhotoImage(file=right_iconfile)
		homeim = ImageTk.PhotoImage(file=home_iconfile)
		anchorim = ImageTk.PhotoImage(file=anchor_iconfile)
		return

	def _createNVwidgets(self):
		"""
		Creates Canvas widgets for displaying scan images
		"""
		self.LFRefMap = LabelFrame(self.navigatorGroup, \
					padx=4, pady=4, \
					text='Refrence Map')
		self.LFRefMap.grid(row=1, column=0, sticky=N+E+W+S)

		self.CanvasRefMap = Canvas(self.LFRefMap, \
					width=self.w, height=self.h, \
					relief=RIDGE, \
					bg = "light yellow")
		self.CanvasRefMap.grid(sticky=N+E+W+S)

		self.LblImageFile = Label(self.navigatorGroup, \
					fg = 'blue', \
					text = "")
		self.LblImageFile.grid(row=0, column=0, sticky=W)

		self.LFButtons = LabelFrame(self.navigatorGroup, \
					padx=2, pady=4)
		self.LFButtons.grid(row=1, column=1, sticky=N+E+W+S)
		self.BtnUp = Button(self.LFButtons, \
					repeatdelay=10, \
					repeatinterval=10, \
					image = upim)
		self.BtnUp.grid(row=0,column=1,sticky=N+E+W+S)	
		self.BtnLeft = Button(self.LFButtons, \
					repeatdelay=10, \
					repeatinterval=10, \
					image = leftim)
		self.BtnLeft.grid(row=1,column=0,sticky=N+E+W+S)	
		self.BtnHome = Button(self.LFButtons, \
					repeatdelay=10, \
					repeatinterval=10, \
					image = homeim)
		self.BtnHome.grid(row=1,column=1,sticky=N+E+W+S)	
		self.BtnRight = Button(self.LFButtons, \
					repeatdelay=10, \
					repeatinterval=10, \
					image = rightim)
		self.BtnRight.grid(row=1,column=2,sticky=N+E+W+S)	
		self.BtnDown = Button(self.LFButtons, \
					repeatdelay=10, \
					repeatinterval=10, \
					image = downim)
		self.BtnDown.grid(row=2,column=1,sticky=N+E+W+S)	
	
		self.SliderArea = Scale(self.LFButtons, \
					orient=HORIZONTAL, \
					from_=1, to=50,resolution=1, 
					sliderlength=15, \
					length=120, \
					showvalue=0, \
					)
		self.SliderArea.grid(row=4,column=0, columnspan=3, sticky=N)

		self.LblFrameInfo = Label(self.LFButtons, \
					fg = 'blue', \
					text = "")
		self.LblFrameInfo.grid(row=3, column=0, columnspan=3, sticky=E+W)

		self.BtnDropAnchor = Button(self.LFButtons, \
                                                text='Drop Anchor', \
						fg='blue', \
                                                compound=TOP, \
						height=100, \
						image = anchorim)
		self.BtnDropAnchor.grid(row=5,column=0, \
						#pady=20, \
						columnspan=3, \
						sticky=N+E+W+S)	
		return
	
	def _createNVmenu(self):
		self.NavigatorMenu = Menu(self.navigatorGroup, \
					font=menu_font_type, \
					tearoff=0, \
					borderwidth=1)
		self.navigatorGroup.config(menu=self.NavigatorMenu)

		self.filemenu = Menu(self.NavigatorMenu, font=menu_font_type)
		self.filemenu.config(tearoff=0)
		self.NavigatorMenu.add_cascade(label='File', menu=self.filemenu)

		self.refmapmenu = Menu(self.filemenu, font=menu_font_type)
		self.refmapmenu.config(tearoff=0)
		self.filemenu.add_cascade(label='Select Ref Map', menu=self.refmapmenu)

		self.settingsmenu = Menu(self.NavigatorMenu, font=menu_font_type)
		self.settingsmenu.config(tearoff=0)
		self.NavigatorMenu.add_cascade(label='Settings', menu=self.settingsmenu)
		return

