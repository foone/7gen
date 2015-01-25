#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


from struct import unpack,pack
from array import array
#from OpenGL.GL import *
import random
import os.path
#import fs
from error import LoadError
import cStringIO
from math import sqrt
def modarr(verts,rescales,shifts):
	out=[]
	xrescale,yrescale,zrescale=rescales
	xshift,yshift,zshift=shifts
	for x,y,z,u,v in verts:
		x*=xrescale
		y*=yrescale
		z*=zrescale
		x+=xshift
		y+=yshift
		z+=zshift
		out.append((x,y,z,u,v))
	return out
def distsq(v1,v2):
	xd=v1[0]-v2[0]
	yd=v1[1]-v2[1]
	zd=v1[2]-v2[2]
	return xd**2 + yd**2 + zd**2
def midpoint(v1,v2):
	xd=v1[0]+v2[0]
	yd=v1[1]+v2[1]
	zd=v1[2]+v2[2]
	ud=v1[3]+v2[3]
	vd=v1[4]+v2[4]
	return (xd/2.0,yd/2.0,zd/2.0,ud/2.0,vd/2.0)
def triarea(v1,v2,v3):
	a=distsq(v1,v2)**0.5 # SQRT
	b=distsq(v1,v3)**0.5 # SQRT
	c=distsq(v2,v3)**0.5 # SQRT
	t=(a+b+c)*(b+c-a)*(c+a-b)*(a+b-c)
	return 0.25* (t**0.5)
def triarea_edges(a,b,c):
	t=(a+b+c)*(b+c-a)*(c+a-b)*(a+b-c)
	return 0.25* (t**0.5)
class BRenderModel:
	def __init__(self,filename=None):
		self.verts=[]
		self.vertmap={}
		self.tris=[]
		self.rescalef=163840.0
		self.texrescalef=65535.0 
		self.pos=[0,0,0]
		self.normals=False
		self.tris_normals=[]
		if filename:
			self.load(filename)
	def load(self,filename):
		tx=self.texrescalef
		self.verts=[]
		self.vertmap={}
		self.tris=[]
		self.tris_normals=[]
		self.filename=filename
		self.normals=False
		fop=open(filename,'rb') #I DON'T WANT FOP!
		marker=tuple(array('B',fop.read(4)))
		if marker!=(1,0,3,3):	raise LoadError,'Bad marker'
		vertcount=unpack('<H',fop.read(2))[0]
		tricount=unpack('<H',fop.read(2))[0]
		junk=fop.read(40) # For later.
		for k in range(vertcount):
			vert=fop.read(32)
			x,y,z=unpack('<lll',vert[0:12])
			u,v=unpack('<ll',vert[12:20])
			self.verts.append((x/self.rescalef,y/self.rescalef,z/self.rescalef,u/tx,v/tx))
		for k in range(tricount):
			tri=fop.read(32)
			vert1,vert2,vert3=unpack('<HHH',tri[0:6])
			self.tris.append((vert1,vert2,vert3))
		#raise LoadError,'Not implemented'
	def dump(self):
		print 'File: %s\n%i vertices, %i triangles' % (self.filename,len(self.verts),len(self.tris))
		
		print 'Rescale factor is %0.2f' % (self.rescalef)
		i=0
		for x,y,z,u,v in self.verts:
			print 'Vertex %i: %0.2f %0.2f %0.2f' % (i,x,y,z)
			print 'Texcoords: %0.2f,%0.2f' % (u,v)
			i+=1
		i=0
		for v1,v2,v3 in self.tris:
			print 'Triangle %i: v%i v%i v%i' % (i,v1,v2,v3)
			i+=1
	def SetPos(self,x,y,z):
		self.pos=[x,y,z]
	def drawColored(self):
#		glPushMatrix()
#		glTranslatef(*self.pos)
		glBegin(GL_TRIANGLES)
		for v1,v2,v3 in self.tris:
			glColor3ub(random.randint(0,255),random.randint(0,255),random.randint(0,255))
			x,y,z,u,v=self.verts[v1]
			glVertex3f(x,y,z)
			glColor3ub(random.randint(0,255),random.randint(0,255),random.randint(0,255))
			x,y,z,u,v=self.verts[v2]
			glVertex3f(x,y,z)
			glColor3ub(random.randint(0,255),random.randint(0,255),random.randint(0,255))
			x,y,z,u,v=self.verts[v3]
			glVertex3f(x,y,z)
		glEnd()
#		glPopMatrix()		
	def drawTextured(self):
#		glPushMatrix()
#		glTranslatef(*self.pos)
		glColor3ub(255,255,255)
		glBegin(GL_TRIANGLES)
		for v1,v2,v3 in self.tris:
			x,y,z,u,v=self.verts[v1]
			glTexCoord2f(u,v)
			glVertex3f(x,y,z)
			x,y,z,u,v=self.verts[v2]
			glTexCoord2f(u,v)
			glVertex3f(x,y,z)
			x,y,z,u,v=self.verts[v3]
			glTexCoord2f(u,v)
			glVertex3f(x,y,z)
		glEnd()
