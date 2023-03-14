from dice import four_sided, six_sided, make_test_dice
from hog import make_averaged, roll_dice, select_free_bacon_margin, average_win_rate, winner, always_roll, BASELINE_NUM_ROLLS
import csv
import json

import matplotlib.pyplot as plt

# UTILS
def export_to_format(format):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if format == 'csv':
                filename = func.__name__ + '.csv'
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(result)
            elif format == 'json':
                filename = func.__name__ + '.json'
                with open(filename, 'w') as file:
                    json.dump(result, file)
            elif format == 'txt':
                filename = func.__name__ + '.txt'
                with open(filename, 'w') as file:
                    for item in result:
                        file.write(str(item) + '\n')
            elif format == 'plot':
                for keys, values in kwargs.items():
                    values = values
                filename = func.__name__ + values +'.png'
                plt.savefig(filename)
            return result
        return wrapper
    return decorator


# ANALYSIS OF FAIR DICES
def get_avg_score_per_n_dices(dice=six_sided, n_samples = 100000, max_dices = 10):
    """ Return a list registering the average count per number of dices rolled in n_samples turns considering the pig-out rule (see hog.py).

    Args:
        dice (_type_, optional):  A model of a fair six-sided dice based on randint module. Defaults to six_sided.
        n_samples (int, optional): Number of times the dice roll is repeated. Defaults to 10000.
        max_dices (int, optional): Maximum permissible number of dices to be rolled per turn.

    Returns:
        _type_: list of average scores per number of dices in n_samples.
    """
    avg_scores = []
    for n in range(1, max_dices + 1):
        average_n = make_averaged(roll_dice, n_samples)(n, dice)
        assert average_n > 0, 'average result must be positive.'
        avg_scores.append(average_n)
        print('{} dice scores {} on average'.format(n, round(average_n, 1)))
    return avg_scores

# Analyze effectiveness of different free bacon thresholds. 
def get_fb_impact_over_win_rate(margin, baseline=always_roll(BASELINE_NUM_ROLLS)) -> dict:
    """ A function that stores the average win rate for different free bacon margins (0-11) and returns the percentage diff of each margin against the reference value (no free bacon, margin > 10).

    Args:
        margin (int): Maximum points scored by free bacon + 1 

    Returns:
        dict: a dictionary with keys indicating each free bacon margin and values reflecting the win rate pertenage difference (positive or negative) with respect to the reference vale (no free bacon).
    """
    win_rate_per_free_bacon_margin = {}
    for m in range(1, margin + 1):
        win_rate_as_player_0 = 1 - make_averaged(winner, 10000)(select_free_bacon_margin(m), baseline)
        win_rate_as_player_1 = make_averaged(winner, 10000)(baseline, select_free_bacon_margin(m))
        win_rate_m = (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results for free bacon threshold m
        win_rate_per_free_bacon_margin[str(m)] = win_rate_m
    
    for key in win_rate_per_free_bacon_margin.keys():
        win_rate_per_free_bacon_margin[key] = win_rate_per_free_bacon_margin[key] - win_rate_per_free_bacon_margin[str(margin)] 
    return win_rate_per_free_bacon_margin



# GRAPH VALUES
@export_to_format('plot')
def bar_plot(data, format):
    """ A generic function for creating a bar graph in Matplotlib.

    Args:
        format (_type_): a list of strings defining X, Y labels and Title in that order.
        data (list, optional): a list containing data to be plotted. 

    Returns:
        _type_: a bar graph.
    """
    plt.bar(range(len(data)), data) # creating the bar plot
    x_label, y_label, title = [d for d in format]
    plt.xticks(range(len(data)), [(x + 1) for x in range(len(data))]) # modify xticks
    plt.xlabel(x_label) # label x
    plt.ylabel(y_label) # label Y
    plt.title(title) # graph title



if __name__ == '__main__':
    avg_scores = get_avg_score_per_n_dices()
    win_rate_diff_to_ref = get_fb_impact_over_win_rate(11)
    win_rate_list = list(win_rate_diff_to_ref.values())        
        
    bar_plot(avg_scores, ['Number of Dices', 'Average Count per Roll', 'Average count per roll per number of dices'])
    bar_plot(win_rate_list, ['Free bacon threshold', 'Effect percentage against ref. (no free bacon)', 'Percentual change in win rate based on free bacon threshold'])