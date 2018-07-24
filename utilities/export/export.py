####################
#   Export Class   #
####################
from Tkinter import *
import tkFileDialog, tkMessageBox
import os
import cPickle

import dialogs
import import_

FileTypes = 	( \
		  #('ASCII Image Files', '*.txt'),\
		  ('nanoREV Image Files', '*.npic'),\
		  #('Gxsm ASCII Files', '*.gxsm'),\
	    	)

def export(master):
	"""
        Returns an object of class Export
	"""
        oExport = Export(master)
        return oExport

class ExportGUI(dialogs.GridDialog):
	def __init__(self, master, exportOptsVar, exportOpts, filenameVar):
		self.exportOptsVar = exportOptsVar
		self.exportOpts = exportOpts 
		self.filenameVar = filenameVar
		dialogs.GridDialog.__init__(self, master ,'Export Options')
		return

	def body(self, master):
		self.master = master
		#self.configExportOptions()
		optionsFrame = LabelFrame(self.master)
		optionsFrame.grid(row = 0, column = 0, columnspan = 2)
		row = 0
		for opt in self.exportOpts:
			if opt == '.npic':
				text = opt + ' (Split Multi-channel Image File)'
			else:
				text = opt
			rb = Radiobutton(optionsFrame, text = text, value = opt, variable = self.exportOptsVar)
			rb.grid(row = row, column = 0, columnspan = 2, sticky = W)
			row += 1
		row += 1
		Label(optionsFrame, text = 'Save exported file as: ').grid(row = row, column = 0)
		TextFilename = Entry(optionsFrame, textvariable = self.filenameVar)
		TextFilename.grid(row = row, column = 1)
		#TextFilename.insert(0, self.filenameVar.get())
		row += 1
		btnApply = Button(self.master, text='Apply', width=7, command=self.okCB)
		btnApply.grid(row=1, column=0, padx=3, pady=3, sticky=N+E+W+S)
		btnCancel = Button(self.master, text='Cancel', command=self.cancelCB)
		btnCancel.grid(row=1, column=1, padx=3, pady=3, sticky=N+E+W+S)
		return

	def okCB(self):
		filename = self.filenameVar.get() + self.exportOptsVar.get()
		self.filenameVar.set(filename)
		self.ok()

	def apply(self):
		pass

	def cancelCB(self):
		filename = None
		self.filenameVar.set(filename)
		self.cancel()


