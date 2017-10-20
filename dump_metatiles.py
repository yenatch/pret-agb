import os

if __name__ == '__main__':
	walk = list(os.walk('data/tilesets'))
	rom = bytearray(open('baserom.gba', 'rb').read())

	lines = []
	for line in open('data/tilesets/metatiles.s'):
		if 'gMetatiles' in line:
			name = line.split(':')[0].split('gMetatiles_')[1]
			attributes = False
		elif 'gMetatileAttributes' in line:
			name = line.split(':')[0].split('gMetatileAttributes_')[1]
			attributes = True

		if '.incbin' in line:
			start, length = map(lambda x: int(x, 0), line.split(',')[1:3])
			data = rom[start:start+length]
			filename = None
			if name.endswith('Primary'):
				primary = 'primary'
			elif name.endswith('Secondary'):
				primary = 'secondary'
			else:
				primary = None
			name = name.replace('Secondary', '')
			name = name.replace('Primary', '')
			old_name = name
			name = ''
			for i, letter in enumerate(old_name):
				if letter.isupper() and i and not old_name[i-1].isupper():
					name += '_'
				if letter.isdigit() and i and not old_name[i-1].isdigit():
					name += '_'
				name += letter.lower()
			for root, dirs, files in walk:
				if name.lower() in dirs:
					if (not primary) or primary in root:
						if attributes:
							filename = os.path.join(root, name.lower() + '/metatile_attributes.bin')
						else:
							filename = os.path.join(root, name.lower() + '/metatiles.bin')
						break
			if filename:
				line = '\t.incbin "{}"\n'.format(filename)
				open(filename, 'wb').write(data)
		lines += [line]
	print ''.join(lines)
