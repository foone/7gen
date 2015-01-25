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
def Get3dmmInstallDirectory():
	try:
		handle=reg.OpenKey(reg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Microsoft\Microsoft Kids\3D Movie Maker')
		path,type=reg.QueryValueEx(handle,'InstallDirectory')
		if type!=reg.REG_SZ:
			return False
		rpath,type=reg.QueryValueEx(handle,'InstallSubDir')
		if type!=reg.REG_SZ:
			return False
		return os.path.join(path,rpath)
	except WindowsError:
		return False
