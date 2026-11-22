# Performance Lab: Optimizing an 8-Week Training Plan with an EA

CISC 455 (Fall 2026), Group 17: Sara, Sarah, Esme, Omar, Petar.

An evolutionary algorithm searches for the 56-day training plan that gives the best predicted
race-day performance under a Banister fitness-fatigue model, while following four training rules.

## The problem

- **Plan:** a list of 56 integers, one per day: 0 = rest, 1 = easy, 2 = moderate, 3 = hard.
  Days 0-6 are week 1, days 7-13 are week 2, and so on.
- **Model:** each day, fitness = fitness x e^(-1/28) + f(w) and fatigue = fatigue x e^(-1/7) + d(w),
  with f = [0, 1, 2, 3] and d = [0, 0.5, 1.5, 3.5] for intensities 0-3.
  Race-day performance is **P = 100 + 0.1 x fitness - 0.3 x fatigue** (resting every day gives P = 100).
- **Rules:** weekly load (sum of the 7 days) is at most 14; it rises at most 2 over the previous week
  (the week before the plan counts as 6); every week has at least 1 rest day; at most 2 hard days in a row.
- **Score:** **P - lambda x violation units**, with lambda = 2. One violation unit = 1 load point over
  the cap or the ramp, 1 week with no rest day, or 1 hard day past 2 in a row.

## The EA

| Part | Choice |
|---|---|
| Representation | 56 integers (0-3), one gene per day |
| Population | 100 random plans |
| Parent selection | Tournament, k = 3 |
| Crossover | One-point, cut only between weeks, rate 0.8 (uniform crossover available as a setting) |
| Mutation | Creep: each day moves up or down 1 with probability 1/56; swap: two days inside one week, probability 0.5 per child |
| Survivor selection | Best 50 parents + 50 children |
| Stopping | 200 generations (10,100 evaluations per run) |

## Files

| File | What it does | Owner |
|---|---|---|
| `fitness.py` | `score(plan)`: simulates a plan and returns its fitness | Sara (Role 1) |
| `test_fitness.py` | Tests for the fitness model | Sara (Role 1) |
| `ea.py` | `run_ea(...)`: the evolutionary algorithm | Esme (Role 2) |
| `test_ea.py` | Tests for the EA | Esme (Role 2) |
| `experiments.py` | Runs every experiment setting with 10 seeds, saves `results/` | Esme (Roles 3-4) |
| `plots.py` | Turns `results/runs.json` into the figures in `figures/` | Esme (Roles 3-4) |
| `results/` | `summary.csv` (one row per setting) and `runs.json` (every run) | generated |
| `figures/` | 4 figures of the results (the charts in our slides use the same data) | generated |

## How to run

Requires Python 3 and matplotlib (for the figures only).

```
pip install -r requirements.txt
python ea.py                  # one EA run with the fitness model
python -m unittest -v         # run all 25 tests
python experiments.py         # all experiments (about 20 seconds), writes results/
python plots.py               # writes the figures to figures/
```

Every run uses a fixed seed (`random.Random(seed)`), so rerunning `experiments.py` reproduces
`results/` exactly.

## How the pieces connect

- **`score(plan, lam=2.0, rules=True)`** returns one number. Higher is better. It never changes `plan`,
  and the same plan always gets the same score. `lam` sets the penalty weight; `rules=False` scores
  performance only.
- **`run_ea(seed, settings, score)`** returns `(best_plan, best_score, history)`.
  `settings` is optional and overrides any default, e.g. `{"crossover": "uniform"}`.
  `score` defaults to `fitness.score`. `history` is `{"best": [...], "avg": [...]}`, one value per generation.
  The same seed always gives the same result.

## Experiments and results

Every setting changes one thing from the baseline and runs with seeds 0-9 and the same budget:
10,100 evaluations per run (population 100, 50 new children per generation, 200 generations).

- **Mean best score:** final score (P - lambda x violation units), averaged over the 10 runs.
- **Success:** the run's best plan breaks no rules and is within 0.01 of the best legal P found by any run (102.244).
- **Evals to converge:** evaluations until the run first gets within 0.01 of its own final score (mean of 10 runs).

| Setting | Mean best score | SD | Mean P | Mean violation units | Legal runs | Success rate | Evals to converge |
|---|---|---|---|---|---|---|---|
| Baseline (lambda 2) | 102.237 | 0.005 | 102.237 | 0 | 10/10 | 6/10 | 5,390 |
| lambda 0 (no penalty) | 103.292 | 0.000 | 103.292 | 96 | 0/10 | 0/10 | 4,515 |
| lambda 0.02 | 102.388 | 0.006 | 102.648 | 13 | 0/10 | 0/10 | 4,865 |
| lambda 0.05 | 102.250 | 0.008 | 102.320 | 1.4 | 1/10 | 1/10 | 5,145 |
| lambda 0.1 | 102.237 | 0.005 | 102.237 | 0 | 10/10 | 7/10 | 5,880 |
| lambda 10 | 102.240 | 0.005 | 102.240 | 0 | 10/10 | 8/10 | 5,775 |
| Uniform crossover | 102.225 | 0.007 | 102.225 | 0 | 10/10 | 1/10 | 8,515 |
| No swap mutation | 102.194 | 0.015 | 102.194 | 0 | 10/10 | 0/10 | 5,395 |

**What we found**
- **The EA discovers tapering on its own.** Every baseline run finds the same weekly shape:
  8, 10, 12, 14, 14, 14, 9, 3 (build up, hold at the cap, taper), P = 102.24 vs 100 for resting.
- **Without a penalty the EA ignores the rules.** It trains hard every day for the first 5 weeks
  (21 per week, 96 violation units) to reach P = 103.29, about 1 point more than the legal plan.
- **The penalty only has to outweigh what breaking a rule gains.** In our runs each violation unit gained
  at most about 0.06 of P, so from lambda = 0.1 upward every run is legal. lambda = 2 is safely above that.
- **Week-boundary crossover finds the best plan more often and faster:** 6/10 successes vs 1/10 for
  uniform crossover, converging in about 5,400 evaluations instead of 8,500.
- **Swap mutation handles the final fine-tuning.** Without it no run reaches the best plan (0/10),
  and runs end lower (102.194 vs 102.237).
- **Limitation:** the last bit of fine-tuning is slow (under 0.005 gained in the last 50 generations),
  so 4 of 10 baseline runs end just short of the best plan.