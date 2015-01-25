#!/usr/env python
# Change this stuff:
name='Katari Space Bongo'
author='Travis Wells'
origauthor='Travis Wells'
shortname='jkkatari' # out file will be shortname with a 'vxp' extension
jklmap='Katari.jkl' # Set to the filename of the map
uniqueid=0 # Set to 0 if you don't have one.
leveltype='mots'
install=True # set to True to install, False to leave in the current directory
imagemode=1 #Modes: 0: Palette look-up. Fast, but ugly. 1: Quantize, no dither. 2: Quantize, with dither
cache=True # Set to True to cache converted textures, False to convert every time
subdivide_threshold=0.5

motsgob=r'H:\SITHLARD\MotS\Resource'
jkgob=r'C:\Program Files\LucasArts\Jedi Knight\Resource'



#Don't change this stuff:
#JKL2VXP: Converts Dark Forces 2: Jedi Knight JKL levels to VXP expansions
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os
import sys
sys.path.append('code')
import zipfile
import pygame
from pygame.constants import *
import lib3dmm
from simpleMBMP import MBMP
from urllib import urlopen
from struct import pack
from idgenerator import GenerateID
import sockgui
from bmdl import BRenderModel
from jediknight import GOB,Material,ColorMapPalette,JediKnightLevel
from geofs import GeoFS
from tmap import TMAP
from vxpinstaller import installVXP
from error import SaveError,LoadError
from time import time
version='0.1'
def CreateVXPExpansionFromJediKnightMap(name,author,origauth,outfile,shortname,jklmap,uniqueid,leveltype,gobdirs,imagemode,cache,subdivide_threshold,progress,statusfunc=None,numtexfunc=None):
	created_files=[]
	try:
				def SaveCFG(outzip):
					cfg='Name=%s\nAuthor=%s\nOriginal Author=%s\nType=Portable\nContent=Props\nDate=%i\nGenerator=jkl2vxp %s\n' % (name,author,origauth,int(time()),version)
					outzip.writestr(shortname+'.cfg',cfg)
					progress()
				def Save3CN(outzip):
					if statusfunc is not None:
						statusfunc('Generating 3cn...')	
					tmpl=lib3dmm.Quad('TMPL',uniqueid,2)
					tmpl.setData('\x01\x00\x03\x03\x00\x00\x00\x40\x00\x00\x14\x00\x04\x00\x00\x00')
					tmpl.setString(name)
					actn=lib3dmm.Quad('ACTN',uniqueid)
					actn.setData('\x01\x00\x03\x03\x0A\x00\x00\x00')
					actn.setString('At Rest')
					ggcl=lib3dmm.Quad('GGCL',uniqueid)
					length=12+len(texturelist)*4
					data=pack('< 4B 2L l 3L 2H', 1,0,3,3,1,length,-1,8,0,163840,0,0)
					for i in range(len(texturelist)):
						data+=pack('<2H',i+1,0)
					data+=pack('< 2L',0,length)
					ggcl.setData(data)				
					glxf=lib3dmm.Quad('GLXF',uniqueid)
					glxf.setData('\x01\x00\x03\x03\x30\x00\x00\x00\x01\x00\x00\x00\xFC\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFC\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFC\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
					blankbmdl=lib3dmm.Quad('BMDL',uniqueid)
					blankbmdl.setData(pack('<4B 44s',1,0,3,3,''))

					cmtl=lib3dmm.Quad('CMTL',uniqueid)
					cmtl.setData(pack('<4B L',1,0,3,3,0))
					firstmtrl=lib3dmm.Quad('MTRL',uniqueid)
					mtrldata='\x01\x00\x03\x03\x00\x00\x00\x00\x00\x00\xFF\xFF\x00\x00\x17\x07\x00\x00\x32\x00'
					firstmtrl.setData(mtrldata)
					cmtl.addReference(firstmtrl,0)
					
					progress()
					mtrlrest=[]
					tmaprest=[]
					for i,textureid in enumerate(texturelist):
						if statusfunc is not None:
							text='Converting texture: %s' % (texturenames[i])
							statusfunc(text)
						surf=getTexture(textureid)
						tmap=TMAP()
						tmap.loadFromSurface(surf)
						mtrl=lib3dmm.Quad('MTRL',uniqueid+i+1)
						mtrl.setData(mtrldata)
						tmapquad=lib3dmm.Quad('TMAP',uniqueid+i+1)
						tmapquad.setData(tmap.getData())
						mtrl.addReference(tmapquad,0)
						mtrlrest.append(mtrl)
						tmaprest.append(tmapquad)
						cmtl.addReference(mtrl,i+1)
						progress()
					ggcm=lib3dmm.Quad('GGCM',uniqueid)
					ggcm.setData('\x01\x00\x03\x03\x01\x00\x00\x00\x08\x00\x00\x00\xFF\xFF\xFF\xFF\x04\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00')
					glbs=lib3dmm.Quad('GLBS',uniqueid)
					glbs.setData(pack('<4B 2L %is' % ((len(texturelist)+1)*2),1,0,3,3,2,len(texturelist)+1,''))
					glpi=lib3dmm.Quad('GLPI',uniqueid)
					glpidata=pack('<4B 2L h', 1,0,3,3,2,len(texturelist)+1,-1)
					for i in range(len(texturelist)):
						glpidata+=pack('<h',i)
					glpi.setData(glpidata)
					progress()
					bmdlrest=[]
					for i,textureid in enumerate(texturelist):
							if statusfunc is not None:
								text='Section: %i of %i (%s)' % (i+1,len(texturelist),texturenames[i])
								statusfunc(text)
							bmdl=jkmap.makeBMDL(textureid,texturesizes[textureid])
							bmdl.rescale((4.0,4.0,4.0))
							if subdivide_threshold not in (0,None):
								count=0
								while bmdl.subdivide(subdivide_threshold)!=0:
									count+=1
									if statusfunc is not None:
										text='Subdividing #%i. Tris: %i' % (count,bmdl.getTriangleCount())
										statusfunc(text)
							bmdlquad=lib3dmm.Quad('BMDL',uniqueid+i+1)
							bmdldata=bmdl.getData(True,bmdl.rescalef,bmdl.texrescalef)
							#if len(bmdldata)<=48: # ignore this error for now.
								
							bmdlquad.setData(bmdldata)
							bmdlrest.append(bmdlquad)
							progress()
					tmpl.addReference(actn,0)
					actn.addReference(ggcl,0)
					actn.addReference(glxf,0)
					tmpl.addReference(blankbmdl,0)
					tmpl.addReference(cmtl,0)
					tmpl.addReference(ggcm,0)
					tmpl.addReference(glbs,0)
					tmpl.addReference(glpi,0)
					for i,bmdl in enumerate(bmdlrest):
						tmpl.addReference(bmdl,i+1)
					vxp3cn=lib3dmm.c3dmmFileOut()
					vxp3cn.addQuad(tmpl)
					vxp3cn.addQuad(actn)
					vxp3cn.addQuad(ggcl)
					vxp3cn.addQuad(glxf)
					vxp3cn.addQuad(blankbmdl)
					vxp3cn.addQuad(cmtl)
					vxp3cn.addQuad(firstmtrl)
					for mtrl in mtrlrest:
						vxp3cn.addQuad(mtrl)
					for tmap in tmaprest:
						vxp3cn.addQuad(tmap)
					vxp3cn.addQuad(ggcm)						
					vxp3cn.addQuad(glbs)						
					vxp3cn.addQuad(glpi)
					for bmdlq in bmdlrest:
						vxp3cn.addQuad(bmdlq)
					progress()
					outzip.writestr(shortname+'.3cn',vxp3cn.getData())
					progress()

				def CreateMBMP():
					surf=pygame.Surface((72,72),SWSURFACE,palette_surf)
					surf.fill(30)
					surf.set_palette(palette_surf.get_palette())
					font=sockgui.Font('code/font.png')
					font.draw(surf,(2,2),'JKL map')
					font.draw(surf,(2,2+8), jklmap)
					#stuff here.
					return surf
				def Save3TH(outzip):
					if statusfunc is not None:
						statusfunc('Generating 3th...')	
					prth=lib3dmm.Quad('PRTH',uniqueid,mode=2)
					prth.setData(pack('<4B 4s L',1,0,3,3,'TMPL'[::-1],uniqueid))
					gokd=lib3dmm.Quad('GOKD',uniqueid)
					gokd.setData('\x01\x00\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x61\xC3\x00\x00\xFF\xFF\xFF\xFF')
					
					mbmp=lib3dmm.Quad('MBMP',uniqueid)
					mbmpdata=MBMP()
					mbmpdata.loadFromSurface(minisurf)
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
				def createPaletteLookup(inpal,outpal):
					table=[]
					for r,g,b in inpal:
						nearest=None
						ndiff=None
						for i,(nr,ng,nb) in enumerate(outpal):
							rdelta=r-nr
							gdelta=g-ng
							bdelta=b-nb
							diff=rdelta**2 + gdelta**2 + bdelta**2
							if nearest is None or diff<ndiff:
								ndiff=diff
								nearest=i
						table.append(nearest)
					return table
				def FixPalette(surf):
					newsurf=pygame.Surface(surf.get_size(),0,surf)
					newsurf.set_palette(palette_surf.get_palette())
					newsurf.blit(surf,(0,0)) #palette mapping should save us.
					return newsurf
				def QuantizeImage(infile,outfile,dither):
						import quantizer2.quantizer
						return quantizer2.quantizer.quantize(infile,outfile,'palette.bmp',dither)
				def getTexture(textureid):
						texname=jkmap.getMaterialName(textureid)
						cachename='cache/%s/mode%i/%s.bmp' % (leveltype,imagemode,texname)
						if cache:
							if os.path.exists(cachename):
								surf=pygame.image.load(cachename)
								texturesizes[textureid]=surf.get_size()
								return surf
						mat=Material()
						mat.loadFromObject(geofs.open('mat\\'+texname))
						mat.setPalette(defcmp)
						size=mat.getSize(0)
						texturesizes[textureid]=size
						if imagemode==0:
							data=mat.getPixels(0)
							str=''.join([chr(palettelookup[ord(c)]) for c in data])
							surf=pygame.image.fromstring(str,size,'P')
							surf.set_palette(palette_surf.get_palette())

						elif imagemode in (1,2):
							qfilename='quant_temp.bmp'
							presurf=mat.getImage(0)
							pygame.image.save(presurf,qfilename)
							if not QuantizeImage(qfilename,'quant_temp.tga',imagemode==2):
								raise SaveError('Quantizing image failed!')
							else:
								surf=pygame.image.load('quant_temp.tga')
								surf=FixPalette(surf)
							os.unlink('quant_temp.tga')
							os.unlink('quant_temp.bmp')
						if cache:
							pygame.image.save(surf,cachename)
						return surf
				if name=='':
					raise SaveError('No name')
				if author=='':
					raise SaveError('No author')
				if origauth=='':
					raise SaveError('No original author')
				if shortname=='':
					raise SaveError('No shortname')
				if jklmap=='':
					raise SaveError('No map')
				if leveltype not in ('jk','mots','auto'):
					raise SaveError('Unknown leveltype')
				if statusfunc is not None:
					statusfunc('Loading level...')	
				jkmap=JediKnightLevel(jklmap)
				texturelist=jkmap.getUsedTextures()
				texturesizes={}
				texturenames=[]
				ignorelist=[]#'00ctile1.mat']
				for tex in texturelist:
					texname=jkmap.getMaterialName(tex)
					if texname in ignorelist:
						texturelist.remove(tex)
					else:
						texturenames.append(texname)
				if numtexfunc is not None:
					numtexfunc(len(texturelist))
				#progress()
				if leveltype=='auto':
					leveltype=jkmap.getLevelType()
				geofs=GeoFS()
				for directory in gobdirs[leveltype]+gobdirs['all']:
					if os.path.isdir(directory):
						for filename in os.listdir(directory):
							lext=filename[-4:].lower()
							if lext in ('.gob','.goo'):
								geofs.addArchive(os.path.join(directory,filename),type='GOB')
				geofs.addCurrentDirectory()
				#geofs.dump()
				if cache:
					try:
						os.makedirs('cache/%s/mode%i' % (leveltype,imagemode))
					except OSError:
						pass
				if outfile=='':
					raise SaveError('No outfile')
				pygame.init()
				palette_surf=pygame.image.load('code/palette.bmp')
				if uniqueid is None or uniqueid==0:
					uniqueid=GenerateID()
					if uniqueid==0:
						raise SaveError("Couldn't get ID (or id==0)")

				firstmap=jkmap.getColorMaps()[0]
				defcmp=ColorMapPalette()
				try:
					defcmpfilename='misc\\cmp\\'+firstmap
					defcmp.loadFromObject(geofs.open(defcmpfilename))
				except IOError:
					raise LoadError('Couldn\'t find %s in any GOB/GOO' % (defcmpfilename))
				palettelookup=createPaletteLookup(defcmp.colors,palette_surf.get_palette())
				progress()
				minisurf=CreateMBMP()
				progress()
				if statusfunc is not None: 
					if len(texturelist)==1:
						statusfunc('1 map section')
					else:
						statusfunc('%i map sections' % (len(texturelist)))
				created_files.append(outfile)
				outvxp=zipfile.ZipFile(outfile,'w',zipfile.ZIP_DEFLATED)
				SaveCFG(outvxp)
				Save3CN(outvxp)
				Save3TH(outvxp)
				
				outvxp.close()
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
	gobdirs={}
	gobdirs['jk']=[jkgob]
	gobdirs['mots']=[motsgob]
	gobdirs['all']=['']
	CreateVXPExpansionFromJediKnightMap(name,author,origauthor,outfile,shortname,jklmap,uniqueid,leveltype,gobdirs,imagemode,cache,subdivide_threshold,NullProgress,Echo)
	if install:
		installVXP(outfile)
