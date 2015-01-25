#!/usr/env python
from error import SaveError,LoadError,CompressedError
from zipfs import fsopen,isZip,GetFileNameInZip
import os
import pygame
class TextureConverter:
	def __init__(self,palette=None):
		if palette is not None:
			self.palette_surf=palette
		else:
			self.palette_surf=pygame.image.load('code/palette.bmp')
	def palettesMatch(self,othersurf):
		return othersurf.get_palette()==self.palette_surf.get_palette()
	def quantizeImage(self,infile,outfile,dither):
		import quantizer2.quantizer
		return quantizer2.quantizer.quantize(infile,outfile,'palette.bmp',dither)
	def fixPalette(self,surf):
		newsurf=pygame.Surface(surf.get_size(),0,surf)
		newsurf.set_palette(self.palette_surf.get_palette())
		newsurf.blit(surf,(0,0)) #palette mapping should save us.
		return newsurf
	def getTexture(self,filename,dither=False,changedir=True):
		gdither=dither
		if filename[0] in ('-','+'):
			gdither=filename[0]=='+'
			filename=filename[1:]
		if not os.path.exists(filename):
			raise SaveError('Image %s does not exist!' % (filename))
		try:
			texsurf=pygame.image.load(fsopen(filename,'rb'))
			if texsurf.get_bitsize()==8 and  self.palettesMatch(texsurf):
				return texsurf
		except pygame.error:
			pass
		# Try to quantize
		if changedir:
			olddir=os.getcwd()
			os.chdir('..')
	
		try:
			qfilename='quant_temp_in.bmp'
			pygame.image.save(texsurf,qfilename)
			if not self.quantizeImage(qfilename,'quant_temp.tga',gdither):
				os.unlink(qfilename)
				raise SaveError('Quantizing image failed!')
			else:
				texsurf=pygame.image.load('quant_temp.tga')
				texsurf=self.fixPalette(texsurf)
				os.unlink('quant_temp.tga')
				os.unlink(qfilename)
				if changedir:
					os.chdir(olddir)
				return texsurf
		except ImportError:
			if isZip(filename):
				os.unlink(qfilename)
			if changedir:
				os.chdir(olddir)
			raise# SaveError('Bad palette, and missing quantizer!')

