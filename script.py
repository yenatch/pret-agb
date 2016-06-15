# coding: utf-8

"""Classes for parsing Pokemon Emerald scripts.
"""

import os

from constants import *


def is_rom_address(address):
    return (0x8000000 <= address <= 0x9ffffff)

def is_label(asm):
    if asm:
        line = asm.split('@')[0].rstrip()
        if line and line[-1] == ':':
            return True
    return False


class Object(object):
    arg_names = []
    rom = None
    version = None
    def __init__(self, *args, **kwargs):
        map(self.__dict__.__setitem__, self.arg_names, args)
        self.__dict__.update(kwargs)
        self.parse()
    def parse(self):
        pass

class Chunk(Object):
    arg_names = ['address']
    atomic = False
    @property
    def length(self):
        return self.last_address - self.address
    def parse(self):
        #print '@debug: parsing', self.__class__.__name__, 'at', hex(self.address)
        self.pointers = []
        self.chunks = []
        self.last_address = self.address
    def to_asm(self):
        return None

class Param(Chunk):
    num_bytes = 1
    atomic = True
    @property
    def asm(self):
        return str(self.value)
    def to_asm(self):
        return '\t' + self.name + ' ' + self.asm

class Value(Param):
    big_endian = False
    def parse(self):
        Param.parse(self)
        # Note: the loop is to make sure reads are within the bounds of the rom.
        bytes_ = []
        for i in xrange(self.num_bytes):
            bytes_ += [self.rom[self.address + i]]
        #bytes_ = self.rom[self.address : self.address + self.num_bytes]
        if self.big_endian:
            bytes_.reverse()
        self.value = sum(byte << (8 * i) for i, byte in enumerate(bytes_))
        self.last_address = self.address + self.num_bytes

class Byte(Value):
    name = '.byte'
    num_bytes = 1

class Word(Value):
    name = '.2byte'
    num_bytes = 2

class Int(Value):
    name = '.4byte'
    num_bytes = 4
    @property
    def asm(self):
        return '0x{:x}'.format(self.value)

class SignedInt(Int):
	def parse(self):
		Int.parse(self)
		self.value -= (self.value & 0x80000000) * 2
	@property
	def asm(self):
		return str(self.value)

class Pointer(Int):
    target = None
    target_arg_names = []
    include_address = True # passed to Label

    def resolve(self):
        if not is_rom_address(self.value):
            return None
        if self.target is None:
            return None
        return self.target(self.real_address, **self.target_args)
    @property
    def target_args(self):
        return { k: getattr(self, k, None) for k in self.target_arg_names }
    def get_label(self):
        if hasattr(self, 'label'):
            return self.label.asm
        return self.version['labels'].get(self.value)
    @property
    def real_address(self):
        if not is_rom_address(self.value) and not self.value == 0:
            raise Exception('invalid pointer at 0x{:08x} (0x{:08x})'.format(self.address, self.value))
            return None
        return self.value & 0x1ffffff
    @property
    def asm(self):
        label = self.get_label()
        if label:
            return label
        return '0x{:x}'.format(self.value)

class ThumbPointer(Pointer):
    def get_label(self):
        return Pointer.get_label(self) or self.version['labels'].get(self.value - 1)

class ParamGroup(Chunk):
    param_classes = []
    def parse(self):
        Chunk.parse(self)
        address = self.address
        self.chunks = []
        self.params = {}
        for item in self.param_classes:
            name = None
            try:
                name, param_class = item
            except:
                param_class = item
            param = param_class(
                address,
                version=self.version,
                rom=self.rom,
            )
            self.chunks += [param]
            if name:
                self.params[name] = param
            address += param.length
        self.last_address = address
    @property
    def asm(self):
        return ', '.join(param.asm for param in self.chunks)

class Variable(Word):
    @property
    def asm(self):
        return {
            0x800c: 'FACING',
            0x800d: 'RESULT',
            0x800f: 'LAST_TALKED',
        }.get(self.value, '0x{:x}'.format(self.value))

class WordOrVariable(Word):
    @property
    def asm(self):
        if self.value >= 0x4000:
            return Variable.asm.fget(self)
        return str(self.value)

class Species(Word):
    @property
    def asm(self):
        return self.version.get('pokemon_constants', {}).get(self.value, str(self.value))

class Item(Word):
    @property
    def asm(self):
        return self.version.get('item_constants', {}).get(self.value, WordOrVariable.asm.fget(self))

class BFItem(Item):
	@property
	def asm(self):
		return self.version.get('battle_frontier_item_constants', {}).get(self.value, str(self.value))

