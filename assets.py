import pygame
from pygame.rect import Rect
from constants import Z


_sheet = None
sprite_sheet = None
animated = None


def load_assets():
    global _sheet, sprite_sheet, animated
    _sheet = pygame.image.load("assets/space_ships.png").convert_alpha()
    sprite_sheet = {
        "mine": scale_up(_sheet.subsurface(Rect(48, 0, 16, 16))),
        "hero": scale_up(_sheet.subsurface(Rect(0, 16, 16, 16))),
        "cargo": scale_up(_sheet.subsurface(Rect(0, 0, 16, 16))),
        "cargo_leader": scale_up(_sheet.subsurface(Rect(64, 0, 16, 16))),
        "interceptor": scale_up(_sheet.subsurface(Rect(16, 0, 16, 16))),
        "interceptor_leader": scale_up(_sheet.subsurface(Rect(80, 0, 16, 16))),
        "fighter": scale_up(_sheet.subsurface(Rect(32, 0, 16, 16))),
        "fighter_leader": scale_up(_sheet.subsurface(Rect(96, 0, 16, 16))),
        "shield": scale_up(_sheet.subsurface(Rect(0, 80, 48, 16))),
        # UI
        "mm_hero": scale_up(_sheet.subsurface(Rect(0, 112, 4, 4))),
        "mm_mothership": scale_up(_sheet.subsurface(Rect(0, 116, 4, 4))),
        "mm_corner": scale_up(_sheet.subsurface(Rect(16, 112, 16, 16))),
        "mm_side": scale_up(_sheet.subsurface(Rect(32, 112, 16, 16))),
        "ui_pause": scale_up(_sheet.subsurface(Rect(0, 176, 48, 16))),
        "ui_play": scale_up(_sheet.subsurface(Rect(0, 128, 32, 16))),
        "ui_exit": scale_up(_sheet.subsurface(Rect(32, 128, 32, 16))),
        "ui_about": scale_up(_sheet.subsurface(Rect(0, 160, 32, 16))),
        "title": scale_up(_sheet.subsurface(Rect(48, 80, 132, 28))),
    }

    animated = {
        "satellite": [
            scale_up(_sheet.subsurface(Rect(64 + i * 16, 48, 16, 16)))
            for i in range(3)
        ],
        "explosion": [
            scale_up(_sheet.subsurface(Rect(i * 16, 64, 16, 16)))
            for i in range(8)
        ],
        "star": [
            scale_up(_sheet.subsurface(Rect(32 + i * 16, 32, 16, 16)))
            for i in range(6)
        ],
        "rock": [
            scale_up(_sheet.subsurface(Rect(48 + 16 * i, 16, 16, 16)))
            for i in range(2)
        ],
        "bullet": [
            scale_up(_sheet.subsurface(Rect(32 + 16 * i, 48, 16, 16)))
            for i in range(2)
        ],
        "mothership": [
            scale_up(_sheet.subsurface(Rect(16 * i, 96, 16, 16)))
            for i in range(2)
        ],
    }


def get_sprite(name):
    return sprite_sheet[name]


def get_animation(name):
    return animated[name]


def scale_up(surf):
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (Z * w, Z * h))


def get_all_assets():
    d = {k: "static" for k in sprite_sheet}
    d.update({k: "anim" for k in animated})
    return d
