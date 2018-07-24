#################
# Splash Image  #
# on SiM launch #
#################

import os
from PIL import ImageTk
import time
#import threading
#import sys

import Tkinter

status_font = ('Helvetica', 16, 'normal')
substatus_font = ('Helvetica', 12, 'normal')

splashimage = 'splash.png'

logpath = os.path.join(os.curdir, 'log')
apploadinglog = os.path.join(logpath, 'stm.log')
globlogfile = os.path.join(logpath, 'glob.dat')

#try:
#	ImageFilename = sys.argv[1]
#except:
ImageFilename = os.path.join(os.curdir, 'apps', 'icons', splashimage)

class SplashScreen( object ):
   def __init__( self, tkRoot, minSplashTime=3.0):
      self._root              = tkRoot
      self._image             = ImageTk.PhotoImage( file=ImageFilename )
      self._splash            = None
      self._splash_text       = 'Loading SiM : nanoREV Control Application... '
      self._minSplashTime     = time.time() + minSplashTime

   def __enter__( self ):
      # Remove the app window from the display
      self._root.withdraw( )

      # Calculate the geometry to center the splash image
      scrnWt = self._root.winfo_screenwidth( )
      scrnHt = self._root.winfo_screenheight( )

      imgWt = self._image.width()
      imgHt = self._image.height()

      imgXPos = (scrnWt / 2) - (imgWt / 2)
      imgYPos = (scrnHt / 2) - (imgHt / 2)

      # Create the splash screen      
      self._splash = Tkinter.Toplevel()
      self._splash.overrideredirect(1)
      self._splash.geometry( '+%d+%d' % (imgXPos, imgYPos) )
      self.LblStat = Tkinter.Label( self._splash, text=self._splash_text, \
			compound=Tkinter.BOTTOM, fg='blue', \
			image=self._image, cursor='watch')
      self.LblStat.grid(row=0, column=0)

      # Force Tk to draw the splash screen outside of mainloop()
      self._splash.update( )

   def __exit__( self, exc_type, exc_value, traceback ):
      # Make sure the minimum splash time has elapsed
      timeNow = time.time()
      if timeNow < self._minSplashTime:
         time.sleep( self._minSplashTime - timeNow )

      # Destroy the splash window
      self._splash.destroy( )

      # Display the application window
      self._root.deiconify( )

"""
class SplashImage:
	def __init__(self, master):
		self.master = master
		screen_width = self.master.winfo_screenwidth()
		screen_height = self.master.winfo_screenheight()
		self.image = ImageTk.PhotoImage(splashim)
		w, h = splashim.size[0], splashim.size[1]
		self.master.bind('<Control-q>', self.master.destroy) 
		self.master.geometry('+%d+%d' % ((screen_width-w) /2 , (screen_height-h)/2))
		self.master.overrideredirect(1)
		self.parent = Frame(master)
		self.parent.pack()
		self.ImCanvas = Canvas(self.parent,width=w,height=h)
		self.ImCanvas.create_image(0,0,image=self.image,anchor=NW)
		self.ImCanvas.pack()
		homename = 'Quazar Technologies\n www.quazartech.com'
		canText = self.ImCanvas.create_text(w-20,h-20, \
				text=homename, \
				anchor=SE, \
				font=substatus_font, \
				fill='blue')
		return
		

	def show_progress(self):
		time.sleep(0.001)	
		return

	def disappear(self):
		self.parent.quit()
		self.master.destroy()
		return

	def main(self):
		k = KillThread()
		k.vGetCanvas(self)
		k.start()
		self.master.mainloop()
		return

class KillThread(threading.Thread):
	def __init__(self):
		#print 'Killer Thread Activated ...'
		self.lock=threading.Lock()
		threading.Thread.__init__(self)
		return

	def vGetCanvas(self, oSplash):
		self.master = oSplash.master
		self.ImCanvas = oSplash.ImCanvas
		return 

	def run(self):
		opening_text = 'SiM - nanoREV Control Application...Loading'
		status = 4
		canText = self.ImCanvas.create_text(20,20, \
					text=opening_text, \
					anchor=NW, \
					font=status_font, \
					fill='blue')
		canDot = self.ImCanvas.create_oval(20,50,30,60,\
					outline='blue', \
					fill='blue')
		refresh_count = 0
		count = 0
		step = 1
		while(1):
		    refresh_count +=1
		    if refresh_count > 10:
			refresh_count = 0
		        count += step
		        self.ImCanvas.move(canDot,step*2,0)
		        if count < 0 or count > 150:
			    step *= -1
		    time.sleep(0.01)
		    try:
		        f = open(apploadinglog)
		        lines = f.readlines()
		        f.close()
		    except:
			continue
		    try:
			if lines[-1] == 'Done\n':
			    break
		    except:
			continue
		    if len(lines) > status:
			try:
			    self.ImCanvas.delete(canText)
			except:
			    pass
			
		        canText = self.ImCanvas.create_text(20,20, \
					text=lines[status-1], \
					anchor=NW, \
					font=status_font, \
					fill='blue')
			status += 1
		    self.master.update()
		self.lock.acquire()
		#print 'Now destroy'
		s.parent.quit()
		try:
			s.master.destroy()
		except:
			pass
		self.lock.release()
		return
	
splashim = Image.open(Imagefilename)

from Tkinter import *
if __name__=='__main__':
	# Blanking Logfile
	f = open(apploadinglog, 'w')
	f.close()
	root = Tk()
	s = SplashImage(root)
	s.main()
"""
