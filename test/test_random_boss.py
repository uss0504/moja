import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from random_boss import adjusted_weights, secrets_choice


class FirstRoll:
    def randrange(self, stop):
        return 0


class AdjustedWeightsTests(unittest.TestCase):
    def test_recent_multipliers_preserve_base_weights(self):
        population = [
            {"pageid": 1, "weight": 2},
            {"pageid": 2, "weight": 3},
            {"pageid": 3, "weight": 4},
            {"pageid": 4, "weight": 5},
            {"pageid": 5, "weight": 6},
        ]

        weights = adjusted_weights(
            population,
            ["pageid:1", "pageid:2", "pageid:3", "pageid:4"],
            [0.05, 0.12, 0.20, 0.40],
        )

        self.assertEqual(weights, [0.1, 0.36, 0.8, 2.0, 6])
        self.assertEqual(
            [item["weight"] for item in population],
            [2, 3, 4, 5, 6],
        )

    def test_zero_weight_stays_zero(self):
        population = [{"pageid": 1, "weight": 0}]

        self.assertEqual(
            adjusted_weights(population, ["pageid:1"], [0.05]),
            [0],
        )

    def test_positive_weight_is_not_rounded_to_zero(self):
        selected = secrets_choice(
            ["small-positive-weight"],
            [0.00000001],
            rnd=FirstRoll(),
        )

        self.assertEqual(selected, ["small-positive-weight"])


if __name__ == "__main__":
    unittest.main()
