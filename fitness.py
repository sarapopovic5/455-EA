"""
Fitness model

score(plan) simulates an athlete following a 56-day plan with a Banister
fitness-fatigue model, computes race-day performance P, and subtracts a
penalty for every broken training rule:

    F = P - LAMBDA * violations

A plan is a list of 56 ints, each 0 = rest, 1 = easy, 2 = moderate, 3 = hard.
Days 0-6 are week 1, days 7-13 are week 2, and so on. Higher score is better.
score() never changes the plan and always gives the same score for the same plan.

"""

import math

# ---------------------------------------------------------------------------
# Model constants (assumptions from the draft, not fitted to a real athlete)
# ---------------------------------------------------------------------------
DAYS = 56
DAYS_PER_WEEK = 7

FITNESS_DECAY = math.exp(-1 / 28)  # ~0.965: fitness fades over ~28 days
FATIGUE_DECAY = math.exp(-1 / 7)   # ~0.867: fatigue fades over ~7 days

# Gain per day for each intensity 0..3
FITNESS_GAIN = [0.0, 1.0, 2.0, 3.0]   # f(w)
FATIGUE_GAIN = [0.0, 0.5, 1.5, 3.5]   # d(w)

# Race-day performance: P = BASE + K_FITNESS * fitness - K_FATIGUE * fatigue
BASE_PERFORMANCE = 100.0
K_FITNESS = 0.1
K_FATIGUE = 0.3

# Rules
MAX_WEEKLY_LOAD = 14     # rule 1: weekly load cap
MAX_WEEKLY_RAMP = 2      # rule 2: max rise in load over the previous week
STARTING_LOAD = 6        # athlete's load in the week before the plan (for week-1 ramp)
MAX_HARD_STREAK = 2      # rule 4: at most 2 hard days in a row
HARD = 3
REST = 0

LAMBDA = 2.0             # penalty weight


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
def simulate(plan):
    """Run the fitness-fatigue model day by day.

    Returns (fitness, fatigue): two lists of 56 values, the state at the end
    of each day. Useful for plotting (Role 4).
    """
    _check(plan)
    fit, fat = 0.0, 0.0
    fitness, fatigue = [], []
    for w in plan:
        fit = fit * FITNESS_DECAY + FITNESS_GAIN[w]
        fat = fat * FATIGUE_DECAY + FATIGUE_GAIN[w]
        fitness.append(fit)
        fatigue.append(fat)
    return fitness, fatigue


def performance(plan):
    """Race-day performance P after day 56 (no penalties)."""
    fitness, fatigue = simulate(plan)
    return BASE_PERFORMANCE + K_FITNESS * fitness[-1] - K_FATIGUE * fatigue[-1]


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
def weekly_loads(plan):
    """Sum of intensities for each of the 8 weeks."""
    return [sum(plan[i:i + DAYS_PER_WEEK]) for i in range(0, DAYS, DAYS_PER_WEEK)]


def violations(plan):
    """Return a dict with the size of each rule violation (0 = rule satisfied).

    cap    : sum over weeks of max(0, load - 14)
    ramp   : sum over weeks of max(0, load - previous load - 2);
             week 1 is compared against STARTING_LOAD
    rest   : number of weeks with no rest day (+1 per such week)
    streak : sum over runs of hard days of max(0, run length - 2)
    """
    _check(plan)
    loads = weekly_loads(plan)

    cap = sum(max(0, load - MAX_WEEKLY_LOAD) for load in loads)

    ramp = 0
    prev = STARTING_LOAD
    for load in loads:
        ramp += max(0, load - prev - MAX_WEEKLY_RAMP)
        prev = load

    rest = sum(
        1 for i in range(0, DAYS, DAYS_PER_WEEK)
        if REST not in plan[i:i + DAYS_PER_WEEK]
    )

    streak = 0
    run = 0
    for w in list(plan) + [None]:  # sentinel closes the last run
        if w == HARD:
            run += 1
        else:
            streak += max(0, run - MAX_HARD_STREAK)
            run = 0

    return {"cap": cap, "ramp": ramp, "rest": rest, "streak": streak}


def total_violations(plan):
    return sum(violations(plan).values())


# ---------------------------------------------------------------------------
# Fitness function used by the EA
# ---------------------------------------------------------------------------
def score(plan, lam=LAMBDA, rules=True):
    """F = P - lam * total violations. Higher is better.

    lam   : penalty weight (for the lambda experiments: 0.5, 2, 10)
    rules : set False to score P alone (the "rules off" experiment)
    """
    p = performance(plan)
    if not rules:
        return p
    return p - lam * total_violations(plan)


def _check(plan):
    if len(plan) != DAYS:
        raise ValueError(f"plan must have {DAYS} days, got {len(plan)}")
    for w in plan:
        if w not in (0, 1, 2, 3):
            raise ValueError(f"each day must be 0, 1, 2 or 3, got {w!r}")


if __name__ == "__main__":
    rest_only = [0] * DAYS
    print("rest-only plan:", score(rest_only))

    all_hard = [3] * DAYS
    print("all-hard plan :", round(score(all_hard), 3), violations(all_hard))

    # A simple legal plan: steady load of 8, then an easy final week
    week = [1, 2, 0, 2, 1, 2, 0]
    sample = week * 7 + [1, 0, 1, 0, 1, 0, 0]
    print("sample plan   :", round(score(sample), 3), violations(sample))
