from Tkinter import *
import tkSimpleDialog
import tkFileDialog
import tkMessageBox
from PIL import Image
import numpy 
import os

import app_import
import iprog
import dialogs

FileTypes = 	( \
		  ('ASCII Image Files', '*.txt'),\
		  ('JPG Image Files', '*.jpg'),\
		  ('PNG Image Files', '*.png'),\
		  ('GXSM Image Files', '*.nc'),\
		  ('GXSM ASCII Files', '*.gxsm'),\
	    	)
def Import_(oToolbar=None):

	"""
	Function : Import
        	Returns an object of class Import

	Arguments :
		To diaplay the images toolbar provides handle for Scanner
	Returns :
		oImport : object of class Import
	"""
        oImport = Import(oToolbar)
        return oImport
 
class Import:
	
	def __init__(self, oToolbar):
		"""
		Class Constructor: 
			Import
		Arguments : 
			None
		Returns : 
			None
		1. Open a text file with:
		    -- 256x256 array of floating point numbers, 
		    -- each row with 256 floats seperated by tabspace ending with a tab space
		    -- If there is a header in the text file then:
			* it is seperated from the array by a newline from main data
		2. Make a scan image array of class numpy
		3. Take default dic parameters
		4. Display Imported image
		"""
    		path = dialogs.strPathTracker()
		filename = tkFileDialog.askopenfilename(\
			defaultextension='.txt', \
			title='Import', \
			filetypes=FileTypes, \
			initialdir=path)
		if not filename:
		    return
    		dialogs.strPathTracker(filename)
		dicImportFrom = {'txt' : self.afImportFromASCII, \
		   	       	'gxsm' : self.afImportFromASCII, \
		   	       	'nc'   : self.afImportFromGXSM, \
		   	       	'jpg'  : self.afImportFromJPG, \
		   	       	'png'  : self.afImportFromJPG, \
				}
		ext = filename.rsplit(os.extsep, 1)[1]
		data = dicImportFrom[ext](filename)
		self.oToolbar = oToolbar
		if not self.oToolbar:
		    self.vSaveImportedDataToPic()
		    return
		self.oToolbar.oScanner.dicScanParam = dialogs.dicDefaultParam
		self.oToolbar.oScanner.vDisplayImages(data, data)
		return

	def afImportFromASCII(self, filename):
		"""
		Method : afImportFromASCII
			Reads data from a text file and return back numpy class scan matrix	

		Arguments :
			Text file name

		Returns :
			2D array of float values of a scan matrix		
		"""
		asciifd = open(filename)
		strAllData = asciifd.read()
		asciifd.close()
		arAllData = strAllData.split('\n')
		data = []
		for row in arAllData:
		    if len(row.split()) <= 128:
			continue
		    data.append(map(lambda(x):float(x), row.split())) 
		scandata = numpy.asarray(data)
		return scandata[:256,:256]
		
	def afImportFromGXSM(self,filename):
		"""
		Method : afImportFromGXSM
			Extracts data from ".nc" file	
		
		Arguments : 
			filename : string filename
		
		Returns :
			2D array of float values of a scan matrix		
		"""
		f = NetCDFFile(filename,"r")
		size = [f.dimensions['dimx'],f.dimensions['dimy']]
		try:
			data = f.variables['H']
		except:
			data = f.variables['FloatField']
		f.close()
		tmp = data.getValue()
		scandata = numpy.asarray(tmp[0][0])
		return scandata

	def afImportFromJPG(self,filename):
		"""
		Method : afImportFromJPG
			Extracts data from ".jpg" file
 	
		Arguments :
			filename : string filename

		Returns :
			2D array of float values of a scan matrix		
		"""
		im=Image.open(filename).convert('L')
		print "Image Size: ", im.size
		ImData=im.getdata()
		ImMatrix=numpy.asarray(ImData)
		ImMatrix.resize((im.size[1], im.size[0]))
		scandata = ImMatrix[:256, :256]		
		return scandata 

	def vSaveImportedDataAsPic(self):
		pass
		return

if __name__ =="__main__":
	Import_()
