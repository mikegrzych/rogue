import libtcodpy as libtcod
import math

def is_blocked(zone, objects, x, y):
  """Checks to see if a provided space in the zone is blocked. Takes the current zone, objects list, and chosen x-y coordinates as arguments.

  Modifies nothing. Returns True if the coordinate is blocked, and False otherwise.
  """
  if zone[x][y].blocks is True:
    return True

  for obj in objects:
    if obj.blocks is True and obj.x == x and obj.y == y:
      return True

  return False

class Object:
    # Generic Object class;
    # Can be used to represent any object in game world, such as:
    #   Players
    #   Enemies
    #   Stairs
    #   Items
    #   etc...
    # An Object is always represented by a character on the screen.
    def __init__(self, name, x, y, char, color, blocks=False, fighter=None, ai=None):
      """Initialization procedure for an Object.

      Initializes Object with specified name, x-y position, displayed character, color, and blocking status.
      """
      self.name = name
      self.blocks = blocks
      self.x = x
      self.y = y
      self.char = char
      self.color = color
      self.fighter = fighter
      if self.fighter:
        self.fighter.owner = self

      self.ai = ai
      if self.ai:
        self.ai.owner = self

    def move(self, state, dx, dy):
      """Move the object according to a provided distance vector (dx, dy).

      Modifies x and y attributes.
      """
      if not is_blocked(state["current_zone"], state["objs"], self.x + dx, self.y + dy):
        self.x += dx;
        self.y += dy;

    def move_toward(self, state, target_x, target_y):
      dx = target_x - self.x
      dy = target_y - self.y
      distance = math.sqrt(dx ** 2 + dy ** 2)

      # Normalize to a unit vector, round, and convert to int,
      # thereby restricting movement to map grid
      dx = int(round(dx / distance))
      dy = int(round(dy / distance))
      self.move(state, dx, dy)

    def distance_to(self, other):
      """Determine the distance between this Object and other.

      Returns a float.
      """
      dx = other.x - self.x
      dy = other.y - self.y
      return math.sqrt(dx ** 2 + dy ** 2)

    def draw(self, console, fov_map):
      """Draws the Object's character and color to the specified console.
      """
      if libtcod.map_is_in_fov(fov_map, self.x, self.y):
        libtcod.console_set_default_foreground(console, self.color)
        libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def move_to_front(self, object_list):
      """Moves this Object to the front of the object_list, assuming Object is an element of object_list.

      Modifies object_list.
      """
      object_list.remove(self)
      object_list.insert(0, self)

    def clear(self, console):
      """Erases the Object's character from the specified console.
      """
      libtcod.console_put_char(console, self.x, self.y, ' ', libtcod.BKGND_NONE)

class Tile:
  # A tile on the map, has properties and attributes
  def __init__(self, blocks, blocks_sight = None):
    self.blocks = blocks
    self.explored = False

    # By default, a tile that blocks also blocks_sight
    if blocks_sight is None:
      blocks_sight = blocks

    self.blocks_sight = blocks_sight

class Rect:
  # A rectangle on the map, used to depict a room
  def __init__(self, x, y, w, h):
    self.x1 = x
    self.y1 = y
    self.x2 = x + w
    self.y2 = y + h

  def center(self):
    center_x = (self.x1 + self.x2) / 2
    center_y = (self.y1 + self.y2) / 2
    return (center_x, center_y)

  def intersect(self, other):
    # Returns True if Rect self intersects with Rect other
    return (self.x1 <= other.x2 and self.x2 >= other.x1 and \
            self.y1 <= other.y2 and self.y2 >= other.y1)

class Fighter:
  # Combat-related properties and methods
  # For:
  #  - Player
  #  - Monsters
  #  - NPCs
  def __init__(self, hp, defense, power, death_func=None):
    self.max_hp = hp
    self.cur_hp = hp
    self.defense = defense
    self.power = power
    self.death_func = death_func

  def take_damage(self, damage):
    # Apply damage if possible
    if damage > 0:
      self.cur_hp -= damage
    if self.cur_hp <= 0:
      func = self.death_func
      if func is not None:
        func(self.owner)

  def attack(self, target):
    damage = self.power - target.fighter.defense

    if damage > 0:
      # Make the target take some damage
      print self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.'
      target.fighter.take_damage(damage)
    else:
      print self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'

class MonsterBasic:
  # Basic AI component
  # For:
  #  - Monsters
  def take_turn(self, state):
    monster = self.owner
    if libtcod.map_is_in_fov(state["fov_map"], monster.x, monster.y):
      if monster.distance_to(state["player"]) >= 2:
        # Move toward the player if far away
        monster.move_toward(state, state["player"].x, state["player"].y)
      elif state["player"].fighter.cur_hp > 0:
        # Attack the player if player is adjacent and alive
        monster.fighter.attack(state["player"])
