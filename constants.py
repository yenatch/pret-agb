# coding: utf-8

from map_names import map_names

paths_to_search = ['asm/emerald.s']

labels = {}

def find_labels(path):
	lines = open(path).readlines()
	for line in lines:
		if '.include' in line:
			incpath = line.split('"')[1]
			find_labels(incpath)
		elif ': ;' in line:
			i = line.find(':')
			label, address = line[:i], int(line[i+3:], 16)
			labels[address] = label

for path in paths_to_search:
	find_labels(path)


def load_rom(filename):
    return bytearray(open(filename).read())

baserom = load_rom('base_emerald.gba')


def read_map_groups():
	path = 'constants/map_constants.s'
	lines = open(path).readlines()
	variables = {}
	maps = {}
	for line in lines:
		line = line.strip()
		if line.startswith('.set'):
			name, value = line.split('.set')[1].split(',')
			variables[name.strip()] = int(value, 0)
		elif line.startswith('new_map_group'):
			variables['cur_map_group'] += 1
			variables['cur_map_num'] = 0
			maps[variables['cur_map_group']] = {}
		elif line.startswith('map_group'):
			text = line.split('map_group')[1]
			group, num = map(variables.get, ['cur_map_group','cur_map_num'])
			name = text.split()[0].title().replace('_','')
			maps[group][num] = name
			variables['cur_map_num'] += 1

        # Replace the extracted names with the ones in map_names.py.
        i = 0
        for group_num, group in maps.items():
            for map_num, name in group.items():
                new_name = map_names[i]
                maps[group_num][map_num] = new_name
                i += 1

	return maps

map_groups = read_map_groups()

def get_map_name(group, num):
	group = map_groups.get(group)
	if group:
		label = group.get(num)
		if label:
			return label

def read_constants(path):
	lines = open(path).readlines()
	variables = {}
	for line in lines:
		line = line.strip()
		if line.startswith('.set'):
			name, value = line.split('.set')[1].split(',')
			variables[name.strip()] = int(value, 0)
	return {v:k for k,v in variables.items()}

pokemon_constants = read_constants('constants/species_constants.s')
item_constants = read_constants('constants/item_constants.s')
