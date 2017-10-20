"""This is where one-off dumps go to die.
"""

from script import *
from event_script import *
from dump_maps import *
from battle_script import *
from dump_graphics import *


class Specials(List):
	param_classes = [ThumbPointer]
	count = 0x558 / 4
	address = 0x14b194

class StdScripts(List):
	param_classes = [EventScriptPointer]
	count = 0x20 / 4
	address = 0x14b6ec

class gUnknown_0814B14C(List):
	param_classes = [Pointer]
	count = 0x48 / 4
	address = 0x14b14c

class UnreferencedMap1(MapAttributes):
	group = -1
	num = -1
	address = 0x2bf1e4

class UnreferencedMap2(MapAttributes):
	group = -1
	num = -1
	address = 0x2cf540 + 24

class MoveEffect(BattleScript):
	pass

class MoveEffectPointer(BattleScriptPointer):
	target = MoveEffect

class MoveEffects(List):
	param_classes = [MoveEffectPointer]
	count = 214
	address = 0x1d6bbc
	def parse(self):
		List.parse(self)
		for i, chunk in enumerate(self.chunks):
			constant = self.version.get('move_effect_constants', {}).get(i)
			if constant:
				label_name = 'MoveEffect_' + constant.title().replace('_', '')
				label = Label(chunk.real_address)
				label.asm = label_name
				chunk.chunks += [label]
				chunk.label = label

class gUnknown_081FAC4C(List):
	param_classes = [BattleScriptPointer]
	count = 39
	address = 0x1fac4c

class gUnknown_08401508(BattleTextList):
	count = 10
	address = 0x401508

class gUnknown_081D9E48(List):
	param_classes = [BattleScriptPointer]
	count = 24
	address = 0x1d9e48

class gUnknown_0842F6C0(List):
	param_classes = [Int, Pointer]
	count = 19
	address = 0x42f6c0
	atomic = True
	def to_asm(self):
		text = ''
		for num, pointer in zip(self.chunks[::2], self.chunks[1::2]):
			text += '\t.4byte {}, {}\n'.format(num.asm, pointer.asm)
		return text

class gUnknown_0840AE80(List):
	param_classes = [Pointer]
	count = 4
	address = 0x40ae80

class gUnknown_08402D08(ParamGroup):
	param_classes = [Pointer, Byte, Byte, Byte, Byte]
	atomic = True
	def to_asm(self):
		text = ''
		text += self.chunks[0].to_asm() + '\n'
		text += '\t.byte {}\n'.format(', '.join(x.asm for x in self.chunks[1:]))
		return text

class gUnknown_084017F0(List):
	param_classes = [Pointer, ThumbPointer]
	count = 3
	address = 0x4017f0

class gUnknown_083F7FC4(TerminatedList):
	address = 0x3f7fc4
	def terminator(self):
		return all(chunk.value == 0 for chunk in self.chunks[-5:])
	param_classes = [Byte, Byte, Byte, Byte, ThumbPointer]
	atomic = True
	def to_asm(self):
		text = ''
		for i in xrange(0, len(self.chunks), 5):
			text += '\t.byte {}\n'.format(', '.join(byte.asm for byte in self.chunks[i:i+4]))
			text += '\t.4byte {}\n'.format(self.chunks[i+4].asm)
		return text

class ObjTilesList(TerminatedList):
	def terminator(self):
		return self.chunks[-1].is_null()
	param_classes = [ObjTiles]

class ObjPalList(TerminatedList):
	def terminator(self):
		return self.chunks[-1].is_null()
	param_classes = [ObjPal]

class gUnknown_083ECF0C(List):
	count = 0x8c/4
	address = 0x3ecf0c
	param_classes = [ThumbPointer]

class gUnknown_083EC860(List):
	param_classes = [Pointer, Pointer, Pointer, Int]
	count = 10
	address = 0x3ec860
	atomic = True
	def to_asm(self):
		text = ''
		for i in xrange(0, len(self.chunks), 4):
			text += '\t.4byte {}\n'.format(', '.join(chunk.asm for chunk in self.chunks[i:i+4]))
		return text

