import sys
import pprint

class Cept_page:
	x = None
	y = None
	lines_cept = []
	data_cept = None
	italics = False
	bold = False
	link = False
	dirty = False
	title_image_width = 0
	title_image_height = 0
	lines_per_page = 17

	def __init__(self):
		self.x = 0
		self.y = -1
		self.init_new_line()

	def init_new_line(self):
		self.data_cept = bytearray()
		self.data_cept.extend(Cept.clear_line())
#		sys.stderr.write("self.y: '" + pprint.pformat(self.y) + "'\n")
#		sys.stderr.write("self.y % lines_per_page: '" + pprint.pformat(self.y % lines_per_page) + "'\n")
		self.x = 0
		self.y += 1

		if (self.y % self.lines_per_page) == 0:
			self.resend_attributes()

#		s = str(self.y) + " "
#		self.data_cept.extend(Cept.from_str(s))
#		self.x += len(s)

	def print_newline(self):
		if self.x == 0 and self.y % self.lines_per_page == 0:
			# no empty first lines
			return
		self.data_cept.extend(Cept.repeat(" ", 40 - self.x))
		self.create_new_line()

	def resend_attributes(self):
#		sys.stderr.write("self.italics: " + pprint.pformat(["self.italics: ",self.italics , self.bold , self.link]) + "\n")
		if self.italics:
			self.data_cept.extend(Cept.set_fg_color(6))
		elif self.bold:
			self.data_cept.extend(Cept.set_fg_color(0))
		if self.link:
			self.data_cept.extend(Cept.underline_on())
			self.data_cept.extend(Cept.set_fg_color(4))
		if not self.italics and not self.bold and not self.link:
			self.data_cept.extend(Cept.set_fg_color(15))
			self.data_cept.extend(Cept.underline_off())
		self.dirty = False

	def add_string(self, s):
		if self.dirty:
			self.resend_attributes()
		self.data_cept.extend(Cept.from_str(s))
#		sys.stderr.write("before self.x: " + pprint.pformat(self.x) + "\n")
#		sys.stderr.write("adding: '" + pprint.pformat(s) + "'\n")
#		sys.stderr.write("self.data_cept: " + pprint.pformat(self.data_cept) + "\n")

	# API
	def create_new_line(self):
		self.lines_cept.append(self.data_cept)
		self.init_new_line()

	# API
	def set_italics_on(self):
		self.italics = True
		self.dirty = True

	# API
	def set_italics_off(self):
		self.italics = False
		self.dirty = True

	# API
	def set_bold_on(self):
		self.bold = True
		self.dirty = True

	# API
	def set_bold_off(self):
		self.bold = False
		self.dirty = True

	# API
	def set_link_on(self):
		self.link = True
		self.dirty = True

	# API
	def set_link_off(self):
		self.link = False
		self.dirty = True

	# API
	def print(self, s):
		if s == "":
			return

		components = s.split("\n")
		if len(components) > 1:
			for s in components:
				self.print(s)
				self.print_newline()

#		sys.stderr.write("s: " + pprint.pformat(s) + "\n")
		while s:
			index = s.find(" ")
			if index < 0:
				index = len(s)
				ends_in_space = False
			else:
				ends_in_space = True

			if self.y < self.title_image_height:
				line_width = 40 - self.title_image_width
			else:
				line_width = 40

#			sys.stderr.write("decide self.x: " + pprint.pformat(self.x) + "\n")
#			sys.stderr.write("decide index: " + pprint.pformat(index) + "\n")
			if index == 0 and self.x == 0:
#				sys.stderr.write("A\n")
				# starts with space and we're at the start of a line
				# -> skip space
				pass
			elif index + self.x > line_width:
#				sys.stderr.write("B\n")
				# word doesn't fit, print it (plus the space)
				# into a new line
				if self.link:
					self.data_cept.extend(Cept.underline_off())
				self.data_cept.extend(Cept.repeat(" ", 40 - self.x))
				if self.link:
					self.data_cept.extend(Cept.underline_on())
				self.create_new_line()
				self.add_string(s[:index + 1])
				self.x += index
				if ends_in_space:
					self.x += 1
			elif ends_in_space and index + self.x + 1 == 40:
#				sys.stderr.write("C\n")
				# space in last column
				# -> just print it, cursor will be in new line
				self.add_string(s[:index + 1])
				self.create_new_line()
			elif not ends_in_space and index + self.x == 40:
#				sys.stderr.write("D\n")
				# character in last column, not followed by a space
				# -> just print it, cursor will be in new line
				self.add_string(s[:index])
				self.create_new_line()
			elif ends_in_space and index + self.x == 40:
