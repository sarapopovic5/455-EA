"""Tests for ea.py. Run with:  python -m unittest test_ea -v"""

import random
import unittest

from ea import DAYS, WEEK, random_plan, tournament, crossover, mutate, run_ea
import fitness

def placeholder_score(plan):
    """Known best = 112: every week exactly at the 14 cap. Rewards total load, minus 2 for each unit a week goes over 14."""
    total = sum(plan)
    over_cap = 0
    for w in range(0, DAYS, WEEK):
        over_cap += max(0, sum(plan[w:w + WEEK]) - 14)
    return total - 2 * over_cap

def weekly(plan):
    return [sum(plan[w:w + WEEK]) for w in range(0, DAYS, WEEK)]

class TestOperators(unittest.TestCase):
    def test_random_plan_is_valid(self):
        plan = random_plan(random.Random(1))
        self.assertEqual(len(plan), DAYS)
        self.assertTrue(all(d in (0, 1, 2, 3) for d in plan))

    def test_tournament_never_picks_worst(self):
        pop, fit = ["a", "b", "c", "d", "e"], [1, 5, 3, 2, 4]
        rng = random.Random(0)
        self.assertEqual(tournament(pop, fit, 5, rng), "b")
        picks = [tournament(pop, fit, 2, rng) for _ in range(200)]
        self.assertNotIn("a", picks)

    def test_week_crossover_keeps_whole_weeks(self):
        c1, c2 = crossover([0] * DAYS, [3] * DAYS, "week", random.Random(2))
        for load in weekly(c1) + weekly(c2):
            self.assertIn(load, (0, 21))

    def test_mutate_copies_and_stays_in_range(self):
        plan = [3] * DAYS
        child = mutate(plan, 1, 0, random.Random(3))
        self.assertEqual(plan, [3] * DAYS) # original unchanged
        self.assertTrue(set(child) <= {2, 3}) # never creeps to 4

    def test_swap_keeps_weekly_load(self):
        plan = [0, 1, 2, 3, 0, 1, 2] * 8
        child = mutate(plan, 0, 1, random.Random(1))
        self.assertNotEqual(child, plan)
        self.assertEqual(weekly(child), weekly(plan))

class TestRunEA(unittest.TestCase):
    def test_finds_known_optimum(self):
        for seed in range(5):
            _, best, _ = run_ea(seed, {}, placeholder_score)
            self.assertEqual(best, 112)

    def test_same_seed_same_result(self):
        a = run_ea(5, {}, placeholder_score)
        b = run_ea(5, {}, placeholder_score)
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[2], b[2])

    def test_history_and_elitism(self):
        _, _, hist = run_ea(3, {"generations": 50}, placeholder_score)
        self.assertEqual(len(hist["best"]), 50)
        self.assertEqual(len(hist["avg"]), 50)
        for prev, nxt in zip(hist["best"], hist["best"][1:]):
            self.assertLessEqual(prev, nxt) # best never gets worse

    def test_real_model_gives_legal_plan(self):
        plan, best, _ = run_ea(0)
        self.assertEqual(fitness.total_violations(plan), 0)
        self.assertGreater(best, 100) # beats the rest-only plan

if __name__ == "__main__":
    unittest.main()