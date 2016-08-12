# coding: utf-8

"""Pokemon Emerald event script parsing.
"""

from new import classobj

import sys

from script import *
from text import *
from movement import *


class EventScript(Script):
    # event_command_classes doesn't exist yet, but it depends on EventScript being defined first.
    @property
    def commands(self):
        return event_command_classes

    def parse(self):
        Script.parse(self)
        self.check_forced_stops()
        self.filter_macros()
        self.check_extra_ends()

    def check_forced_stops(self):
        """
        There are some malformed scripts that need to be manually ended.
        This function rewinds a script if it passes through an address in force_stop_addresses.
        """
        force_stop_addresses = self.version.get('force_stop_addresses')
        if not force_stop_addresses:
            return
        for i, chunk in enumerate(self.chunks):
            if chunk.last_address in force_stop_addresses:
                self.chunks = self.chunks[:i+1]
                self.last_address = chunk.last_address
                self.chunks += [Comment(self.last_address, comment='forced stop')]
                break

    def check_extra_ends(self):
        """
        Some scripts ending in 'jump' have an extra 'end' afterward.
        """
        if not self.chunks:
            return
        chunk = self.chunks[-1]
        if getattr(chunk, 'name', None) not in ['jump']:
            return
        address = self.last_address
        command_class = self.commands.get(Byte(address, version=self.version, rom=self.rom).value)
        if command_class:
            if command_class.name in ['end']:
                command = command_class(address, version=self.version, rom=self.rom)
                self.chunks += [command]
                address += command.length
        self.last_address = address

    def filter_macros(self):
        self.filter_msgbox()
        self.filter_switch()
        self.filter_giveitem()

    def filter_switch(self):
        copyvar = None
        compare = None
        i = 0
        while i < len(self.chunks):
            command = self.chunks[i]
            name = getattr(command, 'name', None)
            if name == 'copyvar':
                if command.chunks[1].value == 0x8000:
                    copyvar = command
                    macro = Switch(chunks=[copyvar])
                    self.chunks.pop(i)
                    self.chunks.insert(i, macro)
            elif name == 'compare':
                if copyvar:
                    if command.chunks[1].value == 0x8000:
                        compare = command
                    else:
                        compare = None
            elif name == 'jumpif':
                if command.chunks[1].value == 1:
                    if copyvar and compare and compare.last_address == command.address:
                        macro = SwitchCase(compare=compare, jumpif=command)
                        try:
                            index = self.chunks.index(compare)
                            self.chunks.pop(index)
                            self.chunks.pop(index)
                            self.chunks.insert(index, macro)
                            i -= 1
                        except:
                            pass
            if name != 'compare':
                compare = None
            i += 1

    def filter_msgbox(self):
        loadptr = None
        i = 0
        while i < len(self.chunks):
            command = self.chunks[i]
            name = getattr(command, 'name', None)
            if name == 'loadptr':
                loadptr = command
            elif name == 'callstd':
                if loadptr:
                    macro = MsgBox(loadptr=loadptr, callstd=command)
                    index = self.chunks.index(loadptr)
                    self.chunks.pop(index)
                    self.chunks.pop(index)
                    self.chunks.insert(index, macro)
                    i -= 1
                loadptr = None
            else:
                loadptr = None
            i += 1

    def filter_giveitem(self):
        item = None
        amount = None
        i = 0
        while i < len(self.chunks):
            command = self.chunks[i]
            name = getattr(command, 'name', None)
            if name == 'setorcopyvar':
                if not item and command.params['destination'].value == 0x8000:
                    item = command
                    amount = None
                elif command.params['destination'].value == 0x8001:
                    amount = command
            elif name == 'callstd':
                if item and amount and command.params['function'].value in (0, 1):
                    replace_class(item, 'source', Item)
                    replace_class(amount, 'source', Amount)
                    macro = GiveItem(copyitem=item, copyamount=amount, callstd=command)
                    index = self.chunks.index(item)
                    self.chunks.pop(index)
                    self.chunks.pop(index)
                    self.chunks.pop(index)
                    self.chunks.insert(index, macro)
                    i -= 2
                elif item and (not amount) and command.params['function'].value == 7:
                    replace_class(item, 'source', Decoration)
                    macro = GiveDecoration(setorcopyvar=item, callstd=command)
                    index = self.chunks.index(item)
                    self.chunks.pop(index)
                    self.chunks.pop(index)
                    self.chunks.insert(index, macro)
                    i -= 1
                item = None
                amount = None
            else:
                item = None
                amount = None
            i += 1

def replace_class(chunk, name, class_):
	classes = list(chunk.param_classes)
	i = 0
	for c in classes:
		try:
			if c[0] == name:
				classes[i] = (name, class_)
				chunk.param_classes = classes
				chunk.parse()
				break
		except:
			pass
		i += 1

#	def filter_msgbox(self):
#		loadptr = None
#		chunks = IterChunks(self.chunks)
#		for command in chunks:
#			name = getattr(command, 'name', None)
#			if name == 'loadptr':
#				loadptr = command
#			elif name == 'callstd':
#				if loadptr:
#					macro = MsgBox(loadptr=loadptr, callstd=command)
#					chunks.replace(loadptr, macro)
#					chunks.remove(callstd)
#				loadptr = None
#			else:
#				loadptr = None

#class IterChunks:
#	def init(self, chunks):
#		self.chunks = chunks
#		self.index = -1
#	def __iter__(self):
#		return self
#	def next(self):
#		self.index += 1
#		try:
#			chunk = self.chunks[self.index]
#		except:
#			raise StopIteration
#		return chunk
#	def replace(self, target, replacement):
#		index = self.chunks.index(target)
#		self.chunks.pop(index)
#		self.chunks.insert(index, replacement)
#	def remove(self, target):
#		index = self.chunks.index(target)
#		self.chunks.pop(index)
#		if self.index > index:
#			self.index -= 1

class EventScriptPointer(Pointer):
    target = EventScript


class Pokemart(ParamGroup):
    param_classes = [ItemList, EventScript]

class PokemartPointer(Pointer):
    target = Pokemart

class PokemartDecor(Pokemart):
	param_classes = [DecorList, EventScript]

class PokemartDecorPointer(PokemartPointer):
	target = PokemartDecor

class TrainerbattleArgs(ParamGroup):
	param_classes = [('type', Byte), TrainerId, Word,]
	def parse(self):
		ParamGroup.parse(self)
		self.param_classes = list(self.param_classes)

		type_ = self.params['type'].value
		if type_ != 3:
			self.param_classes += [TextPointer]
		self.param_classes += [TextPointer]
		if type_ in (1, 2):
			self.param_classes += [EventScriptPointer]
		if type_ in (4, 7, 6, 8):
			self.param_classes += [TextPointer]
		if type_ in (6, 8):
			self.param_classes += [EventScriptPointer]

		ParamGroup.parse(self)

