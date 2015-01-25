#!/usr/bin/python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import pygame
from pygame.constants import *
import os.path
have_clipboard=False
try:
	import win32clipboard
	have_clipboard=True
except:
	pass
datapath=''
def BoolConv(val):
	lval=str(val).lower()
	if lval in ('true','t','1','on','yes','yep','ja','hai','da','si','ya','ken'):
		return True
	return False
def PasteString():
	if not have_clipboard:
		return None
	win32clipboard.OpenClipboard()
	if win32clipboard.IsClipboardFormatAvailable(1):
		data=win32clipboard.GetClipboardData()
	else:
		data=None
	win32clipboard.CloseClipboard()
	return data
def setDataPath(newpath):
	global datapath
	datapath=newpath
UPPERCASE='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWERCASE='abcdefghijklmnopqrstuvwxyz'
DIGITS='0123456789'
class Font:
	def __init__(self,filename):
		try:
			self.surf=pygame.image.load(filename)
		except pygame.error: 
			self.surf=pygame.image.load(os.path.join('code',filename))
		self.surf.set_colorkey((255,0,255))
		self.redsurf=pygame.Surface(self.surf.get_size(),0,self.surf)
		npal=self.surf.get_palette()
		self.redsurf.set_palette(list(npal[0:1])+[(255,0,0)]+list(npal[2:]))
		self.redsurf.blit(self.surf,(0,0))
		self.redsurf.set_colorkey((255,0,255))
	def draw(self,dest,pos,text,red=False):
		xpos,ypos=pos
		if red:
			surf=self.redsurf
		else:
			surf=self.surf
		for char in text:
			val=ord(char)-32
			ys=(val/16)*8
			xs=(val%16)*8
			if val>=96: # 128-32, so invalid.
				ys=48
				xs=16
			dest.blit(surf,(xpos,ypos),(xs,ys,5,8))
			xpos+=5
	def optimize(self):
		self.surf=self.surf.convert()
		self.surf.set_colorkey((255,0,255))
		self.redsurf=self.redsurf.convert()
		self.redsurf.set_colorkey((255,0,255))
	def drawCheck(self,dest,pos):
		dest.blit(self.surf,pos,(0,48,8,8))
	def drawCorner(self,dest,pos,number):
		if number==0:
			dest.blit(self.surf,pos,(8,50,3,3))
		elif number==1:
			dest.blit(self.surf,pos,(11,50,3,3))
		elif number==2:
			dest.blit(self.surf,pos,(8,53,3,3))
		elif number==3:
			dest.blit(self.surf,pos,(11,53,3,3))
			
	def getTextLength(self,text):
		return (len(text)*5,8)
class Window:
	def __init__(self,rect=[0,0,0,0],color=(255,255,255)):
		self.rect=list(rect)
		self.children=[]
		self.color=color
	def draw(self,dest):
		dest.fill(self.color,pygame.Rect(self.rect))
		oldclip=dest.get_clip()
		dest.set_clip(self.rect)
		for child in self.children:
			child.draw(dest)
		dest.set_clip(oldclip)
	def add(self,widget):
		self.children.append(widget)
	def mouseMove(self,pos,buttons):
		found=False
		for child in self.children:
			if child.mouseMove(pos,button):
				found=True
		return found
	def mouseDown(self,pos,button):
		found=False
		for child in self.children:
			if child.mouseDown(pos,button):
				found=True
		return found
	def mouseUp(self,pos,button):
		found=False
		for child in self.children:
			if child.mouseUp(pos,button):
				found=True
		return found
	def keyUp(self,key,mod):
		for child in self.children:
			if child.keyUp(key,mod):
				return True
		return False
	def keyDown(self,key,mod,unicode):
		for child in self.children:
			if child.keyDown(key,mod,unicode):
				return True
		return False
	def setSilly(self,silly):
		for child in self.children:
			child.setSilly(silly)
		return True
