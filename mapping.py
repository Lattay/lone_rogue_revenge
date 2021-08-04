import pygame


button_map = {
    "fire": 0,
    "ui_select": 0,
    "ui_back": 2,
}

key_map = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "fire": pygame.K_c,
    "ui_select": pygame.K_RETURN,
    "ui_back": pygame.K_BACKSPACE,
    "debug": pygame.K_KP_PLUS,
}


def get_button_mapping(name):
    return button_map[name]


def get_key_mapping(name):
    return key_map[name]


def set_mapping(name, input_spec):
    pass
