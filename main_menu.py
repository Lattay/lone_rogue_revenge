from pygame.transform import rotate
from pygame.math import Vector2

from constants import W, H, Z
from glob import globs
from ui import UiMaster, Manager, Button, Ui
from assets import get_sprite


def setup_main_menu(group):
    managers = [MainMenuManager(group)]
    return UiMaster(managers, group)


class MainMenuManager(Manager):
    def __init__(self, group):
        super().__init__()
        self.group = group

        Title(Z * 16, group)

        self.button_sprites = [
            ("ui_play", play_cb),
            ("ui_about", about_cb),
            ("ui_exit", exit_cb),

        ]

        n = len(self.button_sprites)

        self.buttons = [
            SpriteButton(i, n, sp, cb, self, group)
            for i, (sp, cb) in enumerate(self.button_sprites)
        ]

        self.cursor = Cursor(Z * 2 * 16, self.buttons[0].rect.centery, group)
        self.cursor_index = 0

    def up(self):
        if not self.cursor.traveling:
            change = False

            if globs.actions.up:
                self.cursor_index = max(self.cursor_index - 1, 0)
                change = True
            elif globs.actions.down:
                self.cursor_index = min(self.cursor_index + 1, len(self.button_sprites) - 1)
                change = True

            if change:
                self.cursor.target_y = self.buttons[self.cursor_index].rect.centery


class Title(Ui):
    def __init__(self, y, *args, **kwargs):
        self.image = get_sprite("title")
        size = self.image.get_size()
        super().__init__(0, 0, *size, *args, **kwargs)

        self.rect.center = (W * 0.5, y)


class SpriteButton(Button):
    def __init__(self, i, n, sprite_name, callback, *args, **kwargs):
        self.image = get_sprite(sprite_name)
        size = self.image.get_size()
        super().__init__(0, 0, *size, *args, **kwargs)
        x = W * 0.5
        y = H * 0.5 + (i / n - 0.5) * (H - 4 * 16 * Z) + 2 * 16 * Z
        self.rect.center = (x, y)
        self.name = sprite_name
        self.callback = callback

    def on_hit(self, _):
        self.callback()


class Cursor(Ui):
    def __init__(self, x, y, group):
        sprite = get_sprite("hero")
        self.moving = [sprite, rotate(sprite, 180)]
        self.not_moving = self.image = rotate(sprite, -90)
        size = self.image.get_size()
        super().__init__(0, 0, *size, group)
        self.rect.center = (x, y)

        self.target_y = y
        self.traveling = False
        self.v = 4

    def up(self):
        dy = self.target_y - self.rect.centery
        if abs(dy) > self.v:
            direction = Vector2(0, dy / abs(dy))
            self.rect.center += direction * self.v
            self.image = self.moving[1 if dy > 0 else 0]
            self.traveling = True
        else:
            self.rect.centery = self.target_y
            self.image = self.not_moving
            self.traveling = False
        if globs.actions.ui_select:
            self.fire()

    def fire(self):
        pass


def play_cb():
    pass


def about_cb():
    pass


def exit_cb():
    pass
