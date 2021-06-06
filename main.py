import pygame
from pygame.math import Vector2

from constants import (
    W, H, DEADZONE, BLACK, DEBUG, RESET_PLAYER, LOOSE,
    LOOSE_STATE, NEXT_LEVEL_STATE, START_STATE, WIN_STATE,
    LEVELS
)
from glob import globs

from assets import load_assets
from utils import FlexObj, Debug
from action import ActionStates, handler
from collision_handler import CollisionHandler
from hero import reset, save_hero_state

from scene_tools import load_level

max_spawn_rate = 0.015

button_map = {
    "fire": 0,
    "ui_select": 1,
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
}


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
    return event.button == button_map["fire"]


@handler.register(pygame.JOYBUTTONDOWN, "ui_select")
def joy_select(_, event):
    return event.button == button_map["ui_select"]


@handler.register(pygame.JOYBUTTONDOWN, "ui_back")
def joy_back(_, event):
    return event.button == button_map["ui_back"]


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


@handler.register(pygame.KEYDOWN, "fire")
def key_fire(_, event):
    return event.key == key_map["fire"]


@handler.register(pygame.KEYDOWN, "ui_select")
def key_select(_, event):
    return event.key == key_map["ui_select"]


@handler.register(pygame.KEYDOWN, "ui_back")
def key_back(_, event):
    return event.key == key_map["ui_back"]


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

    visible = pygame.sprite.Group()
    ally_bullet = pygame.sprite.Group()
    enemy_bullet = pygame.sprite.Group()
    enemy = pygame.sprite.Group()
    solid = pygame.sprite.Group()
    mothership = pygame.sprite.Group()
    hero = pygame.sprite.GroupSingle()
    globs.groups = FlexObj()
    globs.groups.visible = visible
    globs.groups.ally_bullet = ally_bullet
    globs.groups.enemy_bullet = enemy_bullet
    globs.groups.enemy = enemy
    globs.groups.solid = solid
    globs.groups.hero = hero
    globs.groups.mothership = mothership

    globs.spawn_proba = max_spawn_rate

    globs.debug = db = Debug()
    load_level(level_name, visible, ally_bullet,
               enemy_bullet, enemy, solid, hero, mothership)

    save_hero_state(globs, hero.sprite)

    collision_handlers = [
        CollisionHandler(hero, enemy, solid, enemy_bullet),
        CollisionHandler(enemy_bullet, solid, enemy),
        CollisionHandler(ally_bullet, hero, solid, enemy),
        CollisionHandler(enemy, solid),
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

        # update
        visible.update()
        globs.spawn_proba = max_spawn_rate / (1 + len(enemy.sprites()))

        # draw
        screen.fill(BLACK)

        visible.draw(screen)
        globs.debug.debug(f"hero life: {globs.life}")
        globs.debug.debug(f"score: {globs.score}")

        if DEBUG:
            db.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    game_state['score'] = globs.score
    game_state['life'] = globs.life
    return next_state


def main():
    pygame.init()
    pygame.joystick.init()

    screen = pygame.display.set_mode((W, H), flags=pygame.RESIZABLE | pygame.SCALED)
    load_assets()

    game_state = {
        'score': 0,
        'life': 2,
    }

    level = 0

    state = START_STATE
    while state and state != LOOSE_STATE:
        if state == START_STATE:
            level_name = LEVELS[level]
            state = run_level(game_state, screen, level_name)
        elif state == NEXT_LEVEL_STATE:
            level += 1
            if level >= len(LEVELS):
                state = WIN_STATE
            else:
                state = START_STATE
        elif state == WIN_STATE:
            break
    print(state)

    pygame.quit()


if __name__ == "__main__":
    main()
