from pygame.transform import rotate
from pygame.math import Vector2

from constants import W, H, FIELD_SIZE_SPRITE, Z
from utils import wrap
from assets import get_sprite
from glob import globs
from ui import Ui


def setup_in_game_ui(group):
    init_minimap(group)


def init_minimap(group):
    y = Z * 8
    x = W - Z * (4 * 16 + 8)

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
