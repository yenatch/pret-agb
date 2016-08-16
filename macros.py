from create_event_macros import get_macro

def get_script_macros(commands):
	lines = []
	for byte, command in sorted(commands.items()):
		if command.has_key('macro'):
			lines += [command['macro']]
			continue
		lines += [get_macro(byte, command).rstrip()]
	text = '\n\n'.join(lines)
	return text
