import random
from bisect import bisect_right as bisect
from enum import Enum
from enum import auto as enum_auto
from math import hypot
from functools import reduce

from pygame.surface import Surface
from pygame.sprite import Sprite, Group
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.time import get_ticks
from pygame.transform import rotate
from pygame import mask

from constants import Z, ROTATIONS
from glob import globs
from entity import Entity
from assets import get_animation, get_sprite
from ship import Ship
from objects import Explosion, Bullet
from utils import dist2, FlexObj, wrap

dirs = [
    (d, Vector2(*d).normalize())
    for d, _ in ROTATIONS
]

obstacle_dist2 = (Z * 24)**2
aggro_dist2 = (12 * Z * 16)**2
abandon_dist2 = (14 * Z * 16)**2
shoot_dist2 = (Z * 5 * 16)**2
despawn_dist2 = 1300**2

satellite_shooting_rate = 2000
fighter_shooting_rate = 1500


class EnemyState(Enum):
    WANDERING = enum_auto()
    FOLLOWING = enum_auto()
    FLEEING = enum_auto()
    AGGRO = enum_auto()


class Enemy(Ship):
    radius = Z * 8
    direction_cooldown_length = 500
    value = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bullet_group = globs.groups.enemy_bullet
        self.direction = (1, 0)
        self.next_change = 0

        self.direction_cooldown = 0

        self.state = EnemyState.WANDERING

    def transit(self, state):
        self.state = state

    def pick_direction(self):
        return (0, 1)

    def want_to_shoot(self):
        return False

    def wander(self):
        return random.choice(dirs)[0]

    def watch_solid(self):
        myp = Vector2(*self.pos)
        d = Vector2(*self.direction)
        positions = [Vector2(*sp.pos) for sp in globs.groups.solid]

        if any(dist2(p, myp) < obstacle_dist2
               for p in positions
               if d.dot(p - myp) > 0):
            d = self.direction
            while d == self.direction:
                d = random.choice(dirs)[0]
            return d
        return None

    def target_hero(self, flee=False):
        hero = globs.groups.hero.sprite
        if hero is None:
            return None
        hx, hy = hero.pos
        mx, my = self.pos
        target = Vector2(wrap(hx - mx), wrap(hy - my))
        if flee:
            target = -target

        return max(dirs, key=lambda d: d[1].dot(target))[0]

    def destroy(self):
        Explosion(*self.pos, globs.groups.visible)
        self.kill()

    def update(self):
        if self.state == EnemyState.FOLLOWING:
            for sender, msg in self.get_messages():
                if msg == "hit":
                    if isinstance(sender, Bullet):
                        self.score()
                    self.destroy()
                    return
                elif msg == "disband":
                    self.transit(EnemyState.FLEEING)
                elif isinstance(msg, tuple):
                    label, data = msg
                    if label == "changedir":
                        self.direction = data
        else:
            if self.state == EnemyState.FLEEING:
                h = globs.groups.hero.sprite
                if h and dist2(h.pos, self.pos) > despawn_dist2:
                    self.kill()
                    return
            tk = get_ticks()
            if tk > self.direction_cooldown:
                d = self.pick_direction()
                if not d:
                    d = self.wander()
                self.direction = d
                self.direction_cooldown = tk + self.direction_cooldown_length

            for sender, msg in self.get_messages():
                if msg == "hit":
                    if isinstance(sender, Bullet):
                        self.score()
                    self.destroy()
                    return

        self.move_toward(self.direction)

        if self.want_to_shoot():
            self.shoot(self.direction)

        self.update_rect()


def leader(Cls):
    def update(self):
        for sender, msg in self.get_messages():
            if msg == "hit":
                squad = self.squad.sprites()
                if squad:
                    for member in self.squad:
                        self.send(member, "disband")
                if isinstance(sender, Bullet):
                    if not squad:
                        self.value = 3 * self.value
                    self.score()
                self.destroy()
                return

        tk = get_ticks()

        if tk > self.direction_cooldown:
            d = self.pick_direction()
            if not d:
                d = self.wander()
            self.direction = d
            self.direction_cooldown = tk + self.direction_cooldown_length
            for member in self.squad:
                self.send(member, ("changedir", d))

        self.move_toward(self.direction)
        self.update_rect()

    def spawn_squad(self):
        for i in range(4):
            pos = self.pos + Vector2(1, 1).rotate(i * 90) * Z * 16
            m = self.Member(*pos, self.squad, *self.groups())
            m.transit(EnemyState.FOLLOWING)

    Cls.update = update
    Cls.value = Cls.value + 50

    def Wrapper(*args, **kwargs):
        instance = Cls(*args, **kwargs)
        instance.squad = Group()
        spawn_squad(instance)
        instance.transit(EnemyState.AGGRO)
        return instance

    return Wrapper


class Cargo(Enemy):
    sprite_name = "cargo"
    speed = 3.5
    value = 50

    def pick_direction(self):
        if self.state == EnemyState.FLEEING:
            return self.watch_solid() or self.target_hero(flee=True)
        else:
            return self.watch_solid() or self.target_hero()


@leader
class CargoLeader(Cargo):
    sprite_name = "cargo_leader"
    Member = Cargo


