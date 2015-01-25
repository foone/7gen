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
import time
import md2_to_vxp
from error import SaveError
import ConfigParser
import vxpinstaller
from filedialog import FileDialog,IMAGEFORMATS
from GetFrameNames import GetAnimations
from md2info import GetAuthor
from fnmatch import fnmatch
class md22vxpGUI(ConverterBase):
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

		ys=self.makeTab(ys+94+5,185,'MD2 settings')
		ys2=self.makeTab(ys+27+5,115,'Animations',10,screen.get_width()-193)
		self.animbox=sockgui.CheckedListBox(ui,[15,ys2+5],[30,10],items=[])
		ui.add(sockgui.Button(ui,[330,ys+10],'Load',callback=self.browseMD2))
		self.actor=sockgui.CheckBox(ui,[15,ys2+103],'Make Actor',self.getActor())
		self.md2filenamelabel=sockgui.Label(ui,[20,ys+10],'Model: <NOTLOADED>')
		ui.add(self.md2filenamelabel)
		ys3=self.makeTab(ys+27+5,120,'Textures (Check to dither)',197,screen.get_width()-207)
		self.texturebox=sockgui.CheckedListBox(ui,[203,ys3+5],[27,10],items=[])
		ui.add(self.animbox)
		ui.add(self.texturebox)
		ui.add(sockgui.Button(ui,[205,ys3+self.texturebox.getSize()[1]+10],'Add...',callback=self.addTexture))
		ui.add(sockgui.Button(ui,[205+50,ys3+self.texturebox.getSize()[1]+10],'Add black',callback=self.addBlackTexture))
		ui.add(sockgui.Button(ui,[205+50+69,ys3+self.texturebox.getSize()[1]+10],'Delete',callback=self.removeTexture))
		ui.add(sockgui.Label(ui,[15,ys2+121+3],'Scale:'))
		self.scaletext=sockgui.TextBox(ui,[50,ys2+121],10,self.getScaling())
		self.actor=sockgui.CheckBox(ui,[120,ys2+121+3],'Make Actor',self.getActor())
		self.scaletext.setAllowedKeys('0123456789.,')	

		ys=self.makeTab(ys+185+5,30,'3dmm IDs',10,screen.get_width()-193)
		ui.add(sockgui.Button(ui,[85,ys2+95],'Toggle single frame',callback=self.toggleSingle))
		ui.add(sockgui.Button(ui,[15,ys2+95],'Up',callback=self.moveUp))
		ui.add(sockgui.Button(ui,[35,ys2+95],'Down',callback=self.moveDown))
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		ui.add(self.scaletext)
		ui.add(self.actor)
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		self.idbox.setAllowedKeys('0123456789')	
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		
		ys=self.makeTab(135+185+5,88,'Preview',200,164)
		self.previewbox=sockgui.ImageBox(ui,[209,ys+9],[72,72])
		ui.add(self.previewbox)
		ui.add(sockgui.Button(ui,[285,ys+65],'Load image...',callback=self.loadPreview))
#		ys=self.makeTab(338+30+5,44,'Control')
		ys=self.makeTab(420,44,'Control')
		self.install_check=sockgui.CheckBox(ui,[290,ys+26],'Install VXP',self.getInstallCheck())
		ui.add(self.install_check)
		self.progress=sockgui.ProgressBox(ui,[80,ys+22],[200,16],maxvalue=12)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+8],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+22],'Create VXP',callback=self.createVXP)
		ui.add(self.startbutton)
		
