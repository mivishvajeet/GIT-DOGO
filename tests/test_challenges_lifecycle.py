"""Tests for Challenges Registry and Lifecycle."""

import io
import json
import shutil
import unittest
from src.git_dojo.challenges import get_all_challenges, get_challenge, ChallengeCategory
from src.git_dojo.core.config import config
from src.git_dojo.core.git_client import GitClient
from src.git_dojo.core.repo_manager import repo_manager
from src.git_dojo.web.server import CockpitApiHandler


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

    def test_all_30_challenges_setup_and_initial_verify(self):
        orig_path = repo_manager.repo_path
        orig_git = repo_manager.git
        probe = config.playground_root / "_unittest_probe"
        repo_manager.repo_path = probe
        repo_manager.git = GitClient(probe)
        try:
            for c in get_all_challenges():
                with self.subTest(level=c.level_id):
                    c.setup()
                    self.assertTrue((probe / "nexus_platform" / "app").is_dir())
                    ok, msg = c.verify(probe)
                    self.assertFalse(ok, f"{c.level_id} unexpectedly passed before solving: {msg}")
        finally:
            repo_manager.repo_path = orig_path
            repo_manager.git = orig_git
            if probe.exists():
                shutil.rmtree(probe)

    def test_level_19_platform_tests_run_properly(self):
        orig_path = repo_manager.repo_path
        orig_git = repo_manager.git
        probe = config.playground_root / "_unittest_level19"
        repo_manager.repo_path = probe
        repo_manager.git = GitClient(probe)
        try:
            c = get_challenge("level_19")
            c.setup()
            ok, msg = c.verify(probe)
            self.assertFalse(ok)
            self.assertNotIn("is not a git command", msg)

            # Fix the breaking change in users.py and verify tests pass
            user_srv = probe / "nexus_platform" / "app" / "services" / "users.py"
            user_srv.write_text(user_srv.read_text().replace('"user_handle": username', '"username": username'))
            repo_manager.git.add(".")
            repo_manager.git.commit("fix(api): restore username compatibility")
            ok_after, msg_after = c.verify(probe)
            self.assertTrue(ok_after, msg_after)
        finally:
            repo_manager.repo_path = orig_path
            repo_manager.git = orig_git
            if probe.exists():
                shutil.rmtree(probe)

    def test_web_api_endpoints_return_valid_json(self):
        class DummySocket:
            def __init__(self, req_bytes: bytes):
                self.rfile = io.BytesIO(req_bytes)
                self.wfile = io.BytesIO()

            def makefile(self, mode, *args, **kwargs):
                return self.rfile if "r" in mode else self.wfile

            def sendall(self, data):
                self.wfile.write(data)

            def close(self):
                pass

        for path in ["/", "/api/scenarios", "/api/prs", "/api/repo/status", "/api/repo/commits"]:
            sock = DummySocket(f"GET {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode())
            CockpitApiHandler(sock, ("127.0.0.1", 12345), None)
            raw = sock.wfile.getvalue()
            header, body = raw.split(b"\r\n\r\n", 1)
            self.assertIn(b"200 OK", header)
            if path.startswith("/api/"):
                parsed = json.loads(body.decode("utf-8"))
                self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()

