from script import *
import versions

class Graphic(BinFile):
	size = 32
	@property
	def filename(self):
		return 'graphics/unsorted/' + hex(self.address) + '.4bpp'

class GraphicPointer(Pointer):
	target = Graphic
	target_arg_names = ['size', 'filename']

class ObjTiles(Macro):
	name = 'obj_tiles'
	param_classes = [
		('address', GraphicPointer),
		('size', Word),
		('tag', Word),
	]
	_length = 8
	def parse(self):
		Macro.parse(self)
		address = self.params['address']
		size = self.params['size']
		tag = self.params['tag']
		if size.value % 32:
			raise Exception('ObjTiles at 0x{:x}: size {} is not a multiple of 32'.format(self.address, size.value))
		if not size.value:
			raise Exception('ObjTiles at 0x{:x}: size is {}'.format(self.address, size.value))
		if not tag.value:
			raise Exception('ObjTiles at 0x{:x}: tag is {}'.format(self.address, size.value))
		address.size = size.value

class RGB(Macro):
	"""
	Oops. This is not used. Palettes should be binary in normal circumstances.
	"""
	name = 'rgb'
	param_classes = [('value', Word)]
	def parse(self):
		Macro.parse(self)
		value = self.params['value'].value
		self.red = value & 0x1f
		self.green = (value >> 5) & 0x1f
		self.blue = (value >> 10) & 0x1f
	@property
	def asm(self):
		return ', '.join(map('{:2}'.format, [self.red, self.green, self.blue]))

class RGBPalette(ParamGroup):
	param_classes = [RGB] * 16

class Palette(BinFile):
	size = 2 * 16
	@property
	def filename(self):
		return 'graphics/unsorted/' + hex(self.address) + '.pal'

class PalPointer(Pointer):
	target = Palette
	target_arg_names = ['size', 'filename']

class ObjPal(Macro):
	name = 'obj_pal'
	param_classes = [
		('address', PalPointer),
		('tag', Word),
		('filler', Word),
	]
	_length = 8
	def parse(self):
		Macro.parse(self)
		address = self.params['address']
		tag = self.params['tag']
		filler = self.params['filler']
		if not address.value:
			raise Exception('ObjPal at 0x{:x}: address is {}'.format(self.address, address.value))
		if not tag.value:
			raise Exception('ObjPal at 0x{:x}: tag is {}'.format(self.address, tag.value))
		if filler.value:
			raise Exception('ObjPal at 0x{:x}: filler should be 0 (is {})'.format(self.address, filler.value))
	@property
	def asm(self):
		return ', '.join([self.params['address'].asm, self.params['tag'].asm])

class ObjTilesOrObjPal(ParamGroup):
	def parse(self):
		try:
			self.param_classes = [ObjTiles]
			ParamGroup.parse(self)
		except:
			self.param_classes = [ObjPal]
			ParamGroup.parse(self)

class ObjTilesList(List):
	param_classes = [ObjTilesOrObjPal]


def read_incbin(line):
	line = line.split('@')[0]
	params = line.split('.incbin')[1].split(',')
	return map(str.strip, params)

def dump_graphics(filename, version):
	setup_version(version)
	chunks = []
	for line in open(filename):
		if '.incbin "baserom.gba"' in line:
			_, start, length = read_incbin(line)
			start = int(start, 16)
			length = int(length, 16)
			count = length / ObjTiles._length
			if (not count) or length % ObjTiles._length:
				continue
			try:
				chunks_ = recursive_parse(
					ObjTilesList,
					start,
					count=count,
					version=version,
					rom=version['baserom']
				)
			except:
				continue
			chunks += chunks_.values()
	chunks = flatten_nested_chunks(chunks)
	for path in version['maps_paths']:
		insert_chunks(chunks, path, versions.ruby)
	if filename not in version['maps_paths']:
		insert_chunks(chunks, filename, versions.ruby)
	create_files_of_chunks(chunks)

def main():
	from argparse import ArgumentParser as ap
	ap = ap()
	ap.add_argument('filename')
	args = ap.parse_args()
	dump_graphics(args.filename, versions.ruby)

if __name__ == '__main__':
	main()
