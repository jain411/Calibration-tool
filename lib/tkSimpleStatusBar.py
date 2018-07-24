from Tkinter import *
class StatusBar:
	def __init__(self, master):
		self.master = master
		self.master.create_text(0,0,anchor=NW, text="joshua")
		coords = self.master.bbox(ALL)
		print coords
		return

	def minimum(self, value):
		print value
		return

	def maximum(self, value):
		print value
		return

	def value(self, status):
		print status
		return

if __name__ == "__main__":
	root = Tk()
	f = Frame(root).pack()
	c = Canvas(f, width=90, height=20, bg='white')
	c.pack()
	s = StatusBar(c)
	root.mainloop()
