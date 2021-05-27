from pygame.locals import USEREVENT
from pygame.time import get_ticks, set_timer

from constants import Z
from glob import globs

from ship import Ship
from objects import Explosion


class Hero(Ship):
    sprite_name = "hero"
    speed = 3.0
    radius = Z * 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldown = -1
        self.bullet_group = globs.groups.ally_bullet
        globs.dead = False

    def update(self):
        # ===== React to messages =====
        for sender, msg in self.get_messages():
            if msg == "hit":
                Explosion(*self.pos, globs.groups.visible)
                globs.dead = True
                self.kill()
                if globs.life > 0:
                    plan_event(USEREVENT, 1000)
                return

        # ===== React to inputs =====
        act = globs.actions
        # Movement
        d = (act.right - act.left, act.down - act.up)
        if d != (0, 0) and d != self.direction:
            self.direction = d
        self.move_toward(self.direction)
        globs.camera = self.pos

        # Fire
        if act.fire and self.cooldown < get_ticks():
            dx, dy = self.direction
            self.shoot((dx, dy))
            self.shoot((-dx, -dy))
            self.cooldown = get_ticks() + 300

        globs.debug.debug(f"hero pos: ({int(self.pos[0])}, {int(self.pos[1])})")


def plan_event(event_type, t):
    set_timer(event_type, t, True)


def reset():
    globs.life -= 1

    Hero(*globs.starter_pos, globs.groups.visible, globs.groups.hero)
    globs.camera = globs.starter_pos
