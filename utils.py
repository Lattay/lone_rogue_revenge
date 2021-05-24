import math

import pygame

from constants import WHITE, FIELD_SIZE
from glob import register_global_singleton


@register_global_singleton
class constants:
    W, H = 1280, 720  # Canvas size
    Z = 4  # Zoom

    FIELD_SIZE_SPRITE = 32
    FIELD_SIZE = FIELD_SIZE_SPRITE * Z * 16
    BULLET_DIST = FIELD_SIZE * 0.45

    DEADZONE = 0.2  # Joystick trigger

    # Colors (palette pink_ink)
    WHITE = (255, 255, 255)
    LIGHT = (254, 108, 144)
    BRIGHT = (208, 55, 145)
    MID = (135, 40, 106)
    DARK = (69, 36, 89)
    BLACK = (38, 13, 52)

    ROTATIONS = [
        ((0, 1), 0),
        ((1, 1), 45),
        ((1, 0), 90),
        ((1, -1), 135),
        ((0, -1), 180),
        ((-1, -1), -135),
        ((-1, 0), -90),
        ((-1, 1), -45),
    ]

    SQRT_2 = 2 ** 0.5

    DEBUG = True


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


@register_global_singleton
class debug:
    def __init__(self):
        super().__init__()
        self.font = None
        self._debug_stack = []
        self._offset = 0

    def draw(self, screen):
        self.init_font()
        for i, msg in enumerate(self._debug_stack):
            img = self.font.render(msg, True, WHITE)
            screen.blit(img, (20, i * 20))

        self._debug_stack.clear()

    def init_font(self):
        if self.font is None:
            self.font = pygame.font.SysFont(None, 24)

    def debug(self, msg):
        self._debug_stack.append(msg)
