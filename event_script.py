# coding: utf-8

"""Pokemon Emerald event script parsing.
"""
from new import classobj

import sys

from script import *
from event_commands import *
from pokemon_codecs import emerald

force_stop_addresses = [
	0x209a99, # SlateportCityBattleTent waitstate
	0x2c8381, # TrainerHill1F missing end
]


class String(Chunk):
    name = 'text'
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
        return self.bytes.decode('emerald')
    def to_asm(self):
        newline = '"\n\t{} "'.format(self.name)
        asm = self.asm
        asm = asm.replace('\n', '\\n')
        for newline_token in ('+', '\\n', '{FA}',):
            asm = asm.replace(newline_token, newline_token + newline)
        return newline[2:] + asm + '"'

class Text(ParamGroup):
    param_classes = [String]

TextPointer.target = Text


alphabet = map(chr, xrange(ord('A'), ord('Z')+1))

class BrailleString(String):
    name = 'braille'
    letters = [ 1, 5, 3, 11, 9, 7, 15, 13, 6, 14, 17, 21, 19, 27, 25, 23, 31, 29, 22, 30, 49, 53, 46, 51, 59, 57 ]
    mapping = dict(zip(letters, alphabet))
    mapping.update({ 0: ' ', 28: '!', 16: '\'', 4: ',', 48: '-', 44: '.', 52: '?', 8: '"', 0xfe: '\n', 0xff: '$' })
    @property
    def asm(self):
        return ''.join(map(self.mapping.get, self.bytes))

class Braille(ParamGroup):
    param_classes = [Byte, Byte, Byte, Byte, Byte, Byte, ('string', BrailleString)]

BraillePointer.target = Braille


class EventScript(Script):
    commands = event_command_classes

    def parse(self):
        Script.parse(self)
        self.check_forced_stops()
        self.filter_msgbox()
        #self.check_extra_ends()

    def check_forced_stops(self):
        """
        There are some malformed scripts that need to be manually ended.
        This function rewinds a script if it passes through an address in force_stop_addresses.
        """
        for i, chunk in enumerate(self.chunks):
            if chunk.last_address in force_stop_addresses:
                self.chunks = self.chunks[:i+1]
                self.last_address = chunk.last_address
                self.chunks += [Comment(self.last_address, comment='forced stop')]
                break

    def check_extra_ends(self):
        address = self.last_address
        byte = Byte(address)
        command_class = self.commands.get(byte.value)
        if command_class:
            if command_class.name == 'end':
                command = command_class(address)
                self.chunks += [command]
                address += command.length
        self.last_address = address

    def filter_msgbox(self):
        loadptrs = []
        for command in self.chunks:
            if hasattr(command, 'name'):
                if command.name == 'loadptr':
                    if command.chunks[1].value == 0:
                        loadptrs += [command]
                elif command.name == 'callstd':
                    if command.chunks[1].value in (2, 3, 4, 5, 6, 9,):
                        for loadptr in loadptrs:
                            classes = list(loadptr.param_classes)
                            classes[2] = TextPointer
                            loadptr.param_classes = classes
                            loadptr.parse()
                        loadptrs = []

EventScriptPointer.target = EventScript


def recursive_event_script(address):
    return recursive_parse(EventScript, address)

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

def print_recursive_event_script(address):
    scripts = recursive_event_script(address).values()
    return print_nested_chunks(scripts)

def print_nested_chunks(*args):
    return print_chunks(flatten_nested_chunks(*args))

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

def print_recursive(class_, address):
	return print_nested_chunks(recursive_parse(class_, address).values())

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('address')
    args = ap.parse_args()

    print print_recursive(
        EventScript,
        int(args.address, 16)
    ).encode('utf-8')
