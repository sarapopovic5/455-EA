# Performance Lab: Optimizing an 8-Week Training Plan with an EA

CISC 455 Group 17. An evolutionary algorithm searches for the 56-day training plan
that gives the best predicted race-day performance (Banister fitness-fatigue model).

## Files

| File | What it does | Owner |
|---|---|---|
| `fitness.py` | `score(plan)`: simulates a plan and returns its fitness | Sara (Role 1) |
| `ea.py` | `run_ea(...)`: the evolutionary algorithm | Role 2 |
| (others add their own files here) | | |

Rule: only edit your own file. Tell the repo maintainer if you need something changed elsewhere.

## How to run

```
pip install -r requirements.txt
python ea.py
```

## How the pieces connect

- **plan**: a list of 56 integers, one per day, each 0 = rest, 1 = easy, 2 = moderate, 3 = hard.
  Days 0-6 are week 1, days 7-13 are week 2, and so on.
- **`score(plan)`** returns one number. Higher is better. It must not change `plan`,
  and the same plan must always get the same score.
- **`run_ea(seed, settings, score)`** returns `(best_plan, best_score, history)`.
  `history` is `{"best": [...], "avg": [...]}`, one value per generation.
  The same seed always gives the same result.

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