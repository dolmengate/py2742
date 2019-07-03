import multiprocessing
import random

from main import esper
from .processor import *
from sys import exit


class SpawnProcess:
    def __init__(self, max_enemies, resx, resy, pipe_game_side):
        self._settings = {
            "max_enemies": max_enemies,
            "res_x": resx,
            "res_y": resy,
            "vel_max": 2,
            "sleep": 0.2,
            "scale_min": 0.2,
            "scale_max": 0.5,
            "enabled": True,
        }
        self._pipe_game_side = pipe_game_side
        self._proc = multiprocessing.Process(target=self._enemies_over_time)
        self._proc.start()

    def _enemies_over_time(self) -> None:
        """
        Callback passed to a subprocess (multiprocessing.Process) as the target to periodically generate attributes
        to construct enemies with. This function doesn't know anything about the world, it simply generates enemy
        attributes based on its current settings
        :return: None, enemy attributes are sent through self._game.send() for interprocess communication.
        """
        while self._settings["enabled"]:
            posx = random.randint(0, self._settings["res_x"])
            posy = random.randint(0, self._settings["res_y"])
            vel_max = self._settings["vel_max"]
            velx = random.randint(-vel_max, vel_max)
            vely = random.randint(-vel_max, vel_max)
            time.sleep(self._settings["sleep"])
            scale = random.uniform(self._settings["scale_min"], self._settings["scale_max"])

            # send enemies to pipe
            if self._settings["enabled"]:
                self._pipe_game_side.send((posx, posy, velx, vely, scale))

            # print(f'generated enemy attributes\nvel: {velx},{vely}\nscale:{scale}')

            # apply pending updates from the other side of the pipe
            if self._pipe_game_side.poll():
                self._settings.update(self._pipe_game_side.recv())

    def get_max_enemies(self) -> int:
        return self._settings['max_enemies']


class SpawnController:
    def __init__(self, game, max_enemies, resx, resy):
        # todo enemy locations based on player location
        # todo spawn frequency based on enemies on map
        # todo velocity based on Difficulty
        # todo alter entity speed based on size

        self.world = game.world
        self.game = game
        self._game, self._enemies = multiprocessing.Pipe()
        self._process = SpawnProcess(max_enemies, resx, resy, self._game)

    def process(self):
        if not len(self.world._entities) >= self._process.get_max_enemies():
            # add next enemy
            if self.enemies_in_queue():
                self.game.add_enemy(*self.next_enemy())

        # update difficulty
        # if len(self.world._entities) >= 2:
        #     self.spawn.update_settings({"scale_min": 0.5, "scale_max": 0.5, "sleep": 1, "vel_max": 1})

    def _update_settings(self, settings: dict) -> None:
        """
        Change the parameters by which self._enemies_over_time() creates enemy attributes
        Any keys in @settings that already have a value in _enemies_over_time will override
        :param settings: a dictionary of settings and values, see _enemies_over_time for valid values
        :return: None
        """
        self._enemies.send(settings)

    def enemies_in_queue(self) -> bool:
        return self._enemies.poll()

    def next_enemy(self) -> tuple:
        return self._enemies.recv()

    def pause(self):
        self._enemies.send({"enabled": False})
        return self

    def resume(self):
        self._enemies.send({"enabled": True})
        return self


class Game:
    def __init__(self, enemies_per_sec=5, max_enemies=99, fps=60, res=(1080, 720)):
        self.eps = enemies_per_sec
        self.fps = fps
        self.res = res
        self.world = esper.World()
        self.window = pygame.display.set_mode(self.res)
        self.spawn = SpawnController(self, max_enemies, res[0], res[1])

    def _add_player(self) -> int:
        player = self.world.create_entity()
        self.world.add_component(player, Velocity(x=0, y=0))
        self.world.add_component(player, RenderableActor(posx=100, posy=100, scale=0.5, color=(100, 0, 255)))
        self.world.add_component(player, Consumer(g_rate=0.05))
        self.world.add_component(player, ScoreValue())
        return player

    def add_enemy(self, x: int, y: int, velx: int, vely: int, scale=1) -> None:
        enemy = self.world.create_entity()
        self.world.add_component(enemy, Velocity(x=velx, y=vely))
        self.world.add_component(enemy, RenderableActor(posx=x, posy=y, scale=scale))
        self.world.add_component(enemy, Consumer(g_rate=0.1))
        self.world.add_component(enemy, ScoreValue())

    def build_game_status(self):
        font = pygame.font.SysFont('default', 20)
        player_score = self.world.create_entity()
        menu_renderable = MenuItem("score", (20, 20), 40, 40)
        menu_renderable.image = font.render('Score: ', False, (255, 255, 255))
        self.world.add_component(player_score, menu_renderable)

    def _load_processors(self):
        self.world.add_processor(RenderProcessor(window=self.window))
        self.world.add_processor(MovementProcessor(minx=0, maxx=self.res[0], miny=0, maxy=self.res[1]))
        self.world.add_processor(CollisionProcessor())

    def _game_over(self) -> bool:
        try:
            self.world.component_for_entity(1, Velocity)
        except KeyError:
            return True
        return False

    def start(self):
        pygame.init()
        pygame.display.set_caption("Aggressor")
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)

        player = self._add_player()
        self._load_processors()
        self.build_game_status()

        running = True
        while running:
            if self._game_over():
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.world.component_for_entity(player, Velocity).x = -3
                    elif event.key == pygame.K_RIGHT:
                        self.world.component_for_entity(player, Velocity).x = 3
                    elif event.key == pygame.K_UP:
                        self.world.component_for_entity(player, Velocity).y = -3
                    elif event.key == pygame.K_DOWN:
                        self.world.component_for_entity(player, Velocity).y = 3
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.world.component_for_entity(player, Velocity).x = 0
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        self.world.component_for_entity(player, Velocity).y = 0

            self.world.process()
            self.spawn.process()
            clock.tick(self.fps)
        self.spawn.pause()
        exit(0)
