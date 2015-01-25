#!/usr/bin/env python

# Change this stuff:
name='Gilia plant'
author='Travis Wells'
origauth='Travis Wells'
shortname='giliaplant'
objfile='gilia.obj'
uniqueid=0 # set to 0 if you don't have one
enhance_color=True
#OBJ2VXP: Converts simple OBJ files to VXP expansions
#Copyright (C) 2004-2005 Travis Wells / Philip D. Bober
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
import lib3dmm
from urllib import urlopen
from struct import pack
from simpleMBMP import MBMP
from tmap import TMAP
from idgenerator import GenerateID
from error import SaveError
import cPickle as pickle
import sockgui
from obj import WavefrontModel 
from time import time
version='0.4'
def CreateVXPExpansionFromOBJ(name,author,origauth,outfile,shortname,objfile,uniqueid,progress,enhance_color,statusfunc=None):
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
		if objfile=='':
			raise SaveError('No OBJ')
		if outfile=='':
			raise SaveError('No outfile')
		def SaveCFG(outzip):
			cfg='Name=%s\nAuthor=%s\nOriginal Author=%s\nType=Portable\nContent=Props\nDate=%i\nGenerator=obj2vxp %s\n' % (name,author,origauth,int(time()),version)
			outzip.writestr(shortname+'.cfg',cfg)
			progress()
		def Save3CN(outzip):
			if statusfunc is not None:
				statusfunc('Creating 3CN...')
			vxp3cn=pickle.load(open('code/templates/objtemplate3cn.pl3','rb'))
			for quad in vxp3cn.quads:
				if quad.type=='TMPL':
					quad.setID(uniqueid)
					quad.setString(name)
				if quad.type=='BMDL' and quad.source.get_length()==0:
					if statusfunc is not None:
						statusfunc('Creating BMDL...')
					bmdl=modelobj.makeBMDL(statusfunc)
					quad.setData(bmdl.getData(True,bmdl.rescalef/25.0,bmdl.texrescalef))
				if quad.type=='TMAP':
					tmapdata=TMAP()
					tmapdata.loadFromSurface(texture)
					quad.setData(tmapdata.getData())
			progress()
			outzip.writestr(shortname+'.3cn',vxp3cn.getData())
			progress()
		def Save3TH(outzip):
			if statusfunc is not None:
				statusfunc('Creating 3TH...')
			vxp3th=pickle.load(open('code/templates/objtemplate3th.pl3','rb'))
			for quad in vxp3th.quads:
				quad.setID(uniqueid)
				for id,otherquad in quad.references:
					otherquad.setID(uniqueid)
				if quad.type=='MBMP':
					mbmpdata=MBMP()
					mbmpdata.loadFromSurface(minisurf)
					quad.setData(mbmpdata.getData())
				if quad.type=='PRTH':
					quad.setData(pack('<4B 4s L',1,0,3,3,'TMPL'[::-1],uniqueid))
			progress()
			outzip.writestr(shortname+'.3th',vxp3th.getData())
			progress()
		if uniqueid is None or uniqueid==0:
			uniqueid=GenerateID()
			if uniqueid==0:
				raise SaveError("Couldn't get ID (or id==0)")
		def CreateMBMP():
			surf=pygame.Surface((72,72),pygame.SWSURFACE,palette_surf)
			surf.fill(30)
			surf.set_palette(palette_surf.get_palette())
			font=sockgui.Font('code/font.png')
			font.draw(surf,(2,2),'OBJ file')
			font.draw(surf,(2,2+8), name)
			#stuff here.
			return surf
		if statusfunc is not None:
			statusfunc('Loading OBJ...')
		modelobj=WavefrontModel(objfile)
		if statusfunc is not None:
			statusfunc('Creating textures...')
		pygame.init()
		palette_surf=pygame.image.load('code/palette.bmp')
		minisurf=CreateMBMP()
		texture=modelobj.makeTexture(palette_surf,enhance_color)
		#pygame.image.save(texture,'out.bmp')
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
	CreateVXPExpansionFromOBJ(name,author,origauth,outfile,shortname,objfile,uniqueid,NullProgress,enhance_color)

