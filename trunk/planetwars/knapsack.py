import player
from planetwars.orderchain import Strategy
import priority
from logging import getLogger
from planetwars.util import Point

__author__ = 'ibo.ezhe'

log = getLogger(__name__)

class KnapSack:
    def __init__(self, source, ships_available, max_distance=20):
        if not ships_available or ships_available == 0:
            raise AttributeError("Knapsack called with no ships")

        self.max_distance = max_distance
        self.source = source
        self.universe = source.universe
        self.ships_available = ships_available
        self.my_mid = self.get_mid_point(self.universe.my_planets)
        self.enemy_mid = self.get_mid_point(self.universe.enemy_planets)

    #TODO: expansion based on mid point is stupid. we can send ships from our faraway planet to other part of the galaxy
    #TODO: fix it
    #TODO: actually, it is quite good
    def get_mid_point(self, planets):
        x = float(0)
        y = float(0)
        count = len(planets)
        for p in planets:
            x += p.position.x
            y += p.position.y
        mid_x = (1+float(x))/(1+float(count))
        mid_y = (1+float(y))/(1+float(count))
        return Point(mid_x, mid_y)

    def issue_expand_orders(self):
        #candidates to expansion: planets closer to me
        candidates = dict()
        for p in self.universe.nobodies_planets:
            distance_to_me = self.universe.get_distance(p, self.my_mid)
            if distance_to_me <= self.max_distance and \
               distance_to_me < self.universe.get_distance(p, self.enemy_mid):
                growth_rate = p.growth_rate
                if not candidates.has_key(growth_rate):
                    candidates[growth_rate] = list()
                if p.ship_count < self.ships_available:
                    candidates[growth_rate].append(p)

        sorted_keys = sorted(candidates.keys())


        strategy = Strategy(priority.Expand)
        universe = self.source.universe
        turn = universe.game.turn_count
        ships_available = self.ships_available

        #2. attack planets with higher growth rate
        i = len(sorted_keys)-1
        while i >= 0:
            key = sorted_keys[i]
            planets = candidates[key]
            min_ships_needed = 999999
            min_planet = None
            for p in planets:
                if p in self.universe.my_targets:
                    continue
                ships_needed = p.ship_count + 1
                if ships_needed < min_ships_needed and ships_needed < ships_available:
                    min_ships_needed = ships_needed
                    min_planet = p
            if min_planet:
                ships_available -= min_ships_needed
                strategy.issue_order(turn, self.source, min_planet, min_ships_needed)
                #repeat the same iteration
                continue
            else:
                i-=1
        self.universe.add_strategy(strategy)

