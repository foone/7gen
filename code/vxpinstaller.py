#!/usr/env python
#md2_to_vxp: Converts Quake 2 MD2 files to v3dmm expansions (VXPs)
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import _winreg as reg
from error import InstallError
import os
import shutil
def getV3dmmInstallDirectory():
	try:
		handle=reg.OpenKey(reg.HKEY_CURRENT_USER,r'Software\TravisWells\v3dmmManager\paths')
		path,type=reg.QueryValueEx(handle,'v3dmmdir')
		if type!=reg.REG_SZ:
			return False
		return os.path.join(path,'Expansions')
	except WindowsError:
		return False
def installVXP(filename):
	path=getV3dmmInstallDirectory()
	if path is False:
		raise InstallError('Couldn\'t get v3dmm Expansion directory')
	outpath=os.path.join(path,filename)
	try:
		shutil.copy(filename,outpath)
	except:
		raise InstallError('Copy failed')
	return True