class Export:
	 
	def __init__(self, master):
		"""
		Export Class Constructor
		"""
		ext = '.npic'
		dicExport2 = { 	'.txt' : self.vExport2ASCII, \
				'.npic': self.export2SplitChannels, \
		       		'.gxsm'  : self.vExport2GXSM }
    		fd = open(dialogs.trackerlogfile)
		path = fd.readline().strip()
		self.strOrigFilename = fd.readline()
		fd.close()
		filepath, filename = os.path.split(self.strOrigFilename)

		validExt = []
		for key in dicExport2.keys():
			validExt.append(str(key))
		self.exportOptSelectedVar = StringVar()
		self.exportOptSelectedVar.set(validExt[0])
		self.ExportFilenameVar = StringVar()
		self.ExportFilenameVar.set(os.path.splitext(filename)[0])

		oExportGUI = ExportGUI(master, self.exportOptSelectedVar, validExt, self.ExportFilenameVar)

		if self.ExportFilenameVar.get() == 'None':
			return
		fname, ext = os.path.splitext(self.ExportFilenameVar.get())
		if ext == '':	# Actually if filname is left blank, split make the extn as filename and extn is blank
			tkMessageBox.showerror('Cannot Export', 'Please enter valid filename...')
			return

		exportFile = os.path.join(filepath, self.ExportFilenameVar.get()) 
		print exportFile
		exportext = os.path.splitext(exportFile)[1]
		status = dicExport2[exportext](exportFile)
		if status == False:
			tkMessageBox.showerror('Cannot Export', 'Please check error details on terminal...')
		else:
			tkMessageBox.showinfo('Export Success', self.ExportFilenameVar.get() + ' exported successfully, find more details on the terminal...')
		return

	def vExport2ASCII(self, filename):
		"""
		Converts ".pic" file to ".ascii"
		"""
		[s, r, d] = import_.aafReadPicFile(self.strOrigFilename)
		if self.bPic2ASCII(filename, s, d, 'scan') == False:
		    print 'Failed to convert scan image to ASCII...'
		    return False
		self.bPic2ASCII(filename, r, d, 'ret')
		return True 

	def bPic2ASCII(self, filename, data, param, type_):
		strASCIIfilename = os.path.join(os.path.split(filename)[0], os.path.splitext(os.path.split(filename)[1])[0] + type_ + '.txt')
		print 'Converting pic to ASCII file: ', strASCIIfilename
		try:
		    asciifd = open(strASCIIfilename, 'w')
		except:
		    print 'Cannot Open File', 'Write permission denied \n Please try another folder'
		    return False
		for key in param:
		    asciifd.write(str(key) + ': ' + str(param[key]) + '\n')
		asciifd.write('\n')
		for i in range(0,data.shape[0]):
			for j in range(0,data.shape[1]):
				asciifd.write(str(data[i][j])+'\t')
			asciifd.write('\n')
		asciifd.close()
		return True

	def export2SplitChannels(self, filename):
		[s, r, d] = import_.aafReadPicFile(self.strOrigFilename)
		if d.has_key('NoOfChannels'):
			noc = d['NoOfChannels']
		else:
			print 'Please select an image having multi-channel data...'
			return False
		if noc == 1:
			print 'Please select an image having multi-channel data...'
			return False
		basename, ext = os.path.splitext(filename)
		dicNew = d.copy()
		dicNew['NoOfChannels'] = 1
		for count in range(noc):
			newfilename = basename + '_Chn' + str(count) + ext
			print 'Split Channel Data written to...', newfilename
			fd = open(newfilename, 'w')
			dicNew['ChannelNames'] = [ d['ChannelNames'][count] ]
			cPickle.dump(s[count], fd)
			cPickle.dump(r[count], fd)
			cPickle.dump(dicNew, fd)
			fd.close()
		return True

	def vExport2GXSM(self, filename):
		"""
		Converts ".pic" file to ".gxsm", which is an ascii file that
		can be read by the gxsm software.
		"""
		[s, r, d] = import_.aafReadPicFile(self.strOrigFilename)
		self.vPic2GXSMASCII(filename, s, d, 'scan')
		self.vPic2GXSMASCII(filename, r, d, 'ret')
		return True		

	def vPic2GXSMASCII(self, filename, data, param, type):
		strASCIIfilename = filename.rsplit(os.extsep,1)[0] + type + '.gxsm'
		print 'Converting pic to GXSM ASCII file: ', strASCIIfilename
		asciifd = open(strASCIIfilename, 'w')
		asciifd.write('scan length= '+str(param['ImageSize'][1])+'\n')
		asciifd.write('points/line= '+str(param['ImageSize'][0])+'\n')
		asciifd.write('points spacing= '+str(param['StepSize'][0])+'\n')
		asciifd.write('# lines= '+str(param['StepSize'][0])+'\n')
		asciifd.write('line spacing= '+str(param['StepSize'][1])+'\n')
		asciifd.write('points in average=1'+'\n')
		asciifd.write('velocity= '+str(param['Delay'])+'\n')
		asciifd.write('lock in constant (msec)= '+str(param['Gain'])+'\n') # dummy
		asciifd.write('X origin= '+str(param['XOffset'])+'\n')
		asciifd.write('Y origin= '+str(param['YOffset'])+'\n')
		asciifd.write('\n')
		asciifd.write('end'+'\n')
		asciifd.write('\n')
		for i in range(0,data.shape[0]):
			for j in range(0,data.shape[1]):
				asciifd.write(str(data[i][j])+'\t')
			asciifd.write('\n')
		asciifd.close()
		return 

if  __name__=="__main__":
	export()
