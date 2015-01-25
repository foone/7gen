#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from error import LoadError
from struct import unpack
import os
import re
from zipfs import fsopen
q2frames=[('Idle',0,39,9),
('Run',40,45,10),
('Attack',46,53,10),
('Pain 1',54,57,7),
('Pain 2',58,61,7),
('Pain 3',62,65,7),
('Jump',66,71,7),
('Flip',72,83,7),
('Salute',84,94,7),
('Taunt',95,111,10),
('Wave',112,122,7),
('Point',123,134,6),
('Crouching Stand',135,153,10),
('Crouching Walk',154,159,7),
('Crouching Attack',160,168,10),
('Crouching Pain',169,172,7),
('Crouching Death',173,177,5),
('Death 1',178,183,7),
('Death 2',184,189,7),
('Death 3',190,197,7),
#('Boom',198,198,5)
]
def GetString(fop,length):
	temp=fop.read(length)
	for i in range(len(temp)):
		if temp[i]=='\0':
			return temp[:i]
def OrganizeIntoAnimations(frames):
	animations={}
	allchar=re.compile(r'^\D+$')
	char_letters=re.compile(r'(\D+)([0-9]+)$')
	frames.sort()
	for frame,fnnumber in frames:
		matches=char_letters.match(frame)
		if matches is None:
			animations[frame]=[(frame,fnnumber)]
		else:
			name,number=matches.groups()
			animations.setdefault(name,[]).append((frame,fnnumber))
	ranim=[]
	for animation in animations:
		ranim.append((animation,animations[animation]))
	return ranim
def GetAnimations(filename,type='auto'):
	fop=fsopen(filename,'rb')
	magic=fop.read(4)
	if magic!='IDP2':
		raise LoadError('Bad magic! Wanted IDP2, got ' +magic)
	version=unpack('<l',fop.read(4))[0]
	if version!=8:
		raise LoadError('Bad version. Wanted 8, got '+version)
	w,h=unpack('<ll',fop.read(8))
	framesize=unpack('<l',fop.read(4))[0]
	numskins,numverts,numtexcoords,numtris,numgl,numframes=unpack('<6l',fop.read(24))
	offskins,offtexcoords,offtris,offframes,offgl,offend=unpack('<6l',fop.read(24))
	framenames=[]
	if type not in ('q2','namedmd2'):
		if numframes==198:
			type='q2'
		else:
			type='namedmd2'
	if type=='namedmd2':
		for i in range(numframes):
			fop.seek(offframes+i*framesize)
			scale=unpack('<fff',fop.read(12))
			translate=unpack('<fff',fop.read(12))
			name=GetString(fop,16)
			if name[0] not in ('$','-'):
				framenames.append((name,i))	
		return (framenames,OrganizeIntoAnimations(framenames))
	elif type=='q2':
		for i in range(numframes):
			fop.seek(offframes+i*framesize)
			scale=unpack('<fff',fop.read(12))
			translate=unpack('<fff',fop.read(12))
			name=GetString(fop,16)
			framenames.append((name,i))	
		anim=[]
		for name,start,end,fps in q2frames:
			ajunk=[]
			for i in range(start,end+1):
				ajunk.append(framenames[i])
			anim.append((name,ajunk))
		return (framenames,anim)

