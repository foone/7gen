#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from zipfile import ZipFile
from cStringIO import StringIO
def isZip(filename):
	parts=filename[2:].split(':')
	return len(parts)!=1
def getZipFileName(filename):
	parts=filename[2:].split(':')
	if len(parts)==1:
		return filename
	else:
		return filename[0:2]+parts[0]
def GetFileNameInZip(filename):
	parts=filename[2:].split(':')
	if len(parts)==1:
		return None
	else:
		return parts[1]
def fsopen(filename,mode):
	parts=filename[2:].split(':')
	if len(parts)==1:
		return open(filename,mode)
	else:
		if mode not in ('r','rb'):
			raise ValueError('Bad mode')
		zip=ZipFile(filename[0:2]+parts[0],'r')
		try:
			sio=StringIO(zip.read(parts[1]))
		except KeyError:
			raise IOError('File not found:'+parts[1]+' in '+filename[0:2]+parts[0])
		zip.close()
		return sio
