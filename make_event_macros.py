from create_event_macros import make_event_macro
from event_script import event_commands

trainerbattle = """\
	@ If the Trainer flag for Trainer index is not set, this command does absolutely nothing.
	.macro trainerbattle type, trainer, word, pointer1, pointer2, pointer3, pointer4
	.byte 0x5c
	.byte \\type
	.2byte \\trainer
	.2byte \\word
	.if \\type == 0
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
	.elseif \\type == 1
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
		.4byte \\pointer3 @ event script
	.elseif \\type == 2
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
		.4byte \\pointer3 @ event script
	.elseif \\type == 3
		.4byte \\pointer1 @ text
	.elseif \\type == 4
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
		.4byte \\pointer3 @ text
	.elseif \\type == 5
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
	.elseif \\type == 6
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
		.4byte \\pointer3 @ text
		.4byte \\pointer4 @ event script
	.elseif \\type == 7
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
		.4byte \\pointer3 @ text
	.elseif \\type == 8
		.4byte \\pointer1 @ text
		.4byte \\pointer2 @ text
		.4byte \\pointer3 @ text
		.4byte \\pointer4 @ event script
	.endif
	.endm
"""

supplementary = """
@ Supplementary

	.macro jumpeq dest
	jumpif 1, \\dest
	.endm

	.macro switch var
	copyvar 0x8000, \\var
	.endm

	.macro case condition, dest
	compare 0x8000, \\condition
	jumpeq \\dest
	.endm
"""

def print_event_macros():
	lines = []
	event_commands[0x5c] = {'macro': trainerbattle}
	for byte, cmd in sorted(event_commands.items()):
		if cmd.has_key('macro'):
			lines += [cmd['macro']]
			continue
		lines += [make_event_macro(byte, cmd).rstrip()]
	text = '\n\n'.join(lines)
	text = '\n'.join(line.rstrip() for line in text.split('\n'))
	text += '\n\n' + supplementary
	print text

if __name__ == '__main__':
	print_event_macros()
