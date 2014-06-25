import libtcodpy as libtcod
import roguesettings as settings
import rogueclasses as classes
import roguesystem as system
import roguedungeon as dungeon



# Helper Funcs



if __name__ == "__main__":
  (system.GAME_STATE["player"].x, system.GAME_STATE["player"].y, system.GAME_STATE["current_zone"], system.GAME_STATE["objs"]) = dungeon.make_zone(settings.ZONE_PROPERTIES, system.GAME_STATE["objs"])
#  system.GAME_STATE = dungeon.make_zone(settings.ZONE_PROPERTIES, system.GAME_STATE)
  (system.GAME_STATE["fov_map"], system.GAME_STATE["fov_recomp"]) = system.make_fov_map(system.GAME_STATE["current_zone"])
  system.game_loop(system.GAME_STATE)
