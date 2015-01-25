#!/usr/env python
single_frame={}

# Change this stuff: NOTE: a filename like foo.zip:bar.md2 means "the file bar.md2 inside the zip foo.zip"

# Name of expansion.
name='Doom Demon'

# Your name
author='Travis Wells'		

# Original author of the model
orig_author='jDoom project'

# out file will be shortname with a 'vxp' extension
shortname='doomdemon'	

# Set to 0 if you don't have one.
uniqueid=0

#Filename of MD2
md2file='models\Monst\Demon\Demon.md2' 

#Filenames of textures
md2textures=[
'models\\Monst\\Demon\Skindemon.pcx', 'models\\Monst\\Demon\Skindemondie.pcx', 
'models\\Monst\\Demon\Skindemonpain.pcx', 'models\\Monst\\Demon\Skindemonpain2.pcx']

#Animations to export (Use md2Info.py to get a list)
md2animations=['Idle','Run','Bite','Pain']

#File to use for the thumbnail in 3dmm and v3dmm Manager.
previewimage='models/demon.png'

# Set to True if you want the VXP to be installed, False otherwise.
install=True

# Set to True to dither textures, False otherwise.
dither=True

# Set to True to make an actor, False to make a prop
actor=True

# Size to scale md2 to. 1.0 is no scaling, 0.5 is halfsize, 2.0 is double, etc. 0.15 seems about right for most models.
scaling=0.05

#Single frames: Let you turn a animation into a frame. Useful for those q2 models with huge idle animations. Example:
#single_frame['idle']=11 # For the "Idle" animation, only use frame 11 (Remove the first # to make this active)