#		ui.registerHotKey(K_F5,self.updateListBox)
		self.lastdialogpath='.'
		self.previewimg=None
		self.previewpath=None
		self.md2path=None
		self.prog=0
	def moveUp(self,junk):
		if self.md2path is None:
			return
		index=self.animbox.selected
		if index is None or index==0:
			return
		self.swapAnimations(index,index-1)
		self.animbox.select(self.animbox.selected,-1)
	def moveDown(self,junk):
		if self.md2path is None:
			return
		index=self.animbox.selected
		if index is None or index==len(self.animations)-1:
			return
		self.swapAnimations(index,index+1)
		self.animbox.select(self.animbox.selected,+1)
	def swapAnimations(self,a,b):
		tempanim=self.animations[a]
		tempsingle=self.singlelist[a]
		self.animations[a]=self.animations[b]
		self.singlelist[a]=self.singlelist[b]
		self.animations[b]=tempanim
		self.singlelist[b]=tempsingle
		ac=self.animbox.isChecked(a)
		bc=self.animbox.isChecked(b)
		self.animbox.setItemText(a,self.getStringForAnimationIndex(a))
		self.animbox.setItemText(b,self.getStringForAnimationIndex(b))
		self.animbox.setChecked(a,bc)
		self.animbox.setChecked(b,ac)
	def getStringForAnimationIndex(self,index):
		animation,frames=self.animations[index]
		framecount=len(frames)
		if self.singlelist[index]:
			return '%s (Single frame)' % (animation)
		if framecount==1:
			return '%s (1 frame)' % (animation)
		else:
			return '%s (%i frames)' % (animation,framecount)
	def toggleSingle(self,junk):
		if self.md2path is None:
			return
		index=self.animbox.selected
		if index is None:
			return
		animation,frames=self.animations[index]
		framecount=len(frames)
		if framecount==1:
			return
		else:
			self.singlelist[index]=not self.singlelist[index]
			self.animbox.setItemText(index,self.getStringForAnimationIndex(index))
	def addBlackTexture(self,junk):
		if self.md2path is None:
			return
		if not 'code\\black.png' in self.textures:
			self.textures.append('code\\black.png')
			self.texturebox.addItem('black.png',False)
