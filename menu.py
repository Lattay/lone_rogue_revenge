import pygame

from constants import (
    DEADZONE, DEBUG, BLACK
)

from glob import globs

from mapping import get_button_mapping, get_key_mapping
from action import ActionStates, EventHandler

from utils import FlexObj, Debug

from main_menu import setup_main_menu


menu_table = {
    "main": setup_main_menu,
}

handler = EventHandler()


# FIXME Add a cooldown or something similar joysticks to prevent super speed menu scrolling
# Joystick controls
@handler.register(None, "up")
def joy_up(_):
    return any(j.get_axis(1) < -DEADZONE for j in globs.joysticks)


@handler.register(None, "down")
def joy_down(_):
    return any(j.get_axis(1) > DEADZONE for j in globs.joysticks)


@handler.register(None, "left")
def joy_left(_):
    return any(j.get_axis(0) < -DEADZONE for j in globs.joysticks)


@handler.register(None, "right")
def joy_right(_):
    return any(j.get_axis(0) > DEADZONE for j in globs.joysticks)


@handler.register(pygame.JOYBUTTONDOWN, "ui_select")
def joy_select(_, event):
    return event.button == get_button_mapping("ui_select")


@handler.register(pygame.JOYBUTTONDOWN, "ui_back")
def joy_back(_, event):
    return event.button == get_button_mapping("ui_back")


@handler.register(pygame.KEYDOWN, "up")
def key_up(_, event):
    return event.key == get_key_mapping("up")


@handler.register(pygame.KEYDOWN, "down")
def key_down(_, event):
    return event.key == get_key_mapping("down")


@handler.register(pygame.KEYDOWN, "left")
def key_left(_, event):
    return event.key == get_key_mapping("left")


@handler.register(pygame.KEYDOWN, "right")
def key_right(_, event):
    return event.key == get_key_mapping("right")


@handler.register(pygame.KEYDOWN, "ui_select")
def key_select(_, event):
    return event.key == get_key_mapping("ui_select")


@handler.register(pygame.KEYDOWN, "ui_back")
def key_back(_, event):
    return event.key == get_key_mapping("ui_back")


@handler.register(pygame.KEYDOWN, "debug")
def key_debug(_, event):
    return event.key == get_key_mapping("debug")


@handler.register(pygame.QUIT, "quit")
def on_quit(_, __):
    return True


def run_menu(screen, name):
    """ Return either None to quit or an integer to jump to a level.
    """

    setup = menu_table[name]

    globs.clear()

    globs.joysticks = [
        pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())
    ]

    globs.debug = db = Debug()

    globs.groups = FlexObj()
    globs.groups.ui = ui = pygame.sprite.Group()

    clock = pygame.time.Clock()

    ui_master = setup(ui)

    globs.next_level = None

    while True:
        actions = ActionStates()
        handler.handle_events(actions)
        globs.actions = actions
        db.debug(f"FPS: {clock.get_fps()}")

        if actions.quit:
            break

        ui_master.update()

        screen.fill(BLACK)
        ui.draw(screen)

        if DEBUG:
            db.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    return globs.next_level
