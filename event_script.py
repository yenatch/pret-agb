# coding: utf-8

"""Pokemon Emerald event script parsing.
"""
from new import classobj

import sys

from script import *
from event_commands import *
from pokemon_codecs import emerald

class String(Chunk):
    macro_name = u'.text'
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
        newline = u'"\n\t{} "'.format(self.macro_name)
        asm = self.asm
        #for fake_newline in (u'\n', u'\\n', u'{FA}',):
        #    asm = asm.replace(fake_newline, u' ')
        asm = asm.replace(u'\n', u'\\n')
        for newline_token in (u'+', u'\\n', u'{FA}',):
            asm = asm.replace(newline_token, newline_token + newline)
        return newline[2:] + asm + u'"'

        #lines = []
        #for line in self.asm.split('\n'):
        #    lines += [u'\t{} "{}\\n"'.format(self.macro_name, line)]
        #return '\n'.join(lines)[:-3] + '"'

alphabet = map(chr, xrange(ord('A'), ord('Z')+1))

class BrailleString(String):
    macro_name = u'.braille'
    letters = [ 1, 5, 3, 11, 9, 7, 15, 13, 6, 14, 17, 21, 19, 27, 25, 23, 31, 29, 22, 30, 49, 53, 46, 51, 59, 57 ]
    mapping = dict(zip(letters, alphabet))
    mapping.update({ 0: u' ', 28: u'!', 16: u'\'', 4: u',', 48: u'-', 44: u'.', 52: u'?', 8: u'"', 0xfe: u'\n', 0xff: u'$' })
    @property
    def asm(self):
        return u''.join(map(self.mapping.get, self.bytes))

class Braille(ParamGroup):
    param_classes = [Byte, Byte, Byte, Byte, Byte, Byte, ('string', BrailleString)]

BraillePointer.target = Braille

class Text(ParamGroup):
    param_classes = [String]

TextPointer.target = Text

class EventScriptLabel(Label):
    default_label_base = 'Event'

class EventScript(Script):
    commands = event_command_classes
    def parse(self):
        Script.parse(self)
        self.filter_msgbox()
        self.check_extra_ends()
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
        #print ' ' * closure['level'], class_, hex(address)
        #sys.stdout.flush()

        # container chunk for chunk + label
        # XXX not the case anymore, is this still required?
        container = Chunk()
        chunk = class_(address, *args_, **kwargs_)
        container.chunks += [chunk]

        context = hasattr(chunk, 'context_label')
        if context:
            closure['context_labels'] += [chunk.context_label]
        chunks[address] = container
        recurse_pointers(container)
        if context:
            closure['context_labels'].pop()
        closure['level'] -= 1
    def recurse_pointers(chunk):
        if hasattr(chunk, 'target'):
            if chunk.target: # redundant, but avoids errors
		if chunk.real_address:
                    label = Label(
                        chunk.real_address,
                        default_label_base=chunk.target.__name__,
                        context_label=closure['context_labels'][-1]
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
