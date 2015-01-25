#!/usr/env python

# Make sure you set these.
data_dir=r'C:\Program Files\Microsoft Kids\3D Movie Maker'
author='Travis Wells'

# These get overwriten if you use a preset.
thid=8208
outpath='bongo'
shortname='bongo'
name='3dmm: bongo'
actor=True
tilesheet=True # Set to True to make a tilesheet
recompress=True
exepath=r"C:\Program Files\Microsoft Kids\3D Movie Maker\3DMOVIE.EXE" # Only needed if you have tilesheet or recompress on

#Don't change here down:
#actorextractor: Extracts 3dmm model-trees from the 3dmm datafiles
#Copyright (C) 2004 Travis Wells / Philip D. Bober
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys
sys.path.append('code')
import lib3dmm 
import os
from error import SaveError,LoadError,CompressedError
from struct import unpack,pack
from idgenerator import GenerateID 
from sources import MemorySource
from extract_presets import presets
from tmap import TMAP,palette
from time import time
from simpleMBMP import MBMP
from zipfs import fsopen,isZip,GetFileNameInZip
try:
	import decompress3dmm 
	have_decompress=True
except:
	have_decompress=False
import pygame
import cPickle
from basictexture import TextureConverter
version='0.7'
if len(sys.argv)>1:
	for entry in sys.argv:
		lentry=entry.lower()
		if lentry in presets:
			pres=presets[lentry]
			thid=pres['thid']
			shortname=outpath=pres['shortname']
			name=pres['name']
			actor=pres['actor']
def AddReferenced(quad,quadsource,bucket,addedlist,preprocess):
	if preprocess is not None:
		quad=preprocess('quad',quad)
	outquad=lib3dmm.Quad(quad['type'],quad['id'],quad['mode'],quad['string'])
	for ref in quad['references']:
		if preprocess is not None:
			nref=preprocess('ref',ref)
		else:
			nref=ref
		outquad.addFakeReference(nref['type'],nref['id'],nref['ref_id'])
	outquad.setSource(quad['source'])
	outquad.sortReferences()
	bucket.addQuad(outquad)
	for ref in quad['references']:
		quaddata=(ref['type'],ref['id'])
		fquad=quadsource.find_quad(*quaddata)
		if fquad is None:
			raise LoadError('Couldn\'t find leaf quad to copy: %s:%i' % quaddata)
		if quaddata not in addedlist:
			addedlist.append(quaddata)
			AddReferenced(fquad,quadsource,bucket,addedlist,preprocess)
def CopyTree(source,outfile,quadtype,quadid,preprocess=None):
	outmovie=lib3dmm.c3dmmFileOut()
	outmovie.should_sort=True
	startquad=source.find_quad(quadtype,quadid)
	if startquad is None:
		raise LoadError('Couldn\'t find starting quad to copy: %s:%i' % (quadtype,quadid))
	else:
		addedlist=[]
		AddReferenced(startquad,source,outmovie,addedlist,preprocess)
#	progress()
	outmovie.save(outfile)
