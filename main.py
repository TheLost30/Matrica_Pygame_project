import pygame

from images import *


class Map(SpriteGroup):
	def __init__(self, map_width, map_height):
		super().__init__()
		self.display_place = pygame.display.get_surface()
		self.background = load_image('background.png')
		self.back_rect = self.background.get_rect(topleft=(-200, 0))
		self.map_matrix = self.generate(int(map_width // 20), int(map_height // 20), int(map_height // 50), 3)
		self.rect_list = [pygame.Rect(x * 50, y * 50, 50, 50) for y in range(len(self.map_matrix))
		                  for x in range(len(self.map_matrix[y])) if self.map_matrix[y][x] != ' ']
		self.pos_x = 0
		self.pos_y = 0
		self.vertical_speed, self.horisontal_speed = 0, 0
		self.up_pressed, self.left_pressed, self.right_pressed, self.down_pressed = False, False, False, False
		self.spawn_point = [0, 0]

	def turn(self, button, state):
		match button:
			case 'up':
				self.up_pressed = state
			case 'left':
				self.left_pressed = state
			case 'right':
				self.right_pressed = state
			case 'down':
				self.down_pressed = state

	def collides(self, side):
		match side:
			case 'top':
				rects = game.hero.rect.collidelistall(self.rect_list)
				if not rects:
					return 0
				for i in rects:
					if -5 <= game.hero.rect.top - self.rect_list[i].bottom <= 0:
						if game.hero.rect.top - self.rect_list[i].bottom <= -2:
							self.pos_y -= game.hero.rect.top - self.rect_list[i].bottom
						return 1
			case 'left':
				wrects = game.hero.wrect.collidelistall(self.rect_list)
				if not wrects:
					return 0
				for i in wrects:
					if -4 <= game.hero.wrect.left - self.rect_list[i].right <= 0:
						if game.hero.wrect.left - self.rect_list[i].right <= -1:
							self.pos_x -= game.hero.wrect.left - self.rect_list[i].right
						return 1
			case 'right':
				wrects = game.hero.wrect.collidelistall(self.rect_list)
				if not wrects:
					return 0
				for i in wrects:
					if 4 >= game.hero.wrect.right - self.rect_list[i].left >= 0:
						if game.hero.wrect.right - self.rect_list[i].left >= 1:
							self.pos_x -= game.hero.wrect.right - self.rect_list[i].left
						return 1
			case 'bottom':
				rects = game.hero.rect.collidelistall(self.rect_list)
				if not rects:
					return 0
				for i in rects:
					if 10 >= game.hero.rect.bottom - self.rect_list[i].top >= 0:
						if game.hero.rect.bottom - self.rect_list[i].top >= 2:
							self.pos_y -= game.hero.rect.bottom - self.rect_list[i].top
						return 1
		return 0

	def acceleration(self):
		left, right = self.collides('left'), self.collides('right')
		up, bottom = self.collides('top'), self.collides('bottom')
		if left or right:
			self.horisontal_speed = 0
		else:
			self.horisontal_speed *= 0.9
		if self.left_pressed:
			if left:
				self.horisontal_speed = 0
			else:
				self.horisontal_speed -= 0.25 if self.horisontal_speed > -2 else 0
		if self.right_pressed:
			if right:
				self.horisontal_speed = 0
			else:
				self.horisontal_speed += 0.25 if self.horisontal_speed < 2 else 0

		if bottom:
			if self.up_pressed:
				self.vertical_speed = -5
			else:
				self.vertical_speed = 0
		else:
			self.vertical_speed += 0.25 if self.vertical_speed < 5 else 0

		self.pos_x += self.horisontal_speed
		self.pos_y += self.vertical_speed

	def custom_draw(self):
		self.acceleration()
		self.display_place.blit(self.background, ((game.game_time / 3) % self.background.get_width(), -200))
		self.display_place.blit(self.background, (((game.game_time / 3) % self.background.get_width())
		                                          - self.background.get_width(), -200))
		self.place()

	def place(self):
		top_image = load_image(r'Map/Dirt_GU.png')
		bot_image = load_image(r'Map/Dirt.png')
		self.rect_list = []
		for y in range(len(self.map_matrix)):
			for x in range(len(self.map_matrix[y])):
				if self.map_matrix[y][x] != ' ' and self.map_matrix[y][x] != 'P':
					self.rect_list.append(pygame.Rect(x * 50 - self.pos_x, y * 50 - self.pos_y, 50, 50))
					if self.map_matrix[y][x] == '-':
						screen.blit(top_image, self.rect_list[-1])
					elif self.map_matrix[y][x] == '█':
						screen.blit(bot_image, self.rect_list[-1])

	def generate(self, x, y, earth_level, max_level):
		sp = []
		sp.extend(list([' '] * x for _ in range(y)))
		k = earth_level
		player_placed = False

		for i in range(len(sp[0])):
			n = randint(0, 1)
			k += randint(-n, n)
			if 0 >= k:
				k = 0
			elif k >= len(sp):
				k = len(sp) - 1
			if k < max_level:
				k = max_level
			if randint(0, 20) == 1 and not player_placed:
				player_placed = True
				sp[k - 1][i] = 'P'
				self.spawn_point = [(k - 1) * 50, i * 50]
			sp[k][i] = '-'
			for j in range(k + 1, len(sp)):
				sp[j][i] = '█'
		return sp


class Hero(Sprite):
	def __init__(self, pos_x, pos_y, group):
		super(Hero, self).__init__(group)
		self.image_idle = AnimatedSprite(load_image(r'Cyborg/Cyborg_idle.png'), 6, 1, 96, 96, group)
		self.image_jump = AnimatedSprite(load_image(r'Cyborg/Cyborg_doublejump.png'), 6, 1, 96, 96, group)
		self.image_run = AnimatedSprite(load_image(r'Cyborg/Cyborg_run.png'), 6, 1, 96, 96, group)
		self.pos_x = pos_x + screen.get_width() // 2
		self.pos_y = pos_y + screen.get_height() // 2
		self.rect = self.image_idle.image_frame().get_rect()
		self.wrect = self.rect.copy()
		self.last_side = 'right'
		self.collected_coins = 0
		self.health = 100

	def get_pos(self):
		return self.pos_x, self.pos_y

	def acceleration(self):
		self.rect = pygame.Rect((self.pos_x + 12, self.pos_y + 15), (32, 76))
		self.wrect = pygame.Rect((self.pos_x + 8, self.pos_y + 24), (40, 65))
		game.hero_group.update()
		if not game.game_map.collides('bottom'):
			if game.game_map.horisontal_speed > 0 or self.last_side == 'right':
				screen.blit(self.image_jump.image_frame(), (self.pos_x, self.pos_y - 5))
			elif game.game_map.horisontal_speed < 0 or self.last_side == 'left':
				image = pygame.transform.flip(self.image_jump.image_frame(), True, False)
				screen.blit(image, (self.pos_x - 40, self.pos_y - 5))
			self.image_run.cur_frame = 0
		elif game.game_map.left_pressed or game.game_map.right_pressed:
			if game.game_map.horisontal_speed > 0 or self.last_side == 'right':
				screen.blit(self.image_run.image_frame(), (self.pos_x, self.pos_y - 5))
			elif game.game_map.horisontal_speed < 0 or self.last_side == 'left':
				image = pygame.transform.flip(self.image_run.image_frame(), True, False)
				screen.blit(image, (self.pos_x - 40, self.pos_y - 5))
			self.image_jump.cur_frame = 0
		else:
			if self.last_side == 'right':
				screen.blit(self.image_idle.image_frame(), (self.pos_x, self.pos_y - 5))
			if self.last_side == 'left':
				image = pygame.transform.flip(self.image_idle.image_frame(), True, False)
				screen.blit(image, (self.pos_x - 40, self.pos_y - 5))
			self.image_run.cur_frame = 0
			self.image_jump.cur_frame = 0
		if game.game_map.horisontal_speed > 0:
			self.last_side = 'right'
		elif game.game_map.horisontal_speed < 0:
			self.last_side = 'left'


class OverlayingGUI(Sprite):
	def __init__(self, group):
		self.display_place = pygame.display.get_surface()
		super(OverlayingGUI, self).__init__(group)
		self.score = None
		self.health = None
		self.exit_r = None
		self.settings_r = None
		self.continue_r = None
		self.start_r = None
		self.font_50 = pygame.font.Font('Data/m5x7.ttf', 50)
		self.font_100 = pygame.font.Font('Data/m5x7.ttf', 100)
		self.font_150 = pygame.font.Font('Data/m5x7.ttf', 150)
		self.pause_trans_gray = load_image(r'gray_t.png')

	def update_values(self):
		self.score = self.font_50.render(f'score: {((game.game_time // 60) * 7) + (game.hero.collected_coins * 10)}',
		                                 True, (255, 255, 255))
		self.health = self.font_100.render(f'HP: {game.hero.health}', True, (100, 255, 100))
		self.display_place.blit(self.score, ((self.display_place.get_width()) - self.score.get_width(),
		                                     self.display_place.get_height() - self.score.get_height()))
		self.display_place.blit(self.health, (self.health.get_width() - 220, self.display_place.get_height()
		                                      - self.health.get_height()))

	def pause_overlay(self):
		text = self.font_100.render("Game Paused", True, (255, 255, 255))
		self.display_place.blit(self.pause_trans_gray, (0, 0))
		self.display_place.blit(text,
		                        (text.get_width() - 350, screen.get_height() // 9))

	def menu_overlay(self):
		name = self.font_150.render('Game title', True, (255, 255, 255))
		name_b = self.font_150.render('Game title', True, (0, 0, 0))
		self.display_place.blit(name_b, (99, 99))
		self.display_place.blit(name, (100, 100))

		start_t = self.font_100.render('Start', True, (255, 255, 255))
		self.start_r = pygame.Rect((150, 300), (start_t.get_width(), start_t.get_height()))
		self.display_place.blit(start_t, (150, 300))

		continue_t = self.font_100.render('Continue', True, (255, 255, 255))
		self.continue_r = pygame.Rect((150, 400), (continue_t.get_width(), continue_t.get_height()))
		self.display_place.blit(continue_t, (150, 400))

		settings_t = self.font_100.render('Settings', True, (255, 255, 255))
		self.settings_r = pygame.Rect((150, 500), (settings_t.get_width(), settings_t.get_height()))
		self.display_place.blit(settings_t, (150, 500))

		exit_t = self.font_100.render('Quit', True, (255, 255, 255))
		self.exit_r = pygame.Rect((150, 600), (exit_t.get_width(), exit_t.get_height()))
		self.display_place.blit(exit_t, (150, 600))


def terminate():
	pygame.quit()
	sys.exit()


class MainGame:
	def __init__(self):
		self.display_place = pygame.display.get_surface()
		self.game_map = Map(width, height)
		self.map_group = SpriteGroup()
		self.hero_group = SpriteGroup()
		self.hero = Hero(*self.game_map.spawn_point, self.hero_group)
		self.game_time = 0
		self.paused = 2  # 0-game, 1-pause, 2-menu
		self.overlay_group = SpriteGroup()
		self.overlay = OverlayingGUI(self.overlay_group)

	def game(self):
		while not self.paused:
			self.hero.image_idle.update()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					terminate()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.paused = 1
						continue
					if event.key == pygame.K_w or event.key == pygame.K_UP:
						self.game_map.turn('up', True)
					elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
						self.game_map.turn('left', True)
					elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
						self.game_map.turn('right', True)
					elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
						self.game_map.turn('down', True)

				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_w or event.key == pygame.K_UP:
						self.game_map.turn('up', False)
					elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
						self.game_map.turn('left', False)
					elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
						self.game_map.turn('right', False)
					elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
						self.game_map.turn('down', False)
				elif not pygame.display.get_active():
					self.paused = 1
					continue
			self.game_time += 1
			self.game_map.custom_draw()
			self.hero.acceleration()
			self.overlay.update_values()
			pygame.display.flip()
			clock.tick(60)

	def pause(self):
		self.overlay.pause_overlay()
		while self.paused == 1:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					terminate()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.paused = 0
						continue
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_w or event.key == pygame.K_UP:
						self.game_map.turn('up', False)
					elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
						self.game_map.turn('left', False)
					elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
						self.game_map.turn('right', False)
					elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
						self.game_map.turn('down', False)
			pygame.display.flip()
			clock.tick(60)

	def menu(self):
		time = 0
		background = load_image('background.png')
		while self.paused == 2:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					terminate()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					x, y = pygame.mouse.get_pos()
					if self.overlay.start_r.left < x < self.overlay.start_r.right and \
						self.overlay.start_r.top < y < self.overlay.start_r.bottom:
						self.paused = 0
			screen.blit(background, ((time / 3) % background.get_width(), -200))
			screen.blit(background, (((time / 3) % background.get_width()) - background.get_width(), -200))
			self.overlay.menu_overlay()
			time += 1
			pygame.display.flip()
			clock.tick(60)

	def opener(self, n):
		match n:
			case 0:
				self.game()
			case 1:
				self.pause()
			case 2:
				self.menu()


if __name__ == '__main__':
	clock = pygame.time.Clock()
	pygame.init()
	size = width, height = 1600, 800
	screen = pygame.display.set_mode(size)

	game = MainGame()
	while True:
		game.opener(game.paused)
