import libtcodpy as libtcod
import roguesettings as settings
import rogueclasses as classes
import copy


def make_zone(zone_properties, objects_in):
  """Creates a dungeon zone.

  Takes a dictionary zone_properties as an argument, which contains information for zone height (int), zone width (int), minimum room size (int), maximum room size (int), maximum number of rooms (int), and a list of Objects as a second argument.

  Returns a tuple of the form (player_pos_x, player_pos_y, zone, objects_out)
  """
  rooms = []
  num_rooms = 0
  objects_out = copy.copy(objects_in)

  # Fill zone with "unblocked" tiles
  zone = [[ classes.Tile(True)
    for y in range(zone_properties["height"]) ]
      for x in range(zone_properties["width"])]

  for r in range(settings.MAX_ROOMS):
    w = libtcod.random_get_int(0, zone_properties["r_min"], zone_properties["r_max"])
    h = libtcod.random_get_int(0, zone_properties["r_min"], zone_properties["r_max"])
    x = libtcod.random_get_int(0, 0, zone_properties["width"] - w - 1)
    y = libtcod.random_get_int(0, 0, zone_properties["height"] - h - 1)
    new_room = classes.Rect(x, y, w, h)
    intersects = False
    for other_room in rooms:
      if new_room.intersect(other_room):
        intersects = True
        break
    if not intersects:
      create_room(zone, new_room)
      # Add objects to room (monsters, chests, etc)
      place_objects(new_room, zone_properties["r_mons_max"], objects_out)
      (new_x, new_y) = new_room.center()
      if num_rooms == 0:
        player_x = new_x
        player_y = new_y
      else:
        (prev_x, prev_y) = rooms[num_rooms-1].center()
        if libtcod.random_get_int(0, 0, 1) == 1:
          # First carve horizontally, then vertically
          create_h_tunnel(zone, prev_x, new_x, prev_y)
          create_v_tunnel(zone, prev_y, new_y, new_x)
        else:
          # Carve vertically, then horizontally
          create_v_tunnel(zone, prev_y, new_y, prev_x)
          create_h_tunnel(zone, prev_x, new_x, new_y)
      rooms.append(new_room)
      num_rooms += 1
  return (player_x, player_y, zone, objects_out)

def create_room(zone, room):
  """Creates walkable space in the shape of a room.

  Takes a zone[Tile][Tile] and Rect (room) as an argument. Modifies zone[x][y].
  """
  # Iterate through the tiles in the Rect and make them passable
  for x in range(room.x1 + 1, room.x2):
    for y in range(room.y1 + 1, room.y2):
      zone[x][y].blocks = False
      zone[x][y].blocks_sight = False

def create_h_tunnel(zone, x1, x2, y):
  for x in range(min(x1, x2), max(x1, x2) + 1):
    zone[x][y].blocks = False
    zone[x][y].blocks_sight = False

def create_v_tunnel(zone, y1, y2, x):
  for y in range(min(y1, y2), max(y1, y2) + 1):
    zone[x][y].blocks = False
    zone[x][y].blocks_sight = False

def place_objects(room, max_monsters, objects):
  """Places a random number n monsters (0 < n < max_monsters) in the provided room, appending them to objects.

  Modifies objects. Returns nothing.
  """
  # Choose a random number of monsters
  num_monsters = libtcod.random_get_int(0, 0, max_monsters )

  for i in range(num_monsters):
    # Choose random spot for monster
    x = libtcod.random_get_int(0, room.x1, room.x2)
    y = libtcod.random_get_int(0, room.y1, room.y2)

    if libtcod.random_get_int(0, 0, 100) < 80:  #80% Chance of Orc
      # Create an Orc
      monster = classes.Object(x, y, 'o', libtcod.desaturated_green)
    else:
      #create a Troll
      monster = classes.Object(x, y, 'T', libtcod.darker_green)
    objects.append(monster)
