from script import *
from text import *
from event_script import make_command_classes


class BattleScript(Script):
	@property
	def commands(self):
		return battle_script_command_classes

class BattleScriptPointer(Pointer):
	target = BattleScript


class UnboundedList(List):
	max_count = 0x100 # arbitrary
	def parse(self):
		self.count = 0
		List.parse(self)
		while self.count < self.max_count:
			self.count += 1
			try:
				self.parse_item()
			except Exception as e:
				self.count -= 1
				break
		List.parse(self)


class Ability(Byte):
	@property
	def asm(self):
		return self.version.get('ability_constants', {}).get(self.value, Byte.asm.fget(self))

class Type(Byte):
	@property
	def asm(self):
		return self.version.get('type_constants', {}).get(self.value, Byte.asm.fget(self))

class Status(Int):
	masks = {
		'SLP': 0x07,
		'PSN': 0x08,
		'BRN': 0x10,
		'FRZ': 0x20,
		'PAR': 0x40,
		'TOX': 0x80,
	}
	@property
	def asm(self):
		statuses = []
		remaining = self.value
		for constant, mask in sorted(self.masks.items(), key = lambda x: x[1]):
			if (self.value & mask) == mask:
				statuses += [constant]
				remaining &= ~mask
		if remaining:
			statuses += [hex(remaining)]
		return ' | '.join(statuses)

class SecondaryStatus(Status):
	masks = {
		'S_CONFUSED': 0x07,
		'S_CONTINUE': 0x1000,
		'S_FOCUS_ENERGY': 0x100000,
		'S_SUBSTITUTE': 0x1000000,
		'S_MEAN_LOOK': 0x4000000,
		'S_NIGHTMARE': 0x8000000,
	}

class SpecialStatus(Status):
	masks = {
	}

class InvalidBattleTextId(Exception):
	pass

class BattleTextId(Word):
	def parse(self):
		Word.parse(self)
		if self.value > 400:
			raise InvalidBattleTextId
	@property
	def asm(self):
		return self.version.get('battle_text_constants', {}).get(self.value, Word.asm.fget(self))

class BattleTextList(UnboundedList):
	param_classes = [BattleTextId]

class BattleTextListPointer(Pointer):
	target = BattleTextList


class Target(Byte):
	@property
	def asm(self):
		if self.value == 0:
			return 'TARGET'
		elif self.value == 1:
			return 'USER'
		else:
			return Byte.asm.fget(self)


