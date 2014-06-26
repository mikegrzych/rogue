import libtcodpy as libtcod
import roguesettings as settings
import rogueclasses as classes

def player_death(player):
  # The player has died, and the game ends
  print 'You died!'
  GAME_STATE["status"] = 'dead'

  # Transform the player into a corpse
  player.char = '%'
  player.color = libtcod.dark_red

def player_move_or_attack(state, dx, dy):
  # Coordinate the player is moving to or attacking
  x = state["player"].x + dx
  y = state["player"].y + dy

  # Try to find an attackable object
  target = None
  for obj in state["objs"]:
    if obj.fighter and obj.x == x and obj.y == y:
      target = obj
      break

  # Attack if there's a viable target, otherwise move
  if target is not None:
    state["player"].fighter.attack(target)
  else:
    state["player"].move(state, dx, dy)
    state["fov_recomp"] = True

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
    return 'no_action'
  elif key.vk == libtcod.KEY_ESCAPE:
    return 'exit'  # Exit game

  if state["status"] == 'playing':
    # Movement Keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      player_move_or_attack(state, 0, -1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      player_move_or_attack(state, 0, 1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      player_move_or_attack(state, -1, 0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      player_move_or_attack(state, 1, 0)
    else:
      return 'no_action'

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
    if obj != state["player"]:
      obj.draw(state["console"], state["fov_map"])
  state["player"].draw(state["console"], state["fov_map"])

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
  # Show the player's stats
  libtcod.console_set_default_foreground(state["console"], libtcod.white)
  libtcod.console_print_ex(0, 1, settings.SCREEN_HEIGHT - 2, \
                            libtcod.BKGND_NONE, libtcod.LEFT, \
                            'HP: ' + str(state["player"].fighter.cur_hp) + \
                             '/' + str(state["player"].fighter.max_hp))

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

    state["action"] = handle_keys(state)
    if state["action"] == 'exit':
      break

    if state["status"] == 'playing' and state["action"] != 'no_action':
      for obj in state["objs"]:
        if obj.ai:
          obj.ai.take_turn(state)

GAME_CONSOLE = libtcod.console_new(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

# Initialize PLAYER and world information
# Kind of messy right now, will eventually need refactoring to be cleaner
# and minimize pollution of module namespace

PLAYER = classes.Object("Hero", settings.SCREEN_WIDTH/2, settings.SCREEN_HEIGHT/2, settings.PLAYER_SYMBOL, settings.PLAYER_COLOR, fighter=classes.Fighter(hp=30, defense=2, power=5, death_func=player_death))

PLAYER_ACTION = None
GAME_STATUS = 'playing'
#npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
OBJECTS = [PLAYER]
ZONE = None
FOV_MAP = None
FOV_RECOMPUTE = None
GAME_STATE = { "console":GAME_CONSOLE, "player":PLAYER, "action":PLAYER_ACTION, "status":GAME_STATUS, "objs":OBJECTS, "current_zone":ZONE, "fov_map":FOV_MAP, "fov_recomp":FOV_RECOMPUTE }
