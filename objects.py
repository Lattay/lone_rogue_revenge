import math
import random

from pygame import transform

from constants import Z, BULLET_DIST
from glob import globs
from entity import Entity
from assets import get_animation, get_sprite


class Destructible(Entity):
    explode = True

    def update(self):
        for sender, msg in self.get_messages():
            if msg == "hit":
                if isinstance(sender, HeroBullet):
                    self.score()
                if self.explode:
                    Explosion(*self.pos, globs.groups.visible)
                self.kill()
                return


class Rock(Destructible):
    radius = Z * 6
    value = 15

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = transform.rotate(
            random.choice(get_animation("rock")),
            random.choice([0, 90, 180, -90]),
        )
        self.size = self.image.get_rect().size


class Mine(Destructible):
    radius = Z * 8
    value = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = get_sprite("mine")
        self.size = self.image.get_rect().size


class Bullet(Destructible):
    radius = Z * 1
    speed = 6.0
    explode = False

    def __init__(self, toward, x, y, *args, **kwargs):
        super().__init__(x, y, self.bullet_group(), *args, **kwargs)
        self.animation = get_animation("bullet")
        self.image = self.animation[0]
        self.anim_counter = 0
        self.size = self.image.get_rect().size
        dx, dy = toward
        n = math.hypot(dx, dy)
        self.dx = dx * self.speed / n
        self.dy = dy * self.speed / n

    def bullet_group(self):
        return globs.groups.enemy_bullet

    def update(self):
        super().update()
        x, y = self.pos
        self.pos = (x + self.dx, y + self.dy)
        self.anim_counter += 1
        self.image = self.animation[(self.anim_counter // 12) % 2]
        if self.anim_counter > BULLET_DIST / self.speed:
            self.kill()


class HeroBullet(Bullet):
    speed = 7.0

    def bullet_group(self):
        return globs.groups.ally_bullet


class Star(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = transform.rotate(
            random.choice(get_animation("star")),
            random.choice([0, 90, 180, -90]),
        )
        self.size = self.image.get_rect().size


class Explosion(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        r = random.choice([0, 90, 180, -90])
        self.animation = [transform.rotate(f, r) for f in get_animation("explosion")]
        self.image = self.animation[0]
        self.size = self.image.get_rect().size
        self.anim_counter = 0

    def update(self):
        self.anim_counter += 1
        a = self.anim_counter // 4
        if a == len(self.animation):
            self.kill()
        else:
            self.image = self.animation[a]
