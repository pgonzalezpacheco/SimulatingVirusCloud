from enum import Enum


class Type(Enum):
    WORKPLACE = 0
    SCHOOL = 1
    HOME = 2
    OTHER = 3


class Infection(Enum):
    INCUBATION = 0
    INFECTION_ASIMP = 1
    INFECTION_SIMP = 2
    IMMUNE = 3
    DEATH = 4
