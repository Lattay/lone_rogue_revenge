from pygame.transform import rotate
from pygame.math import Vector2

from constants import W, H, FIELD_SIZE_SPRITE, Z
from utils import wrap
from assets import get_sprite
from glob import globs
from ui import Ui, Manager, UiMaster


def setup_in_game_ui(group):
    mm_x = W - Z * (4 * 16 + 8)
    mm_y = H - Z * (4 * 16 + 8)

    managers = [
        init_minimap(mm_x, mm_y, group),
        init_life_bar(mm_x, mm_y - Z * 16, group),
    ]

    return UiMaster([m for m in managers if m is not None], group)


def init_minimap(x, y, group):

    # center
    cx, cy = x + Z * 2 * 16, y + Z * 2 * 16

    _ = [
        MmCorner(cx, cy, i, group)
        for i in range(4)
    ]
    _ = [
        MmSide(cx, cy, i, j, group)
        for i in range(4)
        for j in range(2)
    ]

    for m in globs.groups.mothership:
        MmMothership(cx, cy, m, group)

    MmHero(cx, cy, globs.groups.hero, group)
    return None


def init_life_bar(x, y, group):
    cx, cy = x + Z * 2 * 16, y + Z * 0.5 * 16

    manager = LifeBar(cx, cy, group)

    return manager


class MmCorner(Ui):
    def __init__(self, x, y, direction, *args, **kwargs):
        dx, dy = Z * (Vector2(-24, -24).rotate(90 * direction) - Vector2(8, 8))
        self.image = rotate(get_sprite("mm_corner"), -90 * direction)
        size = self.image.get_size()
        super().__init__(x + dx, y + dy, *size, *args, **kwargs)


class MmSide(Ui):
    def __init__(self, x, y, direction, i, *args, **kwargs):
        dx, dy = Z * ((Vector2(-24, 0) + (i - 0.5) * Vector2(0, 16)).rotate(90 * direction) - Vector2(8, 8))
        self.image = rotate(get_sprite("mm_side"), -90 * direction)
        size = self.image.get_size()
        super().__init__(x + dx, y + dy, *size, *args, **kwargs)


class MmMothership(Ui):
    def __init__(self, x, y, ship, *args, **kwargs):
        self.ship = ship
        sx, sy = ship.pos
        mx = x + wrap(sx) * 4 / FIELD_SIZE_SPRITE
        my = y + wrap(sy) * 4 / FIELD_SIZE_SPRITE
        self.image = get_sprite("mm_mothership")
        size = self.image.get_size()
        super().__init__(mx, my, *size, *args, **kwargs)

    def up(self):
        if not self.ship.alive():
            self.kill()


class MmHero(Ui):
    def __init__(self, x, y, hero_group, *args, **kwargs):
        self.hero_group = hero_group
        self.center = Vector2(x, y)

        pos = self.get_pos()

        self.image = get_sprite("mm_hero")
        size = self.image.get_size()
        super().__init__(*pos, *size, *args, **kwargs)
        self.rect.center = self.get_pos()

    def up(self):
        self.rect.center = self.get_pos()

    def get_pos(self):
        if self.hero_group.sprite:
            sx, sy = self.hero_group.sprite.pos
        else:
            sx, sy = 0, 0

        return self.center + Vector2(wrap(sx), wrap(sy)) * 4 / FIELD_SIZE_SPRITE


class Life(Ui):
    def __init__(self, x, y, i, n, *args, **kwargs):
        self.center_x = x
        self.image = get_sprite("hero")
        size = self.image.get_size()
        self.i = i
        self.n = n
        super().__init__(0, 0, *size, *args, **kwargs)
        self.rect.centery = y
        self.on_update_pos(None, n)

    def on_die(self, _):
        self.kill()

    def on_update_pos(self, _, n):
        self.n = n
        self.rect.centerx = ((self.i + 0.5) / self.n - 0.5) * Z * 4 * 16 + self.center_x


class LifeBar(Manager):
    def __init__(self, cx, cy, group):
        super().__init__()
        self.lives = []
        self.cx = cx
        self.cy = cy
        self.group = group

    def up(self):
        i = len(self.lives)
        n = globs.life + 1

        if i != n:
            for life in self.lives:
                self.send(life, "update_pos", n)

            while i < n:
                self.lives.append(Life(self.cx, self.cy, i, n, self.group))
                i += 1

            while i > n:
                life = self.lives.pop()
                self.send(life, "die")
                i -= 1
