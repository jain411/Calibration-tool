from Tkinter import *
from PIL import Image, ImageTk
import os

iconpath	 = os.path.join('apps', 'icons')		#  path for icons folder containing thumbimages for toolbar 
movie_iconfile	 = os.path.join(iconpath, 'movie.png')		#  movie iconpath
init_iconfile	 = os.path.join(iconpath, 'settings.png')       #  Init Settings iconpath
open_iconfile	 = os.path.join(iconpath, 'open2.png')		#  Open File iconpath 
save_iconfile	 = os.path.join(iconpath, 'filesave.png')	#  Save File conpath	
filter_iconfile	 = os.path.join(iconpath, 'filter.png')		#  I-Prog iconpath	
area_iconfile	 = os.path.join(iconpath, 'area.png')		#  Area Choice iconpath
fb_iconfile	 = os.path.join(iconpath, 'pi.png')		#  Feedback Control iconpath
litho_iconfile	 = os.path.join(iconpath, 'litho.png')		#  Lithography iconpath	
spectro_iconfile = os.path.join(iconpath, 'artsfftscope.png')	#  I-V Spectroscopy iconpath
softcro_iconfile = os.path.join(iconpath, 'cro.png')		#  CRO iconpath 
help_iconfile	 = os.path.join(iconpath, 'help.png')		#  Help iconpath
exit_iconfile	 = os.path.join(iconpath, 'exit.png')		#  Quit iconpath
cam_iconfile	 = os.path.join(iconpath, 'cam.png')		#  movie iconpath

btn_font_type = ('verdana', 10, 'normal')			#  font description

def app_toolbar():
	"""
	Returns ToolBarGui object
	"""
	tGuiObj = ToolBarGui()
	return tGuiObj

class ToolBarGui:
	
	def __init__(self):
		"""
		Class Contructor : ToolBarGui
		"""
		print 'Toolbar window created'
		return

	def createTBwindow(self, master):
		"""
		Method : createTBwindow
		"""
		self.tbarGroup = master
		self._createImages()
		self._createTBwidgets()
		return

	def _createTBwidgets(self):
		"""
		Loads Toolbar Widgets in Toolbar Window 
		"""
		self.BtnInitStm = Button(self.tbarGroup,\
						image=initim, \
						font=btn_font_type, 
						text='Init', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnInitStm.pack(side=LEFT, anchor=NW)

		self.BtnOpenFile = Button(self.tbarGroup,\
						image=openim, \
						font=btn_font_type, 
						text='Open', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnOpenFile.pack(side=LEFT, anchor=NW)

		self.BtnSaveFile = Button(self.tbarGroup,\
						image=saveim, \
						font=btn_font_type, 
						text='Save', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnSaveFile.pack(side=LEFT, anchor=NW)

		self.BtnMovieSettings= Button(self.tbarGroup,\
						image=movieim, \
						font=btn_font_type, 
						text='Movie', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnMovieSettings.pack(side=LEFT, anchor=NW)

		self.BtnImageFiltering = Button(self.tbarGroup,\
						image=filtim, \
						font=btn_font_type, 
						text='Filt', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnImageFiltering.pack(side=LEFT, anchor=NW)

		self.BtnAreaSettings = Button(self.tbarGroup,\
						image=areaim, \
						font=btn_font_type, 
						text='Area', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnAreaSettings.pack(side=LEFT, anchor=NW)

		self.BtnFB_Settings = Button(self.tbarGroup,\
						image=fbim, \
						font=btn_font_type, 
						text='FdBk', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnFB_Settings.pack(side=LEFT, anchor=NW)

		self.BtnLIASettings = Button(self.tbarGroup,\
						image=softcroim, \
						font=btn_font_type, 
						text='LIA', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnLIASettings.pack(side=LEFT, anchor=NW)

		self.BtnLitho = Button(self.tbarGroup,\
						image=lithoim, \
						font=btn_font_type, 
						text='Lith', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnLitho.pack(side=LEFT, anchor=NW)
	
		self.BtnSpectro = Button(self.tbarGroup,\
						image=spectroim, \
						font=btn_font_type, 
						text='IVSp', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnSpectro.pack(side=LEFT, anchor=NW)

		'''
		self.BtnSoftCRO = Button(self.tbarGroup,\
						image=softcroim, \
						font=btn_font_type, 
						text='CRO', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnSoftCRO.pack(side=LEFT, anchor=NW)
		'''
		self.BtnCam = Button(self.tbarGroup,\
						image=camim, \
						font=btn_font_type, 
						text='Cam', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnCam.pack(side=LEFT, anchor=NW)

		self.BtnHelp = Button(self.tbarGroup,\
						image=helpim, \
						font=btn_font_type, 
						text='Help', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnHelp.pack(side=LEFT, anchor=NW)
	
		self.BtnExit = Button(self.tbarGroup,\
						image=exitim, \
						font=btn_font_type, 
						text='Exit', \
						relief=FLAT, \
						overrelief=RAISED, \
						compound=TOP)
		self.BtnExit.pack(side=LEFT, anchor=NW)
		return

	def _createImages(self):
		"""
		Method : _createImages
			Attaches thumbnails to Toolbar buttons

		Arguments :
			None

		Returns :
			None
		"""
		global initim, movieim, filtim, openim, saveim, areaim, lithoim, \
                       spectroim, helpim, exitim, fbim, camim, softcroim
		initim		= ImageTk.PhotoImage(file=init_iconfile)
		openim		= ImageTk.PhotoImage(file=open_iconfile)
		saveim		= ImageTk.PhotoImage(file=save_iconfile)
		movieim 	= ImageTk.PhotoImage(file=movie_iconfile)
		filtim		= ImageTk.PhotoImage(file=filter_iconfile)
		areaim		= ImageTk.PhotoImage(file=area_iconfile)
		fbim		= ImageTk.PhotoImage(file=fb_iconfile)
		lithoim		= ImageTk.PhotoImage(file=litho_iconfile)
		spectroim	= ImageTk.PhotoImage(file=spectro_iconfile)
		softcroim	= ImageTk.PhotoImage(file=softcro_iconfile)
		helpim		= ImageTk.PhotoImage(file=help_iconfile)
		exitim		= ImageTk.PhotoImage(file=exit_iconfile)
		camim		= ImageTk.PhotoImage(file=cam_iconfile)
		return


