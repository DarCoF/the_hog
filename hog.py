"""The Game of Hog."""
from sys import platform
from audioop import avg
from platform import platform
from time import sleep
import time
from dice import four_sided, make_n_outcomes, mersenne_cracker, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact
from randcrack import RandCrack

import multiprocessing
from multiprocessing import Queue
if platform == 'Windows':
    try:
        multiprocessing.set_start_method('spawn')
    except Exception as e:
        print('ERROR:', e)
elif platform == 'Linux':
    try:
        multiprocessing.set_start_method('fork')
    except Exception as e:
        print('ERROR:', e)
else:
    OSError('OS not compliant with current implementation')


GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Simulate rolling the DICE exactly NUM_ROLLS > 0 times. Return the sum of
    the outcomes unless any of the outcomes is 1. In that case, return 1.

    num_rolls:  The number of dice rolls that will be made.
    dice:       A function that simulates a single dice roll outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    # BEGIN PROBLEM 1
    "*** YOUR CODE HERE ***"
    total, k = 0, 0
    while k < num_rolls:
        roll = dice()
        if roll == 1:
            return 1
        total, k = total + roll, k + 1
    return total
    # END PROBLEM 1

def find_ones_in_roll(num_rolls, dice=six_sided):
    k = 0
    while k < num_rolls:
        roll = dice()
        if roll == 1:
            return 1
        k += 1
    return 0

def free_bacon(score):
    """   
    Return the points scored from rolling 0 dice (Free Bacon).

    Args:
        score (int):  The opponent's current score.

    Returns:
        int: The free bacon score in a single turn.
    """
    # BEGIN PROBLEM 2
    "*** YOUR CODE HERE ***"
    points_in_turn = max([int(d) for d in str(score)]) + 1
    return points_in_turn
    # END PROBLEM 2

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    "*** YOUR CODE HERE ***"
    if num_rolls == 0:
        return free_bacon(opponent_score)
    else:
        return roll_dice(num_rolls, dice)

# Playing a game

