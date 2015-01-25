#!/usr/env python
# Change this stuff:
name='OBJ Texture Test'
author='Travis Wells'
origauthor='Travis Wells'
shortname='objtexturetest1' # out file will be shortname with a 'vxp' extension
objfile='monkey2.obj' # Set to the filename of the map
uniqueid=0 # Set to 0 if you don't have one.
install=True # set to True to install, False to leave in the current directory



#Don't change this stuff:
#OBJ2VXP: Converts Wavefront OBJ files to v3dmm expansions
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
from obj import WavefrontModelTextured 
from tmap import TMAP
from vxpinstaller import installVXP
from error import SaveError,LoadError
from time import time
from basictexture import TextureConverter
version='0.1'
def CreateVXPExpansionFromOBJTextured(name,author,origauth,outfile,shortname,objfile,uniqueid,progress,statusfunc=None):
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
					length=12+len(texturenames)*4
					data=pack('< 4B 2L l 3L 2H', 1,0,3,3,1,length,-1,8,0,163840,0,0)
					for i in range(len(texturenames)):
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
					for i,texname in enumerate(texturenames):
						if statusfunc is not None:
							text='Converting texture: %s' % (texname)
							statusfunc(text)
						surf=texconv.getTexture(texname,changedir=False)
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
					glbs.setData(pack('<4B 2L %is' % ((len(texturenames)+1)*2),1,0,3,3,2,len(texturenames)+1,''))
					glpi=lib3dmm.Quad('GLPI',uniqueid)
					glpidata=pack('<4B 2L h', 1,0,3,3,2,len(texturenames)+1,-1)
					for i in range(len(texturenames)):
						glpidata+=pack('<h',i)
					glpi.setData(glpidata)
					progress()
					bmdlrest=[]
					for i,textureid in enumerate(texturenames):
							if statusfunc is not None:
								text='Section: %i of %i (%s)' % (i+1,len(texturenames),textureid)
								statusfunc(text)
							bmdl=obj.makeBMDL(textureid)
#							bmdl=jkmap.makeBMDL(textureid,texturesizes[textureid])
#							bmdl.rescale((4.0,4.0,4.0))
#							if subdivide_threshold not in (0,None):
#								count=0
#								while bmdl.subdivide(subdivide_threshold)!=0:
#									count+=1
#									if statusfunc is not None:
#										text='Subdividing #%i. Tris: %i' % (count,bmdl.getTriangleCount())
#										statusfunc(text)
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
					font.draw(surf,(2,2),'OBJ file')
					font.draw(surf,(2,2+8), objfile)
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
				if name=='':
					raise SaveError('No name')
				if author=='':
					raise SaveError('No author')
				if origauth=='':
					raise SaveError('No original author')
				if shortname=='':
					raise SaveError('No shortname')
				if objfile=='':
					raise SaveError('No map')
				if outfile=='':
					raise SaveError('No outfile')
				if statusfunc is not None:
					statusfunc('Loading OBJ...')	
				obj=WavefrontModelTextured(objfile)
				try:
					texturenames=obj.getTextureNames()
				except KeyError:
					raise SaveError('Missing texturegroups')
				if len(texturenames)==0:
					raise SaveError('No textures!')
				pygame.init()
				palette_surf=pygame.image.load('code/palette.bmp')
				if uniqueid is None or uniqueid==0:
					uniqueid=GenerateID()
					if uniqueid==0:
						raise SaveError("Couldn't get ID (or id==0)")
				progress()
				minisurf=CreateMBMP()
				progress()
				texconv=TextureConverter()
				if statusfunc is not None: 
					if len(texturenames)==1:
						statusfunc('1 group')
					else:
						statusfunc('%i groups' % (len(texturenames)))
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
	CreateVXPExpansionFromOBJTextured(name,author,origauthor,outfile,shortname,objfile,uniqueid,NullProgress,Echo)
	if install:
		installVXP(outfile)
