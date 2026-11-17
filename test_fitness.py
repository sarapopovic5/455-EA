"""Tests for fitness.py. Run with:  python -m unittest test_fitness -v"""

import unittest

import fitness as fm
from fitness import score, violations, simulate, performance, weekly_loads


def week_plan(*weeks):
    """Build a 56-day plan from 8 lists of 7 days."""
    plan = [d for w in weeks for d in w]
    assert len(plan) == 56
    return plan


# A legal week: load 8, has rest, no hard days
LEGAL = [1, 2, 0, 2, 1, 2, 0]


class TestScore(unittest.TestCase):
    def test_rest_only_scores_exactly_100(self):
        self.assertEqual(score([0] * 56), 100.0)

    def test_deterministic_and_does_not_change_plan(self):
        plan = [3, 0, 2, 1] * 14
        copy = list(plan)
        self.assertEqual(score(plan), score(plan))
        self.assertEqual(plan, copy)

    def test_legal_plan_has_no_violations(self):
        plan = week_plan(*[LEGAL] * 8)
        self.assertEqual(violations(plan), {"cap": 0, "ramp": 0, "rest": 0, "streak": 0})
        self.assertAlmostEqual(score(plan), performance(plan))

    def test_score_is_p_minus_lambda_times_violations(self):
        plan = [3] * 56
        v = sum(violations(plan).values())
        self.assertAlmostEqual(score(plan), performance(plan) - 2 * v)
        self.assertAlmostEqual(score(plan, lam=10), performance(plan) - 10 * v)
        self.assertAlmostEqual(score(plan, rules=False), performance(plan))

    def test_bad_input_rejected(self):
        with self.assertRaises(ValueError):
            score([0] * 55)
        with self.assertRaises(ValueError):
            score([4] + [0] * 55)


class TestSimulation(unittest.TestCase):
    def test_one_easy_day(self):
        fit, fat = simulate([1] + [0] * 55)
        self.assertEqual(fit[0], 1.0)
        self.assertEqual(fat[0], 0.5)
        self.assertAlmostEqual(fit[-1], 1.0 * fm.FITNESS_DECAY ** 55)
        self.assertAlmostEqual(fat[-1], 0.5 * fm.FATIGUE_DECAY ** 55)

    def test_decay_constants_match_draft(self):
        self.assertAlmostEqual(fm.FITNESS_DECAY, 0.965, places=3)
        self.assertAlmostEqual(fm.FATIGUE_DECAY, 0.867, places=3)

    def test_hard_day_on_race_day_hurts(self):
        base = week_plan(*[LEGAL] * 8)
        hard_last = base[:-1] + [3]
        self.assertLess(performance(hard_last), performance(base))


class TestRules(unittest.TestCase):
    def test_weekly_loads(self):
        self.assertEqual(weekly_loads(week_plan(*[LEGAL] * 8)), [8] * 8)

    def test_cap(self):
        heavy = [3, 3, 0, 3, 3, 2, 1]  # load 15, has rest, no 3-in-a-row
        v = violations(week_plan(*[LEGAL] * 7, heavy))
        self.assertEqual(v["cap"], 1)       # 15 - 14
        self.assertEqual(v["ramp"], 5)      # 15 - 8 - 2
        self.assertEqual(v["rest"], 0)
        self.assertEqual(v["streak"], 0)

    def test_ramp_week_one_uses_starting_load(self):
        # Week 1 load 8 vs starting load 6: 8 - 6 - 2 = 0
        self.assertEqual(violations(week_plan(*[LEGAL] * 8))["ramp"], 0)
        # Week 1 load 10: 10 - 6 - 2 = 2
        w10 = [2, 2, 0, 2, 2, 2, 0]
        self.assertEqual(violations(week_plan(w10, *[LEGAL] * 7))["ramp"], 2)

    def test_ramp_only_penalizes_increases(self):
        easy = [1, 0, 0, 0, 0, 0, 0]  # load 1
        plan = week_plan(LEGAL, easy, *[LEGAL] * 6)
        # 8 -> 1 is fine, 1 -> 8 is +7: 7 - 2 = 5
        self.assertEqual(violations(plan)["ramp"], 5)

    def test_rest_one_per_week_without_rest(self):
        no_rest = [1] * 7
        plan = week_plan(no_rest, LEGAL, no_rest, *[LEGAL] * 5)
        self.assertEqual(violations(plan)["rest"], 2)

    def test_streak(self):
        plan = [0] * 56
        plan[0:3] = [3, 3, 3]          # run of 3 -> 1
        plan[10:15] = [3, 3, 3, 3, 3]  # run of 5 -> 3
        plan[20:22] = [3, 3]           # run of 2 -> 0
        self.assertEqual(violations(plan)["streak"], 4)

    def test_streak_at_end_of_plan(self):
        self.assertEqual(violations([0] * 52 + [3, 3, 3, 3])["streak"], 2)

    def test_all_hard(self):
        v = violations([3] * 56)
        self.assertEqual(v["cap"], 8 * (21 - 14))
        self.assertEqual(v["ramp"], 21 - 6 - 2)  # only week 1 rises
        self.assertEqual(v["rest"], 8)
        self.assertEqual(v["streak"], 56 - 2)


if __name__ == "__main__":
    unittest.main()
