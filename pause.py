from constants import W, H
from assets import get_sprite

from ui import Ui


def setup_pause_screen(group):
    PauseScreen(W / 2, H / 2, group)


class PauseScreen(Ui):
    def __init__(self, x, y, *args, **kwargs):

        self.image = get_sprite("ui_pause")
        size = self.image.get_size()

        super().__init__(0, 0, *size, *args, **kwargs)
        self.rect.center = (x, y)
