import time
from typing import Tuple

from .esper import Processor
from .component import *
import pygame
import itertools
from math import hypot

from main.component import RenderableActor, Consumer


class CollisionProcessor(Processor):
    def __init__(self):
        super().__init__()

    def _collide(self, comps1: Tuple[int, RenderableActor, Consumer, ScoreValue],
                 comps2: Tuple[int, RenderableActor, Consumer, ScoreValue]):
        def consume_enemy(consumer: Tuple[int, RenderableActor, Consumer, ScoreValue],
                          consumed: Tuple[int, RenderableActor, Consumer, ScoreValue]):
            consumed_entity = consumed[0]
            consumer_rend, consumed_rend = consumer[1], consumed[1]
            consumer_value = consumer[3]
            consumed_value = consumed[3].points

            self.world.delete_entity(consumed_entity)
            consumer_value.increment(consumed_value)
            consumer_rend.increment_size(1)

        rend1, rend2 = comps1[1], comps2[1]
        if rend1.is_bigger_than(rend2):
            consume_enemy(comps1, comps2)
        else:
            consume_enemy(comps2, comps1)

    def process(self):
        # Sprite Groups instead?
        for a, b in itertools.product(self.world.get_components(RenderableActor, Consumer, ScoreValue), repeat=2):
            # get Renderables, Consumers and ScoreValues
            a_rend, b_rend = a[1][0], b[1][0]
            a_cons, b_cons = a[1][1], b[1][1]
            a_scor, b_scor = a[1][2], b[1][2]
            if a_rend != b_rend and pygame.sprite.collide_rect(a_rend, b_rend):
                self._collide((a[0], a_rend, a_cons, a_scor), (b[0], b_rend, b_cons, b_scor))


class MovementProcessor(Processor):
    def __init__(self, minx, maxx, miny, maxy):
        super().__init__()
        self.screen_min_x = minx
        self.screen_max_x = maxx
        self.screen_min_y = miny
        self.screen_max_y = maxy

    def process(self):
        for ent, (vel, rend) in self.world.get_components(Velocity, RenderableActor):
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
                enemy_entities = (e[1][0] for e in self.world.get_components(RenderableActor) if e[0] != ent)
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


class RenderProcessor(Processor):
    def __init__(self, window, clear_color=(20, 20, 20)):
        super().__init__()
        self.window = window
        self.clear_color = clear_color
        self._menu_font = pygame.font.SysFont('default', 20)

    def process(self):
        self.window.fill(self.clear_color)

        # render player and enemies
        for ent, rend in self.world.get_component(RenderableActor):
            self.window.blit(rend.image, (rend.x, rend.y))

        # render menus
        for ent, rend in self.world.get_component(MenuItem):
            if rend.name is "score":
                try:
                    player_score = self.world.component_for_entity(1, ScoreValue).points
                except KeyError:
                    break
                rend.image = self._menu_font.render(f'Score: {player_score}', False, (255, 255, 255))
            self.window.blit(rend.image, (rend.x, rend.y))

        # Flip the framebuffers
        pygame.display.flip()
