from new import classobj

from event_script import *

map_group_pointers_address = 0x486578

def get_map_name(group, num):
	group = map_groups.get(group)
	if group:
		label = group.get(num)
		if label:
			return label

def dump_maps():
	label = Label(map_group_pointers_address, asm='gMapGroups')
	chunks = recursive_parse(MapGroups, map_group_pointers_address)
	chunks[map_group_pointers_address].label = label
	return chunks.values()

class List(Chunk):
	param_classes = []
	def parse(self):
		Chunk.parse(self)
		self.chunks = []
		address = self.address
		count = getattr(self, 'count', 0)
		for i in xrange(count):
			for item in self.param_classes:
				name = None
				try:
					name, param_class = item
				except:
					param_class = item
				param = param_class(address)
				self.chunks += [param]
				address += param.length
		self.last_address = address

class ItemList(List):
	param_classes = [Item]
	def parse(self):
		self.count = 1
		List.parse(self)
		while self.chunks[-1].value != 0:
			self.count += 1
			List.parse(self)
class Pokemart(ParamGroup):
	param_classes = [ItemList, EventScript]

PokemartPointer.target = Pokemart

class MapGroup(List):
    def parse(self):
        self.param_classes = [MapPointer]
        self.count = len(map_groups[self.group])
        List.parse(self)
        for i, chunk in enumerate(self.chunks):
            chunk.group = self.group
            chunk.num = i
            label_name = 'g' + map_groups[self.group][i]
            label = Label(chunk.real_address)
            label.asm = label_name
            chunk.chunks += [label]
            chunk.label = label

class MapGroupPointer(Pointer):
    target = MapGroup
    target_arg_names = ['group']

class MapGroups(List):
    param_classes = [MapGroupPointer]
    def parse(self):
        self.count = len(map_groups)
        List.parse(self)
        for i, chunk in enumerate(self.chunks):
            chunk.group = i
            label_name = 'gMapGroup{}'.format(i)
            label = Label(chunk.real_address)
            label.asm = label_name
            chunk.chunks += [label]
            chunk.label = label

class BinFile(Chunk):
	name = '.incbin'
	def parse(self):
		Chunk.parse(self)
		address = self.address
		address += self.length
		self.value = self.rom[self.address:address]
		self.last_address = address
	@property
	def asm(self):
		return '"' + self.filename + '"'
	def to_asm(self):
		return '\t' + self.name + ' ' + self.asm
	def create_file(self):
		with open(self.filename, 'wb') as out:
			out.write(bytearray(self.value))

class MapBorder(BinFile):
	length = 4 * 2
class MapBorderPointer(Pointer):
	target = MapBorder
	include_address = False
	target_arg_names = ['filename']

class MapBlockdata(BinFile):
	@property
	def length(self):
		return self.width * self.height * 2
class MapBlockdataPointer(Pointer):
	target = MapBlockdata
	include_address = False
	target_arg_names = ['width', 'height', 'filename']

class TilesetImage(Chunk): pass
class TilesetImagePointer(Pointer):
	target = TilesetImage
class TilesetPalettes(Chunk): pass
class TilesetPalettesPointer(Pointer):
	target = TilesetPalettes
class TilesetBlocks(Chunk): pass
class TilesetBlocksPointer(Pointer):
	target = TilesetBlocks
class TilesetAnimations(Chunk): pass
class TilesetAnimationsPointer(Pointer):
	target = TilesetAnimations
class TilesetBehavior(Chunk): pass
class TilesetBehaviorPointer(ThumbPointer): pass
#	target = TilesetBehavior

class Tileset(ParamGroup):
	param_classes = [
		Byte, Byte, Byte, Byte,
		TilesetImagePointer, TilesetPalettesPointer, TilesetBlocksPointer, TilesetAnimationsPointer, TilesetBehaviorPointer,
	]
class TilesetPointer(Pointer):
	target = Tileset
	include_address = False

class Tileset2(Tileset): pass
class Tileset2Pointer(TilesetPointer):
	target = Tileset2

class MapAttributes(ParamGroup):
	param_classes = [
		('width', Int), ('height', Int),
		('border_p', MapBorderPointer),
		('blockdata_p', MapBlockdataPointer),
		TilesetPointer,
		Tileset2Pointer,
		#Byte, Byte, # FRLG
	]
	def parse(self):
		ParamGroup.parse(self)
		map_name = get_map_name(self.group, self.num)
		blockdata_p = self.params['blockdata_p']
		blockdata_p.width = self.params['width'].value
		blockdata_p.height = self.params['height'].value
		blockdata_p.filename = 'maps/{}.blk'.format(map_name)
		border_p = self.params['border_p']
		border_p.filename = 'maps/{}_border.blk'.format(map_name)

class MapAttributesPointer(Pointer):
	target = MapAttributes
	include_address = False
	target_arg_names = ['group', 'num']

class MapObject(Macro):
	name = 'object_event'
	param_classes = [
		Byte, Word,
	] + [Byte] * 13 + [
		EventScriptPointer,
		Word, Byte, Byte,
	]

class MapObjects(List):
	param_classes = [MapObject]

class MapObjectsPointer(Pointer):
	target = MapObjects
	target_arg_names = ['count']
	include_address = False

class MapWarp(Macro):
	name = 'warp_def'
	param_classes = [
		('x', Word),
		('y', Word),
		Byte,
		('warp', Byte),
		('map', WarpMapId),
	]
