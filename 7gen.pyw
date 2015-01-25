#!/usr/env python
import sys
sys.path.append('code')
import traceback
def osfo():
	try:
		major,minor,build,platform,text=sys.getwindowsversion()
		if platform==0:
			return 'Windows 3.1 (%i.%i %s, build %i)' % (major,minor,text,build)
		elif platform==1:
			return 'Windows 9x/ME (%i.%i %s, build %i)' % (major,minor,text,build)
		elif platform==2:
			return 'Windows NT/2K/XP (%i.%i %s, build %i)' % (major,minor,text,build)
		elif platform==3:
			return 'Windows CE (%i.%i %s, build %i)' % (major,minor,text,build)
		else:
			return 'Windows ? (%i.%i %s, build %i)' % (major,minor,text,build)
	except:
		return 'OS: %s' % (sys.platform)
def ErrorLogger(filename):
	try:
		type,value,trace=sys.exc_info()
		errortext='Python %s\n%s\n' % (sys.version,osfo())
		errortext+=''.join(traceback.format_exception(type,value,trace))
		sys.stdout.write(errortext)
		fop=open(filename,'w')
		fop.write(errortext)
		fop.close()
	except:
		pass
try:
	import sevengeninterface
	sevengeninterface.run(sys.argv[1:])
except:
	ErrorLogger('errorlog.txt')

