"""Tests for Challenges Registry and Lifecycle."""

import unittest
from src.git_dojo.challenges import get_all_challenges, get_challenge, ChallengeCategory


class TestChallengesLifecycle(unittest.TestCase):

    def test_all_30_challenges_registered(self):
        challenges = get_all_challenges()
        self.assertEqual(len(challenges), 30)

        expected_ids = [f"level_{i:02d}" for i in range(1, 31)]
        for lid in expected_ids:
            c = get_challenge(lid)
            self.assertIsNotNone(c, f"Challenge {lid} missing from registry")
            self.assertTrue(len(c.title) > 0)
            self.assertTrue(len(c.description) > 0)
            self.assertTrue(len(c.hints) > 0)
            self.assertTrue(len(c.interview_questions) > 0)
            self.assertTrue(callable(getattr(c, "setup", None)))
            self.assertTrue(callable(getattr(c, "verify", None)))

    def test_category_distribution(self):
        challenges = get_all_challenges()
        cat_counts = {}
        for c in challenges:
            cat_counts[c.category] = cat_counts.get(c.category, 0) + 1

        self.assertEqual(cat_counts[ChallengeCategory.A_INTERNALS], 5)
        self.assertEqual(cat_counts[ChallengeCategory.B_BRANCHING], 10)
        self.assertEqual(cat_counts[ChallengeCategory.C_DISTRIBUTED], 5)
        self.assertEqual(cat_counts[ChallengeCategory.D_RELEASE], 5)
        self.assertEqual(cat_counts[ChallengeCategory.E_INCIDENTS], 5)


if __name__ == "__main__":
    unittest.main()
