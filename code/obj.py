#!/usr/env python
from error import LoadError
from bmdl import BRenderModel
import pygame
from colorsys import rgb_to_hsv,hsv_to_rgb
import os
COLORWIDTH=8
class WavefrontModel:
	def __init__(self,filename=None):
		if filename is not None:
			self.load(filename)
	def load(self,filename):
		fop=open(filename,'r')	
		self.verts=[(0,0,0)] # Start from 1 my ass. IDIOTS. 
		#self.tris=[]
		self.colors={'DefaultColor':(255,255,255)}
		self.color_order=['DefaultColor']
		self.trispiles={}
		current_pile_name='DefaultColor'
		self.trispiles[current_pile_name]=[]
		current_pile=self.trispiles[current_pile_name]
		for i,line in enumerate(fop):
			self.linenumber=i
			if line[0:1]=='#':
				continue
			stuff=line.strip().split(' ',1)
			if len(stuff)==2:	
				command=stuff[0].lower()
				if command=='v':
					x,y,z=[float(x) for x in stuff[1].split(' ')][:3] # ignore w
					self.verts.append((x,y,z))
				elif command=='f':
					pieces=stuff[1].split(' ')
					if len(pieces)==3:
						verts,tex,normals=self.faceref(pieces)
						current_pile.append(verts)
					elif len(pieces)==4:
						verts,tex,normals=self.faceref(pieces)
						current_pile.append((verts[0],verts[1],verts[2]))
						current_pile.append((verts[0],verts[2],verts[3]))
				elif command=='usemtl':
					current_pile_name=stuff[1].strip()
					if current_pile_name not in self.trispiles:
						self.trispiles[current_pile_name]=[]
					current_pile=self.trispiles[current_pile_name]
					if current_pile_name not in self.colors:
						self.colors[current_pile_name]=(255,255,255) # default to white.
					if current_pile_name not in self.color_order:
						self.color_order.append(current_pile_name)
				elif command=='mtllib':
					try:
						self.loadMTL(stuff[1])
					except IOError:
						pass						# Couldn't load colors/textures. OH WELL. 

	def loadMTL(self,filename):
		current_name=None
		fop=open(filename,'r')
		for line in fop:
			if line[0:1]=='#':
				continue
			stuff=line.strip().split(' ',1)
			if len(stuff)==2:	
				command=stuff[0].lower()
				if command=='newmtl':
					current_name=stuff[1]
				elif command=='kd':
					if current_name is not None:
						r,g,b=[int(float(x)*255.0) for x in stuff[1].strip().split(' ')]
						self.colors[current_name]=(r,g,b)
						if current_name not in self.color_order:
							self.color_order.append(current_name)
	def dump(self):
		print 'Verts:',len(self.verts)
		print 'Tris:',len(self.tris)
	def faceref(self,pieces):
		verts,tex,normal=[],[],[]
		for piece in pieces:
			parts=piece.split('/')
			if len(parts)>3:
				raise LoadError('Too many parts in faceref, line %i' % (self.linenumber))
			if len(parts)==0:
				raise LoadError('Too few parts in faceref, line %i' % (self.linenumber))
			if len(parts)==1:
				verts.append(self.vref(int(parts[0])))
				tex.append(None)
				normal.append(None)
			elif len(parts)==2:
				verts.append(self.vref(int(parts[0])))
				tex.append(None) # TODO: Fix. Create tref?
				normal.append(None)
			elif len(parts)==3:
				verts.append(self.vref(int(parts[0])))
				tex.append(None) # TODO: Fix. Create tref?
				normal.append(None) # TODO: Fix. Create nref?
		return verts,tex,normal
	def vref(self,v):
		if v<0:
			return len(self.verts)+v
		else:
			return v
	def makeBMDL(self,statusfunc=None):
		bmdl=BRenderModel()
		bmdl.tris_normals=[]
		bmdl.filename='<JKL>'
		bmdl.normals=True
#		for x,y,z in self.verts:
#			bmdl.verts.append((x,y,z,0,0))
		width=float(len(self.color_order))
		for x,color in enumerate(self.color_order):
			u=(x+0.5)/width
			if color in self.trispiles:
				r,g,b=self.colors[color]
			else:
				r,g,b=(255,0,255) # default to white if we are missing this color.
			if statusfunc is not None:
				statusfunc('Converting %i verts in %s' % (len(self.trispiles[color]),color))
			for v1,v2,v3 in self.trispiles[color]:
				x,y,z=self.verts[v1]
				a=bmdl.happyVertex(x,y,z,u,0.5)
				x,y,z=self.verts[v2]
				b=bmdl.happyVertex(x,y,z,u,0.5)
				x,y,z=self.verts[v3]
				c=bmdl.happyVertex(x,y,z,u,0.5)
				bmdl.tris.append((a,b,c))
		if statusfunc is not None:
			statusstr='%i verts, %i tris' % (len(bmdl.verts),len(bmdl.tris))
			statusfunc(statusstr)
		return bmdl
	def makeTexture(self,palette_surf,enhance_color=True):
		size=(len(self.color_order)*COLORWIDTH,COLORWIDTH)
		surf=pygame.Surface(size,pygame.SWSURFACE,palette_surf)
		surf.set_palette(palette_surf.get_palette())
		for x,color in enumerate(self.color_order):
			r,g,b=self.colors[color]
			if enhance_color:
				h,s,v=rgb_to_hsv(r/255.0,g/255.0,b/255.0)
				s=min(1.0,s+0.1)
				r,g,b=[int(temp*255.0) for temp in hsv_to_rgb(h,s,v)]
			nearest=None
			ndiff=None
			for i,(nr,ng,nb) in enumerate(palette_surf.get_palette()):
				rdelta=r-nr
				gdelta=g-ng
				bdelta=b-nb
				diff=rdelta**2 + gdelta**2 + bdelta**2
				if nearest is None or diff<ndiff:
					ndiff=diff
					nearest=i
			surf.fill(nearest,(x*COLORWIDTH,0,COLORWIDTH,COLORWIDTH))
		return surf
