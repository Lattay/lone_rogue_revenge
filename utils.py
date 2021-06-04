import math

import pygame
from pygame.surface import Surface

from constants import WHITE, FIELD_SIZE


class Actor:
    """Some object that can send and receive messages"""

    def __init__(self):
        self._mailbox = []

    @staticmethod
    def send_to(dest, msg):
        dest._recv(None, msg)

    def send(self, dest, msg):
        dest._recv(self, msg)

    def _recv(self, sender, msg):
        self._mailbox.append((sender, msg))

    def get_messages(self):
        yield from self._mailbox
        self._mailbox.clear()


def wrap(a):
    return (a + 0.5 * FIELD_SIZE) % FIELD_SIZE - 0.5 * FIELD_SIZE


def dist2(a, b):
    xa, ya = a
    xb, yb = b
    dx = wrap(xa - xb)
    dy = wrap(ya - yb)
    return dx * dx + dy * dy


def dist(a, b):
    xa, ya = a
    xb, yb = b
    dx = wrap(xa - xb)
    dy = wrap(ya - yb)
    return math.hypot(dx, dy)


class FlexObj:
    pass


class Debug:
    def __init__(self):
        super().__init__()
        self.font = None
        self._debug_stack = []
        self._primitives = []
        self._offset = 0

    def draw(self, screen):
        self.init_font()

        for i, (type, data) in enumerate(self._primitives):
            if type == "rect":
                img = Surface(data.size)
                img.fill((255, 30, 100))
                screen.blit(img, data.topleft)

        self._primitives.clear()

        for i, msg in enumerate(self._debug_stack):
            img = self.font.render(msg, True, WHITE)
            screen.blit(img, (20, i * 20))

        self._debug_stack.clear()

    def init_font(self):
        if self.font is None:
            self.font = pygame.font.SysFont(None, 24)

    def debug(self, msg):
        self._debug_stack.append(msg)

    def debug_rect(self, rect):
        self._primitives.append(("rect", rect))
