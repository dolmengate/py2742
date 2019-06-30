from pygame import sprite, image, transform, Surface


class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable(sprite.Sprite):
    def __init__(self, image_loc, posx, posy, scale: float = 1, *groups):
        super().__init__(*groups)
        # self.image = image.load(image_loc)  # surface
        self.image = Surface((20, 20))
        self.image.fill((255, 255, 0))
        self.rescale(scale)
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy
        self.toggle = True

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
