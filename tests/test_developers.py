"""Tests for Nexus Engineering organizations and 100 fictional identities."""

import unittest
from src.git_dojo.organization.teams import TEAMS, TEAMS_BY_ID
from src.git_dojo.organization.developers import (
    DEVELOPERS,
    DEVELOPERS_BY_ID,
    CommitBehavior,
    get_developers_by_team,
    get_developer_by_behavior,
)


class TestNexusEngineeringOrg(unittest.TestCase):

    def test_teams_count_and_uniqueness(self):
        self.assertEqual(len(TEAMS), 15)
        team_ids = [t.id for t in TEAMS]
        self.assertEqual(len(team_ids), len(set(team_ids)))

    def test_exactly_100_developers_generated(self):
        self.assertEqual(len(DEVELOPERS), 100)
        self.assertEqual(len(DEVELOPERS_BY_ID), 100)

    def test_deterministic_identities(self):
        # Developer 001 identity should be deterministic across runs
        d1 = DEVELOPERS[0]
        self.assertEqual(d1.id, "dev_001")
        self.assertTrue(d1.email.endswith("@nexus.internal"))
        self.assertIn(d1.team_id, TEAMS_BY_ID)
        self.assertIsNotNone(d1.role)
        self.assertIsNotNone(d1.behavior)

    def test_every_team_has_engineers(self):
        for team in TEAMS:
            devs = get_developers_by_team(team.id)
            self.assertGreaterEqual(len(devs), 5, f"Team {team.id} has fewer than 5 developers")

    def test_behavior_distribution(self):
        clean_devs = get_developer_by_behavior(CommitBehavior.CLEAN_ATOMIC)
        bug_devs = get_developer_by_behavior(CommitBehavior.INTRODUCES_BUGS)
        force_devs = get_developer_by_behavior(CommitBehavior.FORCE_PUSH_PRONE)
        self.assertGreater(len(clean_devs), 0)
        self.assertGreater(len(bug_devs), 0)
        self.assertGreater(len(force_devs), 0)


if __name__ == "__main__":
    unittest.main()
