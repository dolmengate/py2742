#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import esper
import random
import time
import multiprocessing

FPS = 60
RESOLUTION = 720, 480


class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable:
    def __init__(self, image, posx, posy, depth=0):
        self.image = image
        self.depth = depth
        self.x = posx
        self.y = posy
        self.w = image.get_width()
        self.h = image.get_height()


class MovementProcessor(esper.Processor):
    def __init__(self, minx, maxx, miny, maxy):
        super().__init__()
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, rend) in self.world.get_components(Velocity, Renderable):
            # Update the Renderable Component's position by it's Velocity:
            rend.x += vel.x
            rend.y += vel.y
            # An example of keeping the sprite inside screen boundaries. Basically,
            # adjust the position back inside screen boundaries if it tries to go outside:
            rend.x = max(self.minx, rend.x)
            rend.y = max(self.miny, rend.y)
            rend.x = min(self.maxx - rend.w, rend.x)
            rend.y = min(self.maxy - rend.h, rend.y)


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


def run():
    pygame.init()
    window = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Henlo")
    clock = pygame.time.Clock()
    pygame.key.set_repeat(1, 1)

    world = esper.World()

    def add_player(w: esper.World) -> int:
        player = w.create_entity()
        w.add_component(player, Velocity(x=4, y=0))
        w.add_component(player, Renderable(image=pygame.image.load("redsquare.png"), posx=100, posy=100))
        return player

    def add_enemy(w, x=400, y=250):
        enemy = w.create_entity()
        w.add_component(enemy, Renderable(image=pygame.image.load("bluesquare.png"), posx=x, posy=y))

    def add_processors(w):
        render_processor = RenderProcessor(window=window)
        movement_processor = MovementProcessor(minx=0, maxx=RESOLUTION[0], miny=0, maxy=RESOLUTION[1])
        w.add_processor(render_processor)
        w.add_processor(movement_processor)

    player = add_player(world)
    add_enemy(world)
    add_processors(world)

    from multiprocessing import Pipe

    into, outof = Pipe()

    def enemies_over_time(pipe_conn, sec: int) -> None:
        while True:
            x = random.randint(0, RESOLUTION[0])
            y = random.randint(0, RESOLUTION[1])
            time.sleep(sec)
            print(f'new enemy location {x},{y}')
            pipe_conn.send((x, y))

    enemy_spawn = multiprocessing.Process(target=enemies_over_time,
                                          args=(into, 2),
                                          daemon=True)
    enemy_spawn.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    world.component_for_entity(player, Velocity).x = -3
                elif event.key == pygame.K_RIGHT:
                    world.component_for_entity(player, Velocity).x = 3
                elif event.key == pygame.K_UP:
                    world.component_for_entity(player, Velocity).y = -3
                elif event.key == pygame.K_DOWN:
                    world.component_for_entity(player, Velocity).y = 3
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    world.component_for_entity(player, Velocity).x = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    world.component_for_entity(player, Velocity).y = 0

        world.process()
        clock.tick(FPS)
        if outof.poll():
            add_enemy(world, *outof.recv())


if __name__ == "__main__":
    run()
    pygame.quit()
