#BMP2VXP: Converts BMP files to VXP expansions
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
import bmp2vxp
from error import SaveError
from idgenerator import GenerateID
import ConfigParser
import vxpinstaller
class bmp2vxpGUI(ConverterBase):
	def __init__(self,screen):
		ConverterBase.__init__(self,screen)
		ui=self.ui
		#ui.add(sockgui.BorderBox(ui,[5,5],[x-10 for x in screen.get_size()]))
		
		#ui.add(sockgui.BorderBox(ui,[10,10],[screen.get_width()-20,94]))
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

		#ui.add(sockgui.BorderBox(ui,[10,109],[screen.get_width()-20,110]))
		ys=self.makeTab(ys+94+5,120,'BMP to convert')
		self.files=sockgui.ListBox(ui,[20,ys+10],[62,10],items=self.getImageList())
		if self.files.getNumItems()>0:
			self.files.select(0)
		ui.add(self.files)
		self.dither=sockgui.CheckBox(ui,[100,ys+103],'Dither image',self.getDither())
		ui.add(sockgui.Button(ui,[20,ys+99],'Refresh list',callback=self.refreshList))
		ui.add(self.dither)
			
		#ui.add(sockgui.BorderBox(ui,[10,224],[screen.get_width()-20,110]))
		ys=self.makeTab(ys+120+5,30,'3dmm IDs')
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		
		ys=self.makeTab(ys+30+5,66,'Control')
		self.install_check=sockgui.CheckBox(ui,[240,ys+13],'Install VXP',self.getInstallCheck())
		ui.add(self.install_check)
		self.progress=sockgui.ProgressBox(ui,[20,ys+10],[200,16],maxvalue=11)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+32],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+46],'Create VXP',callback=self.createVXP)
		ui.add(self.startbutton)
		
		ui.registerHotKey(K_F5,self.updateListBox)
	def refreshList(self,junk):
		self.files.setItems(self.getImageList())
	def updateListBox(self,event):
		if event.type==KEYUP:
			self.refreshList(0)
	def createVXP(self,junk):
		self.saveSettings()
		self.progress.setValue(0)
		try:
			outfile=self.shortnamebox.getText()+'.vxp'
			bmpname=self.files.getSelectedText()
			if bmpname is None:
				raise SaveError('no Image selected')
			uniqueid=int(self.idbox.getText())
			self.errortext.setText('Converting %s...' % (bmpname))
			self.ui.draw()
			ret=bmp2vxp.CreateVXPExpansionFromBMP(str(self.namebox.getText()),str(self.authorbox.getText()),str(self.origauthorbox.getText()),
				str(outfile),str(self.shortnamebox.getText()),str(bmpname),uniqueid,self.progressCallback,self.dither.isChecked())
			if ret:
				self.errortext.setText('VXP saved as %s' % (outfile))
				self.idbox.setText('') #So we don't reuse them by mistake.
				if self.install_check.isChecked():
					vxpinstaller.installVXP(outfile)
					self.errortext.setText('VXP saved as %s, and installed.' % (outfile))
			else:
				self.errortext.setText('Failed: unknown error (!ret)')
		except SaveError,e:
			self.errortext.setText('Failed: ' + str(e))
		except ValueError:
			self.errortext.setText('Failed: Bad ID!')
		except pygame.error,e:
			self.errortext.setText('Failed: ' + str(e))
	def copyAuthorToOrigAuthor(self,junk):
		self.origauthorbox.setText(self.authorbox.getText())
	def saveExtraSettings(self):
		try:
			self.config.add_section('bmp2vxp')
		except:
			pass
		self.config.set('bmp2vxp','dither',`self.dither.isChecked()`)
	def getDither(self):
		return self.getBoolConfig('bmp2vxp','dither')
	def getImageList(self):
		out=[]
		for file in os.listdir('.'):
			if file in ('font.png','palette.bmp'):
				continue
			try:
				ext=file[file.rindex('.'):].lower()
			except ValueError:
				ext=''
			if ext in ('.bmp','.png','.tga','.pcx','.jpg','.jpeg','.gif'):
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
	pygame.display.set_caption(title+'bmp2vxp '+bmp2vxp.version)
	screen=pygame.display.set_mode((375,394))
	gui=bmp2vxpGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('bmp2vxp','Create 3D words textures from BMP/JPG/PNG',None,bmp2vxp.version) # None is the ICONOS.
