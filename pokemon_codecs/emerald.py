# coding: utf-8

"""Charmap codec for Pokémon Emerald.
"""

import codecs

class Codec(codecs.Codec):

	error_chars = {
		'strict': None,
		'ignore': u'',
		'replace': u'?',
	}

	def decode(self, input, errors='replace'):
		default_char = self.error_chars.get(errors)
		old = bytearray(input)
		new = u''
		i = 0
		len_old = len(old)
		while i < len_old:
			char = old[i]
			if char == 0xfd:
				i += 1
				new += emerald_decode[0xfd].get(old[i], default_char)
			else:
				new += emerald_decode.get(char, default_char)
			i += 1
		return new, i

	def encode(self, input, errors='replace'):
		default_char = self.error_chars.get(errors)
		old = input
		new = ''
		i = 0
		len_old = len(old)
		while i < len_old:
			char = old[i]
			if char == '{':
				j = i + old.find('}', i) + 1
				new += emerald_encode.get(old[i:j], default_char)
				i = j
			else:
				new += emerald_encode.get(char, default_char)
				i += 1
		return new, i

class IncrementalEncoder(codecs.IncrementalEncoder):
	def encode(self, input, final=False):
		return Codec().encode(input, self.errors)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
	def decode(self, input, final=False):
		return Codec().decode(input, self.errors)[0]

class StreamWriter(Codec, codecs.StreamWriter):
	pass

class StreamReader(Codec, codecs.StreamReader):
	pass

def getregentry():
	return codecs.CodecInfo(
		name='emerald',
		encode=Codec().encode,
		decode=Codec().decode,
		incrementalencoder=IncrementalEncoder,
		incrementaldecoder=IncrementalDecoder,
		streamreader=StreamReader,
		streamwriter=StreamWriter,
	)

def search(search_name):
	if search_name == 'emerald':
		return getregentry()
	return None

codecs.register(search)

