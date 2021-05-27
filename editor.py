import sys
import json

import pygame
from pygame import transform
from pygame.rect import Rect
from pygame.surface import Surface

from constants import W, H, BLACK
from glob import globs
from action import ActionStates, handler
from assets import get_animation, get_sprite, sprite_sheet, animated
from entity import Entity
from utils import wrap


key_map = {
    "turn": pygame.K_r,
    "up": pygame.K_z,
    "down": pygame.K_s,
    "left": pygame.K_q,
    "right": pygame.K_d,
    "new": pygame.K_SPACE,
    "save": pygame.K_RETURN,
}


@handler.register(pygame.MOUSEBUTTONDOWN, "left_c")
def lc(_, event):
    return event.button == pygame.BUTTON_LEFT


@handler.register(pygame.MOUSEBUTTONUP, "left_r")
def lr(_, event):
    return event.button == pygame.BUTTON_LEFT


@handler.register(pygame.MOUSEBUTTONDOWN, "right_c")
def rc(_, event):
    return event.button == pygame.BUTTON_RIGHT


# @handler.register(pygame.MOUSEBUTTONUP, "right_r")
# def rr(_, event):
#     return event.button == pygame.BUTTON_RIGHT


@handler.register(pygame.MOUSEBUTTONDOWN, "next_sprite")
def wheelup(_, event):
    return event.button == pygame.BUTTON_WHEELUP


@handler.register(pygame.MOUSEBUTTONDOWN, "prev_sprite")
def wheeldown(_, event):
    return event.button == pygame.BUTTON_WHEELDOWN


@handler.register(pygame.KEYDOWN, "turn")
def key_turn(_, event):
    return event.key == key_map["turn"]


@handler.register(pygame.KEYDOWN, "new")
def key_new(_, event):
    return event.key == key_map["new"]


@handler.register(pygame.KEYDOWN, "save")
def key_save(_, event):
    return event.key == key_map["save"]


@handler.register(None, "up")
def key_up(_):
    return pygame.key.get_pressed()[key_map["up"]]


@handler.register(None, "down")
def key_down(_):
    return pygame.key.get_pressed()[key_map["down"]]


@handler.register(None, "left")
def key_left(_):
    return pygame.key.get_pressed()[key_map["left"]]


@handler.register(None, "right")
def key_right(_):
    return pygame.key.get_pressed()[key_map["right"]]


@handler.register(pygame.QUIT, "quit")
def on_quit(_, __):
    return True


def main(filename):
    pygame.init()
    screen = pygame.display.set_mode((W, H), flags=pygame.RESIZABLE | pygame.SCALED)
    clock = pygame.time.Clock()

    db = globs.debug

    globs.camera = (0, 0)

    visible = pygame.sprite.Group()
    globs.group_all = visible

    world = World(filename)

    running = True
    while running:
        globs.actions = actions = ActionStates()
        handler.handle_events(actions)
        running = not actions.quit
        db.debug(f"FPS: {clock.get_fps()}")

        world.update()

        visible.update()

        # draw
        screen.fill(BLACK)

        visible.draw(screen)

        db.draw(screen)

        world.draw_ui(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


dirs = ["up", "left", "down", "right"]


class World:
    def __init__(self, filename):
        self.filename = filename
        self.dir = 0
        self.sprites = get_all_assets()
        self.sprite = self.sprites[0]
        self.sprite_index = 0
        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return

        for sprite, lst in data.items():
            for pos, rot in lst:
                self.spawn(sprite, pos, rot)

    def spawn(self, sprite, pos, rot):
        Anchor(sprite, rot, *pos, globs.group_all)

    def update(self):
        act = globs.actions

        if act.turn:
            self.dir = (self.dir + 1) % len(dirs)

        if act.new:
            self.spawn(self.sprite, globs.camera, self.dir * 90)

        if act.save:
            dump(sp for sp in globs.group_all if isinstance(sp, Anchor))

        if act.next_sprite:
            self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
            self.sprite = self.sprites[self.sprite_index]
        if act.prev_sprite:
            self.sprite_index = (self.sprite_index - 1) % len(self.sprites)
            self.sprite = self.sprites[self.sprite_index]

        dx = act.right - act.left
        dy = act.down - act.up

        x, y = globs.camera
        globs.camera = (x + 5 * dx, y + 5 * dy)

        globs.debug.debug(f"pos: ({int(x + dx)}, {int(y + dy)})")
        globs.debug.debug(f"dir: {dirs[self.dir]}")
        globs.debug.debug(f"current sprite: {self.sprite}")

    def draw_ui(self, screen):
        if get_type_asset(self.sprite) == "anim":
            im = get_animation(self.sprite)[0]
        else:
            im = get_sprite(self.sprite)

        r = im.get_rect()
        w, h = r.size
        r = Rect(W - w - 20, 20, w, h)
        screen.blit(im, r)


class Anchor(Entity):
    def __init__(self, sprite, rot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grabbed = False
        self.prev_pos = (0, 0)
        self.rot = rot

        self.sprite = sprite

        if get_type_asset(sprite) == "anim":
            self.anim = True
            self.images = [
                transform.rotate(f, rot)
                for f in get_animation(sprite)
            ]
            self.image = self.images[0]
            self.anim_counter = 0
        else:
            self.anim = False
            self.image = transform.rotate(get_sprite(sprite), rot)

        self.size = self.image.get_rect().size

    def clicked(self, left=True):
        if left:
            act = globs.actions.left_c
        else:
            act = globs.actions.right_c
        return act and self.rect.collidepoint(pygame.mouse.get_pos())

    def update(self):
        if self.grabbed:
            if globs.actions.left_r:
                self.grabbed = False
            else:
                x, y = self.pos
                px, py = self.prev_pos
                nx, ny = pygame.mouse.get_pos()
                self.prev_pos = (nx, ny)
                self.pos = (x + nx - px, y + ny - py)
        elif self.clicked(left=True):
            self.grabbed = True
            self.prev_pos = pygame.mouse.get_pos()

        if self.anim:
            self.anim_counter += 1
            self.image = self.images[(self.anim_counter // 6) % len(self.images)]

        if self.clicked(left=False):
            self.kill()


def get_type_asset(name):
    if name in animated:
        return "anim"
    else:
        return "static"


def get_all_assets():
    return list(sprite_sheet) + list(animated)


def dump(anchors):
    d = {}

    for a in anchors:
        x, y = a.pos
        d.setdefault(a.sprite, []).append(
            ((wrap(x), wrap(y)), a.rot)
        )

    with open("level_dump.json", "w") as f:
        json.dump(d, f)


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "level_dump.json"
    main(filepath)
