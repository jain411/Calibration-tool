########################
#   Calibration Class  #
########################
from Tkinter import *
import tkMessageBox, tkSimpleDialog
import tkFileDialog
import numpy
from PIL import Image
from PIL import ImageTk
import math
import time
import itertools
import os

import app_calibration
import iprog
import dialogs
import import_

SIGMA	= 2.5
variable = 1

FILETYPES = {	'npic':('SiM Files','*.npic'),\
		#'dat':('Old Stm Files','*.dat'), \
		}					# Stm File types 

def calibration(f=None, oMenuBar=None, olut=None):
	"""
	Returns Calibration object
	"""
	if not f:
		root=Tk()
		f=Frame(root).grid()
	oAppCalib = app_calibration.app_calibration()
	oAppCalib.createCSwindow(f)
	oCalibration = Calibration(oAppCalib, oMenuBar, olut)	
	if not f:
		root.title('Calibration')
		root.mainloop()
	return oCalibration
      
      
#############################
class GridBasedCalibration:
  '''
  To process image-data in the form of a grid, which is made out of maxima points
  '''  
  def __init__(self):#, rawImageData):
    '''
    Class Contructor : Calibration
    '''
    self.gridPointsInLine = []
    #self.rawImageData = rawImageData
    return 
  
  def __createGrid(self,imageArray,maskSize):
    '''
    Returns grid image to getGrid
    '''
    imageSize = numpy.shape(imageArray)
    self.maximaPointIndices = numpy.ones((0,2), dtype = int)
    gridImage = numpy.zeros((256,256), dtype = float)   
    for i in range((maskSize/2),255 - (maskSize/2)):
      for j in range((maskSize/2),255 - (maskSize/2)):
        position = imageArray[(i - (maskSize/2)):(i + (maskSize/2) + 1), (j - (maskSize/2)):(j + (maskSize/2) + 1)].argmax()
        xCoordinate = position % maskSize
        yCoordinate = position / maskSize
        if(xCoordinate == maskSize/2 and yCoordinate == maskSize/2):
	    xPosition = i - (maskSize/2) + xCoordinate
            yPosition = j - (maskSize/2) + yCoordinate
            self.maximaPointIndices = numpy.append(self.maximaPointIndices, [[yPosition,xPosition]],axis = 0)   
       
    # Making all maxima points similar irrespective of their magnitudes

    for k in range(len(self.maximaPointIndices)):
	gridImage[self.maximaPointIndices[k][1], self.maximaPointIndices[k][0]] = 255
    
    
    # Making an image using maxima points:
    #%matplotlib 
    #plt.imshow(gridImage,cmap = 'gray')
    return gridImage
  
  def getmaximaPointIndices(self):
    '''
    Returns maximaPointIndices
    '''
    return self.maximaPointIndices
  
  
  def getGrid(self,imageArray, maskSize):
    '''
    Calls __createGrid and returns grid matrix
    '''
    finalGrid = self.__createGrid(imageArray, maskSize)
    return finalGrid
  
  def __distancefromline(self,adjacentPoint,lineCoordinates):
     '''
     Returns the distance between a point and a line
     '''
     slopeOfLine = self.__slope(lineCoordinates[0], lineCoordinates[1])
     if(slopeOfLine == lineCoordinates[0][0]):
        distanceOfPointFromLine = (adjacentPoint[0] - slopeOfLine)
        return abs(distanceOfPointFromLine)
     distanceOfPointFromLine = ((slopeOfLine * adjacentPoint[0]) - (adjacentPoint[1]) + (lineCoordinates[0][1] - (slopeOfLine * lineCoordinates[0][0])))/(math.sqrt(1+(slopeOfLine**2))) 
     return abs(distanceOfPointFromLine)
  
  def __slope(self,x,y):
    '''
    Returns the slope of line joining two points
    '''
    if ((x[0]-y[0]) != 0):
        sl = (1.0*x[1]-y[1])/(x[0]-y[0])
        return sl
    if ((x[0]-y[0]) == 0):
        return x[0] 
  
  
  def __lineSelect(self,initialPoint, finalPoint, adjacentPoint, allowedRange):
    '''
    Selects all the points which should lie on the line joining the two points
    '''
    self.lineCollector = []
    for maximaPoints in self.maximaPointIndices:
        if(min(finalPoint[0],initialPoint[0]) <= maximaPoints[0] <= max(finalPoint[0],initialPoint[0])):
            if(min(finalPoint[1],initialPoint[1]) <= maximaPoints[1] <= max(finalPoint[1],initialPoint[1])):        
                distance = self.__distancefromline(maximaPoints,[finalPoint,initialPoint])
                if ((distance) <= allowedRange):
                    self.lineCollector.append(maximaPoints)
    self.gridPointsInLine.append(self.lineCollector)
                    
    return
  
 
  
  def getGridPointsInLine(self, initialPoint, finalPoint, adjacentPoint):
    '''
    Calls __lineSelect and sets an allowed range for points to be on the line
    '''
    distanceFromLine = self.__distancefromline(adjacentPoint,[initialPoint,finalPoint])
    allowedRange = 0.4 * distanceFromLine                    
    self.__lineSelect(initialPoint, finalPoint, adjacentPoint, allowedRange)
    return self.gridPointsInLine, self.lineCollector
  
  
  
	
