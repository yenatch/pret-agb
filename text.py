# coding: utf-8

from script import *
import charmap


class String(Chunk):
    name = '.string'
    atomic = True
    def parse(self):
        Chunk.parse(self)
        address = self.address
        address = self.rom.find('\xff', address) + 1
        self.last_address = address
    @property
    def bytes(self):
        return self.rom[self.address:self.last_address]
    @property
    def asm(self):
        return '"' + charmap.decode(self.bytes, self.version['charmap']) + '"'
    def to_asm(self):
        newline = '"\n\t{} "'.format(self.name)
        asm = self.asm
        for newline_token in ('\\l', '\\p', '\\n',):
            asm = asm.replace(newline_token, newline_token + newline)
        return '\t' + self.name + ' ' + asm

class Text(ParamGroup):
    param_classes = [String]

class TextPointer(Pointer):
    target = Text


class JPString(String):
	@property
	def asm(self):
		return '"' + charmap.decode(self.bytes, self.version['charmap_jp']) + '"'

class JPText(Text):
	param_classes = [JPString]

alphabet = map(chr, xrange(ord('A'), ord('Z')+1))

class BrailleString(String):
    name = '.braille'
    letters = [ 1, 5, 3, 11, 9, 7, 15, 13, 6, 14, 17, 21, 19, 27, 25, 23, 31, 29, 22, 30, 49, 53, 46, 51, 59, 57 ]
    mapping = dict(zip(letters, alphabet))
    mapping.update({ 0: ' ', 28: '!', 16: '\'', 4: ',', 48: '-', 44: '.', 52: '?', 8: '"', 0xfe: '\\n', 0xff: '$' })
    @property
    def asm(self):
        return '"' + strmap(self.mapping.get, self.bytes) + '"'

strmap = lambda *args: ''.join(map(*args))
class RawString(String):
	"""Just spits out "{0x..}...{0xff}"."""
	@property
	def asm(self):
		return '"' + strmap('{{0x{:02x}}}'.format, self.bytes) + '"'

class Braille(ParamGroup):
    param_classes = [Byte, Byte, Byte, Byte, Byte, Byte, ('string', BrailleString)]

class BraillePointer(Pointer):
    target = Braille


def main():
	import argparse
	ap = argparse.ArgumentParser()
	ap.add_argument('address')
	ap.add_argument('version', nargs='?', default='ruby')
	args = ap.parse_args()

	import versions
	version = versions.__dict__[args.version]
	setup_version(version)
	chunks = recursive_parse(
		Text,
		int(args.address, 16),
		version=version,
		rom=version['baserom']
	)

	chunks = flatten_nested_chunks(chunks.values())
	for path in version['maps_paths']:
		insert_chunks(chunks, path, version)

if __name__ == '__main__':
	main()
