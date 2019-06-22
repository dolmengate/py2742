from pygame import sprite, image, transform


class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable(sprite.Sprite):
    def __init__(self, image_loc, posx, posy, scale: float = 1, *groups):
        super().__init__(*groups)
        self.image = image.load(image_loc)
        self.w = None
        self.h = None
        self.rescale_image(scale)
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy

    def rescale_image(self, sc: float):
        self.image = transform.scale(
            self.image,
            (int(self.image.get_width() * sc), int(self.image.get_height() * sc))
        )
        self.w = self.image.get_width()
        self.h = self.image.get_height()

    def is_bigger_than(self, candidate):
        return self.rect.w > candidate.rect.w


class Consumer:
    def __init__(self, g_rate=0.05):
        self.growth_rate = g_rate
