# coding: utf-8

"""Pokemon Emerald event script parsing.
"""

from new import classobj

import sys

from script import *
from event_commands import *


force_stop_addresses = [
	0x209a99, # SlateportCityBattleTent waitstate
	0x2c8381, # TrainerHill1F missing end
]

class EventScript(Script):
    commands = event_command_classes

    def parse(self):
        Script.parse(self)
        self.check_forced_stops()
        self.filter_msgbox()
        self.check_extra_ends()

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
        """
        Some scripts ending in 'jump' have an extra 'end' afterward.
        """
        chunk = self.chunks[-1]
        if not hasattr(chunk, 'name') or chunk.name not in ['jump']:
            return
        address = self.last_address
        byte = Byte(address)
        command_class = self.commands.get(Byte(address).value)
        if command_class:
            if command_class.name in ['end']:
                command = command_class(address)
                self.chunks += [command]
                address += command.length
        self.last_address = address

    def filter_msgbox(self):
        """
        The loadptr command usually (always?) points to a string, but not necessarily.
        Eventually, this will replace loadptr/callstd combos with higher-level macros like msgbox.
        """
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


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('address')
    args = ap.parse_args()

    print print_recursive(
        EventScript,
        int(args.address, 16)
    )