#		glPopMatrix()		
	def drawShaded(self):
		if not self.normals:
			self.generateNormals()
		glColor3ub(255,255,255)
		glBegin(GL_TRIANGLES)
		for v1,v2,v3,nx,ny,nz in self.tris_normals:
			glNormal3f(nx,ny,nz) #Normals are per-triangle cause I'm hella lazy. 
			x,y,z,u,v=self.verts[v1]
			glVertex3f(x,y,z)
			x,y,z,u,v=self.verts[v2]
			glVertex3f(x,y,z)
			x,y,z,u,v=self.verts[v3]
			glVertex3f(x,y,z)
		glEnd()
#		glPopMatrix()		
	def shrink(self,scalefactor,filename):
		normals=True
		outfile=open(filename,'wb')
		outfile.write('\x01\x00\x03\x03')
		outfile.write(pack('<HH',len(self.verts),len(self.tris)))
		outfile.write('\x00' * 40)
		for x,y,z,u,v in self.verts:
			rx=int(x*scalefactor*self.rescalef)
			ry=int(y*scalefactor*self.rescalef)
			rz=int(z*scalefactor*self.rescalef)
			u*=self.texrescalef
			v*=self.texrescalef
			outfile.write(pack('<lllll',rx,ry,rz,int(u),int(v)))
			outfile.write('\x00' * 12)
		for v1,v2,v3 in self.tris:
			outfile.write(pack('<HHH',v1,v2,v3))
			if normals:
				outfile.write('\x00' * 10)
				outfile.write('\x01')
				outfile.write('\x00' * 15)
			else:
				outfile.write('\x00' * 26)
		outfile.close()
	def modify(self):
		normals=True
		outvert=[]
		parts=6
		#legs:
		outvert.append(modarr(self.verts,(0.1,0.1,1.2),(-0.9,-0.9,0)))
		outvert.append(modarr(self.verts,(0.1,0.1,1.2),(0.9,-0.9,0)))
		outvert.append(modarr(self.verts,(0.1,0.1,1.2),(-0.9,0.9,0)))
		outvert.append(modarr(self.verts,(0.1,0.1,1.2),(0.9,0.9,0)))
		#top:
		outvert.append(modarr(self.verts,(1,1,0.1),(0,0,1.3)))
		#back:
		outvert.append(modarr(self.verts,(1,0.1,0.8),(0,0.9,2.2)))
		realout=[]
		for arr in outvert:
			for vert in arr:
				realout.append(vert)

		triangles=self.tris
		outtris=[]
		shiftamt=len(self.verts)
		for offset in range(parts):
			for v1,v2,v3 in self.tris:
				outtris.append((v1+offset*shiftamt,v2+offset*shiftamt,v3+offset*shiftamt))
		outfile=open('newmodel.bmdl','wb')
		outfile.write('\x01\x00\x03\x03')
		outfile.write(pack('<HH',len(realout),len(outtris)))
		outfile.write('\x00' * 40)
		for x,y,z,u,v in realout:
			rx=int(x*self.rescalef)
			ry=int(y*self.rescalef)
			rz=int(z*self.rescalef)
			outfile.write(pack('<lll',rx,rz,ry))
			outfile.write('\x00' * 20)
		for v1,v2,v3 in outtris:
			outfile.write(pack('<HHH',v1,v2,v3))
			if normals:
				outfile.write('\x00' * 10)
				outfile.write('\x01')
				outfile.write('\x00' * 15)
			else:
				outfile.write('\x00' * 26)
	def getFilename(self):
		return os.path.basename(self.filename)
	def getTriangleCount(self):
		return len(self.tris)
	def generateNormals(self):
		self.tris_normals=[]
		for v1,v2,v3 in self.tris:
			p1=self.verts[v1]
			p2=self.verts[v2]
			p3=self.verts[v3]
			vec1=Vector([p3[i]-p1[i] for i in range(3)]) #BLACK MAJIK!
			vec2=Vector([p2[i]-p1[i] for i in range(3)])
			final=vec2.cross(vec1).normal()
			self.tris_normals.append((v1,v2,v3,final.x(),final.y(),final.z()))
		self.normals=True
	def happyVertex(self,x,y,z,u,v):
		th=0.001
		txth=0.01
		a,b,c,d,e=[int(j*1000) for j in (x,y,z,u,v)]
		vertkey=(a,b,c,d,e)
		if vertkey in self.vertmap:
			return self.vertmap[vertkey]
		else:
			self.verts.append((x,y,z,u,v))
			index=len(self.verts)-1
			self.vertmap[vertkey]=index
			return index
					
