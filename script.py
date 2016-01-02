# coding: utf-8
"""Classes for parsing Pokemon Emerald scripts.
"""


#parsed_chunks = {}
#def mark_parsed_chunk(instance):
#    class_ = instance.__class__
#    address = instance.address
#    if not parsed_chunks.has_key(class_):
#        parsed_chunks[class_] = []
#    parsed_chunks[class_][address] = instance
#def get_parsed_chunk(class_, address):
#    return parsed_chunks.get(class_, {}).get(address)

#labels = {}
#def get_label(address):
#    return labels.get(address)

def load_rom(filename):
    return bytearray(open(filename).read())
baserom = load_rom('base_emerald.gba')

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
        return '\t' + self.macro_name + ' ' + self.asm

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
    macro_name = '.byte'
    num_bytes = 1

class Word(Value):
    macro_name = '.2byte'
    num_bytes = 2

class Int(Value):
    macro_name = '.4byte'
    num_bytes = 4
    @property
    def asm(self):
        return '0x{:x}'.format(self.value)

class Pointer(Int):
    target = None
    target_arg_names = []

    #def parse(self):
    #    Int.parse(self)
    #    if not is_address_parsed(self.target, self.real_address):
    #        mark_address(self.target, self.real_address)
    #        chunk = self.resolve()
    #        if chunk is not None:
    #            self.chunks += [chunk]

    def resolve(self):
        if not (0x8000000 <= self.value <= 0x9ffffff):
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
        return None
    @property
    def real_address(self):
        if not (0x8000000 <= self.value <= 0x9ffffff) and not self.value == 0:
            #raise Exception('invalid pointer at 0x{:08x} (0x{:08x})'.format(self.address, self.value))
            return None
        return self.value & 0x1ffffff
    @property
    def asm(self):
        label = self.get_label()
        if label:
            return label
        return '0x{:x}'.format(self.value)

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

class Command(ParamGroup):
    end = False
    atomic = True
    def to_asm(self):
        chunks = self.chunks[1:]
        return '\t' + self.name + ' ' + ', '.join(param.asm for param in chunks)

class Label(Chunk):
    atomic = True
    context_label = 'g'
    default_label_base = 'Unknown'
    def parse(self):
        Chunk.parse(self)
        if not hasattr(self, 'asm'):
            label = self.context_label + self.default_label_base + '_0x{:x}'.format(self.address)
            self.asm = label
    def to_asm(self):
        return self.asm + ':'
    #@property
    #def label(self):
    #    return get_label(self.address)

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

def print_chunks(chunks):
    def is_label(asm):
        return asm and asm[-1] == ':'
    sorted_chunks = sorted(set((c.address, c.last_address, c.to_asm()) for c in chunks))
    lines = []
    previous_address = None
    for address, last_address, asm in sorted_chunks:
        if previous_address:
            if address > previous_address:
                if lines and not is_label(lines[-1]):
                    lines += ['']
                lines += ['\tbaserom 0x{:x}, 0x{:x}'.format(previous_address, address), '']
	if asm:
            if lines and lines[-1]:
                if is_label(asm) and not is_label(lines[-1]):
                    lines += ['']
            lines += [asm]
        previous_address = last_address
    return '\n'.join(lines) + '\n'

def print_scripts(scripts):
    chunks = []
    for script in scripts:
        chunks += script.chunks
    return print_chunks(chunks)