#			self.texturebox.items.append(('black.png',True))
	def addTexture(self,junk):
		if self.md2path is None:
			return
		dia=FileDialog(self.ui.screen,self.lastdialogpath,IMAGEFORMATS)
		dia.run()
		if dia.selected is not None:
			path=dia.selected
			if not os.path.isdir(path):
				self.textures.append(path)
				self.texturebox.items.append((os.path.basename(path),True))
		self.lastdialogpath=dia.path
	def loadPreview(self,junk):
		dia=FileDialog(self.ui.screen,self.lastdialogpath,IMAGEFORMATS)
		dia.run()
		if dia.selected is not None:
			path=dia.selected
			if not os.path.isdir(path):
				try:
					surf=pygame.image.load(path)
					if surf.get_size()!=(72,72):
						surf=pygame.transform.scale(surf,(72,72))
					self.previewimg=surf
					self.previewbox.setImage(surf)
					self.previewpath=path
				except Exception,e:
					self.errortext.setText('Couldn\'t load '+surf)
				pass
				#self.textures.append(path)
				#self.texturebox.items.append((os.path.basename(path),True))
		self.lastdialogpath=dia.path
	def removeTexture(self,junk):
		index=self.texturebox.getSelectedIndex()
		if index is None:
			return
		else:
			self.textures=self.textures[:index]+self.textures[index+1:]
			self.texturebox.items=self.texturebox.items[:index]+self.texturebox.items[index+1:]
			self.texturebox.unselect()
		pass
	def loadMD2(self,path):
		if os.path.exists(path):
			ntxt=path
			if len(ntxt)>50:
				ntxt='...'+ntxt[-47:]
			self.md2filenamelabel.setText('Model: '+ntxt)
			self.frames,self.animations=GetAnimations(path)
			self.md2path=path
			self.singlelist=[]
			nlist=[]
			for i,(animation,frames) in enumerate(self.animations):
				self.singlelist.append(False)
				nlist.append(self.getStringForAnimationIndex(i))
			
			self.animbox.setItems(nlist)	
			self.scanTextures(path)
	def scanTextures(self,filename):
		path=os.path.dirname(filename)
		goodtex=[]
		prettytex=[]
		for file in os.listdir(path):
			matched=False
			for pattern in IMAGEFORMATS:
				if fnmatch(file,pattern):
					basename,ext=os.path.splitext(file)
					if (not basename.lower().endswith('_i')) and basename.lower()!='weapon':
						matched=True
			if matched:
				goodtex.append(os.path.join(path,file))
				prettytex.append(file)
		self.textures=goodtex
		self.texturebox.setItems(prettytex)
	def browseMD2(self,junk):
		dia=FileDialog(self.ui.screen,self.lastdialogpath,['*.md2'])
		dia.run()
		if dia.selected is not None:
			path=dia.selected
			if os.path.isdir(path):
				path=os.path.join(path,'tris.md2')
			self.loadMD2(path)
			if self.origauthorbox.getText()=='':
				author=self.guessAuthor(path)
				if author is not None:
					self.origauthorbox.setText(author)
		self.lastdialogpath=dia.path
	def guessAuthor(self,path):
		dirpath=os.path.dirname(path)
		author=None
		for filename in os.listdir(dirpath):
			if filename.lower().endswith('.txt'):
				fullpath=os.path.join(dirpath,filename)
				author=GetAuthor(open(fullpath,'r').read())
		return author
	def updateListBox(self,event):
		if event.type==KEYUP:
			self.refreshList(0)
	def progressCallback(self):
		self.progress.incValue(1)
		self.prog+=1
		self.ui.draw()
	def statusCallback(self,text):
		self.errortext.setText(text)
		self.ui.draw()
	def createVXP(self,junk):
		self.prog=0
		self.saveSettings()
		self.progress.setValue(0)
		activeanimations=[]
		for i,(animname,frame) in enumerate(self.animations):
			if self.animbox.isChecked(i):
				activeanimations.append(animname)
			pass
		self.progress.setMax(6+len(activeanimations)+4*len(self.textures))
		try:
			if len(activeanimations)==0:
				raise SaveError('No animations active!')
			name=str(self.namebox.getText())
			author=str(self.authorbox.getText())
			origauthor=str(self.origauthorbox.getText())
			outfile=self.shortnamebox.getText()+'.vxp'
			shortname=str(self.shortnamebox.getText())
			md2file=self.md2path
			if md2file is None:
				raise SaveError('no md2 selected')
			if self.idbox.getText()=='':
				raise SaveError('No ID')
			uniqueid=int(self.idbox.getText())
			outtextures=[]
			for i,texture in enumerate(self.textures):
				if self.texturebox.isChecked(i):
					outtextures.append('+'+texture)
				else:
					outtextures.append('-'+texture)
			preview=self.previewimg
			if preview is None:
				raise SaveError('no preview image!')
			pygame.image.save(preview,'temp_preview.bmp')
			dither=True # We override, so who cares.
			actor=self.actor.getValue()
			scaling=float(self.scaletext.getValue().replace(',','.'))
			single_frame={}
			for animation,single in zip(self.animations,self.singlelist):
				if single:
					single_frame[animation[0]]=0
			
			ret=md2_to_vxp.CreateVXPExpansionFromMD2(name,author,origauthor,outfile,shortname,md2file,
						outtextures,activeanimations,'temp_preview.bmp',dither,actor,scaling,single_frame,uniqueid,
						self.progressCallback,self.statusCallback)
			if ret:
				self.errortext.setText('VXP saved as %s' % (outfile))
				self.idbox.setText('') #So we don't reuse them by mistake.
				if self.install_check.isChecked():
					vxpinstaller.installVXP(outfile)
					self.errortext.setText('VXP saved as %s, and installed.' % (outfile))
			else:
				self.errortext.setText('Failed: unknown error (!ret)')
			try:
				os.unlink('temp_preview.bmp')
			except:
				pass
		except SaveError,e:
			self.errortext.setText('Failed: ' + str(e))
		except ValueError:
			self.errortext.setText('Failed: Bad Scaling!')
		except pygame.error,e:
			self.errortext.setText('Failed: ' + str(e))
	def copyAuthorToOrigAuthor(self,junk):
		self.origauthorbox.setText(self.authorbox.getText())
	def saveExtraSettings(self):
		try:
			self.config.add_section('md2_to_vxp')
		except:
			pass
		self.config.set('md2_to_vxp','actor',`self.actor.isChecked()`)
		self.config.set('md2_to_vxp','scaling',self.scaletext.getText())
	def getScaling(self):
		try:
			return self.config.get('md2_to_vxp','scaling')
		except:
			return '0.15'
	def getActor(self):
		try:
			val=self.config.get('md2_to_vxp','actor')
			return sockgui.BoolConv(val)
		except:
			return True
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
	pygame.display.set_caption(title+'md2_to_vxp '+md2_to_vxp.version)
	screen=pygame.display.set_mode((375,480))
	gui=md22vxpGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('md2_to_vxp','Convert Quake 2 models to actors/props',None,md2_to_vxp.version) # None is the ICONOS.
