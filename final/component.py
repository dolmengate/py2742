from pygame import sprite, image, transform


class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable(sprite.Sprite):
    def __init__(self, image_loc, posx, posy, scale: float = None, *groups):
        super().__init__(*groups)
        self.image = image.load(image_loc)
        if scale:
            self.image = transform.scale(
                self.image,
                (int(self.image.get_width() * scale), int(self.image.get_height() * scale))
            )
        self.rect = self.image.get_rect()
        self.rect.x = posx
        self.rect.y = posy
        self.w = self.image.get_width()
        self.h = self.image.get_height()