def select_dice(score, opponent_score): # hog wild rule
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).

    >>> select_dice(4, 24) == four_sided
    True
    >>> select_dice(16, 64) == six_sided
    True
    >>> select_dice(0, 0) == four_sided
    True
    """
    "*** YOUR CODE HERE ***"
    if (score + opponent_score) % 7 == 0:
        return four_sided
    elif (score + opponent_score) == 0:
        return four_sided
    else:
        return six_sided

def swine_swap(score0: int, score1: int ) -> int:
    """ A rule that compares if any of the input values pass to the formal parameters is double the other. In that case, values as swaped and returned.

    Args:
        score0 (int): first integer representing a player's score
        score1 (int): second integer representing a player's score

    Returns:
        score0 (int): returned score value after applying swine swap rule (if applicable). Otherwise, returns same input value.
        score1 (int): returned score value after applying swine swap rule (if applicable). Otherwise, returns same input value.
    """
    if score0 or score1 == 0:
        return score0, score1
    elif score0 / score1 == 2.0 or score1 / score0 == 2.0:
        score0, score1 = score1, score0
    return score0, score1

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    score, opponent_score = 0, 0
    "*** YOUR CODE HERE ***"
    while score or opponent_score < GOAL_SCORE:
        if who == 0:
            dice = select_dice(score, opponent_score) # select between six_sided or four_sided depending on hog wild rule.
            n_rolls = strategy0(score, opponent_score) # select number of dice to roll based on a certain strategy that considers both current and opponent scores.
            print('Current player throws {} dices'. format(n_rolls))
            score += take_turn(n_rolls, opponent_score, dice) # roll dices and add up to count/score.
            print(' Score is: {}'.format(score))
            if score >= 100:
                break            
            score, opponent_score = swine_swap(score, opponent_score) # apply swine swap rule in case conditions are met.
            print('Score and Opponent Score are: {}, {} respectively'.format(score, opponent_score))
        
        else:
            dice = select_dice(score, opponent_score)
            n_rolls = strategy1(opponent_score, score)
            print('Opponent throws {} dices'. format(n_rolls))
            opponent_score += take_turn(n_rolls, score, dice)
            print('Opponent score is: {}'.format(opponent_score))
            if opponent_score >= 100:
                break            
            score, opponent_score = swine_swap(score, opponent_score)
            print('Score and Opponent Score are: {}, {} respectively'.format(score, opponent_score))

        who = other(who) # swap player
    print('FINAL SCORE & OPPONENT SCORES ARE: {}, {}'.format(score, opponent_score))
    return score, opponent_score

#######################
# Phase 2: Strategies #
#######################

# GLOBAL VARIABLES
FINAL_BASELINE_NUM_ROLLS = 6
SCORE_MARGIN = 15
MY_BACON_MARGIN = 8
BACON_MARGIN_AHEAD = 7
BACON_MARGIN_BEHIND = 9
HOT_WILD_THRESHOLD = 40
SELECTOR = 1
FREE_BACON_RANGE = 11

# Basic Strategy
BASELINE_NUM_ROLLS = 5
BACON_MARGIN = 8

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments
def make_averaged(fn, num_samples=15625): #YEP. ESO ES 1 MILLÓN DE PARTIDAS :)))) y la fiesta comienza. Quedan muchas horas.
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    "*** YOUR CODE HERE ***"
    def average_score_n_turns(*args) -> int:
        average, n = 0, 0
        while n < num_samples:
            average += fn(*args) / num_samples
            n += 1
            print('REMAINING PLAYS {}'.format(num_samples - n))                   
        return round(average, 2)
    return average_score_n_turns

def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """
    "*** YOUR CODE HERE ***"
    max_score = 0
    avg_scores = []
    for n in range(1, 11):
        average_n = make_averaged(roll_dice, 10000)(n, dice)
        assert average_n > 0, 'average result must be positive.'
        avg_scores.append(average_n)
        print('{} dice scores {} on average'.format(n, round(average_n, 1)))
        if average_n > max_score:
            max_score = average_n
            curr_max_val_n_idx = (n, max_score)    
    return curr_max_val_n_idx, avg_scores


def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(BASELINE_NUM_ROLLS)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results


def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if False: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))
    
    if False: #
        print('free_bacon_impact_study', avg_win_rate_free_vs_no_free_bacon(FREE_BACON_RANGE))

    if False: # Change to True to test predictive strategy
        print('Predictive strategy', average_win_rate(predictive_strategy(mersenne_cracker, 10)))
    
    if True: # Test predictive strategy with multi-threading
        queue = start_worker_multiprocess(32)
        results = get_results_from_queue(queue)
        print("Average win rate for each thread is {}. Final average win rate for 1m plays is {}".format(results, sum(results) / len(results)))       

    "*** You may add additional experiments as you wish ***"

# Strategies
# Basic bacon strategy
def bacon_strategy(score, opponent_score):
    """This strategy rolls 0 dice if that gives at least BACON_MARGIN points,
    and rolls BASELINE_NUM_ROLLS otherwise.

    >>> bacon_strategy(0, 0)
    5
    >>> bacon_strategy(70, 50)
    5
    >>> bacon_strategy(50, 70)
    0
    """
    "*** YOUR CODE HERE ***"
    if free_bacon(opponent_score) >= BACON_MARGIN:
        return 0
    else:
        return BASELINE_NUM_ROLLS

