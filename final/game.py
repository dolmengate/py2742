import time
import multiprocessing
import random
from processor import *


class Game:
    def __init__(self, enemies_per_sec=2, fps=60, res=(720, 480)):
        self.eps = enemies_per_sec
        self.fps = fps
        self.res = res
        self.world = esper.World()
        self.window = pygame.display.set_mode(self.res)

    def _add_player(self) -> int:
        player = self.world.create_entity()
        self.world.add_component(player, Velocity(x=0, y=0))
        self.world.add_component(player, Renderable("redsquare.png", posx=100, posy=100))
        return player

    def _add_enemy(self, x: int = 400, y: int = 250) -> None:
        enemy = self.world.create_entity()
        self.world.add_component(enemy, Velocity(x=0, y=0))
        self.world.add_component(enemy, Renderable("bluesquare.png", posx=x, posy=y))

    def _load_processors(self):
        render_processor = RenderProcessor(window=self.window)
        movement_processor = MovementProcessor(minx=0, maxx=self.res[0], miny=0, maxy=self.res[1])
        collision_processor = CollisionProcessor()
        self.world.add_processor(render_processor)
        self.world.add_processor(movement_processor)
        self.world.add_processor(collision_processor)

    def _enemy_spawn(self, enable=True):
        if enable:
            into, outof = multiprocessing.Pipe()

            def enemies_over_time(pipe_conn, sec: int) -> None:
                while True:
                    x = random.randint(0, self.res[0])
                    y = random.randint(0, self.res[1])
                    time.sleep(sec)
                    print(f'new enemy location {x},{y}')
                    pipe_conn.send((x, y))

            multiprocessing.Process(target=enemies_over_time, args=(into, 2), daemon=True).start()

            return outof

    def start(self):
        pygame.init()
        pygame.display.set_caption("Henlo")
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)

        player = self._add_player()
        self._add_enemy()
        self._load_processors()

        # out_conn = self._enemy_spawn()

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
            # if out_conn.poll():
            #     self._add_enemy(*out_conn.recv())

# todo fix enemy spawn process not exiting on game exit with Escape
