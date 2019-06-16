import pygame


class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable(pygame.sprite.Sprite):
    def __init__(self, image_loc, posx, posy, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load(image_loc)
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy
        self.w = self.image.get_width()
        self.h = self.image.get_height()
