#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


import pygame
from error import LoadError,CompressedError
from struct import pack,unpack
import cStringIO
from cStringIO import StringIO
palette=None
def loadPalette():
	global palette
	palette=[]
	surf=pygame.image.load('code/palette.bmp')
	palette=surf.get_palette()

#	fop=open('3dmm.palette','r')
#	for line in fop:
#		dummy,r,g,b=line.split(',')
#		palette.append((int(r),int(g),int(b)))
class TMAP:
	def __init__(self,filename=None):
		self.surf=None
		if filename:
			self.load(filename)
	def loadFromSurface(self,surf):
		if surf.get_bitsize()!=8:
			raise LoadError('Not an 8bit surface')
		self.surf=surf
	def load(self,filename):
		if filename[-5:].lower()=='.tmap':
			self.loadTMAP(filename)
		else:
			self.loadImage(filename)
	def loadTMAP(self,filename):
		return loadTMAPFromObject(open(filename,'rb'))
	def loadTMAPFromString(self,str):
		return self.loadTMAPFromObject(StringIO(str))
	def loadTMAPFromObject(self,fop):
		if palette==None: loadPalette()
		strmarker=fop.read(4)
		marker=unpack('<4B',strmarker)
		if strmarker in ('KCDC','KCD2'):
			raise CompressedError,'Section is compressed'
		if marker not in ((1,0,3,3),(1,0,5,5)):	raise LoadError('Bad marker')
		junk=fop.read(8)
		w,h=unpack('<2H',fop.read(4))
		fullsize=unpack('<L',fop.read(4))[0]
		surf=pygame.image.fromstring(fop.read(w*h),(w,h),'P',True)
		surf.set_palette(palette)
		self.surf=surf
	def loadImage(self,filename):
		try:
			surf=pygame.image.load(filename)
		except pygame.error:
			raise LoadError('Pygame could not load this image')
		if surf.get_bitsize()!=8:
			raise LoadError('Not an 8bit surface')
		self.surf=surf
	def save(self,filename,asTMAP=False):
		if asTMAP:
			fop=open(filename,'wb')
			self.saveTMAP(fop)
			fop.close()
		else:
			pygame.image.save(self.surf,filename)
	def getData(self):
		strio=cStringIO.StringIO()
		self.saveTMAP(strio)
		return strio.getvalue()
	def saveTMAP(self,fop):
		w,h=self.surf.get_size()
		fop.write(pack('<4BH2BL2HL',1,0,3,3,w,3,2,0,w,h,0))
		fop.write(pygame.image.tostring(self.surf,'P',True))
#		raise LoadError('NOT IMPLEMENTS')


