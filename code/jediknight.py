#!/usr/env python
from error import LoadError
from bmdl import BRenderModel 
from cStringIO import StringIO
from error import LoadError
from struct import unpack
import pygame
def preprocessLines(lines):
	out=[]
	for line in lines:
		if not line.startswith('#'):
			out.append(line.lower())
	return out
class TemplatePile:
	def __init__(self):
		self.templates={}
		pass
	def add(self,name,parent,attribs):
		temp={}
		if parent.lower()=='none':
			temp['parent']=None
		else:
			temp['parent']=parent
		temp['attribs']={}
		for attrib in attribs:
			n,v=attrib.split('=')
			temp['attribs'][n.lower()]=v
		self.templates[name]=temp
	def get(self,name,attrib):
		root=self.templates[name]
		lattrib=attrib.lower()
		if lattrib in root['attribs']:
			return root['attribs'][lattrib]
		else:
			return self.get(root['parent'],attrib)
	def __contains__(self,name):
		return name in self.templates
class JediKnightLevel:
	def __init__(self,filename=None):
		self.sectors=[]
		self.verts=[]
		self.texverts=[]
		self.surfaces=[]
		self.materials=[]
		self.colormaps=[]
		self.things=[]
		self.templates=TemplatePile()
		if filename is not None:
			self.load(filename)
	def load(self,filename):
		return self.loadFromObject(open(filename,'r'))			
	def loadFromObject(self,fop):
		lines=preprocessLines(fop.readlines())
		for i,line in enumerate(lines):
			if line.lower().startswith('section:'):	#WE GOTS A SECTION
				junk,section=line.strip().split(' ')
				#print 'SECTION:',section
				lsection=section.lower()
				if lsection=='sectors':
					self.loadSectors(lines,i)
				if lsection=='georesource':
					self.loadGeoResource(lines,i)
				if lsection=='materials':
					self.loadMaterials(lines,i)
				if lsection=='templates':
					self.loadTemplates(lines,i)
				if lsection=='things':
					self.loadThings(lines,i)
	def loadThings(self,lines,startline):
		things=[]
		for i,line in enumerate(lines[startline+1:]):
			lline=line.lower()
			if lline.startswith('section:') or lline.startswith('end'):
				self.things=things
				return # end of our sections
			pieces=lline.strip().split(' ')
			if lline.startswith('world things'):
				thingcount=int(pieces[2])-200
				for vline in lines[startline+i+2:startline+i+2+thingcount]:
					vpieces=vline.strip().split()
					thing={}
					thing['template']=vpieces[1]
					thing['pos']=[float(f) for f in vpieces[3:6]]
					thing['rot']=[float(f) for f in vpieces[6:9]]
					thing['sector']=int(vpieces[9])
					things.append(thing)
		self.things=things
	def loadTemplates(self,lines,startline):
		for i,line in enumerate(lines[startline+1:]):
			lline=line.lower()
			if lline.startswith('section:') or lline.startswith('end'):
				return # end of our sections
			pieces=lline.strip().split(' ')
			if lline.startswith('world templates'):
				tempcount=int(pieces[2])
				for vline in lines[startline+i+2:startline+i+2+tempcount]:
					vpieces=vline.strip().split()
					self.templates.add(vpieces[0],vpieces[1],vpieces[2:])
	def loadMaterials(self,lines,startline):
		materials=[]
		for i,line in enumerate(lines[startline+1:]):
			lline=line.lower()
			if lline.startswith('section:') or lline.startswith('end'):
				self.materials=materials
				return # end of our sections
			pieces=lline.strip().split(' ')
			if lline.startswith('world materials'):
				matcount=int(pieces[2])
				for vline in lines[startline+i+2:startline+i+2+matcount]:
					vpieces=vline.strip().split()
					materials.append(vpieces[1])
		self.materials=materials
	def loadSectors(self,lines,startline):
		sectors=[]
		current=None
		for i,line in enumerate(lines[startline+1:]):
			lline=line.lower()
			if lline.startswith('section:'):
				self.sectors=sectors
				return # end of our sections
			pieces=lline.strip().split(' ')
			if lline.startswith('world sectors'):
				x,x,sectorcount=lline.strip().split(' ')
				sectorcount=int(pieces[2])
				sectors=[]
				for j in range(sectorcount):
					sectors.append({})
			if lline.startswith('sector'):
				sectornumber=int(pieces[1])
				current=sectors[sectornumber]
			if lline.startswith('vertices'):
				vertcount=int(pieces[1])
				current['vertcount']=vertcount
				verts=[]
				for vline in lines[startline+i+2:startline+i+2+vertcount]:
					n,v=vline.strip().split()
					verts.append(int(v))
				current['verts']=verts
			if lline.startswith('surfaces'):
				first,count=int(pieces[1]),int(pieces[2])
				current['surface_first']=first
				current['surface_count']=count
			if lline.startswith('colormap'):
				current['colormap']=int(pieces[1])
		self.sectors=sectors
	def loadGeoResource(self,lines,startline):
		#print 'loadGeoResource'
		verts=[]
		texverts=[]
		surfs=[]
		colormaps=[]
		for i,line in enumerate(lines[startline+1:]):
			lline=line.lower()
			if lline.startswith('section:'):
				self.verts=verts
				self.texverts=texverts
				self.surfaces=surfs
				self.colormaps=colormaps
				return # end of our sections
			pieces=lline.strip().split(' ')
			if lline.startswith('world vertices'):
				vertcount=int(pieces[2])
				for vline in lines[startline+i+2:startline+i+2+vertcount]:
					n,x,y,z=vline.strip().split()
					verts.append([float(f) for f in x,y,z])
			if lline.startswith('world texture vertices'):
				texvertcount=int(pieces[3])
				for vline in lines[startline+i+2:startline+i+2+texvertcount]:
					n,u,v=vline.strip().split()
					texverts.append((float(u),float(v)))
			if lline.startswith('world colormaps'):
				colormapcount=int(pieces[2])
				for vline in lines[startline+i+2:startline+i+2+colormapcount]:
					n,name=vline.strip().split()
					colormaps.append(name)
			if lline.startswith('world surfaces'):
				surfcount=int(pieces[2])
				for vline in lines[startline+i+2:startline+i+2+surfcount]:
					parts=vline.strip().split()
					n,mat,sflag,flaces,geo,light,tex,adjoin,extralight,nverts=parts[0:10]
					surf={}
					surf['verts']=[]
					surf['material']=int(mat)
					surf['geo']=int(geo)
					for thing in parts[10:10+int(nverts)]:
						vert,texvert=[int(f) for f in thing.split(',')]
						surf['verts'].append((vert,texvert))
					surfs.append(surf)
