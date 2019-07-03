from pygame import sprite, image, transform, Surface


class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class ScoreValue:
    def __init__(self):
        self.points = 1

    def increment(self, value: int):
        self.points += value


class Renderable:
    def __init__(self, siz, posx, posy, color):
        self.image = Surface(siz)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, val):
        self.rect.x = val

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, val):
        self.rect.y = val

    @property
    def w(self):
        return self.rect.right - self.rect.left

    @property
    def h(self):
        return self.rect.bottom - self.rect.top


class MenuItem(Renderable):
    def __init__(self, name, siz, posx, posy):
        Renderable.__init__(self, siz, posx, posy, (255, 255, 255))
        self.name = name


class RenderableActor(Renderable, sprite.Sprite):
    def __init__(self, posx, posy, scale: float = 1, color=(255, 255, 0), *groups):
        sprite.Sprite.__init__(self, *groups)
        Renderable.__init__(self, (20, 20), posx, posy, color)
        self.rescale(scale)

    def rescale(self, scale):
        increment = self.image.get_width() * scale
        self.image = transform.smoothscale(
            self.image, (int(increment), int(increment))
        )
        if hasattr(self, 'rect'):
            self.rect.inflate_ip(increment, increment)

    def increment_size(self, inc):
        self.image = transform.smoothscale(
            self.image,
            (int(self.w + inc), int(self.h + inc))
        )
        self.rect.inflate_ip(inc, inc)

    def is_bigger_than(self, candidate):
        return self.rect.w > candidate.rect.w


class Consumer:
    def __init__(self, g_rate=0.05):
        self.growth_rate = g_rate