class WavefrontModelTextured:
	def __init__(self,filename=None):
		if filename is not None:
			self.load(filename)
	def load(self,filename):
		fop=open(filename,'r')	
		self.verts=[(0,0,0)] # Start from 1 my ass. IDIOTS. 
		self.texverts=[(0,0,0)]
		self.colors={'DefaultColor':(255,255,255)}
		self.color_order=['DefaultColor']
		self.textures={}
		self.trispiles={}
		current_pile_name='DefaultColor'
		self.trispiles[current_pile_name]=[]
		current_pile=self.trispiles[current_pile_name]
		for i,line in enumerate(fop):
			self.linenumber=i
			if line[0:1]=='#':
				continue
			stuff=line.strip().split(' ',1)
			if len(stuff)==2:	
				command=stuff[0].lower()
				if command=='v':
					x,y,z=[float(x) for x in stuff[1].split(' ')][:3] # ignore w
					self.verts.append((x,y,z))
				elif command=='vt':
					u,v=[float(x) for x in stuff[1].split(' ')]
					self.texverts.append((u,v))
				elif command=='usemtl':
					current_pile_name=stuff[1].strip()
					if current_pile_name not in self.trispiles:
						self.trispiles[current_pile_name]=[]
					current_pile=self.trispiles[current_pile_name]
					if current_pile_name not in self.colors:
						self.colors[current_pile_name]=(255,255,255) # default to white.
					if current_pile_name not in self.color_order:
						self.color_order.append(current_pile_name)
				elif command=='f':
					pieces=stuff[1].split(' ')
					if len(pieces)==3:
						verts,tex,normals=self.faceref(pieces)
						current_pile.append(verts+tex)
					elif len(pieces)==4:
						verts,tex,normals=self.faceref(pieces)
						current_pile.append((verts[0],verts[1],verts[2],tex[0],tex[1],tex[2]))
						current_pile.append((verts[0],verts[2],verts[3],tex[0],tex[2],tex[3]))
				elif command=='mtllib':
					try:
						self.loadMTL(stuff[1])
					except IOError:
						pass						# Couldn't load colors/textures. OH WELL. 
					
	def loadMTL(self,filename):
		current_name=None
		fop=open(filename,'r')
		for line in fop:
			if line[0:1]=='#':
				continue
			stuff=line.strip().split(' ',1)
			if len(stuff)==2:	
				command=stuff[0].lower()
				if command=='newmtl':
					current_name=stuff[1]
				elif command=='kd':
					if current_name is not None:
						r,g,b=[int(float(x)*255.0) for x in stuff[1].strip().split(' ')]
						self.colors[current_name]=(r,g,b)
						if current_name not in self.color_order:
							self.color_order.append(current_name)
				elif command=='map_kd':
					filename=stuff[1]
					if not os.path.exists(filename):
						raise LoadError('Texture Missing: ' +filename)
					self.textures[current_name]=filename
	def dump(self):
		print 'Verts:',len(self.verts)
		print 'Tris:',len(self.tris)
		print 'Textures:'
		for texname in self.textures:
			r,g,b=self.colors[texname]
			print '  %s:%s (%i,%i,%i)' % (texname,self.textures[texname],r,g,b)
	def faceref(self,pieces):
		verts,tex,normal=[],[],[]
		for piece in pieces:
			parts=piece.split('/')
			if len(parts)>3:
				raise LoadError('Too many parts in faceref, line %i' % (self.linenumber))
			if len(parts)==0:
				raise LoadError('Too few parts in faceref, line %i' % (self.linenumber))
			if len(parts)==1:
				verts.append(self.vref(int(parts[0])))
				tex.append(None)
				normal.append(None)
			elif len(parts)==2:
				verts.append(self.vref(int(parts[0])))
				tex.append(self.tref(int(parts[1])))
				tex.append(None) # TODO: Fix. Create tref?
				normal.append(None)
			elif len(parts)==3:
				verts.append(self.vref(int(parts[0])))
				tex.append(self.tref(int(parts[1])))
				normal.append(None) # TODO: Fix. Create nref?
		return verts,tex,normal
	def vref(self,v):
		if v<0:
			return len(self.verts)+v
		else:
			return v
	def tref(self,t):
		if t<0:
			return len(self.texterts)+t
		else:
			return t
	def getTextureGroups(self):
		out=[]
		for key in self.trispiles:
			if len(self.trispiles[key])>0:
				out.append(key)
		return out
	def getTextureNames(self):
		out={}
		for key in self.trispiles:
			if len(self.trispiles[key])>0:
				out[self.textures[key]]=True
		return out.keys()
	def makeBMDL(self,pile,statusfunc=None):
		bmdl=BRenderModel()
		bmdl.tris_normals=[]
		bmdl.filename='<JKL>'
		bmdl.normals=True
#		for x,y,z in self.verts:
#			bmdl.verts.append((x,y,z,0,0))
		width=float(len(self.color_order))
		for pilename in self.trispiles:
			if self.textures.has_key(pilename) and self.textures[pilename]==pile:
				for v1,v2,v3,t1,t2,t3 in self.trispiles[pilename]:
					vs=[]
					for vi,ti in ((v1,t1),(v2,t2),(v3,t3)):
						x,y,z=self.verts[vi]
						u,v=self.texverts[ti]
						vs.append(bmdl.happyVertex(x,y,z,u,v))
					bmdl.tris.append(vs)
		return bmdl
