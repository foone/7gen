#!/usr/env python
import pygame
from pygame.constants import *
from sockgui import *
from path import Path
class PathBox(Widget):
	def __init__(self,ui,pos=[0,0],size=[256,256]):
		Widget.__init__(self,ui,pos,size)
		self.pointbox=(size[0]-2,size[1]-2)
		self.pointpos=(pos[0]+1,pos[1]+1)
		self.border=BorderBox(ui,pos,size,(0,0,0),(240,240,240))
		self.linecolor=(120,120,120)
		self.pointcolor=(255,0,0)
		self.firstpointcolor=(0,0,255)
		self.psize=2
		self.points=[]
		self.addbutton=1
		self.delbutton=3
		self.background=None
	def getInnerSize(self):
		return self.pointbox
	def placepoint(self,point):
		px=self.pointpos[0]+(point[0]*self.pointbox[0])	
		py=self.pointpos[1]+(point[1]*self.pointbox[1])	
		return (px,py)
	def unplacepoint(self,point):
		px=(point[0]-self.pointpos[0])/float(self.pointbox[0])
		py=(point[1]-self.pointpos[1])/float(self.pointbox[1])
		return (px,py)
	def draw(self,dest):
		oldclip=dest.get_clip()
		dest.set_clip(self.border.getRect())
		self.border.draw(dest)
		if self.background is not None:
			dest.blit(self.background,self.pointpos)
		lastpoint=None
		for point in self.points:
			ppoint=self.placepoint(point)
			if lastpoint is not None:
				pygame.draw.line(dest,self.linecolor,lastpoint,ppoint)
			lastpoint=ppoint
		lastpoint=None
		for point in self.points:
			ppoint=self.placepoint(point)
			color=self.pointcolor
			psize=self.psize
			if lastpoint is None:
				color=self.firstpointcolor
				psize=psize+1
			dest.fill(color,(ppoint[0]-psize,ppoint[1]-psize,psize*2,psize*2))
			lastpoint=ppoint
		dest.set_clip(oldclip)
	def mouseDown(self,pos,button):
		if self.isOver(pos):
			if button==self.addbutton:
				self.points.append(self.unplacepoint(pos))
			elif button==self.delbutton:
				self.removeNearest(self.unplacepoint(pos))	
	def removeNearest(self,pos):
		smallest=None
		for point in self.points:
			dx=pos[0]-point[0]
			dy=pos[1]-point[1]
			dist=(dx*dx + dy*dy)
			if smallest is not None:
				p,pdist=smallest
				if dist<pdist:
					smallest=(point,dist)
			else:
				smallest=(point,dist)
		if smallest is not None:
			self.points.remove(smallest[0])
	def getPath(self):
		return Path(self.points)
	def clearPath(self,data=None): # Data is so this can be used as a button callback
		self.points=[]
	def setBackground(self,surf=None):
		self.background=surf