class Calibration:
	
	LATTICE_CONSTT = 2.456
	oGridBasedCalib = GridBasedCalibration()
		 
	def __init__(self, oAppCalib, oMenuBar, olut):
		"""
		Class Contructor : Calibration
		"""
		self.oAppCalib = oAppCalib                
	 	self.oMenuBar = oMenuBar
		self.olut = olut
		self._configureCB()
		self._initCalib()
		self.linePoints = []
		self.pointsOnLine = []
		self.currentLine = []
		self.lineData = []
		
		return

	def _configureCB(self):
		"""
		Attaches Callbacks to CalibGui widgets 
		"""
		'''
		self.oAppCalib.ArrCanvas.bind('<Button-1>', self.vBeginLine)
		self.oAppCalib.ArrCanvas.bind('<B1-Motion>', self.vShowLine)
		self.oAppCalib.ArrCanvas.bind('<ButtonRelease-1>', self.vEndLine)
		'''
		self.gridCheckButton = IntVar()
		self.imageCheckButton = IntVar()
		self.scaleValue = self.oAppCalib.SliderMaskLen.get()
		#self.oAppCalib.btnOpen.configure(command=self.vOpenCB)
		#self.oAppCalib.btnZoom.configure(command=self.CanZoomInCB)
		#self.oAppCalib.btnOrig.configure(command=self.CanZoomOutCB)
		#self.oAppCalib.btnQuit.configure(command=self.vQuitCB)
		self.oAppCalib.filemenu.add_command(label='Open',command=self.vOpenCB)
		self.oAppCalib.filemenu.add_command(label='Quit',command=self.vQuitCB)
		self.oAppCalib.utilitiesmenu.add_command(label='Zoom',command=self.CanZoomInCB)
		self.oAppCalib.utilitiesmenu.add_command(label='Original',command=self.CanZoomOutCB)
		self.oAppCalib.settingsmenu.add_command(label='Lattice Constant',\
								command=self.vSetLatticeConstt)
		self.oAppCalib.settingsmenu.add_command(label='Color Settings',\
								command=self.vChangeColorSettings)
		self.oAppCalib.calibrationmodemenu.add_command(label='Grid Mode',command=self.gridModeWindowCB)
		self.oAppCalib.calibrationmodemenu.add_command(label='Line Mode', command=self.__lineModeDisplayCB)  
		self.oAppCalib.CBShowGrid.configure(command = self.__gridDisplayCB, variable = self.gridCheckButton)
		self.oAppCalib.CBShowImage.configure(command = self.__imageDisplayCB, variable = self.imageCheckButton)
		self.oAppCalib.BtnAddLine.configure(command = self.__detectLinePointsCB)
		self.oAppCalib.BtnRemoveLine.configure(command = self.__removeLineCB)
		self.oAppCalib.BtnAnalyze.configure(command = self.__findStatisicsCB)
		self.oAppCalib.BtnExport.configure(command = self.__exportDataCB)
		self.oAppCalib.SliderMaskLen.configure(command = self.setMaskSize,\
						      variable = self.scaleValue)
		self.oAppCalib.csGroup.protocol('WM_DELETE_WINDOW',self.vQuitCB)
		return
	      
	
	  
	
	def __lineModeDisplayCB(self):
	  '''
	  Opens image in Line Mode
	  '''
	  self.oAppCalib.LFInfoGroup.grid_forget()
	  self.oAppCalib.BtnAddLine.configure(state = DISABLED)
	  self.oAppCalib.BtnRemoveLine.configure(state = DISABLED)
	  self.oAppCalib.BtnAnalyze.configure(state = DISABLED)
	  self.oAppCalib.BtnExport.configure(state = DISABLED)
	  self.oAppCalib.ArrCanvas.bind('<Button-1>', self.vBeginLine)
	  self.oAppCalib.ArrCanvas.bind('<B1-Motion>', self.vShowLine)
	  self.oAppCalib.ArrCanvas.bind('<ButtonRelease-1>', self.vEndLine)
	  
	  return
	
	def gridModeWindowCB(self):
	  '''
	  Creates frames for working with grid mode
	  '''
	  self.oAppCalib.LFgridViewDisp.grid(row=0, column=5, sticky=N+S)
	  self.oAppCalib.LFInfoGroup.grid(row = 1, column = 0,columnspan = 6)
	  self.ciAllHighlightedPoints = []	# Tags of all oval canvas items
	  '''
	  gridPoints = self.oGridBasedCalib.getGrid()
	  for i in range(len(gridPoints)):
	      self.oAppCalib.ArrCanvas.create_oval(gridPoints[i][0],gridPoints[i][1],gridPoints[i][0],gridPoints[i][1], width = 1, fill = 'black')   
	  '''
	  return
	
	def __detectLinePointsCB(self):
	  '''
	  Binds mouse click for adding lines 
	  '''
	  self.oAppCalib.ArrCanvas.bind('<Button-1>', self.__addLinePoints)
	  self.ciHighlightedPoints = [] # Tags of oval canvas items of one line
	  return
	
	def  __addLinePoints(self,event):
	  '''
	  For selection of three points to add line in grid
	  '''
	  range_ = 6
	  xCoordinate = event.x
	  yCoordinate = event.y
	  for index in self.oGridBasedCalib.getmaximaPointIndices():
	    if((index[0] < xCoordinate + range_ and index[0] > xCoordinate - range_) and (index[1] < yCoordinate + range_ and index[1] > yCoordinate - range_) ):
 	         #print(index)	                
                 self.linePoints.append([xCoordinate,yCoordinate])
                 if(len(self.linePoints) % 3 == 1):   
                     #print("Point 1 of line selected:"+ str(index) +"\n Select point 2\n") 
                     self.highlightPoints(index[0],index[1])
                     break
		   
                 if(len(self.linePoints) % 3 == 2):
                     #print("Point 2 of line selected:" + str(index)+'\n')
                     self.highlightPoints(index[0],index[1])
                     #print(" Select a point from an adjacent line ")
                     break

                 if(len(self.linePoints) % 3 == 0):
                     print("Adjacent Point selected \n")
		     self.pointsOnLine, self.currentLine = self.oGridBasedCalib.getGridPointsInLine(self.linePoints[-3], self.linePoints[-2], self.linePoints[-1])
		     for point in self.currentLine:
		       self.highlightPoints(point[0], point[1])
		     self.oAppCalib.ArrCanvas.unbind('<Button-1>')
		     self.ciAllHighlightedPoints.append(self.ciHighlightedPoints)
		     totalLineLength = math.sqrt((self.currentLine[0][0]- self.currentLine[-1][0])**2 + (self.currentLine[0][1]- self.currentLine[-1][1])**2)
		     bondLengthInPixels = totalLineLength/(len(self.currentLine)-1)
		     calibrationConstant = 245.6 / (bondLengthInPixels * self.nXYStepSize)
		     self.lineData.append([totalLineLength,bondLengthInPixels,calibrationConstant])
		     self.__vUpdateList()
	  return
                     
	  
	  
	def highlightPoints(self, xCoord, yCoord):
	  '''
	  Highlights selected points in the grid
	  '''
	  ciOval = self.oAppCalib.ArrCanvas.create_oval(xCoord, yCoord, xCoord, yCoord, width = 5, outline = 'blue')
	  self.ciHighlightedPoints.append(ciOval)
	  self.oAppCalib.ArrCanvas.update()
	  return
	
	def unHighlightPoints(self, lineNo):
	  '''
	  Used when remove line is pressed
	  '''
	  for canItems in self.ciAllHighlightedPoints[lineNo]:
		  self.oAppCalib.ArrCanvas.delete(canItems)
	  self.oAppCalib.ArrCanvas.update()
	  return
	
	def setMaskSize(self, variable):
	  '''
	  sets the mask size according to mask slider position
	  '''
	  self.maskSize = 2 * int(variable) + 1
	  self.__gridDisplayCB()
	  return
	
	def __findStatisicsCB(self):
	  '''
	  Finds the mean and standard deviations of required fields
	  '''
	  meanValueBondLength = sum([row[1] for row in self.lineData])/len(self.lineData)
          meanValueCalibration = sum([row[2] for row in self.lineData])/len(self.lineData)
          self.oAppCalib.ListLine.insert(END, "Mean " + "    " + "    " + "         " + str(format(meanValueBondLength,'.2f')) + \
	                              "    " + str(format(meanValueCalibration,'.2f')))
	  standardDevBondLength = numpy.std([row[1] for row in self.lineData])
	  standardDevCalibration = numpy.std([row[2] for row in self.lineData])
	  self.oAppCalib.ListLine.insert(END, "StDev" + "    " + "    " + "         " + str(format(standardDevBondLength,'.2f')) + \
	                              "      " + str(format(standardDevCalibration,'.2f')))
          return

	def __exportDataCB(self):
	  '''
	  Exports the image data obtained to a CSV file
	  '''
	  filename = os.path.splitext(self.fileName)[0] + '_calib.csv'
	  fileTag = open(filename, 'w')
	  fileTag.write('Line No., Line Length (Pix), Bond Length(Pix), Calib Const.(nm/V)' + '\n')
	  lineNo = 0
	  for item in self.lineData:
	    lineNo += 1
	    fileTag.write(str(lineNo) + ',' + str(format(item[0],'.2f')) + ',' + str(format(item[1],'.2f')) + ',' + str(format(item[2],'.2f'))\
			+ '\n')
	  fileTag.close()
	  self.oAppCalib.ListLine.insert(END, 'Calib Data filename: ' + filename)
	  return

	def __removeLineCB(self):
	  '''
	  Removes the selected line
	  '''
	  sel_indices = self.oAppCalib.ListLine.curselection()
	  sel_indices = map(lambda(x):int(x), sel_indices)   # converting string values to int
	  sel_indices.sort(reverse = True)
	  for index in sel_indices:
	    self.oAppCalib.ListLine.delete(index)
	    del self.lineData[index-1]
	    del self.pointsOnLine[index-1]
	    self.unHighlightPoints(index-1)
	    del self.ciAllHighlightedPoints[index-1]
	  self.__vUpdateList()
	  return
	
	def __gridDisplayCB(self):
	    '''
	    Displays the image in grid form
	    '''
	    gridMatrix = self.originalImageMatrix.copy()
	    if(self.gridCheckButton.get()):
	      self.oAppCalib.CBShowImage.configure(state = NORMAL)
	      self.imageCheckButton.set(0)
	      gridMatrix = iprog.correctSlope(gridMatrix)
	      gridMatrix = iprog.gaussian_(gridMatrix)
	      self.processedGrid = self.oGridBasedCalib.getGrid(gridMatrix,self.maskSize)
	      #Replace everything on the screen with grid image 
	      self.oAppCalib.ArrCanvas.delete("all")
	      for xIndex in range(len(self.processedGrid)):
		for yIndex in range(len(self.processedGrid)):
		  if(self.processedGrid[xIndex][yIndex] == 255):
		    self.oAppCalib.ArrCanvas.create_oval(yIndex , xIndex , yIndex , xIndex, width = 1, outline = 'blue')
	      self.oAppCalib.ArrCanvas.update()
	     
	    else:
	      imageMatrix = self.originalImageMatrix.copy()
	      self.vShow(imageMatrix) 
	      if( self.imageCheckButton.get()):		
		self.oAppCalib.CBShowImage.configure(state = DISABLED)
	      if( not self.imageCheckButton.get()):
		self.imageCheckButton.set(1)
		self.oAppCalib.CBShowImage.configure(state = DISABLED)
	    return  
	
	def __imageDisplayCB(self):
	  '''
	  Displays the image in normal form
	  '''
	  if(self.imageCheckButton.get()):
	    imageMatrix = self.originalImageMatrix.copy()
	    self.vShow(imageMatrix)
	    
	    for xIndex in range(len(self.processedGrid)):
	      for yIndex in range(len(self.processedGrid)):
		if(self.processedGrid[xIndex][yIndex] == 255):
		  self.oAppCalib.ArrCanvas.create_oval(yIndex , xIndex , yIndex , xIndex, width = 1, outline = 'white')
	    self.oAppCalib.ArrCanvas.update()
	    
	  else:
	    self.oAppCalib.ArrCanvas.delete("all")
	    for xIndex in range(len(self.processedGrid)):
	      for yIndex in range(len(self.processedGrid)):
		if(self.processedGrid[xIndex][yIndex] == 255):
		  self.oAppCalib.ArrCanvas.create_oval(yIndex , xIndex , yIndex , xIndex, width = 1, outline = 'blue')
	    self.oAppCalib.ArrCanvas.update()
	  return
	
	def __vUpdateList(self):
	  '''
	  Shows data related to lines selected 
	  '''
	  self.oAppCalib.ListLine.delete(0,END)
	  nROI = 0
	  self.oAppCalib.ListLine.insert(END, "Line    Line Len    Bondlen(pix)    Calib(nm/V)")
	  for lines in self.lineData:
	    self.oAppCalib.ListLine.insert(END, "Line" + str(nROI+1) + "    " + str(format(lines[0],'.2f')) + "    " + str(format(lines[1],'.2f'))\
				+ "    " + str(format(lines[2],'.2f')))
	    nROI += 1
	  return
  
	def _initCalib(self):
		"""
		Inital Calibration Settings
		"""
		#self.oAppCalib.btnOrig.configure(state=DISABLED)
		self.bZoomIn=BooleanVar()
		self.nZoomedImageBuffer = []
		self.nZoomFactor = 2
		self.vChangeColorSettings(show=False)
		return

	def vChangeColorSettings(self, show=True):
	    dicGUISettings = dialogs.dicReadGUISettings()
	    self.strInfoColor = dicGUISettings['AreaInfo'][0]
	    self.strInfoColorActive = dicGUISettings['AreaInfo'][1]
	    self.strLineColor = dicGUISettings['LEC']	# Line Color
	    if show:
	        tkMessageBox.showinfo('Color Settings', \
					'Color settings taken from Main Window and applied...', \
					parent = self.oAppCalib.csGroup)
	    return

	def vQuitCB(self):
		"""
		Terminates Calibration Utility
		"""
		self.oMenuBar.Calib_Instance = 0	
		self.oAppCalib.csGroup.destroy()
		return	

	def vOpenCB(self):	
		"""
		Opens and Displays a User Select File	
		"""
		filename = self.fOpenFile()
		if not filename:
			return
		self.fileName = filename
		[fScanImageMatrix,fRetImageMatrix,fDicScanParam,sFileType] = import_.aafReadImageFile(filename)
		self.gridCheckButton.set(0)
		nImageMatrix=iprog.float2gray(fScanImageMatrix)
		self.originalImageMatrix = nImageMatrix.copy()
		self.nImageSize = fDicScanParam['ImageSize'][0]
		self.nXYStepSize = fDicScanParam['StepSize'][0]
		self.nZoomedImageBuffer.append(nImageMatrix)
		self.imageCheckButton.set(1)
		self.oAppCalib.CBShowImage.configure(state = DISABLED)
		self.vShow(nImageMatrix)
		return

	def fOpenFile(self):
		"""
		Pops up a Filemenu to open ".pic" / ".dat" to be displayed
		"""
		ftype=FILETYPES.values()
		filepath =dialogs.strPathTracker()
		file = tkFileDialog.askopenfilename(title='Load File', \
							defaultextension="pic", \
							filetypes=ftype, \
							initialdir=filepath, \
							parent = self.oAppCalib.csGroup)
		if not(file):
			tkMessageBox.showerror('File not selected', 'Please select an image file!', \
							parent = self.oAppCalib.csGroup)
		if not(file):
			return
		dialogs.strPathTracker(file)
		return file

	def vShow(self,nImageMatrix,min_max = True):
		"""
		Displays Image on the Image Canvas
		"""
		
		if nImageMatrix is None:
			print 'No Input Matrix'
			return None
		self.nImageMatrix = nImageMatrix
		if(min_max == True):
		  nImageMatrix = iprog.min_maxfilter(nImageMatrix.copy(), SIGMA)
		#nImageMatrix = iprog.repair(nImageMatrix.copy())	# slope correction
		self.vRenewCanvas(nImageMatrix)
		return

	def vRenewCanvas(self, nImageMatrix):
		"""
		Refreshes Image Canvas with the new Image data
		"""
		#nImageMatrix=im.gaussian_filter(nImageMatrix,1.1)
		self.vCreateImage(nImageMatrix)
		
		try:
		       
			self.oAppCalib.ArrCanvas.delete("all")
		        
		except:
			pass
		
		self.CanvasImage = self.oAppCalib.ArrCanvas.create_image(0,0,image=self.ArrIm,anchor=NW)
		self.ArrIm.paste(self.im)
		self.oAppCalib.ArrCanvas.config(width=nImageMatrix.shape[1], \
				height=nImageMatrix.shape[0] )
		
		self.oAppCalib.csGroup.update()
		
		return
	
	def vCreateImage(self, nImageMatrix):
		"""
		Configures Canvas for Gray/RGB Image Diaplay		
		"""
		[row, col] = nImageMatrix.shape
		nImageMatrix=iprog.float2gray(nImageMatrix)
		from PIL import Image
		#if self.bColorVar.get()==False:
		#	self.im = Image.new("I",[row*1,col*1])
		#	self.ArrIm = ImageTk.PhotoImage(self.im)
		#	self.im.putdata(nImageMatrix.flat)
		#if self.bColorVar.get()==True:
		self.im = Image.new("RGB",[row*1,col*1])
		self.ArrIm = ImageTk.PhotoImage(self.im)
		colmatrix=map(lambda(x):self.olut[int(x)],nImageMatrix.flat)
		self.im.putdata(colmatrix)
		return

	def CanZoomInCB(self):
		"""
		Zooms Current Display Image by a Factor of 2
		"""
		self.starttime=time.time()
		print "Zooming in"
		self.bZoomIn = True
		try:
			nZoomedImage = self.nZoomIn(self.nImageMatrix, self.nZoomFactor)
		except:
			return	
		self.nImageMatrix = nZoomedImage
		self.vRenewCanvas(nZoomedImage)
		print "time taken ",time.time()-self.starttime
		self.nZoomFactor+=1
		self.oAppCalib.btnOrig.configure(state=ACTIVE)
		return

	def CanZoomOutCB(self):
		"""
		Zoom out Current Display Image to original dimensions
		"""
		nOriginalImage = self.nCheckInZoomedBuffer()
		if nOriginalImage is None:
			return
		self.vRenewCanvas(nOriginalImage)
		self.nZoomFactor=2
		self.nImageMatrix = nOriginalImage
		self.oAppCalib.btnOrig.configure(state=DISABLED)
		return nOriginalImage

		
	def nCheckInZoomedBuffer(self):
		"""
		Tries to return Original Image data 
		"""
		try:
			nZoomedImage = self.nZoomedImageBuffer[-1]
		except:
			nZoomedImage = None
		return nZoomedImage

	def nZoomIn(self, nImageMatrix, factor):
		"""
		Zooms image by the specified Zoom factor
		"""
		nZoomedImage = self.zoom_in(nImageMatrix,factor)
		return nZoomedImage

	def vBeginLine(self, event):
		"""
		Gets Initial endpoint of the calibration line
		"""
		self.x0 = event.x
		self.y0 = event.y
		return

	def vShowLine(self, event):
		"""
		Displays and Renews Calibration line with mouse movements
		"""
		self.x1 = event.x
		self.y1 = event.y
		try :
			self.oAppCalib.ArrCanvas.delete(self.CanLine)
		except:
			pass
		self.CanLine = self.oAppCalib.ArrCanvas.create_line(self.x0, self.y0, self.x1, self.y1, \
							fill=self.strLineColor, \
							arrow=BOTH, \
							width=2)
		return

	def vEndLine(self, event):
		"""
		Fetches location of final endpoint
		"""
		if not self.CanLine:
			return
		fObservedXY_Step = self.fCalculateXY_Step()
		if fObservedXY_Step:
			self.vShowObservedXY_Step(fObservedXY_Step)
		return

	def vSetLatticeConstt(self):
		"""
		Asks to enter Lattice Constant for the material scanned from literature.
		"""
		lc = tkSimpleDialog.askfloat('Lattice Constant', \
						'Lattice Constant of the material \n (in ANGSTROMS):', \
						initialvalue=self.LATTICE_CONSTT, \
						minvalue = 0.1 , \
						parent = self.oAppCalib.csGroup)
		if not lc:
		    return
		else:
		    self.LATTICE_CONSTT = lc
		return 


	def nAskForNoOfAtoms(self):
		"""
		Fetches No. of Atoms covered by the Calibration line from the user
		"""
		nNoOfAtoms = tkSimpleDialog.askinteger('Atoms Count', 'Enter no. of atoms:', \
							minvalue = 1, \
							parent = self.oAppCalib.csGroup)
		return nNoOfAtoms

	def fCalculateDistanceInMV(self):
		"""
		Calulates length of calibration line in pixels 
		"""
		x = abs(self.x0 - self.x1)/(self.nZoomFactor-1)
		y = abs(self.y0 - self.y1)/(self.nZoomFactor-1)
		dist = math.sqrt(x**2 + y**2)	
		print x, y, dist			
		return dist

	def fCalculateXY_Step(self):
		"""
		Calculates observed Calibration Factor
		"""
		nNoOfAtoms = self.nAskForNoOfAtoms()
		if not nNoOfAtoms:
			try :
				self.oAppCalib.ArrCanvas.delete(self.CanText)
			except:
				pass
			self.oAppCalib.ArrCanvas.delete(self.CanLine)
			return None
		fAtomicDistance = self.LATTICE_CONSTT * nNoOfAtoms
		print 'Lattice Constant (in Angs): ', self.LATTICE_CONSTT
		fDistanceInMV = self.fCalculateDistanceInMV() * self.nXYStepSize
		fObservedXY_Step = fAtomicDistance / fDistanceInMV
		#fObservedXY_Span = (fObservedXY_Step*self.nXYStepSize) * self.nImageSize
		#print 'Total XY Span:'
		#print 'Observed-', fObservedXY_Span
		#print 'Theorectical-', self.THEORETICAL_XY_STEP/1000 * self.nImageSize * self.nXYStepSize
		#print 'Total Atoms Expected in X/Y: ', fObservedXY_Span/self.LATTICE_CONSTT 
		return fObservedXY_Step

	def vShowObservedXY_Step(self, fObservedXY_Step):
		"""
		Displays Observed Calibration Factor
		"""
		try:
			self.oAppCalib.ArrCanvas.delete(self.CanText)
		except:
			pass
		self.CanText = self.oAppCalib.ArrCanvas.create_text(0,0, anchor=NW, \
							fill=self.strInfoColor, \
							activefill=self.strInfoColorActive, \
							font=('Courier', 14, 'bold'), \
							text=str(fObservedXY_Step*100)+" nm/V")
		self.oAppCalib.csGroup.update()
		return

	def zoom_in(self,nImageMatrix, ZoomFactor=2):
		"""
		Converts Float Image data to gray scale 0 - 255
		"""
		xlen=int(nImageMatrix.shape[0]*ZoomFactor)
		padded_im=numpy.zeros([xlen,xlen],'f')
		for i in range(nImageMatrix.shape[0]):
			for j in range(nImageMatrix.shape[1]):
				padded_im[i*ZoomFactor][j*ZoomFactor]=nImageMatrix[i][j]
		row_vect=numpy.zeros([1,2*ZoomFactor-1],'f')
		col_vect=numpy.zeros([2*ZoomFactor-1,1],'f')
		result=self.arBartlettFilter(ZoomFactor)
		nZoomedImage=numpy.convolve(padded_im,result)
		return nZoomedImage
	
	def arBartlettFilter(self,ZoomFactor):
		"""
		Generates Bartlett filter kernel
		"""
		a=2*ZoomFactor-1
		b=2*ZoomFactor
		row_vect=numpy.zeros([1,3],'f')
		col_vect=numpy.zeros([3,1],'f')
		for y in range(1,4):
			if y <=3:
				col_vect[y-1]=3-y+1	
			else:
				col_vect[y-1]=len(col_vect)-y+1
		for x in range(1,4):
			if x <=3:
				row_vect[0][x-1]=x
			else:
				row_vect[0][x-1]=3-x+1
		tmp=col_vect*row_vect
		bartlett=float(1/float(3*3))*tmp
		return bartlett
	      
    

  
    
  
  
  
  
  
  
  
  
  
  
if __name__ == "__main__":
	calibration()