class Widget:
	def __init__(self,ui,pos=[0,0],size=[1,1]):
		self.pos=list(pos)
		self.size=list(size)
		self.ui=ui
		self.collide_rect=pygame.Rect(pos,size)
	def getRect(self):
		return self.pos+self.size
	def getSize(self):
		return self.size
	def getPos(self):
		return self.pos
	def getX(self):
		return self.pos[0]
	def getY(self):
		return self.pos[1]
	def getWidth(self):
		return self.size[0]
	def getHeight(self):
		return self.size[1]
	def draw(self,dest):
		pass
	def resize(self,newsize):
		pass
	def move(self,newpos):
		self.pos=list(newpos)
		self.collide_rect=pygame.Rect(self.pos,self.size)
		self.updateMovables()
	def updateMovables(self): # this is supposed to be overridden
		pass
	def shift(self,x,y):
		self.pos[0]+=x
		self.pos[1]+=y
	def mouseDown(self,pos,button):
		return False
	def mouseUp(self,pos,button):
		return False
	def mouseMove(self,pos,buttons):
		return False
	def keyDown(self,key,mod,code):
		return False
	def keyUp(self,key,mode):
		return False
	def isActivatable(self):
		return False
	def activate(self):
		pass
	def deactivate(self):
		pass
	def isOver(self,pos):
		return self.collide_rect.collidepoint(pos)
	def setCallback(self,callback):
		self.callback=callback
	def setData(self,data):
		self.data=data
	def setSilly(self,silly):
		pass
class ActivatableWidget(Widget):
	def __init__(self,ui,pos,size):
		Widget.__init__(self,ui,pos,size)
		self.active=False
	def keyDown(self,key,mod,uni):
		if not self.active:
			return False
		if key==K_TAB:
			self.deactivate()
			if mod&KMOD_SHIFT:
				self.ui.activatePrev(self)
			else:
				self.ui.activateNext(self)
			return True
		elif key==K_UP:
			self.deactivate()
			self.ui.activatePrev(self)
			return True
		elif key==K_DOWN:
			self.active=False
			self.ui.activateNext(self)
			return True
		return False
	def isActivatable(self):
		return True
	def activate(self):
		self.active=True
	def deactivate(self):
		self.active=False
class UI:
	def __init__(self,screen):
		pygame.key.set_repeat(500,30)
		self.screen=screen
		self.topwindow=Window([0,0]+list(screen.get_size()))
		self.is_running=True
		self.font=Font(os.path.join(datapath,'font.png'))
		self.needs_update=False
		self.activatable=[]
		self.hotkeys={}
		self.move_listeners=[]
		self.die_reason=None
	def draw(self):
		self.topwindow.draw(self.screen)
		pygame.display.flip()
	def event(self,event):
		if event.type==QUIT:
			self.is_running=False
			self.die_reason=QUIT
		if event.type==KEYDOWN:
			callback=self.hotkeys.get(event.key)
			if callback is not None:
				if callback(event):
					return # handled
			self.topwindow.keyDown(*self.translateKey(event.key,event.mod,event.unicode))
		if event.type==KEYUP:
			callback=self.hotkeys.get(event.key)
			if callback is not None:
				if callback(event):
					return # handled
			if event.key==K_ESCAPE:
				self.die_reason=K_ESCAPE
				self.is_running=False
			self.topwindow.keyUp(*self.translateKey(event.key,event.mod))
		if event.type==MOUSEBUTTONDOWN:
			self.topwindow.mouseDown(event.pos,event.button)
		if event.type==MOUSEBUTTONUP:
			self.topwindow.mouseUp(event.pos,event.button)
			self.move_listeners=[]
		if event.type==MOUSEMOTION:
			for listener in self.move_listeners:
				if listener.mouseMove(event.pos,event.buttons):
					return #handled
	def translateKey(self,key,mod,unicode=None):
		uni=unicode
		if mod&KMOD_NUM:
			if key>=K_KP0 and key<=K_KP9:
				diff=key-K_KP0
				key=K_0+(key-K_KP0)
				uni=chr((ord('0')+diff))
		else:
			if key==K_KP4:
				key=K_LEFT
				uni=''
			elif key==K_KP6:
				key=K_RIGHT
				uni=''
			elif key==K_KP8:
				key=K_UP
				uni=''
			elif key==K_KP2:
				key=K_DOWN
				uni=''
		if unicode is None:
			return (key,mod)			
		else:
			return (key,mod,uni)
	def add(self,widget):
		self.topwindow.add(widget)
		if widget.isActivatable():
			self.activatable.append(widget)
	def activateShift(self,current,amt):
		i=self.activatable.index(current)
		i+=amt
		if i<0:
			i=len(self.activatable)-1
		elif i>=len(self.activatable):
			i=0
		try:
			self.activatable[i].activate()
		except IndexError:
			pass
	def activateNext(self,current):
		self.activateShift(current,1)
	def activatePrev(self,current):
		self.activateShift(current,-1)
	def deactivate(self):
		for thing in self.activatable:
			thing.deactivate()
	def update(self):
		self.needs_update=True
	def registerHotKey(self,key,callback):
		self.hotkeys[key]=callback
	def requestMoveEvents(self,widget):
		self.move_listeners.append(widget)
	def shutdown(self):
		self.is_running=False
		self.die_reason='Shutdown'
	def getSize(self):
		return self.screen.get_size()
	def setSilly(self,sillyness):
		self.topwindow.setSilly(sillyness)
		
