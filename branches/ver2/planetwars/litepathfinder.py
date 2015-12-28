import player
from planetwars.orderchain import Strategy
import priority

__author__ = 'ibo.ezhe'

class LitePathFinder:
    def __init__(self, head, tail, owner=player.ME):
        self.head = head
        self.universe = self.head.universe
        self.tail = tail
        self.owner = owner

    def __get_heuristics_cost(self, source, tail):
        #in our universe actual distance is always the shortest path
        #but we cannot control our ships while they are in flight
        #so we assume, better use chains of planets than fly through the open space
        actual_distance = source.distance(tail)
        if actual_distance <= 5:
            return actual_distance
        if actual_distance <= 7:
            return actual_distance*2
        if actual_distance <= 10:
            return actual_distance*3
        if actual_distance <= 15:
            return actual_distance*10
        if actual_distance <= 20:
            return actual_distance*100
        return actual_distance*1000

    def __get_total_cost(self, source, tail):
        hc = self.__get_heuristics_cost(source, tail)
        tc = source.distance(tail)
        return hc + tc

    @property
    def next_target(self):
        planets = self.head.universe.get_closest_planets(self.head, owner=self.owner)
        tc_straight_line = self.__get_total_cost(self.head, self.tail)
        tc_dict = dict()
        tc_dict[tc_straight_line] = list()
        tc_dict[tc_straight_line].append(self.tail)
        for p in planets:
            tc = self.__get_total_cost(p, self.tail)
            if not tc_dict.has_key(tc):
                tc_dict[tc] = list()
            tc_dict[tc].append(p)

        for k in sorted(tc_dict.keys()):
            planet_list = tc_dict[k]
            if self.tail in planet_list:
                return self.tail
            else:
                #return first match (according to Accama principle)
                return planet_list[0]

    def issue_supply_orders(self, turn, ships):
        next_target = self.next_target
        strategy = Strategy(priority.Supply)
        strategy.issue_order(turn, self.head, next_target, ships)
        self.universe.add_strategy(strategy)



  