# Basic swap strategy
def swap_strategy(score, opponent_score):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls BASELINE_NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least BACON_MARGIN points and rolls
    BASELINE_NUM_ROLLS otherwise.

    >>> swap_strategy(23, 60) # 23 + (1 + max(6, 0)) = 30: Beneficial swap
    0
    >>> swap_strategy(27, 18) # 27 + (1 + max(1, 8)) = 36: Harmful swap
    5
    >>> swap_strategy(50, 80) # (1 + max(8, 0)) = 9: Lots of free bacon
    0
    >>> swap_strategy(12, 12) # Baseline
    5
    """
    "*** YOUR CODE HERE ***"
    if opponent_score / (score + free_bacon(opponent_score)) == 2.0:
        return 0
    elif (score + free_bacon(opponent_score)) / opponent_score == 2.0:
        return BASELINE_NUM_ROLLS
    else:
        return bacon_strategy(score, opponent_score)

# Final Strategy
def is_multiple(multiple, base) -> bool:
    if multiple % base == 0:
        return True
    else:
        return False

def alternate_rolls(selector) -> int:
    if selector == 1:
        return FINAL_BASELINE_NUM_ROLLS
    if selector == (-1):
        return FINAL_BASELINE_NUM_ROLLS + 1

def my_bacon_strategy(score, opponent_score, margin) -> int:
    """This strategy rolls 0 dice if that gives at least BACON_MARGIN points,
    and rolls BASELINE_NUM_ROLLS otherwise.

    >>> bacon_strategy(0, 0)
    5
    >>> bacon_strategy(70, 50)
    5
    >>> bacon_strategy(50, 70)
    0
    """
    "*** YOUR CODE HERE ***"
    if free_bacon(opponent_score) >= margin:
        if sum(free_bacon(opponent_score), score) / opponent_score == 2.0:
            return FINAL_BASELINE_NUM_ROLLS 
        return 0
    else:
        return FINAL_BASELINE_NUM_ROLLS

def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.

    *** YOUR DESCRIPTION HERE ***
    1- Always roll 6s. After 1000000 rolls for each number of dice, 6 dices consistenly shows the highest avg count per turn. Closely followed by 5 and 7 rolls.
    2- The average count per roll with 5 & 6 dices is 8.6 and 8.7 respectively. Therefore, always use free bacon when opponent score is higher than 80.
    3- If opponent is winning by a big leap (SCORE_MARGIN = 20) increase risk in turns. Up number of rolls to 7 or 8.
    4- Always check for swine swap when opponent is ahead.
    5- When rolling four-sided dices, always choose 4. Maximize average count.
    6- Always consider using hot wild if opponent score is >40. Free bacon will give you 6 points and, in turn, the max average for a four-sided dice throwing 5 dices is 4.3.


    """
    "*** YOUR CODE HERE ***"
    SELECTOR = 1
    if opponent_score > HOT_WILD_THRESHOLD and is_multiple(sum([opponent_score, score, free_bacon(opponent_score)]), 7):
        return 0
    else:
        if score >= opponent_score:
            return my_bacon_strategy(score, opponent_score, BACON_MARGIN_AHEAD)        
        elif score < opponent_score:
            if opponent_score / (score + free_bacon(opponent_score)) == 2.0:
                return 0
            elif (opponent_score - score) > SCORE_MARGIN:
                SELECTOR = SELECTOR * (-1)
                return alternate_rolls(SELECTOR)
            else:
                return my_bacon_strategy(score, opponent_score, BACON_MARGIN_BEHIND)


def select_free_bacon_margin(margin):
    """ A higher-order fucntion that returns a function with a simple strategy. Runs free bacon in case opponent score is higher than margin or 5 dices otherwise. 
    This is meant to compare the impact of using different free bacon margins against the reference of not using free bacon at all.

    Args:
        n (_type_): _description_
    """

    def get_strategy(score, opponent_score):
        """_summary_

        Args:
            score (_type_): _description_
            opponent_score (_type_): _description_

        Returns:
            _type_: _description_
        """
        if free_bacon(opponent_score) >= margin:
            return 0
        else:
            return BASELINE_NUM_ROLLS
    return get_strategy

