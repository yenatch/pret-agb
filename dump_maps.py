import os

from event_script import *
import versions
import find_files

g = ''

def dump_maps(version):
	rom = version['baserom']
	address = version['map_groups_address']
	chunks = get_maps(version)
	label = Label(address, asm='gMapGroups')
	chunks[address].label = label
	return chunks.values()

def get_maps(version):
	return recursive_parse(MapGroups, version['map_groups_address'], version=version)

class MapBorder(BinFile):
	size = 4 * 2
class MapBorderPointer(Pointer):
	target = MapBorder
	include_address = False
	target_arg_names = ['filename']

class MapBlockdata(BinFile):
	@property
	def size(self):
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
		map_name = get_map_name(self.version.get('map_groups'), self.__dict__.get('group'), self.__dict__.get('num'))
		blockdata_p = self.params['blockdata_p']
		blockdata_p.width = self.params['width'].value
		blockdata_p.height = self.params['height'].value
		blockdata_p.filename = 'data/maps/{}/map.bin'.format(map_name)
		border_p = self.params['border_p']
		border_p.filename = 'data/maps/{}/border.bin'.format(map_name)

class MapAttributesPointer(Pointer):
	target = MapAttributes
	include_address = False
	target_arg_names = ['group', 'num']

class MapObject(Macro):
	name = 'object_event'
	param_classes = [
		('index', Byte),
		('sprite', FieldGFXId),
		('replacement', Byte),
		('x', Int16),
		('y', Int16),
		('elevation', Byte),
		('movement_type', Byte),
		('radius', Byte),
		(Byte), # filler
		('trainer_type', Word),
		('sight_radius_tree_etc', Word),
		('script', EventScriptPointer),
		('event_flag', Word),
		(Byte), # filler
		(Byte), # filler
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
		('x', Int16),
		('y', Int16),
		('trigger', Byte),
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
		('x', Int16),
		('y', Int16),
		('elevation', Byte),
		Byte,
		WordOrVariable,
		Word,
		Word,
		('script', EventScriptPointer),
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
		('x', Int16),
		('y', Int16),
		Byte,
		('kind', Byte),
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

class MapEvents(Macro):
	name = 'map_events'
	is_global = True
	param_classes = [
		Byte, Byte, Byte, Byte,
		MapObjectsPointer, MapWarpsPointer, MapCoordEventsPointer, MapBGEventsPointer,
	]
	def parse(self):
		ParamGroup.parse(self)
		for byte, pointer in zip(self.chunks[:4], self.chunks[4:]):
			pointer.count = byte.value
	@property
	def asm(self):
		return ', '.join(chunk.asm for chunk in self.chunks[4:])

class MapEventsPointer(Pointer):
	target = MapEvents
	include_address = False

class MapScript1(ParamGroup):
	param_classes = [EventScript]

class MapScript1Pointer(Pointer):
	target = MapScript1

class MapScript2Entry(Macro):
	name = 'map_script_2'
	param_classes = [WordOrVariable, Word, EventScriptPointer]

class MapScript2(ParamGroup):
	param_classes = [Word]
	def parse(self):
		self.param_classes = list(self.param_classes)
		while True:
			ParamGroup.parse(self)
			if self.chunks[-1].value == 0:
				break
			self.param_classes.insert(-1, MapScript2Entry)

class MapScript2Pointer(Pointer):
	target = MapScript2

class MapScriptEntry(Macro):
	name = 'map_script'
	param_classes = [('type', Byte)]
	def parse(self):
		self.param_classes = list(self.param_classes)
		Macro.parse(self)
		value = self.params['type'].value
		if value == 0:
			raise Exception('MapScriptEntry is a terminator')
		if value in (1, 3, 5, 6, 7):
			self.param_classes += [MapScript1Pointer]
		else:
			self.param_classes += [MapScript2Pointer]
		Macro.parse(self)

class MapScripts(ParamGroup):
	is_global = True
	param_classes = [Byte]
	def parse(self):
		self.param_classes = list(self.param_classes)
		while True:
			ParamGroup.parse(self)
			if self.chunks[-1].value == 0:
				break
			self.param_classes.insert(-1, MapScriptEntry)

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
		('events_p', MapEventsPointer),
		('scripts_p', MapScriptsPointer),
		('connections_p', MapConnectionsPointer),
		('bgm', Word),
		('index', Word),
		('location', Byte),
		('visibility', Byte),
		('weather', Byte),
		('type', Byte),
		Word,
		('show_location', Byte),
		('battle_scene', Byte),
	]

	def parse(self):
		ParamGroup.parse(self)
		attributes_p = self.params['attributes_p']
		if hasattr(self, 'group'):
			attributes_p.group = self.group
		if hasattr(self, 'num'):
			attributes_p.num = self.num

	@property
	def context_label(self):
		map_name = get_map_name(self.version.get('map_groups'), self.group, self.num)
		if map_name:
			return g + map_name
		return g

class MapPointer(Pointer):
	target = Map
	target_arg_names = ['group', 'num', 'map_name']

	@property
	def context_label(self):
		map_name = None
		if hasattr(self, 'group') and hasattr(self, 'num'):
			map_name = get_map_name(self.version.get('map_groups'), self.group, self.num)
		if hasattr(self, 'map_name'):
			map_name = self.map_name
		if map_name:
			return g + map_name
		return g

class MapGroup(List):
    def parse(self):
        map_groups = self.version['map_groups']
        self.param_classes = [MapPointer]
        self.count = len(map_groups.get(self.__dict__.get('group'), []))
        List.parse(self)
        for i, chunk in enumerate(self.chunks):
            chunk.group = self.group
            chunk.num = i
            label_name = g + get_map_name(map_groups, self.group, i)
            label = Label(chunk.real_address)
            label.asm = label_name
            chunk.chunks += [label]
            chunk.label = label

class MapGroupPointer(Pointer):
    target = MapGroup
    target_arg_names = ['group']

class MapGroups(List):
    @property
    def address(self):
        return self.version['map_groups_address']
    param_classes = [MapGroupPointer]
    def parse(self):
        self.count = len(self.version['map_groups'])
        List.parse(self)
        for i, chunk in enumerate(self.chunks):
            chunk.group = i
            label_name = 'gMapGroup{}'.format(i)
            label = Label(chunk.real_address)
            label.asm = label_name
            chunk.chunks += [label]
            chunk.label = label


if __name__ == '__main__':
    from argparse import ArgumentParser as ap
    ap = ap()
    ap.add_argument('version', nargs='?', default='ruby')
    ap.add_argument('--debug', action='store_true')
    args = ap.parse_args()
    version = versions.__dict__[args.version]
    setup_version(version)
    if args.debug:
        print print_nested_chunks(dump_maps(version))
    else:
        chunks = flatten_nested_chunks(dump_maps(version))
        for path in version['maps_paths']:
            insert_chunks(chunks, path, version)
        create_files_of_chunks(chunks)
        find_files.main(version)
