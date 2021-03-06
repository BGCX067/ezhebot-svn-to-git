#!/usr/bin/env python
#

"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
"""
# Strategy: balance between colonizers, warriors, saboteurs
# 0. no max_fleet count
# 1. our planet count < MIN_PLANET_COUNT -> expand quickly (colonize) / take into account GrowthRate
# 2. find enemy closest planet to ours attack front
# 2.1 if there are no neutral planets between attack fronts -> attack many to one
# 2.2 if there are neutral planets -> expand many to one
# 2.3 do supply chain from our most distant planets to our attack front
# 3. find enemy strongest planet, find our most distant strongest planet -> attack (saboteur)


from PlanetWars import PlanetWars
from math import floor

FLEETS_COUNT_MAX = 32
ATTACK_PERCENTAGE = 99
MIN_FLEET_SIZE = 13

def DoTurn(pw):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(pw.MyFleets()) >= FLEETS_COUNT_MAX:
        return
    # (2) Find my strongest planet.
    source = -1
    source_score = -999999.0
    source_num_ships = 0
    my_planets = pw.MyPlanets()
    for p in my_planets:
        score = float(p.NumShips())
        if score > source_score:
            source_score = score
            source = p.PlanetID()
            source_num_ships = p.NumShips()
    source_num_ships = floor(float(source_num_ships) * float(ATTACK_PERCENTAGE) / float(100))
    if source_num_ships < MIN_FLEET_SIZE:
        return

    # (3) find the nearest weakest enemy planet.
    dest = -1
    min_distance = 999999.0
    not_my_planets = pw.EnemyPlanets()
    for p in not_my_planets:
        distance = pw.Distance(source, p.PlanetID())
        future_ship_number = float(p.NumShips()) + float(distance)*float(p.GrowthRate()) + 10
        if distance < min_distance and source_num_ships > future_ship_number:
            min_distance = distance
            dest = p.PlanetID()

    #if not found enemy planet to shoot at, find neutral target
    not_my_planets = pw.NotMyPlanets()
    if dest == -1:
        min_distance = 999999.0
        for p in not_my_planets:
            distance = pw.Distance(source, p.PlanetID())
            if distance < min_distance and source_num_ships > float(p.NumShips()):
                min_distance = distance
                dest = p.PlanetID()

    # (4) Send the ships
    if source >= 0 and dest >= 0:
        pw.IssueOrder(source, dest, source_num_ships)


def main():
    map_data = ''
    while(True):
        current_line = raw_input()
        if len(current_line) >= 2 and current_line.startswith("go"):
            pw = PlanetWars(map_data)
            DoTurn(pw)
            pw.FinishTurn()
            map_data = ''
        else:
            map_data += current_line + '\n'


if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        main()
    except KeyboardInterrupt:
        print 'ctrl-c, leaving ...'
