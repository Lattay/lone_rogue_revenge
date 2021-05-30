import json
import random

from constants import Z, FIELD_SIZE_SPRITE
from objects import Star

from hero import Hero
from enemies import Cargo, Fighter, Interceptor, Mothership, Spawner
from objects import Rock, Mine

HALF_FIELD_SPRITE = FIELD_SIZE_SPRITE // 2


def gen_stars(*groups):
    for i in range(-HALF_FIELD_SPRITE, HALF_FIELD_SPRITE):
        for j in range(-HALF_FIELD_SPRITE, HALF_FIELD_SPRITE):
            if random.random() < 0.1:
                Star(i * 16 * Z, j * 16 * Z, *groups)


def load_level(name, visible, ally_bullet, enemy_bullet, enemy, solid, hero):
    simples = {
        "rock": (Rock, False, (visible, solid)),
        "mine": (Mine, False, (visible, solid)),
        "cargo": (Cargo, True, (visible, enemy)),
        "fighter": (Fighter, True, (visible, enemy)),
        "interceptor": (Interceptor, True, (visible, enemy)),
    }

    with open(name) as f:
        data = json.load(f)

    gen_stars(visible)

    for name, instances in data.items():
        if name == "bullet":
            for pos, _ in instances:
                Spawner(*pos, visible)
        elif name == "hero":
            (pos, rot), *_ = instances
            h = Hero(*pos, visible, hero)
            h.set_rot(rot)

        elif name in simples:
            Cls, use_rot, groups = simples[name]
            for pos, rot in instances:
                obj = Cls(*pos, *groups)
                if use_rot:
                    obj.set_rot(rot)
        elif name == "mothership":
            for pos, _ in instances:
                Mothership(*pos, visible, enemy)