# Predictive strategy no threading
def get_index_on_iterable(iterable: list = [], condition: int = 0) -> int:
    for d in iterable:
        if d == condition:
            return iterable.index(d)

def predictive_strategy(fn, max_dices: int, dice_sides: int = 6, rc = RandCrack(), n_bits = 624, ) -> int:
    """ A higher-order function that returns a function computing the next max_dices values based on a predictor.

    Args:
        fn (function): a pseudo-random predictor function.
        max_dices (int): the maximum number of dices to be predicted.
        dices_sides (int, optional): the type of dice. Defaults to 6.
    """
    assert max_dices < 11 # never roll more than 10 dices
    # TODO: esto es una chapuza
    def get_n_dices(*args) -> int:
        """A function that returns a number of dices.
        """
        rc = RandCrack()
        fn(rc, n_bits) # call function
        dices_next = []
        for _ in range(max_dices):
            dices_next.append(rc.predict_randrange(1, dice_sides + 1))
        if 1 not in dices_next:
            return len(dices_next)
        else:
            index = get_index_on_iterable(dices_next, 1) # Return el índice donde está el primer uno
            if sum(dices_next[:index]) <= free_bacon(args[1]):
                return 0
            else:
                return index
    return get_n_dices

# Predictive strategy using multiprocessing

def worker(num, queue):
    """Thread worker function"""
    print("Worker %d started" % num)
    time.sleep(2)
    result = average_win_rate(predictive_strategy(mersenne_cracker, 10))
    queue.put(result)
    print("Worker %d finished" % num)
    
def start_worker_multiprocess(num_proc):
    queue = Queue()
    processes = []
    for i in range(num_proc):
        p =  multiprocessing.Process(target=worker, args=(i, queue))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    return queue

def get_results_from_queue(queue):
    results = []
    while not queue.empty():
        result = queue.get()
        results.append(result)
    return results


##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.

def get_int(prompt, min):
    """Return an integer greater than or equal to MIN, given by the user."""
    choice = input(prompt)
    while not choice.isnumeric() or int(choice) < min:
        print('Please enter an integer greater than or equal to', min)
        choice = input(prompt)
    return int(choice)

def interactive_dice():
    """A dice where the outcomes are provided by the user."""
    return get_int('Result of dice roll: ', 1)

def make_interactive_strategy(player):
    """Return a strategy for which the user provides the number of rolls."""
    prompt = 'Number of rolls for Player {0}: '.format(player)
    def interactive_strategy(score, opp_score):
        if player == 1:
            score, opp_score = opp_score, score
        print(score, 'vs.', opp_score)
        choice = get_int(prompt, 0)
        return choice
    return interactive_strategy

def roll_dice_interactive():
    """Interactively call roll_dice."""
    num_rolls = get_int('Number of rolls: ', 1)
    turn_total = roll_dice(num_rolls, interactive_dice)
    print('Turn total:', turn_total)

def take_turn_interactive():
    """Interactively call take_turn."""
    num_rolls = get_int('Number of rolls: ', 0)
    opp_score = get_int('Opponent score: ', 0)
    turn_total = take_turn(num_rolls, opp_score, interactive_dice)
    print('Turn total:', turn_total)

def play_interactive():
    """Interactively call play."""
    strategy0 = make_interactive_strategy(0)
    strategy1 = make_interactive_strategy(1)
    score0, score1 = play(strategy0, strategy1)
    print('Final scores:', score0, 'to', score1)

@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--interactive', '-i', type=str,
                        help='Run interactive tests for the specified question')
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.interactive:
        test = args.interactive + '_interactive'
        if test not in globals():
            print('To use the -i option, please choose one of these:')
            print('\troll_dice', '\ttake_turn', '\tplay', sep='\n')
            exit(1)
        try:
            globals()[test]()
        except (KeyboardInterrupt, EOFError):
            print('\nQuitting interactive test')
            exit(0)
    elif args.run_experiments:
        run_experiments()
