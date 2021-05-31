import pygame
from pygame.rect import Rect
from constants import Z


def scale_up(surf):
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (Z * w, Z * h))


_sheet = pygame.image.load("assets/space_ships.png")
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
