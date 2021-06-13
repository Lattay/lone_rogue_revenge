from pygame.event import custom_type


W, H = 1280, 720  # Canvas size
Z = 4  # Zoom

FIELD_SIZE_SPRITE = 32
FIELD_SIZE = FIELD_SIZE_SPRITE * Z * 16
BULLET_DIST = FIELD_SIZE * 0.45

DEADZONE = 0.2  # Joystick trigger

# Colors (palette pink_ink)
WHITE = (255, 255, 255)
LIGHT = (254, 108, 144)
BRIGHT = (208, 55, 145)
MID = (135, 40, 106)
DARK = (69, 36, 89)
BLACK = (38, 13, 52)

ROTATIONS = [
    ((0, -1), 0),
    ((-1, -1), 45),
    ((-1, 0), 90),
    ((-1, 1), 135),
    ((0, 1), 180),
    ((1, 1), -135),
    ((1, 0), -90),
    ((1, -1), -45),
]

SQRT_2 = 2 ** 0.5

DEBUG = True

RESET_PLAYER = custom_type()
LOOSE = custom_type()


LOOSE_STATE = 1
START_STATE = 2
NEXT_LEVEL_STATE = 3
WIN_STATE = 4

LEVELS = (
    "assets/level2.json",
    "assets/level1.json",
)
