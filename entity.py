from pygame.sprite import Sprite
from pygame.rect import Rect
from pygame.math import Vector2

from constants import W, H
from glob import globs
from utils import wrap, Actor


class Entity(Actor, Sprite):
    """An actor that is drawable. It has a position and a size."""

    radius = 0.0

    def __init__(self, x, y, *args, **kwargs):
        Sprite.__init__(self, *args, **kwargs)
        Actor.__init__(self)
        self._mailbox = []
        self.pos = Vector2(x, y)
        self.size = (0, 0)

    @property
    def rect(self):
        rx, ry = globs.camera
        x, y = self.pos
        w, h = self.size
        wx = wrap(x - w / 2 - rx)
        wy = wrap(y - h / 2 - ry)
        return Rect((wx + W / 2, wy + H / 2), self.size)
