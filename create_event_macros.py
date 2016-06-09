#!/usr/bin/env python

import yaml
import os
import sys
from bs4 import BeautifulSoup, Comment

num_commands = 0xe3

enders = ['end', 'return', 'jump', 'jumpstd', 'jumpram', 'die', 'jumpasm', 'vjump', 'execram']

name_overrides = {
	0x00: 'snop',
	0x01: 'snop1',
	0x06: 'jumpif',
	0x07: 'callif',
	0x0a: 'jumpstdif',
	0x0b: 'callstdif',
	0x5a: 'faceplayer',
	0x5b: 'spriteface',
	0xa6: 'tileeffect',
	0xbb: 'if5',
	0xbc: 'if6',
	0xc3: 'inccounter',
	0xc8: 'loadhelp',
	0xc9: 'unloadhelp',
	0xe2: 'storeitems2',
}

struct_overrides = {
	0x1b: 'byte byte',
	#0x2c: '',
	0x5c: 'byte word word pointer pointer pointer pointer',
	#0x8a: '',
	#0x96: '',
	#0xb1: '',
	0xc8: 'pointer',
	#0xd5: '',
}

aliases = {
	0x05: 'goto',
	0x06: 'if gotoif',
	0x08: 'gotostd',
	0x0a: 'gotostdif',
	0x0d: 'killscript',
	0x0f: 'loadpointer',
	0x10: 'setbyte2',
	#0x13: 'setfarbyte',
	#0x14: 'copyscriptbanks',
	#0x1a: 'copyvarifnotzero',
	0x24: 'gotoasm',
	0x26: 'special2',
	0x2f: 'sound',
	0x33: 'playsong',
	0x34: 'playsong2 playbattlesong playbattlemusic',
	0x36: 'fadesong',
	0x3f: 'setwarpplace',
	0x42: 'getplayerpos',
	0x46: 'checkitemroom',
	0x4b: 'adddecoration',
	0x4c: 'removedecoration',
	0x4d: 'testdecoration',
	0x4e: 'checkdecoration',
	0x4f: 'applymovement',
	0x50: 'applymovementpos movexy',
	0x51: 'waitmovement',
	0x52: 'waitmovementpos waitmovecoords',
	0x53: 'hidesprite',
	0x54: 'hidespritepos',
	0x55: 'showsprite',
	0x56: 'showspritepos',
	0x5d: 'repeattrainerbattle',
	0x66: 'waitmsg',
	0x67: 'msg preparemsg',
	0x68: 'closeonkeypress',
	0x6d: 'waitkeypress',
	0x85: 'bufferstring',
	0x86: 'cry',
	#0xa6: 'cmda6',
	0xc5: 'waitcry',
	0xcc: 'comparecounter',
	0xd0: 'setworldmapflag',
	0xd2: 'setcatchlocation',
}

def override_commands(commands, name_overrides=name_overrides, struct_overrides=struct_overrides, aliases=aliases):
	for cmd, name in name_overrides.items():
		#commands[cmd]['aliases'].append(commands[cmd]['name'])
		commands[cmd]['name'] = name
	for cmd, param_types in struct_overrides.items():
		commands[cmd]['param_types'] = param_types.split()
		commands[cmd]['param_names'] = param_types.split()
	for cmd, names in aliases.items():
		commands[cmd]['aliases'] = list(set(commands[cmd]['aliases'] + names.split()))

	# unique names for each arg
	for cmd in commands.keys():
		param_names = commands[cmd]['param_names']
		for param_name in set(param_names):
			count = 0
			for param in param_names:
				if param == param_name:
					count += 1
			i = 0
			for j, param in enumerate(param_names):
				if param == param_name:
					i += 1
					if count > 1:
						param_names[j] += str(i)

		commands[cmd]['param_names'] = param_names

		if commands[cmd]['name'] in enders:
			commands[cmd]['end'] = True

	return commands


def read_sphericalice_html(filename='extras/index.html'):
	text = open(filename).read()

	commands = {}

	soup = BeautifulSoup(text)
	command_entries = list(soup.find(id='list'))[1::2] # every other child is blank??
	for li in command_entries:
		if type(li) == Comment:
			continue
		byte_str, name = li.h3.text.split()[:2]
		byte = int(byte_str, 16)
		name = name.encode('ascii', 'ignore')

		if li.ul:
			args = list(li.ul.find_all('li'))
			args = [arg.text.split() for arg in args]
			param_types = [arg[0] for arg in args]
			param_names = [arg[1] for arg in args]
		else:
			param_types = []
			param_names = []
		for i, param_type in enumerate(param_types):
			new_type = {
				'bank': 'byte',
				'dword': 'long',
				'variable': 'word',
				'word-or-variable': 'word',
				'flag-or-variable': 'word',
				'byte-or-variable': 'word',
				'pointer-or-bank-0': 'pointer',
				'pointer-or-bank': 'pointer',
				'hidden-variable': 'byte',
				'buffer': 'byte',
			}.get(param_type)
			if new_type:
				param_types[i] = new_type

		description = li.p.text

		commands[byte] = {
			'name': name,
			'param_types': map(lambda x: x if type(x) != unicode else x.encode('ascii'), param_types),
			'param_names': map(lambda x: x if type(x) != unicode else x.encode('ascii'), param_names), #map(unicode.decode, param_names),
			'description': description.encode('ascii', 'ignore'),
		}

	return commands


