from pygame.sprite import Sprite
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.mask import Mask

from constants import W, H
from glob import globs
from utils import wrap, Actor


class Entity(Actor, Sprite):
    """An actor that is drawable. It has a position and a size."""

    radius = 0.0
    value = 0

    def __init__(self, x, y, *args, **kwargs):
        Sprite.__init__(self, *args, **kwargs)
        Actor.__init__(self)
        self._mailbox = []
        self.pos = Vector2(x, y)
        self.size = (0, 0)
        self.mask = Mask((int(1.5 * self.radius), int(1.5 * self.radius)), fill=True)

    def score(self):
        globs.score += self.value

    @property
    def rect(self):
        rx, ry = globs.camera
        x, y = self.pos
        wx = wrap(x - rx)
        wy = wrap(y - ry)
        r = Rect((0, 0), self.size)
        r.center = (wx + W / 2, wy + H / 2)
        return r