class TrainerId(Word):
	@property
	def asm(self):
		return self.version.get('trainer_constants', {}).get(self.value, str(self.value))

class FieldGFXId(Word):
	@property
	def asm(self):
		return self.version.get('field_gfx_constants', {}).get(self.value, str(self.value))

class Macro(ParamGroup):
    atomic = True
    @property
    def asm(self):
        chunks = self.chunks
        return ', '.join(param.asm for param in chunks)
    def to_asm(self):
        asm = self.asm
        return '\t' + self.name + (' ' if asm else '') + asm

class Command(Macro):
    end = False
    @property
    def asm(self):
        chunks = self.chunks[1:]
        return ', '.join(param.asm for param in chunks)

class Label(Chunk):
    atomic = True
    context_label = '' # 'g'
    default_label_base = 'Unknown'
    include_address = True
    address_comment = True
    def parse(self):
        Chunk.parse(self)
        if not hasattr(self, 'asm'):
            if self.context_label:
                label = self.context_label + '_' + self.default_label_base
            else:
                label = self.default_label_base
            if self.include_address:
                label += '_{:X}'.format(self.address)
            self.asm = label
    def to_asm(self):
        asm = self.asm + '::'
        if self.address_comment:
            asm += ' @ {:X}'.format(0x8000000 + self.address)
        #asm = '\t.global {}\n'.format(self.asm) + asm
        return asm

class Comment(Chunk):
    def to_asm(self):
        if hasattr(self, 'comment') and self.comment:
            return '@ ' + self.comment
        return ''

class Script(Chunk):
    commands = {}
    default_label = Label
    def parse(self):
        Chunk.parse(self)
        self.chunks = []
        address = self.address
        end = False
        while not end:
            byte = Byte(address, version=self.version, rom=self.rom)
            command_class = self.commands.get(byte.value)
            if command_class:
                command = command_class(address, version=self.version, rom=self.rom)
                self.chunks += [command]
                end = command.end
                address += command.length
            else:
                break
        self.last_address = address
        #self.chunks += [self.get_label()]
    def get_label(self):
        return self.default_label(self.address)
    def to_asm(self):
        return print_chunks(self.chunks)


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
				param = param_class(
					address,
					version=self.version,
					rom=self.rom,
				)
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

class BinFile(Chunk):
	atomic = True
	name = '.incbin'
	def parse(self):
		Chunk.parse(self)
		address = self.address
		address += self.size
		self.value = self.rom[self.address:address]
		self.last_address = address
	@property
	def asm(self):
		return '"' + self.filename + '"'
	def to_asm(self):
		return '\t' + self.name + ' ' + self.asm
	def create_file(self):
		filename = self.filename
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError:
			pass
		with open(filename, 'wb') as out:
			out.write(bytearray(self.value))

def create_files_of_chunks(chunks):
	for chunk in chunks:
		if hasattr(chunk, 'create_file'):
			chunk.create_file()


class MapId(Macro):
    name = 'map'
    param_classes = [
        ('group', Byte),
        ('number', Byte),
    ]
    @property
    def asm(self):
        group = self.params['group'].value
        number = self.params['number'].value
        if group == 0x7f and number == 0x7f:
            return 'NONE'
        if group == 0xff and number == 0xff:
            return 'UNDEFINED'
        map_name = self.version['map_groups'].get(group, {}).get(number)
        if not map_name:
            return Word(self.address, version=self.version, rom=self.rom).asm
        return map_name
    def to_asm(self):
        return '\t' + 'map ' + self.asm

class WarpMapId(MapId):
    """Reversed MapId."""
    param_classes = [
        ('number', Byte),
        ('group', Byte),
    ]


def recursive_parse(*args, **kwargs):
    chunks = {}
    closure = {
        'level': -1,
        'context_labels': [''],
    }
    def recurse(class_, address, *args_, **kwargs_):
        if chunks.get(address):
            return
        if class_ is None:
            return
        if address in (None, 0):
            return
        closure['level'] += 1
        chunk = class_(address, *args_, **kwargs_)
        chunks[address] = chunk
        context = hasattr(chunk, 'context_label')
        if context:
            closure['context_labels'] += [chunk.context_label]
        recurse_pointers(chunk)
        if context:
            closure['context_labels'].pop()
        closure['level'] -= 1

    def recurse_pointers(chunk):
        if hasattr(chunk, 'target') and chunk.target:
            if chunk.real_address:
                if not hasattr(chunk, 'label') or not chunk.label:
                    label = Label(
                        chunk.real_address,
                        default_label_base=chunk.target.__name__,
                        context_label=closure['context_labels'][-1],
                        include_address=chunk.include_address,
			version=chunk.version,
			rom=chunk.rom,
                    )
                    asm = chunk.version['labels'].get(chunk.value)
                    if asm and 'Unknown' not in asm: label.asm = asm
                    chunk.label = label
		target_args = {}
		target_args.update(kwargs)
		target_args.update(chunk.target_args)
                recurse(chunk.target, chunk.real_address, **target_args)
        for c in chunk.chunks:
            recurse_pointers(c)

    recurse(*args, **kwargs)
    return chunks