#					n,u,v=vline.strip().split()
#					texverts.append((float(u),float(v)))
					
		self.verts=verts
		self.texverts=texverts
		self.surfaces=surfs
		self.colormaps=colormaps
	def getUsedTextures(self):
		used={}
		for surface in self.surfaces:
			used[surface['material']]=True
		return used.keys()
	def getMaterialName(self,id):
		return self.materials[id]
	def dump(self):
		print 'Sectors:'
		for sector in self.sectors:
			print sector
		print
		print 'Verts:'
		for vert in self.verts:
			print vert
		print
		print 'Tex Verts:'
		for texverts in self.texverts:
			print texverts
		print
		print 'Surfaces:'
		for surf in self.surfaces:
			print surf
		print
		print 'Materials:'
		for mat in self.materials:
			print mat
		print
		print 'Colormaps:'
		for cmap in self.colormaps:
			print cmap
		print
	def getColorMaps(self):
		return self.colormaps
	def TexAdj(self,surfsize,texid):
		u,v=self.texverts[texid]
		return [u/surfsize[0],1-v/surfsize[1]]
	def makeBMDL(self,textureonly=None,texturesize=[1.0,1.0]):
		bmdl=BRenderModel()
		bmdl.tris_normals=[]
		bmdl.filename='<JKL>'
		bmdl.normals=True
#		for x,y,z in self.verts:
#			bmdl.verts.append((-x,z,y,0,0)) 
		for sector in self.sectors:
			first=sector['surface_first']
			count=sector['surface_count']
			for surface in self.surfaces[first:first+count]:
				if surface['geo']==4:
					if textureonly is None or surface['material']==textureonly:
						verts=surface['verts']
						if len(verts)==3:
							a=bmdl.happyVertexR(*(self.verts[verts[0][0]]+self.TexAdj(texturesize,verts[0][1])))
							b=bmdl.happyVertexR(*(self.verts[verts[1][0]]+self.TexAdj(texturesize,verts[1][1])))
							c=bmdl.happyVertexR(*(self.verts[verts[2][0]]+self.TexAdj(texturesize,verts[2][1])))
							
							bmdl.tris.append((a,b,c))
						elif len(verts)>3:
							for i in range(1,len(verts)-1):
								a=bmdl.happyVertexR(*(self.verts[verts[0][0]]+self.TexAdj(texturesize,verts[0][1])))
								b=bmdl.happyVertexR(*(self.verts[verts[i][0]]+self.TexAdj(texturesize,verts[i][1])))
								c=bmdl.happyVertexR(*(self.verts[verts[i+1][0]]+self.TexAdj(texturesize,verts[i+1][1])))
								bmdl.tris.append((a,b,c))
		return bmdl
	def getLevelType(self):
		if 'ghostcam' in self.templates:
			return 'mots'
		else:
			return 'jk'
