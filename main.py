import pygame

from constants import (
    W, H,
    LOOSE_STATE, NEXT_LEVEL_STATE, START_STATE, WIN_STATE,
    LEVELS
)

from assets import load_assets

from play import run_level
from menu import run_menu


def main():
    pygame.init()
    pygame.joystick.init()

    screen = pygame.display.set_mode((W, H), flags=pygame.RESIZABLE | pygame.SCALED)
    load_assets()

    game_state = {
        'score': 0,
        'life': 2,
    }

    level = run_menu(screen, "main")

    while level is not None:
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

        level = run_menu(screen, "main")

    pygame.quit()


if __name__ == "__main__":
    main()
