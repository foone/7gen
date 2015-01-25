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
import rgb2vxp
from error import SaveError,InstallError
from idgenerator import GenerateID
import ConfigParser
import vxpinstaller
class rgb2vxpGUI(ConverterBase):
	def __init__(self,screen):
		ConverterBase.__init__(self,screen)
		ui=self.ui
		#ui.add(sockgui.BorderBox(ui,[5,5],[x-10 for x in screen.get_size()]))
		
		#ui.add(sockgui.BorderBox(ui,[10,10],[screen.get_width()-20,94]))
		ys=self.makeTab(10,76,'CFG settings')
		ui.add(sockgui.Label(ui,[20,ys+10],'Expansion name:'))
		ui.add(sockgui.Label(ui,[20,ys+26],'Author name:'))
		ui.add(sockgui.Label(ui,[20,ys+42],'Shortname:'))
		ui.add(sockgui.Label(ui,[20,ys+58],'Filename:'))
		
		
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

		ys=self.makeTab(ys+76+5,90,'Color')

		ui.add(sockgui.Label(ui,[20,ys+10],'Red:'))
		ui.add(sockgui.Label(ui,[20,ys+27],'Green:'))
		ui.add(sockgui.Label(ui,[20,ys+44],'Blue:'))

		self.slider_red=sockgui.Slider(ui,[52,ys+10-4],[280,16],255,255,callback=self.sliderMove)
		self.slider_red.setData(self.slider_red)
		ui.add(self.slider_red)
		self.color_box_red=sockgui.TextBox(ui,[338,ys+10-4],3,'255',callback=self.textboxChanged)
		self.color_box_red.setData(self.slider_red)
		ui.add(self.color_box_red)
		
		self.slider_green=sockgui.Slider(ui,[52,ys+27-4],[280,16],255,255,callback=self.sliderMove)
		self.slider_green.setData(self.slider_green)
		ui.add(self.slider_green)
		self.color_box_green=sockgui.TextBox(ui,[338,ys+27-4],3,'255',callback=self.textboxChanged)
		self.color_box_green.setData(self.slider_green)
		ui.add(self.color_box_green)

		self.slider_blue=sockgui.Slider(ui,[52,ys+44-4],[280,16],255,255,callback=self.sliderMove)
		self.slider_blue.setData(self.slider_blue)
		ui.add(self.slider_blue)
		self.color_box_blue=sockgui.TextBox(ui,[338,ys+44-4],3,'255',callback=self.textboxChanged)
		self.color_box_blue.setData(self.slider_blue)
		ui.add(self.color_box_blue)

		self.hexcolor=sockgui.Label(ui,[20,ys+62+6],'Hex color: #FFFFFF')
		ui.add(self.hexcolor)
		self.color_preview=sockgui.BorderBox(self.ui,[120,ys+62],[239,20],bgcolor=(255,255,255))
		self.ui.add(self.color_preview)

		ys=self.makeTab(ys+90+5,30,'3dmm IDs')
		ui.add(sockgui.Label(ui,[20,ys+10],'ID:'))
		self.idbox=sockgui.TextBox(ui,[40,ys+7],10)
		ui.add(self.idbox)
		ui.add(sockgui.Button(ui,[110,ys+7],'Generate ID',callback=self.generateNewID))
		
		ys=self.makeTab(ys+30+5,66,'Control')
		self.install_check=sockgui.CheckBox(ui,[240,ys+13],'Install VXP',self.getInstallCheck())
		ui.add(self.install_check)
		self.progress=sockgui.ProgressBox(ui,[20,ys+10],[200,16],maxvalue=7)
		ui.add(self.progress)
		self.errortext=sockgui.Label(ui,[20,ys+32],'')
		ui.add(self.errortext)

		self.startbutton=sockgui.Button(ui,[20,ys+46],'Create VXP',callback=self.createVXP)
		ui.add(self.startbutton)
		
		self.tbox_changed_events=True	
	def updateColors(self):
		r=self.slider_red.getValue()
		g=self.slider_green.getValue()
		b=self.slider_blue.getValue()
		self.hexcolor.setText('Hex color: #%02X%02X%02X'%(r,g,b))
		self.color_preview.setBackground((r,g,b))
		pass
	def sliderMove(self,value,slider):
		slider.setValue(value)
		self.tbox_changed_events=False
		if slider==self.slider_red:
			self.color_box_red.setText(str(value))
		elif slider==self.slider_green:
			self.color_box_green.setText(str(value))
		elif slider==self.slider_blue:
			self.color_box_blue.setText(str(value))
		self.tbox_changed_events=True
		self.updateColors()
	def textboxChanged(self,slider,newtext):
		if self.tbox_changed_events:
			try:
				if newtext in ('','x','X'):
					val=0
				else:
					if newtext[0] in ('x','X'):
						val=abs(int(newtext[1:],16))
					else:
						val=abs(int(newtext))
				slider.setValue(val)				
				self.updateColors()
			except Exception,e:
				return
	def createVXP(self,junk):
		self.saveSettings()
		self.progress.setValue(0)
		try:
			outfile=self.shortnamebox.getText()+'.vxp'
			uniqueid=int(self.idbox.getText())
			r,g,b=self.slider_red.getValue(),self.slider_green.getValue(),self.slider_blue.getValue()
			ret=rgb2vxp.CreateVXPExpansionFromColor(str(self.namebox.getText()),str(self.authorbox.getText()),str(outfile),str(self.shortnamebox.getText()),(r,g,b),uniqueid,self.progressCallback)
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
		except InstallError,e:
			self.errortext.setText('Install failed: ' + str(e))
		except ValueError:
			self.errortext.setText('Failed: Bad ID!')
		except pygame.error,e:
			self.errortext.setText('Failed: ' + str(e))
	def onShortNameChanged(self,data,newtext):
		if newtext=='':
			out=''
		else:
			out=self.shortnamebox.getText() + '.vxp'
		self.filenamelabel.setRed(os.path.exists(out))
		self.filenamelabel.setText(out)
def RunConverter(title):
	pygame.display.set_caption(title+'rgb2vxp '+rgb2vxp.version)
	screen=pygame.display.set_mode((375,394-45))
	gui=rgb2vxpGUI(screen)
	return gui.run()
if __name__=='__main__':
	pygame.init()
	RunConverter('')
def GetInfo():
	return ('rgb2vxp','Create a single-colored scene background',None,rgb2vxp.version) # None is the ICONOS.