class ColorMapPalette:
	def __init__(self,filename=None):
		self.colors=[]
		if filename is not None:
			self.load(filename)
	def load(self,filename):
		return self.loadFromObject(open(filename,'rb'))
	def loadFromString(self,str):
		return self.loadFromObject(StringIO(str))
	def loadFromObject(self,fop):
		marker=fop.read(4)
		if marker!='CMP ':
			raise LoadError('Bad Marker')
		version,trans,padding=unpack('<2L52s',fop.read(60))
		if version not in (20,30):
			raise LoadError('Bad version. Wanted 20/30, got %i' % (version))
		for i in range(256):
			r,g,b=unpack('<3B',fop.read(3))
			self.colors.append((r,g,b))
	def __getitem__(self,i):
		return self.colors[i]
	def __len__(self):
		return len(self.colors)

class Material:
	def __init__(self,filename=None,palette=None):
		self.setPalette(palette)
		self.textures=[]
		if filename is not None:
			self.load(filename)
	def load(self,filename):
		return self.loadFromObject(open(filename,'rb'))
	def loadFromString(self,str):
		return self.loadFromObject(StringIO(str))
	def loadFromObject(self,fop):
		marker=fop.read(4)
		if marker!='MAT ':
			raise LoadError('Bad Marker')
		version,type,texcount,texcount2=unpack('<4L',fop.read(16))
		if version!=0x32:
			raise LoadError('Bad version')
		if type!=2:
			raise NotImplemented('Weird-ass color system')
		fop.read(8+48) # junk
		if type==2:
			for i in range(texcount):
				fop.read(4+4+16+8+4+4) # skipify
			for i in range(texcount):
				w,h,pad1,pad2,pad3,mipcount=unpack('<6L',fop.read(24))
				tex={'width':w,'height':h}
				data=fop.read(w*h)
				#open('out.dump','wb').write(data)
				tex['main']=data
				tex['mipmaps']=[]
				mw,mh=w,h
				for j in range(mipcount-1):
					mw,mh=[x/2 for x in (mw,mh)]
					data=fop.read(mw*mh)
					tex['mipmaps'].append((mw,mh,data))
				self.textures.append(tex)
	def getImage(self,number,mipmap=0):
		tex=self.textures[number]
		if mipmap==0:
			surf=pygame.image.fromstring(tex['main'],(tex['width'],tex['height']),'P')
			surf.set_palette(self.palette)
			return surf
		else:
			w,h,data=tex['mipmaps'][mipmap-1]
			surf=pygame.image.fromstring(data,(w,h),'P')
			surf.set_palette(self.palette)
			return surf
	def getPixels(self,number,mipmap=0):
		tex=self.textures[number]
		if mipmap==0:
			return tex['main']
		else:
			return tex['mipmaps'][mipmap-1][2]
	def getSize(self,number,mipmap=0):
		tex=self.textures[number]
		if mipmap==0:
			return (tex['width'],tex['height'])
		else:
			return tex['mipmaps'][mipmap-1][0:2]
	def setPalette(self,palette=None):
		if palette is None:
			self.palette=zip(range(256),range(256),range(256))
		else:
			self.palette=palette
def unnullterm(a):
	try:
		return a[0:a.index('\0')]
	except ValueError:
		return a
class GOB:
	def __init__(self,filename=None):
		if filename is not None:
			self.load(filename)
		else:
			self.files=[]
			self.filemap={}
			self.fop=None
			self.path='<NONE>'
	def load(self,filename):
		self.path=filename
		return self.loadFromObject(open(filename,'rb'))
	def loadFromObject(self,fop):
		self.files=[]
		self.filemap={}
		self.fop=fop
		marker,version=unpack('<3sb',fop.read(4))
		if marker!='GOB':
			raise LoadError('Bad marker')
		if version!=0x20:
			raise LoadError('Bad version')
		sizeoffset,numberoffset,filecount=unpack('<3l',fop.read(12))
		for i in range(filecount):
			offset,length,name=unpack('<2L128s',fop.read(136))
			fixedname=unnullterm(name)
			self.files.append((offset,length,fixedname))
			self.filemap[fixedname]=(offset,length)
	def dump(self):
		print 'GOB: '+self.path
	def getVirtual(self,filename):
		try:
			return open(filename,'rb').read()
		except IOError:
			return self.get(filename)
	def get(self,filename):
		offset,length=self.filemap[filename]
		self.fop.seek(offset)
		data=self.fop.read(length)
		return data
	def open(self,path):
		return StringIO(self.get(path))
	def filelist(self):
		return [x[2] for x in self.files]
