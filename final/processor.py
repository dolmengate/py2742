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
            rend1.increment_size(1)

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
        self.screen_min_x = minx
        self.screen_max_x = maxx
        self.screen_min_y = miny
        self.screen_max_y = maxy

    def process(self):
        for ent, (vel, rend) in self.world.get_components(Velocity, Renderable):
            rend.x += vel.x
            rend.y += vel.y

            # disallow movement outside the boundaries of the screen
            rend.x = max(self.screen_min_x, rend.x)
            rend.y = max(self.screen_min_y, rend.y)
            rend.x = min(self.screen_max_x - rend.w, rend.x)
            rend.y = min(self.screen_max_y - rend.h, rend.y)

            # enemy-specific movement logic
            if ent != 1:

                # run away bruh
                enemy_entities = (e[1][0] for e in self.world.get_components(Renderable) if e[0] != ent)
                enemies = sorted(enemy_entities,
                                 key=lambda c: hypot(c.x - rend.x, c.y - rend.y)
                                 )
                if enemies:
                    closest = enemies[0]
                    # print(f'{closest.x}, {closest.y}')
                    if closest.x < rend.x:
                        vel.x = -2.9
                    elif closest.x > rend.x:
                        vel.x = 2.9
                    if closest.y < rend.y:
                        vel.y = -2.9
                    elif closest.y > rend.y:
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
            self.window.blit(rend.image, (rend.x, rend.y))
        # Flip the framebuffers
        pygame.display.flip()
