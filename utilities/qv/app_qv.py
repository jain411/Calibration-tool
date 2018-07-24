from Tkinter import *
from PIL import ImageTk
import os


if os.path.exists(os.path.join(os.curdir, 'qvicons')):
    iconpath = os.path.join(os.curdir, 'qvicons')
else:
    iconpath = os.path.join(os.curdir, 'apps', 'qvicons')

#APP_PATH = '/usr/stm/SiM4.2.0'		# to run as independent module
#if os.getcwd() != APP_PATH:
#    iconpath = os.path.join(os.curdir, 'qvicons')
#else:
#    iconpath = os.path.join(os.curdir, 'apps', 'qvicons')

browse_iconfile = os.path.join(iconpath, 'browse.png')
prev_iconfile = os.path.join(iconpath, 'prev.png')
next_iconfile = os.path.join(iconpath, 'next.png')
last_iconfile = os.path.join(iconpath, 'last.png')
first_iconfile = os.path.join(iconpath, 'first.png')
save_iconfile = os.path.join(iconpath, 'save.png')
saverem_iconfile = os.path.join(iconpath, 'saveremark.png')

def app_qv():
	"""
	Create quickvu object  
	"""
	qvObj = QuickViewGui()
	return qvObj 

class QuickViewGui:

	w = h = 256	# width and height of image canvas
	def __init__(self):
		#print 'qv window created'
                pass
		return

	def createQVwindow(self, master):
		self.qvGroup = master
		self.__createImages()
		self._createQVwidgets()
		self._createQVmenu()
		return

	def __createImages(self):
		global browseim, previm, nextim, firstim, lastim, saveim, saveremim
		browseim = ImageTk.PhotoImage(file=browse_iconfile)
		previm = ImageTk.PhotoImage(file=prev_iconfile)
		nextim = ImageTk.PhotoImage(file=next_iconfile)
		firstim = ImageTk.PhotoImage(file=first_iconfile)
		lastim = ImageTk.PhotoImage(file=last_iconfile)
		saveim = ImageTk.PhotoImage(file=save_iconfile)
		saveremim = ImageTk.PhotoImage(file=saverem_iconfile)
		return

	def _createQVwidgets(self):
		"""
		Creates Canvas widgets for displaying scan images
		"""
		self.LFscan = LabelFrame(self.qvGroup, \
					padx=4, pady=4, \
					text='Scan Image')
		self.LFscan.grid(row=0, column=0, sticky=N+E+W+S)

		self.CanvasScan = Canvas(self.LFscan, \
					width=self.w, height=self.h, \
					relief=RIDGE, \
					bg = "light yellow")
		self.CanvasScan.grid(sticky=N+E+W+S)

		self.LFretrace = LabelFrame(self.qvGroup, \
					padx=4, pady=4, \
					text='Retrace Image')
		self.LFretrace.grid(row=0, column=1, sticky=N+E+W+S)

		self.CanvasRetrace = Canvas(self.LFretrace, \
					width=self.w, height=self.h, \
					relief=RIDGE, \
					bg = "light yellow")
		self.CanvasRetrace.grid(sticky=N+E+W+S)
		"""
		self.LblImageInfo = Label(self.qvGroup,
					fg = 'blue',
					text = "")
		self.LblImageInfo.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S)
		"""
		self.LFButtons = LabelFrame(self.qvGroup, \
					#text='Bu', \
					padx=2, pady=2)
		self.LFButtons.grid(row=1, column=0, columnspan=2, sticky=E+W)
		self.BtnBrowse = Button(self.LFButtons, \
					image = browseim)
		self.BtnBrowse.grid(row=0,column=0,sticky=N+E+W+S)	
		self.BtnPrev = Button(self.LFButtons, \
					image = previm)
		self.BtnPrev.grid(row=0,column=1,sticky=N+E+W+S)	
		self.BtnNext = Button(self.LFButtons, \
					image = nextim)
		self.BtnNext.grid(row=0,column=2,sticky=N+E+W+S)	
		self.BtnFirst = Button(self.LFButtons, \
					image = firstim)
		self.BtnFirst.grid(row=0,column=3,sticky=N+E+W+S)	
		self.BtnLast = Button(self.LFButtons, \
					image = lastim)
		self.BtnLast.grid(row=0,column=4,sticky=N+E+W+S)	
		self.BtnSave = Button(self.LFButtons, \
					image = saveim)
		self.BtnSave.grid(row=0,column=5,sticky=N+E+W+S)	
		self.BtnSaveRemark = Button(self.LFButtons, \
					image = saveremim)
		self.BtnSaveRemark.grid(row=0,column=6,sticky=N+E+W+S)	
		self.LFInfoGroup = LabelFrame(self.qvGroup, \
					padx=4, pady=4, \
					text='Current Image Info')
		self.LFInfoGroup.grid(row=0, column=2, rowspan=3, sticky=N+S)

		self.SBXInfoBar = Scrollbar(self.LFInfoGroup, \
					orient=HORIZONTAL, \
					)
		self.SBXInfoBar.grid(row=1,column=0, sticky=E+W)

		self.SBYInfoBar = Scrollbar(self.LFInfoGroup, \
					orient=VERTICAL, \
					)
		self.SBYInfoBar.grid(row=0,column=1, sticky=N+S)
		self.LInfoBox = Listbox(self.LFInfoGroup, \
					#height=30, \ # windows
					height=27, \
					#width=20, \
					bg = 'light blue', \
					xscrollcommand=self.SBXInfoBar.set, \
					yscrollcommand=self.SBYInfoBar.set, \
					)
		self.LInfoBox.grid(row=0, column=0, sticky=N)
		self.SBXInfoBar.config(command=self.LInfoBox.xview)
		self.SBYInfoBar.config(command=self.LInfoBox.yview)
		# If a separate 'Remarks Block is needed....'
		self.LFRemarkGroup = LabelFrame(self.qvGroup, \
					padx=4, pady=4, \
					text='Write Remarks')
		self.LFRemarkGroup.grid(row=2,column=0, columnspan=2, sticky=N+S)
		self.SBXRemBar = Scrollbar(self.LFRemarkGroup, \
					orient=HORIZONTAL, \
					)
		self.SBXRemBar.grid(row=1,column=0, sticky=E+W)

		self.SBYRemBar = Scrollbar(self.LFRemarkGroup, \
					orient=VERTICAL, \
					)
		self.SBYRemBar.grid(row=0,column=1, sticky=N+S)
		self.TBRemark = Text(self.LFRemarkGroup, \
					height=8, \
					#width=80, \	# windows
					width=70, \
					bg = 'white', \
					xscrollcommand=self.SBXRemBar.set, \
					yscrollcommand=self.SBYRemBar.set, \
					)
		self.TBRemark.grid(row=0, column=0, sticky=N+S)
		self.SBXRemBar.config(command=self.TBRemark.xview)
		self.SBYRemBar.config(command=self.TBRemark.yview)

	def _createQVmenu(self):
		self.ImagingMenu = Menu(self.qvGroup, tearoff=0)
		return
