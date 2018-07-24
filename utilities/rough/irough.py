######################
#   IRough Class     #
######################
from Tkinter import *
import iprog
import scanner

def irough(oQlaunch, oImaging, nADCGain):
	"""
	Function : irough
		Returns IRough object

	Arguments :
		oQlaunch : object of class QuickLaunch
		oImaging : object of class Imaging

	Returns :
		oir : object of class IRough
	"""
	oir=IRough(oQlaunch, oImaging, nADCGain)
	return oir

class IRough:
	
	def __init__(self,oQlaunch, oImaging, nADCGain):
		"""
		Class Contructor : IRough
	
		Arguments :
			oImaging : object of class Imaging
	
		Returns :
			None
		"""
		self.oImaging = oImaging
		self.oAppImaging = oImaging.oAppImaging
		self.color = 'blue'
		self.vLaunchIRough()
		return

	def vLaunchIRough(self):
		"""
		Method : vLaunchIRough
			Calculates & Displays Image Roughness	
				
		Arguments :
			None
	
		Returns :
			None
		"""
		self.vCalculateIRough()
		self.vDisplayIRough()
		return

	def vCalculateIRough(self):
		"""
		Method : vCalculateIRough
			Calculates Image's Mean Stddev values
				
		Arguments :
			None
				
		Returns :
			None
		"""
		afScanData = self.oImaging.oScanner.afCalculateNormalizedImageData(1)# Scan
		afRetData  = self.oImaging.oScanner.afCalculateNormalizedImageData() # Retrace
		(self.fScanMean,self.fScanStddev) = self.afCalculateParams(afScanData)
		(self.fRetMean,self.fRetStddev) = self.afCalculateParams(afRetData)
		return

	def afCalculateParams(self,fmatrix):
		"""
		Method : afCalculateParams
			Calculates's Images Parameters like Mean and Standard Deviation.
	
		Arguments :
			fmatrix : float image matrix
				
		Returns :
			None
		"""
		PIEZO_Z = scanner.fGetPiezoZCalibration()/1e3	# Data in mV and calib in nm/V
		mean = fmatrix.mean()
		stddev = fmatrix.std()
		return [mean*PIEZO_Z, stddev*PIEZO_Z]

	def vDisplayIRough(self):
		"""
		Method : vDisplayIRough
			Displays Image Roughness
	
		Arguments :
			None
				
		Returns :
			None
		"""
		self.vClearCanvas()
		self.vShowIRough()	
		return

	def vClearCanvas(self):
		"""
		Method : vCleanCanvas
			Deletes old values from the Imaging Canvas
	
		Arguments :
			None
				
		Returns :
			None
		"""
		try:
			self.oAppImaging.CanvasScan.delete(self.oImaging.sScanMean)
			self.oAppImaging.CanvasScan.delete(self.oImaging.sScanStddev)
		except:
			pass
		try:
			self.oAppImaging.CanvasRetrace.delete(self.oImaging.sRetMean)
			self.oAppImaging.CanvasRetrace.delete(self.oImaging.sRetStddev)
		except:
			pass
		return
		
	def vShowIRough(self):
		"""
		Method : vShowIRough
			Displays Image's Mean & Stddev values
	
		Arguments :
			None
				
		Returns :
			None
		"""
		self.oImaging.sScanMean = self.oAppImaging.CanvasScan.create_text(160,220,\
								text='Mean    '+str('%3.2f'%self.fScanMean)+' nm',\
								anchor = NW,\
								activefill='black', \
								fill = self.color)
		self.oImaging.sScanStddev = self.oAppImaging.CanvasScan.create_text(160,240,\
								text='Stddev  '+str('%3.2f'%self.fScanStddev)+' nm',\
								anchor = NW,\
								activefill='black', \
								fill = self.color)
		if self.oImaging.bDumpVar.get()==False:
			self.oImaging.sRetMean = self.oAppImaging.CanvasRetrace.create_text(160,220,\
								text='Mean    '+str('%3.2f'%self.fRetMean)+' nm',\
								anchor = NW,\
								activefill='black', \
								fill = self.color)
			self.oImaging.sRetStddev = self.oAppImaging.CanvasRetrace.create_text(160,240,\
								text='Stddev  '+str('%3.2f'%self.fRetStddev)+' nm',\
								anchor = NW,\
								activefill='black', \
								fill = self.color)
		return
