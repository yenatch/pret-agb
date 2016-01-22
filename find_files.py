import os

from map_names import map_names
from script import is_label

root = 'data/data1.s'
lines = open(root).readlines()

current_name = None
seen_names = []
writes = []
def write(start, end):
	filename = 'data/maps/{}/scripts.s'.format(seen_names[-1])
	try:
		os.makedirs(os.path.dirname(filename))
	except OSError:
		pass
	open(filename, 'w').write(''.join(lines[start:end]))
	#print 'wrote lines {}-{} to {}'.format(start, end, filename)
	global writes
	writes += [(start, end, filename)]

start = None
for i, line in enumerate(lines):
	if is_label(line):
		label = line.split(':')[0]
		if label.endswith('_MapScripts'):
			if start:
				write(start, i)
				start = None
			name = label.split('_MapScripts')[0][1:]
			seen_names += [name]
			start = i
	# arbitrary end point
	if '0x271315' in line and 'incbin' in line:
		write(start, i)
		start = None
i = 0
new_lines = []
for start, end, filename in writes:
	new_lines += lines[i:start]
	new_lines += ['\t.include "{}"\n'.format(filename)]
	i = end
new_lines += lines[i:]

open(root, 'w').write(''.join(new_lines))