class BorderBox(Widget):
	def __init__(self,ui,pos=[0,0],size=[1,1],color=(0,0,0),bgcolor=None):
		Widget.__init__(self,ui,pos,size)
		self.color=color
		self.background=bgcolor
	def setColor(self,color):
		self.color=color
	def setBackground(self,background):
		self.background=background
	def draw(self,dest):
		rect=self.pos + self.size
		if self.background is not None:
			dest.fill(self.background,rect)
		pygame.draw.rect(dest,self.color,rect,1)
class Seperator(Widget):
	def __init__(self,ui,pos=[0,0],size=[1,1],color=(0,0,0)):
		Widget.__init__(self,ui,pos,size)
		self.color=color
	def setColor(self,color):
		self.color=color
	def draw(self,dest):
		rect=self.pos + self.size
		dest.fill(self.color,rect)
class ImageBox(Widget):
	def __init__(self,ui,pos=[0,0],size=[1,1],bgcolor=(127,127,127),image=None):
		Widget.__init__(self,ui,pos,size)
		self.bgcolor=bgcolor
		self.image=image
	def setImage(self,image=None):
		self.image=image
	def setBackground(self,background):
		self.bgcolor=background
	def draw(self,dest):
		rect=self.pos + self.size
		if self.image is not None:
			dest.blit(self.image,self.pos,(0,0,self.size[0],self.size[1]))
		else:
			dest.fill(self.bgcolor,rect)
class Label(Widget):
	def __init__(self,ui,pos=[0,0],text='<Label>',red=False):
		size=ui.font.getTextLength(text)
		Widget.__init__(self,ui,pos,size)
		self.red=red
		self.text=text
	def setText(self,newtext):
		self.text=newtext
		self.size=self.ui.font.getTextLength(self.text)
	def setRed(self,red=False):
		self.red=red
	def draw(self,dest):
		self.ui.font.draw(dest,self.pos,self.text,self.red)
class Button(ActivatableWidget):
	def __init__(self,ui,pos=[0,0],text='<Button>',padding=3,callback=None,data=None):
		txtsize=ui.font.getTextLength(text)
		size=[txtsize[0]+padding*2,txtsize[1]+padding*2]
		ActivatableWidget.__init__(self,ui,pos,size)
		self.text=text
		self.callback=callback
		self.data=data
		self.down=False
		self.padding=padding
		self.updateMovables()
	def updateMovables(self):
		shadowcolor=(127,127,127)
		shadowpos=[self.pos[0]+1,self.pos[1]+1]
		self.shadow=BorderBox(self.ui,shadowpos,self.size,shadowcolor,shadowcolor)
		self.border=BorderBox(self.ui,self.pos,self.size,(0,0,0),(160,160,160))
		self.active_border=BorderBox(self.ui,self.pos,self.size,(0,0,0),(220,220,220))
		self.label=Label(self.ui,[self.pos[0]+self.padding,self.pos[1]+self.padding],self.text)
	def draw(self,dest):
		border=self.border
		if self.active:
			border=self.active_border
		if self.down:
			border.shift(1,1)
			self.label.shift(1,1)
			border.draw(dest)
			self.label.draw(dest)
			border.shift(-1,-1)
			self.label.shift(-1,-1)
		else:
			self.shadow.draw(dest)
			border.draw(dest)
			self.label.draw(dest)
	def clicked(self):
		if self.callback is not None:
			self.callback(self.data)
	def mouseDown(self,pos,button):
		if self.isOver(pos):
			self.down=True
			self.ui.requestMoveEvents(self)
			return True
		return False
	def mouseUp(self,pos,button):
		if not self.down:
			return False
		self.down=False
		if self.isOver(pos):
			self.clicked()
			return True
		return False
	def mouseMove(self,pos,buttons):
		if self.down:
			if not self.isOver(pos):
				self.down=False
		return False
	def keyDown(self,key,mod,unicode):
		if not self.active:
			return False
		if ActivatableWidget.keyDown(self,key,mod,unicode):
			return True
		if key in (K_SPACE,K_RETURN):
			if self.down:
				return True # No keyboarding while we're down.
			self.down=True #Fake a click to make it look nicer.
			self.ui.draw()
			self.clicked()
			self.down=False 
			return True
		return False
