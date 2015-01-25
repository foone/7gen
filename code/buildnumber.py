#!/usr/env python
number=None
def Increment(name):
	num=Get(name)
	open('.'+name+'.bn','w').write('%i' % (num+1))
def Get(name):
	global number
	if number is None:
		try:
			line=open('.'+name+'.bn','r').read()
			number=int(line)
		except IOError:
			number=0
	return number