#		for i in range(len(self.verts)-1,-1,-1):
#			verts=self.verts[i]
#			vx,vy,vz,vu,vv=verts
#			if abs(x-vx)<th and abs(y-vy)<th and abs(z-vz)<th and abs(u-vu)<txth and abs(v-vv)<txth:
#				return i # found
		#Not found, so add.
		
	def happyVertexR(self,x,y,z,u,v):
		return self.happyVertex(-x,z,y,u,v)
	def addVertex(self,x,y,z,u=0.0,v=0.0):
		self.verts.append((x,y,z,u,v))
		return len(self.verts)-1
	def loadFromMD2Subframe(self,model,frames,amt=0.5,filename='MD2SOURCE'):
		if len(frames)!=2:
			raise ValueError('frames list must be 2 long')
		if amt<0 or amt>1:
			raise ValueError('amt needs to be between 0 and 1')
		verts=[model.getVerticesForFrame(frames[0]),
			model.getVerticesForFrame(frames[1])]
		iamt=1-amt
		outverts=[]
		for v1,v2 in zip(*verts):
			temp=[y*amt + x*iamt for x,y in zip(v1[0:3],v2[0:3])]
			if v1[3:6]!=v2[3:6]:
				raise ValueError('WTF THE FUCK!? Something wrong with your model, got different texcoords for the same VERTEX')
			outverts.append(temp+list(v1[3:6]))
		self.loadFromFrames(model,outverts,filename)	
	def loadFromMD2(self,model,frame,filename='<MD2SOURCE>'):
		self.loadFromFrames(model,model.getVerticesForFrame(frame),filename)	
	def loadFromFrames(self,model,verts,filename='<MD2SOURCE>'):
		self.verts=[]
		self.vertmap={}
		self.tris=[]
		self.tris_normals=[]
		self.filename=filename
		self.normals=True
		for x,y,z,u,v in verts:
			self.verts.append((-x,z,y,u,1-v)) 
		for v1,v2,v3 in model.tris:
			self.tris.append((v1,v3,v2))
	def save(self,filename,savenormals=True,scalefactor=1.0,texrescale=1.0):
		outfile=open(filename,'wb')
		self.writeToObject(outfile,savenormals,scalefactor,texrescale)
		outfile.close()
	def addTriangle(self,v1,v2,v3):
		a=self.happyVertex(*v1)
		b=self.happyVertex(*v2)
		c=self.happyVertex(*v3)
		self.tris.append((a,b,c))
	def rescale(self,verts=(1.0,1.0,1.0),tex=(1.0,1.0)):
		rx,ry,rz=verts
		ru,rv=tex
		newverts=[]
		for x,y,z,u,v in self.verts:
			newverts.append((x*rx,y*ry,z*rz,u*ru,v*rv))
		self.verts=newverts
		self.vertmap={}
	def subdivide(self,threshold):
		oldverts=self.verts
		oldtris=self.tris
		self.verts=[]
		self.vertmap={}
		self.tris=[]
		replaces=0
		for v1,v2,v3 in oldtris:
			vc1=oldverts[v1]
			vc2=oldverts[v2]
			vc3=oldverts[v3]
			d12=distsq(vc1,vc2)
			d23=distsq(vc2,vc3)
			d31=distsq(vc3,vc1)
			area=triarea_edges(d12**0.5,d23**0.5,d31**0.5)
			#print area
			if area>threshold:
				replaces+=1
				if d12>max(d23,d31):
					np=midpoint(vc1,vc2)
					a=vc1
					b=vc3
					c=vc2
				elif d23>max(d12,d31):
					np=midpoint(vc2,vc3)
					a=vc2
					b=vc1
					c=vc3
				else:
					np=midpoint(vc3,vc1)
					a=vc3
					b=vc2
					c=vc1
				self.addTriangle(a,np,b)
				self.addTriangle(np,c,b)
			else:
				self.addTriangle(vc1,vc2,vc3)
		return replaces
	def writeToObject(self,outfile,savenormals=True,scalefactor=1.0,texrescale=1.0):
		outfile.write('\x01\x00\x03\x03')
		outfile.write(pack('<HH',len(self.verts),len(self.tris)))
		outfile.write('\x00' * 40)
		for x,y,z,u,v in self.verts:
			rx=int(x*scalefactor)
			ry=int(y*scalefactor)
			rz=int(z*scalefactor)
			u*=texrescale
			v*=texrescale
			outfile.write(pack('<lllll',rx,ry,rz,int(u),int(v)))
			outfile.write('\x00' * 12)
		for v1,v2,v3 in self.tris:
			outfile.write(pack('<HHH',v1,v2,v3))
			if savenormals:
				outfile.write('\x00' * 10)
				outfile.write('\x01')
				outfile.write('\x00' * 15)
			else:
				outfile.write('\x00' * 26)
	def getData(self,savenormals=True,scalefactor=1.0,texrescale=1.0):
		strio=cStringIO.StringIO()
		self.writeToObject(strio,savenormals,scalefactor,texrescale)
		return strio.getvalue()
