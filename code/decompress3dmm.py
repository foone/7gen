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
class Decompressor(object):
	def __init__(self, exe_file):
		decomp_proxy_dll = os.path.join(os.path.dirname(os.path.abspath(__file__)),"DecompProxy.dll")
		decompdll = cdll.LoadLibrary(decomp_proxy_dll)
		DLLInit=getattr(decompdll,'DP_Init')
		DLLInit.argtypes=[c_char_p]
		DLLInit.restype=c_void_p
		self.DLLShutdown=getattr(decompdll,'DP_Shutdown')
		self.DLLShutdown.argtypes=[c_void_p]
		self.GetSize=GetSize=getattr(decompdll,'DP_GetSize')
		GetSize.argtypes=[c_char_p,c_int]
		self.DLLDecompress=DLLDecompress=getattr(decompdll,'DP_DecompressSmart')
		DLLDecompress.argtypes=[c_void_p,c_char_p,c_int,c_char_p]

		ret = self.ctx = DLLInit(exe_file)
		if not ret:
			raise OSError("Failed to initialize decompression")

	def shutdown():
		self.DLLShutdown(self.ctx)

	def decompress(self, compressed_string):
		length=self.GetSize(compressed_string,len(compressed_string))
		if length<=0:
			return None
		outbuffer=c_buffer(length)
		if not self.DLLDecompress(self.ctx, compressed_string,len(compressed_string),outbuffer):
			return None
		else:
			return str(outbuffer.raw)

