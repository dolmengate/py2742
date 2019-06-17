import multiprocessing
import random
from processor import *


class Game:
    def __init__(self, enemies_per_sec=2, max_enemies=5, fps=60, res=(720, 480)):
        self.eps = enemies_per_sec
        self.fps = fps
        self.res = res
        self.world = esper.World()
        self.window = pygame.display.set_mode(self.res)
        self._enemy_spawn_proc = None
        self.max_enemies = max_enemies

    def _add_player(self) -> int:
        player = self.world.create_entity()
        self.world.add_component(player, Velocity(x=0, y=0))
        self.world.add_component(player, Renderable("redsquare.png", posx=100, posy=100))
        return player

    def _add_enemy(self, x: int, y: int, velx: int, vely: int, scale=None) -> None:
        enemy = self.world.create_entity()
        self.world.add_component(enemy, Velocity(x=velx, y=vely))
        self.world.add_component(enemy, Renderable("bluesquare.png", posx=x, posy=y, scale=scale))

    def _load_processors(self):
        self.world.add_processor(RenderProcessor(window=self.window))
        self.world.add_processor(MovementProcessor(minx=0, maxx=self.res[0], miny=0, maxy=self.res[1]))
        self.world.add_processor(CollisionProcessor())

    def _init_enemy_spawn(self):
        """
        Initialize enemy spawning process
        :return: multiprocess.Pipe that integers representing enemy Entities can be .recv()'d
            from and settings .send()'t to
        """
        # todo enemy locations based on player location
        # todo spawn frequency based on enemies on map
        # todo velocity based on Difficulty

        into, outof = multiprocessing.Pipe()

        def enemies_over_time(game_conn) -> None:
            settings = {
                "vel_max": 3,
                "sleep": 2,
                "scale_min": 1.0,
                "scale_max": 1.0,
            }
            while True:
                posx = random.randint(0, self.res[0])
                posy = random.randint(0, self.res[1])
                vel_max = settings["vel_max"]
                velx = random.randint(-vel_max, vel_max)
                vely = random.randint(-vel_max, vel_max)
                time.sleep(settings["sleep"])
                scale = random.uniform(settings["scale_min"], settings["scale_max"])

                game_conn.send((posx, posy, velx, vely, scale))

                print(f'generated enemy with attributes\nvel: {velx},{vely}\nscale:{scale}')

                if game_conn.poll():
                    settings.update(game_conn.recv())

        self._enemy_spawn_proc = multiprocessing.Process(target=enemies_over_time, args=(into,), daemon=True)
        self._enemy_spawn_proc.start()

        return outof

    def start(self):
        pygame.init()
        pygame.display.set_caption("Henlo")
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)

        player = self._add_player()
        self._load_processors()

        enemy_conn = self._init_enemy_spawn()

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
            if enemy_conn.poll():
                if not len(self.world._entities) >= self.max_enemies:
                    self._add_enemy(*enemy_conn.recv())

                    # conditional enemy spawning based on game state
                    if len(self.world._entities) >= 2:
                        enemy_conn.send({"scale_min": 0.5, "scale_max": 0.5, "sleep": 1, "vel_max": 1})





# todo fix enemy spawn process not exiting on game exit with Escape