emerald_decode = {
	0x00: u' ',
	0x01: u'À',
	0x02: u'Á',
	0x03: u'Â',
	0x04: u'Ç',
	0x05: u'È',
	0x06: u'É',
	0x07: u'Ê',
	0x08: u'Ë',
	0x09: u'Ì',
	0x0A: u'{0A}', # None
	0x0B: u'Î',
	0x0C: u'Ï',
	0x0D: u'Ò',
	0x0E: u'Ó',
	0x0F: u'Ô',
	0x10: u'Œ',
	0x11: u'Ù',
	0x12: u'Ú',
	0x13: u'Û',
	0x14: u'Ñ',
	0x15: u'ß',
	0x16: u'à',
	0x17: u'á',
	0x18: u'{18}', # None
	0x19: u'ç',
	0x1A: u'è',
	0x1B: u'é',
	0x1C: u'ê',
	0x1D: u'ë',
	0x1E: u'ì',
	0x1F: u'{1F}', # None
	0x20: u'î',
	0x21: u'ï',
	0x22: u'ò',
	0x23: u'ó',
	0x24: u'ô',
	0x25: u'œ',
	0x26: u'ù',
	0x27: u'ú',
	0x28: u'û',
	0x29: u'ñ',
	0x2A: u'º',
	0x2B: u'ª',
	0x2C: u'¹',
	0x2D: u'&',
	0x2E: u'+',
	0x2F: u'{2F}', # None
	0x30: u'{30}', # None
	0x31: u'{31}', # None
	0x32: u'{32}', # None
	0x33: u'{33}', # None
	0x34: u'{34}', # None # '[Lv]'
	0x35: u'=',
	0x36: u';',
	0x37: u'{37}', # None
	0x38: u'{38}', # None
	0x39: u'{39}', # None
	0x3A: u'{3A}', # None
	0x3B: u'{3B}', # None
	0x3C: u'{3C}', # None
	0x3D: u'{3D}', # None
	0x3E: u'{3E}', # None
	0x3F: u'{3F}', # None
	0x40: u'{40}', # None
	0x41: u'{41}', # None
	0x42: u'{42}', # None
	0x43: u'{43}', # None
	0x44: u'{44}', # None
	0x45: u'{45}', # None
	0x46: u'{46}', # None
	0x47: u'{47}', # None
	0x48: u'{48}', # None
	0x49: u'{49}', # None
	0x4A: u'{4A}', # None
	0x4B: u'{4B}', # None
	0x4C: u'{4C}', # None
	0x4D: u'{4D}', # None
	0x4E: u'{4E}', # None
	0x4F: u'{4F}', # None
	0x50: u'{50}', # None
	0x51: u'¿',
	0x52: u'¡',
	0x53: u'{PK}',
	0x54: u'{MN}',
	0x55: u'{PO}',
	0x56: u'{Ké}',
	0x57: u'{BL}',
	0x58: u'{OC}',
	0x59: u'{K}',
	0x5A: u'Í',
	0x5B: u'%',
	0x5C: u'(',
	0x5D: u')',
	0x5E: u'{5E}', # None
	0x5F: u'{5F}', # None
	0x60: u'{60}', # None
	0x61: u'{61}', # None
	0x62: u'{62}', # None
	0x63: u'{63}', # None
	0x64: u'{64}', # None
	0x65: u'{65}', # None
	0x66: u'{66}', # None
	0x67: u'{67}', # None
	0x68: u'â',
	0x69: u'{69}', # None
	0x6A: u'{6A}', # None
	0x6B: u'{6B}', # None
	0x6C: u'{6C}', # None
	0x6D: u'{6D}', # None
	0x6E: u'{6E}', # None
	0x6F: u'í',
	0x70: u'{70}', # None
	0x71: u'{71}', # None
	0x72: u'{72}', # None
	0x73: u'{73}', # None
	0x74: u'{74}', # None
	0x75: u'{75}', # None
	0x76: u'{76}', # None
	0x77: u'{77}', # None
	0x78: u'{78}', # None
	0x79: u'{79}', # None
	0x7A: u'{7A}', # None
	0x7B: u'{7B}', # None
	0x7C: u'{7C}', # None
	0x7D: u'{7D}', # None
	0x7E: u'{7E}', # None
	0x7F: u'{7F}',
	0x80: u'{80}', # None
	0x81: u'{81}', # None
	0x82: u'{82}', # None
	0x83: u'{83}', # None
	0x84: u'{84}', # None
	0x85: u'{85}', # None
	0x86: u'{86}', # None
	0x87: u'{87}', # None
	0x88: u'{88}', # None
	0x89: u'{89}', # None
	0x8A: u'{8A}', # None
	0x8B: u'{8B}', # None
	0x8C: u'{8C}', # None
	0x8D: u'{8D}', # None
	0x8E: u'{8E}', # None
	0x8F: u'{8F}', # None
	0x90: u'{90}', # None
	0x91: u'{91}', # None
	0x92: u'{92}', # None
	0x93: u'{93}', # None
	0x94: u'{94}', # None
	0x95: u'{95}', # None
	0x96: u'{96}', # None
	0x97: u'{97}', # None
	0x98: u'{98}', # None
	0x99: u'{99}', # None
	0x9A: u'{9A}', # None
	0x9B: u'{9B}', # None
	0x9C: u'{9C}', # None
	0x9D: u'{9D}', # None
	0x9E: u'{9E}', # None
	0x9F: u'{9F}', # None
	0xA0: u'{A0}', # None
	0xA1: u'0',
	0xA2: u'1',
	0xA3: u'2',
	0xA4: u'3',
	0xA5: u'4',
	0xA6: u'5',
	0xA7: u'6',
	0xA8: u'7',
	0xA9: u'8',
	0xAA: u'9',
	0xAB: u'!',
	0xAC: u'?',
	0xAD: u'.',
	0xAE: u'-',
	0xAF: u'|',
	0xB0: u'…',
	0xB1: u'“',
	0xB2: u'”',
	0xB3: u'‘',
	0xB4: u"'",#u'’',
	0xB5: u'♂',
	0xB6: u'♀',
	0xB7: u'¥',
	0xB8: u',',
	0xB9: u'×',
	0xBA: u'/',
	0xBB: u'A',
	0xBC: u'B',
	0xBD: u'C',
	0xBE: u'D',
	0xBF: u'E',
	0xC0: u'F',
	0xC1: u'G',
	0xC2: u'H',
	0xC3: u'I',
	0xC4: u'J',
	0xC5: u'K',
	0xC6: u'L',
	0xC7: u'M',
	0xC8: u'N',
	0xC9: u'O',
	0xCA: u'P',
	0xCB: u'Q',
	0xCC: u'R',
	0xCD: u'S',
	0xCE: u'T',
	0xCF: u'U',
	0xD0: u'V',
	0xD1: u'W',
	0xD2: u'X',
	0xD3: u'Y',
	0xD4: u'Z',
	0xD5: u'a',
	0xD6: u'b',
	0xD7: u'c',
	0xD8: u'd',
	0xD9: u'e',
	0xDA: u'f',
	0xDB: u'g',
	0xDC: u'h',
	0xDD: u'i',
	0xDE: u'j',
	0xDF: u'k',
	0xE0: u'l',
	0xE1: u'm',
	0xE2: u'n',
	0xE3: u'o',
	0xE4: u'p',
	0xE5: u'q',
	0xE6: u'r',
	0xE7: u's',
	0xE8: u't',
	0xE9: u'u',
	0xEA: u'v',
	0xEB: u'w',
	0xEC: u'x',
	0xED: u'y',
	0xEE: u'z',
	0xEF: u'{EF}', # None
	0xF0: u':',
	0xF1: u'Ä',
	0xF2: u'Ö',
	0xF3: u'Ü',
	0xF4: u'ä',
	0xF5: u'ö',
	0xF6: u'ü',
	0xF7: u'{F7}', # None
	0xF8: u'{F8}', # None
	0xF9: u'{F9}', # None
	0xFA: u'{FA}', # None
	0xFB: u'+',
	0xFC: u'{FC}', # None
	0xFD: {
		1: u'{PLAYER}',
		2: u'{STRVAR_1}',
		3: u'{STRVAR_2}',
		4: u'{STRVAR_3}',
		6: u'{RIVAL}',
		7: u'{VERSION}',
		8: u'{AQUA}',
		9: u'{MAGMA}',
		10: u'{ARCHIE}',
		11: u'{MAXIE}',
		12: u'{KYOGRE}',
		13: u'{GROUDON}',
	},
	0xFE: u'\n',
	0xFF: u'$',
}

emerald_encode = {}
for k, v in emerald_decode.items():
	if type(v) is dict:
		for k2, v2 in v.items():
			emerald_encode[v2] = chr(k) + chr(k2)
	else:
		emerald_encode[v] = chr(k)
