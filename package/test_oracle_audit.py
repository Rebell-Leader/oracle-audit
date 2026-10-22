"""Regression checks for score direction, depth boundaries and tie handling."""
import unittest
import numpy as np
from oracle_audit import composition_overlap, depth_test, sign_test


class AuditTests(unittest.TestCase):
    def test_composition_overlap_counts_duplicates(self):
        self.assertEqual(composition_overlap(["AK", "AK", "GG"], ["KA", "GG", "TT"]), 2)

    def test_first_crossing_and_last_passing_depth(self):
        result = depth_test([4, 3], [2, 1], min_k=1)
        self.assertEqual(result["k_first_below"], 3)
        self.assertEqual(result["k_at_floor"], 2)

    def test_failure_at_start_is_zero_usable_depth(self):
        result = depth_test([1], [2], min_k=1)
        self.assertEqual(result["k_at_floor"], 0)

    def test_floor_equality_is_passing(self):
        result = depth_test([4, 3, 2], [1], min_k=1)
        self.assertIsNone(result["k_first_below"])
        self.assertEqual(result["k_at_floor"], 4)

    def test_mic_direction(self):
        result = depth_test([1, 2], [3, 4], lower_is_better=True, min_k=1)
        self.assertEqual(result["k_first_below"], 3)
        rates = sign_test([1, 2], [3, 4], threshold=2, lower_is_better=True)
        self.assertEqual(rates["pos_rate"], 1)
        self.assertEqual(rates["decoy_rate"], 0)

    def test_minimum_depth_ignores_early_dip(self):
        result = depth_test([5, 4, 3], [6, 2, 1], min_k=4)
        self.assertEqual(result["k_first_below"], 5)

    def test_ties_are_repeatable(self):
        a = depth_test([1] * 20, [1] * 20)
        b = depth_test([1] * 20, [1] * 20)
        np.testing.assert_array_equal(a["precision"], b["precision"])

    def test_bad_inputs_fail(self):
        for scores in ([], [float("nan")], [float("inf")], [[1, 2]]):
            with self.assertRaises(ValueError):
                sign_test(scores, [1])
        with self.assertRaises(ValueError):
            depth_test([1], [2], min_k=3)
        with self.assertRaises(ValueError):
            depth_test([1], [2], precision_floor=1.2, min_k=1)


if __name__ == "__main__":
    unittest.main()