#Don't change this stuff:-----------------------------------------------------
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys
sys.path.append('code')
from GetFrameNames import GetAnimations
from md2 import Quake2Model
from bmdl import BRenderModel
import os
import zipfile
import pygame
from pygame.constants import *
import lib3dmm
from tmap import TMAP
from simpleMBMP import MBMP
from urllib import urlopen
from struct import pack
from idgenerator import GenerateID
import sockgui
from vxpinstaller import installVXP
from zipfs import fsopen,isZip,GetFileNameInZip
from error import SaveError
from time import time
version='0.3'
def CreateVXPExpansionFromMD2(name,author,orig_author,outfile,shortname,md2file,
		md2textures,animations,preview,dither,actor,scaling,single_frames,uniqueid,progress,statusfunc=None):
	created_files=[]
	try:
		if name=='':
			raise SaveError('No name')
		if author=='':
			raise SaveError('No author')
		if shortname=='':
			raise SaveError('No shortname')
		if outfile=='':
			raise SaveError('No outfile')
		if orig_author=='':
			raise SaveError('no orig author')
		scaling=float(scaling)
		pygame.init()
		palette_surf=pygame.image.load('code/palette.bmp')
		if uniqueid is None or uniqueid==0:
			uniqueid=GenerateID()
			if uniqueid==0:
				raise SaveError("Couldn't get ID (or id==0)")
		def SaveCFG(outzip):
			if actor:
				content='Actors'
			else:
				content='Props'
			cfg='Name=%s\nAuthor=%s\nOriginal Author=%s\nType=Portable\nContent=%s\nDate=%i\nGenerator=md2_to_vxp %s\n' % (name,author,orig_author,content,int(time()),version)
			outzip.writestr(shortname+'.cfg',cfg)
			progress()
		def Save3TH(outzip,previewimg):
			if actor:
				prth=lib3dmm.Quad('TMTH',uniqueid,mode=2)
			else:
				prth=lib3dmm.Quad('PRTH',uniqueid,mode=2)
			prth.setData(pack('<4B 4s L',1,0,3,3,'TMPL'[::-1],uniqueid))
			gokd=lib3dmm.Quad('GOKD',uniqueid)
			gokd.setData('\x01\x00\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x61\xC3\x00\x00\xFF\xFF\xFF\xFF')
			
			mbmp=lib3dmm.Quad('MBMP',uniqueid)
			mbmpdata=MBMP()
			mbmpdata.loadFromSurface(previewimg)
			mbmp.setData(mbmpdata.getData())
			prth.addReference(gokd,0)
			gokd.addReference(mbmp,65536)
			vxp3th=lib3dmm.c3dmmFileOut()
			vxp3th.addQuad(prth)
			vxp3th.addQuad(gokd)
			vxp3th.addQuad(mbmp)
			progress()
			outzip.writestr(shortname+'.3th',vxp3th.getData())
			progress()
		def Save3CN(outzip):
			tmpl=lib3dmm.Quad('TMPL',uniqueid,2)
			if actor:
				tmpl.setData('\x01\x00\x03\x03\x00\x00\x00\x40\x00\x00\x14\x00\x01\x00\x00\x00')
			else:
				tmpl.setData('\x01\x00\x03\x03\x00\x00\x00\x40\x00\x00\x14\x00\x04\x00\x00\x00')
			tmpl.setString(name)
			laterquads=[]
			blankbmdl=lib3dmm.Quad('BMDL',uniqueid)
			blankbmdl.setData(pack('<4B 44s',1,0,3,3,''))
			tmpl.addReference(blankbmdl,0)
			i=1
			for animname,bframes in bmdlanims:
				for stuff in bframes:
					frame,number,bmdl,junk=stuff
					bmdlQuad=lib3dmm.Quad('BMDL',uniqueid+i)
					bmdlQuad.setData(bmdl.getData(False,bmdl.rescalef*scaling,bmdl.texrescalef))
					laterquads.append(bmdlQuad)
					tmpl.addReference(bmdlQuad,i)
					stuff[3]=i
					i+=1
			i=0
			for texture in textures:
				cmtl=lib3dmm.Quad('CMTL',uniqueid+i)
				cmtl.setData(pack('<4B L',1,0,3,3,0))
				mtrl=lib3dmm.Quad('MTRL',uniqueid+i)
				mtrl.setData('\x01\x00\x03\x03\x00\x00\x00\x00\x00\x00\xFF\xFF\x00\x00\x17\x07\x00\x00\x32\x00')
				tmapquad=lib3dmm.Quad('TMAP',uniqueid+i)
				tmap=TMAP()
				tmap.loadFromSurface(texture)
				tmapquad.setData(tmap.getData())
				cmtl.addReference(mtrl,0)
				cmtl.addReference(mtrl,1)
				mtrl.addReference(tmapquad,0)
				tmpl.addReference(cmtl,i)
				laterquads.append(cmtl)
				laterquads.append(mtrl)
				laterquads.append(tmapquad)
				i+=1
			glbs=lib3dmm.Quad('GLBS',uniqueid)
			glbs.setData('\x01\x00\x03\x03\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00')
			tmpl.addReference(glbs,0)
			laterquads.append(glbs)
			glpi=lib3dmm.Quad('GLPI',uniqueid)
			glpi.setData('\x01\x00\x03\x03\x02\x00\x00\x00\x02\x00\x00\x00\xff\xff\x00\x00')
			tmpl.addReference(glpi,0)
			laterquads.append(glpi)
			ggcm=lib3dmm.Quad('GGCM',uniqueid)
			ggcmdata=pack('<4B5l',1,0,3,3,1,4+len(textures)*4,-1,4,len(textures))
			for i in range(len(textures)):
				ggcmdata+=pack('<l',i)
			ggcmdata+=pack('<ll',0,4+len(textures)*4)
			ggcm.setData(ggcmdata)
			tmpl.addReference(ggcm,0)
			laterquads.append(ggcm)
			i=0
			for animname,bframes in bmdlanims:
				actn=lib3dmm.Quad('ACTN',uniqueid+i)
				actn.setData('\x01\x00\x03\x03\x0a\x00\x00\x00')
				actn.setString(animname)
				ggcl=lib3dmm.Quad('GGCL',uniqueid+i)
				ggcldata=pack('<4b4l',1,0,3,3,len(bframes),len(bframes)*16,-1,8)
				for frame in bframes:
					framelookup=69
					ggcldata+=pack('<2l4h',0,163840,0,0,frame[3],1)
				for j in range(len(bframes)):
					ggcldata+=pack('<2l',j*16,16)
				ggcl.setData(ggcldata)
				glxf=lib3dmm.Quad('GLXF',uniqueid+i)
	#			glxfdata=pack('<4Bll',1,0,3,3,48,len(bframes))
	#			for x in bframes:
	#				glxfdata+='\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	#			glxf.setData(glxfdata)
				glxf.setData('\x01\x00\x03\x03\x30\x00\x00\x00\x02\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
				actn.addReference(ggcl,0)	
				actn.addReference(glxf,0)	
				tmpl.addReference(actn,i)
				laterquads.append(actn)	
				laterquads.append(ggcl)	
				laterquads.append(glxf)	
				i+=1
			tmpl.sortReferences()
			vxp3cn=lib3dmm.c3dmmFileOut()
			vxp3cn.addQuad(tmpl)
			vxp3cn.addQuad(blankbmdl)
			for quad in laterquads:
				vxp3cn.addQuad(quad)
			progress()
			outzip.writestr(shortname+'.3cn',vxp3cn.getData())
			progress()
		def PalettesMatch(othersurf):
			return othersurf.get_palette()==palette_surf.get_palette()
		def QuantizeImage(infile,outfile,dither):
			import quantizer2.quantizer
			return quantizer2.quantizer.quantize(infile,outfile,'palette.bmp',dither)
		def FixPalette(surf):
			newsurf=pygame.Surface(surf.get_size(),0,surf)
			newsurf.set_palette(palette_surf.get_palette())
			newsurf.blit(surf,(0,0)) #palette mapping should save us.
			return newsurf
		def GetTexture(filename):
			gdither=dither
			if filename[0] in ('-','+'):
				gdither=filename[0]=='+'
				filename=filename[1:]
			if (not isZip(filename)) and (not os.path.exists(filename)):
				raise SaveError('Image %s does not exist!' % (filename))
			try:
				texsurf=pygame.image.load(fsopen(filename,'rb'))
				if texsurf.get_bitsize()==8 and  PalettesMatch(texsurf):
					return texsurf
			except pygame.error:
				pass
			progress()
			# Try to quantize
			try:
				if isZip(filename):
					short,ext=os.path.splitext(GetFileNameInZip(filename))
					qfilename='quant_temp'+ext
					fs=open(qfilename,'wb')
					fs.write(fsopen(filename,'rb').read())
					fs.close()
				else:
					qfilename=filename
				if not QuantizeImage(qfilename,'quant_temp.tga',gdither):
					if isZip(filename):
						os.unlink(qfilename)
					raise SaveError('Quantizing image failed!')
				else:
					progress()
					texsurf=pygame.image.load('quant_temp.tga')
					progress()
					texsurf=FixPalette(texsurf)
					os.unlink('quant_temp.tga')
					if isZip(filename):
						os.unlink(qfilename)
					progress()
					return texsurf
			except ImportError:
				if isZip(filename):
					os.unlink(qfilename)
				raise SaveError('Bad palette, and missing quantizer!')
		previewimg=GetTexture(preview)
		textures=[]
		for texture in md2textures:
			try:
				if statusfunc is not None:
					statusfunc('Converting texture %s' % (os.path.basename(texture)))
				textures.append(GetTexture(texture))
			except pygame.error:
				raise SaveError('Failed to convert '+texture)
		frames,anims=GetAnimations(md2file)
		models=[]
		md2animations=[x.lower() for x in animations]
		singlef={}
		for key in single_frames:
			singlef[key.lower()]=single_frames[key]
		md2=Quake2Model(md2file)
		bmdlanims=[]
		for anname in md2animations:
			for animname,animdata in anims:
				if animname.lower()==anname:
					bframes=[]
					first=0
					last=len(animdata)
					if anname in singlef:
						first=singlef[anname]
						last=first+1
					framecount=len(animdata[first:last])
					for i,(frame,number) in enumerate(animdata[first:last]):
						verts=md2.GetVertsForFrameIndex(number)
						bmdl=BRenderModel() # no filename
						bmdl.loadFromMD2(md2,frame)
						bframes.append([frame,number,bmdl,0])
						if statusfunc is not None:
							statusfunc('Converting animation %s (Frame %i of %i)' % (anname,i+1,framecount))
					bmdlanims.append((anname,bframes))
					progress()
		
		created_files.append(outfile)
		outvxp=zipfile.ZipFile(outfile,'w',zipfile.ZIP_DEFLATED)
		if statusfunc is not None:
			statusfunc('Making 3TH...')
		Save3TH(outvxp,previewimg)
		if statusfunc is not None:
			statusfunc('Making CFG...')
		SaveCFG(outvxp)
		if statusfunc is not None:
			statusfunc('Making 3CN...')
		Save3CN(outvxp)
		progress()
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
def NullProgress():
	pass
def Echo(msg):
	print msg
if __name__=='__main__':
	outfile=shortname+'.vxp'
	CreateVXPExpansionFromMD2(name,author,orig_author,outfile,shortname,md2file,md2textures,
			md2animations,previewimage,dither,actor,scaling,single_frame,uniqueid,NullProgress,Echo)
	if install:
		installVXP(outfile)

