# coding: utf-8

from new import classobj

from script import *

movements = [
	'step_00',
	'step_01',
	'step_02',
	'step_03',
	'slow_step_down',
	'slow_step_up',
	'slow_step_left',
	'slow_step_right',
	'step_down',
	'step_up',
	'step_left',
	'step_right',
	'fast_step_down',
	'fast_step_up',
	'fast_step_left',
	'fast_step_right',
	'step_10',
	'step_11',
	'step_12',
	'step_13',
]

movement_commands = {
	0x91: { 'name': 'step_91', },
	0x92: { 'name': 'step_92', },
	0x96: { 'name': 'step_96', },
	0xfe: { 'name': 'step_end', 'end': True, },
}

num_movement_commands = 0x64

def make_movement_command_classes():
	classes = {}
	for byte, name in enumerate(movements):
		movement_commands[byte] = {
			'name': name,
		}
	for byte in xrange(byte, num_movement_commands):
		movement_commands[byte] = {
			'name': 'step_{:02x}'.format(byte)
		}
	for byte, command in movement_commands.items():
		class_name = 'Movement_' + command['name']
		attributes = {}
		attributes['id'] = byte
		attributes['param_classes'] = [Byte] + command.get('param_types', list())
		attributes.update(command)
		classes[byte] = classobj(class_name, (Command,), attributes)
	return classes

movement_command_classes = make_movement_command_classes()

class Movement(Script):
	commands = movement_command_classes

class MovementPointer(Pointer):
	target = Movement
