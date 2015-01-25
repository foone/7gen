#!/usr/env python
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
from zipfile import ZipFile
import os
from cStringIO import StringIO
from GetFrameNames import GetAnimations
import re
def ReturnPossibleTextures(filelist,prepath=''):
	supportedexts=('.pcx','.png','.bmp','.gif','.jpg','.jpeg')
	skipfiles=('base.pcx','weapon.pcx')
	textures=[]
	for name in filelist:
		lfile=os.path.basename(name).lower()
		ext=os.path.splitext(lfile)[1]
		if ext in supportedexts and lfile[-6:]!='_i.pcx':
			if lfile not in skipfiles:
				textures.append(prepath+name)
	return textures
def GetAuthor(data):
	lines=data.split('\n')
	author=None
	for line in lines:
		stuff=line.split(':',2)
		if len(stuff)==2:
			try:
				junk=stuff[0].lower().index('author')
				author=stuff[1].strip()
			except ValueError:
				pass
	return author
if __name__=='__main__':
	if len(sys.argv)>1:
		ziplist=sys.argv[1:]
	else:
		ziplist=os.listdir('.')
	for zipname in ziplist:
		ext=os.path.splitext(zipname)[1].lower()
		good=False
		author=None
		if ext=='.zip':
			zip=ZipFile(zipname,'r')
			tris_name=None
			weapon_name=None
			for file in zip.namelist():
				filename=os.path.basename(file)
				lfile=filename.lower()
				if lfile=='tris.md2':
					tris_name=zipname+':'+file
				if lfile=='weapon.md2':
					weapon_name=file
				if lfile[-4:]=='.txt':
					author=GetAuthor(zip.read(file))
			textures=ReturnPossibleTextures(zip.namelist(),zipname+':')
			good=True
		elif ext=='.md2':
			tris_name=zipname
			zpath=os.path.dirname(zipname)
			textures=ReturnPossibleTextures(os.listdir(zpath),zpath)
			good=True
		if good:
			print 'Model:',tris_name
			if author is not None:
				print 'Author:',author
			print 'Textures:'
			print `textures`
			frames,anim=GetAnimations(tris_name)
			print 'Animation list:'
			names=[]
			for i,animation in enumerate(anim):
				names.append(animation[0])
			print '[\'' + '\',\''.join(names)+'\']'
