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
        self._update_rect()
        self._skip_update = False

    def skip_update(self):
        self._skip_update = True

    def score(self):
        globs.score += self.value

    def up(self):
        pass

    def update(self):
        if not self._skip_update:
            self._handle_messages()
            self.up()
            self._update_rect()

    def _handle_messages(self):
        for sender, msg, data in self.get_messages():
            handler = getattr(self, "on_" + msg, None)
            if handler:
                handler(sender, *data)

    def _update_rect(self):
        rx, ry = globs.camera
        x, y = self.pos
        wx = wrap(x - rx)
        wy = wrap(y - ry)
        self.rect = Rect((0, 0), self.size)
        self.rect.center = (wx + W / 2, wy + H / 2)

    def on_screen(self):
        screen = Rect(0, 0, W, H)
        return screen.colliderect(self.rect)
