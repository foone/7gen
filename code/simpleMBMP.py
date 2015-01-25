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
class MBMP:
	def __init__(self,filename=None):
		self.surf=None
		if filename:
			self.load(filename)
	def loadFromSurface(self,surf):
		if surf.get_bitsize()!=8:
			raise LoadError('Not an 8bit surface')
		self.surf=surf
	def loadFromString(self,data):
		return self.loadMBMPFromObject(cStringIO.StringIO(data))
	def load(self,filename):
		if filename[-5:].lower()=='.mbmp':
			self.loadMBMPFromFile(filename)
		else:
			self.loadImage(filename)
	def loadMBMPFromFile(self,filename):
		return self.loadMBMPFromObject(open(filename,'rb'))
	def loadMBMPFromObject(self,fop):
		if palette==None: loadPalette()
		strmarker=fop.read(4)
		marker=unpack('<4B',strmarker)
		if strmarker in ('KCDC','KCD2'):
			raise CompressedError,'Section is compressed'
		if marker not in ((1,0,3,3),(1,0,5,5)):	raise LoadError('Bad marker')
		junk,x,y,w,h,filesize=unpack('<6l',fop.read(24))
		w-=x
		h-=y
		linelengths=unpack('<%iH' % (h),fop.read(2*h))
		surf=pygame.Surface((w,h),pygame.SWSURFACE,8)
		surf.set_palette(palette)
		for line in range(h):
			if linelengths[line]!=0:
				linepos=0
				xpos=0
				while linepos<linelengths[line]:
					skip,linesize=unpack('<2B',fop.read(2))
					xpos+=skip
					linepos+=2
					linedata=fop.read(linesize)
					for x in range(linesize):
						surf.set_at((xpos,line),ord(linedata[x]))
						xpos+=1
					linepos+=linesize
		self.surf=surf
	#	raise LoadError('Not Implements')
	def getSurface(self):
		return self.surf
	def loadImage(self,filename):
		try:
			surf=pygame.image.load(filename)
		except pygame.error:
			raise LoadError('Pygame could not load this image')
		if surf.get_bitsize()!=8:
			raise LoadError('Not an 8bit surface')
		self.surf=surf
	def save(self,filename,asMBMP=False):
		if asMBMP:
			fop=open(filename,'wb')
			self.saveMBMP(fop)
			fop.close()
		else:
			pygame.image.save(self.surf,filename)
	def getData(self):
		strio=cStringIO.StringIO()
		self.saveMBMP(strio)
		return strio.getvalue()
	def saveMBMP(self,fop):
		w,h=self.surf.get_size()
		data=''
		linelengths=[0] * h
		surfdata=pygame.image.tostring(self.surf,'P',False)
		dn=0
		while dn<w*h:
			linesize=0
			lastentry=0
			cdn=dn
			while cdn<(dn+w):
				n=0
				n=min(255,w-lastentry)
				skip=0
				lastentry+=n
				data+=pack('<2B',skip,n)
				data+=surfdata[cdn:cdn+n]
				cdn+=n
				linesize+=n+2
			linelengths[dn//w]=linesize
			dn+=w
		xpos,ypos=0,0 # TODO: Implement this stuff?
		right=xpos+w
		bottom=ypos+h
		predata=''
		for length in linelengths:
			predata+=pack('<H',length)
		filesize=28 + len(predata) + len(data)
		fop.write(pack('<4B L 2l 2l L',1,0,3,3, 0, xpos,ypos, right,bottom,filesize))
		fop.write(predata)
		fop.write(data)



