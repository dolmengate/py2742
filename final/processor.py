import time
import esper
from component import *
import pygame
import itertools


class CollisionProcessor(esper.Processor):
    def __init__(self):
        pass

    def process(self):
        # Sprite Groups instead?
        for a, b in itertools.product(self.world.get_components(Renderable), repeat=2):
            s1 = a[1][0]
            s2 = b[1][0]
            if s1 != s2 and pygame.sprite.collide_rect(s1, s2):
                print(f'{time.time()} collision between {s1} and {s2}')


class MovementProcessor(esper.Processor):
    def __init__(self, minx, maxx, miny, maxy):
        super().__init__()
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

    def process(self):
        for ent, (vel, rend) in self.world.get_components(Velocity, Renderable):
            rend.rect.x += vel.x
            rend.rect.y += vel.y

            # disallow movement outside the boundaries of the screen
            rend.rect.x = max(self.minx, rend.rect.x)
            rend.rect.y = max(self.miny, rend.rect.y)
            rend.rect.x = min(self.maxx - rend.w, rend.rect.x)
            rend.rect.y = min(self.maxy - rend.h, rend.rect.y)


class RenderProcessor(esper.Processor):
    def __init__(self, window, clear_color=(20, 20, 20)):
        super().__init__()
        self.window = window
        self.clear_color = clear_color

    def process(self):
        # Clear the window:
        self.window.fill(self.clear_color)
        # This will iterate over every Entity that has this Component, and blit it:
        for ent, rend in self.world.get_component(Renderable):
            self.window.blit(rend.image, (rend.rect.x, rend.rect.y))
        # Flip the framebuffers
        pygame.display.flip()
