import os

import pygame


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class AnimatedSprite(Sprite):
    def __init__(self, sheet, columns, rows, x, y, group):
        super().__init__(group)
        self.number_frames = (columns * rows) - 1
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.times = 0
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.coords = [0, 0]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        if self.times < self.number_frames:
            self.times += 1
        elif self.times == self.number_frames:
            self.cur_frame = int(self.cur_frame + 1) % len(self.frames)
            self.times = 0
        self.image = self.frames[self.cur_frame]

    def image_frame(self):
        return self.image

    def get_coords(self):
        return self.coords

    def set_coords(self, coords):
        self.coords = [*coords]


def load_image(name, color_key=None):
    fullname = os.path.join('Data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image
