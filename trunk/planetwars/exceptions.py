__author__ = 'lynx'

class NoMoreShipsError(Exception):
   def __init__(self, value):
       self.parameter = value
   def __str__(self):
       return repr(self.parameter)
   @property
   def value(self):
       return self.parameter

class GameRulesError(Exception):
   def __init__(self, value):
       self.parameter = value
   def __str__(self):
       return repr(self.parameter)