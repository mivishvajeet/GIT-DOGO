"""Tests for Git Forensic Toolkit."""

import unittest
import tempfile
from pathlib import Path

from src.git_dojo.core.git_client import GitClient
from src.git_dojo.forensics.inspector import ForensicInspector
from src.git_dojo.forensics.report import ForensicReportRenderer


class TestForensicToolkit(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo_dir = Path(self.tmp.name) / "test_repo"
        self.git = GitClient(self.repo_dir)
        self.git.init()
        self.git.config("user.name", "Forensic Tester")
        self.git.config("user.email", "forensics@nexus.internal")

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_repo_analysis(self):
        (self.repo_dir / "README.md").write_text("# Clean Repo\n")
        self.git.add(".")
        self.git.commit("feat: initial commit")

        inspector = ForensicInspector(self.repo_dir)
        report = inspector.analyze()

        self.assertTrue(report.is_valid_repo)
        self.assertEqual(report.current_branch, "main")
        self.assertFalse(report.is_detached)
        self.assertFalse(report.has_merge_conflicts)
        self.assertEqual(report.health_status, "EXCELLENT")

        rendered = ForensicReportRenderer.render(report)
        self.assertIn("REPOSITORY HEALTH REPORT", rendered)
        self.assertIn("EXCELLENT", rendered)

    def test_detects_secrets_and_conflicts(self):
        (self.repo_dir / "secret.env").write_text("AWS_KEY=AKIAIOSFODNN7EXAMPLE\n")
        self.git.add(".")
        self.git.commit("feat: leak secret")

        inspector = ForensicInspector(self.repo_dir)
        report = inspector.analyze()

        self.assertGreater(len(report.suspicious_findings), 0)
        self.assertLess(report.health_score, 100)


if __name__ == "__main__":
    unittest.main()
