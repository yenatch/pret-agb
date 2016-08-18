from battle_script import *


class Score(Byte):
	@property
	def asm(self):
		if self.value > 0x80:
			return str(-(0x100 - self.value))
		else:
			return '+' + str(self.value)

class Percent(Byte):
	pass

class ByteList(TerminatedList):
	param_classes = [Byte]
	terminator = 0xff
	def parse(self):
		"""
		A hack to prevent 16-bit constants from looking stupid.
		"""
		TerminatedList.parse(self)
		self.chunks[-1].constants = {}

ByteListPointer = Pointer.to(ByteList)

class WordList(TerminatedList):
	param_classes = [Word]
	terminator = 0xffff

WordListPointer = Pointer.to(WordList)

class IntList(TerminatedList):
	param_classes = [Int]
	terminator = 0xffffffff

IntListPointer = Pointer.to(IntList)

class TurnCount(Word):
	pass

class Stat(Byte):
	constants = {
		1: 'ATTACK',
		2: 'DEFENSE',
		3: 'SPEED',
		4: 'SP_ATTACK',
		5: 'SP_DEFENSE',
		6: 'ACCURACY',
		7: 'EVASION',
	}

class StatLevel(Byte):
	# this is kind of an abuse...
	constants = {
		12: 'MAX_STAT + 1',
		0: 'MIN_STAT - 1',
	}

class UnknownStatus(Status):
	masks = {}

class Weather(Byte):
	constants = {
		0: 'WEATHER_NONE',
		1: 'WEATHER_RAIN',
		2: 'WEATHER_SUN',
		3: 'WEATHER_SANDSTORM',
		4: 'WEATHER_HAIL',
	}

class MoveEffect(Byte):
	constants = 'move_effect_constants'

class HoldEffect(Byte):
	constants = 'hold_effect_constants'


class BattleAIScript(Script):
	@property
	def commands(self):
		return battle_ai_command_classes
	def parse(self):
		Script.parse(self)
		self.infer_types()

	infer_commands = [
		'if_less_than', 'if_more_than', 'if_equal', 'if_not_equal',
		'if_less_than_32', 'if_more_than_32', 'if_equal_32', 'if_not_equal_32',
	]
	infer_list_commands = [
		'if_in_bytes', 'if_not_in_bytes', 'if_in_words', 'if_not_in_words',
	]
	command_types = {
		'get_ability': Ability,
		'get_weather': Weather,
		'get_move_effect': MoveEffect,
		'get_move': Move,
		'get_move_type': Type,
		'get_item': Item,
		'get_effect': MoveEffect,
		'get_type': Type,
		'get_hold_effect': HoldEffect,
	}
	def infer_types(self):
		current_type = None
		for i, command in enumerate(self.chunks):
			name = getattr(command, 'name', None)
			if self.command_types.has_key(name):
				current_type = self.command_types[name]
			elif name in self.infer_commands:
				if current_type and hasattr(current_type, 'constants'):
					command.params['value'].constants = current_type.constants
			elif name in self.infer_list_commands:
				if current_type and hasattr(current_type, 'constants'):
					pointer = command.params['list']
					param = pointer.target.param_classes[0]
					new_param = param.extend(
						constants = current_type.constants
					)
					pointer.target = pointer.target.extend(
						param_classes = [new_param] + pointer.target.param_classes[1:]
					)
					pointer.target.__name__ = current_type.__name__ + 'List'
			else:
				current_type = None

BattleAIScriptPointer = Pointer.to(BattleAIScript)

class BattleAIs(List):
	param_classes = [BattleAIScriptPointer]
	count = 32
	address = 0x1da01c


def expand(commands):
	new = {}
	for key, command in commands.items():
		if command:
			name = command.pop(0)
		else:
			name = 'ai_{:02x}'.format(key)
		params = []
		dicts = []
		for item in command:
			if type(item) is dict:
				dicts += [item]
			else:
				params += [item]
		new[key] = {
			'name': name,
			'param_names': [param[1] for param in params],
			'param_types': [param[0] for param in params]
		}
		for d in dicts:
			new[key].update(d)
	return new

