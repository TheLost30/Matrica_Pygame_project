import pygame
import sys
import math
from random import randint
from images import *
from functools import cache
import numpy as np


class Map(SpriteGroup):
    def __init__(self, width, height):
        super().__init__()
        self.display_place = pygame.display.get_surface()
        self.background = load_image('background.webp')
        self.back_rect = self.background.get_rect(topleft=(-200, 0))
        self.map_matrix = self.generate(int(width // 20), int(height // 20), int(height // 50), 3)
        self.rect_list = [pygame.Rect(x * 50, y * 50, 50, 50) for y in range(len(self.map_matrix))
                          for x in range(len(self.map_matrix[y])) if self.map_matrix[y][x] != ' ']
        self.pos_x = 0
        self.pos_y = 0
        self.vertical_speed, self.horisontal_speed = 0, 0
        self.up_pressed, self.left_pressed, self.right_pressed, self.down_pressed = False, False, False, False
        self.spawn_point = [0, 0]

    def get_pos(self):
        return self.pos

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
        if game.game_pause:
            self.display_place.fill((0, 0, 0))
            font = pygame.font.Font(None, 50)
            text = font.render("Game Paused", True, (255, 255, 255))
            self.display_place.blit(text, ((screen.get_width() // 2) - (text.get_width() // 2), screen.get_height() // 4))
        else:
            self.acceleration()
            self.display_place.blit(self.background, (game.hero.pos_x // 10 - 200, game.hero.pos_y // 10 - 200))
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

    def get_pos(self):
        return self.pos_x, self.pos_y

    def acceleration(self):
        self.rect = pygame.Rect((self.pos_x + 12, self.pos_y + 15), (32, 76))
        self.wrect = pygame.Rect((self.pos_x + 8, self.pos_y + 24), (40, 65))
        game.hero_group.update()
        if not game.game_pause:
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


# class OverlayingGUI(Sprite):
#     def __init__(self):
#         super(OverlayingGUI, self).__init__(overlay_group)

def terminate():
    pygame.quit()
    sys.exit()


class MainGame:
    def __init__(self):
        # rect_list, pause_menu, game_time
        self.game_map = Map(width, height)
        self.map_group = SpriteGroup()
        self.hero_group = SpriteGroup()
        self.hero = Hero(*self.game_map.spawn_point, self.hero_group)
        self.game_time = 0
        self.game_pause = False
        # overlay_group = SpriteGroup()
        # overlay = OverlayingGUI()

    def start(self):
        while not self.game_pause:
            self.hero.image_idle.update()
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_pause = True
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
                    self.game_pause = True
                    continue

            self.game_time += 1
            self.game_map.custom_draw()
            self.hero.acceleration()
            pygame.display.flip()
            clock.tick(60)
        self.pause_menu()

    def pause_menu(self):
        while self.game_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_pause = False
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
            clock.tick(60)
        self.start()


if __name__ == '__main__':
    clock = pygame.time.Clock()
    pygame.init()
    size = width, height = 1600, 800
    screen = pygame.display.set_mode(size)

    game = MainGame()
    game.start()
