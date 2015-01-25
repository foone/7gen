#!/usr/env python
from math import sqrt
import pygame
class Path:
	def __init__(self,points=None,filename=None):
		self.points=[]
		if points is not None:
			for px,py in points:
				self.points.append((float(px),float(py)))
		self.calcLength()
		if filename is not None:
			self.load(filename)
	def calcLength(self):
		lastpoint=None
		dist=0.0
		ptotal=[0.0]
		for point in self.points:
			if lastpoint is not None:
				dx=point[0]-lastpoint[0]
				dy=point[1]-lastpoint[1]
				dist+=sqrt(dx*dx + dy*dy)
				ptotal.append(dist)
			lastpoint=point
			
		self.length=dist
		self.ptotal=ptotal
	def getLength(self):
		return self.length
		
	def setPoints(self,pointlist):
		self.points=[]
		for a,b in pointlist:
			self.points.append((float(a),float(b)))
		self.calcLength()
	def load(self,filename):
		self.points=[]
		for line in open(filename,'r'):
			a,b=line.strip().split(' ')
			pf=(float(a),float(b))
			self.points.append(pf)
		self.calcLength()
	def render(self,size,palette=None,drawlines=True,drawpoints=True,pointsize=2):
		surf=pygame.Surface(size,0,8)
		if palette is not None:
			surf.set_palette(palette)
			bg=12
			linecolor=16
			pointcolor=68
		else:
			surf.set_palette([(255,255,255),(0,0,0),(127,127,127)])
			bg=0
			linecolor=1
			pointcolor=2
		surf.fill(bg)
		if drawlines:
			lastpoint=None
			for point in self.points:
				px=point[0]*size[0]
				py=point[1]*size[1]
				if lastpoint is not None:
					pygame.draw.line(surf,linecolor,lastpoint,(px,py))
				lastpoint=(px,py)
		if drawpoints:
			for point in self.points:
				px=point[0]*size[0]
				py=point[1]*size[1]
				surf.fill(pointcolor,(px-pointsize,py-pointsize,pointsize*2,pointsize*2))
		return surf
	def getPointByPercent(self,amt):
		return self.getPointByDist((amt/100.0)*(self.getLength()))
	def getPointByDist(self,dist):
		fi=None
		fidist=None
		for i,pdist in enumerate(self.ptotal):
			if pdist<=dist and self.ptotal[i+1]>=dist:
				fi=i
				fidist=pdist
				break
		if fi is None: return None
		p1=self.points[fi]
		p2=self.points[fi+1]
		pdx=p1[0]-p2[0]
		pdy=p1[1]-p2[1]
		ldist=sqrt(pdx*pdx + pdy*pdy)
		adist=dist-fidist
		amt=(adist/float(ldist))
		x=p1[0]*(1-amt) + p2[0]*amt
		y=p1[1]*(1-amt) + p2[1]*amt
		return (x,y)
