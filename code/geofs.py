#!/usr/env python
import os
from zipfile import ZipFile
from cStringIO import StringIO
class DirectoryHandler:
	def __init__(self,path):
		self.path=path
	def open(self,path):
		return open(os.path.join(self.path,path),'rb')
	def dump(self):
		print 'Directory: '+self.path
class ZipHandler:
	def __init__(self,path):
		self.zipfile=ZipFile(path,'r')
		self.path=path
	def open(self,path):
		return StringIO(self.zipfile.read(path))
	def dump(self):
		print 'ZipFile: '+self.path
from jediknight import GOB
class GeoFS:
	def __init__(self,*files):
		self.archives=[]
		for file in files:
			self.addArchive(file)
	def addArchive(self,path,front=False,type='autodetect'):
		ltype=type.lower()
		if ltype=='gob':
			return self.addHandler(GOB(path),front)
		elif ltype=='zip':
			return self.addHandler(ZipHandler(path),front)
		elif ltype in ('real','directory','dir','folder'):
			return self.addHandler(DirectoryHandler(path),front)
		else:
			raise NotImplemented('Not yet!')
	def addCurrentDirectory(self,front=False):
		return self.addHandler(DirectoryHandler(''),front)
	def addDirectory(self,path='',front=False):
		return self.addHandler(DirectoryHandler(path),front)
	def addHandler(self,handler,front=False):
		if front:
			self.archives.insert(0,handler)
		else:
			self.archives.append(handler)
		return True
	def open(self,filename):
		for archive in self.archives:
			try:
				return archive.open(filename)
			except:
				pass
		raise IOError('File not found in any archive: '+filename)
	def dump(self):
		for archive in self.archives:
			archive.dump()
