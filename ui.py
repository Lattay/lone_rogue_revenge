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


class Manager(Actor):
    def up(self):
        pass

    def update(self):
        self._handle_messages()
        self.up()


class UiMaster(Manager):
    def __init__(self, children, group):
        self.group = group
        self.children = children

    def update(self):
        self.group.update()

        for m in self.children:
            m.update()
