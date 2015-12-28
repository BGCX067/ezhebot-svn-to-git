import priority
from logging import getLogger
from planetwars.exceptions import NoMoreShipsError

__author__ = 'ibo.ezhe@gmail.com'

log = getLogger(__name__)

class Order(object):
    def __init__(self, strategy, turn_number, planet_source, planet_destination, ship_count):
        self.turn = turn_number
        self.source = planet_source
        self.destination = planet_destination
        self.ship_count = ship_count
        self.strategy = strategy

    def execute(self):
        ship_count = self.ship_count
        if not ship_count or ship_count <= 0:
            raise AttributeError("ship count is null or less then 1 (%s)" % ship_count)
        if self.source.ship_count < ship_count:
            msg = "order from source=%s to dest=%s (has ships=%s, expected=%s)" % \
                  (self.source, self.destination, self.source.ship_count, ship_count)
            raise NoMoreShipsError(msg)
        if self.strategy.priority == priority.Reserve and \
           self.source == self.destination:
            log.debug("Executing Reserve order: %s ships" % ship_count)
        self.source.send_fleet(self.destination, ship_count)

class Strategy(object):
    def __init__(self, priority=priority.Misc):
        self.priority = priority
        self.orders = list()
        self.cancelled = False

    def issue_order(self, turn_number, planet_source, planet_destination, ship_count):
        order = Order(self, turn_number, planet_source, planet_destination, ship_count)
        self.orders.append(order)

    def execute(self, turn_number):
        if self.cancelled:
            return
        for o in self.orders:
            if(o.turn == turn_number):
                try:
                    o.execute()
                except NoMoreShipsError, e:
                    log.error("Strategy execution error! %s" % e.value)
                    self.cancel()

    def cancel(self):
        log.debug("Cancelling %s strategy with %d orders" % (self.priority, len(self.orders)))
        self.cancelled = True
        self.orders = list()

    def __repr__(self):
        return "[%s] orders (%d)" % (self.priority, len(self.orders))


class Strategies(object):
    def __init__(self):
        self.__strategies = dict()

    def append(self, strategy):
        strategies = self.get_matches_priority(strategy.priority)
        strategies.append(strategy)

    def get_matches_priority(self, priority):
        if not self.__strategies.has_key(priority):
            self.__strategies[priority] = list()
        return self.__strategies[priority]

    def get_lesser_priority(self, priority):
        for k in sorted(self.__strategies.keys(), reverse=True):
            if k < priority:
                yield self.__strategies[k]
        return

    @property
    def items(self):
        for k in sorted(self.__strategies.keys()):
            for s in self.__strategies[k]:
                yield s
        return

    def execute(self, turn):
        for s in self.items:
            s.execute(turn)
  