from copy import copy
import player
import planet

__author__ = 'lynx'

class FutureDepthError(Exception):
   def __init__(self, value):
       self.parameter = value
   def __str__(self):
       return repr(self.parameter)
   @property
   def value(self):
       return self.parameter

class PlanetStub:
    def __init__(self, planet, turn):
        self.id = planet.id
        self.owner = planet.owner
        self.ship_count = planet.ship_count
        self.position = planet.position
        self.growth_rate = planet.growth_rate
        self.planet = planet
        self.turn = turn

class FuturePrediction:
    def __init__(self, universe):
        self.future_depth = universe.max_planet_distance
        self.universe = universe
        self.cache = dict()

    def get(self, planet, turn):
        if turn > self.universe.turn_count + self.future_depth:
            raise FutureDepthError("for planet %s on %d turn" % (planet, turn))
        return self.cache[(planet, turn)]

    @property
    def turn(self):
        return self.universe.turn_count

    @property
    def future_range(self):
        return range(self.turn, self.turn + self.future_depth)

    def predict(self):
        for p in self.universe.planets:
            for step in self.future_range:
                k = (p, step)
                p2 = p.in_future(step-self.turn)
                v = PlanetStub(p2, step)
                self.cache[k] = v











  