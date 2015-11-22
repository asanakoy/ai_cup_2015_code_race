__author__ = 'artem'

class MockWorld:
    def __init__(self, tick, tiles_x_y, waypoints):
        self.tick = tick
        self.tiles_x_y = tiles_x_y
        self.waypoints = waypoints
        self.width = len(tiles_x_y)
        self.height = len(tiles_x_y[0])


    @staticmethod
    def create(mapname):
        mapnames = ['map04']
        if mapname not in mapnames:
            raise ValueError('Unknown map')
        return MockWorld(0, MockWorld._tiles[mapname], MockWorld._waypoints[mapname])



    _tiles = {'map04' :
                        [[3, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 5],
                         [2, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 9],
                         [4, 8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8, 5, 2],
                         [0, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6, 2, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 5, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 8, 9, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 9, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 9, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 6, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 2],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 3, 6],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 6, 0]]
             }

    _waypoints = {'map04': [[13, 15], [1, 15], [0, 0], [2, 0], [2, 14], [13, 13]] }