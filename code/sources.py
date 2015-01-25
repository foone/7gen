#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


import os
class Source:
	def get_length(self):
		return 0
	def get(self):
		return ''
	def write(self,fop):
		pass
	def make_memory_source(self):
		return MemorySource(self.get())
class MemorySource(Source):
	def __init__(self,data):
		self.data=data
	def get_length(self):
		return len(self.data)
	def get(self):
		return self.data
	def write(self,fop):
		fop.write(self.data)
	def make_memory_source(self):
		return self
class CachedMemorySource(Source):
	def __init__(self,data):
		self.file=os.tmpfile()
		self.length=data
		self.file.write(data)
	def get(self):
		self.file.seek(0)
		return self.file.read()
	def write(self,fop):
		fop.write(self.get())
class FileSource(Source):
	def __init__(self,filename,offset,length):
		self.filename=filename
		self.offset=offset
		self.length=length
	def get_length(self):
		return self.length
	def get(self):
		fop=open(self.filename,'rb')
		fop.seek(self.offset)
		return fop.read(self.length)
	def write(self,fop):
		fop.write(self.get())
	def shiftOffset(self,amount):
		self.offset+=amount


