#!/usr/env python

# Change this stuff:
name='Arka Texture'
author='Travis Wells'
origauth='Travis Wells'
shortname='arkatexture' # out file will be shortname with a 'vxp' extension
image='sleep2.bmp'
uniqueid=0 # Set to 0 if you don't have one.
dither=True # Set to False if you are doing sprites, True for photos

#Don't change this stuff:
#BMP2VXP: Converts BMP files to VXP expansions
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
from tmap import TMAP
import lib3dmm
from urllib import urlopen
from struct import pack
from simpleMBMP import MBMP
from idgenerator import GenerateID
from error import SaveError
from time import time
version='0.6'
def CreateVXPExpansionFromBMP(name,author,origauth,outfile,shortname,image,uniqueid,progress,dither=True):
	created_files=[]
	try:
				if name=='':
					raise SaveError('No name')
				if author=='':
					raise SaveError('No author')
				if origauth=='':
					raise SaveError('No orig. author')
				if shortname=='':
					raise SaveError('No shortname')
				if image=='':
					raise SaveError('image')
				if outfile=='':
					raise SaveError('No outfile')
				def SaveCFG(outzip):
					cfg='Name=%s\nAuthor=%s\nOriginal Author=%s\nType=Portable\nContent=Textures\nDate=%i\nGenerator=bmp2vxp %s\n' % (name,author,origauth,int(time()),version)
					outzip.writestr(shortname+'.cfg',cfg)
					progress()
				def Save3CN(outzip):
					tmapdata=TMAP()
					tmapdata.loadFromSurface(texsurf)
				#	tmapdata.save('out.tmap',True)
					tmapquad=lib3dmm.Quad('TMAP',uniqueid)
					tmapquad.setData(tmapdata.getData())
					mtrlquad=lib3dmm.Quad('MTRL',uniqueid,2)
					mtrlquad.addReference(tmapquad,0)
					mtrlquad.setData('\x01\x00\x03\x03\x00\x00\x00\x00\x00\x00\xFF\xFF\x00\x00\x15\x07\x00\x00\x32\x00')
					vxp3cn=lib3dmm.c3dmmFileOut()
					vxp3cn.addQuad(mtrlquad)
					vxp3cn.addQuad(tmapquad)
					progress()
					outzip.writestr(shortname+'.3cn',vxp3cn.getData())
					progress()
				def Save3TH(outzip):
					mtth=lib3dmm.Quad('MTTH',uniqueid,mode=2)
					mtth.setData(pack('<4B 4s L',1,0,3,3,'MTRL'[::-1],uniqueid))
					gokd=lib3dmm.Quad('GOKD',uniqueid)
					gokd.setData('\x01\x00\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x61\xC3\x00\x00\xFF\xFF\xFF\xFF')
					mbmp=lib3dmm.Quad('MBMP',uniqueid)
					mbmpdata=MBMP()
					mbmpdata.loadFromSurface(minisurf)
					mbmp.setData(mbmpdata.getData())
					mtth.addReference(gokd,0)
					gokd.addReference(mbmp,65536)
					vxp3th=lib3dmm.c3dmmFileOut()
					vxp3th.addQuad(mtth)
					vxp3th.addQuad(gokd)
					vxp3th.addQuad(mbmp)
					progress()
					outzip.writestr(shortname+'.3th',vxp3th.getData())
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
				pygame.init()
				palette_surf=pygame.image.load('code/palette.bmp')
				if uniqueid is None or uniqueid==0:
					uniqueid=GenerateID()
					if uniqueid==0:
						raise SaveError("Couldn't get ID (or id==0)")
				texsurf=pygame.image.load(image)
				if texsurf.get_bitsize()!=8 or (not PalettesMatch(texsurf)):
					progress()
					# Try to quantize
					try:
						if not QuantizeImage(image,'temp.tga',dither):
							raise SaveError('Quantizing image failed!')
						else:
							progress()
							texsurf=pygame.image.load('temp.tga')
							progress()
							texsurf=FixPalette(texsurf)
							os.unlink('temp.tga')
							progress()
					except ImportError:
						raise SaveError('Bad palette, and missing quantizer!')
				else:
					progress()
					progress()
					progress()
					progress()

				minisurf=pygame.transform.scale(texsurf,(64,30))
				progress()
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
if __name__=='__main__':
	outfile=shortname+'.vxp'
	CreateVXPExpansionFromBMP(name,author,origauth,outfile,shortname,image,uniqueid,NullProgress,dither)
