#OBJ2VXP: Converts simple OBJ files to VXP expansions
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys
sys.path.append('code')
import pygame
from pygame.constants import *
import sockgui
sockgui.setDataPath('code')
from converterbase import ConverterBase
import os
import time
import obj2vxp
import obj2vxptex
from error import SaveError,LoadError
import ConfigParser
import vxpinstaller
class obj2vxpGUI(ConverterBase):
	def __init__(self,screen):
		ConverterBase.__init__(self,screen)
		ui=self.ui


		ys=self.makeTab(10,94,'CFG settings')
		ui.add(sockgui.Label(ui,[20,ys+10],'Expansion name:'))
		ui.add(sockgui.Label(ui,[20,ys+26],'Author name:'))
		ui.add(sockgui.Label(ui,[20,ys+42],'Orig. Author name:'))
		ui.add(sockgui.Label(ui,[20,ys+58],'Shortname:'))
		ui.add(sockgui.Label(ui,[20,ys+74],'Filename:'))
		
		
		self.filenamelabel=sockgui.Label(ui,[120,ys+74],'')
		ui.add(self.filenamelabel)
		
		self.namebox=       sockgui.TextBox(ui,[120,ys+10-3],40)
		self.authorbox=     sockgui.TextBox(ui,[120,ys+26-3],40)
		self.origauthorbox= sockgui.TextBox(ui,[120,ys+42-3],40)
		self.shortnamebox=  sockgui.TextBox(ui,[120,ys+58-3],40,callback=self.onShortNameChanged)
		self.shortnamebox.setAllowedKeys(sockgui.UPPERCASE+sockgui.LOWERCASE+sockgui.DIGITS+'._-')

		self.authorbox.setText(self.getAuthor())
		
		ui.add(self.namebox)
		ui.add(self.authorbox)
		ui.add(self.origauthorbox)
		ui.add(sockgui.Button(ui,[330,ys+42-3],'Same',callback=self.copyAuthorToOrigAuthor))
		ui.add(self.shortnamebox)
		self.namebox.activate()

		ys=self.makeTab(ys+94+5,120,'OBJ to convert')
		self.files=sockgui.ListBox(ui,[20,ys+10],[62,10],items=self.getOBJList())
		if self.files.getNumItems()>0:
			self.files.select(0)
		ui.add(self.files)
		self.enhance_color=sockgui.CheckBox(ui,[100,ys+103],'Enhance Color',self.getEnhanceColor())
		self.textured=sockgui.CheckBox(ui,[200,ys+103],'Textured',self.getTextured())
		ui.add(sockgui.Button(ui,[20,ys+99],'Refresh list',callback=self.refreshList))
		ui.add(self.enhance_color)
		ui.add(self.textured)
			
		#ui.add(sockgui.BorderBox(ui,[10,224],[screen.get_width()-20,110]))
		ys=self.makeTab(ys+120+5,30,'3dmm IDs')
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		self.idbox.setAllowedKeys('0123456789')	
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		
		ys=self.makeTab(ys+30+5,66,'Control')
		self.install_check=sockgui.CheckBox(ui,[240,ys+13],'Install VXP',self.getInstallCheck())
		ui.add(self.install_check)
		self.progress=sockgui.ProgressBox(ui,[20,ys+10],[200,16],maxvalue=6)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+32],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+46],'Create VXP',callback=self.createVXP)
		ui.add(self.startbutton)
		
		ui.registerHotKey(K_F5,self.updateListBox)
	def refreshList(self,junk):
		self.files.setItems(self.getOBJList())
	def updateListBox(self,event):
		if event.type==KEYUP:
			self.refreshList(0)
	def statusCallback(self,text):
		self.errortext.setText(text)
		self.ui.draw()
	def createVXP(self,junk):
		self.saveSettings()
		self.progress.setValue(0)
		try:
			outfile=str(self.shortnamebox.getText())+'.vxp'
			objfile=self.files.getSelectedText()
			if objfile is None:
				raise SaveError('no OBJ selected')
			try:
				uniqueid=int(self.idbox.getText())
			except ValueError:
				raise SaveError('Failed: Bad ID!')
			name=str(self.namebox.getText())
			author=str(self.authorbox.getText())
			origauthor=str(self.origauthorbox.getText())
			shortname=str(self.shortnamebox.getText())
			enhance=self.enhance_color.isChecked()
			self.errortext.setText('Converting...')
			if self.textured.isChecked():
				ret=obj2vxptex.CreateVXPExpansionFromOBJTextured(name,author,origauthor,outfile,shortname,objfile,
						uniqueid,self.progressCallback,self.statusCallback)
			else:
				ret=obj2vxp.CreateVXPExpansionFromOBJ(name,author,origauthor,outfile,shortname,objfile,
						uniqueid,self.progressCallback,enhance,self.statusCallback)
			if ret:
				self.errortext.setText('VXP saved as %s' % (outfile))
				self.idbox.setText('') #So we don't reuse them by mistake.
				if self.install_check.isChecked():
					vxpinstaller.installVXP(outfile)
					self.errortext.setText('VXP saved as %s, and installed.' % (outfile))
			else:
				self.errortext.setText('Failed: unknown error (!ret)')
		except SaveError,e:
			self.errortext.setText('Failed: ' + str(e).strip('"'))
		except LoadError,e:
			self.errortext.setText('Failed: ' + str(e).strip('"'))
		except ValueError:
			self.errortext.setText('Failed: Bad ID!')
		except pygame.error,e:
			self.errortext.setText('Failed: ' + str(e).strip('"'))
	def copyAuthorToOrigAuthor(self,junk):
		self.origauthorbox.setText(self.authorbox.getText())
	def saveExtraSettings(self):
		try:
			self.config.add_section('obj2vxp')
		except:
			pass
		self.config.set('obj2vxp','enhance',`self.enhance_color.isChecked()`)
		self.config.set('obj2vxp','textured',`self.textured.isChecked()`)
	def getEnhanceColor(self):
		try:
			val=self.config.get('obj2vxp','enhance')
			return sockgui.BoolConv(val)
		except:
			return False
	def getTextured(self):
		try:
			val=self.config.get('obj2vxp','textured')
			return sockgui.BoolConv(val)
		except:
			return False
	def getOBJList(self):
		out=[]
		for file in os.listdir('.'):
			flower=file.lower()
			if flower.endswith('.obj'):
				out.append(file)
		return out
	def onShortNameChanged(self,data,newtext):
		if newtext=='':
			out=''
		else:
			out=self.shortnamebox.getText() + '.vxp'
		self.filenamelabel.setRed(os.path.exists(out))
		self.filenamelabel.setText(out)
def RunConverter(title):
	pygame.display.set_caption(title+'obj2vxpGUI '+obj2vxp.version)
	screen=pygame.display.set_mode((375,397))
	gui=obj2vxpGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('obj2vxp','Convert OBJs to props',None,obj2vxp.version) # None is the ICONOS.