def sort_chunks(chunks):
    return sorted(set((c.address, c.last_address, c.to_asm()) for c in chunks))

def print_chunks(chunks):
    sorted_chunks = sort_chunks(chunks)
    lines = []
    previous_address = None
    for address, last_address, asm in sorted_chunks:
        if previous_address:
            if address > previous_address:
                if lines and not is_label(lines[-1]):
                    lines += ['']
                lines += ['\tbaserom 0x{:x}, 0x{:x}'.format(previous_address, address), '']
            elif address < previous_address:
                if asm: asm = '@' + asm
                #lines += ['@ ERROR (0x{:x}, 0x{:x})'.format(address, previous_address)]
        if asm:
            if lines and lines[-1]:
                if is_label(asm) and not is_label(lines[-1]):
                    lines += ['']
            lines += [asm]
        previous_address = last_address
    return ('\n'.join(lines) + '\n').encode('utf-8')

def incbin(path, start, end):
    return '\t.incbin "{path}", 0x{start:x}, 0x{length:x}'.format(path=path, start=start, length=end - start)

def insert_chunks(chunks, filename, version):
    baserom_path = version['baserom_path']
    closure = {}
    def next_chunk():
        closure['previous_address'] = closure.get('last_address')
        closure['previous_asm'] = closure.get('asm')
        try:
            chunk = sorted_chunks.next()
        except StopIteration:
            chunk = None, None, None
        closure['address'], closure['last_address'], closure['asm'] = chunk
        return current_chunk()
    def current_chunk():
        return closure['address'], closure['last_address'], closure['asm']
    def previous_address():
        return closure.get('previous_address')
    def previous_asm():
        return closure.get('previous_asm')

    def insert(filename):
        if not os.path.exists(filename):
            return
        lines = open(filename).readlines()
        for i, line in enumerate(lines):
            if '.include' in line:
                sub = line.split('"')[1]
                insert(sub)
            elif '.incbin "{path}"'.format(path=baserom_path) in line:
                args = map(eval, line.split('@')[0].split(',')[1:3])
                try:
                    start, length = args
                    end = start + length
                except:
                    start = args[0]
                    end = 0x1000000

                address, last_address, asm = current_chunk()
                # sorry dead chunks
                while address < start:
                    address, last_address, asm = next_chunk()
                    if address is None:
                        break
                if address is None:
                    break

                new_line = ''

                closure['previous_address'] = start
                while start <= address <= last_address <= end:
                    if address == end:
                        break # it's a label
                    previous = previous_address()
                    if previous < address:
                        new_line += '\n' + incbin(baserom_path, previous, address) + '\n'
                    if asm:
                        if not is_label(previous_asm()) and is_label(asm):
                            new_line += '\n'
                        new_line += asm.encode('utf-8') + '\n'
                    address, last_address, asm = next_chunk()
                    if address is None:
                        break
                previous = previous_address()
                if new_line and start <= previous < end:
                    new_line += '\n' + incbin(baserom_path, previous, end) + '\n'
                if new_line:
                    lines[i] = new_line

                if address is None:
                    break
        with open(filename, 'w') as out:
            out.write(''.join(lines))

    sorted_chunks = iter(sort_chunks(chunks))
    next_chunk()
    insert(filename)

def flatten_nested_chunks(*args):
    closure = {'flattened': []}
    def recurse(chunks, labels_only=False):
        for chunk in chunks:
            if hasattr(chunk, 'label') and chunk.label:
                closure['flattened'] += [chunk.label]
            if not labels_only:
                if chunk.chunks and not chunk.atomic:
                    recurse(chunk.chunks)
                else:
                    closure['flattened'] += [chunk]
                    recurse(chunk.chunks, labels_only=True)
            else:
                recurse(chunk.chunks, labels_only=True)
    recurse(*args)
    return closure['flattened']

def print_nested_chunks(*args):
    return print_chunks(flatten_nested_chunks(*args))

def print_recursive(class_, address, *args, **kwargs):
    return print_nested_chunks(recursive_parse(class_, address, *args, **kwargs).values())