#	progress()
def ExtractActorFromDatafiles(data_dir,author,thid,outpath,shortname,name,actor,myid,tilesheet,
		recompress,decomp,progress,statusfunc=None):
	global preview_mbmp
	created_files=[]
	preview_mbmp=None
	try:
		def thPreProcess(type,thing):
			global preview_mbmp
			mything=dict(thing)
			if type in ('quad','ref'):
				if thing['type'] in ('TMTH','PRTH') and type=='quad':
					newth=pack('<4B4sL',1,0,3,3,'LPMT',myid)
					mything['source']=MemorySource(newth)
				elif type=='quad' and thing['type']=='MBMP' and tilesheet:
					preview_mbmp=thing['source'].get()
				mything['id']=myid
			return mything
		def Copy3TH():
			if actor:
				orig_file=os.path.join(data_dir,'actor.3th')
				quad='TMTH'
			else:
				orig_file=os.path.join(data_dir,'prop.3th')
				quad='PRTH'
			thpath=os.path.join(outpath,shortname+'.3th')
			progress()
			thfile=lib3dmm.c3dmmFile(orig_file)
			progress()
			startquad=thfile.find_quad(quad,thid)
			if startquad is None:
				raise LoadError('Couldn\'t find starting quad!')
			data=startquad['source'].get()
			progress()
			created_files.append(thpath)
			CopyTree(thfile,thpath,quad,thid,thPreProcess)
			progress()
			quadr,id=unpack('<4sL',data[4:])
			return quadr[::-1],id
		def cnPreProcess(type,thing):
			mything=thing
			if recompress and type=='quad' and thing['mode']&4:
				if statusfunc is not None:
					statusfunc('Decompressing %s:%i' % (thing['type'],thing['id']))
				mything=dict(thing)
				mything['mode']=thing['mode']^4 #remove compression
				mything['source']=MemorySource(decomp.decompress(mything['source'].get()))
			if thing['type']=='TMPL':
				mything=dict(thing)
				mything['id']=myid
			elif type=='quad' and thing['type']=='TMAP' and tilesheet:
				tiles.append((thing['id'],thing['source'].get()))
			return mything
		def Copy3CN(quad,id):
			orig_file=os.path.join(data_dir,'TMPLS.3CN')
			cnpath=os.path.join(outpath,shortname+'.3cn')
			progress()
			cnfile=lib3dmm.c3dmmFile(orig_file)
			progress()
			progress()
			created_files.append(cnpath)
			CopyTree(cnfile,cnpath,quad,id,cnPreProcess)
			progress()
		def GenerateCFG():
			cfgpath=os.path.join(outpath,shortname+'.cfg')
			created_files.append(cfgpath)
			if actor:
				content='Actors'
			else:
				content='Props'
			cfg='Name=%s\nAuthor=%s\nOriginal Author=Microsoft\nType=Portable\nContent=%s\nDate=%i\nGenerator=actorextractor %s\n' % (name,author,content,int(time()),version)
			fop=open(cfgpath,'w')
			fop.write(cfg)
			fop.close()
			progress()
		def MakeMakeScript():
			pypath=os.path.join(outpath,'makevxp.py')
			created_files.append(pypath)
			fop=open(pypath,'w')
			fop.write("""#!/usr/bin/env python
shortname='%s'
tilemap=%s
import os
if tilemap:
	import sys
	sys.path.append('../bin')
	sys.path.append('../code')
	import actorextractor
	actorextractor.UpdateTMAPs(shortname)
os.system('..\code\zip -9 -X %%s.vxp %%s.cfg %%s.3cn %%s.3th' %% ((shortname,)*4))""" % (shortname,tilesheet)) 
			progress()
		def SurfSorter(a,b):
			aw,ah=a[1].get_size()
			bw,bh=b[1].get_size()
			return cmp(bw*bh,aw*ah)
		def MakeTileSheet():
			if len(tiles)==0:
				raise SaveError('No textures found!')
			tilepath=os.path.join(outpath,shortname+'.bmp')
			previewpath=os.path.join(outpath,'preview_'+shortname+'.bmp')
			datpath=os.path.join(outpath,shortname+'.tsl')
			mbmp=MBMP()
			try:
				mbmp.loadFromString(preview_mbmp)
			except:
				decompstr=decomp.decompress(preview_mbmp)
				mbmp.loadFromString(decompstr)
			surf=mbmp.getSurface()
			pygame.image.save(surf,previewpath)
			surfs=[]
			mw,mh=0,0
			pal=[]
			surfinfo=[]
			for id,tile in tiles:
				tmap=TMAP()
				try:
					tmap.loadTMAPFromString(tile)
				except CompressedError:
					decompstr=decomp.decompress(tile)
					tmap.loadTMAPFromString(decompstr)
				surfs.append((id,tmap.surf))
				w,h=tmap.surf.get_size()
				mw=max(mw,w)
				mh=max(mh,h)
				pal=tmap.surf.get_palette()
			per_row=6
			tsize=(mw*per_row,mh*len(surfs)/(per_row-1))
			ubersurf=pygame.Surface(tsize,0,8)
			ubersurf.set_palette(pal)
			xm,ym=0,0
			surfs.sort(SurfSorter)
			x,y=0,0
			linemaxheight=0
			shade=0
			for i in range(len(surfs)):
				id,surf=surfs[i]
				w,h=surf.get_size()
				linemaxheight=max(linemaxheight,h)
				ubersurf.blit(surf,(x,y))
				surfinfo.append((id,x,y,w,h))
				xm=max(xm,x+w)
				ym=max(ym,y+h)
				x+=w
				if x+w>=tsize[0]:
					x=0
					y+=linemaxheight
					linemaxheight=0
			lastsurf=pygame.Surface((xm,ym),0,8)
			lastsurf.set_palette(pal)
			lastsurf.blit(ubersurf,(0,0),(0,0,xm,ym))
			created_files.append(tilepath)
			pygame.image.save(lastsurf,tilepath)
			created_files.append(datpath)
			fop=open(datpath,'w')
			fop.write('#TMAP ID to surface location lookup table.\n')
			fop.write('#ActorExtractor version %s\n' % (version))
			fop.write('# ID     X       Y         W       H\n')
			for stuff in surfinfo:
				fop.write('% -8i% -8i% -8i% -8i% -8i\n' % stuff)
			fop.close()
		if tilesheet and not decomp:
			raise SaveError('No decompressor given!')
		tiles=[]
		try:
			os.mkdir(outpath)
		except OSError,oe:
			pass
		created_files.append(outpath)
		if not myid:
			myid=GenerateID()
		if statusfunc is not None:
			statusfunc('Creating CFG...')
		GenerateCFG()
		if statusfunc is not None:
			statusfunc('Creating 3TH...')
		cnquad,cnid=Copy3TH()
		if statusfunc is not None:
			statusfunc('Creating 3CN...')
		Copy3CN(cnquad,cnid)
		if statusfunc is not None:
			statusfunc('Creating tilesheet...')
		if tilesheet:
			MakeTileSheet()
		if statusfunc is not None:
			statusfunc('Creating script...')
		MakeMakeScript()
		created_files=[] # Clear file list, so they won't be nuked
		return True
	finally:
		try:
			files=[]
			dirs=[]
			for file in created_files:
				if os.path.isdir(file):
						dirs.append(file)
				else:
					files.append(file)
			for file in files:
				try:
					os.unlink(file)
				except:
					pass
			for dirfile in dirs:
				try:
					os.rmdir(dirfile)
				except OSError:
					pass
		except OSError:
			pass
