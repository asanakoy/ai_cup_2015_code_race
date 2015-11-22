import utils
from DirectionExt import DirectionExt
from DirectionExt import get_vector_by_direction

class PathTile:

    def __init__(self, tile, is_waypoint=False, wp_index=None,  direction=DirectionExt.UNKNOWN, path_index=None):
        self.coord = tuple(tile)
        self.is_waypoint = is_waypoint
        self.wp_index = wp_index
        self.direction = direction
        self.direction_vector = get_vector_by_direction(direction)
        self.index = path_index  # index inside path

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)