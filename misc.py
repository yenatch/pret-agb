"""This is where one-off dumps go to die.
"""

from script import *
from event_script import *
from dump_maps import *
from battle_script import *


class Specials(List):
	param_classes = [ThumbPointer]
	count = 0x558 / 4
	address = 0x14b194

class StdScripts(List):
	param_classes = [EventScriptPointer]
	count = 0x20 / 4
	address = 0x14b6ec

class gUnknown_0814B14C(List):
	param_classes = [Pointer]
	count = 0x48 / 4
	address = 0x14b14c

class UnreferencedMap1(MapAttributes):
	group = -1
	num = -1
	address = 0x2bf1e4

class UnreferencedMap2(MapAttributes):
	group = -1
	num = -1
	address = 0x2cf540 + 24

class MoveEffect(BattleScript):
	pass

class MoveEffectPointer(BattleScriptPointer):
	target = MoveEffect

class MoveEffects(List):
	param_classes = [MoveEffectPointer]
	count = 214
	address = 0x1d6bbc
	def parse(self):
		List.parse(self)
		for i, chunk in enumerate(self.chunks):
			constant = self.version.get('move_effect_constants', {}).get(i)
			if constant:
				label_name = 'MoveEffect_' + constant.title().replace('_', '')
				label = Label(chunk.real_address)
				label.asm = label_name
				chunk.chunks += [label]
				chunk.label = label

class gUnknown_081FAC4C(List):
	param_classes = [BattleScriptPointer]
	count = 39
	address = 0x1fac4c

class gUnknown_08401508(BattleTextList):
	count = 10
	address = 0x401508

class gUnknown_081D9E48(List):
	param_classes = [BattleScriptPointer]
	count = 24
	address = 0x1d9e48

bad_labels = [
	'gUnknown_081D8E4A', 'gUnknown_081D8E37', 'gUnknown_081D8E44', 'gUnknown_081D94DA', 'gUnknown_081D8E02', 'gUnknown_081D8E0D', 'gUnknown_081D8DBE', 'gUnknown_081D8DCE', 'gUnknown_081D8E02', 'gUnknown_081D8DD1', 'gUnknown_081D8E29', 'gUnknown_081D8E14', 'gUnknown_081D8E22', 'gUnknown_081D8E30', 'gUnknown_081D8E4E', 'gUnknown_081D8E3B', 'gUnknown_081D8E3B', 'gUnknown_081D9144', 'gUnknown_081D937C', 'gUnknown_081D938B', 'gUnknown_081D9464', 'gUnknown_081D9369', 'gUnknown_081D9365', 'gUnknown_081D9030', 'gUnknown_081D9030', 'gUnknown_081D9030', 'gUnknown_081D9041', 'gUnknown_081D939A', 'gUnknown_081D8F62', 'gUnknown_081D8FFF', 'gUnknown_081D8F7D', 'gUnknown_081D9016', 'gUnknown_081D9008', 'gUnknown_081D8FFF', 'gUnknown_081D8F7D', 'gUnknown_081D93D1', 'gUnknown_081D904B', 'gUnknown_081D9518', 'gUnknown_081D9518', 'gUnknown_081D953A', 'gUnknown_081D9613', 'gUnknown_081D9624', 'gUnknown_081D95E2', 'gUnknown_081D95F4', 'gUnknown_081D950F', 'gUnknown_081D957E', 'gUnknown_081D9587', 'gUnknown_081D9148', 'gUnknown_081D914F', 'gUnknown_081D964C', 'gUnknown_081D92D7', 'gUnknown_081D9202', 'gUnknown_081D921D', 'gUnknown_081D8C72', 'gUnknown_081D8C7B', 'gUnknown_081D94FB', 'gUnknown_081D94EE', 'gUnknown_081D94FB', 'gUnknown_081D9545', 'gUnknown_081D9552', 'gUnknown_081D7956', 'gUnknown_081D9573', 'gUnknown_081D9139', 'gUnknown_081D938F', 'gUnknown_081D9459', 'gUnknown_081D9595', 'gUnknown_081D95D4', 'gUnknown_081D9566', 'gUnknown_081D9608', 'gUnknown_081D95FB', 'gUnknown_081D90A7', 'gUnknown_081D90B2', 'gUnknown_081D90F1', 'gUnknown_081D9552', 'gUnknown_081D901D', 'gUnknown_081D9704', 'gUnknown_081D9744', 'gUnknown_081D97FE', 'gUnknown_081D977D', 'gUnknown_081D9730', 'gUnknown_081D9758', 'gUnknown_081D9718', 'gUnknown_081D9843', 'gUnknown_081D9842', 'gUnknown_081D9843', 'gUnknown_081D9842', 'gUnknown_081D987C', 'gUnknown_081D987B', 'gUnknown_081D987C', 'gUnknown_081D987B', 'gUnknown_081D9866', 'gUnknown_081D9865', 'gUnknown_081D977D', 'gUnknown_081D977D', 'gUnknown_081D978C', 'gUnknown_081D9726', 'gUnknown_081D9795', 'gUnknown_081D6F62', 'gUnknown_081D936D', 'gUnknown_081D946F', 'gUnknown_081D9812', 'gUnknown_081D9487', 'gUnknown_081D8EEF', 'gUnknown_081D8EEF', 'gUnknown_081D94A9', 'gUnknown_081D94A2', 'gUnknown_081D98BD', 'gUnknown_081D98A5', 'gUnknown_081D98A5', 'gUnknown_081D98B1', 'gUnknown_081D98BD', 'gUnknown_081D98BD', 'gUnknown_081D98D7', 'gUnknown_081D71E5', 'gUnknown_081D7276', 'gUnknown_081D71E5', 'gUnknown_081D7276', 'gUnknown_081D96F6', 'gUnknown_081D9224', 'gUnknown_081D92C0', 'gUnknown_081D9635', 'gUnknown_081D93FA', 'gUnknown_081D944B', 'gUnknown_081D94B0', 'gUnknown_081D8C58', 'gUnknown_081D8C65', 'gUnknown_081D9156', 'gUnknown_081D9468', 'gUnknown_081D8EF3', 'gUnknown_081D8EEF', 'gUnknown_081D9132', 'gUnknown_081D955D', 'gUnknown_081D919F', 'gUnknown_081D9171', 'gUnknown_081D91CD', 'gUnknown_081D9834', 'gUnknown_081D9128', 'gUnknown_081D83D6', 'gUnknown_081D989B', 'gUnknown_081D90FC', 'gUnknown_081D95DB', 'gUnknown_081D9826', 'gUnknown_081D98C9', 'gUnknown_081D6F74', 'gUnknown_081D6F74', 'gUnknown_081D6F44', 'gUnknown_081D83B5', 'gUnknown_081D839B', 'gUnknown_081D92C2', 'gUnknown_081D92C9', 'gUnknown_081D92D0',
]

def insert_labels(labels):
	version = get_setup_version('ruby')
	chunks = []
	for label in labels:
		address = int(label[-6:], 16)
		chunks += [Label(address, asm=label, is_global=True, version=version)]
	for path in version['maps_paths']:
		insert_chunks(chunks, path, version)


if __name__ == '__main__':
    args = get_args(
        'classname',
        'address',
	('version', {'nargs':'?', 'default':'ruby'}),
	('-i', {'dest': 'insert', 'action': 'store_true'}),
    )
    class_ = globals()[args.classname]
    address = int(args.address, 16)
    version = args.version

    if args.insert:
        insert_recursive(class_, address, version)
    else:
        print print_recursive(class_, address, version)
