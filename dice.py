"""Functions that simulate dice rolls.

A dice function takes no arguments and returns a number from 1 to n
(inclusive), where n is the number of sides on the dice.

Types of dice:

 -  Dice can be fair, meaning that they produce each possible outcome with equal
    probability.

 -  For testing functions that use dice, we use deterministic dice that always
    cycle among a fixed set of values when rolled.
"""

import random, time
from random import randint


def make_fair_dice(sides):
    """Return a die that returns 1 to SIDES with equal chance."""
    assert type(sides) == int and sides >= 1, 'Illegal value for sides'
    def dice():
        return randint(1,sides)
    return dice

four_sided = make_fair_dice(4)
six_sided = make_fair_dice(6)

def make_test_dice(*outcomes):
    """Return a die that cycles deterministically through OUTCOMES.

    This function uses Python syntax/techniques not yet covered in this course.

    >>> dice = make_test_dice(1, 2, 3)
    >>> dice()
    1
    >>> dice()
    2
    >>> dice()
    3
    >>> dice()
    1
    >>> dice()
    2
    """
    assert len(outcomes) > 0, 'You must supply outcomes to make_test_dice'
    for o in outcomes:
        assert type(o) == int and o >= 1, 'Outcome is not a positive integer'
    index = len(outcomes) - 1
    def dice():
        nonlocal index
        index = (index + 1) % len(outcomes)
        return outcomes[index]
    return dice

def make_n_outcomes(n_rolls: int, dice = six_sided) -> list:
    """Returns outcomes resulting from rolling a dice n_rolls times"""
    outcomes = []
    for _ in range(n_rolls):
        outcomes.append(dice())
    return outcomes

def mersenne_cracker(rc, gen_bits: int = 624):
    random.seed(time.time())
    for i in range(gen_bits):
        rc.submit(random.randint(0, 4294967294))
        # Could be filled with random.randint(0,4294967294) or random.randrange(0,4294967294)