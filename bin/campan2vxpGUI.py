#CAMPAN2VXP: Creates VXPs/VMMs of camera pans
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
import campan2vxp
from error import SaveError,InstallError
from idgenerator import GenerateID
import ConfigParser
import vxpinstaller
import pathwidget
import campan2vxp
from filedialog import FileDialog,IMAGEFORMATS
class campan2vxpGUI(ConverterBase):
	def __init__(self,screen):
		ConverterBase.__init__(self,screen)
		ui=self.ui
		#ui.add(sockgui.BorderBox(ui,[5,5],[x-10 for x in screen.get_size()]))
		
		#ui.add(sockgui.BorderBox(ui,[10,10],[screen.get_width()-20,94]))
		ys=self.makeTab(10,76,'CFG settings')
		ui.add(sockgui.Label(ui,[20,ys+10],'Expansion name:'))
		ui.add(sockgui.Label(ui,[20,ys+26],'Author name:'))
		ui.add(sockgui.Label(ui,[20,ys+42],'Shortname:'))
		ui.add(sockgui.Label(ui,[20,ys+58],'Filenames:'))
		
		
		self.filenamelabel=sockgui.Label(ui,[120,ys+58],'')
		ui.add(self.filenamelabel)
		
		self.namebox=       sockgui.TextBox(ui,[120,ys+10-3],40)
		self.authorbox=     sockgui.TextBox(ui,[120,ys+26-3],40)
		self.shortnamebox=  sockgui.TextBox(ui,[120,ys+42-3],40,callback=self.onShortNameChanged)
		self.shortnamebox.setAllowedKeys(sockgui.UPPERCASE+sockgui.LOWERCASE+sockgui.DIGITS+'._-')

		self.authorbox.setText(self.getAuthor())
		
		ui.add(self.namebox)
		ui.add(self.authorbox)
		ui.add(self.shortnamebox)
		self.namebox.activate()

		ys=self.makeTab(ys+76+5,225,'Path')

		self.pathbox=pathwidget.PathBox(ui,[15,ys+5],[200,200])
		ui.add(self.pathbox)
		ui.add(sockgui.Label(ui,[15+200+10,ys+8],'# of frames:'))
		self.framesbox=sockgui.TextBox(ui,[15+200+75,ys+5],10)
		self.framesbox.setAllowedKeys('0123456789')	
		self.framesbox.setText(`self.getFrameCount()`)
		ui.add(self.framesbox)
		ui.add(sockgui.Label(ui,[15+200+10,ys+24],'Movement per frame:'))
		self.movementbox=sockgui.TextBox(ui,[15+200+75,ys+38],10)
		self.movementbox.setAllowedKeys('0123456789.,')	
		self.movementbox.setText(`self.getSavedMovementAmount()`)
		ui.add(self.movementbox)

		ui.add(sockgui.Label(ui,[15+200+10,ys+68],'Background Color:'))
		ui.add(sockgui.Label(ui,[15+200+10,ys+68+16+3],'Red:'))
		ui.add(sockgui.Label(ui,[15+200+10,ys+68+32+3],'Green:'))
		ui.add(sockgui.Label(ui,[15+200+10,ys+68+48+3],'Blue:'))
		self.color=self.getColor()
		self.redbox=sockgui.TextBox(ui,[15+200+75,ys+68+16],10,`self.color[0]`,callback=self.textboxChanged,data='R')
		self.greenbox=sockgui.TextBox(ui,[15+200+75,ys+68+32],10,`self.color[1]`,callback=self.textboxChanged,data='G')
		self.bluebox=sockgui.TextBox(ui,[15+200+75,ys+68+48],10,`self.color[2]`,callback=self.textboxChanged,data='B')
		self.redbox.setAllowedKeys('0123456789Xx')	
		self.greenbox.setAllowedKeys('0123456789Xx')	
		self.bluebox.setAllowedKeys('0123456789Xx')	
		ui.add(self.redbox)
		ui.add(self.greenbox)
		ui.add(self.bluebox)

		self.color_preview=sockgui.BorderBox(self.ui,[15+200+75,ys+68+64],[50,20],bgcolor=self.color)
		self.ui.add(self.color_preview)

		ui.add(sockgui.Label(ui,[15+195+10,ys+150],'Aspect:'))
		widescreentypes=['Full (1.777)','Academy Flat (1.85:1)','Anamorphic Scope (2.35:1)','Academy Standard (1.33:1)']
		self.aspectbox=sockgui.ListBox(ui,[15+195+10,ys+160],[26,4],items=widescreentypes,scrollbar=False)
		self.aspectbox.select(self.getAspect())
		ui.add(self.aspectbox)

		ui.add(sockgui.Button(ui,[15,ys+207],'Set guide image...',callback=self.setBG))
		ui.add(sockgui.Button(ui,[15+100,ys+207],'Clear guide',callback=self.clearBG))
		ui.add(sockgui.Button(ui,[15+175,ys+207],'Clear points',callback=self.pathbox.clearPath))
		
		ys=self.makeTab(ys+230,30,'3dmm IDs')
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		self.idbox.setAllowedKeys('0123456789')	
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		
		ys=self.makeTab(ys+30+5,66,'Control')
		self.install_check=sockgui.CheckBox(ui,[240,ys+13-4],'Install VXP',self.getInstallCheck())
		ui.add(self.install_check)
		self.makemovie_check=sockgui.CheckBox(ui,[240,ys+26-4],'Make VMM Movie',self.getMakeMovieCheck())
		ui.add(self.makemovie_check)
		self.progress=sockgui.ProgressBox(ui,[20,ys+10],[200,16],maxvalue=7)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+32],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+46],'Create VXP',callback=self.createVXP)
		ui.add(self.startbutton)
		
		self.tbox_changed_events=True	
		self.lastdialogpath='.'
	def setBG(self,data):
		dia=FileDialog(screen,self.lastdialogpath,IMAGEFORMATS)
		dia.run()
		if dia.selected is not None:
			try:
				surf=pygame.image.load(dia.selected)
				imgw,imgh=surf.get_size()
				goodsize=self.pathbox.getInnerSize()
				if (imgw,imgh)!=goodsize:
					surf=pygame.transform.scale(surf,goodsize)
				self.pathbox.setBackground(surf.convert())
			except pygame.error:
				pass
		self.lastdialogpath=dia.path
	def clearBG(self,data):
		self.pathbox.setBackground()
	def textboxChanged(self,color,newtext):
		try:
			if newtext in ('','x','X'):
				val=0
			else:
				if newtext[0] in ('x','X'):
					val=abs(int(newtext[1:],16))
				else:
					val=abs(int(newtext))
			if val>255:
				val=255
			if val<0:
				val=0
			if color=='R':
				self.color[0]=val
			if color=='G':
				self.color[1]=val
			if color=='B':
				self.color[2]=val
			self.color_preview.setBackground(self.color)
		except Exception,e:
			return
	def createVXP(self,junk):
		self.saveSettings()
		self.progress.setValue(0)
		try:
			shortname=str(self.shortnamebox.getText())
			outfile=shortname+'.vxp'
			outmovie=shortname+'.vmm'
			uniqueid=int(self.idbox.getText())
			path=self.pathbox.getPath()
			name=str(self.namebox.getText())
			author=str(self.authorbox.getText())
			frames=int(self.framesbox.getText())
			if frames<=0:
				self.errortext.setText('Frame count must be >0')
				return
			if path.getLength()<=0.0:
				self.errortext.setText('Path must have at least 2 points.')
				return
			aspect=self.aspectbox.getSelectedIndex()
			movementscale=self.getMovementAmount()
			ret=campan2vxp.CreateVXPExpansionFromPan(name,author,outfile,shortname,self.color,
					path,frames,movementscale,aspect,uniqueid,self.progressCallback)
			if ret:
				self.errortext.setText('VXP saved as %s' % (outfile))
				self.idbox.setText('') #So we don't reuse them by mistake.
				installed=False
				if self.install_check.isChecked():
					vxpinstaller.installVXP(outfile)
					self.errortext.setText('VXP saved as %s, and installed.' % (outfile))
					installed=True
				if self.makemovie_check.isChecked(): 	
					campan2vxp.GenerateMovie(shortname,uniqueid,frames,outfile)
					if installed:
						self.errortext.setText('VMM created as %s (.VXP installed)' % (shortname+'.vmm'))
					else:
						self.errortext.setText('VMM created as %s.' % (shortname+'.vmm'))
			else:
				self.errortext.setText('Failed: unknown error (!ret)')
		except SaveError,e:
			self.errortext.setText('Failed: ' + str(e))
		except InstallError,e:
			self.errortext.setText('Install failed: ' + str(e))
		except ValueError:
			self.errortext.setText('Failed: Bad ID!')
		except pygame.error,e:
			self.errortext.setText('Failed: ' + str(e))
	def getMovementAmount(self):
		try:
			boxstr=self.movementbox.getText().replace(',','.')
			return float(boxstr)
		except: 
			return 0.0
	def saveExtraSettings(self):
		try:
			self.config.add_section('campan')
		except:
			pass
		self.config.set('campan','framecount',self.framesbox.getText())
		self.config.set('campan','makemovie',`self.makemovie_check.isChecked()`)
		self.config.set('campan','moveamt',`self.getMovementAmount()`)
		self.config.set('campan','r',`self.color[0]`)
		self.config.set('campan','g',`self.color[1]`)
		self.config.set('campan','b',`self.color[2]`)
		self.config.set('campan','aspect',`self.aspectbox.getSelectedIndex()`)
	def getFrameCount(self):
		try:
			return int(self.config.get('campan','framecount'))
		except:
			return 10
	def getAspect(self):
		try:
			return int(self.config.get('campan','aspect'))
		except:
			return 0
	def getSavedMovementAmount(self):
		try:
			return float(self.config.get('campan','moveamt'))
		except:
			return 200.0
	def getColor(self):
		try:
			r=int(self.config.get('campan','r'))
			g=int(self.config.get('campan','g'))
			b=int(self.config.get('campan','b'))
			return [r,g,b]
		except:
			return [255,255,255]
	def getMakeMovieCheck(self):
		try:
			val=self.config.get('campan','makemovie')
			return sockgui.BoolConv(val)
		except:
			return False
	def onShortNameChanged(self,data,newtext):
		if newtext=='':
			rtxt=''
			out=''
		else:
			rtxt=self.shortnamebox.getText()
			out=rtxt+'(.vxp/.vmm)'
		self.filenamelabel.setRed(os.path.exists(rtxt+'.vxp'))
		self.filenamelabel.setText(out)

def RunConverter(title):
	global screen
	pygame.display.set_caption(title+'campan2vxp '+campan2vxp.version)
	screen=pygame.display.set_mode((375,480))
	gui=campan2vxpGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('campan2vxp','Create a 2D camera pan scene',None,campan2vxp.version) # None is the ICONOS.

