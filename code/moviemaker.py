#!/usr/env python
import lib3dmm
from struct import pack
def makeMovie(id,length,outfile):
	mvie=lib3dmm.Quad('MVIE',0,mode=2)
	mvie.setDataFromFile('code/templates/template.mvie')
	scen=lib3dmm.Quad('SCEN',1)
	scen.setData(pack('<4B3l',1,0,3,3,length,1,3))

	gst=lib3dmm.Quad('GST ',1)
	gst.setDataFromFile('code/templates/template.gst')
	gst2=lib3dmm.Quad('GST ',2)
	gst2.setDataFromFile('code/templates/template2.gst')
	ggfr=lib3dmm.Quad('GGFR',1)
	data='\x01\x00\x03\x03'
	data+=pack('<ll',length,length*12)
	data+='\xFF\xFF\xFF\xFF\x08\x00\x00\x00'
	for i in range(length):
		data+=pack('<3l',i,3,i)

	#stuff

	for i in range(length):
		data+=pack('<ll',i*12,12)
	ggfr.setData(data)
	ggst=lib3dmm.Quad('GGST',1)
	ggstdata='\x01\x00\x03\x03\x01\x00\x00\x00\x18\x00\x00\x00\xff\xff\xff\xff\x08\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x44\x47\x4b\x42'+pack('<l',id) + '\x00\x00\x00\x00\x18\x00\x00\x00'
	ggst.setData(ggstdata)
	thum=lib3dmm.Quad('THUM',1)
	thum.setDataFromFile('code/templates/template.thum')
	mvie.addReference(gst,0)
	mvie.addReference(scen,0)
	mvie.addReference(gst2,1)

	scen.addReference(ggfr,0)
	scen.addReference(thum,0)
	scen.addReference(ggst,1)
	movie=lib3dmm.c3dmmFileOut()
	movie.addQuad(mvie)
	movie.addQuad(scen)
	movie.addQuad(ggfr)
	movie.addQuad(ggst)
	movie.addQuad(thum)
	movie.addQuad(gst)
	movie.addQuad(gst2)
	movie.save(outfile)
