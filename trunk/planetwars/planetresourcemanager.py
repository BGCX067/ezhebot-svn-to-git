import player

__author__ = 'ibo.ezhe'

class PlanetResourceManager(object):
    def __init__(self, universe):
        self.universe = universe

    @property
    def turn_count(self):
        return self.universe.turn_count

    def ships_available(self, planet):
        turn = self.universe.turn_count
        ships_available = planet.ship_count

        if self.turn_count == 1:
            #1. is to figure out how many of your ships you want to commit to expansion. I take the approach that I *don't* want to lose my starting planet
            if planet.owner == player.ME:
                my_planet = planet
                enemy_planet = self.universe.enemies_strongest_planet
            elif planet.owner == player.ENEMIES:
                enemy_planet = planet
                my_planet = self.universe.my_strongest_planet
            else:
                return ships_available
            ships_growth = my_planet.growth_rate * self.universe.get_distance(my_planet, enemy_planet)
            ships_available = min(my_planet.ship_count, ships_growth)

        for s in self.universe.strategies.items:
            for o in s.orders:
                if o.source == planet and o.turn >= turn:
                    ships_available -= o.ship_count
        return max(ships_available, 0)
  