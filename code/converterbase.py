#!/usr/env python
import ConfigParser
import sockgui
import pygame
from pygame.constants import *
from idgenerator import GenerateID
class ConverterBase:
	def __init__(self,screen):
		self.config=ConfigParser.SafeConfigParser()
		self.config.read('vxp.ini')
		self.ui=sockgui.UI(screen)
	def run(self):
		ui=self.ui
		while ui.is_running:
			ui.draw()
			for ev in pygame.event.get():
				ui.event(ev)
			pygame.time.wait(10)
		self.saveSettings()
		return ui.die_reason
	def saveSettings(self):
		try:
			self.config.add_section('main')
		except:
			pass
		try:
			self.config.set('main','author',self.authorbox.getText())
		except AttributeError:
			pass
		try:
			self.config.set('main','install',`self.install_check.isChecked()`)
		except AttributeError:
			pass
		self.saveExtraSettings()
		fp=open('vxp.ini','w')
		self.config.write(fp)
		fp.close()
	def saveExtraSettings(self):
		pass
	def getSilly(self):
		return self.getBoolConfig('main','silly',True)
	def getAuthor(self):
		try:
			return self.config.get('main','author')
		except:
			return ''
	def getInstallCheck(self):
		return self.getBoolConfig('main','install')
	def getBoolConfig(self,section,name,default=True):
		try:
			return sockgui.BoolConv(self.config.get(section,name))
		except:
			return default
	def progressCallback(self):
		self.progress.incValue(1)
		self.ui.draw()
	def makeTab(self,ystart,height,text,startx=10,width=None):
		tab=sockgui.SimpleTab(self.ui,ystart,height,text,startx,width,silly=self.getSilly())
		self.ui.add(tab)
		return tab.getYS()
	def getNewID(self,junk):
		import urllib
		try:
			id=int(urllib.urlopen('http://v.3dmm2.com/scripts/makeid.php?simple=1').read())
			self.idbox.setText(str(id))
		except:
			pass
	def generateNewID(self,junk):
		self.idbox.setText(str(GenerateID()))