battle_script_commands = {

	0: { 'name': 'attackcanceler',
	},

	1: { 'name': 'accuracycheck',
		'param_names': ['address', 'param1'],
		'param_types': [BattleScriptPointer, Word],
	},

	2: { 'name': 'attackstring',
	},

	3: { 'name': 'ppreduce',
	},

	4: { 'name': 'critcalc',
	},

	5: { 'name': 'atk5',
	},

	6: { 'name': 'atk6',
	},

	7: { 'name': 'atk7',
	},

	8: { 'name': 'atk8',
	},

	9: { 'name': 'attackanimation',
	},

	0xA: { 'name': 'waitanimation',
	},

	0xB: { 'name': 'graphicalhpupdate',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0xC: { 'name': 'datahpupdate',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0xD: { 'name': 'critmessage',
	},

	0xE: { 'name': 'missmessage',
	},

	0xF: { 'name': 'resultmessage',
	},

	0x10: { 'name': 'printstring',
		'param_names': ['string'],
		'param_types': [BattleTextId],
	},

	0x11: { 'name': 'printstring2',
		'param_names': ['string'],
		'param_types': [BattleTextId],
	},

	0x12: { 'name': 'waitmessage',
		'param_names': ['delay'],
		'param_types': [Word],
	},

	0x13: { 'name': 'printfromtable',
		'param_names': ['table'],
		'param_types': [BattleTextListPointer],
	},

	0x14: { 'name': 'printfromtable2',
		'param_names': ['table'],
		'param_types': [BattleTextListPointer],
	},

	0x15: { 'name': 'seteffectwithchancetarget',
	},

	0x16: { 'name': 'seteffecttarget',
	},

	0x17: { 'name': 'seteffectuser',
	},

	0x18: { 'name': 'clearstatus',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x19: { 'name': 'faintpokemon',
		'param_names': ['bank', 'param2', 'param3'],
		'param_types': [Target, Byte, BattleScriptPointer],
	},

	0x1A: { 'name': 'atk1a',
		'param_names': ['param1'],
		'param_types': [Byte],
	},

	0x1B: { 'name': 'atk1b',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x1C: { 'name': 'jumpifstatus',
		'param_names': ['bank', 'status', 'address'],
		'param_types': [Target, Status, BattleScriptPointer],
	},

	0x1D: { 'name': 'jumpifsecondarytstatus',
		'param_names': ['bank', 'status', 'address'],
		'param_types': [Target, SecondaryStatus, BattleScriptPointer],
	},

	0x1E: { 'name': 'jumpifability',
		'param_names': ['bank', 'ability', 'address'],
		'param_types': [Target, Ability, BattleScriptPointer],
	},

	0x1F: { 'name': 'jumpifhalverset',
		'param_names': ['bank', 'status', 'address'],
		'param_types': [Target, Word, BattleScriptPointer],
	},

	0x20: { 'name': 'jumpifstat',
		'param_names': ['bank', 'flag', 'quantity', 'statid', 'address'],
		'param_types': [Target, Byte, Byte, Byte, BattleScriptPointer],
	},

	0x21: { 'name': 'jumpifspecialstatusflag',
		'param_names': ['bank', 'mask', 'status', 'address'],
		'param_types': [Target, SpecialStatus, Byte, BattleScriptPointer],
	},

	0x22: { 'name': 'jumpiftype',
		'param_names': ['bank', 'type', 'address'],
		'param_types': [Target, Type, BattleScriptPointer],
	},

	0x23: { 'name': 'atk23',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x24: { 'name': 'atk24',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x25: { 'name': 'atk25',
	},

	0x26: { 'name': 'atk26',
		'param_names': ['param1'],
		'param_types': [Byte],
	},

	0x27: { 'name': 'atk27',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x28: { 'name': 'jump',
		'end': True,
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x29: { 'name': 'jumpifbyte',
		'param_names': ['ifflag', 'checkaddr', 'compare', 'address'],
		'param_types': [Byte, Pointer, Byte, BattleScriptPointer],
	},

	0x2A: { 'name': 'jumpifhalfword',
		'param_names': ['ifflag', 'checkaddr', 'compare', 'address'],
		'param_types': [Byte, Pointer, Word, BattleScriptPointer],
	},

	0x2B: { 'name': 'jumpifword',
		'param_names': ['ifflag', 'checkaddr', 'compare', 'address'],
		'param_types': [Byte, Pointer, Int, BattleScriptPointer],
	},

	0x2C: { 'name': 'jumpifarrayequal',
		'param_names': ['mem1', 'mem2', 'size', 'address'],
		'param_types': [Pointer, Pointer, Byte, BattleScriptPointer],
	},

	0x2D: { 'name': 'jumpifarraynotequal',
		'param_names': ['mem1', 'mem2', 'size', 'address'],
		'param_types': [Pointer, Pointer, Byte, BattleScriptPointer],
	},

	0x2E: { 'name': 'setbyte',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Byte],
	},

	0x2F: { 'name': 'addbyte',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Byte],
	},

	0x30: { 'name': 'subtractbyte',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Byte],
	},

	0x31: { 'name': 'copyarray',
		'param_names': ['destination', 'source', 'size'],
		'param_types': [Pointer, Pointer, Byte],
	},

	0x32: { 'name': 'atk32',
		'param_names': ['param1', 'param2', 'param3', 'byte'],
		'param_types': [Pointer, Pointer, Pointer, Byte],
	},

	0x33: { 'name': 'orbyte',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Byte],
	},

	0x34: { 'name': 'orhalfword',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Word],
	},

	0x35: { 'name': 'orword',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Int],
	},

	0x36: { 'name': 'bicbyte',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Byte],
	},

	0x37: { 'name': 'bichalfword',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Word],
	},

	0x38: { 'name': 'bicword',
		'param_names': ['pointer', 'value'],
		'param_types': [Pointer, Int],
	},

	0x39: { 'name': 'pause',
		'param_names': ['pause_duration'],
		'param_types': [Word],
	},

	0x3A: { 'name': 'waitstateatk',
	},

	0x3B: { 'name': 'somethinghealatk3b',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x3C: { 'name': 'return',
		'end': True,
	},

	0x3D: { 'name': 'end',
		'end': True,
	},

	0x3E: { 'name': 'end2',
		'end': True,
	},

	0x3F: { 'name': 'end3',
		'end': True,
	},

	0x40: { 'name': 'atk40',
		'param_names': ['address'],
		'param_types': [Pointer],
	},

	0x41: { 'name': 'callatk',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x42: { 'name': 'jumpiftype2',
		'param_names': ['bank', 'type', 'address'],
		'param_types': [Target, Type, BattleScriptPointer],
	},

	0x43: { 'name': 'jumpifabilitypresent',
		'param_names': ['ability', 'address'],
		'param_types': [Ability, BattleScriptPointer],
	},

	0x44: { 'name': 'atk44',
	},

	0x45: { 'name': 'playanimation',
		'param_names': ['bank', 'animation', 'var_address'],
		'param_types': [Target, Byte, Pointer],
	},

	0x46: { 'name': 'atk46',
		'param_names': ['bank', 'address', 'int'],
		'param_types': [Byte, Pointer, Pointer],
	},

	0x47: { 'name': 'atk47',
	},

	0x48: { 'name': 'playstatchangeanimation',
		'param_names': ['bank', 'color', 'byte'],
		'param_types': [Target, Byte, Byte],
	},

	0x49: { 'name': 'atk49',
		'param_names': ['byte1', 'byte2'],
		'param_types': [Byte, Byte],
	},

	0x4A: { 'name': 'damagecalc2',
	},

	0x4B: { 'name': 'atk4b',
	},

	0x4C: { 'name': 'switch1',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x4D: { 'name': 'switch2',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x4E: { 'name': 'switch3',
		'param_names': ['bank', 'byte'],
		'param_types': [Target, Byte],
	},

	0x4F: { 'name': 'jumpifcannotswitch',
		'param_names': ['bank', 'address'],
		'param_types': [Target, BattleScriptPointer],
	},

	0x50: { 'name': 'openpartyscreen',
		'param_names': ['bank', 'address'],
		'param_types': [Target, BattleScriptPointer],
	},

	0x51: { 'name': 'atk51',
		'param_names': ['bank', 'param2'],
		'param_types': [Target, Byte],
	},

	0x52: { 'name': 'atk52',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x53: { 'name': 'atk53',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x54: { 'name': 'atk54',
		'param_names': ['word'],
		'param_types': [Word],
	},

	0x55: { 'name': 'atk55',
		'param_names': ['int'],
		'param_types': [Pointer],
	},

	0x56: { 'name': 'atk56',
		'param_names': ['bank_or_side'],
		'param_types': [Byte],
	},

	0x57: { 'name': 'atk57',
	},

	0x58: { 'name': 'atk58',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x59: { 'name': 'checkiflearnmoveinbattle',
		'param_names': ['param1', 'param2', 'bank_maybe'],
		'param_types': [BattleScriptPointer, BattleScriptPointer, Byte],
	},

	0x5A: { 'name': 'atk5a',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x5B: { 'name': 'atk5b',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x5C: { 'name': 'atk5c',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x5D: { 'name': 'atk5d',
	},

	0x5E: { 'name': 'atk5e',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x5F: { 'name': 'atk5f',
	},

	0x60: { 'name': 'atk60',
		'param_names': ['byte'],
		'param_types': [Byte],
	},

	0x61: { 'name': 'atk61',
		'param_names': ['bank_or_side'],
		'param_types': [Byte],
	},

	0x62: { 'name': 'atk62',
		'param_names': ['bank_or_side'],
		'param_types': [Byte],
	},

	0x63: { 'name': 'jumptoattack',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x64: { 'name': 'statusanimation',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x65: { 'name': 'atk65',
		'param_names': ['bank_or_side', 'address'],
		'param_types': [Byte, Pointer],
	},

	0x66: { 'name': 'atk66',
		'param_names': ['bank_or_side', 'bank_or_side2', 'secondary_status'],
		'param_types': [Byte, Byte, SecondaryStatus],
	},

	0x67: { 'name': 'atk67',
	},

	0x68: { 'name': 'atk68',
	},

	0x69: { 'name': 'atk69',
	},

	0x6A: { 'name': 'removeitem',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x6B: { 'name': 'atk6b',
	},

	0x6C: { 'name': 'atk6c',
	},

	0x6D: { 'name': 'atk6d',
	},

	0x6E: { 'name': 'atk6e',
	},

	0x6F: { 'name': 'atk6f',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x70: { 'name': 'atk70',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x71: { 'name': 'atk71',
	},

	0x72: { 'name': 'atk72',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x73: { 'name': 'atk73',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0x74: { 'name': 'atk74',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

	0x75: { 'name': 'atk75',
	},

	0x76: { 'name': 'atk76',
		'param_names': ['bank', 'byte'],
		'param_types': [Target, Byte],
	},

	0x77: { 'name': 'setprotect',
	},

	0x78: { 'name': 'faintifabilitynotdamp',
	},

	0x79: { 'name': 'setuserhptozero',
	},

	0x7A: { 'name': 'jumpwhiletargetvalid',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x7B: { 'name': 'setdamageasrestorehalfmaxhp',
		'param_names': ['address', 'byte'],
		'param_types': [BattleScriptPointer, Byte],
	},

	0x7C: { 'name': 'jumptolastusedattack',
	},

	0x7D: { 'name': 'setrain',
	},

	0x7E: { 'name': 'setreflect',
	},

	0x7F: { 'name': 'setleechseed',
	},

	0x80: { 'name': 'manipulatedamage',
		'param_names': ['id'],
		'param_types': [Byte],
	},

	0x81: { 'name': 'setrest',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x82: { 'name': 'jumpifnotfirstturn',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x83: { 'name': 'nop3',
	},

	0x84: { 'name': 'jumpifcannotsleep',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x85: { 'name': 'stockpile',
	},

	0x86: { 'name': 'stockpiletobasedamage',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x87: { 'name': 'stockpiletohprecovery',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x88: { 'name': 'negativedamage',
	},

	0x89: { 'name': 'statbuffchange',
		'param_names': ['target', 'address'],
		'param_types': [Byte, BattleScriptPointer],
	},

	0x8A: { 'name': 'normalisebuffs',
	},

	0x8B: { 'name': 'setbide',
	},

	0x8C: { 'name': 'confuseifrepeatingattackends',
	},

	0x8D: { 'name': 'setloopcounter',
		'param_names': ['count'],
		'param_types': [Byte],
	},

	0x8E: { 'name': 'atk8e',
	},

	0x8F: { 'name': 'forcerandomswitch',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x90: { 'name': 'changetypestoenemyattacktype',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x91: { 'name': 'givemoney',
	},

	0x92: { 'name': 'setlightscreen',
	},

	0x93: { 'name': 'koplussomethings',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x94: { 'name': 'gethalfcurrentenemyhp',
	},

	0x95: { 'name': 'setsandstorm',
	},

	0x96: { 'name': 'weatherdamage',
	},

	0x97: { 'name': 'tryinfatuatetarget',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x98: { 'name': 'atk98',
		'param_names': ['byte'],
		'param_types': [Byte],
	},

	0x99: { 'name': 'setmisteffect',
	},

	0x9A: { 'name': 'setincreasedcriticalchance',
	},

	0x9B: { 'name': 'transformdataexecution',
	},

	0x9C: { 'name': 'setsubstituteeffect',
	},

	0x9D: { 'name': 'copyattack',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0x9E: { 'name': 'metronomeeffect',
	},

	0x9F: { 'name': 'nightshadedamageeffect',
	},

	0xA0: { 'name': 'psywavedamageeffect',
	},

	0xA1: { 'name': 'counterdamagecalculator',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xA2: { 'name': 'mirrorcoatdamagecalculator',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xA3: { 'name': 'disablelastusedattack',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xA4: { 'name': 'setencore',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xA5: { 'name': 'painsplitdamagecalculator',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xA6: { 'name': 'settypetorandomresistance',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xA7: { 'name': 'setalwayshitflag',
	},

	0xA8: { 'name': 'copymovepermanently',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xA9: { 'name': 'selectrandommovefromusermoves',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xAA: { 'name': 'destinybondeffect',
	},

	0xAB: { 'name': 'atkab',
	},

	0xAC: { 'name': 'remaininghptopower',
	},

	0xAD: { 'name': 'reducepprandom',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xAE: { 'name': 'clearstatusifnotsoundproofed',
	},

	0xAF: { 'name': 'cursetarget',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xB0: { 'name': 'setspikes',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xB1: { 'name': 'setforesight',
	},

	0xB2: { 'name': 'setperishsong',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xB3: { 'name': 'rolloutdamagecalculation',
	},

	0xB4: { 'name': 'jumpifconfusedandattackmaxed',
		'param_names': ['bank', 'address'],
		'param_types': [Byte, BattleScriptPointer],
	},

	0xB5: { 'name': 'furycutterdamagecalculation',
	},

	0xB6: { 'name': 'happinesstodamagecalculation',
	},

	0xB7: { 'name': 'presentdamagecalculation',
	},

	0xB8: { 'name': 'setsafeguard',
	},

	0xB9: { 'name': 'magnitudedamagecalculation',
	},

	0xBA: { 'name': 'atkba',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xBB: { 'name': 'setsunny',
	},

	0xBC: { 'name': 'maxattackhalvehp',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xBD: { 'name': 'copyfoestats',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xBE: { 'name': 'breakfree',
	},

	0xBF: { 'name': 'setcurled',
	},

	0xC0: { 'name': 'recoverbasedonsunlight',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xC1: { 'name': 'hiddenpowerdamagecalculation',
	},

	0xC2: { 'name': 'selectnexttarget',
	},

	0xC3: { 'name': 'setfutureattack',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xC4: { 'name': 'beatupcalculation',
		'param_names': ['address1', 'address2'],
		'param_types': [BattleScriptPointer, BattleScriptPointer],
	},

	0xC5: { 'name': 'hidepreattack',
	},

	0xC6: { 'name': 'unhidepostattack',
	},

	0xC7: { 'name': 'setminimize',
	},

	0xC8: { 'name': 'sethail',
	},

	0xC9: { 'name': 'jumpifattackandspecialattackcannotfall',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xCA: { 'name': 'setforcedtarget',
	},

	0xCB: { 'name': 'setcharge',
	},

	0xCC: { 'name': 'callterrainattack',
	},

	0xCD: { 'name': 'cureifburnedparalysedorpoisoned',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xCE: { 'name': 'settorment',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xCF: { 'name': 'jumpifnodamage',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD0: { 'name': 'settaunt',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD1: { 'name': 'sethelpinghand',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD2: { 'name': 'itemswap',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD3: { 'name': 'copyability',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD4: { 'name': 'atkd4',
		'param_names': ['byte', 'address'],
		'param_types': [Byte, BattleScriptPointer],
	},

	0xD5: { 'name': 'setroots',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD6: { 'name': 'doubledamagedealtifdamaged',
	},

	0xD7: { 'name': 'setyawn',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD8: { 'name': 'setdamagetohealthdifference',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xD9: { 'name': 'scaledamagebyhealthratio',
	},

	0xDA: { 'name': 'abilityswap',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xDB: { 'name': 'imprisoneffect',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xDC: { 'name': 'setgrudge',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xDD: { 'name': 'weightdamagecalculation',
	},

	0xDE: { 'name': 'assistattackselect',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xDF: { 'name': 'setmagiccoat',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xE0: { 'name': 'setstealstatchange',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xE1: { 'name': 'atke1',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xE2: { 'name': 'atke2',
		'param_names': ['bank'],
		'param_types': [Target],
	},

	0xE3: { 'name': 'jumpiffainted',
		'param_names': ['bank', 'address'],
		'param_types': [Target, BattleScriptPointer],
	},

	0xE4: { 'name': 'naturepowereffect',
	},

	0xE5: { 'name': 'pickupitemcalculation',
	},

	0xE6: { 'name': 'actualcastformswitch',
	},

	0xE7: { 'name': 'castformswitch',
	},

	0xE8: { 'name': 'settypebasedhalvers',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xE9: { 'name': 'seteffectbyweather',
	},

	0xEA: { 'name': 'recycleitem',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xEB: { 'name': 'settypetoterrain',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xEC: { 'name': 'pursuitwhenswitched',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xED: { 'name': 'snatchmove',
	},

	0xEE: { 'name': 'removereflectlightscreen',
	},

	0xEF: { 'name': 'pokemoncatchfunction',
	},

	0xF0: { 'name': 'catchpoke',
	},

	0xF1: { 'name': 'capturesomethingf1',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xF2: { 'name': 'capturesomethingf2',
	},

	0xF3: { 'name': 'capturesomethingf3',
		'param_names': ['address'],
		'param_types': [BattleScriptPointer],
	},

	0xF4: { 'name': 'removehp',
	},

	0xF5: { 'name': 'curestatusfirstword',
	},

	0xF6: { 'name': 'atkf6',
	},

	0xF7: { 'name': 'activesidesomething',
	},

	# FR only?
	0xF8: { 'name': 'atkf8',
		'param_names': ['bank'],
		'param_types': [Byte],
	},

}

battle_script_command_classes = make_command_classes(battle_script_commands, 'BattleCommand_')


def print_battle_script_macros():
	from create_event_macros import make_event_macro
	lines = []
	for byte, cmd in sorted(battle_script_commands.items()):
		if cmd.has_key('macro'):
			lines += [cmd['macro']]
			continue
		lines += [make_event_macro(byte, cmd).rstrip()]
	text = '\n\n'.join(lines)
	text = '\n'.join(line.rstrip() for line in text.split('\n'))
	print text


if __name__ == '__main__':
	args = get_args([
		('address', {
			'nargs': '*',
		}),
		('-i', {
			'dest': 'insert',
			'action': 'store_true',
		}),
		('--macros', {
			'action': 'store_true',
		}),
	])
	if args.macros:
		print_battle_script_macros()
	elif args.insert:
		for address in args.address:
			address = int(address, 16)
			insert_recursive(BattleScript, address, paths=['data/data1.s'])
	else:
		for address in args.address:
			address = int(address, 16)
			print just_do_it(BattleScript, address, 'ruby')
