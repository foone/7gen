#BMP2VXP: Converts BMP files to VXP expansions
#Copyright (C) 2004 Travis Wells / Philip D. Bober
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
import background2vxp
from error import SaveError
from idgenerator import GenerateID
import ConfigParser
import vxpinstaller
from filedialog import FileDialog,IMAGEFORMATS
class background2vxpGUI(ConverterBase):
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

		ys=self.makeTab(ys+94+5,90,'Images')
		ui.add(sockgui.Label(ui,[20,ys+10],'Background:'))
		ui.add(sockgui.Label(ui,[20,ys+26],'Depth Map:'))
		ui.add(sockgui.Label(ui,[20,ys+42],'Preview:'))
		self.backgroundbox=       sockgui.Label(ui,[80,ys+10-3],'<NONE>')
		ui.add(self.backgroundbox)
		ui.add(sockgui.Button(ui,[300,ys+10-3],'Load...',callback=self.browseForImage,data='background'))
		ui.add(sockgui.Button(ui,[345,ys+10-3],'Reset',callback=self.resetTextbox,data='background'))
		self.depthmapbox=       sockgui.Label(ui,[80,ys+26-3],'<NONE>')
		ui.add(self.depthmapbox)
		ui.add(sockgui.Button(ui,[300,ys+26-3],'Load...',callback=self.browseForImage,data='depthmap'))
		ui.add(sockgui.Button(ui,[345,ys+26-3],'Reset',callback=self.resetTextbox,data='depthmap'))
		self.previewbox=       sockgui.Label(ui,[80,ys+42-3],'<NONE>')
		ui.add(self.previewbox)
		ui.add(sockgui.Button(ui,[300,ys+42-3],'Load...',callback=self.browseForImage,data='preview'))
		ui.add(sockgui.Button(ui,[345,ys+42-3],'Reset',callback=self.resetTextbox,data='preview'))
		self.ditherbackground=sockgui.CheckBox(ui,[20,ys+60],'Dither background',self.getDitherBackground())
		ui.add(self.ditherbackground)
		self.ditherpreview=sockgui.CheckBox(ui,[20,ys+74],'Dither preview',self.getDitherPreview())
		ui.add(self.ditherpreview)
			
		ys=self.makeTab(ys+90+5,30,'3dmm IDs')
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		
		ys=self.makeTab(ys+30+5,66,'Control')
		self.install_check=sockgui.CheckBox(ui,[240,ys+46],'Install VXP',self.getInstallCheck())
		self.progress=sockgui.ProgressBox(ui,[20,ys+10],[330,16],maxvalue=15)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+32],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+46],'Create VXP',callback=self.createVXP)
		ui.add(self.startbutton)
		ui.add(self.install_check)

		self.lastdialogpath='.'
		self.background=None
		self.preview=None
		self.depthmap=None
	def browseForImage(self,type):
		dia=FileDialog(self.ui.screen,self.lastdialogpath,IMAGEFORMATS)
		dia.run()
		if dia.selected is not None:
			path=dia.selected
			if not os.path.isdir(path):
				self.setPath(type,path)
				#tbox.setText(path)
		self.lastdialogpath=dia.path
	def resetTextbox(self,type):
		if type=='background':
			self.background=None
			self.backgroundbox.setText('<NONE>')
		elif type=='depthmap':
			self.depthmap=None
			self.depthmapbox.setText('<NONE>')
		elif type=='preview':
			self.preview=None
			self.previewbox.setText('<NONE>')
		pass
	def setPath(self,type,path):
		ntxt=path
		if len(ntxt)>37:
			ntxt='...'+ntxt[-37-3:]
		if type=='background':
			self.background=path
			self.backgroundbox.setText(ntxt)
		elif type=='depthmap':
			self.depthmap=path
			self.depthmapbox.setText(ntxt)
		elif type=='preview':
			self.preview=path
			self.previewbox.setText(ntxt)

	def createVXP(self,junk):
		self.saveSettings()
		self.progress.setValue(0)
		try:
			outfile=str(self.shortnamebox.getText()+'.vxp')
			uniqueid=int(self.idbox.getText())
			name=str(self.namebox.getText())
			author=str(self.authorbox.getText())
			origauthor=str(self.origauthorbox.getText())
			shortname=str(self.shortnamebox.getText())
			dither=False
			background=self.background
			preview=self.preview
			depth=self.depthmap
			if background is None:
				raise SaveError('No background image!')
			if preview is None:
				raise SaveError('No preview image!')


			self.errortext.setText('Converting %s...' % (os.path.basename(background)))
			self.ui.draw()


			if self.ditherbackground.isChecked():
				background='+'+background
			if self.ditherpreview.isChecked():
				preview='+'+preview
			print background,preview	
			ret=background2vxp.CreateBackgroundFromImages(name,author,outfile,shortname,
					background,depth,preview,dither,uniqueid,self.progressCallback)
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
			self.config.add_section('background2vxp')
		except:
			pass
		self.config.set('background2vxp','ditherbackground',`self.ditherbackground.isChecked()`)
		self.config.set('background2vxp','ditherpreview',`self.ditherpreview.isChecked()`)
	def getDitherBackground(self):
		return self.getBoolConfig('background2vxp','ditherbackground')
	def getDitherPreview(self):
		return self.getBoolConfig('background2vxp','ditherpreview')
	def onShortNameChanged(self,data,newtext):
		if newtext=='':
			out=''
		else:
			out=self.shortnamebox.getText() + '.vxp'
		self.filenamelabel.setRed(os.path.exists(out))
		self.filenamelabel.setText(out)

def RunConverter(title):
	pygame.display.set_caption(title+'background2vxp '+background2vxp.version)
	screen=pygame.display.set_mode((395,364))
	gui=background2vxpGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('background2vxp','Create backgrounds from BMP/JPG/PNG',None,background2vxp.version) # None is the ICONOS.
