# vim:ts=4:shiftwidth=4:et

from planetwars.universe import Universe, player
from planetwars.player import Player
from copy import deepcopy, copy
from math import ceil
from math import sqrt
from planetwars.util import Point
from planetwars.smartconstants import SmartConstants

class Universe2(Universe):
    __constants = None

    @property
    def constants(self):
        if not self.__constants:
            self.__constants = SmartConstants(self)
        return self.__constants


    def weakest_planets(self, owner, count=1):
        """
        Returns a set of `count' planets with the smallest ship_count.

        Returns <Planets> (@see planet.py) objects (a set subclass).
        """
        planets = self.find_planets(owner=owner)
        if count > 0:
            res = []
            #sorted_planets = sorted(planets, key=lambda p : p.ship_count)
            sorted_planets = sorted(planets, key=lambda p : (1.0+p.growth_rate)/(1.0+p.ship_count), reverse=True)
            if count >= len(planets):
                return sorted_planets
            return sorted_planets[:count]
        return []

    # Shortcut / convenience properties
    def my_weakest_planets(self, count):
        return self.weakest_planets(owner=player.ME, count=count)

    @property
    def my_weakest_planet(self):
        return self.my_weakest_planets(1)[0]

    def enemies_weakest_planets(self, count):
        return self.weakest_planets(owner=player.ENEMIES, count=count)

    @property
    def enemies_weakest_planet(self):
        return self.enemies_weakest_planets(1)[0]

    def strongest_planets(self, owner, count=1):
        """
        Returns a set of `count' planets belonging to owner with the biggest ships_available.

        Returns <Planets> (@see planet.py) objects (a set subclass).
        """
        planets = self.find_planets(owner=owner)
        if count > 0:
            sorted_planets = sorted(planets, key=lambda p : p.ships_available, reverse=True)
            if count >= len(planets):
                return sorted_planets
            return sorted_planets[:count]
        return []

    # Shortcut / convenience properties
    def my_strongest_planets(self, count):
        return self.strongest_planets(owner=player.ME, count=count)

    @property
    def my_strongest_planet(self):
        return self.my_strongest_planets(1)[0]

    def enemies_strongest_planets(self, count):
        return self.strongest_planets(owner=player.ENEMIES, count=count)

    @property
    def enemies_strongest_planet(self):
        return self.enemies_strongest_planets(1)[0]

    # Returns the number of ships that the current player has, either located
    # on planets or in flight.
    def get_num_ships(self, owner):
        numShips = 0
        planets = self.find_planets(owner=owner)
        fleets = self.find_fleets(destination=self)
        for p in planets:
            numShips += p.ship_count
        for f in fleets:
            numShips += f.ship_count
        return numShips

    #Returns the production of the given player.
    def get_production(self, owner):
        prod = 0
        planets = self.find_planets(owner=owner)
        for p in planets:
            if (p.Owner() == playerID):
                prod += p.growth_rate
        return prod

    #Returns the production of the given player.
    def get_distance(self, planet1, planet2):
        return planet1.distance(planet2)

    #Returns the production of the given player.
    def get_point_distance(self, planet, x, y):
        xy = Point(x,y)
        return planet.distance(xy)

    def get_closest_planets(self, planet, owner=player.ME, max_radius=None):
        if not max_radius:
            max_radius = self.constants.nearby_radius

        planets = self.find_planets(owner=owner)
        planets_dict = dict()
        for p in planets:
            d = planet.distance(p)
            if not planets_dict.has_key(d):
                planets_dict[d] = list()
            planets_dict[d].append(p)
        for k in sorted(planets_dict.keys()):
            if k > max_radius:
                break
            planets_list = planets_dict[k]
            for p in planets_list:
                yield p

    def closest_enemy_planet(self, planet):
        candidates = self.get_closest_planets(planet, owner=player.ENEMIES)
        for p in candidates:
            return p
        return None

    def get_far_planets(self, planet, owner=player.ME, min_radius=None):
        if not min_radius:
            min_radius = self.constants.nearby_radius

        planets = self.find_planets(owner=owner)
        planets_dict = dict()
        for p in planets:
            d = planet.distance(p)
            if not planets_dict.has_key(d):
                planets_dict[d] = list()
            planets_dict[d].append(p)
        for k in sorted(planets_dict.keys(), reverse=True):
            if k < min_radius:
                break
            planets_list = planets_dict[k]
            for p in planets_list:
                yield p

    @property
    def turn_count(self):
        return self.game.turn_count

    @property
    def my_targets(self):
        for f in self.my_fleets:
            yield f.destination
        return

    def get_planet_by_id(self, id):
        for p in self.planets:
            if p.id == id:
                return p
        return None




