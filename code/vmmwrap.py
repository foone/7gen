#!/usr/env python
from struct import pack
from zipfile import ZipFile
from error import LoadError
import os.path
def Wrap3dmmMovieInVmm(movie,expansions,outfile):
	fop=open(outfile,'wb')
	fop.write('v3dmm\x01')
	numexpansions=len(expansions)+1 # Plus 1: 3dmm
	fop.write(pack('<l',numexpansions))
	fop.write(pack('<lh',0,4)+'3dmm')
	
	expinfo=[]
	for expansion in expansions:
		zip=ZipFile(expansion,'r')
		found=False
		for zipfile in zip.namelist():
			base,ext=os.path.splitext(zipfile)
			if ext.lower()=='.cfg':
				found=True
				shortname=base
				data=zip.read(zipfile)
				lines=data.split('\n')
				db={}
				for line in lines:
					if len(line)>1 and line[0]!='#':
						try:
							name,value=line.split('=')
							db[name.lower()]=value
						except ValueError:
							pass # Skip this one, must be bad.
		if not found:
			raise LoadError('Couldn\'t find CFG in $s' % (expansion))
		else:
			expinfo.append((expansion,shortname,db,os.path.getsize(expansion)))			
		
	for filename,shortname,cfg,size in expinfo:
		name=cfg['name']
		fop.write(pack('<lh',size,len(name)))
		fop.write(name)
	for filename,shortname,cfg,size in expinfo:
		if size!=0:
			fop.write('\xF0\x0B')
			fop.write(open(filename,'rb').read())
			fop.write('\xFE\xEB')
	fop.write(open(movie,'rb').read())
	fop.close()
	return True
