#!/usr/env python
#7gen: Simple chooser proggie for all the converter scripts.
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys
sys.path.append('code')
sys.path.append('bin')
import pygame
from pygame.constants import *
import sockgui
sockgui.setDataPath('code')
from converterbase import ConverterBase
import ConfigParser

version='0.7'

modules=[]
try:
	import actorextractorGUI 
	mod=actorextractorGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
try:
	import background2vxpGUI 
	mod=background2vxpGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
try:
	import bmp2vxpGUI 
	mod=bmp2vxpGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
try:
	import campan2vxpGUI
	mod=campan2vxpGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
try:
	import jkl2vxpGUI 
	mod=jkl2vxpGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
try:
	import md2_to_vxpGUI 
	mod=md2_to_vxpGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
try:
	import obj2vxpGUI 
	mod=obj2vxpGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
try:
	import rgb2vxpGUI 
	mod=rgb2vxpGUI
	mod.GetInfo()
	modules.append(mod)
except (ImportError,AttributeError):
	pass
class SevenGen(ConverterBase):
	def __init__(self,screen):
		ConverterBase.__init__(self,screen)
		ui=self.ui
		sillyv=self.getSilly()
		ys=-30 # HACKERY!
		y=10
		self.sillybox=sockgui.CheckBox(ui,[10,430],'Use silly borders',self.getSilly(),self.toggleSilly)
		ui.add(self.sillybox)
		for module in modules:
			name,desc,icon,version=module.GetInfo()
			h=30
			tab=sockgui.SimpleTab(ui,ys+h+10,h,name+' '+version,silly=sillyv,callback=self.runConverter,data=name)
			ys=tab.getYS()
			ui.add(tab)
			ui.add(sockgui.Label(ui,[20,ys+10],desc));
			textw,texth=ui.font.getTextLength(name)
			ui.add(sockgui.Button(ui,[screensize[0]-23-textw,ys+10],name,callback=self.runConverter,data=name))
	def toggleSilly(self,data):
		self.ui.setSilly(self.sillybox.isChecked())
		config=ConfigParser.SafeConfigParser()
		config.read('vxp.ini')
		try:
			self.config.add_section('main')
		except:
			pass
		try:
			self.config.set('main','silly',str(self.sillybox.isChecked()))
		except AttributeError:
			pass
		fp=open('vxp.ini','w')
		self.config.write(fp)
		fp.close()

	def runConverter(self,data):
		if not self.ui.is_running:
			return
#		raise OSError
		global should_continue
		for module in modules:
			name,desc,icon,version=module.GetInfo()
			if name==data:
				diereason=module.RunConverter('7gen: ')
				print 'DIED!'
				if diereason!=QUIT:
					should_continue=True
				self.ui.shutdown()
	def run(self): # Override so that saveSettings isn't called (as it would overwrite the just-written values)
		ui=self.ui
		while ui.is_running:
			ui.draw()
			for ev in pygame.event.get():
				ui.event(ev)
			pygame.time.wait(10)
		return ui.die_reason
def run(args):
	global screensize,should_continue
	should_continue=True
	pygame.init()
	screensize=(375,444)
	while should_continue:
		should_continue=False
		pygame.display.set_caption('7gen '+version)
		screen=pygame.display.set_mode(screensize)
		gui=SevenGen(screen)
		if len(args)>0:
			for arg in args:
				gui.runConverter(arg)
			args=[] # only run the command line'd options once.
		gui.run()
if __name__=='__main__':
	run()


