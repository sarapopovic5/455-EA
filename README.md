# Performance Lab: Optimizing an 8-Week Training Plan with an EA

CISC 455 Group 17. An evolutionary algorithm searches for the 56-day training plan
that gives the best predicted race-day performance (Banister fitness-fatigue model).

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
| `figures/` | The 4 figures used in the slides | generated |

Rule: only edit your own file. Tell the repo maintainer if you need something changed elsewhere.

## How to run

```
pip install -r requirements.txt
python ea.py                  # one EA run with the fitness model
python -m unittest -v         # run every test in the repo
python experiments.py         # all experiments (about 20 seconds), writes results/
python plots.py               # writes the figures to figures/
```

Run the tests before opening a pull request to make sure nothing broke.

## How the pieces connect

- **plan**: a list of 56 integers, one per day, each 0 = rest, 1 = easy, 2 = moderate, 3 = hard.
  Days 0-6 are week 1, days 7-13 are week 2, and so on.
- **`score(plan, lam=2.0, rules=True)`** returns one number. Higher is better. It must not change `plan`,
  and the same plan must always get the same score. `lam` sets the penalty weight; `rules=False` scores
  performance only.
- **`run_ea(seed, settings, score)`** returns `(best_plan, best_score, history)`.
  `settings` is optional and overrides any default, e.g. `{"crossover": "uniform"}`.
  `score` defaults to `fitness.score`. `history` is `{"best": [...], "avg": [...]}`, one value per generation.
  The same seed always gives the same result.

## Experiments and results

Every setting runs with seeds 0-9 and the same budget: 10,100 evaluations per run
(population 100, 50 new children per generation, 200 generations).
A run **succeeds** if its best plan breaks no rules and is within 0.01 of the best legal P found by any run (102.244).

| Setting | Mean best score | SD | Mean P | Mean violations | Legal runs | Success rate | Evals to converge |
|---|---|---|---|---|---|---|---|
| Baseline (lambda 2) | 102.237 | 0.005 | 102.237 | 0 | 10/10 | 6/10 | 5,390 |
| lambda 0 (rules off) | 103.292 | 0.000 | 103.292 | 96 | 0/10 | 0/10 | 4,515 |
| lambda 0.02 | 102.388 | 0.006 | 102.648 | 13 | 0/10 | 0/10 | 4,865 |
| lambda 0.05 | 102.250 | 0.008 | 102.320 | 1.4 | 1/10 | 1/10 | 5,145 |
| lambda 0.1 | 102.237 | 0.005 | 102.237 | 0 | 10/10 | 7/10 | 5,880 |
| lambda 10 | 102.240 | 0.005 | 102.240 | 0 | 10/10 | 8/10 | 5,775 |
| Uniform crossover | 102.225 | 0.007 | 102.225 | 0 | 10/10 | 1/10 | 8,515 |
| No swap mutation | 102.194 | 0.015 | 102.194 | 0 | 10/10 | 0/10 | 5,395 |

**What we found**
- **The EA discovers tapering on its own.** Every baseline run finds the same weekly shape:
  8, 10, 12, 14, 14, 14, 9, 3 (build up, peak at the cap, taper), P = 102.24 vs 100 for resting.
- **The rules cost about 1 point of performance.** With no penalty the best plan trains at 21 per week
  until the taper (96 violations) and reaches P = 103.29. That plan is unrealistic, which is why the rules exist.
- **The penalty only has to outweigh what breaking a rule gains.** From lambda = 0.1 upward every run is legal;
  below that the EA trades rule-breaking for performance. lambda = 2 is safely above the threshold.
- **Week-boundary crossover matters most.** Same final quality range, but 6/10 successes vs 1/10 for
  uniform crossover, and it converges in about 5,400 evaluations instead of 8,500.
- **Swap mutation helps the final fine-tuning.** Without it, runs stall below the best plan (0/10 successes).

## How to add your code

Never push straight to `main`. Put your work on a branch and open a pull request.

**Option A: in VS Code (terminal)**
```
git pull
git checkout -b your-branch-name
git add your_file.py
git commit -m "Short description"
git push -u origin your-branch-name
```
Then go to the repo on GitHub and click **Compare & pull request**.

**Option B: on the GitHub website**
Add file > Upload files > choose "Create a new branch for this commit and start a pull request".

The maintainer reviews and merges every pull request.