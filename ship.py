import math

from pygame.transform import rotate
from pygame.math import Vector2

from constants import ROTATIONS, SQRT_2

from entity import Entity
from assets import get_sprite
from glob import globs
from objects import Bullet

directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]


class Ship(Entity):
    Bullet = Bullet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        im = get_sprite(self.sprite_name)
        self.images = {d: rotate(im, angle) for d, angle in ROTATIONS}
        self.image = im
        self.size = self.image.get_rect().size

        self.shift_0 = self.image.get_rect().width / 2
        self.shift_45 = self.shift_0 * SQRT_2

        self.shift = self.shift_0
        self.direction = (0, 1)

    def look_toward(self, direction):
        self.direction = direction
        self.image = self.images[direction]

        dx, dy = direction

        if abs(dx) + abs(dy) == 2:
            self.shift = self.shift_45
            self.size = self.image.get_rect().size
            dx /= SQRT_2
            dy /= SQRT_2
        else:
            self.shift = self.shift_0
            self.size = self.image.get_rect().size

    def move_toward(self, direction):
        self.look_toward(direction)
        x, y = self.pos
        dx, dy = direction
        if abs(dx) + abs(dy) == 2:
            dx /= SQRT_2
            dy /= SQRT_2
        self.pos = Vector2(x + dx * self.speed, y + dy * self.speed)

    def shoot(self, toward):
        x, y = self.pos
        dx, dy = toward
        n = math.hypot(dx, dy)
        dx *= 1.5 * self.radius / n
        dy *= 1.5 * self.radius / n

        self.Bullet(toward, x + dx, y + dy, globs.groups.visible)

    def set_rot(self, rot):
        """ Change the initial rotation.

        :param rot: Angle in degree, must be a multiple of 90
        """
        r = (int(rot) // 90 % 4)
        self.look_toward(directions[r])
