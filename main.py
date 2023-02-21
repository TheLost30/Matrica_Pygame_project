from images import *
import json


class Map(SpriteGroup):
    def __init__(self, map_width, map_height):
        super().__init__()
        self.top_block_image = load_image(r'Map/Dirt_GU.png')
        self.bottom_block_image = load_image(r'Map/Dirt.png')
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

    def hero_collides(self, side):
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

    def emeny_collides(self, side):
        match side:
            case 'top':
                rect = game.hero.rect.collidelistall(self.rect_list)
                if not rect:
                    return 0
                for i in rect:
                    if -5 <= game.hero.rect.top - self.rect_list[i].bottom <= 0:
                        if game.hero.rect.top - self.rect_list[i].bottom <= -2:
                            self.pos_y -= game.hero.rect.top - self.rect_list[i].bottom
                        return 1
            case 'left':
                rect = game.hero.wrect.collidelistall(self.rect_list)
                if not rect:
                    return 0
                for i in rect:
                    if -4 <= game.hero.wrect.left - self.rect_list[i].right <= 0:
                        if game.hero.wrect.left - self.rect_list[i].right <= -1:
                            self.pos_x -= game.hero.wrect.left - self.rect_list[i].right
                        return 1
            case 'right':
                rect = game.hero.wrect.collidelistall(self.rect_list)
                if not rect:
                    return 0
                for i in rect:
                    if 4 >= game.hero.wrect.right - self.rect_list[i].left >= 0:
                        if game.hero.wrect.right - self.rect_list[i].left >= 1:
                            self.pos_x -= game.hero.wrect.right - self.rect_list[i].left
                        return 1
            case 'bottom':
                rect = game.hero.rect.collidelistall(self.rect_list)
                if not rect:
                    return 0
                for i in rect:
                    if 10 >= game.hero.rect.bottom - self.rect_list[i].top >= 0:
                        if game.hero.rect.bottom - self.rect_list[i].top >= 2:
                            self.pos_y -= game.hero.rect.bottom - self.rect_list[i].top
                        return 1
        return 0

    def acceleration(self):
        left, right = self.hero_collides('left'), self.hero_collides('right')
        up, bottom = self.hero_collides('top'), self.hero_collides('bottom')
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
            self.vertical_speed += 0.25 if self.vertical_speed < 4 else 0

        self.pos_x += self.horisontal_speed
        self.pos_y += self.vertical_speed

    def place(self):
        self.rect_list = []
        for y in range(len(self.map_matrix)):
            for x in range(len(self.map_matrix[y])):
                if self.map_matrix[y][x] != ' ' and self.map_matrix[y][x] != 'P':
                    self.rect_list.append(pygame.Rect(x * 50 - self.pos_x, y * 50 - self.pos_y, 50, 50))
                    if self.map_matrix[y][x] == '-':
                        screen.blit(self.top_block_image, self.rect_list[-1])
                    elif self.map_matrix[y][x] == '█':
                        screen.blit(self.bottom_block_image, self.rect_list[-1])

    def custom_draw(self):
        self.acceleration()
        self.display_place.blit(self.background, ((game.time / 3) % self.background.get_width(), -200))
        self.display_place.blit(self.background, (((game.time / 3) % self.background.get_width())
                                                  - self.background.get_width(), -200))
        self.place()

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
        self.stats = data['default']

    def get_pos(self):
        return self.pos_x, self.pos_y

    def acceleration(self):
        self.rect = pygame.Rect((self.pos_x + 12, self.pos_y + 15), (32, 76))
        self.wrect = pygame.Rect((self.pos_x + 8, self.pos_y + 24), (40, 65))
        game.hero_group.update()
        if not game.map.hero_collides('bottom'):
            if game.map.horisontal_speed > 0 or self.last_side == 'right':
                screen.blit(self.image_jump.image_frame(), (self.pos_x, self.pos_y - 5))
            elif game.map.horisontal_speed < 0 or self.last_side == 'left':
                image = pygame.transform.flip(self.image_jump.image_frame(), True, False)
                screen.blit(image, (self.pos_x - 40, self.pos_y - 5))
            self.image_run.cur_frame = 0
        elif game.map.left_pressed or game.map.right_pressed:
            if game.map.horisontal_speed > 0 or self.last_side == 'right':
                screen.blit(self.image_run.image_frame(), (self.pos_x, self.pos_y - 5))
            elif game.map.horisontal_speed < 0 or self.last_side == 'left':
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
        if game.map.horisontal_speed > 0:
            self.last_side = 'right'
        elif game.map.horisontal_speed < 0:
            self.last_side = 'left'


