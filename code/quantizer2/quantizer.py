#!/usr/env python
#BMP2VXP: Converts BMP files to VXP expansions
#Copyright (C) 2004-2015 Foone Turing
#
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
import os
def quantize(infile,outfile,palettefile,dither):
	try:
		os.chdir('code\\quantizer2')
		if dither:
			ditherstr='on'
		else:
			ditherstr='off'
		filename='Quanter2.exe'
		relinfile='"%s"' % (os.path.join('..\\..',infile))
		reloutfile='"%s"' % (os.path.join('..\\..',outfile))
		relpalfile='"%s"' % (os.path.join('..',palettefile))
		pathjunk=filename,filename,relinfile,reloutfile,relpalfile,ditherstr
		#print pathjunk
		ret=os.spawnl(os.P_WAIT,*pathjunk)
		os.chdir('..\\..')
	except OSError:
		return False
	return ret==0