class CheckBox(ActivatableWidget):
	def __init__(self,ui,pos=[0,0],text='',value=True,callback=None,data=None):
		txtsize=ui.font.getTextLength(text)
		size=[8+3+txtsize[0],max(8,txtsize[1])]
		ActivatableWidget.__init__(self,ui,pos,size)
		self.text=text
		self.callback=callback
		self.data=data
		self.value=value
		self.border=BorderBox(ui,pos,[8,8],(0,0,0),(160,160,160))
		self.active_border=BorderBox(ui,pos,[8,8],(0,0,0),(220,220,220))
		self.label=Label(ui,[pos[0]+8+3,pos[1]],text)
	def draw(self,dest):
		border=self.border
		if self.active:
			border=self.active_border
		border.draw(dest)
		if self.value:
			self.ui.font.drawCheck(dest,self.pos)
		self.label.draw(dest)
	def clicked(self):
		self.value=not self.value
		if self.callback:
			self.callback(self.data)
	def mouseDown(self,pos,button):
		if self.isOver(pos):
			self.clicked()
			return True
		return False
	def keyDown(self,key,mod,unicode):
		if not self.active:
			return False
		if ActivatableWidget.keyDown(self,key,mod,unicode):
			return True
		if key in (K_SPACE,K_RETURN):
			self.clicked()
			return True
		return False
	def isChecked(self):
		return self.value
	def getValue(self):
		return self.value
class TextBox(ActivatableWidget):
	def __init__(self,ui,pos,length,init_text='',padding=3,callback=None,data=None):
		txtsize=[length*5,8]
		size=[txtsize[0]+padding*2,txtsize[1]+padding*2]
		ActivatableWidget.__init__(self,ui,pos,size)
		self.text=init_text
		self.length=length
		self.txtpos=[pos[0]+padding,pos[1]+padding]
		self.border=BorderBox(ui,pos,size,bgcolor=(160,160,160))
		self.active_border=BorderBox(ui,pos,size,bgcolor=(220,220,220))
		self.allowed_keys=None
		self.callback=callback
		self.data=data
		#self.changed()
	def getText(self):
		return self.text
	def getValue(self):
		return self.text
	def setText(self,newtext):
		if len(newtext)>self.length:
			newtext=newtext[0:self.length]
		self.text=newtext
		self.changed()
	def changed(self):
		if self.callback is not None:
			self.callback(self.data,self.text)
	def keyDown(self,key,mod,unicode):
		if not self.active:
			return False
		if ActivatableWidget.keyDown(self,key,mod,unicode):
			return True
		if key==K_BACKSPACE:
			self.text=self.text[0:-1]
			self.changed()
			return True
		if key==K_INSERT and mod&KMOD_SHIFT!=0:
			data=PasteString()
			if data is not None:
				for char in data:
					self.addChar(char)
			return True
		if key==K_v and mod&KMOD_CTRL!=0:
			data=PasteString()
			if data is not None:
				for char in data:
					self.addChar(char)
			return True
		elif key in (K_LEFT,K_RIGHT):
			return True
		else:
			return self.addChar(unicode)
	def addChar(self,unicode):
		if unicode=='' or ord(unicode)<ord(' '):
			return True # Control character
		if self.allowed_keys is not None:
			if unicode not in self.allowed_keys:
				return True
		self.text+=unicode
		if len(self.text)>self.length:
			self.text=self.text[0:self.length]
		else:
			self.changed()
	def setAllowedKeys(self,mask=None):
		self.allowed_keys=mask
	def mouseDown(self,pos,button):
		if self.isOver(pos):
			self.ui.deactivate()
			self.activate()
			return True
		return False
	def draw(self,dest):
		if self.active:
			self.active_border.draw(dest)
			if len(self.text)==self.length:
				self.ui.font.draw(dest,self.txtpos,self.text)
			else:
				self.ui.font.draw(dest,self.txtpos,self.text+chr(127))
		else:
			self.border.draw(dest)
			self.ui.font.draw(dest,self.txtpos,self.text)
