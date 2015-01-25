#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


from error import LoadError
from struct import unpack,pack
from array import array
from zipfs import fsopen
def getCName(str):
	a=''
	for letter in str:
		if ord(letter)==0:
			return a
		a+=letter
	return a
	
class Quake2Model:
	def __init__(self,filename=None):
		self.verts=[]
		self.tris=[]
		self.texcoords=[]
		self.texverts=[]
		self.frames=[]
		self.framenames=[]
		self.filename=None
		self.frameoffsets={}
		self.vertremap=[]
		self.mappedverts={}
		self.new_vert_tex=[]
		if filename is not None:
			self.load(filename)
	def load(self,filename):
		self.verts=[]
		self.tris=[]
		self.texcoords=[]
		self.texverts=[]
		self.frames=[]
		self.framenames=[]
		self.frameoffsets={}
		self.vertremap=[]
		self.new_vert_tex=[]
		self.mappedverts={}
		fop=fsopen(filename,'rb')
		if fop.read(4)!='IDP2':
			raise LoadError('Bad header')
		if unpack('<l',fop.read(4))[0] !=8:
			raise LoadError('Bad version number.')
		texsize=unpack('<2l',fop.read(4*2))
		self.framesize=framesize=unpack('<l',fop.read(4))[0]
		self.nums=unpack('<llllll',fop.read(4*6))
		num_skins,num_verts,num_texcoords,num_tris,num_gl,num_frames=self.nums
		self.offsets=offsets=unpack('<llllll',fop.read(4*6))

		#print 'verts: %i tris: %i texcoords: %i' % (num_verts,num_tris,num_texcoords)

		#read texcoords
		fop.seek(offsets[1])
		for i in range(num_texcoords):
			t,s=unpack('<2H',fop.read(2*2))
			u=t/float(texsize[0])
			v=s/float(texsize[1])
			self.texcoords.append((u,v))
		self.texverts=[[] for x in range(num_verts)]
		#read tris
		fop.seek(offsets[2])
		for i in range(num_tris):
			v1,v2,v3,tx1,tx2,tx3=unpack('<6H',fop.read(6*2))
			self.texverts[v1].append(tx1)
			self.texverts[v2].append(tx2)
			self.texverts[v3].append(tx3)
			v1t=self.getVert(v1,tx1)
			v2t=self.getVert(v2,tx2)
			v3t=self.getVert(v3,tx3)
			self.tris.append((v1t,v2t,v3t))
#		print '%i texverts' % (len(self.texverts))
		i=0
		for v in self.texverts:
			same=True
			num=len(v)
			for j in range(num-1):
				if v[j]!=v[1]:
					same=False
#			if not same:
#				print '%i: %i coords !' % (i,num)
			i+=1		

		for i in range(num_frames):
			offset=offsets[3] + (i*framesize)
			fop.seek(offset + (6*4)) # skip scale/translate
			name=getCName(fop.read(16)) # chop off null?
			self.framenames.append(name)
			self.frameoffsets[name]=offset
		self.filename=filename
	def getVert(self,vertex,texture):
		id=(vertex,texture)
		if id in self.mappedverts:
			return self.mappedverts[id]
		else:
			number=len(self.vertremap)
			self.vertremap.append((vertex,texture))
			self.mappedverts[id]=number
			self.new_vert_tex.append(self.texcoords[texture])
			return number
	def listFrames(self):
		return self.framenames
	def getVerticesForFrame(self,frame):
		offset=self.frameoffsets[frame]
		return self.GetVertsFromOffset(offset)
	def GetVertsForFrameIndex(self,framei):
		offset=self.offsets[3] + (framei*self.framesize)	
		return self.GetVertsFromOffset(offset)
	def GetVertsFromOffset(self,offset):
		verts=[]
		fop=fsopen(self.filename,'rb')
		fop.seek(offset)	
		scale=unpack('<fff',fop.read(4*3))
		translate=unpack('<fff',fop.read(4*3))
		num_verts=self.nums[1]
		fop.read(16) # frame name, which we already know.
		for i in range(num_verts):
			coords=unpack('<BBBB',fop.read(4))
			coords=[a*b for a,b in zip(coords,scale)] #Rescale
			coords=[a+b for a,b in zip(coords,translate)] #translate
			verts.append(coords)
		return [(verts[i][0],verts[i][1],verts[i][2],self.texcoords[x][0],self.texcoords[x][1]) for i,x in self.vertremap]
			
