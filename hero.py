from pygame.time import get_ticks, set_timer

from constants import Z, RESET_PLAYER, LOOSE, DEBUG
from glob import globs

from ship import Ship
from objects import Explosion, HeroBullet


shoot_cooldown = 250


class Hero(Ship):
    sprite_name = "hero"
    speed = 3.2
    radius = Z * 5
    Bullet = HeroBullet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldown = -1
        globs.dead = False

    def update(self):
        # ===== React to messages =====
        for sender, msg in self.get_messages():
            if msg == "hit":
                Explosion(*self.pos, globs.groups.visible)
                globs.dead = True
                self.kill()
                if globs.life > 0:
                    plan_event(RESET_PLAYER, 1000)
                else:
                    plan_event(LOOSE, 1000)
                return

        # ===== React to inputs =====
        act = globs.actions
        # Movement
        d = (act.right - act.left, act.down - act.up)
        if d != (0, 0) and d != self.direction:
            self.direction = d

        self.move_toward(self.direction)

        globs.camera.update(self.pos)

        # Fire
        if act.fire and self.cooldown < get_ticks():
            dx, dy = self.direction
            self.shoot((dx, dy))
            self.shoot((-dx, -dy))
            self.cooldown = get_ticks() + shoot_cooldown

        globs.debug.debug(f"hero pos: ({int(self.pos[0])}, {int(self.pos[1])})")
        super().update()


def plan_event(event_type, t):
    set_timer(event_type, t, True)


def reset():
    globs.life -= 1

    h = Hero(*globs.starter_pos, globs.groups.visible, globs.groups.hero)
    h.look_toward(globs.starter_dir)

    globs.camera = globs.starter_pos


def save_hero_state(globs, hero):
    globs.starter_pos = hero.pos
    globs.starter_dir = hero.direction