class ScrollBar(Widget):
	def __init__(self,ui,pos=[0,0],size=[10,10],maxv=1,callback=None):
		Widget.__init__(self,ui,pos,size)
		self.border=BorderBox(ui,pos,size,bgcolor=(190,190,190))
		if maxv==0:
			self.height=8
		else:
			self.height=max(8,self.size[1]/maxv)
		self.thumber=BorderBox(ui,pos,[size[0],self.height],bgcolor=(120,120,120))
		self.max=maxv
		self.value=0
		self.callback=callback
	def setValue(self,value):
		self.value=value
	def setMax(self,maxv):
		self.max=max(0,maxv)
	def draw(self,dest):
		self.border.draw(dest)
		try:
			thumbpos=int((self.value/float(self.max))*(self.size[1]-self.height))
		except ZeroDivisionError:
			thumbpos=0
		self.thumber.move([self.pos[0],self.pos[1]+thumbpos])
		self.thumber.draw(dest)
	def mouseMove(self,pos,buttons):
		if 1 in buttons:
			return self.mousePositioned(pos)
				
		return False
	def mouseDown(self,pos,button):
		if self.isOver(pos) and self.callback is not None:
			return self.mousePositioned(pos)
		return False
	def mousePositioned(self,pos):
			amt=((pos[1]-self.pos[1])/float(self.size[1]-2))*self.max
			amt=min(self.max,amt)
			self.callback(int(amt+0.5))
			self.ui.requestMoveEvents(self)
			return True
class Slider(Widget):
	def __init__(self,ui,pos=[0,0],size=[10,10],maxv=1,value=0,callback=None,data=None):
		Widget.__init__(self,ui,pos,size)
		self.border=BorderBox(ui,[pos[0],(pos[1]+size[1]/2)-1],[size[0],2],color=(190,190,190))
		self.thumber=BorderBox(ui,pos,[8,size[1]],bgcolor=(120,120,120))
		self.max=maxv
		self.value=value
		if callback is None:
			callback=self.setValue
		self.callback=callback
		self.data=data
	def setValue(self,value,junk=None):
		self.value=value
	def setMax(self,maxv):
		self.max=max(0,maxv)
	def setValue(self,value):
		self.value=min(value,self.max)
	def getValue(self):
		return self.value
	def draw(self,dest):
		self.border.draw(dest)
		try:
			thumbpos=int((self.value/float(self.max))*(self.size[0]-8))
		except ZeroDivisionError:
			thumbpos=0
		self.thumber.move([self.pos[0]+thumbpos,self.pos[1]])
		self.thumber.draw(dest)
	def mouseMove(self,pos,buttons):
		if 1 in buttons:
			return self.mousePositioned(pos)
		return False
	def mouseDown(self,pos,button):
		if self.isOver(pos) and self.callback is not None:
			return self.mousePositioned(pos)
		return False
	def mousePositioned(self,pos):
		amt=max(0,min(((pos[0]-self.pos[0])/float(self.size[0]-2))*self.max,self.max))
		self.callback(int(amt),self.data)
		self.ui.requestMoveEvents(self)
		return True
