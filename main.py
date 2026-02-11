#!/usr/bin/env python3
import random
import sys
import argparse
import textwrap
import time


def slowprint(s, delay=0.01):
	for c in s:
		sys.stdout.write(c)
		sys.stdout.flush()
		time.sleep(delay)
	print()


ASCII = {
	"player": "☺",
	"npc": "(^_^)",
	"ghost": "(~_~)",
	"exit": "[EXIT]",
	"treasure": "✨🎁✨",
}


class Room:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.character = None

	def coords(self):
		return (self.x, self.y)


class Character:
	def __init__(self, name, kind, message=None):
		self.name = name
		self.kind = kind  # 'npc' or 'ghost'
		self.message = message or ""

	def icon(self):
		return ASCII['npc'] if self.kind == 'npc' else ASCII['ghost']


class Game:
	DIRS = {
		'utara': (0, -1), 'u': (0, -1), 'n': (0, -1),
		'selatan': (0, 1), 's': (0, 1),
		'barat': (-1, 0), 'b': (-1, 0), 'w': (-1, 0),
		'timur': (1, 0), 't': (1, 0), 'e': (1, 0),
	}

	def __init__(self, size=3):
		self.size = size
		self.map = [[Room(x, y) for x in range(size)] for y in range(size)]
		self.player_x = size // 2
		self.player_y = size // 2
		self.health = 5
		self.exit = self.place_exit()
		self.place_characters()
		self.turn = 0

	def place_exit(self):
		s = self.size
		perimeter = []
		for y in range(s):
			for x in range(s):
				if x == 0 or y == 0 or x == s - 1 or y == s - 1:
					perimeter.append((x, y))
		start = (self.player_x, self.player_y)
		choices = [c for c in perimeter if c != start]
		return random.choice(choices)

	def place_characters(self):
		s = self.size
		positions = [(x, y) for y in range(s) for x in range(s)]
		positions.remove((self.player_x, self.player_y))
		if self.exit in positions:
			positions.remove(self.exit)
		random.shuffle(positions)

		npc_names = ['Pak Joko', 'Mbak Sari', 'Kakek Tua']
		ghost_names = ['Hantu Kecil', 'Bayangan']

		for name in npc_names:
			if not positions:
				break
			x, y = positions.pop()
			dir_hint = self.direction_hint((x, y), self.exit)
			msg = f"Petunjuk: arah keluar kira-kira ke {dir_hint}."
			self.map[y][x].character = Character(name, 'npc', msg)

		for name in ghost_names:
			if not positions:
				break
			x, y = positions.pop()
			msg = "Sebuah hawa dingin menyentuhmu..."
			self.map[y][x].character = Character(name, 'ghost', msg)

	def direction_hint(self, from_pos, to_pos):
		fx, fy = from_pos
		tx, ty = to_pos
		dx = tx - fx
		dy = ty - fy
		parts = []
		if dy < 0:
			parts.append('utara')
		elif dy > 0:
			parts.append('selatan')
		if dx < 0:
			parts.append('barat')
		elif dx > 0:
			parts.append('timur')
		return ' '.join(parts) or 'di sekitar sini'

	def in_bounds(self, x, y):
		return 0 <= x < self.size and 0 <= y < self.size

	def current_room(self):
		return self.map[self.player_y][self.player_x]

	def move(self, direction):
		direction = direction.lower()
		if direction not in self.DIRS:
			return "Arah tidak dikenal. Gunakan 'utara/selatan/timur/barat' atau n/s/e/w."
		dx, dy = self.DIRS[direction]
		nx = self.player_x + dx
		ny = self.player_y + dy
		if not self.in_bounds(nx, ny):
			return "Tidak bisa bergerak ke sana (batas ruangan)."
		self.player_x, self.player_y = nx, ny
		self.turn += 1
		return self.describe_current()

	def describe_current(self):
		room = self.current_room()
		out = []
		out.append(f"Kamu berada di posisi ({room.x},{room.y}).")
		if (room.x, room.y) == self.exit:
			out.append("Kamu melihat sebuah pintu keluar!")
		if room.character:
			ch = room.character
			if ch.kind == 'npc':
				out.append(f"{ch.icon()} Kamu bertemu {ch.name}. {ch.message}")
			else:
				out.append(f"{ch.icon()} {ch.name} muncul! {ch.message}")
				dmg = random.randint(1, 3)
				self.health -= dmg
				out.append(f"{ch.name} mengurangi nyawamu sebanyak {dmg}. Nyawa: {self.health}")
		return '\n'.join(out)

	def is_alive(self):
		return self.health > 0

	def is_exit(self):
		return (self.player_x, self.player_y) == self.exit

	def status(self):
		return f"Nyawa: {self.health} | Posisi: ({self.player_x},{self.player_y}) | Giliran: {self.turn}"

	def print_map(self, reveal=False):
		s = self.size
		lines = []
		for y in range(s):
			row = []
			for x in range(s):
				if (x, y) == (self.player_x, self.player_y):
					row.append('P')
				elif (x, y) == self.exit and reveal:
					row.append('E')
				elif self.map[y][x].character:
					row.append('N' if self.map[y][x].character.kind == 'npc' else 'H')
				else:
					row.append('.')
			lines.append(' '.join(row))
		return '\n'.join(lines)


