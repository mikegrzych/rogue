import libtcodpy as libtcod
import roguesettings as settings
import rogueclasses as classes

GAME_CONSOLE = libtcod.console_new(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

# Initialize PLAYER and world information
PLAYER = classes.Object(settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2, settings.PLAYER_SYMBOL, settings.PLAYER_COLOR)
#npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
OBJECTS = [PLAYER]
ZONE = None
FOV_MAP = None
FOV_RECOMPUTE = None
GAME_STATE = { "console":GAME_CONSOLE, "player":PLAYER, "objs":OBJECTS, "current_zone":ZONE, "fov_map":FOV_MAP, "fov_recomp":FOV_RECOMPUTE }

def handle_keys(state):
  """Handles key inputs from the PLAYER.

  UP/DOWN/LEFT/RIGHT keys will move the PLAYER in their respective directions. Fullscreen mode is toggled with LAlt+ENTER; Game exit is triggered with ESCAPE.

  Accesses and modifies PLAYER, ZONE, and the FOV_RECOMPUTE flag.
  """

  # Fullscreen and Exit keys;
  # Use "True" arg for turn-based; omit for real-time
  key = libtcod.console_check_for_keypress(True)
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  elif key.vk == libtcod.KEY_ESCAPE:
    return True

  # Movement Keys
  if libtcod.console_is_key_pressed(libtcod.KEY_UP):
    state["player"].move(state["current_zone"], 0, -1)
    state["fov_recomp"] = True
  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    state["player"].move(state["current_zone"], 0, 1)
    state["fov_recomp"] = True
  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    state["player"].move(state["current_zone"], -1, 0)
    state["fov_recomp"] = True
  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    state["player"].move(state["current_zone"], 1, 0)
    state["fov_recomp"] = True

def make_fov_map(zone):

  fov_recompute = True
  fov_map = libtcod.map_new(len(zone), len(zone[0]))

  for x in range(len(zone)):
    for y in range(len(zone[0])):
      libtcod.map_set_properties(fov_map, x, y, not zone[x][y].blocks_sight, not zone[x][y].blocks)

  return (fov_map, fov_recompute)

def render_all(state):

  # Recompute the FoV map if necessary
  if state["fov_recomp"] is True:
    state["fov_recomp"] = False
    libtcod.map_compute_fov(state["fov_map"], state["player"].x, state["player"].y, settings.TORCH_RADIUS, settings.FOV_LIGHT_WALLS, settings.FOV_ALGO)

  # Draws all Objects in the list
  for obj in state["objs"]:
    obj.draw(GAME_CONSOLE, state["fov_map"])

  for x in range(len(state["current_zone"])):
    for y in range(len(state["current_zone"][0])):
      visible = libtcod.map_is_in_fov(state["fov_map"], x, y)
      wall = state["current_zone"][x][y].blocks_sight
      if visible:
        if wall:
          libtcod.console_set_char_background(state["console"], x, y, \
                                              settings.COLORS["wall_lt"], \
                                              libtcod.BKGND_SET)
        else:
          libtcod.console_set_char_background(state["console"], x, y, \
                                              settings.COLORS["gnd_lt"], \
                                              libtcod.BKGND_SET)
        state["current_zone"][x][y].explored = True
      else:
        # Even if not currently visible, PLAYER may see this space if it has already been explored
        if state["current_zone"][x][y].explored:
          if wall:
            libtcod.console_set_char_background(state["console"], x, y, \
                                                settings.COLORS["wall_dk"], \
                                                libtcod.BKGND_SET)
          else:
            libtcod.console_set_char_background(state["console"], x, y, \
                                                settings.COLORS["gnd_dk"], \
                                                libtcod.BKGND_SET)
  #  Flush console and push changes to screen
  libtcod.console_blit(state["console"], 0, 0, \
                      settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, \
                      0, 0, 0)

# Main game loop
#  If real-time, each loop iteration is a frame;
#  If turn-based, each loop iteration is a turn
def game_loop(state):

  while not libtcod.console_is_window_closed():
    render_all(state)

    libtcod.console_flush()

    # Erase all OBJECTS at their old locations, before they move
    for obj in state["objs"]:
      obj.clear(state["console"])

    exit = handle_keys(state)
    if exit:
      break
