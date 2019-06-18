import multiprocessing
import random
from processor import *
from os.path import join


class EnemySpawn:
    def __init__(self, resx, resy):
        # todo enemy locations based on player location
        # todo spawn frequency based on enemies on map
        # todo velocity based on Difficulty

        self._settings = {
            "res_x": resx,
            "res_y": resy,
            "vel_max": 3,
            "sleep": 2,
            "scale_min": 1.0,
            "scale_max": 1.0,
            "enabled": True,
        }
        self._game, self._enemies = multiprocessing.Pipe()
        self._proc = multiprocessing.Process(target=self._enemies_over_time, daemon=True)
        self._proc.start()

    def _enemies_over_time(self) -> None:
        """
        Callback passed to a subprocess (multiprocessing.Process) as the target to periodically generate attributes
        to construct enemies with. This function doesn't know anything about the world, it simply generates enemy
        attributes based on its current settings
        :return: None, enemy attributes are sent through self._game.send() for interprocess communication.
        """
        while True:
            posx = random.randint(0, self._settings["res_x"])
            posy = random.randint(0, self._settings["res_y"])
            vel_max = self._settings["vel_max"]
            velx = random.randint(-vel_max, vel_max)
            vely = random.randint(-vel_max, vel_max)
            time.sleep(self._settings["sleep"])
            scale = random.uniform(self._settings["scale_min"], self._settings["scale_max"])

            if self._settings["enabled"]:
                self._game.send((posx, posy, velx, vely, scale))

            print(f'generated enemy attributes\nvel: {velx},{vely}\nscale:{scale}')

            if self._game.poll():
                self._settings.update(self._game.recv())

    def update_settings(self, settings: dict) -> None:
        """
        Change the parameters by which self._enemies_over_time() creates enemy attributes
        Any keys in @settings that already have a value in _enemies_over_time will override
        :param settings: a dictionary of settings and values, see _enemies_over_time for valid values
        :return: None
        """
        self._enemies.send(settings)

    def enemies_remain(self) -> bool:
        return self._enemies.poll()

    def next_enemy(self) -> tuple:
        return self._enemies.recv()

    def pause(self):
        self._enemies.send({"enabled": False})

    def resume(self):
        self._enemies.send({"enabled": True})


class Game:
    def __init__(self, enemies_per_sec=2, max_enemies=2, fps=60, res=(720, 480)):
        # todo move max enemies to EnemySpawn setting
        self.eps = enemies_per_sec
        self.fps = fps
        self.res = res
        self.world = esper.World()
        self.window = pygame.display.set_mode(self.res)
        self.spawn = EnemySpawn(res[0], res[1])
        self.max_enemies = max_enemies

    def _add_player(self) -> int:
        player = self.world.create_entity()
        self.world.add_component(player, Velocity(x=0, y=0))
        self.world.add_component(player, Renderable(join("images", "honkler_ss.png"), posx=100, posy=100))
        return player

    def _add_enemy(self, x: int, y: int, velx: int, vely: int, scale=None) -> None:
        enemy = self.world.create_entity()
        self.world.add_component(enemy, Velocity(x=velx, y=vely))
        self.world.add_component(enemy, Renderable(join("images", "nose.png"), posx=x, posy=y, scale=scale))

    def _load_processors(self):
        self.world.add_processor(RenderProcessor(window=self.window))
        self.world.add_processor(MovementProcessor(minx=0, maxx=self.res[0], miny=0, maxy=self.res[1]))
        self.world.add_processor(CollisionProcessor())

    def start(self):
        pygame.init()
        pygame.display.set_caption("Henlo")
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)

        player = self._add_player()
        self._load_processors()

        running = True
        while running:
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
            clock.tick(self.fps)
            if not len(self.world._entities) >= self.max_enemies:
                if self.spawn.enemies_remain():
                    self._add_enemy(*self.spawn.next_enemy())
                # conditional enemy spawning based on game state
                if len(self.world._entities) >= 2:
                    self.spawn.update_settings({"scale_min": 0.5, "scale_max": 0.5, "sleep": 1, "vel_max": 1})

# todo fix enemy spawn process not exiting on game exit with Escape
