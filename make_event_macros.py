from event_script import event_commands
from macros import get_script_macros

event_commands[0x5c]['macro'] = """\
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

event_supplementary = """
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

def get_event_macros():
	return get_script_macros(event_commands) + '\n\n' + event_supplementary

if __name__ == '__main__':
	print get_event_macros()
