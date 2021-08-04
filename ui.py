from pygame.sprite import Sprite
from pygame.rect import Rect

from utils import Actor


class Ui(Actor, Sprite):
    """An actor that is drawable.

    It has a position in the screen referencial and a size.
    """

    def __init__(self, x, y, w, h, *args, **kwargs):
        Sprite.__init__(self, *args, **kwargs)
        Actor.__init__(self)
        self._mailbox = []
        self.rect = Rect(x, y, w, h)
        self.ticks = 0

    def up(self):
        pass

    def update(self):
        self._handle_messages()
        self.up()
        self.ticks += 1
