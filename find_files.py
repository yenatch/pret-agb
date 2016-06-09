import os

from script import is_label
import versions

g = ''

def makedirs(*args, **kwargs):
	try:
		os.makedirs(*args, **kwargs)
	except OSError:
		pass


def split_stuff(root, writes):

	lines = open(root).readlines()
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
	if '.global' in line:
		return line.split(' ')[1].strip()
	if is_label(line):
		return line.split(':')[0].strip()


def split_map_scripts(version):
	root = 'data/data1.s'

	seen = []
	def get_filename():
		return 'data/maps/scripts/{}.s'.format(seen[-1])

	writes = []
	def write(start, end):
		if start is not None:
			writes.append((start, end, get_filename()))

	start = None
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			if label.endswith('_MapScripts'):
				name = label[len(g):-len('_MapScripts')]
				if name not in seen:
					write(start, i)
					seen += [name]
					start = i
			elif (
				'_EventScript_' not in label
				and '_MapScript1_' not in label
				and '_MapScript2_' not in label
				and ((not seen) or (seen[-1] + '_' not in label))
			):
				write(start, i)
				start = None
			# arbitrary stopping point
			if version['version'] == 'emerald':
				if '0x271315' in line:
					break

	split_stuff(root, writes)

def split_map_text(version):
	if version['version'] == 'emerald':
		return

	root = 'data/data1.s'

	seen = []
	def get_filename():
		return 'data/maps/text/{}.s'.format(seen[-1])

	writes = []
	def write(start, end):
		if start is not None:
			writes.append((start, end, get_filename()))

	start = None
	for i, line in enumerate(open(root)):
		label = get_label(line)
		if label:
			if '_Text_' in label:
				name = label[len(g):label.find('_Text_')]
				if name not in seen:
					write(start, i)
					seen += [name]
					start = i
				elif seen and name != seen[-1]:
					write(start, i)
					start = None
			else:
				write(start, i)
				start = None
		if version['version'] == 'ruby':
			if '0x19f7de' in line:
				write(start, i)
				start = None
				#break

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
		return 'data/maps/events/{}.s'.format(seen[-1])

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
					name = label.split(ender)[0][len(g):]
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


def split_map_headers(version):
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
			name = label[len(g):]
			if name in version['map_names']:
				if name not in seen:
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
				if start is None: start = i
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
				name = label.split(ender)[0][len(g):]
				if name not in seen:
					write(start, i)
					seen += [name]
					start = i
			elif not label.endswith('_MapConnections'):
				write(start, i)
				start = None
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			write(start, i)
			start = None

	split_stuff(root, writes)


def main(version):
	split_map_scripts(version)
	split_map_assets()
	split_map_events()
	split_map_headers(version)
	split_map_groups()
	split_map_connections()
	split_map_text(version)

if __name__ == '__main__':
	main(versions.ruby)
