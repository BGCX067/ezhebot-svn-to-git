from math import ceil

__author__ = 'lynx'

class SmartConstants:
    MAX_EXPAND_DISTANCE_PERCENT = 25 #in percents
    MAX_ATTACK_DISTANCE_PERCENT = 40 #in percents
    NEARBY_RADIUS_PERCENT = 15

    def __init__(self, universe):
        self.universe = universe
        self.max_distance = universe.max_planet_distance
        self.__max_expand = ceil(float(self.max_distance) / float(100) * float(self.MAX_EXPAND_DISTANCE_PERCENT))
        self.__max_attack = ceil(float(self.max_distance) / float(100) * float(self.MAX_ATTACK_DISTANCE_PERCENT))
        self.__nearby_radius = ceil(float(self.max_distance) / float(100) * float(self.NEARBY_RADIUS_PERCENT))

    @property
    def nearby_radius(self):
        return self.__nearby_radius

    @property
    def max_attack_distance(self):
        return self.__max_attack

    @property
    def max_expand_distance(self):
        return self.__max_expand
