import os

from map_names import map_names
from script import is_label


def makedirs(*args, **kwargs):
	try:
		os.makedirs(*args, **kwargs)
	except OSError:
		pass


def split_stuff(root, writes):

	for start, end, filename in writes:
		makedirs(os.path.dirname(filename))
		open(filename, 'w').write(''.join(lines[start:end]))

	i = 0
	new_lines = []
	lines = open(root).readlines()
	for start, end, filename in writes:
		new_lines += lines[i:start]
		new_lines += ['\t.include "{}"\n'.format(filename)]
		i = end
	new_lines += lines[i:]

	open(root, 'w').write(''.join(new_lines))


def get_label(line):
	if is_label(line):
		return line.split(':')[0]


def split_map_scripts():
	root = 'data/data1.s'

	seen = []
	def get_filename():
		return 'data/maps/{}/scripts.s'.format(seen[-1])

	writes = []
	def write(start, end):
		if start is not None:
			writes.append((start, end, get_filename()))

	writes = []
	start = None
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			if label.endswith('_MapScripts'):
				write(start, i)
				name = label[1:-len('_MapScripts')
				seen += [name]
				start = i
			# arbitrary stopping point
			if '0x271315' in line:
				break

	split_stuff(root, writes)


def split_map_assets():
	root = 'data/data2.s'

	start = None
	enders = ('_MapBorder', '_MapBlockdata', '_MapAttributes')
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			if any(map(label.endswith, enders)):
				if start is None: start = i
			elif start:
				break
	end = i
	split_stuff(root, [(start, end, 'data/maps/_assets.s')])


def split_map_events():
	root = 'data/data2.s'

	seen = []
	def get_filename():
		return 'data/maps/{}/events.s'.format(seen[-1])

	writes = []
	def write(start, end):
		if start is not None:
			writes.append((start, end, get_filename()))

	start = None
	enders = ('_MapObjects', '_MapWarps', '_MapCoordEvents', '_MapBGEvents', '_MapEvents')
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			for ender in enders:
				if label.endswith(ender):
					name = label.split(ender)[0][1:]
					if name not in seen:
						write(start, i)
						seen += [name]
						start = i
					break
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			write(start, i)
			start = None

	split_stuff(root, writes)


def split_map_headers():
	root = 'data/data2.s'

	seen = []
	def get_filename():
		return 'data/maps/{}/header.s'.format(seen[-1])

	writes = []
	def write(start, end):
		if start is not None:
			writes.append((start, end, get_filename()))

	start = None
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			name = label[1:]
			if name in map_names:
				write(start, i)
				seen += [name]
				start = i
			else:
				write(start, i)
				start = None
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			write(start, i)
			start = None

	split_stuff(root, writes)


def split_map_groups():
	root = 'data/data2.s'

	start = None
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			if label.startswith('gMapGroup'):
				if start is not None: start = i
			elif start is not None:
				break
	end = i
	split_stuff(root, [(start, end, 'data/maps/_groups.s')])


def split_map_connections():
	root = 'data/data2.s'

	seen = []
	def get_filename():
		return 'data/maps/{}/connections.s'.format(seen[-1])

	writes = []
	def write(start, end):
		if start is not None:
			writes.append((start, end, get_filename()))

	start = None
	ender = '_MapConnectionsList'
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			if label.endswith(ender):
				write(start, i)
				name = label.split(ender)[0][1:]
				seen_names += [name]
				start = i
			elif not label.endswith('_MapConnections'):
				write(start, i)
				start = None
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			write(start, i)
			start = None

	split_stuff(root, writes)


def main():
	split_map_scripts()
	split_map_assets()
	split_map_events()
	split_map_headers()
	split_map_groups()
	split_map_connections()

if __name__ == '__main__':
	main()
