import pygame
from pygame.math import Vector2


from constants import (
    DEADZONE, BLACK, DEBUG, RESET_PLAYER, LOOSE,
    LOOSE_STATE, NEXT_LEVEL_STATE,
)
from glob import globs

from mapping import get_button_mapping, get_key_mapping

from utils import FlexObj, Debug
from action import ActionStates, EventHandler
from collision_handler import CollisionHandler
from hero import reset, save_hero_state

from pause import setup_pause_screen


from scene_tools import load_level

from in_game_ui import setup_in_game_ui

max_spawn_rate = 0.015

handler = EventHandler()


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


@handler.register(pygame.JOYBUTTONDOWN, "fire")
def joy_fire(_, event):
    return event.button == get_button_mapping("fire")


@handler.register(pygame.JOYBUTTONDOWN, "ui_select")
def joy_select(_, event):
    return event.button == get_button_mapping("ui_select")


@handler.register(pygame.JOYBUTTONDOWN, "ui_back")
def joy_back(_, event):
    return event.button == get_button_mapping("ui_back")


@handler.register(None, "up")
def key_up(_):
    return pygame.key.get_pressed()[get_key_mapping("up")]


@handler.register(None, "down")
def key_down(_):
    return pygame.key.get_pressed()[get_key_mapping("down")]


@handler.register(None, "left")
def key_left(_):
    return pygame.key.get_pressed()[get_key_mapping("left")]


@handler.register(None, "right")
def key_right(_):
    return pygame.key.get_pressed()[get_key_mapping("right")]


@handler.register(pygame.KEYDOWN, "fire")
def key_fire(_, event):
    return event.key == get_key_mapping("fire")


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


@handler.register(RESET_PLAYER, "reload")
def on_reload(_, __):
    return True


@handler.register(LOOSE, "loose")
def on_loose(_, __):
    return True


def run_level(game_state, screen, level_name):
    globs.clear()

    globs.score = game_state['score']
    globs.life = game_state['life']

    globs.joysticks = [
        pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())
    ]

    clock = pygame.time.Clock()

    globs.camera = Vector2(0, 0)

    globs.groups = FlexObj()
    globs.groups.visible = visible = pygame.sprite.Group()
    globs.groups.ui = ui = pygame.sprite.Group()
    globs.groups.pause = pause = pygame.sprite.Group()

    globs.groups.ally_bullet = ally_bullet = pygame.sprite.Group()
    globs.groups.enemy_bullet = enemy_bullet = pygame.sprite.Group()
    globs.groups.enemy = enemy = pygame.sprite.Group()
    globs.groups.solid = solid = pygame.sprite.Group()
    globs.groups.hero = hero = pygame.sprite.GroupSingle()
    globs.groups.mothership = mothership = pygame.sprite.Group()

    globs.spawn_proba = max_spawn_rate

    globs.pause = False

    globs.debug = db = Debug()
    load_level(level_name, visible, ally_bullet,
               enemy_bullet, enemy, solid, hero, mothership)

    setup_pause_screen(pause)

    ui_master = setup_in_game_ui(ui)

    save_hero_state(globs, hero.sprite)

    collision_handlers = [
        CollisionHandler(hero, enemy, solid, enemy_bullet),
        CollisionHandler(enemy, solid, enemy_bullet, ally_bullet),
        CollisionHandler(enemy_bullet, solid),
        CollisionHandler(ally_bullet, solid),
    ]

    next_state = None

    while True:
        # handle events
        actions = ActionStates()
        handler.handle_events(actions)
        globs.actions = actions
        db.debug(f"FPS: {clock.get_fps()}")

        if actions.quit:
            break

        if actions.reload:
            reset()

        if actions.ui_select:
            globs.pause = not globs.pause

        if DEBUG and actions.debug:
            globs.life += 1

        elif actions.loose:
            next_state = LOOSE_STATE
            print("You lost !")
            break
        else:
            if not mothership.sprites():
                next_state = NEXT_LEVEL_STATE
                print("Next level !")
                break

        for h in collision_handlers:
            h.handle_collisions()

        if not globs.pause:
            # update
            visible.update()
            globs.spawn_proba = max_spawn_rate / (1 + len(enemy.sprites()))

            ui_master.update()

        # draw
        screen.fill(BLACK)

        visible.draw(screen)
        ui.draw(screen)

        if globs.pause:
            pause.draw(screen)

        globs.debug.debug(f"hero life: {globs.life}")
        globs.debug.debug(f"score: {globs.score}")

        if DEBUG:
            db.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    game_state['score'] = globs.score
    game_state['life'] = globs.life
    return next_state