def print_welcome():
	art = r'''
  ____  _                        _               _
 |  _ \(_) __ _ _   _ _ __   ___| |__   ___  ___| |_
 | | | | |/ _` | | | | '_ \ / __| '_ \ / _ \/ __| __|
 | |_| | | (_| | |_| | | | | (__| | | |  __/ (__| |_
 |____/|_|\__, |\__,_|_| |_|\___|_| |_|\___|\___|\__|
		  |___/    
'''
	print(art)
	print('Selamat datang di Mystery Escape Room!')
	print('Ketik "bantuan" untuk melihat perintah. Mainkan dalam bahasa Indonesia.')


def print_help():
	help_text = '''
Perintah:
- pergi <arah>  : pindah ke arah (utara/selatan/timur/barat) atau n/s/e/w
- lihat         : melihat peta sederhana
- status        : lihat nyawa dan posisi
- bantuan       : tampilkan pesan ini
- keluar        : keluar dari permainan
'''
	print(textwrap.dedent(help_text))


def victory_art():
	return r'''
	   ____  _   _  _____ _   _  _____  
	  / ___|| | | |/ ____| \ | |/ ____| 
	  \___ \| |_| | (___ |  \| | |  __  
	   ___) |  _  |\___ \| |\  | | |_ | 
	  |____/|_| |_|_____)|_| \_|\_____| 

	''' + '\n' + 'SELAMAT! Kamu berhasil keluar! ' + ASCII['treasure']


def main(argv=None):
	parser = argparse.ArgumentParser()
	parser.add_argument('--auto-test', action='store_true', help='Run a short non-interactive demo')
	args = parser.parse_args(argv)

	game = Game(size=3)
	print_welcome()

	if args.auto_test:
		print('Menjalankan demo otomatis...')
		print('Peta awal (N=npc, H=ghost, P=player, .=kosong):')
		print(game.print_map(reveal=True))
		print('\nStatus:', game.status())
		print('\nMencoba bergerak utara...')
		print(game.move('utara'))
		print('\nStatus:', game.status())
		print('\nDemo selesai.')
		return

	while True:
		if not game.is_alive():
			print('\nNyawamu habis. Permainan berakhir.')
			break
		if game.is_exit():
			slowprint(victory_art(), 0.002)
			break
		cmd = input('\n> ').strip()
		if not cmd:
			continue
		parts = cmd.split()
		verb = parts[0].lower()
		if verb in ('pergi', 'go') and len(parts) > 1:
			direction = parts[1]
			print(game.move(direction))
		elif verb in ('n', 's', 'e', 'w', 'utara', 'selatan', 'timur', 'barat'):
			print(game.move(verb))
		elif verb == 'lihat' or verb == 'map':
			print('Peta saat ini (N=npc, H=ghost, P=player, .=kosong):')
			print(game.print_map(reveal=False))
		elif verb == 'status':
			print(game.status())
		elif verb == 'bantuan' or verb == 'help':
			print_help()
		elif verb == 'keluar' or verb == 'quit' or verb == 'exit':
			print('Keluar dari permainan. Sampai jumpa!')
			break
		else:
			print('Perintah tidak dikenal. Ketik "bantuan" untuk daftar perintah.')


if __name__ == '__main__':
	main()