class ListBox(ActivatableWidget):
	def __init__(self,ui,pos=[0,0],size=[50,20],items=[],padding=3,double_click=None,scrollbar=True):
		self.charsize=size
		bordersize=[size[0]*5 + padding*2 , size[1]*8 + padding*2]
		if scrollbar:
			rsize=[bordersize[0]+15,bordersize[1]]# 15 is scrollbar
		else:
			rsize=[bordersize[0],bordersize[1]]
		self.txtpos=[x+padding for x in pos]
		ActivatableWidget.__init__(self,ui,pos,rsize)
		self.border=BorderBox(ui,pos,bordersize,bgcolor=(160,160,160))
		self.active_border=BorderBox(ui,pos,bordersize,bgcolor=(220,220,220))
		self.scrollbar=ScrollBar(ui,[pos[0]+bordersize[0]-1,pos[1]],[17,bordersize[1]],5,callback=self.setScroll)
		self.setItems(items)
		self.selected=None
		self.selectcolor=(120,120,255)
		self.selectsize=[bordersize[0]-2,8]
		self.scroll=0
		self.double_click=double_click
		self.use_scrollbar=scrollbar
	def unselect(self):
		self.selected=None
	def setDoubleClickCallback(self,callback=None):
		self.double_click=callback
	def setItems(self,newlist):
		maxv=max(0,len(newlist)-self.charsize[1])
		self.items=newlist
		self.scrollbar.setMax(maxv)
	def setItemText(self,index,text):
		self.items[index]=text
	def addItem(self,newitem):
		self.items.append(newitem)
	def draw(self,dest):
		if self.active:
			self.active_border.draw(dest)
		else:	
			self.border.draw(dest)
		ri=0
		for i,item in list(enumerate(self.items))[self.scroll:self.scroll+self.charsize[1]]:
			pos=(self.txtpos[0],self.txtpos[1]+ri*8)
			if i==self.selected:
				dest.fill(self.selectcolor,[self.pos[0]+1,pos[1]]+self.selectsize)
			self.ui.font.draw(dest,pos,item)
			ri+=1
		if self.use_scrollbar:
			self.scrollbar.draw(dest)
	def getNumItems(self):
		return len(self.items)
	def getSelectedText(self):
		try:
			return self.items[self.selected]
		except IndexError:
			return None
		except TypeError:
			return None
	def getSelectedIndex(self):
		if self.selected is not None and self.selected>=0 and self.selected<len(self.items):
			return self.selected
		else:
			return None
	def mouseDown(self,pos,button):
		if self.isOver(pos):
			if button==4:
				self.setScroll(self.scroll-3)
			elif button==5:
				self.setScroll(self.scroll+3)
			else:
				if self.scrollbar.mouseDown(pos,button):
					return True
				self.ui.deactivate()
				self.activate()
				ind=(pos[1]-self.txtpos[1]-6)/8
				self.select(self.scroll+ind,True)
			return True
		return False
	def keyDown(self,key,mod,uni):
		if not self.active:
			return False
		if key==K_PAGEUP:
			self.select(self.selected,-self.charsize[1])
			return True
		if key==K_PAGEDOWN:
			self.select(self.selected,self.charsize[1])
			return True
		if key==K_HOME:
			self.select(0,0)
			return True
		if key==K_END:
			self.select(len(self.items)-1,0)
			return True
		if key==K_UP:
			self.select(self.selected,-1)
			return True
		if key==K_DOWN:
			self.select(self.selected,1)
			return True
		if key in (K_RETURN,K_SPACE):
			self.select(self.selected,0)
			return True
		if ActivatableWidget.keyDown(self,key,mod,unicode):
			return True
		return False
	def select(self,newsel,shift=0):
		if len(self.items)==0:
			return
		if newsel is None:
			final=0
		else:
			final=newsel+shift
			if final==self.selected and self.double_click is not None:
				if not self.double_click(self,final):
					return # No more processing
		if final>=0 and final < len(self.items):
			self.selected=final
		elif final<0:
			self.selected=0
		elif final>=len(self.items):
			self.selected=len(self.items)-1
		if self.scroll+self.charsize[1]<self.selected+1:
			self.setScroll(self.selected-self.charsize[1]+1)
		elif self.selected<self.scroll:
			self.setScroll(self.selected)
	def setScroll(self,newval):
		maxscroll=max(0,len(self.items)-self.charsize[1])
		self.scroll=min(maxscroll,max(0,newval))
		self.scrollbar.setValue(self.scroll)
