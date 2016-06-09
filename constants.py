# coding: utf-8

from os.path import exists

def find_labels(path):
	labels = {}
	if not exists(path):
		return labels
	lines = open(path).readlines()
	for line in lines:
		if '.include' in line:
			incpath = line.split('"')[1]
			labels.update(find_labels(incpath))
		elif ': @' in line:
			i = line.find(':')
			try:
				label, address = line[:i], int(line[i+3:].split()[0], 16)
				labels[address] = label
			except:
				pass
	return labels

def load_rom(filename):
    return bytearray(open(filename).read())

def read_map_groups(path, map_names):
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

        # Replace the constants with capitalized map names.
        # This is only necessary if the constants have not already been fixed.
        i = 0
        for group_num, group in maps.items():
            for map_num, name in group.items():
                new_name = map_names[i]
                maps[group_num][map_num] = new_name
                i += 1

	return maps

def get_map_name(map_groups, group, num):
	group = map_groups.get(group)
	if group:
		label = group.get(num)
		if label:
			return label

def read_constants(path):
	lines = open(path).readlines()
	variables = {}
	for line in lines:
		line = line.split('@')[0].strip()
		if line.startswith('.set'):
			name, value = line.split('.set')[1].split(',')
			if '<<' in value: # not supported yet
				pass
			else:
				variables[name.strip()] = int(value, 0)
	return variables

def reverse_constants(variables):
	return {v:k for k,v in variables.items()}

def read_reverse_constants(path):
	return reverse_constants(read_constants(path))


def setup_version(version):
	version.update({
		'baserom': load_rom(version['baserom_path']),
		'map_groups': read_map_groups('constants/map_constants.s', version['map_names']),
		'pokemon_constants': read_reverse_constants('constants/species_constants.s'),
		'item_constants': read_reverse_constants('constants/item_constants.s'),
		'trainer_constants': {
			v: k for k, v in read_constants('constants/trainer_constants.s').items()
			if k.startswith('TRAINER_')
			and not k.startswith('TRAINER_PIC_')
			and not k.startswith('TRAINER_CLASS_')
			and not k.startswith('TRAINER_CLASS_NAME_')
			and not k.startswith('TRAINER_ENCOUNTER_MUSIC_')
		},
	})

	version['labels'] = {}
	for path in version['maps_paths']:
		version['labels'].update(find_labels(path))

	path = version.get('frontier_item_constants_path')
	if path:
		version['frontier_item_constants'] = {
			v: k for k, v in read_constants(path).items()
			if k.startswith('BATTLE_FRONTIER_ITEM_')
		}
	path = version.get('field_object_constants_path')
	if path:
		version['field_gfx_constants'] = {
			v: k for k, v in read_constants(path).items()
			if k.startswith('FIELD_OBJ_GFX_')
			or k.startswith('MAP_OBJ_GFX_')
		}
