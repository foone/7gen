#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


from struct import unpack,calcsize,pack
from error import LoadError,SaveError
from sources import *
import cStringIO
def sread(file,struct):
	size=calcsize(struct)
#	print 'Reading %s:%i' % (struct,size)
	res=unpack(struct,file.read(size))
	if len(res)==1:
		return res[0]
	else:
		return res
def refcmp(a, b):
	f=cmp(a[0], b[0])
	if f==0:
		s=cmp(a[1].type,b[1].type)
		if s==0:
			return cmp(a[1].id,b[1].id)
		else: 
			return s
	else:
		return f
class BaseQuad:
	def __init__(self,type,id):
		self.type=type
		self.id=id
	def setID(self,id):
		self.id=id
	def setType(self,type):
		self.type=type
	def isFake(self):
		return False # Maybe?
class FakeQuad(BaseQuad):
	def __init__(self,type,id):
		BaseQuad.__init__(self,type,id)
	def isFake(self):
		return True
class Quad(BaseQuad):
	def __init__(self,type,id=0,mode=0,string=None):
		BaseQuad.__init__(self,type,id)
		self.string=string
		self.mode=mode
		self.source=MemorySource('')
		self.references=[]
	def setData(self,string):
		self.source=MemorySource(string)
	def setMode(self,mode):
		self.mode=mode
	def setDataFromFile(self,file):
		self.source=MemorySource(open(file,'rb').read())
	def setSource(self,source):
		self.source=source
	def setString(self,string):
		if len(string)>255:
			raise SaveError('String too long!')
		self.string=string
	def addReference(self,otherquad,refid):
		self.references.append((refid,otherquad))
	def addFakeReference(self,type,id,refid):
		self.references.append((refid,FakeQuad(type,id)))
	def sortReferences(self):
		self.references.sort(refcmp)
	def getLength(self):
		return self.source.get_length()
	def write(self,fop):
		self.source.write(fop)
	def getNumReferences(self):
		return len(self.references)
	def isFake(self):
		return False
	def makeMemorySource(self):
		self.source=self.source.make_memory_source()
