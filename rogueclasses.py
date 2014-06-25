import libtcodpy as libtcod
class Object:
    # Generic Object class;
    # Can be used to represent any object in game world, such as:
    #   Players
    #   Enemies
    #   Stairs
    #   Items
    #   etc...
    # An Object is always represented by a character on the screen.
    def __init__(self, name, x, y, char, color, blocks=False):
      """Initialization procedure for an Object.

      Initializes Object with specified name, x-y position, displayed character, color, and blocking status.
      """
      self.name = name
      self.blocks = blocks
      self.x = x
      self.y = y
      self.char = char
      self.color = color

    def move(self, state, dx, dy):
      """Move the object according to a provided distance vector (dx, dy).

      Modifies x and y attributes.
      """
      if not is_blocked(state, self.x + dx, self.y + dy):
        self.x += dx;
        self.y += dy;

    def draw(self, console, fov_map):
      """Draws the Object's character and color to the specified console.
      """
      if libtcod.map_is_in_fov(fov_map, self.x, self.y):
        libtcod.console_set_default_foreground(console, self.color)
        libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)

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