class gUnknown_083E5730(List):
	param_classes = [Byte, Byte, Byte, Byte, Pointer]
	address = 0x3e5730
	count = 12
	atomic = True
	def to_asm(self):
		text = ''
		for i in xrange(0, len(self.chunks), 5):
			text += '\t.byte {}\n'.format(', '.join(chunk.asm for chunk in self.chunks[i:i+4]))
			text += '\t.4byte {}\n'.format(self.chunks[i+4].asm)
		return text

class gUnknown_083E57A4(gUnknown_083E5730):
	address = 0x3e57a4

class _4ByteParamGroup(ParamGroup):
	atomic = True
	def to_asm(self):
		text = '\t.4byte {}'.format(', '.join(chunk.asm for chunk in self.chunks))
		return text

class gUnknown_083E53E0(List):
	param_classes = [_4ByteParamGroup.extend(param_classes=[Int, Pointer, Pointer, Pointer])]
	address = 0x3e53e0
	count = 0x24

class gUnknown_083DB608(List):
	param_classes = [_4ByteParamGroup.extend(param_classes=[Int, Int, Int, Int, Pointer, Pointer, Int])]
	address = 0x3db608
	count = 4

class gUnknown_083DB6F4(List):
	param_classes = [_4ByteParamGroup.extend(param_classes=[Pointer, Pointer, Int])]
	address = 0x3db6f4
	count = 17

class SpriteAffineAnim(Chunk):
	pass

class gSpriteAffineAnimTable_83D603C(List):
	param_classes = [Pointer.to(SpriteAffineAnim)]
	address = 0x3d603c
	count = 20

class Unknown_83CE374_Params(ParamGroup):
	param_classes = [Byte] * 8 + [Pointer]
	atomic = True
	def to_asm(self):
		text = ''
		text += '\t.byte {}\n'.format(', '.join(chunk.asm for chunk in self.chunks[:8]))
		text += '\t.4byte {}\n'.format(self.chunks[8].asm)
		return text

class Unknown_83CE374(List):
	param_classes = [Unknown_83CE374_Params]
	address = 0x3ce374
	count = 3

class gUnknown_083CE048(List):
	param_classes = [Pointer]
	address = 0x3ce048
	count = 19

class gUnknown_083C1640(List):
	param_classes = [_4ByteParamGroup.extend(param_classes=[Pointer, ThumbPointer])]
	address = 0x3c1640
	count = 20

class gUnknown_083C1068(List):
	param_classes = [Pointer]
	address = 0x3c1068
	count = 8

class ParamGroup2(ParamGroup):
	atomic = True

class gUnknown_083B5A7C(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer] + [Byte] * 4)]
	count = 6
	address = 0x3b5a7c

class gUnknown_083B59C8(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer, Pointer])]
	count = 19
	address = 0x3b59c8

class gUnknown_083B5968(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer, Pointer])]
	count = 12
	address = 0x3b5968

class gUnknown_083B5910(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer, Pointer])]
	count = 11
	address = 0x3b5910

class gUnknown_083B58D8(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer, Pointer])]
	count = 7
	address = 0x3b58d8

class gUnknown_083B58C0(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer, Pointer])]
	count = 3
	address = 0x3b58c0

class gUnknown_083B57FC(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer] + [Byte] * 8)]
	count = 7
	address = 0x3b57fc

class gUnknown_083B57E4(List):
	param_classes = [ParamGroup2.extend(param_classes=[Pointer] + [Word] * 2)]
	count = 3
	address = 0x3b57e4

class gUnknown_0839F58C(List):
	param_classes = [ParamGroup2.extend(param_classes=[ThumbPointer, Int])]
	count = 14
	address = 0x39f58c

class gUnknown_0839B2C0(List):
	param_classes = [ParamGroup2.extend(param_classes=[TextPointer, ThumbPointer])]
	count = 9
	address = 0x39b2c0

class gUnknown_083762FC(List):
	param_classes = [ParamGroup2.extend(param_classes=[Int, ThumbPointer])]
	count = 14
	address = 0x3762fc

class gUnknown_08216308(List):
	param_classes = [ThumbPointer]
	count = 3
	address = 0x216308

class SpriteAnim(Chunk):
	pass

class gSpriteAnimTable_820AA34(List):
	param_classes = [Pointer.to(SpriteAnim)]
	count = 7
	address = 0x20aa34

class gUnknown_0820A784(List):
	param_classes = [ObjTiles]
	count = 3
	address = 0x20a784


