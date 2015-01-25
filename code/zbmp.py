#!/usr/env python
#7gen: Does various stuff with v3dmm.
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
from error import LoadError
from struct import pack,unpack
from cStringIO import StringIO
import pygame
class ZBMP:
	def __init__(self,filename=None):
		if filename:
			self.load(filename)
	def load(self,filename):
		return self.loadFromObject(open(filename,'rb'))
	def loadFromString(self,str):
		return self.loadFromObject(StringIO(str))
	def loadFromObject(self,fop):
		marker=unpack('<4B',fop.read(4))
		if marker not in ((1,0,3,3),(1,0,5,5)):
			raise LoadError('Invalid marker.')
		padding,w,h=unpack('<LHH',fop.read(8))
		self.size=(w,h)
		self.data=list(unpack('<%iH' % (w*h),fop.read(2*w*h)))
	def loadFromSurface(self,surf):
		w,h=self.size=surf.get_size()
		pixels=pygame.image.tostring(surf,'RGB')
		self.data=[0] * (w*h)
		for i in range(w*h):
			r,g,b=[ord(x) for x in pixels[i*3:i*3+3]]
			self.data[i]=r*256+g
	def __getitem__(self,key):
		x,y=key
		return self.get(x,y)
	def __setitem__(self,key,newval):
		x,y=key
		return self.set(x,y,newval)
	def get(self,x,y):
		line=y*self.size[0]
		return self.data[line+x]
	def set(self,x,y,v):
		line=y*self.size[0]
		self.data[line+x]=v
	def save(self,filename):
		return self.saveToObject(open(filename,'wb'))
	def getData(self):
		fop=StringIO()
		self.saveToObject(fop)
		return fop.getvalue()
	def saveToObject(self,fop):
		w,h=self.size
		fop.write(pack('< 4B L 2H',1,0,3,3,0,w,h))
		for v in self.data:
			fop.write(pack('<H',v))
