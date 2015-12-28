import player
from planetwars.orderchain import Strategy
import priority
from logging import getLogger
from planetwars.util import Point

__author__ = 'ibo.ezhe'

log = getLogger(__name__)

class KnapSack:
    def __init__(self, source, ships_available, max_radius=15):
        if not ships_available or ships_available == 0:
            raise AttributeError("Knapsack called with no ships")

        self.max_radius = max_radius
        self.source = source
        self.universe = source.universe
        self.ships_available = ships_available

    #todo: check if my new expand algorithm is less stupid
    def issue_expand_orders(self):
        #candidates to expansion: planets closer to me
        candidates = dict()

        closest_neutrals = self.universe.get_closest_planets(self.source, owner=player.NOBODY, max_radius=self.max_radius)
        neutral_sum = 0
        for p in closest_neutrals:
            distance_to_me = self.source.distance(p)
            enemy_closest_planets = self.universe.get_closest_planets(p, owner=player.ENEMIES, max_radius=self.max_radius)
            distance_to_enemy = 99999
            enemy_closest_planet = enemy_closest_planets.next()
            if enemy_closest_planet:
                distance_to_enemy = self.source.distance(enemy_closest_planet)
            if distance_to_me < distance_to_enemy:
                log.debug("-- planet %s is closer to me. added to candidates" % p)
                growth_rate = p.growth_rate
                if not candidates.has_key(growth_rate):
                    candidates[growth_rate] = list()
                if p.ship_count < self.ships_available:
                    candidates[growth_rate].append(p)
            neutral_sum+=1
        log.debug("Prepaired knapsack for %d neutral planets" % neutral_sum)


        sorted_keys = sorted(candidates.keys(), reverse=True)


        strategy = Strategy(priority.Expand)
        universe = self.source.universe
        turn = universe.game.turn_count
        ships_available = self.ships_available

        #2. attack planets with higher growth rate
        for key in sorted_keys:
            planets = candidates[key]
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
        self.universe.add_strategy(strategy)

