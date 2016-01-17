from create_event_macros import make_event_macro
from event_commands import event_commands

trainerbattle = """\
	; If the Trainer flag for Trainer index is not set, this command does absolutely nothing.
	.macro trainerbattle type, word1, word2, pointer1, pointer2, pointer3, pointer4
	.byte 0x5c
	.byte \\type
	.2byte \\word1
	.2byte \\word2
if type == 0
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
endc
if type == 1
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
	.4byte \\pointer3 ; event script
endc
if type == 2
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
	.4byte \\pointer3 ; event script
endc
if type == 3
	.4byte \\pointer1 ; text
endc
if type == 4
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
	.4byte \\pointer3 ; text
endc
if type == 5
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
endc
if type == 6
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
	.4byte \\pointer3 ; text
	.4byte \\pointer4 ; event script
endc
if type == 7
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
	.4byte \\pointer3 ; text
endc
if type == 8
	.4byte \\pointer1 ; text
	.4byte \\pointer2 ; text
	.4byte \\pointer3 ; text
	.4byte \\pointer4 ; event script
endc
	.endm
"""

other_trainerbattle = """
if type != 3
	.4byte \\pointer2 ; text
else
endc
if type == 1 || type == 2
	.4byte \\pointer3 ; event script
endc
if type == 4 || type == 6 || type == 7 || type == 8
	.4byte \\pointer3 ; text
endc
if type == 6 || type == 8
	.4byte \\pointer4 ; event script
endc
"""

def print_event_macros():
	lines = []
	event_commands[0x5c] = {'macro': trainerbattle}
	for byte, cmd in event_commands.items():
		if cmd.has_key('macro'):
			lines += [cmd['macro']]
			continue
		lines += [make_event_macro(byte, cmd).rstrip()]
	text = '\n\n'.join(lines)
	text = '\n'.join(line.rstrip() for line in text.split('\n'))
	print text

if __name__ == '__main__':
	print_event_macros()
