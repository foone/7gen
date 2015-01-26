#!/usr/env python
#actorextractor: Extracts 3dmm model-trees from the 3dmm datafiles
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
import actorextractor
from error import SaveError
from idgenerator import GenerateID
import ConfigParser
import extract_presets
from ms3dmmfinder import Get3dmmInstallDirectory
try:
	import decompress3dmm 
	have_decompress=True
except:
	have_decompress=False
class actorextractorGUI(ConverterBase):
	def __init__(self,screen):
		ConverterBase.__init__(self,screen)
		ui=self.ui
		ys=self.makeTab(10,92,'CFG settings')
		ui.add(sockgui.Label(ui,[20,ys+10],'Expansion name:'))
		ui.add(sockgui.Label(ui,[20,ys+26],'Author name:'))
		ui.add(sockgui.Label(ui,[20,ys+42],'3dmm path:'))
		ui.add(sockgui.Label(ui,[20,ys+58],'Shortname:'))
		ui.add(sockgui.Label(ui,[20,ys+74],'Directory/vxp:'))

		self.filenamelabel=sockgui.Label(ui,[100,ys+74],'')
		ui.add(self.filenamelabel)

		self.namebox=      sockgui.TextBox(ui,[100,ys+10-3],70)
		self.authorbox=    sockgui.TextBox(ui,[100,ys+26-3],70)
		self.pathbox=      sockgui.TextBox(ui,[100,ys+42-3],70)
		self.shortnamebox= sockgui.TextBox(ui,[100,ys+58-3],70,callback=self.onShortNameChanged)
		self.shortnamebox.setAllowedKeys(sockgui.UPPERCASE+sockgui.LOWERCASE+sockgui.DIGITS+'._-')
		self.authorbox.setText(self.getAuthor())
		mspath=Get3dmmInstallDirectory()
		if not mspath:
			mspath=''
		self.pathbox.setText(mspath)		
		ui.add(self.namebox)
		ui.add(self.authorbox)
		ui.add(self.pathbox)
		ui.add(self.shortnamebox)

		ys=self.makeTab(ys+92+5,124,'Actor/Prop to extract')
		self.files=sockgui.ListBox(ui,[20,ys+10],[62,10],items=self.getActorList())
		if self.files.getNumItems()>0:
			self.files.select(0)
		ui.add(self.files)
		self.files.activate()
		self.tilesheet=sockgui.CheckBox(ui,[20,ys+100],'Make tilesheet',self.getTileCheck())
		ui.add(self.tilesheet)
		self.recompress=sockgui.CheckBox(ui,[20,ys+112],'Recompress sections',self.getRecompressCheck())
		ui.add(self.recompress)

		ys=self.makeTab(ys+124+5,30,'3dmm IDs')
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		
		ys=self.makeTab(ys+30+5,66,'Control')
		self.progress=sockgui.ProgressBox(ui,[20,ys+10],[335,16],maxvalue=10)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+32],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+46],'Extract Actor/Prop',callback=self.createVXP)
		ui.add(self.startbutton)
		
	def statusCallback(self,text):
		self.errortext.setText(text)
		self.ui.draw()
	def createVXP(self,junk):
		self.saveSettings()
		self.progress.setValue(0)
		try:
			actorname=self.files.getSelectedText()
			if actorname is None:
				raise SaveError('No Actor/Prop selected')
			uniqueid=int(self.idbox.getText())
			preset=self.getPresetFromSillyName(actorname)
			if preset is None:
				raise SaveError('No Actor/Prop selected')
			author=str(self.authorbox.getText())
			if author=='':
				raise SaveError('No Author entered')
			data_dir=str(self.pathbox.getText())
			shortname=str(self.shortnamebox.getText())
			tilesheet=self.tilesheet.isChecked()
			recompress=self.recompress.isChecked()
			name=str(self.namebox.getText())
			haveprop=os.path.exists(os.path.join(data_dir,'prop.3TH'))
			haveactor=os.path.exists(os.path.join(data_dir,'actor.3TH'))
			havetmpls=os.path.exists(os.path.join(data_dir,'tmpls.3CN'))
			exepath=os.path.join(data_dir,'3dmovie.exe')
			haveexe=os.path.exists(exepath)
			if (not haveprop) or (not haveactor):
				raise SaveError('Bad path, prop.3th/actor.3th not found')
			if not havetmpls:
				raise SaveError('TMPLS.3CN not found. Is 3dmm No-CD\'d?')
			decomp=None
			if tilesheet or recompress:
				if not have_decompress:
					raise SaveError('Decompressor not found. Check decompress3dmm.pyd')
				if not haveexe:
					raise SaveError('3dmovie.exe not found! Check path.')
				decomp=decompress3dmm.Decompressor(exepath)

			ret=actorextractor.ExtractActorFromDatafiles(data_dir,author,preset['thid'],shortname,shortname,name,preset['actor'],uniqueid,tilesheet,recompress,decomp,self.progressCallback,self.statusCallback)
			if ret:
				self.errortext.setText('Extracted to %s' % (shortname))
				self.idbox.setText('') #So we don't reuse them by mistake.
			else:
				self.errortext.setText('Failed: unknown error (!ret)')
		except SaveError,e:
			self.errortext.setText('Failed: ' + str(e))
		except ValueError:
			self.errortext.setText('Failed: Bad ID!')
		except pygame.error,e:
			self.errortext.setText('Failed: ' + str(e))
	def getActorList(self):
		out=[]
		for shortname in extract_presets.presets:
			name=extract_presets.presets[shortname]['name']
			if extract_presets.presets[shortname]['actor']:
				name='Actor'+name[4:]
			else:
				name='Prop'+name[4:]
			out.append(name)
		out.sort()
		return out
	def getPresetFromSillyName(self,silly):
		for shortname in extract_presets.presets:
			name=extract_presets.presets[shortname]['name']
			if extract_presets.presets[shortname]['actor']:
				name='Actor'+name[4:]
			else:
				name='Prop'+name[4:]
			if name==silly:
				return extract_presets.presets[shortname]
	def onShortNameChanged(self,data,newtext):
		if newtext=='':
			out=''
		else:
			out=self.shortnamebox.getText()
		self.filenamelabel.setRed(os.path.exists(out))
		self.filenamelabel.setText(out)
	def getTileCheck(self):
		return self.getBoolConfig('actorextractor','tilesheet',True)
	def getRecompressCheck(self):
		return self.getBoolConfig('actorextractor','tilesheet',True)
	def saveExtraSettings(self):
		try:
			self.config.add_section('actorextractor')
		except:
			pass
		self.config.set('actorextractor','tilesheet',`self.tilesheet.isChecked()`)
		self.config.set('actorextractor','recompress',`self.recompress.isChecked()`)

def RunConverter(title):
	pygame.display.set_caption(title+'ActorExtractor '+actorextractor.version)
	screen=pygame.display.set_mode((470,400))
	gui=actorextractorGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('actorextractor','Extract 3dmm actors/props for modifying',None,actorextractor.version) # None is the ICONOS.
