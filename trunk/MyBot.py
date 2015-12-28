from planetwars import BaseBot, Game
from planetwars.universe2 import Universe2
from planetwars.planet2 import Planet2
from planetwars.universe import player
from logging import getLogger
from planetwars.orderchain import Strategy
from planetwars.knapsack import KnapSack
import planetwars
from planetwars.litepathfinder import LitePathFinder
from math import ceil
from planetwars.future import FuturePrediction
from planetwars.botlogic import Logic


log = getLogger(__name__)

# Bot is assuming, there are only 2 players in the game
#todo: 1. implement running away. If we cannot win the battle next turn, send the ships to the nearest planets that is mine in future
#todo: 1. use running away only if there are no ships in flight to this planet
#todo: 2. use c-means to determine fronts
class MyBot(BaseBot):
    @property
    def turn_count(self):
        return self.universe.turn_count

    #caching everything we can on move 1
    def run_caches(self):
        for x in self.universe.planets:
            for y in self.universe.planets:
                if x == y:
                    continue
                else:
                    x.distance(y)

    def evaluate_neutral(self, travelTime, growthRate, numDefenders, myShips):
        #There exists some ratio between TravelTime, GrowthRate, and NumDefenders upon which all planets can be ranked
        # (closer,higher,less are best.) There also exists some relationship between YourNumShips and these
        # ranked planets (in terms of both current_ship_usage and future_ship_growth) that determines the optimal
        # attack plan. (all this is balled up in my "quoted" list of attributes, strategy.)
        ships_lost = myShips - numDefenders
        ratio = float(growthRate) / float(travelTime)*float(ships_lost)+1
        return ratio

    def do_defence(self, planet, fleet):
        p0 = planet
        f = fleet
        p1 = p0.in_future(f.turns_remaining)

        in_turns = f.turns_remaining
        ships_needed = p1.ship_count

        for my_p in self.universe.get_closest_planets(p0):
            if my_p == p0:
                continue
            distance = my_p.distance(p0)
            ships_available = my_p.ships_available
            if distance < in_turns and ships_available >= ships_needed:
                #we have a winner. this planet will issue ships sending
                #todo: implement more sophisticated algorithm
                strategy = Strategy(planetwars.priority.Defence)
                strategy.issue_order(self.universe.game.turn_count + in_turns - distance, my_p, p0, ships_needed)
                self.universe.add_strategy(strategy)
                return True
        return False

    def do_reserve(self, planet, fleet):
        p0 = planet
        f = fleet

        strategy = Strategy(planetwars.priority.Reserve)
        strategy.issue_order(self.universe.game.turn_count + f.turns_remaining, p0, p0, f.ship_count)
        self.universe.add_strategy(strategy)
        return True



    def define_strategies(self):
        if self.turn_count == 1:
            self.run_caches()

        #do future prediction
        future = FuturePrediction(self.universe)
        future.predict()

        logic = Logic(self.universe, future)
        logic.define_strategies()

        return

        #find "head" planet. Will send ships there
        #currently assuming that is a planet closer to enemy strongest planet
        my_head = None

        enemy_head = self.universe.enemies_strongest_planet
        min_d = 999999
        for my_p in self.universe.my_planets:
            d = my_p.distance(enemy_head)
            if d < min_d:
                min_d = d
                my_head = my_p
        log.debug("determined my head here %s" % my_head)

        logic.do_expand()





        #todo:change this very stupid attack algorithm
        attack_short_list = list()

        #calculate future for enemy_fleet
        for f in self.universe.enemy_fleets:
            if f.taken_into_account:
                continue
            f.taken_into_account = True

            #check later if we want to counter
            if not f.source in attack_short_list:
                attack_short_list.append((f.source, f.trip_length - f.turns_remaining))

            p0 = f.destination
            p1 = p0.in_future(f.turns_remaining)
            #if I am the owner in future - reserve ships for the battle
            #todo: we can somehow reserve more then needed
            #we are taking into account all planet fleet, including Attack and other forces
            #and then doing an additional reserve
            if p1.owner == player.ME:
                self.do_reserve(p0, f)
                continue
            #enemy is doing something evil. He always does
            if p0.owner == player.ENEMIES:
                continue
            #enemy is attacking neutral planet. check if we can take it out
            if p0.owner == player.NOBODY:
                in_turns = f.turns_remaining+1
                p2 = p0.in_future(in_turns)
                issued = False
                for my_p in self.universe.my_planets:
                    distance = my_p.distance(p0)
                    ships_needed = p2.ship_count+1
                    if distance <= in_turns and my_p.ships_available >= ships_needed:
                        #we have a winner. this planet will issue ships sending
                        #todo: implement more sophisticated algorithm
                        on_turn = self.universe.game.turn_count + in_turns - distance
                        msg = "RECAPTURE! on turn %s sending %s ships from %s to %s" % \
                              (on_turn, ships_needed, my_p, p0)
                        log.debug(msg)
                        strategy = Strategy(planetwars.priority.Recapture)
                        strategy.issue_order(on_turn, my_p, p0, ships_needed)
                        self.universe.add_strategy(strategy)
                        issued = True
                        break
                if not issued:
                    if not f. source in attack_short_list:
                        attack_short_list.append((f.source, in_turns))

            #enemy is attacking our and will take out the planet
            if p0.owner == player.ME:
                issued = self.do_defence(p0, f)
                in_turns = f.turns_remaining

                if not issued:
                    if not f. source in attack_short_list:
                        attack_short_list.append((f.source, in_turns))

        #going through attack short list
        for item in attack_short_list:
            enemy_p = item[0]
            min_turns = item[1]
            for p in self.universe.my_planets:
                distance = enemy_p.distance(p)
                enemy_p1 = enemy_p.in_future(distance)
                ships_needed = enemy_p1.ship_count + 1
                if p.ships_available >= ships_needed:
                    time_delta = max(distance - min_turns, 0)
                    turn = self.universe.game.turn_count + time_delta
                    strategy = Strategy(planetwars.priority.Attack)
                    log.debug("%s" % strategy)
                    log.debug("--giving orders on turn %d from %s send ships %d to %s" % \
                              (turn, p, ships_needed, enemy_p))
                    strategy.issue_order(turn, p, enemy_p, ships_needed)
                    self.universe.add_strategy(strategy)
                    break

        #todo: add step. prediction for fleet, that is on enemy's planet. pessimistic planning

        return
        #redistribute free ships from faraway planets towards the "head"
        if self.universe.turn_count % 2 == 1:
            supply_planets = self.universe.get_closest_planets(my_head, max_radius=10)
        else:
            supply_planets = self.universe.get_far_planets(my_head, min_radius=10)
        for my_p in supply_planets:
            if my_p == my_head:
                continue
            ships_available = my_p.ships_available
            if ships_available <= 0:
                continue
            ships_to_send = int(ceil(float(ships_available) / 100 * 70))
            try:
                path = LitePathFinder(my_head, my_p)
                path.issue_supply_orders(self.universe.game.turn_count, int(ships_to_send))
            except:
                log.error("Exception in pathfinding", exc_info=True)
        return

    def execute_strategies(self):
        self.universe.strategies.execute(self.universe.turn_count)

    def do_turn(self):
        log.info("I'm starting my turn %s" % self.universe.game.turn_count)

        self.define_strategies()
        self.execute_strategies()
        return


Game(MyBot, universe_class=Universe2, planet_class=Planet2)