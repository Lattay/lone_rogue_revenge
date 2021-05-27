import random
from math import hypot

from pygame import math, time
from pygame.surface import Surface
from pygame.sprite import Sprite, Group
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.time import get_ticks

from constants import Z, ROTATIONS
from glob import globs
from entity import Entity
from assets import get_animation
from ship import Ship
from objects import Explosion, Bullet
from utils import dist2, FlexObj

dirs = [
    (d, math.Vector2(*d).normalize())
    for d, _ in ROTATIONS
]

obstacle_dist2 = (Z * 24)**2
aggro_dist2 = (12 * Z * 16)**2
abandon_dist2 = (14 * Z * 16)**2
shoot_dist2 = (Z * 5 * 16)**2

satellite_shooting_rate = 2000
destroyer_shooting_rate = 1500


class Enemy(Ship):
    radius = Z * 8
    direction_cooldown_length = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bullet_group = globs.groups.enemy_bullet
        self.direction = (1, 0)
        self.next_change = 0

        self.direction_cooldown = 0

    def pick_direction(self):
        return (0, 1)

    def want_to_shoot(self):
        return False

    def wander(self):
        return random.choice(dirs)[0]

    def watch_solid(self):
        myp = math.Vector2(*self.pos)
        d = math.Vector2(*self.direction)
        positions = [math.Vector2(*sp.pos) for sp in globs.groups.solid]

        if any(dist2(p, myp) < obstacle_dist2
               for p in positions
               if d.dot(p - myp) > 0):
            d = self.direction
            while d == self.direction:
                d = random.choice(dirs)[0]
            return d
        return None

    def target_hero(self):
        hero = globs.groups.hero.sprite
        if hero is None:
            return None
        hx, hy = hero.pos
        mx, my = self.pos
        target = math.Vector2(hx - mx, hy - my)

        return max(dirs, key=lambda d: d[1].dot(target))[0]

    def update(self):
        tk = time.get_ticks()
        if tk > self.direction_cooldown:
            d = self.pick_direction()
            if not d:
                d = self.wander()
            self.direction = d
            self.direction_cooldown = tk + self.direction_cooldown_length
        self.move_toward(self.direction)
        for sender, msg in self.get_messages():
            if msg == "hit":
                Explosion(*self.pos, globs.groups.visible)
                self.kill()
                return

        if self.want_to_shoot():
            self.shoot(self.direction)


class Tank(Enemy):
    sprite_name = "tank"
    speed = 3.1

    def pick_direction(self):
        return self.watch_solid() or self.target_hero()


class Hunter(Enemy):
    sprite_name = "hunter"
    speed = 5.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aggro = False
        self.wait_more = 0

    def pick_direction(self):
        hero = globs.groups.hero.sprite

        if hero is not None:
            d = dist2(hero.pos, self.pos)

        if self.aggro:
            self.aggro = (hero is not None) and (d < abandon_dist2)
        else:
            self.aggro = (hero is not None) and (d < aggro_dist2)

        if not self.aggro:
            if self.wait_more == 3:  # wait 3 times more if not aggro
                self.wait_more = 0
                return self.watch_solid()
            else:
                self.wait_more += 1
                return None
        else:
            return self.watch_solid() or self.target_hero()


class Destroyer(Hunter):
    sprite_name = "destroyer"
    speed = 3.5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shoot_cooldown = 0

    def want_to_shoot(self):
        hero = globs.groups.hero.sprite
        if hero and self.aggro and self.shoot_cooldown < get_ticks():
            self.shoot_cooldown = get_ticks() + destroyer_shooting_rate
            return True
        return False


class Mothership(Entity):
    radius = Z * 22

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images = get_animation("mothership")
        self.image = self.images[0]
        self.size = self.image.get_rect().size
        self.i = 0
        self.tick = 0
        self.satellites = Group()
        r = Z * 32
        p = Vector2(*self.pos)
        shared = FlexObj()
        shared.shoot_cooldown = 0
        for i in range(6):
            d = Vector2(0, 1).rotate(60 * i)
            x, y = p + d * r
            Satellites(shared, x, y, globs.groups.visible, globs.groups.enemy, self.satellites)

    def update(self):
        self.tick += 1
        if self.tick >= 40:
            self.tick = 0
            self.i = 1 - self.i
            self.image = self.images[self.i]

        if not self.satellites.sprites():
            Explosion(*self.pos, globs.groups.visible)
            self.kill()
            return


class Satellites(Entity):
    radius = Z * 8

    def __init__(self, shared, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared = shared
        self.image = get_animation("satellite")[1]
        self.size = self.image.get_rect().size
        self.bullet_group = globs.groups.enemy_bullet

    def update(self):
        for sender, msg in self.get_messages():
            if msg == "hit":
                Explosion(*self.pos, globs.groups.visible)
                self.kill()
                return

        hero = globs.groups.hero.sprite
        if hero and dist2(self.pos, hero.pos) < shoot_dist2:
            if self.shared.shoot_cooldown < get_ticks():
                self.shared.shoot_cooldown = get_ticks() + satellite_shooting_rate
                self.shoot(Vector2(hero.pos) - Vector2(self.pos))

    def shoot(self, toward):
        x, y = self.pos
        dx, dy = toward
        n = hypot(dx, dy)
        dx *= 1.5 * self.radius / n
        dy *= 1.5 * self.radius / n

        Bullet(toward, x + dx, y + dy, globs.groups.visible, self.bullet_group)


class Spawner(Sprite):
    def __init__(self, x, y, *args):
        super().__init__(*args)
        self.pos = (x, y)
        self.image = Surface((0, 0))
        self.rect = Rect(0, 0, 0, 0)

    def update(self):
        r = random.random()
        if r < globs.spawn_proba:
            r /= globs.spawn_proba
            if r < 0.2:
                Hunter(*self.pos, globs.groups.visible, globs.groups.enemy)
            elif r < 0.4:
                Destroyer(*self.pos, globs.groups.visible, globs.groups.enemy)
            else:
                Tank(*self.pos, globs.groups.visible, globs.groups.enemy)