class Interceptor(Enemy):
    sprite_name = "interceptor"
    speed = 4.5
    value = 80

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_more = 0

    def pick_direction(self):
        hero = globs.groups.hero.sprite

        if hero is not None:
            d = dist2(hero.pos, self.pos)

        if self.state == EnemyState.AGGRO:
            if hero is None or d > abandon_dist2:
                self.transit(EnemyState.WANDERING)
        elif self.state == EnemyState.WANDERING:
            if hero is not None and d < aggro_dist2:
                self.transit(EnemyState.AGGRO)

        if self.state == EnemyState.WANDERING:
            if self.wait_more == 3:  # wait 3 times more if not aggro
                self.wait_more = 0
                return self.watch_solid()
            else:
                self.wait_more += 1
                return None
        elif self.state == EnemyState.FLEEING:
            return self.watch_solid() or self.target_hero(flee=True)
        elif self.state == EnemyState.AGGRO:
            return self.watch_solid() or self.target_hero()


@leader
class InterceptorLeader(Interceptor):
    sprite_name = "interceptor_leader"
    Member = Interceptor


class Fighter(Interceptor):
    sprite_name = "fighter"
    speed = 3.0
    value = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shoot_cooldown = 0

    def want_to_shoot(self):
        if self.state != EnemyState.AGGRO:
            return False
        hero = globs.groups.hero.sprite
        if hero and self.shoot_cooldown < get_ticks():
            self.shoot_cooldown = get_ticks() + fighter_shooting_rate
            return True
        return False


class Mothership(Entity):
    radius = Z * 8
    value = 200

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

        x, y = self.pos
        self.shields = [
            Shield((0, -1), x, y - Z * 15, globs.groups.visible, globs.groups.enemy),
            Shield((0, 1), x, y + Z * 15, globs.groups.visible, globs.groups.enemy),
        ]

    def destroy(self):
        Explosion(*self.pos, globs.groups.visible)
        self.kill()
        for s in self.satellites:
            s.destroy()
        self.shields[0].destroy()
        self.shields[1].destroy()

    def update(self):
        for sender, msg in self.get_messages():
            if msg == "hit":
                if isinstance(sender, Bullet):
                    self.score()
                self.destroy()

        self.tick += 1
        if self.tick >= 40:
            self.tick = 0
            self.i = 1 - self.i
            self.image = self.images[self.i]

        if not self.satellites.sprites():
            self.score()
            self.destroy()
            return

        super().update()


class Shield(Entity):
    def __init__(self, dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rot = 0
        for d, angle in ROTATIONS:
            if d == dir:
                rot = angle
                break
        self.image = rotate(get_sprite("shield"), rot)
        self.size = self.image.get_rect().size
        self.mask = mask.from_surface(self.image)

    def destroy(self):
        Explosion(*self.pos, globs.groups.visible)
        self.kill()

    def collides(self, other):
        d2 = dist2(self.pos, other.pos)
        if d2 > (other.radius + Z * 24)**2:
            return False
        else:
            o_rect = Rect(0, 0, other.radius * 2, other.radius * 2)
            o_rect.center = other.rect.center
            m_rect = self.rect
            if (
                wrap(o_rect.right - m_rect.left) < 0
                or wrap(o_rect.left - m_rect.right) > 0
            ):
                return False
            if (
                wrap(o_rect.bottom - m_rect.top) < 0
                or wrap(o_rect.top - m_rect.bottom) > 0
            ):
                return False
            return True


class Satellites(Entity):
    radius = Z * 8
    value = 80

    def __init__(self, shared, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared = shared
        self.image = get_animation("satellite")[1]
        self.size = self.image.get_rect().size
        self.bullet_group = globs.groups.enemy_bullet

    def update(self):
        for sender, msg in self.get_messages():
            if msg == "hit":
                if isinstance(sender, Bullet):
                    self.score()
                self.destroy()
                return

        hero = globs.groups.hero.sprite
        if hero and dist2(self.pos, hero.pos) < shoot_dist2:
            if self.shared.shoot_cooldown < get_ticks():
                self.shared.shoot_cooldown = get_ticks() + satellite_shooting_rate
                x, y = Vector2(hero.pos) - Vector2(self.pos)
                self.shoot((wrap(x), wrap(y)))

        super().update()

    def destroy(self):
        Explosion(*self.pos, globs.groups.visible)
        self.kill()

    def shoot(self, toward):
        x, y = self.pos
        dx, dy = toward
        n = hypot(dx, dy)
        dx *= 1.5 * self.radius / n
        dy *= 1.5 * self.radius / n

        Bullet(toward, x + dx, y + dy, globs.groups.visible)


class Spawner(Sprite):
    def __init__(self, x, y, *args):
        super().__init__(*args)
        self.pos = (x, y)
        self.image = Surface((0, 0))
        self.rect = Rect(0, 0, 0, 0)

    def update(self):
        r = random.random()
        if r < globs.spawn_proba:
            RandomClass(*self.pos, globs.groups.visible, globs.groups.enemy)


_odds = [
    (10, Cargo),
    (6, Interceptor),
    (4, Fighter),
    (1, InterceptorLeader),
    (2, CargoLeader),
]

_tot = sum(n for n, _ in _odds)
_proba_table = reduce(lambda s, e: s + [e + s[-1]], (n for n, _ in _odds), [0])
_classes = [Cls for _, Cls in _odds]


def RandomClass(*args):
    i = bisect(_proba_table, random.random()) - 1
    return _classes[i](*args)
