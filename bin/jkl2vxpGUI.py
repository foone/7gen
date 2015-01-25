#JKL2VXP: Converts Dark Forces 2: Jedi Knight JKL levels to VXP expansions
#Copyright (C) 2004-2005 Travis Wells / Philip D. Bober
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
import jkl2vxp
from error import SaveError,LoadError
import ConfigParser
import vxpinstaller
class jkl2vxpGUI(ConverterBase):
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

		ys=self.makeTab(ys+94+5,46,'Directories')
		ui.add(sockgui.Label(ui,[20,ys+10],'Jedi Knight:'))
		ui.add(sockgui.Label(ui,[20,ys+26],'MOTS:'))
		self.jkdirbox=       sockgui.TextBox(ui,[84,ys+10-3],54)
		self.motsdirbox=     sockgui.TextBox(ui,[84,ys+26-3],54)
		self.jkdirbox.setText(self.getJKDirectory())
		self.motsdirbox.setText(self.getMOTSDirectory())
		ui.add(self.jkdirbox)
		ui.add(self.motsdirbox)

		ys=self.makeTab(ys+46+5,140,'Level to convert')
		self.files=sockgui.ListBox(ui,[20,ys+10],[62,10],items=self.getLevelList())
		if self.files.getNumItems()>0:
			self.files.select(0)
		ui.add(self.files)
		self.dither=sockgui.CheckBox(ui,[100,ys+103],'Dither textures',self.getDither())
		self.cache=sockgui.CheckBox(ui,[200,ys+103],'Cache Textures',self.getCache())
		ui.add(sockgui.Button(ui,[20,ys+99],'Refresh list',callback=self.refreshList))
		ui.add(self.dither)
		ui.add(self.cache)
		ui.add(sockgui.Label(ui,[20,ys+120],'Subdivide Threshold:'))
		self.subdivbox=sockgui.TextBox(ui,[130,ys+117],10)
		self.subdivbox.setAllowedKeys('.,0123456789')	
		self.subdivbox.setText(self.getThreshold())
		ui.add(self.subdivbox)
			
		ys=self.makeTab(ys+140+5,30,'3dmm IDs')
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		self.idbox.setAllowedKeys('0123456789')	
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		ui.add(sockgui.Button(ui,[180,ys+7],'Get ID from 3dmm2.com',callback=self.getNewID))
		
		ys=self.makeTab(ys+30+5,66,'Control')
		self.install_check=sockgui.CheckBox(ui,[240,ys+13],'Install VXP',self.getInstallCheck())
		ui.add(self.install_check)
		self.progress=sockgui.ProgressBox(ui,[20,ys+10],[200,16],maxvalue=12)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+32],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+46],'Create VXP',callback=self.createVXP)
		ui.add(self.startbutton)
		
		ui.registerHotKey(K_F5,self.updateListBox)
	def refreshList(self,junk):
		self.files.setItems(self.getLevelList())
	def updateListBox(self,event):
		if event.type==KEYUP:
			self.refreshList(0)
	def statusCallback(self,text):
		self.errortext.setText(text)
		self.ui.draw()
	def textureCountCallback(self,numbah):
		self.progress.setValue(0)
		self.progress.setMax(10+2*numbah)
	def createVXP(self,junk):
		self.saveSettings()
		self.progress.setValue(0)
		try:
			outfile=str(self.shortnamebox.getText())+'.vxp'
			jklname=self.files.getSelectedText()
			if jklname is None:
				raise SaveError('no Level selected')
			uniqueid=int(self.idbox.getText())
			name=str(self.namebox.getText())
			author=str(self.authorbox.getText())
			origauthor=str(self.origauthorbox.getText())
			shortname=str(self.shortnamebox.getText())
			gobdirs={}
			jkpath=str(self.jkdirbox.getText())
			motspath=str(self.motsdirbox.getText())
			gobdirs['jk']=[os.path.join(jkpath,'Resource'),jkpath]
			gobdirs['mots']=[os.path.join(motspath,'Resource'),motspath]
			gobdirs['all']=['']
			if self.dither.isChecked():
				imagemode=2
			else:
				imagemode=0
			cache=self.cache.isChecked()
			try:
				threshold=float(self.subdivbox.getValue().replace(',','.'))
			except ValueError:
				threshold=None

			self.statusCallback('Converting...')
			ret=jkl2vxp.CreateVXPExpansionFromJediKnightMap(name,author,origauthor,outfile,shortname,jklname,
					uniqueid,'auto',gobdirs,imagemode,cache,threshold,self.progressCallback,self.statusCallback,self.textureCountCallback)
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
			self.config.add_section('jkl2vxp')
		except:
			pass
		self.config.set('jkl2vxp','dither',`self.dither.isChecked()`)
		self.config.set('jkl2vxp','cache',`self.cache.isChecked()`)
		self.config.set('jkl2vxp','jkdir',self.jkdirbox.getText())
		self.config.set('jkl2vxp','motsdir',self.motsdirbox.getText())
		self.config.set('jkl2vxp','threshold',self.subdivbox.getText())
	def getJKDirectory(self):
		try:
			return self.config.get('jkl2vxp','jkdir')
		except:
			return r'C:\Program Files\LucasArts\Jedi Knight'
	def getMOTSDirectory(self):
		try:
			return self.config.get('jkl2vxp','motsdir')
		except:
			return r'C:\Program Files\LucasArts\Mots'
	def getThreshold(self):
		try:
			return self.config.get('jkl2vxp','threshold')
		except:
			return '0.5'
	def getDither(self):
		try:
			val=self.config.get('jkl2vxp','dither')
			return sockgui.BoolConv(val)
		except:
			return False
	def getCache(self):
		try:
			val=self.config.get('jkl2vxp','cache')
			return sockgui.BoolConv(val)
		except:
			return True
	def getLevelList(self):
		out=[]
		for file in os.listdir('.'):
			flower=file.lower()
			if flower.endswith('.jkl'):
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
	pygame.display.set_caption(title+'jkl2vxp '+jkl2vxp.version)
	screen=pygame.display.set_mode((375,480))
	gui=jkl2vxpGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('jkl2vxp','Convert Jedi Knight levels to props',None,jkl2vxp.version) # None is the ICONOS.