event_commands = {
    0x00: { 'name': 'snop',
        'aliases': ['nop0', 'nop'],
        'description': 'Does nothing.',
    },
    0x01: { 'name': 'snop1',
        'aliases': ['nop1'],
        'description': 'Does nothing.',
    },
    0x02: { 'name': 'end',
        'end': True,
        'description': 'Terminates script execution.',
        'aliases': ['end'],
    },
    0x03: { 'name': 'return',
        'end': True,
        'aliases': ['return'],
        'description': 'Jumps back to after the last-executed call statement, and continues script execution from there.',
    },
    0x04: { 'name': 'call',
        'param_names': ['destination'],
        'param_types': [EventScriptPointer],
        'aliases': ['call'],
        'description': 'Jumps to destination and continues script execution from there. The location of the calling script is remembered and can be returned to later.',
    },
    0x05: { 'name': 'jump',
        'param_types': [EventScriptPointer],
        'end': True, # Is an ender, but seems to usually be followed by "end"
        'description': 'Jumps to destination and continues script execution from there.',
        'param_names': ['destination'],
        'aliases': ['jump', 'goto'],
    },
    0x06: { 'name': 'jumpif',
        'param_names': ['condition', 'destination'],
        'param_types': ['byte', EventScriptPointer],
        'aliases': ['if1', 'gotoif', 'if'],
        'description': 'If the result of the last comparison matches condition (see Comparison operators), jumps to destination and continues script execution from there.',
    },
    0x07: { 'name': 'callif',
        'param_names': ['condition', 'destination'],
        'param_types': ['byte', EventScriptPointer],
        'aliases': ['if2', 'if'],
        'description': 'If the result of the last comparison matches condition (see Comparison operators), calls destination.',
    },
    0x08: { 'name': 'jumpstd',
        'param_types': ['byte'],
        'end': True,
        'description': 'Jumps to the standard function at index function.',
        'param_names': ['function'],
        'aliases': ['jumpstd', 'gotostd'],
    },
    0x09: { 'name': 'callstd',
        'param_names': ['function'],
        'param_types': ['byte'],
        'aliases': ['callstd', 'gosubstd'],
        'description': 'Calls the standard function at index function.',
    },
    0x0a: { 'name': 'jumpstdif',
        'param_names': ['condition', 'function'],
        'param_types': ['byte', 'byte'],
        'aliases': ['gotostdif', 'if'],
        'description': 'If the result of the last comparison matches condition (see Comparison operators), jumps to the standard function at index function.',
    },
    0x0b: { 'name': 'callstdif',
        'param_names': ['condition', 'function'],
        'param_types': ['byte', 'byte'],
        'aliases': ['callstdif', 'if'],
        'description': 'If the result of the last comparison matches condition (see Comparison operators), calls the standard function at index function.',
    },
    0x0c: { 'name': 'jumpram',
        'end': True,
        'description': 'Executes a script stored in a default RAM location.',
        'aliases': ['jumpram', 'gotoram'],
    },
    0x0d: { 'name': 'die',
        'end': True,
        'description': 'Terminates script execution and "resets the script RAM".',
        'aliases': ['die', 'killscript'],
    },
    0x0e: { 'name': 'setbyte',
        'param_names': ['value'],
        'param_types': ['byte'],
        'aliases': ['setbyte'],
        'description': 'Pads the specified value to a dword, and then writes that dword to a predefined address (0x0203AAA8).',
    },
    0x0f: { 'name': 'loadptr',
        'param_names': ['destination', 'value'],
        'param_types': ['byte', TextPointer],
        'aliases': ['msgbox', 'loadpointer', 'loadptr'],
        'description': 'Sets the specified script bank to value.',
    },
    0x10: { 'name': 'setbufferbyte',
        'param_names': ['destination', 'value'],
        'param_types': ['byte', 'byte'],
        'aliases': ['setbyte2', 'setbufferbyte'],
        'description': 'Sets the specified script bank to value.',
    },
    0x11: { 'name': 'writebytetooffset',
        'param_names': ['value', 'offset'],
        'param_types': ['byte', 'pointer'],
        'aliases': ['writebytetooffset'],
        'description': 'Sets the byte at offset to value.',
    },
    0x12: { 'name': 'loadbytefrompointer',
        'param_names': ['destination', 'source'],
        'param_types': ['byte', 'pointer'],
        'aliases': ['loadbytefrompointer'],
        'description': 'Copies the byte value at source into the specified script bank.',
    },
    0x13: { 'name': 'setptrbyte',
        'param_names': ['source', 'destination'],
        'param_types': ['byte', 'pointer'],
        'aliases': ['setptrbyte', 'setfarbyte'],
        'description': "Not sure. Judging from XSE's description I think it takes the least-significant byte in bank source and writes it to destination.",
    },
    0x14: { 'name': 'copybuffers',
        'param_names': ['destination', 'source'],
        'param_types': ['byte', 'byte'],
        'aliases': ['copyscriptbanks', 'copybuffers'],
        'description': 'Copies the contents of bank source into bank destination.',
    },
    0x15: { 'name': 'copybyte',
        'param_names': ['destination', 'source'],
        'param_types': ['pointer', 'pointer'],
        'aliases': ['copybyte'],
        'description': 'Copies the byte at source to destination, replacing whatever byte was previously there.',
    },
    0x16: { 'name': 'setvar',
        'param_names': ['destination', 'value'],
        'param_types': [Variable, 'word'],
        'aliases': ['setvar'],
        'description': 'Changes the value of destination to value.',
    },
    0x17: { 'name': 'addvar',
        'param_names': ['destination', 'value'],
        'param_types': [Variable, 'word'],
        'aliases': ['addvar'],
        'description': 'Changes the value of destination by adding value to it. Overflow is not prevented (0xFFFF + 1 = 0x0000).',
    },
    0x18: { 'name': 'subvar',
        'param_names': ['destination', 'value'],
        'param_types': [Variable, 'word'],
        'aliases': ['subvar'],
        'description': 'Changes the value of destination by subtracting value to it. Overflow is not prevented (0x0000 - 1 = 0xFFFF).',
    },
    0x19: { 'name': 'copyvar',
        'param_names': ['destination', 'source'],
        'param_types': [Variable, Variable],
        'aliases': ['copyvar'],
        'description': 'Copies the value of source into destination.',
    },
    0x1a: { 'name': 'setorcopyvar',
        'param_names': ['destination', 'source'],
        'param_types': [Variable, WordOrVariable],
        'aliases': ['setorcopyvar', 'copyvarifnotzero'],
        'description': 'If source is not a variable, then this function acts like setvar. Otherwise, it acts like copyvar.',
    },
    0x1b: { 'name': 'comparebuffers',
        'param_names': ['byte1', 'byte2'],
        'param_types': ['byte', 'byte'],
        'aliases': ['comparebuffers', 'comparebanks'],
        'description': 'Compares the values of script banks a and b, after forcing the values to bytes.',
    },
    0x1c: { 'name': 'comparebuffertobyte',
        'param_names': ['a', 'b'],
        'param_types': ['byte', 'byte'],
        'aliases': ['comparebuffertobyte', 'comparebanktobyte'],
        'description': 'Compares the least-significant byte of the value of script bank a to a fixed byte value (b).',
    },
    0x1d: { 'name': 'comparebuffertoptrbyte',
        'param_names': ['a', 'b'],
        'param_types': ['byte', 'pointer'],
        'aliases': ['comparebanktofarbyte', 'comparebuffertoptrbyte'],
        'description': 'Compares the least-significant byte of the value of script bank a to the byte located at offset b.',
    },
    0x1e: { 'name': 'compareptrbytetobuffer',
        'param_names': ['a', 'b'],
        'param_types': ['pointer', 'byte'],
        'aliases': ['compareptrbytetobuffer', 'comparefarbytetobank'],
        'description': 'Compares the byte located at offset a to the least-significant byte of the value of script bank b.',
    },
    0x1f: { 'name': 'compareptrbytetobyte',
        'param_names': ['a', 'b'],
        'param_types': ['pointer', 'byte'],
        'aliases': ['compareptrbytetobyte', 'comparefarbytetobyte'],
        'description': 'Compares the byte located at offset a to a fixed byte value (b).',
    },
    0x20: { 'name': 'compareptrbytes',
        'param_names': ['a', 'b'],
        'param_types': ['pointer', 'pointer'],
        'aliases': ['comparefarbytes', 'compareptrbytes'],
        'description': 'Compares the byte located at offset a to the byte located at offset b.',
    },
    0x21: { 'name': 'compare',
        'param_names': ['var', 'value'],
        'param_types': [Variable, 'word'],
        'aliases': ['compare'],
        'description': 'Compares the value of `var` to a fixed word value (b).',
    },
    0x22: { 'name': 'comparevars',
        'param_names': ['var1', 'var2'],
        'param_types': [Variable, Variable],
        'aliases': ['comparevars'],
        'description': 'Compares the value of `var` to the value of `var2`.',
    },
    0x23: { 'name': 'callasm',
        'param_names': ['code'],
        'param_types': ['pointer'],
        'aliases': ['callasm'],
        'description': 'Calls the ASM routine stored at code. Script execution is blocked until the ASM returns (bx lr, mov pc, lr, etc.). Remember to add 1 to the offset when calling THUMB code.',
    },
    0x24: { 'name': 'jumpasm',
        'param_types': ['pointer'],
        'end': True,
        'description': 'Replaces a pointer in the script engine RAM with asm_pointer.',
        'param_names': ['asm_pointer'],
        'aliases': ['gotoasm', 'jumpasm', 'cmd24'],
    },
    0x25: { 'name': 'special',
        'param_names': ['function'],
        'param_types': ['word'],
        'aliases': ['special'],
        'description': 'Calls a special function; that is, a piece of ASM code designed for use by scripts and listed in a table of pointers.',
    },
    0x26: { 'name': 'specialval',
        'param_names': ['output', 'function'],
        'param_types': [Variable, 'word'],
        'aliases': ['special2', 'specialval'],
        'description': "Calls a special function. That function's output (if any) will be written to the variable you specify.",
    },
    0x27: { 'name': 'waitstate',
        'aliases': ['waitstate'],
        'description': 'Blocks script execution until a command or ASM code manually unblocks it. Generally used with specific commands and specials. If this command runs, and a subsequent command or piece of ASM does not unblock state, the script will remain blocked indefinitely (essentially a hang).',
    },
    0x28: { 'name': 'pause',
        'param_names': ['time'],
        'param_types': ['word'],
        'aliases': ['pause'],
        'description': 'Blocks script execution for time (frames? milliseconds?).',
    },
    0x29: { 'name': 'setflag',
        'param_names': ['a'],
        'param_types': [WordOrVariable],
        'aliases': ['setflag'],
        'description': 'Sets a to 1.',
    },
    0x2a: { 'name': 'clearflag',
        'param_names': ['a'],
        'param_types': [WordOrVariable],
        'aliases': ['clearflag'],
        'description': 'Sets a to 0.',
    },
    0x2b: { 'name': 'checkflag',
        'param_names': ['a'],
        'param_types': [WordOrVariable],
        'aliases': ['checkflag'],
        'description': 'Compares a to 1.',
    },
    0x2c: { 'name': 'compareflags',
        'aliases': ['cmd2c', 'compareflags'],
        'description': 'In FireRed, this command is a nop.',
    },
    0x2d: { 'name': 'checkdailyflags',
        'aliases': ['checkdailyflags'],
        'description': 'In FireRed, this command is a nop.',
    },
    0x2e: { 'name': 'resetvars',
        'aliases': ['resetvars'],
        'description': 'Resets the values of variables 0x8000, 0x8001, and 0x8002. Related to RTC in RSE?',
    },
    0x2f: { 'name': 'playsfx',
        'param_names': ['sound_number'],
        'param_types': ['word'],
        'aliases': ['playsfx', 'sound'],
        'description': 'Plays the specified (sound_number) sound. Only one sound may play at a time, with newer ones interrupting older ones.',
    },
    0x30: { 'name': 'checksound',
        'aliases': ['checksound'],
        'description': 'Blocks script execution until the currently-playing sound (triggered by sound) finishes playing.',
    },
    0x31: { 'name': 'fanfare',
        'param_names': ['fanfare_number'],
        'param_types': ['word'],
        'aliases': ['fanfare'],
        'description': 'Plays the specified (fanfare_number) fanfare.',
    },
    0x32: { 'name': 'waitfanfare',
        'aliases': ['waitfanfare'],
        'description': 'Blocks script execution until all currently-playing fanfares finish.',
    },
    0x33: { 'name': 'playmusic',
        'param_names': ['song_number', 'unknown'],
        'param_types': ['word', 'byte'],
        'aliases': ['playsong', 'playmusic', 'playsound'],
        'description': 'Plays the specified (song_number) song. The byte is apparently supposed to be 0x00.',
    },
    0x34: { 'name': 'playmusicbattle',
        'param_names': ['song_number'],
        'param_types': ['word'],
        'aliases': ['playsong2', 'playsong', 'playbattlesong', 'playmusicbattle', 'playbattlemusic'],
        'description': 'Plays the specified (song_number) song.',
    },
    0x35: { 'name': 'fadedefault',
        'aliases': ['fadedefault'],
        'description': "Crossfades the currently-playing song into the map's default song.",
    },
    0x36: { 'name': 'fademusic',
        'param_names': ['song_number'],
        'param_types': ['word'],
        'aliases': ['fadesong', 'fademusic'],
        'description': 'Crossfades the currently-playng song into the specified (song_number) song.',
    },
    0x37: { 'name': 'fadeout',
        'param_names': ['speed'],
        'param_types': ['byte'],
        'aliases': ['fadeout'],
        'description': 'Fades out the currently-playing song.',
    },
    0x38: { 'name': 'fadein',
        'param_names': ['speed'],
        'param_types': ['byte'],
        'aliases': ['fadein'],
        'description': 'Fades the currently-playing song back in.',
    },
    0x39: { 'name': 'warp',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warp'],
        'description': 'Sends the player to Warp warp on Map bank.map. If the specified warp is 0xFF, then the player will instead be sent to (X, Y) on the map.',
    },
    0x3a: { 'name': 'warpmuted',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warpmuted'],
        'description': 'Clone of warp that does not play a sound effect.',
    },
    0x3b: { 'name': 'warpwalk',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warpwalk'],
        'description': 'Clone of warp that uses "a walking effect".',
    },
    0x3c: { 'name': 'warphole',
        'param_names': ['map'],
        'param_types': [MapId],
        'aliases': ['warphole'],
        'description': 'Warps the player to another map using a hole animation.',
    },
    0x3d: { 'name': 'warpteleport',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warpteleport'],
        'description': 'Clone of warp that uses a teleport effect. It is apparently only used in R/S/E.[source]',
    },
    0x3e: { 'name': 'warp3',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warp3'],
        'description': 'Clone of warp. Used by an (unused?) Safari Zone script to return the player to the gatehouse and end the Safari Game.',
    },
    0x3f: { 'name': 'warpplace',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warpplace', 'setwarpplace'],
        'description': 'Sets a default warp place. If a warp tries to send the player to Warp 127 on Map 127.127, they will instead be sent here. Useful when a map has warps that need to go to script-controlled locations (i.e. elevators).',
    },
    0x40: { 'name': 'warp4',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warp4'],
        'description': 'Clone of warp3, except that this writes data to different offsets...',
    },
    0x41: { 'name': 'warp5',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warp5'],
        'description': 'Clone of warp3, except that this writes data to different offsets...',
    },
    0x42: { 'name': 'getplayerxy',
        'param_names': ['X', 'Y'],
        'param_types': [Variable, Variable],
        'aliases': ['getplayerxy', 'getplayerpos'],
        'description': "Retrieves the player's zero-indexed X- and Y-coordinates in the map, and stores them in the specified variables.",
    },
    0x43: { 'name': 'countpokemon',
        'aliases': ['countpokemon', 'countPokemon'],
        'description': "Retrieves the number of Pokemon in the player's party, and stores that number in variable 0x800D (LASTRESULT).",
    },
    0x44: { 'name': 'additem',
        'param_names': ['index', 'quantity'],
        'param_types': [Item, 'word'],
        'aliases': ['additem'],
        'description': "Attempts to add quantity of item index to the player's Bag. If the player has enough room, the item will be added and variable 0x800D (LASTRESULT) will be set to 0x0001; otherwise, LASTRESULT is set to 0x0000.",
    },
    0x45: { 'name': 'removeitem',
        'param_names': ['index', 'quantity'],
        'param_types': [Item, 'word'],
        'aliases': ['removeitem'],
        'description': "Removes quantity of item index from the player's Bag.",
    },
    0x46: { 'name': 'checkitemspace',
        'param_names': ['index', 'quantity'],
        'param_types': [Item, 'word'],
        'aliases': ['checkitemroom', 'checkitemspace'],
        'description': 'Checks if the player has enough space in their Bag to hold quantity more of item index. Sets variable 0x800D (LASTRESULT) to 0x0001 if there is room, or 0x0000 is there is no room.',
    },
    0x47: { 'name': 'checkitem',
        'param_names': ['index', 'quantity'],
        'param_types': [Item, 'word'],
        'aliases': ['checkitem'],
        'description': 'Checks if the player has quantity or more of item index in their Bag. Sets variable 0x800D (LASTRESULT) to 0x0001 if the player has enough of the item, or 0x0000 if they have fewer than quantity of the item.',
    },
    0x48: { 'name': 'checkitemtype',
        'param_names': ['index'],
        'param_types': [Item],
        'aliases': ['checkitemtype'],
        'description': 'Checks which Bag pocket the specified (index) item belongs in, and writes the value to variable 0x800D (LASTRESULT). This script is used to show the name of the proper Bag pocket when the player receives an item via callstd (simplified to giveitem in XSE).',
    },
    0x49: { 'name': 'addpcitem',
        'param_names': ['index', 'quantity'],
        'param_types': [Item, WordOrVariable],
        'aliases': ['addpcitem'],
        'description': "Adds a quantity amount of item index to the player's PC. Both arguments can be variables.",
    },
    0x4a: { 'name': 'checkpcitem',
        'param_names': ['index', 'quantity'],
        'param_types': [Item, WordOrVariable],
        'aliases': ['checkpcitem'],
        'description': "Checks for quantity amount of item index in the player's PC. Both arguments can be variables.",
    },
    0x4b: { 'name': 'adddecor',
        'param_names': ['decoration'],
        'param_types': [Decoration],
        'aliases': ['adddecor', 'adddecoration'],
        'description': 'In FireRed, this command is a nop. (The argument is read, but not used for anything.)',
    },
    0x4c: { 'name': 'removedecor',
        'param_names': ['decoration'],
        'param_types': [Decoration],
        'aliases': ['removedecoration', 'removedecor'],
        'description': 'In FireRed, this command is a nop. (The argument is read, but not used for anything.)',
    },
    0x4d: { 'name': 'testdecor',
        'param_names': ['decoration'],
        'param_types': [Decoration],
        'aliases': ['testdecoration', 'testdecor'],
        'description': 'In FireRed, this command is a nop. (The argument is read, but not used for anything.)',
    },
    0x4e: { 'name': 'checkdecor',
        'param_names': ['decoration'],
        'param_types': [Decoration],
        'aliases': ['checkdecor', 'checkdecoration'],
        'description': 'In FireRed, this command is a nop. (The argument is read, but not used for anything.)',
    },
    0x4f: { 'name': 'move',
        'param_names': ['index', 'movements'],
        'param_types': [WordOrVariable, MovementPointer],
        'aliases': ['move', 'applymovement'],
        'description': 'Applies the movement data at movements to the specified (index) Person event. Also closes any standard message boxes that are still open.',
    },
    0x50: { 'name': 'movecoords',
        'param_names': ['variable', 'movements', 'x', 'y'],
        'param_types': [WordOrVariable, MovementPointer, Byte, Byte],
        'aliases': ['movexy', 'movecoords', 'applymovementxy', 'applymovementpos'],
        'description': "Apparent clone of applymovement. Oddly, it doesn't seem to work at all if applied to any Person other than the player (0xFF), and the X and Y arguments don't seem to do anything.\nThis command in fact uses variables to access the Person event ID. So, for example, if you setvar 0x8000 to 0x3, and then use applymovementpos 0x8000 @move1, Person event 3 will have the movements at @move1 applied to them. Thank you Shiny Quagsire for bringing this to my attention.",
    },
    0x51: { 'name': 'waitmove',
        'param_names': ['index'],
        'param_types': [WordOrVariable],
        'aliases': ['waitmove', 'pauseevent', 'waitmovement'],
        'description': 'Blocks script execution until the movements being applied to the specified (index) Person event finish. If the specified Person event is 0x0000, then the command will block script execution until all Person events affected by applymovement finish their movements. If the specified Person event is not currently being manipulated with applymovement, then this command does nothing.',
    },
    0x52: { 'name': 'waitmovexy',
        'param_names': ['index', 'X', 'Y'],
        'param_types': [WordOrVariable, 'byte', 'byte'],
        'aliases': ['waitmovexy', 'waitmovecoords', 'waitmovementpos', 'pauseeventxy'],
        'description': "Apparent clone of waitmovement. Oddly, it doesn't seem to work at all if applied to any Person other than the player (0xFF), and the X and Y arguments don't seem to do anything.",
    },
    0x53: { 'name': 'disappear',
        'param_names': ['local_ID'],
        'param_types': [WordOrVariable],
        'aliases': ['hidesprite', 'disappear'],
        'description': 'Attempts to hide the specified (local_ID, a local ID) Person event on the current map, by setting its visibility flag if it has a valid one. If the Person does not have a valid visibility flag, this command does nothing.',
    },
    0x54: { 'name': 'disappearxy',
        'param_names': ['index', 'X', 'Y'],
        'param_types': [WordOrVariable, 'byte', 'byte'],
        'aliases': ['hidespritepos', 'disappearxy'],
        'description': 'Clone of hidesprite that also moves the Person? Test it!',
    },
    0x55: { 'name': 'reappear',
        'param_names': ['word'],
        'param_types': [WordOrVariable],
        'aliases': ['reappear', 'showsprite'],
    },
    0x56: { 'name': 'reappearxy',
        'param_names': ['word', 'byte1', 'byte2'],
        'param_types': [WordOrVariable, 'byte', 'byte'],
        'aliases': ['showspritepos', 'reappearxy'],
    },
    0x57: { 'name': 'movesprite',
        'param_names': ['word1', 'word2', 'word3'],
        'param_types': [WordOrVariable, 'word', 'word'],
        'aliases': ['movesprite'],
    },
    0x58: { 'name': 'spritevisible',
        'param_names': ['word', 'byte1', 'byte2'],
        'param_types': [WordOrVariable, 'byte', 'byte'],
        'aliases': ['spritevisible'],
    },
    0x59: { 'name': 'spriteinvisible',
        'param_names': ['word', 'byte1', 'byte2'],
        'param_types': [WordOrVariable, 'byte', 'byte'],
        'aliases': ['spriteinvisible'],
    },
    0x5a: { 'name': 'faceplayer',
        'aliases': ['spriteface', 'faceplayer'],
        'description': 'If the script was called by a Person event, then that Person will turn to face toward the tile that the player is stepping off of.',
    },
    0x5b: { 'name': 'spriteface',
        'param_names': ['word', 'byte'],
        'param_types': [WordOrVariable, 'byte'],
        'aliases': ['faceplayer'],
    },
    # Params vary depending on the value of `type`.
    # See TrainerbattleArgs.
    0x5c: { 'name': 'trainerbattle',
        'param_names': ['args'],
        'param_types': [TrainerbattleArgs],
        'aliases': ['trainerbattle'],
        'description': 'If the Trainer flag for Trainer index is not set, this command does absolutely nothing.',
    },
    0x5d: { 'name': 'reptrainerbattle',
        'aliases': ['repeattrainerbattle', 'reptrainerbattle'],
        'description': 'Starts a trainer battle using the battle information stored in RAM (usually by trainerbattle, which actually calls this command behind-the-scenes), and blocks script execution until the battle finishes.',
    },
    0x5e: { 'name': 'endtrainerbattle',
        'aliases': ['endtrainerbattle'],
    },
    0x5f: { 'name': 'endtrainerbattle2',
        'aliases': ['endtrainerbattle2'],
    },
    0x60: { 'name': 'checktrainerflag',
        'param_names': ['trainer'],
        'param_types': ['word'],
        'aliases': ['checktrainerflag'],
        'description': 'Compares Flag (trainer + 0x500) to 1. (If the flag is set, then the trainer has been defeated by the player.)',
    },
    0x61: { 'name': 'cleartrainerflag',
        'param_names': ['trainer'],
        'param_types': ['word'],
        'aliases': ['cleartrainerflag'],
        'description': "Sets Flag (trainer + 0x500). (I didn't make a mistake. The command names actually are backwards.)",
    },
    0x62: { 'name': 'settrainerflag',
        'param_names': ['trainer'],
        'param_types': ['word'],
        'aliases': ['settrainerflag'],
        'description': "Clears Flag (trainer + 0x500). (I didn't make a mistake. The command names actually are backwards.)",
    },
    0x63: { 'name': 'movespriteperm',
        'param_names': ['word1', 'word2', 'word3'],
        'param_types': ['word', 'word', 'word'],
        'aliases': ['movespriteperm', 'movesprite2'],
    },
    0x64: { 'name': 'moveoffscreen',
        'param_names': ['word'],
        'param_types': [WordOrVariable],
        'aliases': ['moveoffscreen'],
    },
    0x65: { 'name': 'spritebehave',
        'param_names': ['word', 'byte'],
        'param_types': [WordOrVariable, 'byte'],
        'aliases': ['spritebehave'],
    },
    0x66: { 'name': 'waittext',
        'aliases': ['showmsg', 'waittext', 'waitmsg'],
        'description': 'If a standard message box (or its text) is being drawn on-screen, this command blocks script execution until the box and its text have been fully drawn.',
    },
    0x67: { 'name': 'message',
        'param_names': ['text'],
        'param_types': [TextPointer],
        'aliases': ['msg', 'message', 'preparemsg'],
        'description': 'Starts displaying a standard message box containing the specified text. If text is a pointer, then the string at that offset will be loaded and used. If text is script bank 0, then the value of script bank 0 will be treated as a pointer to the text. (You can use loadpointer to place a string pointer in a script bank.)',
    },
    0x68: { 'name': 'closebutton',
        'aliases': ['closebutton', 'closeonkeypress', 'closemsg'],
        'description': 'Holds the current message box open until the player presses a key. The message box is then closed.',
    },
    0x69: { 'name': 'lockall',
        'aliases': ['lockall'],
        'description': 'Ceases movement for all OWs on-screen.',
    },
    0x6a: { 'name': 'lock',
        'aliases': ['lock'],
        'description': "If the script was called by a Person event, then that Person's movement will cease.",
    },
    0x6b: { 'name': 'releaseall',
        'aliases': ['releaseall'],
        'description': 'Resumes normal movement for all OWs on-screen, and closes any standard message boxes that are still open.',
    },
    0x6c: { 'name': 'release',
        'aliases': ['release'],
        'description': "If the script was called by a Person event, then that Person's movement will resume. This command also closes any standard message boxes that are still open.",
    },
    0x6d: { 'name': 'waitbutton',
        'aliases': ['waitkeypress', 'waitbutton'],
        'description': 'Blocks script execution until the player presses any key.',
    },
    0x6e: { 'name': 'yesnobox',
        'param_names': ['X', 'Y'],
        'param_types': ['byte', 'byte'],
        'aliases': ['yesnobox'],
        'description': 'Displays a YES/NO multichoice box at the specified coordinates, and blocks script execution until the user makes a selection. Their selection is stored in variable 0x800D (LASTRESULT); 0x0000 for "NO" or if the user pressed B, and 0x0001 for "YES".',
    },
    0x6f: { 'name': 'multichoice',
        'param_names': ['X', 'Y', 'list', 'B'],
        'param_types': ['byte', 'byte', 'byte', 'byte'],
        'aliases': ['multichoice'],
        'description': 'Displays a multichoice box from which the user can choose a selection, and blocks script execution until a selection is made. Lists of options are predefined and the one to be used is specified with list. If B is set to a non-zero value, then the user will not be allowed to back out of the multichoice with the B button.',
    },
    0x70: { 'name': 'multichoicedef',
        'param_names': ['X', 'Y', 'list', 'default', 'B'],
        'param_types': ['byte', 'byte', 'byte', 'byte', 'byte'],
        'aliases': ['multichoice2', 'multichoicedef'],
        'description': 'Displays a multichoice box from which the user can choose a selection, and blocks script execution until a selection is made. Lists of options are predefined and the one to be used is specified with list. The default argument determines the initial position of the cursor when the box is first opened; it is zero-indexed, and if it is too large, it is treated as 0x00. If B is set to a non-zero value, then the user will not be allowed to back out of the multichoice with the B button.',
    },
    0x71: { 'name': 'multichoicerow',
        'param_names': ['X', 'Y', 'list', 'per_row', 'B'],
        'param_types': ['byte', 'byte', 'byte', 'byte', 'byte'],
        'aliases': ['multichoicerow', 'multichoice3'],
        'description': 'Displays a multichoice box from which the user can choose a selection, and blocks script execution until a selection is made. Lists of options are predefined and the one to be used is specified with list. The per_row argument determines how many list items will be shown on a single row of the box.',
    },
    0x72: { 'name': 'showbox',
        'param_names': ['byte1', 'byte2', 'byte3', 'byte4'],
        'param_types': ['byte', 'byte', 'byte', 'byte'],
        'aliases': ['showbox'],
    },
    0x73: { 'name': 'hidebox',
        'param_names': ['byte1', 'byte2', 'byte3', 'byte4'],
        'param_types': ['byte', 'byte', 'byte', 'byte'],
        'aliases': ['hidebox'],
    },
    0x74: { 'name': 'clearbox',
        'param_names': ['byte1', 'byte2', 'byte3', 'byte4'],
        'param_types': ['byte', 'byte', 'byte', 'byte'],
        'aliases': ['clearbox'],
    },
    0x75: { 'name': 'showpokepic',
        'param_names': ['species', 'X', 'Y'],
        'param_types': [Species, 'byte', 'byte'],
        'aliases': ['showpokepic'],
        'description': 'Displays a box containing the front sprite for the specified (species) Pokemon species.',
    },
    0x76: { 'name': 'hidepokepic',
        'aliases': ['hidepokepic'],
        'description': 'Hides all boxes displayed with showpokepic.',
    },
    0x77: { 'name': 'showcontestwinner',
        'param_names': ['a'],
        'param_types': ['byte'],
        'aliases': ['showcontestwinner'],
        'description': 'In FireRed, this command is a nop. (The argument is discarded.)',
    },
    0x78: { 'name': 'braillemsg',
        'param_names': ['text'],
        'param_types': [BraillePointer],
        'aliases': ['braillemsg'],
        'description': 'Displays the string at pointer as braille text in a standard message box. The string must be formatted to use braille characters.',
    },
    0x79: { 'name': 'givepokemon',
        'param_names': ['species', 'level', 'item', 'unknown1', 'unknown2', 'unknown3'],
        'param_types': [Species, 'byte', Item, 'long', 'long', 'byte'],
        'aliases': ['givePokemon', 'givepokemon'],
        'description': 'Gives the player one of the specified (species) Pokemon at level level holding item. The unknown arguments should all be zeroes.',
    },
    0x7a: { 'name': 'giveegg',
        'param_names': ['word'],
        'param_types': ['word'],
        'aliases': ['giveegg'],
    },
    0x7b: { 'name': 'setpokemove',
        'param_names': ['byte1', 'byte2', 'word'],
        'param_types': ['byte', 'byte', 'word'],
        'aliases': ['setpkmnpp', 'setpokemove'],
    },
    0x7c: { 'name': 'checkattack',
        'param_names': ['index'],
        'param_types': [Move],
        'aliases': ['checkattack'],
        'description': "Checks if at least one Pokemon in the player's party knows the specified (index) attack. If so, variable 0x800D (LASTRESULT) is set to the (zero-indexed) slot number of the Pokemon that knows the move. If not, LASTRESULT is set to 0x0006.",
    },
    0x7d: { 'name': 'bufferpoke',
        'param_names': ['out', 'species'],
        'param_types': ['byte', Species],
        'aliases': ['bufferpokemon', 'storepokemon', 'bufferPokemon', 'bufferpoke'],
        'description': 'Writes the name of the Pokemon at index species to the specified buffer.',
    },
    0x7e: { 'name': 'bufferfirstpoke',
        'param_names': ['out'],
        'param_types': ['byte'],
        'aliases': ['bufferfirstpoke', 'bufferfirstpokemon', 'storefirstpokemon', 'bufferfirstPokemon'],
        'description': "Writes the name of the first Pokemon in the player's party to the specified buffer.",
    },
    0x7f: { 'name': 'bufferpartypoke',
        'param_names': ['out', 'slot'],
        'param_types': ['byte', 'word'],
        'aliases': ['storepartypokemon', 'bufferpartypokemon', 'bufferpartypoke', 'bufferpartyPokemon'],
        'description': 'Writes the name of the Pokemon in slot slot (zero-indexed) of the player\'s party to the specified buffer. If an empty or invalid slot is specified, ten spaces ("") are written to the buffer.',
    },
    0x80: { 'name': 'bufferitem',
        'param_names': ['out', 'item'],
        'param_types': ['byte', Item],
        'aliases': ['bufferitem', 'storeitem'],
        'description': 'Writes the name of the item at index item to the specified buffer. If the specified index is larger than the number of items in the game (0x176), the name of item 0 ("????????") is buffered instead.',
    },
    0x81: { 'name': 'bufferdecor',
        'param_names': ['a', 'decoration'],
        'param_types': ['byte', Decoration],
        'aliases': ['storedecoration', 'bufferdecoration', 'bufferdecor'],
        'description': 'In FireRed, this command is a nop. (The first argument is discarded immediately. The second argument is read, but not used for anything.)',
    },
    0x82: { 'name': 'bufferattack',
        'param_names': ['out', 'attack'],
        'param_types': ['byte', Move],
        'aliases': ['storeattack', 'bufferattack'],
        'description': 'Writes the name of the attack at index attack to the specified buffer.',
    },
    0x83: { 'name': 'buffernum',
        'param_names': ['out', 'input'],
        'param_types': ['byte', 'word'],
        'aliases': ['buffernumber', 'buffernum'],
        'description': 'Converts the value of input to a decimal string, and writes that string to the specified buffer.',
    },
    0x84: { 'name': 'bufferstd',
        'param_names': ['out', 'index'],
        'param_types': ['byte', 'word'],
        'aliases': ['bufferstd'],
        'description': "Writes the standard string identified by index to the specified buffer. Specifying an invalid standard string (e.x. 0x2B) can and usually will cause data corruption (I've observed destruction of the stored player name and crashes when entering/exiting certain menu screens).",
    },
    0x85: { 'name': 'buffertext',
        'param_names': ['out', 'offset'],
        'param_types': ['byte', TextPointer],
        'aliases': ['buffertext', 'bufferstring', 'storetext'],
        'description': 'Copies the string at offset to the specified buffer.',
    },
    0x86: { 'name': 'pokemart',
        'param_names': ['products'],
        'param_types': [PokemartPointer],
        'aliases': ['pokemart'],
        'description': 'Opens the Pokemart system, offering the specified products for sale.',
    },
    0x87: { 'name': 'pokemartdecor',
        'param_names': ['products'],
        'param_types': [PokemartDecorPointer],
        'aliases': ['pokemartdecor', 'pokemart2'],
        'description': 'Apparent clone of pokemart.',
    },
    0x88: { 'name': 'pokemartbp',
        'param_names': ['products'],
        'param_types': [PokemartPointer],
        'aliases': ['pokemartbp', 'pokemart3'],
        'description': 'Apparent clone of pokemart.',
    },
    0x89: { 'name': 'pokecasino',
        'param_names': ['word'],
        'param_types': ['word'],
        'aliases': ['pokecasino'],
    },
    0x8a: { 'name': 'event_8a',
        'param_names': ['byte1', 'byte2', 'byte3'],
        'param_types': [Byte, Byte, Byte],
        'aliases': ['cmd8a'],
        'description': 'In FireRed, this command is a nop.',
    },
    0x8b: { 'name': 'choosecontestpkmn',
        'aliases': ['choosecontestpkmn'],
        'description': 'In FireRed, this command sets the byte at 0x03000EA8 to 0x01. I do not know what that means.',
    },
    0x8c: { 'name': 'startcontest',
        'aliases': ['startcontest'],
        'description': 'In FireRed, this command is a nop.',
    },
    0x8d: { 'name': 'showcontestresults',
        'aliases': ['showcontestresults'],
        'description': 'In FireRed, this command is a nop.',
    },
    0x8e: { 'name': 'contestlinktransfer',
        'aliases': ['contestlinktransfer'],
        'description': 'In FireRed, this command is a nop.',
    },
    0x8f: { 'name': 'random',
        'param_names': ['limit'],
        'param_types': ['word'],
        'aliases': ['random'],
        'description': 'Stores a random integer between 0 and limit in variable 0x800D (LASTRESULT).',
    },
    0x90: { 'name': 'givemoney',
        'param_names': ['value', 'check'],
        'param_types': ['long', 'byte'],
        'aliases': ['givemoney'],
        'description': "If check is 0x00, this command adds value to the player's money.",
    },
    0x91: { 'name': 'paymoney',
        'param_names': ['value', 'check'],
        'param_types': ['long', 'byte'],
        'aliases': ['paymoney'],
        'description': "If check is 0x00, this command subtracts value from the player's money.",
    },
    0x92: { 'name': 'checkmoney',
        'param_names': ['value', 'check'],
        'param_types': ['long', 'byte'],
        'aliases': ['checkmoney'],
        'description': 'If check is 0x00, this command will check if the player has value or more money; script variable 0x800D (LASTRESULT) is set to 0x0001 if the player has enough money, or 0x0000 if the do not.',
    },
    0x93: { 'name': 'showmoney',
        'param_names': ['X', 'Y'],
        'param_types': ['byte', 'byte'],
        'aliases': ['showmoney'],
        'description': 'Spawns a secondary box showing how much money the player has.',
    },
    0x94: { 'name': 'hidemoney',
        'param_names': ['X', 'Y'],
        'param_types': ['byte', 'byte'],
        'aliases': ['hidemoney'],
        'description': 'Hides the secondary box spawned by showmoney.',
    },
    0x95: { 'name': 'updatemoney',
        'param_names': ['X', 'Y'],
        'param_types': ['byte', 'byte'],
        'aliases': ['updatemoney'],
        'description': 'Updates the secondary box spawned by showmoney. (What does it do with its arguments?)',
    },
    0x96: { 'name': 'event_96',
        'param_names': ['word'],
        'param_types': [Word],
        'aliases': ['cmd96'],
        'description': 'In FireRed, this command is a nop.',
    },
    0x97: { 'name': 'fadescreen',
        'param_names': ['effect'],
        'param_types': ['byte'],
        'aliases': ['fadescreen'],
        'description': "Fades the screen to black or back, using the specified effect. Effect 0x00 fades in, and effect 0x01 fades out. I don't know if other effects exist.",
    },
    0x98: { 'name': 'fadescreendelay',
        'param_names': ['byte1', 'byte2'],
        'param_types': ['byte', 'byte'],
        'aliases': ['fadescreendelay'],
    },
    0x99: { 'name': 'darken',
        'param_names': ['word'],
        'param_types': ['word'],
        'aliases': ['darken'],
    },
    0x9a: { 'name': 'lighten',
        'param_names': ['byte'],
        'param_types': ['byte'],
        'aliases': ['lighten'],
    },
    0x9b: { 'name': 'message2',
        'param_names': ['pointer'],
        'param_types': [TextPointer],
        'aliases': ['message2'],
    },
    0x9c: { 'name': 'doanimation',
        'param_names': ['animation'],
        'param_types': ['word'],
        'aliases': ['doanimation'],
        'description': 'Executes the specified field move animation.',
    },
    0x9d: { 'name': 'setanimation',
        'param_names': ['animation', 'slot'],
        'param_types': ['byte', WordOrVariable],
        'aliases': ['setanimation'],
        'description': 'Tells the game which party Pokemon to use for the next field move animation.',
    },
    0x9e: { 'name': 'checkanimation',
        'param_names': ['animation'],
        'param_types': ['word'],
        'aliases': ['checkanimation'],
        'description': 'Blocks script execution until all playing field move animations complete.',
    },
    0x9f: { 'name': 'sethealplace',
        'param_names': ['flightspot'],
        'param_types': ['word'],
        'aliases': ['sethealplace', 'sethealingplace'],
        'description': 'Sets which healing place the player will return to if all of the Pokemon in their party faint. A list of available healing places can be found on PokeCommunity.',
    },
    0xa0: { 'name': 'checkgender',
        'aliases': ['checkgender'],
        'description': "Checks the player's gender. If male, then 0x0000 is stored in variable 0x800D (LASTRESULT). If female, then 0x0001 is stored in LASTRESULT.",
    },
    0xa1: { 'name': 'pokecry',
        'param_names': ['species', 'effect'],
        'param_types': [Species, 'word'],
        'aliases': ['cry', 'pokecry'],
        'description': "Plays the specified (species) Pokemon's cry. You can use waitcry to block script execution until the sound finishes.",
    },
    0xa2: { 'name': 'setmaptile',
        'param_names': ['X', 'Y', 'tile_number', 'tile_attrib'],
        'param_types': ['word', 'word', 'word', 'word'],
        'aliases': ['setmaptile'],
        'description': 'Changes the tile at (X, Y) on the current map.',
    },
    0xa3: { 'name': 'resetweather',
        'aliases': ['resetweather'],
        'description': 'Queues a weather change to the default weather for the map.',
    },
    0xa4: { 'name': 'setweather',
        'param_names': ['type'],
        'param_types': ['word'],
        'aliases': ['setweather'],
        'description': 'Queues a weather change to type weather.',
    },
    0xa5: { 'name': 'doweather',
        'aliases': ['doweather'],
        'description': 'Executes the weather change queued with resetweather or setweather. The current weather will smoothly fade into the queued weather.',
    },
    0xa6: { 'name': 'tileeffect',
        'param_names': ['subroutine'],
        'param_types': ['byte'],
        'aliases': ['cmda6'],
        'description': 'This command manages cases in which maps have tiles that change state when stepped on (specifically, cracked/breakable floors).',
    },
    0xa7: { 'name': 'setmapfooter',
        'param_names': ['word'],
        'param_types': ['word'],
        'aliases': ['setmapfooter'],
    },
    0xa8: { 'name': 'spritelevelup',
        'param_names': ['word', 'byte1', 'byte2', 'byte3'],
        'param_types': ['word', 'byte', 'byte', 'byte'],
        'aliases': ['spritelevelup'],
    },
    0xa9: { 'name': 'restorespritelevel',
        'param_names': ['word', 'byte1', 'byte2'],
        'param_types': ['word', 'byte', 'byte'],
        'aliases': ['restorespritelevel', 'rebufferspritelevel'],
    },
    0xaa: { 'name': 'createvsprite',
        'param_names': ['byte1', 'byte2', 'word1', 'word2', 'byte3', 'byte4'],
        'param_types': ['byte', 'byte', 'word', 'word', 'byte', 'byte'],
        'aliases': ['createvsprite', 'createsprite'],
    },
    0xab: { 'name': 'vspriteface',
        'param_names': ['byte1', 'byte2'],
        'param_types': ['byte', 'byte'],
        'aliases': ['vspriteface', 'movesprite2'],
    },
    0xac: { 'name': 'setdooropened',
        'param_names': ['X', 'Y'],
        'param_types': [WordOrVariable, WordOrVariable],
        'aliases': ['setdooropened'],
        'description': 'Queues the opening of the door tile at (X, Y) with an animation.',
    },
    0xad: { 'name': 'setdoorclosed',
        'param_names': ['X', 'Y'],
        'param_types': [WordOrVariable, WordOrVariable],
        'aliases': ['setdoorclosed'],
        'description': 'Queues the closing of the door tile at (X, Y) with an animation.',
    },
    0xae: { 'name': 'doorchange',
        'aliases': ['doorchange'],
        'description': 'Executes the state changes queued with setdooropened, setdoorclosed, setdooropened2, and setdoorclosed2.',
    },
    0xaf: { 'name': 'setdooropened2',
        'param_names': ['X', 'Y'],
        'param_types': [WordOrVariable, WordOrVariable],
        'aliases': ['setdooropened2'],
        'description': 'Queues the opening of the door tile at (X, Y) without an animation.',
    },
    0xb0: { 'name': 'setdoorclosed2',
        'param_names': ['X', 'Y'],
        'param_types': [WordOrVariable, WordOrVariable],
        'aliases': ['setdoorclosed2'],
        'description': 'Queues the closing of the door tile at (X, Y) without an animation.',
    },
    0xb1: { 'name': 'event_b1',
        'aliases': ['cmdb1'],
        'description': 'In FireRed, this command is a nop.',
    },
    0xb2: { 'name': 'event_b2',
        'aliases': ['cmdb2'],
        'description': 'In FireRed, this command is a nop.',
    },
    0xb3: { 'name': 'checkcoins',
        'param_names': ['word'],
        'param_types': ['word'],
        'aliases': ['checkcoins'],
    },
    0xb4: { 'name': 'givecoins',
        'param_names': ['word'],
        'param_types': ['word'],
        'aliases': ['givecoins'],
    },
    0xb5: { 'name': 'removecoins',
        'param_names': ['word'],
        'param_types': ['word'],
        'aliases': ['removecoins'],
    },
    0xb6: { 'name': 'setwildbattle',
        'param_names': ['species', 'level', 'item'],
        'param_types': [Species, 'byte', Item],
        'aliases': ['setwildbattle'],
        'description': 'Prepares to start a wild battle against a species at Level level holding item. Running this command will not affect normal wild battles. You start the prepared battle with dowildbattle.',
    },
    0xb7: { 'name': 'dowildbattle',
        'aliases': ['dowildbattle'],
        'description': 'Starts a wild battle against the Pokemon generated by setwildbattle. Blocks script execution until the battle finishes.',
    },
    0xb8: { 'name': 'setvaddress',
        'param_names': ['long', 'word'],
        'param_types': ['long', 'word'],
        'aliases': ['setvirtualaddress', 'setvaddress'],
    },
    0xb9: { 'name': 'vjump',
        'param_names': ['pointer'],
        'param_types': [EventScriptPointer],
        'end': True,
        'aliases': ['virtualgoto', 'vjump', 'virtualjump'],
    },
    0xba: { 'name': 'vcall',
        'param_names': ['pointer'],
        'param_types': [EventScriptPointer],
        'aliases': ['virtualcall', 'vcall'],
    },
    0xbb: { 'name': 'if5',
        'param_names': ['byte', 'pointer'],
        'param_types': ['byte', EventScriptPointer],
        'aliases': ['virtualgotoif', 'virtualjumpif', 'if'],
    },
    0xbc: { 'name': 'if6',
        'param_names': ['byte', 'pointer'],
        'param_types': ['byte', EventScriptPointer],
        'aliases': ['virtualcallif', 'if'],
    },
    0xbd: { 'name': 'vtext',
        'param_names': ['pointer'],
        'param_types': ['pointer'],
        'aliases': ['fakemsgbox', 'vtext'],
    },
    0xbe: { 'name': 'vloadptr',
        'param_names': ['pointer'],
        'param_types': ['pointer'],
        'aliases': ['fakeloadpointer', 'vloadptr'],
    },
    0xbf: { 'name': 'vbuffer',
        'param_names': ['byte', 'pointer'],
        'param_types': ['byte', 'pointer'],
        'aliases': ['vbuffer', 'fakestore', 'fakebuffer'],
    },
    0xc0: { 'name': 'showcoins',
        'param_names': ['X', 'Y'],
        'param_types': ['byte', 'byte'],
        'aliases': ['showcoins'],
        'description': 'Spawns a secondary box showing how many Coins the player has.',
    },
    0xc1: { 'name': 'hidecoins',
        'param_names': ['X', 'Y'],
        'param_types': ['byte', 'byte'],
        'aliases': ['hidecoins'],
        'description': "Hides the secondary box spawned by showcoins. It doesn't appear to use its arguments, but they are still required.",
    },
    0xc2: { 'name': 'updatecoins',
        'param_names': ['X', 'Y'],
        'param_types': ['byte', 'byte'],
        'aliases': ['updatecoins'],
        'description': 'Updates the secondary box spawned by showcoins. (What does it do with its arguments?)',
    },
    0xc3: { 'name': 'inccounter',
        'param_names': ['a'],
        'param_types': ['byte'],
        'aliases': ['cmdc3'],
        'description': "Increases the value of the specified hidden variable by 1. The hidden variable's value will not be allowed to exceed 0x00FFFFFF.",
    },
    0xc4: { 'name': 'warp6',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warp6'],
        'description': "Clone of warp... Except that it doesn't appear to have any effect when used in some of FireRed's default level scripts. (If it did, Berry Forest would be impossible to enter...)",
    },
    0xc5: { 'name': 'waitpokecry',
        'aliases': ['waitcry', 'waitpokecry'],
        'description': 'Blocks script execution until cry finishes.',
    },
    0xc6: { 'name': 'bufferboxname',
        'param_names': ['out', 'box'],
        'param_types': ['byte', 'word'],
        'aliases': ['bufferboxname', 'storeboxname'],
        'description': 'Writes the name of the specified (box) PC box to the specified buffer.',
    },
    0xc7: { 'name': 'textcolor',
        'param_names': ['color'],
        'param_types': ['byte'],
        'aliases': ['textcolor'],
        'description': "Sets the color of the text in standard message boxes. 0x00 produces blue (male) text, 0x01 produces red (female) text, 0xFF resets the color to the default for the current OW's gender, and all other values produce black text.",
    },
    0xc8: { 'name': 'loadhelp',
        'param_names': ['pointer'],
        'param_types': ['pointer'],
        'aliases': ['cmdc8'],
        'description': 'The exact purpose of this command is unknown, but it is related to the blue help-text box that appears on the bottom of the screen when the Main Menu is opened.',
    },
    0xc9: { 'name': 'unloadhelp',
        'aliases': ['cmdc9'],
        'description': 'The exact purpose of this command is unknown, but it is related to the blue help-text box that appears on the bottom of the screen when the Main Menu is opened.',
    },
    0xca: { 'name': 'signmsg',
        'aliases': ['signmsg'],
        'description': 'After using this command, all standard message boxes will use the signpost frame.',
    },
    0xcb: { 'name': 'normalmsg',
        'aliases': ['normalmsg'],
        'description': 'Ends the effects of signmsg, returning message box frames to normal.',
    },
    0xcc: { 'name': 'comparehiddenvar',
        'param_names': ['a', 'value'],
        'param_types': ['byte', 'long'],
        'aliases': ['comparehiddenvar', 'comparecounter'],
        'description': 'Compares the value of a hidden variable to a dword.',
    },
    0xcd: { 'name': 'setobedience',
        'param_names': ['slot'],
        'param_types': ['word'],
        'aliases': ['setobedience'],
        'description': "Makes the Pokemon in the specified slot of the player's party obedient. It will not randomly disobey orders in battle.",
    },
    0xce: { 'name': 'checkobedience',
        'param_names': ['slot'],
        'param_types': ['word'],
        'aliases': ['checkobedience'],
        'description': "Checks if the Pokemon in the specified slot of the player's party is obedient. If the Pokemon is disobedient, 0x0001 is written to script variable 0x800D (LASTRESULT). If the Pokemon is obedient (or if the specified slot is empty or invalid), 0x0000 is written.",
    },
    0xcf: { 'name': 'execram',
        'end': True,
        'description': "Depending on factors I haven't managed to understand yet, this command may cause script execution to jump to the offset specified by the pointer at 0x020370A4.",
        'aliases': ['execram', 'executeram'],
    },
    0xd0: { 'name': 'setworldflag',
        'param_names': ['worldmapflag'],
        'param_types': ['word'],
        'aliases': ['setworldmapflag', 'setworldflag'],
        'description': 'Sets worldmapflag to 1. This allows the player to Fly to the corresponding map, if that map has a flightspot.',
    },
    0xd1: { 'name': 'warpteleport2',
        'param_names': ['map', 'warp', 'X', 'Y'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warpteleport2'],
        'description': 'Clone of warpteleport? It is apparently only used in FR/LG, and only with specials.[source]',
    },
    0xd2: { 'name': 'setcatchlocale',
        'param_names': ['slot', 'location'],
        'param_types': ['word', 'byte'],
        'aliases': ['setcatchlocation', 'setcatchlocale'],
        'description': 'Changes the location where the player caught the Pokemon in the specified slot of their party. A list of valid catch locations can be found on PokeCommunity.',
    },
    0xd3: { 'name': 'event_d3',
        'param_names': ['unknown'],
        'param_types': [WordOrVariable],
        'aliases': ['braille2'],
        #'description': 'Sets variable 0x8004 to a value based on the width of the braille string at text.',
    },
    0xd4: { 'name': 'event_d4',
        'aliases': [],
    },
    0xd5: { 'name': 'event_d5',
        'param_names': ['var'],
        'param_types': [Variable],
        'aliases': ['cmdd5'],
        'description': 'In FireRed, this command is a nop.',
    },
    0xd6: { 'name': 'event_d6',
        'aliases': [],
    },
    0xd7: { 'name': 'warp7',
        'param_names': ['map', 'byte', 'word1', 'word2'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warp7'],
    },
    0xd8: { 'name': 'event_d8',
        'aliases': [],
    },
    0xd9: { 'name': 'event_d9',
        'aliases': [],
    },
    0xda: { 'name': 'hidebox2',
        'aliases': ['hidebox2'],
    },
    0xdb: { 'name': 'message3',
        'param_names': ['pointer'],
        'param_types': [TextPointer],
        'aliases': ['preparemsg3', 'message3'],
    },
    0xdc: { 'name': 'fadescreen3',
        'param_names': ['byte'],
        'param_types': ['byte'],
        'aliases': ['fadescreen3'],
    },
    0xdd: { 'name': 'buffertrainerclass',
        'param_names': ['byte', 'word'],
        'param_types': ['byte', 'word'],
        'aliases': ['buffertrainerclass', 'storetrainerclass'],
    },
    0xde: { 'name': 'buffertrainername',
        'param_names': ['byte', 'word'],
        'param_types': ['byte', 'word'],
        'aliases': ['buffertrainername', 'storetrainername'],
    },
    0xdf: { 'name': 'pokenavcall',
        'param_names': ['pointer'],
        'param_types': ['pointer'],
        'aliases': ['pokenavcall'],
    },
    0xe0: { 'name': 'warp8',
        'param_names': ['map', 'byte', 'word1', 'word2'],
        'param_types': [MapId, 'byte', 'word', 'word'],
        'aliases': ['warp8'],
    },
    0xe1: { 'name': 'buffercontesttype',
        'param_names': ['byte', 'word'],
        'param_types': ['byte', 'word'],
        'aliases': ['storecontesttype', 'buffercontesttype'],
    },
    0xe2: { 'name': 'storeitems',
        'param_names': ['out', 'item', 'quantity'],
        'param_types': ['byte', Item, 'word'],
        'aliases': ['bufferitems', 'storeitems'],
        'description': 'Writes the name of the specified (item) item to the specified buffer. If the specified item is a Berry (0x85 - 0xAE) or Poke Ball (0x4) and if the quantity is 2 or more, the buffered string will be pluralized ("IES" or "S" appended). If the specified item is the Enigma Berry, I have no idea what this command does (but testing showed no pluralization). If the specified index is larger than the number of items in the game (0x176), the name of item 0 ("????????") is buffered instead.',
    },
}

def get_param_class(param_type):
    if type(param_type) is str:
        return {
            'byte': Byte,
            'word': Word,
            'long': Int,
            'pointer': Pointer,
        }.get(param_type)
    return param_type

def make_command_class(byte, command, class_name):
    attributes = {}
    attributes.update(command)
    attributes['id'] = byte
    param_names = command.get('param_names', list())
    param_types = command.get('param_types', list())
    attributes['param_classes'] = [Byte] + zip(param_names, map(get_param_class, param_types))
    return classobj(class_name, (Command,), attributes)

def make_command_classes(commands, class_name_base=''):
    classes = {}
    for byte, command in commands.items():
        class_name = class_name_base + command['name']
        classes[byte] = make_command_class(byte, command, class_name)
        classes[command['name']] = classes[byte]
    return classes

event_command_classes = make_command_classes(event_commands, 'EventCommand_')


# Extend jumpif
class EventCommand_jumpif(event_command_classes['jumpif']):
    def to_asm(self):
        if self.params['condition'].value == 1:
            return '\tjumpeq ' + ', '.join(param.asm for param in self.chunks[2:])
        else:
            return super(EventCommand_jumpif, self).to_asm()
event_command_classes[EventCommand_jumpif.id] = EventCommand_jumpif
event_command_classes['jumpif'] = EventCommand_jumpif


# EventScript macros

class EventScriptMacro(Macro):
	def parse(self):
		self.address = self.chunks[0].address
		self.last_address = self.chunks[-1].last_address
	def _get_params(self):
		pass
	@property
	def asm(self):
		return ', '.join(param.asm for param in self._get_params())

class Switch(EventScriptMacro):
    name = 'switch'
    def _get_params(self):
        return [self.chunks[0].params['source']]

class SwitchCase(EventScriptMacro):
    name = 'case'
    def parse(self):
        self.chunks = [self.compare, self.jumpif]
        EventScriptMacro.parse(self)
    def _get_params(self):
        return [self.compare.params['value'], self.jumpif.params['destination']]

class MsgBox(EventScriptMacro):
	name = 'msgbox'
	def parse(self):
		self.chunks = [self.loadptr, self.callstd]
		EventScriptMacro.parse(self)
	def _get_params(self):
		return [self.loadptr.params['value'], self.callstd.params['function']]

class GiveItem(EventScriptMacro):
	name = 'giveitem'
	def parse(self):
		self.chunks = [self.copyitem, self.copyamount, self.callstd]
		EventScriptMacro.parse(self)
	def _get_params(self):
		item = self.copyitem.params['source']
		amount = self.copyamount.params['source']
		function = self.callstd.params['function']
		params = [item]
		if amount.value != 1 or function.value != 0:
			params += [amount]
		if function.value != 0:
			params += [function]
		return params

class GiveDecoration(EventScriptMacro):
	name = 'givedecoration'
	def parse(self):
		self.chunks = [self.setorcopyvar, self.callstd]
		EventScriptMacro.parse(self)
	def _get_params(self):
		return [self.setorcopyvar.params['source']]

#class GiveItemFanfare(EventScriptMacro):
#	name = 'giveitem'
#	def parse(self):
#		self.chunks = [self.copyitem, self.copyamount, self.copyse, self.callstd]
#		EventScriptMacro.parse(self)
#	def _get_params(self):
#		return [self.copyitem.params['source'], self.copyamount.params['source'], self.copyse.params['source']]

#class WildBattle(EventScriptMacro):
#	name = 'wildbattle'
#	def parse(self):
#		self.chunks = [self.setwildbattle, self.dowildbattle]
#		EventScriptMacro.parse(self)
#	def _get_params(self):
#		params = self.setwildbattle.params
#		return [params['species'], params['level'], params['item']]

#class AddPokenav(EventScriptMacro):
#	name = 'addpokenav'
#	def parse(self):
#		self.chunks = [self.copyvarifnotzero, self.callstd]
#		EventScriptMacro.parse(self)
#	def _get_params(self):
#		return [self.copyvarifnotzero['source']]


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('address')
    args = ap.parse_args()

    import versions
    version = versions.ruby
    setup_version(version)
    print print_recursive(
        EventScript,
        int(args.address, 16),
        version=version,
        rom=version['baserom']
    )
