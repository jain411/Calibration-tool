from Tkinter import *
import time
import threading

class StatusBar(Canvas):
	def __init__(self, master,fillcolor='blue',**kw):
		self.master = master
		self.width = kw['width']
		self.height = kw['height']
		self.fillcolor = fillcolor
		Canvas.__init__(self, master,**kw)
		self.textx, self.texty = self.width/2, self.height/2
		return

	def minimum(self, value):
		self.minval = value		
		return

	def maximum(self, value):
		self.maxval = value		
		return

	def mapping(self, status):
		mapval = int( ((status-self.minval)*1.0 / (self.maxval-self.minval))* self.width)
		return mapval 

	def value(self, status):
		currentwidth = self.mapping(status)
		self.refresh(currentwidth)
		return
	
	def refresh(self, currentwidth):
		self.delete(ALL)
		self.bar = self.create_rectangle(0, 0, currentwidth, self.height, fill = self.fillcolor)
		percent = int (currentwidth * 100 / self.width)
		self.text = self.create_text(self.textx, self.texty, anchor=CENTER, \
					text=str(percent)+ '%')
		self.master.update()
		return

	""" for test purpose"""
	def play(self):
		for i in range(self.maxval):
			self.value(i)
			time.sleep(0.01)
		return

class FreeStatusBar(Canvas):
	def __init__(self,master, barlength, bFlag=None, fillcolor='blue', delay=0.05, **kw):
		self.delay = delay
		self.master = master
		self.width = kw['width']
		self.height = kw['height']
		self.fillcolor = fillcolor
		Canvas.__init__(self,master,**kw)
		self.barlength = barlength
		self.Lock = threading.Lock()
		if bFlag:
			self.bFlag = bFlag
			self.bFlag.set(True)
		else:
			self.bFlag = BooleanVar() 
			self.bFlag.set(True)
		self.direc = 1
		return

	def start(self):
		p = ProcessStatus(self)
		p.start()
		return

	def progress(self):
		self.bFlag.set(False)
		self.bar = self.create_rectangle(0,0,self.barlength,self.height,fill=self.fillcolor)
		while 1:
			if self.bFlag.get():
				break
			self.refresh()
			self.master.update()
			time.sleep(self.delay)
		self.delete(ALL)
		return

	def refresh(self):
		self.move(self.bar,self.direc*5,0)
		if self.bbox(self.bar)[2] >= self.width:
			self.direc = -1
		if self.bbox(self.bar)[0] <= 0:
			self.direc = 1
		return
		
	def stop(self):
		self.Lock.acquire()
		self.delete(ALL)
		self.bFlag.set(True)
		self.Lock.release()
		return
		
class ProcessStatus(threading.Thread):
	def __init__(self, bar):
		threading.Thread.__init__(self)
		print "Thread inits"
		self.bar = bar
		return

	def run(self):
		self.bar.progress()
		return

if __name__ == "__main__":
	import time
	root = Tk()
	f = Frame(root).grid()
	flag = BooleanVar()
	s = FreeStatusBar(f, barlength=20, fillcolor='blue', width=100, height=20, bg='white')
	s.grid()
	#s.minimum(0)
	#s.maximum(256)
	# for testing
	b=Button(f,text='Play',command=s.stop).grid(sticky=N+E+W+S)
	#s.progress()
	s.start()
	print 'We Move from here ... '
	s.bFlag = flag
	root.mainloop()
