import time
from typing import Tuple

import esper
from component import *
import pygame
import itertools
from math import hypot


class CollisionProcessor(esper.Processor):
    def __init__(self):
        super().__init__()

    def _collide(self, comps1: Tuple[int, Renderable, Consumer], comps2: Tuple[int, Renderable, Consumer]):
        def consume_enemy(consumer: Tuple[int, Renderable, Consumer], consumed: Tuple[int, Renderable, Consumer]):
            entity1 = consumer[0]
            entity2 = consumed[0]
            rend1, rend2 = consumer[1], consumed[1]
            cons1, cons2 = consumer[2], consumed[2]
            self.world.delete_entity(entity2)
            rend1.rescale_image(1 + (cons1.growth_rate * (rend2.w / 100)))

        rend1, rend2 = comps1[1], comps2[1]
        if rend1.is_bigger_than(rend2):
            consume_enemy(comps1, comps2)
        else:
            consume_enemy(comps2, comps1)

    def process(self):
        # Sprite Groups instead?
        for a, b in itertools.product(self.world.get_components(Renderable, Consumer), repeat=2):
            # get Renderables and Consumers
            a_rend, b_rend = a[1][0], b[1][0]
            a_cons, b_cons = a[1][1], b[1][1]
            if a_rend != b_rend and pygame.sprite.collide_rect(a_rend, b_rend):
                self._collide((a[0], a_rend, a_cons), (b[0], b_rend, b_cons))


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

            # enemy-specific movement logic
            if ent != 1:
                # bounce enemies off of the screen boundaries
                if rend.rect.left == self.minx or rend.rect.right == self.maxx:
                    vel.x = -vel.x
                if rend.rect.bottom == self.maxy or rend.rect.top == self.miny:
                    vel.y = -vel.y

                # run away bruh
                enemy_entities = (e[1][0] for e in self.world.get_components(Renderable) if e[0] != ent)
                closest = sorted(enemy_entities,
                                 key=lambda c: hypot(c.rect.x - rend.rect.x, c.rect.y - rend.rect.y)
                                 )[0]
                # print(f'{closest.rect.x}, {closest.rect.y}')
                if closest.rect.x < rend.rect.x:
                    vel.x = -2.9
                elif closest.rect.x > rend.rect.x:
                    vel.x = 2.9
                if closest.rect.y < rend.rect.y:
                    vel.y = -2.9
                elif closest.rect.y > rend.rect.y:
                    vel.y = 2.9


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
