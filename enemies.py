from pygame import math

from constants import Z, ROTATIONS
from glob import globs
from entity import Entity
from assets import get_sprite
from ship import Ship
from objects import Explosion

dirs = [
    (d, math.Vector2(*d).normalize())
    for d, _ in ROTATIONS
]


class Enemy(Ship):
    radius = Z * 8

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bullet_group = globs.groups.enemy_bullet

    def update(self):
        self.move_toward(self.pick_direction())
        for sender, msg in self.get_messages():
            if msg == "hit":
                Explosion(*self.pos, globs.groups.visible)
                self.kill()
                return


class Tank(Enemy):
    sprite_name = "tank"
    speed = 3.1

    def pick_direction(self):
        hero = globs.groups.hero.sprite
        hx, hy = hero.pos
        mx, my = self.pos
        target = math.Vector2(hx - mx, hy - my)

        return min(dirs, key=lambda d: d[1].dot(target))[0]


class Destroyer(Enemy):
    sprite_name = "destroyer"
    speed = 3.5

    def pick_direction(self):
        hero = globs.groups.hero.sprite
        hx, hy = hero.pos
        mx, my = self.pos
        target = math.Vector2(hx - mx, hy - my)

        return min(dirs, key=lambda d: d[1].dot(target))[0]


class Hunter(Enemy):
    sprite_name = "hunter"
    speed = 5.0

    def pick_direction(self):
        hero = globs.groups.hero.sprite
        hx, hy = hero.pos
        mx, my = self.pos
        target = math.Vector2(hx - mx, hy - my)

        return min(dirs, key=lambda d: d[1].dot(target))[0]


class Mothership(Entity):
    radius = Z * 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = get_sprite("mothership")
        self.size = self.image.get_rect().size