class TMAPReplacer:
	def __init__(self,tmapmap,surface):
		self.surface=surface
		self.tmapmap=tmapmap
	def __call__(self,type,thing):
		if type=='quad':
			if thing['type']=='TMAP':
				if thing['id'] in self.tmapmap:
					x,y,w,h=self.tmapmap[thing['id']]
#					print 'TMAP: ',thing['id'],x,y,w,h
					tmap=TMAP()
					tmap.loadFromSurface(self.surface.subsurface(x,y,w,h))
					thing['source']=MemorySource(tmap.getData())
					thing['mode']=0
			return thing
		else:
			return thing
class VerySimpleMBMPReplacer:
	def __init__(self,surface):
		self.surface=surface
	def __call__(self,type,thing):
		if type=='quad':
			if thing['type']=='MBMP':
					mbmp=MBMP()
					mbmp.loadFromSurface(self.surface)
					thing['source']=MemorySource(mbmp.getData())
					thing['mode']=0
			return thing
		else:
			return thing
def UpdateTMAPs(shortname):
	pygame.init()
	texconv=TextureConverter(pygame.image.load('../code/palette.bmp'))
	tiledata=open(shortname+'.tsl').readlines()
	idtable={}
	for line in tiledata:
		if not line.startswith('#'):
			try:
				id,x,y,w,h=[int(v) for v in line.strip().split()]
				idtable[id]=(x,y,w,h)
			except ValueError:
				pass
	# update .3cn
	cnfile=lib3dmm.c3dmmFile(shortname+'.3cn')
	cnfile.convertFileSources()
	majors=cnfile.getMajorQuads()
	if len(majors)!=1:
		raise LoadError('Expected 1 major quad, got %i' %( len(majors)))
	qtype=majors[0]['type']
	qid=majors[0]['id']
	outfile=shortname+'.3cn'
#	surface=pygame.image.load(shortname+'.bmp')
	surface=texconv.getTexture(shortname+'.bmp')
	CopyTree(cnfile,outfile,qtype,qid,TMAPReplacer(idtable,surface))
	#update .3th
	thfile=lib3dmm.c3dmmFile(shortname+'.3th')
	thfile.convertFileSources()
	majors=thfile.getMajorQuads()
	if len(majors)!=1:
		raise LoadError('Expected 1 major quad, got %i' %( len(majors)))
	qtype=majors[0]['type']
	qid=majors[0]['id']
	outfile=shortname+'.3th'
	surface=texconv.getTexture('preview_'+shortname+'.bmp')
	CopyTree(thfile,outfile,qtype,qid,VerySimpleMBMPReplacer(surface))
	pass
if __name__=='__main__':
	if tilesheet:
		if not have_decompress:
			raise SaveError('No decompressor')
		decomp=decompress3dmm.Decompressor(exepath)
		pygame.init()
	def NullProgress():
		pass
	ExtractActorFromDatafiles(data_dir,author,thid,outpath,shortname,name,actor,GenerateID(),tilesheet,decomp,NullProgress)