battle_ai_commands = {
	0x00: ['if_random', (Byte, 'percent'), (BattleAIScriptPointer, 'address')],
	0x01: ['if_not_random', (Byte, 'percent'), (BattleAIScriptPointer, 'address')],
	0x02: ['if_random_1', (BattleAIScriptPointer, 'address')],
	0x03: ['if_not_random_1', (BattleAIScriptPointer, 'address')],
	0x04: ['score', (Score, 'score')],
	0x05: ['if_hp_less_than', (Target, 'target'), (Percent, 'percent'), (BattleAIScriptPointer, 'address')],
	0x06: ['if_hp_more_than', (Target, 'target'), (Percent, 'percent'), (BattleAIScriptPointer, 'address')],
	0x07: ['if_hp_equal', (Target, 'target'), (Percent, 'percent'), (BattleAIScriptPointer, 'address')],
	0x08: ['if_hp_not_equal', (Target, 'target'), (Percent, 'percent'), (BattleAIScriptPointer, 'address')],
	0x09: ['if_status', (Target, 'target'), (Status, 'status'), (BattleAIScriptPointer, 'address')],
	0x0a: ['if_not_status', (Target, 'target'), (Status, 'status'), (BattleAIScriptPointer, 'address')],
	0x0b: ['if_status2', (Target, 'target'), (SecondaryStatus, 'status'), (BattleAIScriptPointer, 'address')],
	0x0c: ['if_not_status2', (Target, 'target'), (SecondaryStatus, 'status'), (BattleAIScriptPointer, 'address')],
	0x0d: ['if_status3', (Target, 'target'), (SpecialStatus, 'status'), (BattleAIScriptPointer, 'address')],
	0x0e: ['if_not_status3', (Target, 'target'), (SpecialStatus, 'status'), (BattleAIScriptPointer, 'address')],
	0x0f: ['if_status4', (Target, 'target'), (UnknownStatus, 'status'), (BattleAIScriptPointer, 'address')],
	0x10: ['if_not_status4', (Target, 'target'), (UnknownStatus, 'status'), (BattleAIScriptPointer, 'address')],
	0x11: ['if_less_than', (Byte, 'value'), (BattleAIScriptPointer, 'address')],
	0x12: ['if_more_than', (Byte, 'value'), (BattleAIScriptPointer, 'address')],
	0x13: ['if_equal', (Byte, 'value'), (BattleAIScriptPointer, 'address')],
	0x14: ['if_not_equal', (Byte, 'value'), (BattleAIScriptPointer, 'address')],
	0x15: ['if_less_than_32', (Int, 'value'), (BattleAIScriptPointer, 'address')],
	0x16: ['if_more_than_32', (Int, 'value'), (BattleAIScriptPointer, 'address')],
	0x17: ['if_equal_32', (Int, 'value'), (BattleAIScriptPointer, 'address')],
	0x18: ['if_not_equal_32', (Int, 'value'), (BattleAIScriptPointer, 'address')],
	0x19: ['if_move', (Move, 'move'), (BattleAIScriptPointer, 'address')],
	0x1a: ['if_not_move', (Move, 'move'), (BattleAIScriptPointer, 'address')],
	0x1b: ['if_in_bytes', (ByteListPointer, 'list'), (BattleAIScriptPointer, 'address')],
	0x1c: ['if_not_in_bytes', (ByteListPointer, 'list'), (BattleAIScriptPointer, 'address')],
	0x1d: ['if_in_words', (WordListPointer, 'list'), (BattleAIScriptPointer, 'address')],
	0x1e: ['if_not_in_words', (WordListPointer, 'list'), (BattleAIScriptPointer, 'address')],
	0x1f: ['if_user_can_damage', (BattleAIScriptPointer, 'address')],
	0x20: ['if_user_cant_damage', (BattleAIScriptPointer, 'address')],
	0x21: ['get_turn_count'],
	0x22: ['get_type', (Byte, 'byte')],
	0x23: [],
	0x24: ['is_most_powerful_move'],
	0x25: ['get_move', (Target, 'target')],
	0x26: ['if_type', (Type, 'type'), (BattleAIScriptPointer, 'address')],
	0x27: [],
	0x28: ['if_would_go_first', (Target, 'target'), (BattleAIScriptPointer, 'address')],
	0x29: ['if_would_not_go_first', (Target, 'target'), (BattleAIScriptPointer, 'address')],
	0x2a: [],
	0x2b: [],
	0x2c: ['count_alive_pokemon', (Target, 'target')],
	0x2d: [],
	0x2e: ['get_effect'],
	0x2f: ['get_ability', (Target, 'target')],
	0x30: [],
	0x31: ['if_damage_bonus', (Byte, 'value'), (BattleAIScriptPointer, 'address')],
	0x32: [],
	0x33: [],
	0x34: ['ai_34', (Target, 'target'), (SecondaryStatus, 'status'), (BattleAIScriptPointer, 'address')],
	0x35: [],
	0x36: ['get_weather'],
	0x37: ['if_effect', (MoveEffect, 'byte'), (BattleAIScriptPointer, 'address')],
	0x38: ['if_not_effect', (MoveEffect, 'byte'), (BattleAIScriptPointer, 'address')],
	0x39: ['if_stat_level_less_than', (Target, 'target'), (Stat, 'stat'), (StatLevel, 'level'), (BattleAIScriptPointer, 'address')],
	0x3a: ['if_stat_level_more_than', (Target, 'target'), (Stat, 'stat'), (StatLevel, 'level'), (BattleAIScriptPointer, 'address')],
	0x3b: ['if_stat_level_equal', (Target, 'target'), (Stat, 'stat'), (StatLevel, 'level'), (BattleAIScriptPointer, 'address')],
	0x3c: ['if_stat_level_not_equal', (Target, 'target'), (Stat, 'stat'), (StatLevel, 'level'), (BattleAIScriptPointer, 'address')],
	0x3d: ['if_can_faint', (BattleAIScriptPointer, 'address')],
	0x3e: ['if_cant_faint', (BattleAIScriptPointer, 'address')],
	0x3f: ['if_has_move'],
	0x40: ['if_dont_have_move'],
	0x41: ['if_move_effect', (Target, 'target'), (MoveEffect, 'effect'), (BattleAIScriptPointer, 'address')],
	0x42: ['if_not_move_effect', (Target, 'target'), (MoveEffect, 'effect'), (BattleAIScriptPointer, 'address')],
	0x43: ['if_last_move_did_damage', (Target, 'target'), (Byte, 'byte'), (BattleAIScriptPointer, 'address')],
	0x44: ['if_encored', (BattleAIScriptPointer, 'address')],
	0x45: ['ai_45'],
	0x46: ['ai_46', (BattleAIScriptPointer, 'address')],
	0x47: ['ai_47'],
	0x48: ['get_hold_effect', (Target, 'target')],
	0x49: ['get_gender', (Target, 'target')],
	0x4a: ['ai_4a', (Target, 'target')],
	0x4b: ['get_stockpile_count', (Target, 'target')],
	0x4c: ['is_double_battle'],
	0x4d: ['get_item', (Target, 'target')],
	0x4e: ['get_move_type'],
	0x4f: ['get_move_power'],
	0x50: ['get_move_effect'],
	0x51: ['get_protect_count', (Target, 'target')],
	0x52: [],
	0x53: [],
	0x54: [],
	0x55: [],
	0x56: [],
	0x57: [],
	0x58: ['call', (BattleAIScriptPointer, 'address')],
	0x59: ['jump', (BattleAIScriptPointer, 'address'), {'end': True}],
	0x5a: ['end', {'end': True}],
	0x5b: ['ai_5b', (Target, 'target'), (BattleAIScriptPointer, 'address')],
	0x5c: ['if_taunted', (BattleAIScriptPointer, 'address')],
	0x5d: ['if_not_taunted', (BattleAIScriptPointer, 'address')],
}

battle_ai_commands = expand(battle_ai_commands)

battle_ai_command_classes = make_command_classes(battle_ai_commands, 'BattleAICommand_')

if __name__ == '__main__':
	args = get_args(
		('--macros', {'action': 'store_true'}),
		('-i', {'dest': 'insert', 'action': 'store_true'})
	)
	if args.macros:
		print get_script_macros(battle_ai_commands)
	elif args.insert:
		insert_recursive(BattleAIs, BattleAIs.address)
	else:
		print print_recursive(BattleAIs, BattleAIs.address)
