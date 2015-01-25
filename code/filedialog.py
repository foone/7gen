#!/usr/env python
import sockgui
import os
import pygame
from fnmatch import fnmatch
IMAGEFORMATS=['*.bmp','*.pnm','*.xbm','*.lbm','*.pcx','*.gif','*.jpg','*.jpeg','*.png','*.tga']
def filecmp(a,b):
	if a=='[Parent Directory (..)]':
		return -1
	elif b=='[Parent Directory (..)]':
		return 1
	return cmp(a.lower(),b.lower())
class FileDialog:
	def __init__(self,screen,path,globs=['*.*']):
		scrw,scrh=screen.get_size()
		self.screen=screen
		self.path=os.path.abspath(path)
		self.globs=globs
		self.ui=ui=sockgui.UI(screen)
		fw=(scrw-20-16)/5
		fh=(scrh-55)/8
		self.files=sockgui.ListBox(ui,[10,25],[fw,fh],items=self.getFileList())
		self.files.setDoubleClickCallback(self.doubleClicked)
		self.gobutton=gobutton=sockgui.Button(ui,[320,8],'Go',callback=self.goButton)

		# Move the gobutton to the right
		w,h=gobutton.getSize()
		newx=scrw-w-9
		newy=gobutton.getPos()[1]
		self.gobutton.move((newx,newy))
		
		txtw=(newx-17)//5
		self.pathtxt=sockgui.TextBox(ui,[10,8],txtw) # sockgui.Label(ui,[10,8],self.path)
		self.pathtxt.setText(self.path)

		self.okbutton=okbutton=sockgui.Button(ui,[newx,8],' OK ',callback=self.OKButton)
		w,h=self.okbutton.getSize()
		newx=scrw-w-9
		newy=scrh-h-8
		self.okbutton.move((newx,newy))
		self.cancelbutton=cancelbutton=sockgui.Button(ui,[8,newy],'Cancel',callback=self.CancelButton)
		ui.add(self.pathtxt)
		ui.add(gobutton)
		ui.add(self.files)
		ui.add(self.okbutton)
		ui.add(self.cancelbutton)
		self.pathtxt.activate()
		self.selected=None
	def goButton(self,data):
		self.newPath(self.pathtxt.getText())
	def OKButton(self,data):
		self.doubleClicked(self.files,self.files.selected)
	def CancelButton(self,data):
		self.ui.shutdown()
	def newPath(self,newpath):
		if os.path.isdir(newpath):
			self.path=os.path.abspath(newpath)
			self.refreshFiles()
			self.files.unselect()
			self.pathtxt.setText(self.path)
			self.files.setScroll(0)
	def refreshFiles(self):
		self.files.setItems(self.getFileList())
	def getFileList(self):
		filelist=['[Parent Directory (..)]']
		for file in os.listdir(self.path):
			matched=False
			if os.path.isdir(os.path.join(self.path,file)):
				filelist.append('[%s]' % (file))
			else:
				for pattern in self.globs:
					if fnmatch(file,pattern):
						matched=True
				if matched:
					filelist.append(file)
		filelist.sort(filecmp)
		return filelist
	def doubleClicked(self,listbox,index):
		txt=listbox.getSelectedText()
		if txt is None: return True
		if txt[0]=='[':
			dirname=txt[1:-1]
			if dirname=='Parent Directory (..)':
				newpath=os.path.join(self.path,'..')
			else:
				newpath=os.path.join(self.path,dirname)
			self.newPath(newpath)
			return False
		else:
			self.selected=os.path.join(self.path,txt)
			self.ui.shutdown()
		return True
	def run(self):
		ui=self.ui
		while ui.is_running:
			for ev in pygame.event.get():
				ui.event(ev)
			ui.draw()
			pygame.time.wait(10)

