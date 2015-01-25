# 7gen
7gen is a collection of utilities for generating v3dmm expansions

# Prerequisites for using 7gen:

* Python (>=2.5.x. Tested with 2.7.5)
You can get python at http://www.python.org/
* PyGame (>=1.6. Tested with 1.9.1)
You can get pygame at http://www.pygame.org/

# Other requirements: 

## JKL2VXP:
  To use jkl2vxp, you need a copy of Dark Forces 2: Jedi Knight or Jedi Knight: Mysteries of the Sith. 
  
  You can buy Jedi Knight at: http://store.steampowered.com/app/32380/
  
  And Mysteries of the Sith at: http://store.steampowered.com/app/32390/ 

## OBJ2VXP:
  OBJ2VXP is designed for use with OBJ files created by PlantStudio 2. Other OBJ files might work, but haven't been tested.
  
  You can get PlantStudio 2 here:
  
  http://www.kurtz-fernhout.com/summary_plantstudio.html

## ACTOREXTRACTOR:
  ActorExtractor requires a copy of 3D Movie Maker to be installed and NoCD'd. 
  
  You can get a utility that NoCDs 3DMM here:
  
  http://foone.org/3dmm/files/v3dmm/3dmmNoCD.exe
  
  (Requires the original 3DMM CD)
  
  Also, the automatic combiner scripts created by ActorExtractor are currently Windows-only.
  
  (They use InfoZip's ZIP.EXE to create the .VXP at high compression)

# Licensing:
  All of my (Foone Turing) code (*.py and *.pyw) is under the GPL license. (docs/copying.txt)
  
  The ZIP.EXE file used by ActorExtractor is under the Info-Zip license (docs/INFO-ZIP LICENSE.txt).
  
  The files in quantizer2 (other than quantizer.py) are under the ImageMagic license (docs/ImageMagick License.txt).
  
  The two DLL files (msvcr71.dll and msvcp71.dll) are MSVC 7.1 redistributables.
