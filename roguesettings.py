import libtcodpy as libtcod

WINDOW_TITLE = 'Roguelike Tutorial'
PLAYER_SYMBOL = '@'
PLAYER_COLOR = libtcod.white
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 15

# Map Info
ZONE_WIDTH = 80
ZONE_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
ZONE_PROPERTIES = { "width":ZONE_WIDTH, "height":ZONE_HEIGHT, "r_min":ROOM_MIN_SIZE, "r_max":ROOM_MAX_SIZE, "r_num_max":MAX_ROOMS }

# Game Settings
FOV_ALGO = libtcod.FOV_BASIC
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 4
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)
COLORS = { "wall_dk":color_dark_wall, "wall_lt":color_light_wall, "gnd_dk":color_dark_ground, "gnd_lt":color_light_ground }

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, False)

# Limit FPS for real-time play;
# Comment out if turn-based play is desired.
libtcod.sys_set_fps(LIMIT_FPS)
