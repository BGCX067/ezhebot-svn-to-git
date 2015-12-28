__author__ = 'lynx'

from planetwars.util import TypedSetBase

class Priority(object):
    def __init__(self, value, name):
        self.value = value
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Priority %s>" % self.name

    def __cmp__(self, other):
        return self.value.__cmp__(other.value)

    def __or__(self, other):
        if isinstance(other, Priority):
            return Priorities((self, other))
        elif isinstance(other, Priorities):
            return other | self
        else:
            raise TypeError("Invalid operation for <Player> and %s" % type(other))

class Priorities(TypedSetBase):
    accepts = (Priority, )

Reserve = Priority(0, "Reserve")
Defence = Priority(10, "Defence")
Attack = Priority(20, "Attack")
Recapture = Priority(50, "Recapture")
Retreat = Priority(80, "Retreat")
Expand = Priority(100, "Expand")
Supply = Priority(1000, "Supply")
Misc = Priority(10000, "Misc")


  