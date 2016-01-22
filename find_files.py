import os

from map_names import map_names
from script import is_label


def split_map_scripts():

	root = 'data/data1.s'
	lines = open(root).readlines()

	seen_names = []

	writes = []
	def write(start, end):
		filename = 'data/maps/{}/scripts.s'.format(seen_names[-1])
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		open(filename, 'w').write(''.join(lines[start:end]))
		writes.append((start, end, filename))

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
			if start:
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


def old_split_map_assets():

	root = 'data/data2.s'
	lines = open(root).readlines()

	seen_names = []

	writes = []
	def write(start, end):
		filename = 'data/maps/{}/attributes.s'.format(seen_names[-1])
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		open(filename, 'w').write(''.join(lines[start:end]))
		writes.append((start, end, filename))

	start = None
	for i, line in enumerate(lines):
		if is_label(line):
			label = line.split(':')[0]
			if label.endswith('_MapBorder'):
				if start:
					write(start, i)
					start = None
				name = label.split('_MapBorder')[0][1:]
				seen_names += [name]
				start = i
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			if start:
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

def split_map_assets():

	root = 'data/data2.s'
	lines = open(root).readlines()

	writes = []
	def write(start, end):
		filename = 'data/maps/_assets.s'
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		open(filename, 'w').write(''.join(lines[start:end]))
		writes.append((start, end, filename))

	start = None
	for i, line in enumerate(lines):
		if is_label(line):
			label = line.split(':')[0]
			enders = ('_MapBorder', '_MapBlockdata', '_MapAttributes')
			if any(label.endswith(ender) for ender in enders):
				if not start:
					start = i
			else:
				if start:
					write(start, i)
					start = None
		## arbitrary end point
		#if '0x481d04' in line and 'base_emerald' in line and 'incbin' in line:
		#	if start:
		#		write(start, i)
		#		start = None
	i = 0
	new_lines = []
	for start, end, filename in writes:
		new_lines += lines[i:start]
		new_lines += ['\t.include "{}"\n'.format(filename)]
		i = end
	new_lines += lines[i:]

	open(root, 'w').write(''.join(new_lines))

def split_map_events():

	root = 'data/data2.s'
	lines = open(root).readlines()

	seen_names = []

	writes = []
	def write(start, end):
		filename = 'data/maps/{}/events.s'.format(seen_names[-1])
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		open(filename, 'w').write(''.join(lines[start:end]))
		writes.append((start, end, filename))

	start = None
	for i, line in enumerate(lines):
		if is_label(line):
			label = line.split(':')[0]
			for ender in ('_MapObjects', '_MapWarps', '_MapCoordEvents', '_MapBGEvents', '_MapEvents'):
				if label.endswith(ender):
					name = label.split(ender)[0][1:]
					if name not in seen_names:
						if start:
							write(start, i)
							start = None
						seen_names += [name]
						start = i
					break
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			if start:
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


def split_map_headers():

	root = 'data/data2.s'
	lines = open(root).readlines()

	seen_names = []

	writes = []
	def write(start, end):
		filename = 'data/maps/{}/header.s'.format(seen_names[-1])
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		open(filename, 'w').write(''.join(lines[start:end]))
		writes.append((start, end, filename))

	start = None
	for i, line in enumerate(lines):
		if is_label(line):
			label = line.split(':')[0]
			name = label[1:]
			if name in map_names:
				if start:
					write(start, i)
					start = None
				seen_names += [name]
				start = i
			else:
				if start:
					write(start, i)
					start = None
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			if start:
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


def split_map_groups():

	root = 'data/data2.s'
	lines = open(root).readlines()

	writes = []
	def write(start, end):
		filename = 'data/maps/_groups.s'
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		open(filename, 'w').write(''.join(lines[start:end]))
		writes.append((start, end, filename))

	start = None
	for i, line in enumerate(lines):
		if is_label(line):
			label = line.split(':')[0]
			if 'gMapGroup' in label:
				if not start:
					start = i
			else:
				if start:
					write(start, i)
					start = None
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			if start:
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


def split_map_connections():

	root = 'data/data2.s'
	lines = open(root).readlines()

	seen_names = []

	writes = []
	def write(start, end):
		filename = 'data/maps/{}/connections.s'.format(seen_names[-1])
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		open(filename, 'w').write(''.join(lines[start:end]))
		writes.append((start, end, filename))

	start = None
	for i, line in enumerate(lines):
		if is_label(line):
			label = line.split(':')[0]
			ender = '_MapConnectionsList'
			if label.endswith(ender):
				if start:
					write(start, i)
					start = None
				name = label.split(ender)[0][1:]
				seen_names += [name]
				start = i
			elif not label.endswith('_MapConnections'):
				if start:
					write(start, i)
					start = None
		# dont absorb incbins
		if 'base_emerald' in line and 'incbin' in line:
			if start:
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

if __name__ == '__main__':
	split_map_scripts()
	split_map_assets()
	split_map_events()
	split_map_headers()
	split_map_groups()
	split_map_connections()
