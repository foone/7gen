#!/usr/env python
#BMDLVIEW: Views Microsoft 3D Movie Maker models (BMDLs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from ctypes import *
import os
def Init():
	global decompdll,DLLInit,DLLShutdown,GetSize,DLLDecompress,started
	try:
		if started:
			Shutdown()
	except NameError:
		started=False
	decompdll = cdll.LoadLibrary("DecompProxy.dll")
	DLLInit=getattr(decompdll,'?Init@@YAHPBD@Z')
	DLLInit.argtypes=[c_char_p]
	DLLShutdown=getattr(decompdll,'?Shutdown@@YAHXZ')
	GetSize=getattr(decompdll,'?GetSize@@YAHPAEH@Z') # TEH UGLY!?
	GetSize.argtypes=[c_char_p,c_int]
	DLLDecompress=getattr(decompdll,'?DecompressSmart@@YAHPAEH0@Z')
	DLLDecompress.argtypes=[c_char_p,c_int,c_char_p]
	started=False
	for file in os.listdir(''):
		if file[-4:].lower()=='.exe':
			print 'Trying to load %s... ' % (file),
			ret=DLLInit(file)
			if ret:
				print 'OK'
				started=True
				return True
			else:
				print 'Failed'
	return False
def Shutdown():
	global started
	if started:
		DLLShutdown()
		started=False
def Decompress(string):
	length=GetSize(string,len(string))
	if length<0:
		return None
	outbuffer=c_buffer(length)
	if not DLLDecompress(string,len(string),outbuffer):
		return None
	else:
		return str(outbuffer.raw)