class MapWarps(List):
	param_classes = [MapWarp]
class MapWarpsPointer(Pointer):
	target = MapWarps
	target_arg_names = ['count']
	include_address = False

class MapCoordEvent(Macro):
	name = 'coord_event'
	param_classes = [
		Word, Word,
		Byte, Byte,
		Word, Word, Word,
		EventScriptPointer,
	]

class MapCoordEvents(List):
	param_classes = [MapCoordEvent]

class MapCoordEventsPointer(Pointer):
	target = MapCoordEvents
	target_arg_names = ['count']
	include_address = False

class HiddenItem(ParamGroup):
	param_classes = [ Item, Byte, Byte, ]

class MapBGEvent(Macro):
	name = 'bg_event'
	param_classes = [
		Word, Word,
		Byte, ('kind', Byte),
		Word,
	]
	def parse(self):
		ParamGroup.parse(self)
		self.param_classes = list(self.param_classes)
		kind = self.params['kind'].value
		if kind in (5, 6, 7, 8):
			self.param_classes += [HiddenItem]
		else:
			self.param_classes += [EventScriptPointer]
		ParamGroup.parse(self)

class MapBGEvents(List):
	param_classes = [MapBGEvent]

class MapBGEventsPointer(Pointer):
	target = MapBGEvents
	target_arg_names = ['count']
	include_address = False

class MapEvents(ParamGroup):
	param_classes = [
		Byte, Byte, Byte, Byte,
		MapObjectsPointer, MapWarpsPointer, MapCoordEventsPointer, MapBGEventsPointer,
	]
	def parse(self):
		ParamGroup.parse(self)
		for byte, pointer in zip(self.chunks[:4], self.chunks[4:]):
			pointer.count = byte.value

class MapEventsPointer(Pointer):
	target = MapEvents
	include_address = False

class MapScript1(ParamGroup):
	param_classes = [EventScript]

class MapScript1Pointer(Pointer):
	target = MapScript1

class MapScript2(ParamGroup):
	param_classes = [Word]
	def parse(self):
		self.param_classes = list(self.param_classes)
		while True:
			ParamGroup.parse(self)
			if self.chunks[-1].value == 0:
				break
			self.param_classes += [Word, EventScriptPointer] + [Word]

class MapScript2Pointer(Pointer):
	target = MapScript2

class MapScripts(ParamGroup):
	param_classes = [Byte]
	def parse(self):
		self.param_classes = list(self.param_classes)
		while True:
			ParamGroup.parse(self)
			byte = self.chunks[-1].value
			if byte == 0:
				break
			if byte in (1, 3, 5, 6, 7):
				self.param_classes += [MapScript1Pointer] + [Byte]
			else:
				self.param_classes += [MapScript2Pointer] + [Byte]

class MapScriptsPointer(Pointer):
	target = MapScripts
	include_address = False

class ConnectionDirection(Int):
	"""Does not stand on its own. Should be used only with MapConnection."""
	directions = [
		'0',
		'down', 'up', 'left', 'right',
		'dive', 'emerge',
	]
	@property
	def asm(self):
		return self.directions[self.value]

class SignedInt(Int):
	def parse(self):
		Int.parse(self)
		self.value -= (self.value & 0x80000000) * 2
	@property
	def asm(self):
		return str(self.value)

class MapConnection(Macro):
	name = 'connection'
	param_classes = [
		('direction', ConnectionDirection),
		('offset', SignedInt),
		('map', MapId),
		#('map_group', MapGroupId),
		#('map_number', MapNumberId),
		Word, # filler
	]

class MapConnectionsList(List):
	param_classes = [MapConnection]

class MapConnectionsListPointer(Pointer):
	target = MapConnectionsList
	target_arg_names = ['count']
	include_address = False

class MapConnections(ParamGroup):
	param_classes = [
		('count', Int),
		('pointer', MapConnectionsListPointer),
	]
	def parse(self):
		ParamGroup.parse(self)
		self.params['pointer'].count = self.params['count'].value
	
class MapConnectionsPointer(Pointer):
	target = MapConnections
	include_address = False

class Map(ParamGroup):
	param_classes = [
		('attributes_p', MapAttributesPointer),
		MapEventsPointer,
		MapScriptsPointer,
		MapConnectionsPointer,
		Word, Word, Byte, Byte, Byte, Byte,
		Word, Byte, Byte,
	]

	def parse(self):
		ParamGroup.parse(self)
		attributes_p = self.params['attributes_p']
		attributes_p.group = self.group
		attributes_p.num = self.num

	@property
	def context_label(self):
		map_name = get_map_name(self.group, self.num)
		if map_name:
			return 'g' + map_name
		return 'g'

class MapPointer(Pointer):
	target = Map
	target_arg_names = ['group', 'num']

	@property
	def context_label(self):
		map_name = get_map_name(self.group, self.num)
		if map_name:
			return 'g' + map_name
		return 'g'


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
	0x91: { 'name': 'step_91',
	},
	0x92: { 'name': 'step_92',
	},
	0x96: { 'name': 'step_96',
	},
	0xfe: { 'name': 'step_end',
		'end': True,
	},
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
MovementPointer.target = Movement

if __name__ == '__main__':
    print print_nested_chunks(dump_maps())
