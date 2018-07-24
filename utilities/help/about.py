#################
# About SiM App.#
#################

import os
from Tkinter import *
from PIL import Image, ImageTk
import tkMessageBox
import stm7 as stm

iconpath = os.path.join('apps', 'icons')
qtlogo = os.path.join(iconpath, 'qtlogo.jpg')
iuaclogo = os.path.join(iconpath, 'iuaclogo.jpg')
iitklogo = os.path.join(iconpath, 'iitklogo.jpg')

infofont = ("Helvetica", 14, 'bold')

ack = [ 'Quazar Technologies \nwww.quazartech.com \nstmsupport@quazartech.com', \
	'IUAC (Delhi)', \
	#'Inter University Accelerator Center', \
	'IIT (Kanpur)'
	#'Indian Institute of Technology, Kanpur'\
	]

strCreditsQT = 	 'Joshua Mathew\nAnurag\nHarish Bansal' 
strCreditsIUAC = 'Dr. Kundan Singh\nDr. Ajith B.P.' 
strCreditsIITK = 'Prof. Deshdeep Sahdev\nDr. Anjan K. Gupta'

def about(master, oMenubar=None):
    oAbout = About(master, oMenubar)
    return

class About:
	def __init__(self, master, oMenuBar):
	    self.oMenuBar = oMenuBar
	    self.aGroup = master
	    self._createAwindow()
	    return

	def _createAwindow(self):
		self.__createImages()
		self._createAwidgets()
		return

	def __createImages(self):
		global qtlogoim, iitklogoim, iuaclogoim
		qtlogoim = ImageTk.PhotoImage (file = qtlogo)
		iuaclogoim = ImageTk.PhotoImage (file = iuaclogo)
		iitklogoim = ImageTk.PhotoImage (file = iitklogo)
		return

	def _createAwidgets(self):
		"""
		Creates Canvas widgets for displaying scan images
		"""
		self.aGroup.title('About SiM')
		
		self.LFDevProd = LabelFrame(self.aGroup, \
					text='Developed and Produced by', \
					)
		self.LFDevProd.grid(row=1, column=0, sticky=N+E+W+S)
		self.BtnAbout = Button(self.LFDevProd, \
					relief=FLAT, \
					compound=TOP, \
					text=ack[0], \
					fg = 'blue', \
					command=self.vCreditsQT, \
					justify=CENTER, \
					image = qtlogoim)
		self.BtnAbout.grid(row=0, column=0, sticky=N+E+W+S)
		self.LFContributors = LabelFrame(self.aGroup, \
					text='Contributors', \
					)
		self.LFContributors.grid(row=2, column=0, sticky=N+E+W+S)
		self.BtnAboutIUAC = Button(self.LFContributors, \
					relief=FLAT, \
					compound=TOP, \
					text=ack[1], \
					command=self.vCreditsIUAC, \
					image = iuaclogoim)
		self.BtnAboutIUAC.grid(row=0, column=0, sticky=N+E+W+S)

		self.BtnAboutIITK = Button(self.LFContributors, \
					relief=FLAT, \
					compound=TOP, \
					text=ack[2], \
					command=self.vCreditsIITK, \
					image = iitklogoim)
		self.BtnAboutIITK.grid(row=0, column=1, sticky=N+E+W+S)

		self.LFDevVersion = LabelFrame(self.aGroup, \
                                        text='', \
                                        )
                self.LFDevVersion.grid(row=0, column=0, sticky=N+E+W+S)

                Label(self.LFDevVersion, text= '     ' + stm.__INSTRUMENT__, font = infofont, fg = 'blue')\
                        .grid (row=0, column=0, sticky='ew')
                Label(self.LFDevVersion, text=stm.__SOFTWARE__, fg = 'blue')\
                        .grid (row=1, column=0, sticky='ew')

		self.BtnClose = Button(self.aGroup, \
				command=self.vCloseAppAboutCB, \
				fg='red', \
				text='Close')
		self.BtnClose.grid(row=3, column=0, sticky=N+E+W+S)
		self.aGroup.protocol('WM_DELETE_WINDOW',self.vCloseAppAboutCB)

	def vCreditsQT(self):
		tkMessageBox.showinfo('Authors @ QT', \
				message=strCreditsQT \
				)
		return

	def vCreditsIUAC(self):
		tkMessageBox.showinfo('Special Thanks to.. ', \
				message=strCreditsIUAC \
				)
		return

	def vCreditsIITK(self):
		tkMessageBox.showinfo('Special Thanks to ..', \
				message=strCreditsIITK \
				)
		return

	def vCloseAppAboutCB(self):
	    if self.oMenuBar:
		self.oMenuBar.About_Instance = 0
	    self.aGroup.destroy()