import subprocess
def shell(*args, **kwargs):
	kwargs.setdefault('shell', True)
	kwargs.setdefault('stdout', subprocess.PIPE)
	p = subprocess.Popen(*args, **kwargs)
	return p.communicate()[0]

class DirectSoundMetadata(ParamGroup):
	param_classes = [
		('format', Int),
		('note', Word),
		('pitch', Word),
		('loop_start', Int),
		('length', Int),
	]
	atomic = True
	def to_asm(self):
		return '\t.incbin "{}"'.format(self.filename)
	def create_file(self):
		data = bytearray(self.rom[self.address + 4 : self.address + 4 + 8])
		open(self.filename, 'wb').write(data)

class CompressedPcm(BinFile):
	def create_file(self):
		filename = self.filename
		data = bytearray(self.rom[self.address:self.address + self.size * 2])
		with open(filename, 'wb') as out:
			out.write(data)
		uncompressed_filename = filename.replace('.rl', '')
		shell('tools/gbagfx/gbagfx {} {}'.format(filename, uncompressed_filename))

		# for good measure. we could also just delete the fake .rl
		shell('tools/gbagfx/gbagfx {} {}'.format(uncompressed_filename, filename))
		self.size = len(bytearray(open(filename, 'rb').read()))

class CryPcm(CompressedPcm):
	size = 0

class DirectSoundPcm(BinFile):
	size = 0

class CryDirectSound(ParamGroup):
	param_classes = []

class RealCryDirectSound(ParamGroup):
	param_classes = [
		('format', Int),
		('metadata', DirectSoundMetadata),
		('pcm', CryPcm),
	]
	is_global = True
	def parse(self):
		ParamGroup.parse(self)
		metadata = self.params['metadata']
		pcm = self.params['pcm']
		filename_base = 'sound/direct_sound_samples/8{:06X}'.format(self.address)
		metadata.filename = '{}.bin'.format(filename_base)
		metadata.create_file()

		pcm.filename = '{}.pcm.rl'.format(filename_base)
		pcm.size = metadata.params['length'].value
		pcm.create_file()
		pcm.parse()

class Cry(Macro):
	name = 'cry'
	param_classes = [
		Byte, Byte, Byte, Byte,
		('address', Pointer.to(CryDirectSound)),
		Byte, Byte, Byte, Byte,
	]
	@property
	def asm(self):
		return self.params['address'].asm

class Cries(List):
	param_classes = [Cry]
	count = 388

class Cries_8452590(Cries):
	address = 0x452590

class Cries_84537C0(Cries):
	address = 0x4537c0


