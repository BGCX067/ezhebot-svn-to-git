import player

__author__ = 'ibo.ezhe'

class PlanetResourceManager(object):
    def __init__(self, universe):
        self.universe = universe

    def ships_available(self, planet):
        turn = self.universe.turn_count
        ships_available = planet.ship_count

        if self.universe.turn_count == 1:
            #todo: calculate ships available in different way
            a=1

        for s in self.universe.strategies.items:
            for o in s.orders:
                if o.source == planet and o.turn >= turn:
                    ships_available -= o.ship_count
        return max(ships_available, 0)
  