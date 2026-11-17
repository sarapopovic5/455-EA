"""
CISC 455 Group 17 - Role 2: EA Engineer
Evolves a 56-day training plan. Each gene is one day: 0 rest, 1 easy, 2 moderate, 3 hard.
"""

import random
from fitness import score as real_score

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

def crossover(parent1, parent2, method, rng):
    """Combine two parents into two children."""

    if method == "week":
        # one cut, only between weeks: after day 7, 14, ..., 49
        cut = WEEK * rng.randint(1, DAYS // WEEK - 1)
        child1 = parent1[:cut] + parent2[cut:]
        child2 = parent2[:cut] + parent1[cut:]

    else:
        # uniform: each day comes from either parent, 50/50
        child1, child2 = [], []
        for g1, g2 in zip(parent1, parent2):
            if rng.random() < 0.5:
                child1.append(g1)
                child2.append(g2)
            else:
                child1.append(g2)
                child2.append(g1)
    return child1, child2

def mutate(plan, creep_rate, swap_rate, rng):
    """Return a mutated copy of plan (the original is not changed)."""

    plan = plan[:]
    # creep: each day has a small chance to move up or down one level, kept inside 0-3
    for d in range(DAYS):
        if rng.random() < creep_rate:
            plan[d] = min(3, max(0, plan[d] + rng.choice([-1, 1])))

    # swap: sometimes swap two days inside one week (the week's total stays the same)
    if rng.random() < swap_rate:
        start = WEEK * rng.randrange(DAYS // WEEK)
        a, b = rng.sample(range(start, start + WEEK), 2)
        plan[a], plan[b] = plan[b], plan[a]
    return plan

def run_ea(seed, settings=None, score=real_score):
    """Run the EA once. Returns (best_plan, best_score, history), where history = {"best": [...], "avg": [...]} with one value per generation."""

    s = {**DEFAULT_SETTINGS, **(settings or {})}
    rng = random.Random(seed)

    # initialization: random plans, each scored once
    population = [random_plan(rng) for _ in range(s["pop_size"])]
    fitness = [score(p) for p in population]
    n_keep = int(s["pop_size"] * s["keep_fraction"])
    n_children = s["pop_size"] - n_keep

    history = {"best": [], "avg": []}
    for gen in range(s["generations"]):
        # make children: select two parents, maybe cross them, then mutate
        offspring = []
        while len(offspring) < n_children:
            p1 = tournament(population, fitness, s["tournament_size"], rng)
            p2 = tournament(population, fitness, s["tournament_size"], rng)
            if rng.random() < s["crossover_rate"]:
                c1, c2 = crossover(p1, p2, s["crossover"], rng)
            else:
                c1, c2 = p1[:], p2[:]
            offspring.append(mutate(c1, s["creep_rate"], s["swap_rate"], rng))
            offspring.append(mutate(c2, s["creep_rate"], s["swap_rate"], rng))
        offspring = offspring[:n_children]
        off_fitness = [score(c) for c in offspring]

        # survivor selection: best n_keep parents + all children
        ranked = sorted(range(len(population)), key=lambda i: fitness[i], reverse=True)[:n_keep]
        population = [population[i] for i in ranked] + offspring
        fitness = [fitness[i] for i in ranked] + off_fitness

        # record this generation for experiments and plots
        history["best"].append(max(fitness))
        history["avg"].append(sum(fitness) / len(fitness))

    best = max(range(len(population)), key=lambda i: fitness[i])
    return population[best], fitness[best], history

if __name__ == "__main__":
    plan, best, hist = run_ea(seed=1)
    print("Best score:", best)
    print("Weekly loads:", [sum(plan[w:w + WEEK]) for w in range(0, DAYS, WEEK)])
    for w in range(0, DAYS, WEEK):
        print(f"Week {w // WEEK + 1}:", plan[w:w + WEEK])