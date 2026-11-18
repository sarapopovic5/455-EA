"""
Experiments: runs every setting below with 10 seeds and saves the results.
Run with: python experiments.py
Writes results/summary.csv (one row per setting) and results/runs.json (every run, for plots.py).
"""

import csv
import json
import os
import statistics
import fitness
from ea import run_ea, DEFAULT_SETTINGS

SEEDS = range(10)

# (name, EA settings to change, penalty weight lambda)
# Every setting uses the same budget: 100 + 200 x 50 = 10,100 evaluations per run.
EXPERIMENTS = [
    ("baseline", {}, 2.0),
    # penalty weight: how strongly rule-breaking is punished (0 = rules off)
    ("lambda 0", {}, 0.0),
    ("lambda 0.02", {}, 0.02),
    ("lambda 0.05", {}, 0.05),
    ("lambda 0.1", {}, 0.1),
    ("lambda 10", {}, 10.0),
    # operators: does each design choice help?
    ("uniform crossover", {"crossover": "uniform"}, 2.0),
    ("no swap mutation", {"swap_rate": 0}, 2.0),
]

TOLERANCE = 0.01   # a run "succeeds" if its legal plan is within 0.01 of the best legal P found

def evals_to_converge(history_best, final):
    """Evaluations used before the run first got within TOLERANCE of its final best."""
    pop = DEFAULT_SETTINGS["pop_size"]
    children = pop - int(pop * DEFAULT_SETTINGS["keep_fraction"])
    for gen, best in enumerate(history_best):
        if best >= final - TOLERANCE:
            return pop + (gen + 1) * children
    return pop + len(history_best) * children

def main():
    os.makedirs("results", exist_ok=True)
    runs = {}
    for name, settings, lam in EXPERIMENTS:
        runs[name] = []
        for seed in SEEDS:
            score = lambda plan, lam=lam: fitness.score(plan, lam=lam)
            plan, best, history = run_ea(seed, settings, score)
            runs[name].append({
                "seed": seed,
                "plan": plan,
                "score": best,
                "performance": fitness.performance(plan),
                "violations": fitness.total_violations(plan),
                "evals": evals_to_converge(history["best"], best),
                "history": {k: [round(v, 4) for v in vals] for k, vals in history.items()},
            })
        print(f"done: {name}")

    # success target: best performance reached by any legal plan in any run
    target = max(r["performance"] for rs in runs.values() for r in rs if r["violations"] == 0)

    rows = []
    for name, rs in runs.items():
        scores = [r["score"] for r in rs]
        legal = [r for r in rs if r["violations"] == 0]
        hits = [r for r in legal if r["performance"] >= target - TOLERANCE]
        rows.append({
            "setting": name,
            "mean_best_score": round(statistics.mean(scores), 4),
            "sd": round(statistics.stdev(scores), 4),
            "mean_performance_P": round(statistics.mean(r["performance"] for r in rs), 4),
            "mean_violations": round(statistics.mean(r["violations"] for r in rs), 1),
            "legal_runs": f"{len(legal)}/{len(rs)}",
            "success_rate": f"{len(hits)}/{len(rs)}",
            "mean_evals_to_converge": round(statistics.mean(r["evals"] for r in rs)),
        })

    with open("results/summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    with open("results/runs.json", "w") as f:
        json.dump({"target_P": target, "runs": runs}, f)

    print(f"\nTarget P (best legal plan found): {target:.4f}\n")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
