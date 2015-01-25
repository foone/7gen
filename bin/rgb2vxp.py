#!/usr/env python

# Change this stuff:
name='Light Blue Fun Timexxxx'
author='Travis Wells'
shortname='litebluebg' # out file will be shortname with a 'vxp' extension
color=(155,204,224) # Set to the Red,Green,Blue of the color you want. 
uniqueid=0 # Set to 0 if you don't have one.

#Don't change this stuff:
#RGB2VXP: Converts BMP files to VXP expansions
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
from error import SaveError
from time import time
version='0.2'
def CreateVXPExpansionFromColor(name,author,outfile,shortname,color,uniqueid,progress):
	created_files=[]
	try:
				if name=='':
					raise SaveError('No name')
				if author=='':
					raise SaveError('No author')
				if shortname=='':
					raise SaveError('No shortname')
				try:
					r,g,b=color
					if r<0 or r>255:
						raise SaveError('R channel out of bounds!')
					if g<0 or g>255:
						raise SaveError('G channel out of bounds!')
					if b<0 or b>255:
						raise SaveError('B channel out of bounds!')
				except ValueError:
					raise SaveError('Bad color')
				if outfile=='':
					raise SaveError('No outfile')
				def SaveCFG(outzip):
					cfg='Name=%s\nAuthor=%s\nOriginal Author=%s\nType=Portable\nContent=Backgrounds\nDate=%i\nGenerator=rgb2vxp %s\n' % (name,author,author,int(time()),version)
					outzip.writestr(shortname+'.cfg',cfg)
					progress()
				def Save3CN(outzip):
					bkgd=lib3dmm.Quad('BKGD',uniqueid,2)
					bkgd.setData('\x01\x00\x03\x03\x0A\x5C\xF8\x77')
					bkgd.setString(name)
					bds=lib3dmm.Quad('BDS ',uniqueid)
					bds.setData('\x01\x00\x03\x03\x00\x00\x01\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x44\x4E\x53\x4D\xFF\x4F\x00\x00')
					cam=lib3dmm.Quad('CAM ',uniqueid)
					cam.setData('\x01\x00\x03\x03\x00\x00\x01\x00\x00\x00\x88\x13\xbd\x16\x5f\x4e\x4a\xb7\x5a\x00\x00\x00\x00\x00\x23\x13\x11\x00\x27\x18\x00\x00\x00\x00\x00\x00\x2c\x01\xff\xff\x94\xfd\xff\xff\xf4\xff\x00\x00\xc5\xff\xff\xff\xcc\xfe\x00\x00\x6e\x02\x00\x00\x27\x18\x00\x00\x6c\x28\xa9\x00\xcf\xda\x15\x00\x94\xa8\x17\x00\xc8\xa0\x38\x00\x00\x00\x00\x00\xfb\xdb\x1f\x00')
					mbmp=lib3dmm.Quad('MBMP',uniqueid)
					mbmp.setDataFromFile('code/templates/rgbtemplate.MBMP')
					zbmp=lib3dmm.Quad('ZBMP',uniqueid,4) # compressed
					zbmp.setDataFromFile('code/templates/rgbtemplate.ZBMP')

					gllt=lib3dmm.Quad('GLLT',uniqueid)
					gllt.setData('\x01\x00\x03\x03\x38\x00\x00\x00\x02\x00\x00\x00\x24\xce\x00\x00\x00\x00\x00\x00\xbd\x97\x00\x00\xc9\x44\x00\x00\x26\xe4\x00\x00\x8c\xa2\xff\xff\xc3\x78\xff\xff\x0e\x74\x00\x00\xba\xb7\x00\x00\x1a\xa2\x38\x00\x33\xf2\x9a\x00\x06\x34\x5a\x00\x00\x00\x01\x00\x01\x00\x00\x00\xdb\x11\xff\xff\x00\x00\x00\x00\x27\xa2\xff\xff\x3a\xe0\xff\xff\xda\xf0\x00\x00\xa0\x50\x00\x00\x4d\x58\x00\x00\xac\x56\x00\x00\xef\x1f\xff\xff\x19\x21\x65\x02\xf2\x30\x71\x01\x44\x8b\xaa\xfb\x00\x00\x01\x00\x01\x00\x00\x00')
					glcr=lib3dmm.Quad('GLCR',uniqueid)
					glcrdata=str(open('code/templates/rgb_template.GLCR','rb').read())
					glcrdata=glcrdata[0:772]+pack('<3B',b,g,r)+glcrdata[772+3:]
					glcr.setData(glcrdata)
					
					bkgd.addReference(bds,0)
					bkgd.addReference(cam,0)
					bkgd.addReference(glcr,0)
					bkgd.addReference(gllt,0)
					cam.addReference(mbmp,0)
					cam.addReference(zbmp,0)
					vxp3cn=lib3dmm.c3dmmFileOut()
					vxp3cn.addQuad(bkgd)
					vxp3cn.addQuad(bds)
					vxp3cn.addQuad(cam)
					vxp3cn.addQuad(mbmp)
					vxp3cn.addQuad(zbmp)
					vxp3cn.addQuad(glcr)
					vxp3cn.addQuad(gllt)
					progress()
					outzip.writestr(shortname+'.3cn',vxp3cn.getData())
					progress()
				def CreateMBMP():
					surf=pygame.Surface((128,72),SWSURFACE,palette_surf)
					surf.fill(30)
					surf.set_palette(palette_surf.get_palette())
					font=sockgui.Font('code/font.png')
					font.draw(surf,(2,2),'Custom color')
					font.draw(surf,(2,2+8), 'Red:   %i (%2.0f%%)' % (r,(r/255.0)*100))
					font.draw(surf,(2,2+16),'Green: %i (%2.0f%%)' % (g,(g/255.0)*100))
					font.draw(surf,(2,2+24),'Blue:  %i (%2.0f%%)' % (b,(b/255.0)*100))
					#stuff here.
					return surf
				def Save3TH(outzip):
					bkth=lib3dmm.Quad('BKTH',uniqueid,mode=2)
					bkth.setData(pack('<4B 4s L',1,0,3,3,'BKGD'[::-1],uniqueid))
					cath=lib3dmm.Quad('CATH',uniqueid)
					cath.setData(pack('<4B 4s L',1,0,3,3,'CAM '[::-1],0))
					gokd=lib3dmm.Quad('GOKD',uniqueid)
					gokd.setData('\x01\x00\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x61\xC3\x00\x00\xFF\xFF\xFF\xFF')
					
					mbmp=lib3dmm.Quad('MBMP',uniqueid)
					mbmpdata=MBMP()
					mbmpdata.loadFromSurface(minisurf)
					mbmp.setData(mbmpdata.getData())
					bkth.addReference(cath,0)
					bkth.addReference(gokd,0)
					cath.addReference(gokd,0)
					gokd.addReference(mbmp,65536)
					vxp3th=lib3dmm.c3dmmFileOut()
					vxp3th.addQuad(bkth)
					vxp3th.addQuad(cath)
					vxp3th.addQuad(gokd)
					vxp3th.addQuad(mbmp)
					progress()
					outzip.writestr(shortname+'.3th',vxp3th.getData())
					progress()
				pygame.init()
				palette_surf=pygame.image.load('code/palette.bmp')
				if uniqueid is None or uniqueid==0:
					uniqueid=GenerateID()
					if uniqueid==0:
						raise SaveError("Couldn't get ID (or id==0)")

				minisurf=CreateMBMP()
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
	CreateVXPExpansionFromColor(name,author,outfile,shortname,color,uniqueid,NullProgress)