class CheckedListBox(ListBox):
	def __init__(self,ui,pos=[0,0],size=[50,20],items=[],padding=3,double_click=None):
		ListBox.__init__(self,ui,pos,size,items,padding,self.toggleCheck)
	def isChecked(self,index):
		return self.items[index][1]
	def setChecked(self,index,value):
		text,checked=self.items[index]
		self.items[index]=(text,value)
	def toggleCheck(self,listbox,selected):
		try:
			text,checked=self.items[selected]
			self.items[selected]=(text,not checked)
		except IndexError:
			pass
	def setItems(self,newlist):
		maxv=max(0,len(newlist)-self.charsize[1])
		self.items=[(x,True) for x in newlist]
		self.scrollbar.setMax(maxv)
	def setItemText(self,index,text):
		oldtext,checked=self.items[index]
		self.items[index]=(text,checked)
	def addItem(self,newitem,checked=True):
		self.items.append((newitem,checked))
	def draw(self,dest):
		if self.active:
			self.active_border.draw(dest)
		else:	
			self.border.draw(dest)
		ri=0
		font=self.ui.font
		for i,(item,checked) in list(enumerate(self.items))[self.scroll:self.scroll+self.charsize[1]]:
			pos=(self.txtpos[0],self.txtpos[1]+ri*8)
			if i==self.selected:
				dest.fill(self.selectcolor,[self.pos[0]+1,pos[1]]+self.selectsize)
			textpos=(pos[0]+10,pos[1])
			font.draw(dest,textpos,item)
			if checked:
				font.drawCheck(dest,pos)

			ri+=1
		self.scrollbar.draw(dest)

class ProgressBox(Widget):
	def __init__(self,ui,pos=[0,0],size=[1,1],color=(0,0,0),offcolor=(160,160,160),oncolor=(120,255,120),maxvalue=100):
		Widget.__init__(self,ui,pos,size)
		self.color=color
		self.offcolor=offcolor
		self.oncolor=oncolor
		self.value=0
		self.max=max(0,maxvalue)
	def setMax(self,newmax):
		self.max=max(0,newmax)
	def getMax(self):
		return self.max
	def setValue(self,val):
		self.value=max(0,min(val,self.max))
	def getValue(self):
		return self.value
	def incValue(self,amt):
		self.setValue(self.getValue()+amt)
	def draw(self,dest):
		amt=(self.value/float(self.max))*self.size[0]
		onrect=self.pos + [amt,self.size[1]]
		offrect=[self.pos[0]+amt,self.pos[1],self.size[0]-amt,self.size[1]]
		dest.fill(self.offcolor,offrect)
		dest.fill(self.oncolor,onrect)
		rect=self.pos+self.size
		pygame.draw.rect(dest,self.color,rect,1)
#class Tab(Widget):
#	pass
class SimpleTab(Widget):
	def __init__(self,ui,starty,height,text,startx=10,width=None,silly=True,callback=None,data=None): # Funky args for compatibility reasons
		if width is None:
			scrw,scrh=ui.getSize()
			width=scrw-20
		self.title=label=Label(ui,[startx+3,starty+3],text)
		self.border=BorderBox(ui,[startx,starty],[x+6 for x in label.getSize()])
		tabh=label.getSize()[1]+5
		self.ys=ys=starty+tabh
		self.border2=(BorderBox(ui,[startx,ys],[width,height]))
		pos=[startx,starty]
		size=[width,height+tabh]
		Widget.__init__(self,ui,pos,size)
		self.setSilly(silly)
		self.callback=callback
		self.data=data
	def setSilly(self,silly):
		startx,starty=self.pos
		if silly:
			w,h=self.border.getSize()
			self.border3=Seperator(self.ui,[startx+1,starty+1],(w-2,h-1),(255,255,255))
			self.parts=[self.border,self.border2,self.border3,self.title]
			self.corners=[(self.pos,0),((self.pos[0]+self.border.getWidth()-3,self.pos[1]),1),
			((self.pos[0]+self.border.getWidth()-1,self.pos[1]+self.border.getHeight()-3),2),
			((self.pos[0]+self.border2.getWidth()-3,self.border2.getY()),1),
			((self.pos[0]+self.border2.getWidth()-3,self.border2.getY()+self.border2.getHeight()-3),3),
			((self.pos[0],self.border2.getY()+self.border2.getHeight()-3),2),]
		else:
			self.parts=[self.border,self.border2,self.title]
			self.corners=[]
	def draw(self,dest):
		for part in self.parts:
			part.draw(dest)
		font=self.ui.font
		for pos,number in self.corners:
			font.drawCorner(dest,pos,number)
	def mouseUp(self,pos,button):
		if self.isOver(pos):
			self.clicked()
			return True
		return False
	def clicked(self):
		if self.callback is not None:
			self.callback(self.data)
	def getYS(self):
		return self.ys