class c3dmmFileOut:
	def __init__(self):
		self.quads=[]
		self.sig='CHMP'
		self.unks=(5,4)
		self.magic=(1,0,3,3)
		self.should_sort=True
	def addQuad(self,quad):
		self.quads.append(quad)
	def getData(self):
		strio=cStringIO.StringIO()
		self.saveToFile(strio)
		return strio.getvalue()
	def save(self,filename):
		fop=open(filename,'wb')
		self.saveToFile(fop)
		fop.close()
	def saveToFile(self,fop):
		offset=128
		quadaddys=[]
		self.unfakeQuads()
		if self.should_sort:
			sortedquads=self.makeSortedQuads()
		else:
			sortedquads=self.quads
		for quad in sortedquads:
			length=quad.getLength()
			quadaddys.append((offset,quad,length))
			offset+=length
		indexoffset=offset
		index=self.makeIndex(quadaddys)
		indexlength=len(index)
		total_length=indexoffset+indexlength
		header=self.makeHeader(total_length,indexoffset,indexlength)
		fop.write(header)
		for quad in sortedquads:
			quad.write(fop)
		fop.write(index)
	def unfakeQuads(self):
		for quad in self.quads:
			for i,(refid,refquad) in enumerate(quad.references):
				if refquad.isFake():
					otherquad=self.find_quad(refquad.type,refquad.id)
					if otherquad is None:
						raise SaveError('Couldn\'t find quad: [%s:%i]' % (refquad.type,refquad.id))
					quad.references[i]=(refid,otherquad)
	def makeHeader(self,length,indexoffset,indexlength):
		header=pack('<8s 2H 4B 4L 96s', 'CHN2' + self.sig[::-1],self.unks[0],self.unks[1],self.magic[0],self.magic[1],self.magic[2],self.magic[3],length,indexoffset,indexlength,length,'')
		return header
	def makeIndex(self,quadaddys):
		index=''
		quadentries=[]
		quadmap={}
		quadslength=0
		for rquad in self.quads:
			found=False
			for offset,quad,length in quadaddys:
				if not found and quad is rquad:
					qe,qelen=self.makeQuadEntry(offset,quad)
					quadent=(quadslength,qe,qelen)
					quadentries.append(quadent)
					quadmap[(quad.type,quad.id)]=quadent
					quadslength+=len(qe)
					found=True
			if not found:
				raise SaveError('missing quad!')
		index+=pack('<4B 2L 2l',self.magic[0],self.magic[1],self.magic[2],self.magic[3],len(self.quads),quadslength,-1,20)
		postindex=''
		for offset,quadentry,quadlen in quadentries:
			index+=quadentry
		for off,quad,length in quadaddys:
			offset,quadentry,quadlen=quadmap[(quad.type,quad.id)]
			postindex+=pack('<2L',offset,quadlen)
		index+=postindex
		return index
	def makeQuadEntry(self,offset,quad):
		qe=pack('<4s 2L B',quad.type[::-1],quad.id,offset,quad.mode)
		qe+=pack('<L',quad.getLength())[0:3] # 24 bit numbers ROCK MY COCK OFF
		qe+=pack('<2H',quad.getNumReferences(),self.getReferenceCount(quad))
		for refid,oquad in quad.references:
			#print '[%s:%i]' % (oquad.type,oquad.id)
			qe+=pack('<4s 2L',oquad.type[::-1],oquad.id,refid)
		exblanks=0
		if quad.string is not None:
			#todo: Unicode?
			strlen=len(quad.string)
			if(strlen>255):
				raise SaveError('String too long!')
			qe+=pack('<3B',3,3,strlen)
			qe+=quad.string
			qe+='\0'
			if strlen%4==0:
				exblanks=0
			else:
				exblanks=4-(strlen%4)
			qe+=('\0'*exblanks)
		return (qe,len(qe)-exblanks)
	def getReferenceCount(self,mainquad):
		count=0
		for quad in self.quads:
			for refid,oquad in quad.references:
				if oquad is mainquad:
					count+=1
		return count
	def makeSortedQuads(self):
		sorted=self.quads[:]
		sorted.sort(self.cmpquad)
		return sorted
	def cmpquad(self,a,b):
		if a.type==b.type:
			return cmp(a.id,b.id)
		else:
			return cmp(a.type,b.type)
	def find_quad(self,type,id):
		for quad in self.quads:
			if (type is not None and quad.type==type) and (id is not None and quad.id==id):
				return quad
	def convertFileSources(self):
		for quad in self.quads:
			quad.source.make_memory_source()
class c3dmmFile:
	def __init__(self,filename=None,cache=False):
		self.cache=cache
		if filename is not None:
			self.load(filename)
		else:
			self.reset()
	def reset(self):
		self.filename=None
		self.id='        '
		self.version=(0,0)
		self.file_length=self.index_offset=0
		self.index_length=self.quad_count=self.quads_length=self_quad_start=0
		self.quad_index=[]
		self.quads=[]
	def load(self,filename):
		self.reset()
		self.filename=filename
		fop=open(filename,'rb') # you know my feelings on this issue.
		self.id=sread(fop,'<8s')
		self.version=sread(fop,'<HH')
		marker=sread(fop,'<4B')
		if not marker in [(1,0,3,3),(1,0,5,5)]:
			raise LoadError, 'Bad/missing marker at %i',fop.tell()
		self.file_length,self.index_offset=sread(fop,'<2L')
		self.index_length,dummy=sread(fop,'<2L')
		fop.seek(self.index_offset)
		marker=sread(fop,'<4B')
		if not marker in [(1,0,3,3),(1,0,5,5)]:
			raise LoadError, 'Bad/missing marker at %i',fop.tell()
		self.quad_count,self.quads_length=sread(fop,'<LL')
		unk=sread(fop,'<ll')
		if unk!=(-1,20):
			print 'unk in indexheader is not -1,20? value: %i,%i' % unk
		self.quad_start=self.index_offset+20
		self.load_quad_index(fop)
		self.load_quads(fop)
	def load_quad_index(self,fop):
		fop.seek(self.quad_start+self.quads_length)
		self.quad_index=[]
		for i in range(self.quad_count):
			self.quad_index.append(sread(fop,'<2L')) 
	def load_quads(self,fop):
		self.quads=[]
		for i in range(self.quad_count):
			cquad={}
			offset,length=self.quad_index[i]
			fop.seek(self.quad_start+offset)
			type=sread(fop,'<4s')[::-1]
			id,section_offset=sread(fop,'<2L')
			mode=sread(fop,'<B')
			section_length=unpack('<L',fop.read(3)+'\0')[0]
			references,references_to_this_quad=sread(fop,'<2H')
