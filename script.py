# coding: utf-8

"""Classes for parsing Pokemon Emerald scripts.
"""

from constants import *


def is_rom_address(address):
    return (0x8000000 <= address <= 0x9ffffff)

def is_label(asm):
    if asm:
        line = asm.split(';')[0].rstrip()
        if line and line[-1] == ':':
            return True
    return False


class Object(object):
    arg_names = []
    rom = baserom
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
        return labels.get(self.value)
    @property
    def real_address(self):
        if not is_rom_address(self.value) and not self.value == 0:
            #raise Exception('invalid pointer at 0x{:08x} (0x{:08x})'.format(self.address, self.value))
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
        return Pointer.get_label(self) or labels.get(self.value - 1)

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
            param = param_class(address)
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
        return '0x{:x}'.format(self.value)

class WordOrVariable(Word):
    @property
    def asm(self):
        if self.value >= 0x4000:
            return '0x{:x}'.format(self.value)
        return str(self.value)

class Species(Word):
    @property
    def asm(self):
        return pokemon_constants.get(self.value, str(self.value))

class Item(Word):
    @property
    def asm(self):
        return item_constants.get(self.value, str(self.value))

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
    context_label = 'g'
    default_label_base = 'Unknown'
    include_address = True
    address_comment = True
    def parse(self):
        Chunk.parse(self)
        if not hasattr(self, 'asm'):
            label = self.context_label + self.default_label_base
            if self.include_address:
                label += '_0x{:x}'.format(self.address)
            self.asm = label
    def to_asm(self):
        asm = self.asm + ':'
        if self.address_comment:
            asm += ' ; 0x{:x}'.format(self.address)
        return asm

class Comment(Chunk):
    def to_asm(self):
        if hasattr(self, 'comment') and self.comment:
            return '; ' + self.comment
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
            byte = Byte(address)
            command_class = self.commands.get(byte.value)
            if command_class:
                command = command_class(address)
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
        map_name = map_groups.get(group, {}).get(number)
        if not map_name:
            return Word(self.address).asm
        return map_name
    def to_asm(self):
        return '\t' + 'map ' + self.asm

class WarpMapId(MapId):
    """Reversed MapId."""
    param_classes = [
        ('number', Byte),
        ('group', Byte),
    ]



def recursive_parse(*args):
    chunks = {}
    closure = {
        'level': -1,
        'context_labels': ['g'],
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
                    )
                    chunk.label = label
            recurse(chunk.target, chunk.real_address, **chunk.target_args)
        for c in chunk.chunks:
            recurse_pointers(c)

    recurse(*args)
    return chunks


def print_chunks(chunks):
    sorted_chunks = sorted(set((c.address, c.last_address, c.to_asm()) for c in chunks))
    lines = []
    previous_address = None
    for address, last_address, asm in sorted_chunks:
        if previous_address:
            if address > previous_address:
                if lines and not is_label(lines[-1]):
                    lines += ['']
                lines += ['\tbaserom 0x{:x}, 0x{:x}'.format(previous_address, address), '']
            elif address < previous_address:
                if asm: asm = ';' + asm
                #lines += ['; ERROR (0x{:x}, 0x{:x})'.format(address, previous_address)]
        if asm:
            if lines and lines[-1]:
                if is_label(asm) and not is_label(lines[-1]):
                    lines += ['']
            lines += [asm]
        previous_address = last_address
    return ('\n'.join(lines) + '\n').encode('utf-8')

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

def print_recursive(class_, address):
    return print_nested_chunks(recursive_parse(class_, address).values())