#				sys.stderr.write("E\n")
				# character in last column, followed by space
				# -> omit the space, cursor will be in new line
				self.add_string(s[:index])
				self.create_new_line()
			else:
#				sys.stderr.write("F\n")
				self.add_string(s[:index + 1])
				self.x += len(s[:index + 1])
				if self.x == 40:
					self.create_new_line()
			s = s[index + 1:]

	# API
	def print_heading(self, level, s):
		if level == 2:
			if (self.y + 1) % self.lines_per_page == 0 or (self.y + 2) % self.lines_per_page == 0:
				# don't draw double height title into
				# the last line or the one above
				self.data_cept.extend(b'\n')
				self.create_new_line()
			self.data_cept.extend(Cept.underline_off())
			self.data_cept.extend(Cept.clear_line())
			self.data_cept.extend(b'\n')
			self.data_cept.extend(Cept.clear_line())
			self.data_cept.extend(Cept.set_fg_color(0))
			self.data_cept.extend(Cept.double_height())
			self.data_cept.extend(Cept.from_str(s[:39]))
			self.data_cept.extend(b'\r\n')
			self.data_cept.extend(Cept.normal_size())
			self.data_cept.extend(Cept.set_fg_color(15))
			self.create_new_line()
			self.create_new_line()
		else:
			if (self.y + 1) % self.lines_per_page == 0:
				# don't draw title into the last line
				self.data_cept.extend(b'\n')
				self.create_new_line()
			self.data_cept.extend(Cept.underline_on())
			self.data_cept.extend(Cept.set_fg_color(0))
			self.data_cept.extend(Cept.from_str(s[:39]))
			self.data_cept.extend(Cept.underline_off())
			self.data_cept.extend(Cept.set_fg_color(15))
			self.data_cept.extend(b'\r\n')
			self.create_new_line()
		return


class Cept(bytearray):

	# private
	def g2code(c, mode):
		if mode == 0:
			return b'\x19' + bytearray([ord(c)])
		else:
			return bytearray([ord(c) + 0x80])
	
	def from_str(s1, mode = 0):
		s2 = bytearray()
		for c in s1:
			# TODO: complete conversion!
			if ord(c) == 0xe4:
				s2.extend(Cept.g2code('H', mode) + b'a') # ä
			elif ord(c) == 0xf6:
				s2.extend(Cept.g2code('H', mode) + b'o') # ö
			elif ord(c) == 0xfc:
				s2.extend(Cept.g2code('H', mode) + b'u') # ü
			elif ord(c) == 0xc4:
				s2.extend(Cept.g2code('H', mode) + b'A') # Ä
			elif ord(c) == 0xd6:
				s2.extend(Cept.g2code('H', mode) + b'O') # Ö
			elif ord(c) == 0xdc:
				s2.extend(Cept.g2code('H', mode) + b'U') # Ü
			elif ord(c) == 0xdf:
				s2.extend(Cept.g2code('{', mode))        # ß
			elif ord(c) == 0x0a:
				s2.extend(b'\r\n')                       # \n
			elif ord(c) == 0x201e:
				s2.extend(b'"')
			elif ord(c) == 0x201c:
				s2.extend(b'"')
			elif ord(c) == 0x2018:
				s2.extend(b'"')
			elif ord(c) == 0x201a:
				s2.extend(b'"')
			elif ord(c) < 256:
				s2.append(ord(c))
			else:
				s2.append(ord('?')) # non-Latin-1
		return s2

	def code_to_str(s1):
		# returns a unicode string of the single-char CEPT sequence
		# - there's is nothing we could decode in the string
		# - None: the sequence is incomplete
		if not s1:
			return ""
		if len(s1) == 1 and s1[0] <= 0x7f and s1[0] != 0x19:
			return s1.decode("utf-8") # CEPT == ASCII for 0x00-0x7F (except 0x19)
		if s1[0] == 0x19:
			if len(s1) == 1:
				return None
