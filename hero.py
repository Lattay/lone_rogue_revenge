from pygame.time import get_ticks

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
        self.direction = (0, 1)
        self.life = 3
        self.cooldown = -1
        self.bullet_group = globs.groups.ally_bullet

    def update(self):
        # ===== React to messages =====
        lf = self.life
        for sender, msg in self.get_messages():
            if msg == "hit":
                if lf == 1:
                    Explosion(*self.pos, globs.groups.visible)
                    self.kill()
                    return
                else:
                    self.life = lf - 1  # prevent multiple shot in same frame

        # ===== React to inputs =====
        act = globs.actions
        # Movement
        d = (act.left - act.right, act.up - act.down)
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

        globs.debug.debug(f"hero life: {self.life}")