#			print type,id,section_offset,mode,section_length,references,references_to_this_quad
			length_of_references=12*references
			cquad['reference_count']=references
			cquad['references_to_this_quad_count']=references_to_this_quad
			cquad['references']=[]
			cquad['type']=type
			cquad['id']=id
			cquad['mode']=mode
			cquad['section_offset']=section_offset
			cquad['section_length']=section_length
			cquad['source']=FileSource(self.filename,section_offset,section_length)
			if self.cache:
				cquad['source']=cquad['source'].make_memory_source()
			for j in range(references):
				ref_type=sread(fop,'<4s')[::-1]
				ref_id,ref_ref_id=sread(fop,'<2L')
#				print 'Ref: %s %i %i' % (ref_type,ref_id,ref_ref_id)
				cref={}
				cref['type']=ref_type
				cref['id']=ref_id
				cref['ref_id']=ref_ref_id
				cquad['references'].append(cref)
			if length_of_references+20!=length: # We have a string
				marker=sread(fop,'<2B')
				if marker==(3,3): # ASCII
					length=sread(fop,'<B')
					str=sread(fop,'<%is' % length)
					cquad['string']=str
				elif marker==(5,5): # unicode!
					length=sread(fop,'<B')
					ustr=u''
					for c in range(length):
						char=sread(fop,'!H')
						ustr+=unichr(char)
					cquad['string']=ustr
				else:
					raise LoadError,'Expected string marker 3,3 or 5,5 but got %i,%i!' % marker
			else:
				cquad['string']=None
			self.quads.append(cquad)
		pass
	def save(self,filename):
		data_size=0
		for quad in self.quads:
			data_size+=quad['source'].get_length()
		print data_size
	def dump(self):
		print 'id:',self.id
		print 'version:',self.version
		print 'file length:',self.file_length
		print 'index offset:',self.index_offset
		print 'index length:',self.index_length
		print 'number of quads:',self.quad_count
		print 'quads length:',self.quads_length

		for quad in self.quads:
			if quad['references_to_this_quad_count']==0:
				after=''
				if quad['string'] is not None:
					after='(%s)' % quad['string']
				if len(quad['references'])==0:
					print '* %s %s' % (quad['type'],after)
				else:
					print '+ %s %s' % (quad['type'],after)
					self.dump_quad(quad)
	def dump_quad(self,quad,level=1):
		sep='  ' * level
		for ref in quad['references']:
			subquad=self.find_quad(ref['type'],ref['id'])
			if subquad is not None:
				after=''
				if subquad['string'] is not None:
					after='(%s)' % subquad['string']
				if len(subquad['references'])==0:
					print '%s* %s %s' % (sep,ref['type'],after)
				else:
					print '%s+ %s %s' % (sep,ref['type'],after)
					self.dump_quad(subquad,level+1)
			else:
				print '%s* %s !' % (sep,ref['type'])
	def shift_quads(self,amount):
		for quad in self.quads:
			quad['source'].shiftOffset(amount)
	def find_quad(self,type,id):
		for quad in self.quads:
			if quad['type']==type and quad['id']==id:
				return quad
	def getMajorQuads(self):
		out=[]
		for quad in self.quads:
			if quad['mode'] in (2,6):
				out.append(quad)
		return out
	def convertFileSources(self):
		for quad in self.quads:
			quad['source']=quad['source'].make_memory_source()

