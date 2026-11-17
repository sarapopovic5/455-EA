"""
CISC 455 Group 17 - Role 2: EA Engineer
Evolves a 56-day training plan. Each gene is one day: 0 rest, 1 easy, 2 moderate, 3 hard.
"""

import random

DAYS = 56
WEEK = 7
LEVELS = [0, 1, 2, 3]

DEFAULT_SETTINGS = {
    "pop_size": 100,          # number of plans in the population
    "generations": 200,       # stopping condition
    "tournament_size": 3,     # plans compared per parent pick
    "crossover_rate": 0.8,    # chance two parents are combined
    "crossover": "week",      # "week" = cut between weeks, "uniform" = mix day by day
    "creep_rate": 1 / DAYS,   # chance each day moves up or down one level
    "swap_rate": 0.5,         # chance a child gets two days swapped within one week
    "keep_fraction": 0.5,     # best 50% of parents survive each generation
}


def fake_score(plan):
    """Stand-in until Sara's score() is ready. Best possible = 8 weeks x 14 = 112."""
    total = sum(plan)
    over_cap = 0
    for w in range(0, DAYS, WEEK):
        over_cap += max(0, sum(plan[w:w + WEEK]) - 14)
    return total - 2 * over_cap

def random_plan(rng):
    """One random plan: 56 days, each day picked evenly from 0-3."""
    return [rng.choice(LEVELS) for _ in range(DAYS)]

def tournament(population, fitness, k, rng):
    """Pick k different plans at random; return the one with the highest score."""
    contestants = rng.sample(range(len(population)), k)
    winner = max(contestants, key=lambda i: fitness[i])
    return population[winner]