bad_labels = [
	'gUnknown_081D8E4A', 'gUnknown_081D8E37', 'gUnknown_081D8E44', 'gUnknown_081D94DA', 'gUnknown_081D8E02', 'gUnknown_081D8E0D', 'gUnknown_081D8DBE', 'gUnknown_081D8DCE', 'gUnknown_081D8E02', 'gUnknown_081D8DD1', 'gUnknown_081D8E29', 'gUnknown_081D8E14', 'gUnknown_081D8E22', 'gUnknown_081D8E30', 'gUnknown_081D8E4E', 'gUnknown_081D8E3B', 'gUnknown_081D8E3B', 'gUnknown_081D9144', 'gUnknown_081D937C', 'gUnknown_081D938B', 'gUnknown_081D9464', 'gUnknown_081D9369', 'gUnknown_081D9365', 'gUnknown_081D9030', 'gUnknown_081D9030', 'gUnknown_081D9030', 'gUnknown_081D9041', 'gUnknown_081D939A', 'gUnknown_081D8F62', 'gUnknown_081D8FFF', 'gUnknown_081D8F7D', 'gUnknown_081D9016', 'gUnknown_081D9008', 'gUnknown_081D8FFF', 'gUnknown_081D8F7D', 'gUnknown_081D93D1', 'gUnknown_081D904B', 'gUnknown_081D9518', 'gUnknown_081D9518', 'gUnknown_081D953A', 'gUnknown_081D9613', 'gUnknown_081D9624', 'gUnknown_081D95E2', 'gUnknown_081D95F4', 'gUnknown_081D950F', 'gUnknown_081D957E', 'gUnknown_081D9587', 'gUnknown_081D9148', 'gUnknown_081D914F', 'gUnknown_081D964C', 'gUnknown_081D92D7', 'gUnknown_081D9202', 'gUnknown_081D921D', 'gUnknown_081D8C72', 'gUnknown_081D8C7B', 'gUnknown_081D94FB', 'gUnknown_081D94EE', 'gUnknown_081D94FB', 'gUnknown_081D9545', 'gUnknown_081D9552', 'gUnknown_081D7956', 'gUnknown_081D9573', 'gUnknown_081D9139', 'gUnknown_081D938F', 'gUnknown_081D9459', 'gUnknown_081D9595', 'gUnknown_081D95D4', 'gUnknown_081D9566', 'gUnknown_081D9608', 'gUnknown_081D95FB', 'gUnknown_081D90A7', 'gUnknown_081D90B2', 'gUnknown_081D90F1', 'gUnknown_081D9552', 'gUnknown_081D901D', 'gUnknown_081D9704', 'gUnknown_081D9744', 'gUnknown_081D97FE', 'gUnknown_081D977D', 'gUnknown_081D9730', 'gUnknown_081D9758', 'gUnknown_081D9718', 'gUnknown_081D9843', 'gUnknown_081D9842', 'gUnknown_081D9843', 'gUnknown_081D9842', 'gUnknown_081D987C', 'gUnknown_081D987B', 'gUnknown_081D987C', 'gUnknown_081D987B', 'gUnknown_081D9866', 'gUnknown_081D9865', 'gUnknown_081D977D', 'gUnknown_081D977D', 'gUnknown_081D978C', 'gUnknown_081D9726', 'gUnknown_081D9795', 'gUnknown_081D6F62', 'gUnknown_081D936D', 'gUnknown_081D946F', 'gUnknown_081D9812', 'gUnknown_081D9487', 'gUnknown_081D8EEF', 'gUnknown_081D8EEF', 'gUnknown_081D94A9', 'gUnknown_081D94A2', 'gUnknown_081D98BD', 'gUnknown_081D98A5', 'gUnknown_081D98A5', 'gUnknown_081D98B1', 'gUnknown_081D98BD', 'gUnknown_081D98BD', 'gUnknown_081D98D7', 'gUnknown_081D71E5', 'gUnknown_081D7276', 'gUnknown_081D71E5', 'gUnknown_081D7276', 'gUnknown_081D96F6', 'gUnknown_081D9224', 'gUnknown_081D92C0', 'gUnknown_081D9635', 'gUnknown_081D93FA', 'gUnknown_081D944B', 'gUnknown_081D94B0', 'gUnknown_081D8C58', 'gUnknown_081D8C65', 'gUnknown_081D9156', 'gUnknown_081D9468', 'gUnknown_081D8EF3', 'gUnknown_081D8EEF', 'gUnknown_081D9132', 'gUnknown_081D955D', 'gUnknown_081D919F', 'gUnknown_081D9171', 'gUnknown_081D91CD', 'gUnknown_081D9834', 'gUnknown_081D9128', 'gUnknown_081D83D6', 'gUnknown_081D989B', 'gUnknown_081D90FC', 'gUnknown_081D95DB', 'gUnknown_081D9826', 'gUnknown_081D98C9', 'gUnknown_081D6F74', 'gUnknown_081D6F74', 'gUnknown_081D6F44', 'gUnknown_081D83B5', 'gUnknown_081D839B', 'gUnknown_081D92C2', 'gUnknown_081D92C9', 'gUnknown_081D92D0',
]

def insert_labels(labels):
	version = get_setup_version('ruby')
	chunks = []
	for label in labels:
		address = int(label[-6:], 16)
		chunks += [Label(address, asm=label, is_global=True, version=version)]
	for path in version['maps_paths']:
		insert_chunks(chunks, path, version)


def int16(x):
	return int(x, 16)

if __name__ == '__main__':
    args = get_args(
        'classname',
	('addresses', {'nargs': '*', 'type': int16}),
	('--version', {'default':'ruby'}),
	('-i', {'dest': 'insert', 'action': 'store_true'}),
    )
    class_ = globals()[args.classname]
    version = args.version

    if not args.addresses:
        addresses = [class_.address]
    else:
        addresses = args.addresses

    for address in addresses:
	    if args.insert:
		insert_recursive(class_, address, version)
	    else:
		print print_recursive(class_, address, version)
