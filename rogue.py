import libtcodpy as libtcod
from rogueclasses import *

WINDOW_TITLE = 'Roguelike Tutorial'
PLAYER_SYMBOL = '@'
PLAYER_COLOR = libtcod.white
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 15

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, False)

game_console = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

# Limit FPS for real-time play;
# Comment out if turn-based play is desired.
libtcod.sys_set_fps(LIMIT_FPS)

# Initialize player information
player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, PLAYER_SYMBOL, PLAYER_COLOR)
npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
objects = [npc, player]

# Map Info
ZONE_WIDTH = 80
ZONE_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

# Helper Funcs

def handle_keys():
  """Handles key inputs from the player.

  UP/DOWN/LEFT/RIGHT keys will move the player in their respective directions. Fullscreen mode is toggled with LAlt+ENTER; Game exit is triggered with ESCAPE.
  """
  global player

  # Fullscreen and Exit keys;
  # Use "True" arg for turn-based; omit for real-time
  key = libtcod.console_check_for_keypress(True)
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  elif key.vk == libtcod.KEY_ESCAPE:
    return True

  # Movement Keys
  if libtcod.console_is_key_pressed(libtcod.KEY_UP):
    player.move(zone, 0, -1)
  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    player.move(zone, 0, 1)
  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    player.move(zone, -1, 0)
  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    player.move(zone, 1, 0)

def make_zone():
  global zone
  rooms = []
  num_rooms = 0

  # Fill zone with "unblocked" tiles
  zone = [[ Tile(True)
    for y in range(ZONE_HEIGHT) ]
      for x in range(ZONE_WIDTH)]

  for r in range(MAX_ROOMS):
    w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    x = libtcod.random_get_int(0, 0, ZONE_WIDTH - w - 1)
    y = libtcod.random_get_int(0, 0, ZONE_HEIGHT - h - 1)
    new_room = Rect(x, y, w, h)
    intersects = False
    for other_room in rooms:
      if new_room.intersect(other_room):
        intersects = True
        break
    if not intersects:
      create_room(new_room)
      (new_x, new_y) = new_room.center()
      if num_rooms == 0:
        player.x = new_x
        player.y = new_y
      else:
        (prev_x, prev_y) = rooms[num_rooms-1].center()
        if libtcod.random_get_int(0, 0, 1) == 1:
          # First carve horizontally, then vertically
          create_h_tunnel(prev_x, new_x, prev_y)
          create_v_tunnel(prev_y, new_y, new_x)
        else:
          # Carve vertically, then horizontally
          create_v_tunnel(prev_y, new_y, prev_x)
          create_h_tunnel(prev_x, new_x, new_y)
      rooms.append(new_room)
      num_rooms += 1

def create_room(room):
  """Creates walkable space in the shape of a room.

  Takes a Rect as an argument. Modifies the current zone.
  """
  global zone
  # Iterate through the tiles in the Rect and make them passable
  for x in range(room.x1 + 1, room.x2):
    for y in range(room.y1 + 1, room.y2):
      zone[x][y].blocks = False
      zone[x][y].blocks_sight = False

def create_h_tunnel(x1, x2, y):
  global zone
  for x in range(min(x1, x2), max(x1, x2) + 1):
    zone[x][y].blocks = False
    zone[x][y].blocks_sight = False

def create_v_tunnel(y1, y2, x):
  global zone
  for y in range(min(y1, y2), max(y1, y2) + 1):
    zone[x][y].blocks = False
    zone[x][y].blocks_sight = False

def render_all():
  global color_light_wall
  global color_light_ground
  # Draws all Objects in the list
  for obj in objects:
    obj.draw(game_console)

  for y in range(ZONE_HEIGHT):
    for x in range(ZONE_WIDTH):
      wall = zone[x][y].blocks_sight
      if wall:
        libtcod.console_set_char_background(game_console, x, y, \
                                            color_dark_wall, \
                                            libtcod.BKGND_SET)
      else:
        libtcod.console_set_char_background(game_console, x, y, \
                                            color_dark_ground, \
                                            libtcod.BKGND_SET)
  #  Flush console and push changes to screen
  libtcod.console_blit(game_console, 0, 0, \
                      SCREEN_WIDTH, SCREEN_HEIGHT, \
                      0, 0, 0)

# Main game loop
#  If real-time, each loop iteration is a frame;
#  If turn-based, each loop iteration is a turn
def game_loop():
  while not libtcod.console_is_window_closed():
    render_all()

    libtcod.console_flush()

    # Erase all objects at their old locations, before they move
    for obj in objects:
      obj.clear(game_console)

    exit = handle_keys()
    if exit:
      break

if __name__ == "__main__":
  make_zone()
  game_loop()
