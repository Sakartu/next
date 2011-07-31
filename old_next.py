#!/usr/bin/env python
import os
import re
import subprocess

regexes = [
		r'.*S(\d\d)E(\d\d).*avi',
		r'.*S(\d\d)E(\d\d).*mkv',
		r'.*s(\d\d)e(\d\d).*avi',
		r'.*s(\d\d)e(\d\d).*mkv'
		]

OPENLINE = ['mplayer','-vo','gl','-framedrop','-nocache']

def main():
	cwd = os.getcwd()
	files = os.listdir(cwd)
	eps = get_eps(files)
	with open(os.path.join(cwd, '.nextep'), 'a+') as epfile:
		try:
			currentseason = int(epfile.readline())
			currentep = int(epfile.readline())
		except:
			currentseason = 1
			currentep = 1

		print 'Opening ep %s of season %s' % (currentep, currentseason)
		if currentseason in eps and currentep in eps[currentseason]:
			line = OPENLINE
			line.append(os.path.join(cwd, eps[currentseason][currentep]))
			try:
				subprocess.call(line)
			except KeyboardInterrupt:
				pass
			#change the epfile
			if currentep + 1 in eps[currentseason]:
				epfile.truncate(0)
				epfile.write(str(currentseason) + '\n' + str(currentep + 1))
			elif currentseason + 1 in eps:
				epfile.truncate(0)
				epfile.write(str(currentseason + 1) + '\n' + '1')
			else:
				print "Next episode could not be found, please download new season!"
		else:
			print 'Current ep is unavailable, maybe you should download it before watching :)'

	

def get_eps(files):
	eps = {}
	for f in files:
		for rex in regexes:
			p = re.compile(rex)
			m = p.match(f)
			if m:
				season = int(m.group(1))
				ep = int(m.group(2))
				if season not in eps:
					eps[season] = {}
				eps[season][ep] = f
	return eps


if __name__ == '__main__':
	main()
