from Tkinter import *

CANVAS_FONT = 'LiberationSans-Regular'
CANVAS_FONT_SIZE = 10

def app_imaging():
	"""
	Returns ImagingGui object
	"""
	imGuiObj = ImagingGui()
	return imGuiObj

class ImagingGui:

	w = h = 256	# width and height of image canvas
	def __init__(self):
		"""
		Class Contructor : ImagingGui
		"""
		print 'Imaging Window created'
		return

	def createIWwindow(self, master):
		"""
		Creates Widgets of Scan and retrace windows on the given master frame
		"""
		self.iwGroup = master
		self._createIWwidgets()
		self._createIWmenu()
		return

	def _createIWwidgets(self):
		"""
		Creates Canvas widgets for displaying scan images
		"""
		self.LFscan = LabelFrame(self.iwGroup, \
					padx=4, pady=5, \
					#text='Scan Image'\
					)
		self.LFscan.grid(row=0, column=0, sticky=N+E+W+S)

		scale_bar_h = 15
		#scale_bar_h = 0 
		self.CanvasScan = Canvas(self.LFscan, \
					width=self.w, height=self.h + scale_bar_h, \
					relief=RIDGE, \
					bg = "light yellow")
		self.CanvasScan.grid(sticky=N+E+W+S)

		self.LFretrace = LabelFrame(self.iwGroup, \
					padx=4, pady=5, \
					#text='Retrace Image'\
					)
		self.LFretrace.grid(row=0, column=1, sticky=N+E+W+S)

		self.CanvasRetrace = Canvas(self.LFretrace, \
					width=self.w, height=self.h + scale_bar_h, \
					relief=RIDGE, \
					bg = "light yellow")
		self.CanvasRetrace.grid(row=0,column=0,sticky=N+E+W+S)
		scale_bar_color = 'light blue'
		self.CanvasScan.create_rectangle(0, self.h, self.w + scale_bar_h, self.h + scale_bar_h, \
					width=0, fill=scale_bar_color)
		self.CanvasRetrace.create_rectangle(0, self.h, self.w + scale_bar_h, self.h + scale_bar_h, \
					width=0, fill=scale_bar_color)
		self.CanvasScan.create_text(self.w, self.h , \
			text='SCN', \
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			anchor=NE, 
			fill='blue')
		self.CanvasRetrace.create_text(self.w, self.h, \
			text='RET', \
			anchor=NE, \
			font=(CANVAS_FONT, CANVAS_FONT_SIZE), \
			fill='blue')
		self.CanvasColor = Canvas(self.LFretrace, \
			relief=RIDGE,\
			bg='light yellow')
		self.CanvasColor.config(width=35,height=256 + scale_bar_h)
		self.CanvasColor.grid(row=0,column=1,sticky=N)
		self.CanvasColor.create_rectangle(0, self.h, 35 + scale_bar_h, self.h + scale_bar_h, \
					width=0, fill=scale_bar_color)
		return

	def _createIWmenu(self):
		"""
		Attaches Quick Lunch menu to Scan and Retrace canvases
		"""
		self.ImagingMenu = Menu(self.iwGroup, tearoff=0)
		return

if __name__== "__main__":
	imaging()
