"""
Plots: turns results/runs.json (from experiments.py) into the figures for the slides.
Run with:  python plots.py   (run experiments.py first)
Writes 4 PNGs into figures/.
"""

import json
import os
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import fitness

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "legend.frameon": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})

def mean_curve(runs, key):
    """Average a history curve ("best" or "avg") across all seeds."""
    n = len(runs[0]["history"][key])
    return [statistics.mean(r["history"][key][g] for r in runs) for g in range(n)]

def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join("figures", name), dpi=200)
    plt.close(fig)
    print("saved figures/" + name)

def convergence(runs):
    """Left: best and average score per generation. Right: operator comparison."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    gens = range(1, len(runs["baseline"][0]["history"]["best"]) + 1)

    a.plot(gens, mean_curve(runs["baseline"], "best"), color=BLUE, lw=2, label="Best plan")
    a.plot(gens, mean_curve(runs["baseline"], "avg"), color=ORANGE, lw=2, label="Population average")
    a.set(title="Baseline: score per generation (mean of 10 seeds)",
          xlabel="Generation", ylabel="Score F", ylim=(85, 103.5))
    a.legend(loc="lower right")

    for name, color in [("baseline", BLUE), ("uniform crossover", ORANGE), ("no swap mutation", AQUA)]:
        label = "Week crossover + swap (baseline)" if name == "baseline" else name.capitalize()
        b.plot(gens, mean_curve(runs[name], "best"), color=color, lw=2, label=label)
    b.set(title="Best score by operator choice (zoomed)", xlabel="Generation",
          ylabel="Score F", ylim=(101.5, 102.3))
    b.legend(loc="lower right")
    save(fig, "convergence.png")

def best_of(runs):
    return max(runs, key=lambda r: r["score"])["plan"]

def best_plan(runs):
    """Weekly load of the best plan found, against the cap of 14."""
    loads = fitness.weekly_loads(best_of(runs["baseline"]))
    fig, ax = plt.subplots(figsize=(7, 4.2))
    weeks = range(1, len(loads) + 1)
    ax.bar(weeks, loads, color=BLUE, width=0.7)
    ax.axhline(fitness.MAX_WEEKLY_LOAD, color=MUTED, ls="--", lw=1)
    ax.text(len(loads) + 0.45, fitness.MAX_WEEKLY_LOAD + 0.3, "cap 14", ha="right", color=MUTED, fontsize=10)
    for w, load in zip(weeks, loads):
        ax.text(w, load + 0.3, str(load), ha="center", color=INK, fontsize=10)
    ax.set(title="Best plan found: weekly training load", xlabel="Week",
           ylabel="Weekly load (sum of daily intensity)", ylim=(0, 16), xticks=list(weeks))
    ax.grid(axis="x", visible=False)
    save(fig, "best_plan.png")

def fitness_fatigue(runs):
    """How the best plan's fitness benefit and fatigue cost evolve over the 56 days."""
    plan = best_of(runs["baseline"])
    fit, fat = fitness.simulate(plan)
    benefit = [fitness.K_FITNESS * f for f in fit]
    cost = [fitness.K_FATIGUE * d for d in fat]
    days = range(1, len(plan) + 1)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(days, benefit, color=BLUE, lw=2, label="Fitness benefit (0.1 x fitness)")
    ax.plot(days, cost, color=ORANGE, lw=2, label="Fatigue cost (0.3 x fatigue)")
    p = fitness.performance(plan)
    ax.annotate(f"Race day: P = 100 + {benefit[-1]:.2f} - {cost[-1]:.2f} = {p:.2f}",
                xy=(len(plan), cost[-1]), xytext=(24, 0.3), color=INK, fontsize=10,
                arrowprops=dict(arrowstyle="->", color=MUTED))
    for w in range(7, len(plan), 7):
        ax.axvline(w + 0.5, color=GRID, lw=0.8, zorder=0)
    ax.set(title="Best plan: fitness benefit vs fatigue cost by day (the taper)",
           xlabel="Day", ylabel="Points of race-day performance P", xlim=(1, len(plan)))
    ax.legend(loc="upper left")
    save(fig, "fitness_fatigue.png")

def lambda_sweep(runs):
    """Left: rules broken by the best plan. Right: race-day performance. Same x for both."""
    names = ["lambda 0", "lambda 0.02", "lambda 0.05", "lambda 0.1", "baseline", "lambda 10"]
    labels = ["0", "0.02", "0.05", "0.1", "2", "10"]
    viol = [statistics.mean(r["violations"] for r in runs[n]) for n in names]
    perf = [statistics.mean(r["performance"] for r in runs[n]) for n in names]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    x = range(len(names))

    a.bar(x, viol, color=ORANGE, width=0.6)
    for i, v in zip(x, viol):
        a.text(i, v + 1.5, f"{v:g}", ha="center", color=INK, fontsize=10)
    a.set(title="Rule violations in the best plan", xlabel="Penalty weight lambda",
          ylabel="Mean violations (10 seeds)", xticks=list(x), xticklabels=labels, ylim=(0, 108))
    a.grid(axis="x", visible=False)

    b.plot(x, perf, color=BLUE, lw=2, marker="o", ms=8)
    for i, v in zip(x, perf):
        b.text(i, v + 0.06, f"{v:.2f}", ha="center", color=INK, fontsize=10)
    b.set(title="Race-day performance P of the best plan", xlabel="Penalty weight lambda",
          ylabel="Mean P (10 seeds)", xticks=list(x), xticklabels=labels, ylim=(102.0, 103.5))
    save(fig, "lambda.png")

def main():
    os.makedirs("figures", exist_ok=True)
    with open(os.path.join("results", "runs.json")) as f:
        runs = json.load(f)["runs"]
    convergence(runs)
    best_plan(runs)
    fitness_fatigue(runs)
    lambda_sweep(runs)

if __name__ == "__main__":
    main()