#			sys.stderr.write("s1[1]: " + pprint.pformat(s1[1]) + "\n")
#			sys.stderr.write("len(s1): " + pprint.pformat(len(s1)) + "\n")
			if s1[1] == ord('H'): # "¨" prefix
				if len(s1) == 2: # not complete
					return None
				else:
					if s1[2] == ord('a'):
						return "ä"
					elif s1[2] == ord('o'):
						return "ö"
					elif s1[2] == ord('u'):
						return "ü"
					elif s1[2] == ord('A'):
						return "Ä"
					elif s1[2] == ord('O'):
						return "Ö"
					elif s1[2] == ord('U'):
						return "Ü"
					else:
						return ""
			elif s1[1] == ord('{'): # &szlig
				return "ß"
			else:
				return ""
		return ""

	def compress(s1):
		s2 = bytearray()
		i = 0
		while True:
			c = s1[i]
			if c >= 0x20:
				s1rest = s1[i + 1:]
				l = 1
				for j in range(0, len(s1rest)):
					if s1rest[j] != c:
						break
					l += 1
			else:
				l = 1
			if l > 3:
				if l > 63:
					l = 63
				s2.extend(bytes([c, 0x12, 0x40 + l - 1]))
				i += l
			else:
				s2.append(c)
				i += 1
			if i == len(s1):
				break
		sys.stderr.write("compressed " + str(len(s1)) + " down to " + str(len(s2)) + "\n")
		return s2

	def from_aa(aa, indent = 0):
		dict = { "": 0x20, "1": 0x21, "2": 0x22, "12": 0x23, "3": 0x24, "13": 0x25, "23": 0x26, "123": 0x27, "4": 0x28, "14": 0x29, "24": 0x2a, "124": 0x2b, "34": 0x2c, "134": 0x2d, "234": 0x2e, "1234": 0x2f, "5": 0x30, "15": 0x31, "25": 0x32, "125": 0x33, "35": 0x34, "135": 0x35, "235": 0x36, "1235": 0x37, "45": 0x38, "145": 0x39, "245": 0x3a, "1245": 0x3b, "345": 0x3c, "1345": 0x3d, "2345": 0x3e, "12345": 0x3f, "123456": 0x5f, "6": 0x60, "16": 0x61, "26": 0x62, "126": 0x63, "36": 0x64, "136": 0x65, "236": 0x66, "1236": 0x67, "46": 0x68, "146": 0x69, "246": 0x6a, "1246": 0x6b, "346": 0x6c, "1346": 0x6d, "2346": 0x6e, "12346": 0x6f, "56": 0x70, "156": 0x71, "256": 0x72, "1256": 0x73, "356": 0x74, "1356": 0x75, "2356": 0x76, "12356": 0x77, "456": 0x78, "1456": 0x79, "2456": 0x7a, "12456": 0x7b, "3456": 0x7c, "13456": 0x7d, "23456": 0x7e }
		while len(aa) % 3 != 0:
			aa.append(" " * len(aa[0]))
		if indent < 4:
			for i in range(0, indent):
				indent_cept = b'\x20'
		else:
			indent_cept = bytes([0x20, 0x12, 0x40 + indent - 1])

		data_cept = bytearray()
		data_cept.extend(b'\x0e')                      # G1 into left charset
		for y in range(0, len(aa), 3):
			data_cept.extend(indent_cept)
			for x in range(0, len(aa[0]), 2):
				s = ""
				next_column_exists = x+1 < len(aa[y])
				if aa[y][x] != " ":
					s += "1"
				if next_column_exists and aa[y][x+1] != " ":
					s += "2"
				if aa[y+1][x] != " ":
					s += "3"
				if next_column_exists and aa[y+1][x+1] != " ":
					s += "4"
				if aa[y+2][x] != " ":
					s += "5"
				if next_column_exists and aa[y+2][x+1] != " ":
					s += "6"
				data_cept.append(dict[s])
			data_cept.extend(b'\r\n')
		data_cept.extend(b'\x0f')                       # G0 into left charset
		return Cept.compress(data_cept)

	# CEPT sequences	

	@staticmethod
	def sequence_end_of_page():
		return (
			b'\x1f\x58\x41'		 # set cursor to line 24, column 1
			b'\x11'				 # show cursor
			b'\x1a'				 # end of page
		)
	

	# CEPT codes
	
	@staticmethod
	def ini():
		return 0x13

	@staticmethod
	def ter():
		return 0x1c

	@staticmethod
	def dct():
		return 0x1a

	@staticmethod
	def set_res_40_24():
		return b'\x1f\x2d'

	@staticmethod
	def show_cursor():
		return b'\x11'

	@staticmethod
	def hide_cursor():
		return b'\x14'

	@staticmethod
	def cursor_home():
		return b'\x1e'

	@staticmethod
	def cursor_left():
		return b'\x08'

	@staticmethod
	def cursor_right():
		return b'\x09'

	@staticmethod
	def cursor_down():
		return b'\x0a'

	@staticmethod
	def cursor_up():
		return b'\x0b'

	@staticmethod
	def set_cursor(y, x):
		return bytes([0x1f, 0x40 + y, 0x40 + x])

	@staticmethod
	def clear_screen():
		return b'\x0c'

	@staticmethod
	def clear_line():
		return b'\x18'

	@staticmethod
	def protect_line():
		return b'\x9b\x31\x50'

	@staticmethod
	def unprotect_line():
		return b'\x9b\x31\x51'

	@staticmethod
	def parallel_mode():
		return b'\x1b\x22\x41'
		
	@staticmethod
	def serial_limited_mode():
		return b'\x1f\x2f\x43'
		
	@staticmethod
	def parallel_limited_mode():
		return b'\x1f\x2f\x44'

	@staticmethod
	def repeat(c, n):
		return bytes([ord(c), 0x12, 0x40 + n - 1])

	@staticmethod
	def define_palette(palette, start_color = 16):
		cept = bytearray(
			b'\x1f\x26\x20'			  # start defining colors
			b'\x1f\x26'		          # define colors
		)
		cept.append(0x30 + int(start_color / 10))
		cept.append(0x30 + int(start_color % 10))
	
		for hexcolor in palette:
			if len(hexcolor) == 7:
				r = int(hexcolor[1:3], 16)
				g = int(hexcolor[3:5], 16)
				b = int(hexcolor[5:7], 16)
			elif len(hexcolor) == 4:
				r = int(hexcolor[1:2], 16) << 4
				g = int(hexcolor[2:3], 16) << 4
				b = int(hexcolor[3:4], 16) << 4
			else:
				sys.stderr.write("incorrect palette encoding.\n")
			r0 = (r >> 4) & 1
			r1 = (r >> 5) & 1
			r2 = (r >> 6) & 1
			r3 = (r >> 7) & 1
			g0 = (g >> 4) & 1
			g1 = (g >> 5) & 1
			g2 = (g >> 6) & 1
			g3 = (g >> 7) & 1
			b0 = (b >> 4) & 1
			b1 = (b >> 5) & 1
			b2 = (b >> 6) & 1
			b3 = (b >> 7) & 1
			byte0 = 0x40 | r3 << 5 | g3 << 4 | b3 << 3 | r2 << 2 | g2 << 1 | b2
			byte1 = 0x40 | r1 << 5 | g1 << 4 | b1 << 3 | r0 << 2 | g0 << 1 | b0
			cept.append(byte0)
			cept.append(byte1)
		return cept

	
	@staticmethod
	def set_palette(pal):
		return bytes([0x9b, 0x30 + pal, 0x40])

	@staticmethod
	def set_fg_color_simple(c):
		return bytes([0x80 + c])

	@staticmethod
	def set_bg_color_simple(c):
		return bytes([0x90 + c])

	@staticmethod
	def set_fg_color(c):
		return Cept.set_palette(c >> 3) + Cept.set_fg_color_simple(c & 7)

	@staticmethod
	def set_bg_color(c):
		return Cept.set_palette(c >> 3) + Cept.set_bg_color_simple(c & 7)

	@staticmethod
	def set_line_bg_color_simple(c):
		return bytes([0x1b, 0x23, 0x21, 0x50 + c])

	@staticmethod
	def set_line_bg_color(c):
		return Cept.set_palette(c >> 3) + Cept.set_line_bg_color_simple(c & 7)

	@staticmethod
	def set_screen_bg_color_simple(c):
		return bytes([0x1b, 0x23, 0x20, 0x50 + c])

	@staticmethod
	def set_screen_bg_color(c):
		return Cept.set_palette(c >> 3) + Cept.set_screen_bg_color_simple(c & 7)

	@staticmethod
	def set_line_fg_color_simple(c):
		return bytes([0x1b, 0x23, 0x21, 0x40 + c])

	@staticmethod
	def set_left_g0():
		return b'\x0f'

	@staticmethod
	def set_left_g3():
		return b'\x1b\x6f'

	@staticmethod
	def load_g0_drcs():
		return b'\x1b\x28\x20\x40'

	@staticmethod
	def load_g0_g0():
		return b'\x1b\x28\x40'

	@staticmethod
	def service_break(y):
		return bytes([0x1f, 0x2f, 0x40, 0x40 + y])
	
	@staticmethod
	def service_break_back():
		return b'\x1f\x2f\x4f'
	
	@staticmethod
	def normal_size():
		return b'\x8c'

	@staticmethod
	def double_height():
		return b'\x8d'

	@staticmethod
	def double_width():
		return b'\x8e'

	@staticmethod
	def double_size():
		return b'\x8f'

	@staticmethod
	def underline_off():
		return b'\x99'

	@staticmethod
	def underline_on():
		return b'\x9a'

	@staticmethod
	def hide_text():
		return b'\x98'
		
	@staticmethod
	def code_9d():
		return b'\x9d'
		
	@staticmethod
	def code_9e():
		return b'\x9e'
		
		