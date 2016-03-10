# coding: utf-8

import os

from map_names import map_names

paths_to_search = ['asm/emerald.s']

labels = {}

def find_labels(path):
	if not os.path.exists(path):
		return
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
		line = line.split(';')[0].strip()
		if line.startswith('.set'):
			name, value = line.split('.set')[1].split(',')
			if '<<' in value: # not supported yet
				pass
			else:
				variables[name.strip()] = int(value, 0)
	return variables

def reverse_constants(variables):
	return {v:k for k,v in variables.items()}

pokemon_constants = reverse_constants(read_constants('constants/species_constants.s'))
item_constants = reverse_constants(read_constants('constants/item_constants.s'))
field_gfx_constants = {
	v: k for k, v in read_constants('constants/field_object_constants.s').items()
	if k.startswith('FIELD_OBJ_GFX_')
}
trainer_constants = {
	v: k for k, v in read_constants('constants/trainer_constants.s').items()
	if k.startswith('TRAINER_')
	and not k.startswith('TRAINER_PIC_')
	and not k.startswith('TRAINER_CLASS_')
	and not k.startswith('TRAINER_CLASS_NAME_')
	and not k.startswith('TRAINER_ENCOUNTER_MUSIC_')
}
frontier_item_constants = {
	v: k for k, v in read_constants('constants/battle_frontier_constants.s').items()
	if k.startswith('BATTLE_FRONTIER_ITEM_')
}
