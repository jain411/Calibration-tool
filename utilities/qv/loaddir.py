from Tkinter import *

import FileDialog

class LoadDirDialog(FileDialog.LoadFileDialog):
	"""
	To select the directory from which files are to be viewed
	"""
	def __init__(self, master):
	    FileDialog.LoadFileDialog.__init__(self, master)
	    return

	def godir(self, dir_or_file=None, key=None):
	    self.files.unbind('<ButtonRelease-1>')
	    self.files.unbind('<DoubleButtonRelease-1>')
	    self.go(dir_or_file=dir_or_file, key=key)
	    #print FileDialog.dialogstates['track']
	    return self.directory

	def ok_command(self):
	    self.master.quit()

if __name__ == "__main__":
  root = Tk()
  fd = LoadDirDialog(root)
  dir = fd.godir(key='track')
  print dir
  root.mainloop()
