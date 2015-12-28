from logging import getLogger
from planetwars.orderchain import Strategy
import planetwars
from planetwars.knapsack import KnapSack
import player
import priority
from planetwars.litepathfinder import LitePathFinder
from math import ceil

__author__ = 'lynx'

log = getLogger(__name__)

SIZESORTWEIGHT =60
TURNSORTWEIGHT=1200

class Surplus:
    def __init__(self, planet, ships):
        self.planet = planet
        self.ships = ships

    @property
    def ship_count(self):
        return self.ships

    def __repr__(self):
        return "%d ships for %s" % (self.ships, self.planet)

class Logic:
    def __init__(self, universe, future_prediction):
        self.universe = universe
        self.fp = future_prediction

    @property
    def turn(self):
        return self.universe.turn_count

    def __get_deficits_and_surpluses(self):
        loss_prevention_list = list()
        surplus_list = list()

        for p in self.universe.my_planets:
            surplus = list()
            deficit = None

            prev_owner = p.owner
            was_conquered = False
            for t in self.fp.future_range:
                p_state = self.fp.get(p, t)
                if p_state.owner != prev_owner and p_state.owner != player.ME:
                    #planet was conquered by enemy
                    deficit = (p_state.ship_count, t)
                    was_conquered = True
                    break
                if p_state.owner == prev_owner and p_state.owner == player.ME:
                    surplus.append(p_state.ship_count)
                prev_owner = p_state.owner

            if was_conquered:
                loss_prevention_list.append((p, deficit[0], deficit[1]))
            else:
                surplus = sorted(surplus)
                if len(surplus) > 1:
                    v = surplus[0]
                    surplus_list.append(Surplus(p, v))
        return (loss_prevention_list, surplus_list)

    def __get_conquests(self):
        conquests = list()
        for p in self.universe.enemy_planets:
            was_conquered_by_me = False
            for t in self.fp.future_range:
                p_state = self.fp.get(p, t)
                if p_state.owner == player.ME:
                    was_conquered_by_me = True
                    break

            if not was_conquered_by_me:
                conquests.append(p)
        return conquests

    def define_strategies(self):
        if self.turn == 1:
            #if we are close to enemy consider Kamikaze attack
            if self.do_kamikaze():
                return
            self.do_expand()
            return

        #Generate a list of surplus ships, and ship deficits (potential planetary losses)
        res = self.__get_deficits_and_surpluses()
        loss_prevention_list = res[0]
        surplus_list = res[1]

        #Generate a list of possible conquests
        conquests = self.__get_conquests()

        #Sort the lossprevention list according to # ships required (smaller is better),
        # growth rate of the planet (bigger is better),
        # and number of turns till the potential loss (smaller is better).
        loss_prevention_list = sorted(loss_prevention_list, key = lambda v: self.__sort(v))

        for item in loss_prevention_list:
            planet = item[0]
            ships_deficit = item[1]
            turn = item[2]
            res = self.consider_defence(planet, turn, ships_deficit, surplus_list)
            if res[0]:
                surplus_list = res[1]
            else:
                conquests.append(planet)


        for planet in conquests:
            res = self.consider_attack(planet, surplus_list)
            if res[0]:
                surplus_list = res[1]

        #not in top50 - expand
        for s in surplus_list:
            self.consider_expand(s.planet)

        #redistribute ships
        #Any sources left unused get redistributed to planets closer to the front lines of the battle
        #[It basically tries to minimize (distance source planet->recipient planet + distance recipient
        # planet->nearest enemy planet), and only approves the move if said sum < (distance source->nearest
        # enemy * 1.3)]
        return
        redistribute_list = list()
        for s in surplus_list:
            for target in self.universe.my_planets:
                source = s.planet
                if source == target:
                    continue
                d1 = source.distance(target)
                closest_enemy = self.universe.closest_enemy_planet(target)
                d2 = 0
                if closest_enemy:
                    d2 = target.distance(closest_enemy)
                score = d1 + d2
                redistribute_list.append((score, s, target))
        redistribute_list = sorted(redistribute_list, key = lambda s: s[0])
        for item in redistribute_list:
            score = item[0]
            surplus = item[1]
            source = surplus.planet
            target = item[2]
            closest_enemy = self.universe.closest_enemy_planet(source)
            distance_to_enemy = 0
            if closest_enemy:
                distance_to_enemy = source.distance(closest_enemy)
            if score < distance_to_enemy * 1.3:
                strategy = Strategy(priority.Supply)
                strategy.issue_order(self.turn, source, target, surplus.ship_count)
                surplus.ship_count = 0
                self.universe.add_strategy(strategy)


    def consider_defence(self, planet, turn, ships_deficit, surplus_list):
        #getting closest surpluses
        ordered_surplus = sorted(surplus_list, key=lambda s: planet.distance(s.planet))
        for surplus in ordered_surplus:
            surplus_source = surplus.planet
            surplus_ship_count = surplus.ships
            surplus_distance = planet.distance(surplus_source)
            if surplus_ship_count >= ships_deficit and \
               self.turn + surplus_distance <= turn:
                strategy = Strategy(priority.Defence)
                strategy.issue_order(self.turn, surplus_source, planet, ships_deficit)
                log.debug("%s on turn %d send %d ships from %s to %s" % (strategy, self.turn, ships_deficit, surplus_source, planet))
                self.universe.add_strategy(strategy)
                surplus.ships -= ships_deficit
                return (True, ordered_surplus)
        return (False, ordered_surplus)

    def consider_attack(self, planet, surplus_list):
        #getting closest surpluses

        ordered_surplus = sorted(surplus_list, key=lambda s: planet.distance(s.planet))
        for surplus in ordered_surplus:
            surplus_source = surplus.planet
            surplus_ship_count = surplus.ships
            surplus_distance = planet.distance(surplus_source)

            p1 = self.fp.get(planet, self.turn + surplus_distance)
            ships_deficit = p1.ship_count + 1

            if surplus_ship_count >= ships_deficit and \
                surplus_distance <= self.universe.constants.max_attack_distance:
                strategy = Strategy(priority.Attack)
                strategy.issue_order(self.turn, surplus_source, planet, ships_deficit)
                log.debug("%s on turn %d send %d ships from %s to %s" % (strategy, self.turn, ships_deficit, surplus_source, planet))
                self.universe.add_strategy(strategy)
                surplus.ships -= ships_deficit
                return (True, ordered_surplus)
        return (False, ordered_surplus)



    def __sort(self, v):
        planet = v[0]
        ships = v[1]
        turn = v[2]
        return (ships*SIZESORTWEIGHT + turn*TURNSORTWEIGHT)/planet.growth_rate

    def do_expand(self):
        #find if we can capture something
        #take my second and third strongest planets, but not head
        strongest = self.universe.my_strongest_planets(3)
        for p in strongest:
            self.consider_expand(p)

    def consider_expand(self, planet):
        p = planet
        if p.ships_available <= 0:
            return
        try:
            kn = KnapSack(p, p.ships_available, self.universe.constants.max_expand_distance)
            kn.issue_expand_orders()
        except:
            log.error("Exception in KnapSack", exc_info=True)

    def do_kamikaze(self):
        #if we are close to enemy consider Kamikaze attack
        my_start = self.universe.my_strongest_planet
        enemy_planet = self.universe.enemies_strongest_planet
        #consider maximum fleet we have
        ships_available = my_start.ship_count
        distance = my_start.distance(enemy_planet)
        ships_needed = distance*enemy_planet.growth_rate+1
        if ships_needed < ships_available:
            strategy = Strategy(planetwars.priority.Attack)
            log.debug("Doing Kamikaze attack")
            strategy.issue_order(self.turn, my_start, enemy_planet, ships_available)
            self.universe.add_strategy(strategy)
            return True
        return False
  