def override_from_html(commands, *args, **kwargs):
	commands_2 = read_sphericalice_html(*args, **kwargs)
	for byte, command in commands_2.items():
		command['aliases'] = list(set(commands[byte]['aliases'] + [command['name']]))
		command['name'] = commands[byte]['name']
		commands[byte] = command
	return commands


def read_lapis_yaml(filename='extras/lapis-clean.yaml'):

	lapis = yaml.load(open(filename).read())

	def fix_yaml(d):
		return dict(map(lambda (k, v): (k, []) if v[0] == None else (k, v), d.items()))

	names = lapis['names']
	std = fix_yaml(names['std'])
	xse = fix_yaml(names['xse'])
	pksv = fix_yaml(names['pksv'])
	structs = fix_yaml(lapis['structs'])

	commands = {}

	for cmd in std.keys():
		struct = structs[cmd]
		alt_names = []
		if std[cmd]:
			name = std[cmd][0]
		elif xse[cmd]:
			name = xse[cmd][0]
		elif pksv[cmd]:
			name = pksv[cmd][0]
		else:
			name = 'event_{:02x}'.format(cmd)
		all_names = filter(None, list(set(std[cmd] + xse[cmd] + pksv[cmd])))

		# fix corrupted struct defs
		#struct = filter(None, struct)
		for i, param_type in enumerate(struct):
			if param_type == 'dword':
				struct[i] = 'long'
			elif param_type == 'ord':
				struct[i] = 'word'

		param_types = list(struct)
		param_names = list(struct)

		commands[cmd] = {
			'name': name,
			'param_types': param_types,
			'param_names': param_names,
			'aliases': all_names,
		}

	return commands


macro_base = (
	'\t.macro {name} {args}\n' +
	'\t.byte {id}\n' +
	'{arg_behavior}' +
	'\t.endm\n'
)

def make_event_macros(commands, enum=False):

	lines = []
	if enum: lines += ['\tenum_start\n']

	for byte, cmd in commands.items():
		if byte >= num_commands:
			continue
		lines += [make_event_macro(byte, cmd, enum=enum)]

	text = '\n\n'.join(line.rstrip() for line in lines)
	return text.rstrip()

def make_event_macro(byte, cmd, enum=False):

	text = ''

	name = cmd['name']
	param_types = cmd['param_types']
	param_names = cmd['param_names']
	aliases = cmd['aliases']

	args = ', '.join(param_names)
	arg_behavior = []
	for param_type, param_name in zip(param_types, param_names):
		#macro = '.' + param_type
		macro = {
			'byte': '.byte',
			'word': '.2byte',
			'long': '.4byte',
			'pointer': '.4byte',
		}.get(param_type)

		# Forward compatibility: hope it's a class
		if not macro:
			macro = param_type.name

		arg_behavior.append('\t{macro} \\{param_name}\n'.format(macro=macro, param_name=param_name))

	if cmd.has_key('description'):
		lines = cmd['description'].split('\n')
		text += '\n'.join(['\t@ ' + line for line in lines]) + '\n'

	const_text = '_' + name
	byte_text = '0x{:02x}'.format(byte)
	enum_text = '\tenum  {}\n'.format(const_text)
	if enum:
		text += enum_text
		text += macro_base.format(name=name, args=args, id=const_text, arg_behavior=''.join(arg_behavior))
	else:
		text += macro_base.format(name=name, args=args, id=byte_text, arg_behavior=''.join(arg_behavior))

	"""
	alias_base = (
		'\t.macro {alias} {args} @ alias\n' +
		'\t{name} {passed_args}\n' +
		'\t.endm\n'
	)
	aliases_text = ''.join(alias_base.format(alias=alias, name=name, args=args, passed_args=', '.join('\\' + arg for arg in param_names)) for alias in aliases if alias != name)
	text += aliases_text
	"""
	"""
	if aliases:
		text += '@ aliases: ' + ', '.join(aliases) + '\n'
	"""

	return text


def pretty_print_commands(commands):
	text = ''
	text += 'event_commands = {\n'
	for byte, command in sorted(commands.items()):
		if byte >= 0xe3:
			continue

		used_keys = []

		text += '\t0x{:02x}: {{'.format(byte)
		name = command.get('name')
		if name:
			text += ' \'name\': {},'.format(repr(name))
		text += '\n'
		used_keys += ['name']

		keys = command.keys()
		for key in keys:
			if key in used_keys: continue
			text += '\t\t\'' + key + '\': ' + repr(command[key]) + ',' + '\n'
		text += '\t},\n'
	text += '}\n'
	text = text.replace('\t', ' ' * 4)
	return text

if __name__ == '__main__':
	commands = read_lapis_yaml()
	commands = override_from_html(commands)
	commands = override_commands(commands)
	print pretty_print_commands(commands)[:-1]
	#print make_event_macros(commands)