class Enemy(Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.display_place = pygame.display.get_surface()
        self.enemy_test = load_image(r'hitbox.png')
        self.hp = 100 + 10 * (game.time // 100)
        for y in range(len(game.map.map_matrix)):
            for x in range(len(game.map.map_matrix[y])):
                if game.map.map_matrix[y][x] == '-' and randint(0, 10) == 1:
                    self.rect = pygame.Rect(x * 50, (y * 50) - 96, 38, 96)
                    return

    def acceleration(self):
        coords = [self.rect.left, self.rect.top]
        move = self.player_side((self.display_place.get_width() // 2 + game.map.pos_x) - coords[0])
        coords[0] += move
        self.rect = pygame.Rect(coords[0], coords[1], 38, 96)
        self.display_place.blit(self.enemy_test, (coords[0] - game.map.pos_x, coords[1] - game.map.pos_y))

    @staticmethod
    def player_side(n):
        if n > 0:
            return 1
        elif n < 0:
            return -1
        else:
            return 0


class OverlayingGUI(Sprite):
    def __init__(self, group):
        self.display_place = pygame.display.get_surface()
        super(OverlayingGUI, self).__init__(group)
        self.score_points = None
        self.menu_r = None
        self.score = None
        self.health = None
        self.exit_r = None
        self.continue_r = None
        self.start_r = None
        self.font_50 = pygame.font.Font('Data/m5x7.ttf', 50)
        self.font_100 = pygame.font.Font('Data/m5x7.ttf', 100)
        self.font_150 = pygame.font.Font('Data/m5x7.ttf', 150)
        self.pause_trans_gray = load_image(r'gray_t.png')
        self.old_score = data['score']

    def update_values(self):
        self.score_points = ((game.time // 60) * 7) + (game.hero.collected_coins * 10) + self.old_score
        game.data['score'] = self.score_points
        self.score = self.font_50.render(f'score: {self.score_points}', True, (255, 255, 255))
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

        continue_t = self.font_100.render('Continue', True, (255, 255, 255))
        self.continue_r = pygame.Rect((150, 300), (continue_t.get_width(), continue_t.get_height()))
        self.display_place.blit(continue_t, (150, 300))

        menu_t = self.font_100.render('Main menu', True, (255, 255, 255))
        self.menu_r = pygame.Rect((150, 400), (menu_t.get_width(), menu_t.get_height()))
        self.display_place.blit(menu_t, (150, 400))

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

        exit_t = self.font_100.render('Quit', True, (255, 255, 255))
        self.exit_r = pygame.Rect((150, 500), (exit_t.get_width(), exit_t.get_height()))
        self.display_place.blit(exit_t, (150, 500))


def terminate():
    with open('Data/Data.json', 'w') as datafile:
        json.dump(game.data, datafile)
    pygame.quit()
    sys.exit()


class MainGame:
    def __init__(self, database):
        self.paused = 2  # 0-game, 1-pause, 2-menu
        self.data = database
        self.overlay = None
        self.overlay_group = None
        self.time = None
        self.hero = None
        self.hero_group = None
        self.map_group = None
        self.map = None
        self.map = None
        self.display_place = None
        self.enemy_group = None
        self.enemy_list = None
        self.new_game()

    def new_game(self, type):
        if type == 'default':
            self.display_place = pygame.display.get_surface()
            self.map = Map(width, height)
            self.map_group = SpriteGroup()

            self.hero_group = SpriteGroup()
            self.hero = Hero(*self.map.spawn_point, self.hero_group)

            self.enemy_group = SpriteGroup()
            self.enemy_list = []
            self.time = 0
            self.overlay_group = SpriteGroup()
            self.overlay = OverlayingGUI(self.overlay_group)

        else:
            self.display_place = pygame.display.get_surface()
            self.map = Map(width, height)
            self.map_group = SpriteGroup()

            self.hero_group = SpriteGroup()
            self.hero = Hero(*self.map.spawn_point, self.hero_group)
            self.hero.health = data['present']['hp']

            self.enemy_group = SpriteGroup()
            self.enemy_list = []
            self.time = 0
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
                        return
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.map.turn('up', True)
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.map.turn('left', True)
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.map.turn('right', True)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.map.turn('down', True)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.map.turn('up', False)
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.map.turn('left', False)
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.map.turn('right', False)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.map.turn('down', False)
                elif not pygame.display.get_active():
                    self.paused = 1
                    return
            if randint(0, 10) == 1:
                self.enemy_list.append(Enemy(self.enemy_group))
            self.time += 1
            self.map.custom_draw()
            self.hero.acceleration()
            self.enemy_update()
            self.overlay.update_values()
            pygame.display.flip()
            clock.tick(60)

    def pause(self):
        self.overlay.pause_overlay()
        while self.paused == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if self.overlay.continue_r.left < x < self.overlay.continue_r.right and \
                            self.overlay.continue_r.top < y < self.overlay.continue_r.bottom:
                        self.paused = 0
                    elif self.overlay.menu_r.left < x < self.overlay.menu_r.right and \
                            self.overlay.menu_r.top < y < self.overlay.menu_r.bottom:
                        self.paused = 2
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = 0
                        return
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.map.turn('up', False)
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.map.turn('left', False)
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.map.turn('right', False)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.map.turn('down', False)
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
                        game.new_game()
                        game.overlay.old_score = 0
                        self.paused = 0
                        return
                    elif self.overlay.continue_r.left < x < self.overlay.continue_r.right and \
                            self.overlay.continue_r.top < y < self.overlay.continue_r.bottom:
                        self.paused = 0
                        return
                    elif self.overlay.exit_r.left < x < self.overlay.exit_r.right and \
                            self.overlay.exit_r.top < y < self.overlay.exit_r.bottom:
                        terminate()
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

    def enemy_update(self):
        for i in self.enemy_list:
            i.acceleration()


if __name__ == '__main__':
    with open('Data/Data.json') as data_file:
        data = json.load(data_file)
    clock = pygame.time.Clock()
    pygame.init()
    size = width, height = [1900, 980]
    screen = pygame.display.set_mode(size)

    game = MainGame(data)
    while True:
        game.opener(game.paused)
