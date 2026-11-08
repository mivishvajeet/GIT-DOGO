"""Category E: Production-Grade Git Incidents (Levels 26 - 30)."""

from pathlib import Path
from typing import Tuple, Optional
import json

from ..base import BaseChallenge, ChallengeCategory, InterviewQuestion, register_challenge
from ...core.git_client import GitClient
from ...core.repo_manager import repo_manager


# -----------------------------------------------------------------------------
# LEVEL 26: The Catastrophic Merge
# -----------------------------------------------------------------------------
@register_challenge
class Level26CatastrophicMerge(BaseChallenge):
    level_id = "level_26"
    number = 26
    category = ChallengeCategory.E_INCIDENTS
    title = "Production Incident: The Catastrophic Merge"
    difficulty = "Hardcore"
    estimated_time = "35 minutes"
    description = (
        "Severity 1 Incident: An engineer merged an untested, incomplete branch 'feature/untested-ledger' into 'main'.\n"
        "After this merge, 4 other engineers pushed legitimate, mission-critical production commits.\n"
        "Now production services are crashing because the incomplete ledger module has broken imports and syntax errors.\n"
        "Because 4 legitimate commits exist on top of the merge, running `git reset --hard` would cause catastrophic data loss.\n\n"
        "Your task: Recover the repository without resetting main. Revert the bad merge or surgical-patch the broken "
        "files so all platform unit tests pass and all 4 subsequent commits are 100% preserved."
    )
    initial_state_desc = "Broken merge commit buried under 4 legitimate production commits."
    expected_outcome = "Tests pass. 4 subsequent commits preserved. No broken imports."
    hints = [
        "Run `python3 -m unittest discover -s nexus_platform/tests` to see the exact crash.",
        "Use `git revert -m 1 <merge_commit_sha>` to undo the merge commit cleanly without losing subsequent commits.",
    ]
    solution_guide = (
        "1. Identify the SHA of the merge commit 'Merge branch feature/untested-ledger'.\n"
        "2. Run `git revert -m 1 <merge_sha>`.\n"
        "3. Commit and run `python3 -m unittest discover -s nexus_platform/tests`.\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="Why is `git revert` preferred over `git reset` in shared/production branches?",
            key_points=[
                "`git reset` rewrites existing public history, breaking every other engineer's local clone.",
                "`git revert` creates a new forward-moving commit that records the exact intention and inverse diff.",
                "Keeps a clear audit log for SOC2/ISO compliance and prevents merge conflicts on other team branches.",
            ],
            in_depth_explanation="Resetting public branches requires force-pushes that can silently overwrite teammates' work and trigger git push errors across the entire organization."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Create incomplete broken feature branch
        git.checkout("feature/untested-ledger", create=True)
        bad_file = git.repo_path / "nexus_platform" / "app" / "ledger.py"
        bad_file.write_text("import non_existent_library\nraise SystemExit('CATASTROPHIC_CRASH')\n")
        
        # Also inject import into main.py
        main_file = git.repo_path / "nexus_platform" / "app" / "main.py"
        main_file.write_text("from . import ledger\n" + main_file.read_text())
        git.add(".")
        git.commit("feat(ledger): experimental ledger service", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # Merge into main
        git.checkout("main")
        git.merge("feature/untested-ledger", message="Merge branch 'feature/untested-ledger'", no_ff=True)

        # 4 subsequent legitimate production commits
        for i in range(1, 5):
            (git.repo_path / f"prod_patch_{i}.txt").write_text(f"Crucial production patch #{i}\n")
            git.add(".")
            git.commit(f"feat(prod): critical production patch #{i}", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        # Check that all 4 production patches still exist
        for i in range(1, 5):
            p = git.repo_path / f"prod_patch_{i}.txt"
            if not p.exists():
                return False, f"Critical production patch {i} was destroyed!"

        # Check unit tests pass
        res = git.run("python3", "-m", "unittest", "discover", "-s", "nexus_platform/tests")
        if not res.success:
            return False, f"Tests still failing: {res.stderr or res.stdout}"

        return True, "Successfully recovered from catastrophic merge while preserving production commits!"


# -----------------------------------------------------------------------------
# LEVEL 27: Secret Exposure Incident
# -----------------------------------------------------------------------------
@register_challenge
class Level27SecretExposureIncident(BaseChallenge):
    level_id = "level_27"
    number = 27
    category = ChallengeCategory.E_INCIDENTS
    title = "Security Incident: Secret Exposure & History Purge"
    difficulty = "Hardcore"
    estimated_time = "35 minutes"
    description = (
        "Security Alert: A developer accidentally committed a live AWS access token and database password "
        "in file `config/secrets.env` (dummy value: 'AKIA_NEXUS_LEAKED_KEY_9921_SECRET').\n"
        "Even though they deleted the file in a subsequent commit, the secret STILL EXISTS in Git history objects!\n\n"
        "Your task as Incident Commander:\n"
        "1. Confirm the presence of the secret in past commits using `git log -S`.\n"
        "2. Rewrite repository history using `git filter-branch` (or filter-repo) to completely purge "
        "`config/secrets.env` from EVERY commit in the repository history.\n"
        "3. Create a file `docs/INCIDENT_ROTATION.txt` explaining why Git history rewriting does NOT replace "
        "credential rotation in the secret provider."
    )
    initial_state_desc = "Secret was committed and deleted in next commit; still exists in Git object history."
    expected_outcome = "Secret string completely removed from entire git log. INCIDENT_ROTATION.txt created."
    hints = [
        "Search history: `git log -S 'AKIA_NEXUS_LEAKED_KEY_9921_SECRET'`.",
        "Purge file from history: `git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch config/secrets.env' --prune-empty --tag-name-filter cat -- --all`.",
        "Create docs/INCIDENT_ROTATION.txt.",
    ]
    solution_guide = (
        "1. `git log -S AKIA_NEXUS_LEAKED_KEY_9921_SECRET`\n"
        "2. Run git filter-branch to remove config/secrets.env from all commits.\n"
        "3. Write credential rotation explanation to docs/INCIDENT_ROTATION.txt.\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="Why is credential rotation mandatory immediately upon secret exposure, regardless of Git history rewrite?",
            key_points=[
                "Git history rewrites cannot un-read secrets that were already cloned or sent to remotes/forks.",
                "Webhooks, CI runners, backups, and scrapers may have cached the secret within seconds of push.",
                "The secret must be treated as permanently compromised and immediately revoked at the identity provider.",
            ],
            in_depth_explanation="History scrubbing is purely hygienic (preventing future leaks). The only security mitigation is invalidating the compromised credentials immediately in AWS/GCP/Vault."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Secret commit
        sec_dir = git.repo_path / "config"
        sec_dir.mkdir(parents=True, exist_ok=True)
        sec_file = sec_dir / "secrets.env"
        sec_file.write_text("AWS_ACCESS_KEY_ID=AKIA_NEXUS_LEAKED_KEY_9921_SECRET\nDB_PASS=nexus_secret_pass\n")
        git.add(".")
        git.commit("chore(config): add local environment secrets", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # Deletion commit (the naive attempt to hide it)
        git.run("rm", "config/secrets.env")
        git.commit("chore(config): remove secrets file", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # Legitimate commit
        (git.repo_path / "nexus_platform" / "app" / "health.txt").write_text("health=ok\n")
        git.add(".")
        git.commit("feat(health): update health check status", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        # Check if secret appears anywhere in git log -p
        log_search = git.run("log", "-p", "-S", "AKIA_NEXUS_LEAKED_KEY_9921_SECRET").stdout.strip()
        if "AKIA_NEXUS_LEAKED_KEY_9921_SECRET" in log_search:
            return False, "Leaked secret key still found in Git commit history!"

        doc = git.repo_path / "docs" / "INCIDENT_ROTATION.txt"
        if not doc.exists():
            return False, "docs/INCIDENT_ROTATION.txt does not exist."

        return True, "Successfully purged secret from Git history and documented rotation protocols!"


# -----------------------------------------------------------------------------
# LEVEL 28: Dependency Supply-Chain Incident
# -----------------------------------------------------------------------------
@register_challenge
class Level28DependencySupplyChain(BaseChallenge):
    level_id = "level_28"
    number = 28
    category = ChallengeCategory.E_INCIDENTS
    title = "Dependency Supply-Chain Incident: Pinning & Vulnerability Triage"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "Security Alert: Dependabot flagged a high-severity remote code execution vulnerability (CVE-2026-9901) "
        "in an unpinned dependency in `nexus_platform/requirements.txt`.\n"
        "A developer carelessly used loose wildcard version `requests=*` and `cryptography>=0.1`, which pulled "
        "in compromised package versions.\n\n"
        "Your task:\n"
        "1. Inspect `nexus_platform/requirements.txt`.\n"
        "2. Securely pin all dependencies with explicit, safe semantic version constraints (e.g. `requests==2.31.0`, "
        "`cryptography==42.0.5`).\n"
        "3. Add a dependency audit hash file `nexus_platform/requirements.lock` with deterministic pinned hashes.\n"
        "4. Commit with message 'fix(security): pin safe dependency versions and generate lockfile'."
    )
    initial_state_desc = "Loose unpinned dependencies in requirements.txt with known vulnerable constraints."
    expected_outcome = "Explicit version pins in requirements.txt. Lockfile created. Clean commit."
    hints = [
        "Replace any wildcard or overly permissive constraints in requirements.txt with exact versions.",
        "Create requirements.lock containing package==version entries.",
    ]
    solution_guide = (
        "1. Open nexus_platform/requirements.txt\n"
        "2. Replace loose versions with pinned versions (e.g. requests==2.31.0, cryptography==42.0.5)\n"
        "3. Create nexus_platform/requirements.lock\n"
        "4. `git commit -am 'fix(security): pin safe dependency versions and generate lockfile'`\n"
        "5. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the difference between direct dependency specification and lockfiles (e.g. poetry.lock, Pipfile.lock)?",
            key_points=[
                "Direct specifications (`pyproject.toml`, `requirements.txt`) define compatible semantic ranges.",
                "Lockfiles record the exact transitive tree, exact versions, and cryptographic sha256 hashes of packages.",
                "Lockfiles guarantee reproducible builds across developer machines and production CI/CD.",
            ],
            in_depth_explanation="Without lockfiles, a clean CI build can unexpectedly download a newly published minor or patch version containing a breaking change or supply-chain malware."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        req_file = git.repo_path / "nexus_platform" / "requirements.txt"
        with open(req_file, "a") as f:
            f.write("requests=*\ncryptography>=0.1\n")
        git.add(".")
        git.commit("Base setup with loose dependencies", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        req_file = git.repo_path / "nexus_platform" / "requirements.txt"
        lock_file = git.repo_path / "nexus_platform" / "requirements.lock"

        if not lock_file.exists():
            return False, "nexus_platform/requirements.lock does not exist."

        content = req_file.read_text()
        if "=*" in content or ">=0.1" in content:
            return False, "Loose version wildcards (=* or >=0.1) still found in requirements.txt."

        last_commit = git.log("-n", "1", "--format=%s").strip()
        if "fix(security)" not in last_commit:
            return False, f"Latest commit message is '{last_commit}', expected 'fix(security)...'"

        return True, "Successfully mitigated dependency supply-chain vulnerability!"


# -----------------------------------------------------------------------------
# LEVEL 29: CI/CD Pipeline Failure
# -----------------------------------------------------------------------------
@register_challenge
class Level29CICDPipelineFailure(BaseChallenge):
    level_id = "level_29"
    number = 29
    category = ChallengeCategory.E_INCIDENTS
    title = "CI/CD Pipeline Failure: GitHub Actions Diagnostics"
    difficulty = "Hard"
    estimated_time = "30 minutes"
    description = (
        "Deployment blocker: The GitHub Actions CI workflow '.github/workflows/ci.yml' has 3 fatal defects:\n"
        "1. YAML indentation syntax error in the matrix definition.\n"
        "2. Missing permissions block (`permissions: contents: read`) causing job authorization denial.\n"
        "3. An invalid test command invoking a non-existent test runner.\n\n"
        "Your task: Diagnose the CI configuration, repair the YAML syntax and permissions, ensure the test step "
        "executes `python3 -m unittest discover -s nexus_platform/tests`, and commit the restored workflow on 'main'."
    )
    initial_state_desc = ".github/workflows/ci.yml is broken with YAML syntax, invalid permissions, and wrong test command."
    expected_outcome = ".github/workflows/ci.yml is syntactically valid YAML, correct permissions, runs valid unit tests."
    hints = [
        "Inspect `.github/workflows/ci.yml`.",
        "Check YAML indentation with a parser or linter.",
        "Ensure `permissions: contents: read` is set and tests command is valid.",
    ]
    solution_guide = (
        "1. Open `.github/workflows/ci.yml`.\n"
        "2. Fix YAML indentation, add `permissions:\n  contents: read`.\n"
        "3. Fix test step: `python3 -m unittest discover -s nexus_platform/tests`.\n"
        "4. `git commit -am 'fix(ci): repair workflow syntax, permissions and test runner'`\n"
        "5. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the principle of least privilege in GitHub Actions workflow permissions?",
            key_points=[
                "`GITHUB_TOKEN` defaults can be configured to read-only or read-write across the repository.",
                "Explicitly declaring `permissions: contents: read` restricts stolen tokens from tampering with releases or PRs.",
                "Prevents compromised 3rd-party GitHub Actions from writing malicious commits or pushing tags.",
            ],
            in_depth_explanation="If a third-party action or dependency is hijacked, a read-only GITHUB_TOKEN limits the blast radius and prevents code exfiltration via branch updates."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        
        ci_dir = git.repo_path / ".github" / "workflows"
        ci_dir.mkdir(parents=True, exist_ok=True)
        ci_file = ci_dir / "ci.yml"
        
        # Broken CI YAML
        broken_yaml = """name: Nexus CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
      # INVALID INDENT & WRONG RUNNER
    run: invalid-test-runner-fail --all
"""
        ci_file.write_text(broken_yaml)
        git.add(".")
        git.commit("ci: initial broken ci workflow", author_name="DevOps Team", author_email="devops@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        ci_file = git.repo_path / ".github" / "workflows" / "ci.yml"
        if not ci_file.exists():
            return False, ".github/workflows/ci.yml does not exist."

        content = ci_file.read_text()
        if "invalid-test-runner-fail" in content:
            return False, "Broken test runner command still present in ci.yml."
        if "unittest" not in content and "pytest" not in content:
            return False, "ci.yml does not invoke unit tests."
        if "permissions:" not in content:
            return False, "ci.yml is missing explicit permissions block."

        return True, "Successfully repaired CI/CD pipeline workflow configuration!"


# -----------------------------------------------------------------------------
# LEVEL 30: THE FINAL BOSS — REPOSITORY DISASTER
# -----------------------------------------------------------------------------
@register_challenge
class Level30FinalBoss(BaseChallenge):
    level_id = "level_30"
    number = 30
    category = ChallengeCategory.E_INCIDENTS
    title = "THE FINAL BOSS: Complete Repository Disaster"
    difficulty = "Boss"
    estimated_time = "60 minutes"
    description = (
        "====================================================================\n"
        "                  THE FINAL BOSS: REPOSITORY CATASTROPHE\n"
        "====================================================================\n"
        "Nexus Platform repository has collapsed into complete chaos after an uncoordinated hackathon:\n"
        "1. 20 open messy developer branches exist.\n"
        "2. 3 conflicting database migrations collide in the migration folder.\n"
        "3. 2 incorrect merge commits have broken mainline tests.\n"
        "4. 1 dummy AWS secret key ('AKIA_DISASTER_KEY_8877') is embedded in history.\n"
        "5. 1 broken dependency exists in requirements.txt.\n"
        "6. 1 corrupted release tag ('v2.5.0') points to a broken commit.\n"
        "7. 1 critical lost commit ('fix(orders): patch critical financial ledger rounding') is orphaned in reflog.\n"
        "8. CI/CD workflow '.github/workflows/ci.yml' is completely failing.\n\n"
        "Your task as Staff Principal Engineer & Incident Commander:\n"
        "1. Recover the lost financial ledger commit onto 'main'.\n"
        "2. Resolve the 3 conflicting migrations so down_revisions are linear.\n"
        "3. Revert or fix the bad merge commits until all unit tests pass.\n"
        "4. Scrub the leaked dummy secret from Git history.\n"
        "5. Fix the broken dependency in requirements.txt.\n"
        "6. Fix the corrupted release tag 'v2.5.0' so it points to the stable release commit.\n"
        "7. Restore '.github/workflows/ci.yml'.\n"
        "8. Generate a post-incident report file 'INCIDENT_REPORT.md' at repo root documenting all recoveries."
    )
    initial_state_desc = "Repository afflicted with all 10 major failure modes simultaneously."
    expected_outcome = "Repository 100% clean, all unit tests passing, migrations linear, secret purged, tag fixed, INCIDENT_REPORT.md created."
    hints = [
        "Step 1: Check `git reflog` to recover the lost financial commit.",
        "Step 2: Inspect migrations in `nexus_platform/app/migrations` and linearize down_revisions.",
        "Step 3: Run `python3 -m unittest discover -s nexus_platform/tests` to identify test failures.",
        "Step 4: Purge secret with `git filter-branch`.",
        "Step 5: Write post-incident summary in INCIDENT_REPORT.md.",
    ]
    solution_guide = (
        "1. Recover lost commit: `git reflog` -> cherry-pick or merge into main.\n"
        "2. Linearize migrations 004a, 004b, 004c in app/migrations.\n"
        "3. Fix syntax errors in broken merge, run unit tests.\n"
        "4. Remove leaked key AKIA_DISASTER_KEY_8877 from history.\n"
        "5. Pin requirements.txt.\n"
        "6. Retag v2.5.0 to point to stable commit.\n"
        "7. Repair .github/workflows/ci.yml.\n"
        "8. Create INCIDENT_REPORT.md.\n"
        "9. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is your systematic playbook when taking over a completely corrupted repository?",
            key_points=[
                "1. Freeze changes: enforce branch locks and stop active CI deploys.",
                "2. Create a full immutable bare backup of `.git`.",
                "3. Reflog forensics: map all lost commits and active branches.",
                "4. Isolate production mainline: establish a known-good commit baseline.",
                "5. Linearize migrations and contract schemas.",
                "6. Write post-incident review (blameless postmortem) with preventive controls (rulesets, secret scanning).",
            ],
            in_depth_explanation="A Principal Engineer restores stability methodically: backing up the object database first, diagnosing root causes without panicking, and rebuilding invariants with automated verification."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base platform setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")
        stable_sha = git.rev_parse("HEAD")

        # 1. Simulate 20 developer branches
        for i in range(1, 21):
            b_name = f"dev/feature-stream-{i:02d}"
            git.checkout("main")
            git.checkout(b_name, create=True)
            p = git.repo_path / f"stream_{i:02d}.txt"
            p.write_text(f"Stream {i}\n")
            git.add(".")
            git.commit(f"feat(stream): add stream #{i:02d}", author_name="Marcus Sterling", author_email="marcus.sterling@nexus.internal")

        git.checkout("main")

        # 2. Secret exposure commit
        sec_file = git.repo_path / "config" / "aws_creds.env"
        sec_file.parent.mkdir(parents=True, exist_ok=True)
        sec_file.write_text("AWS_KEY=AKIA_DISASTER_KEY_8877\n")
        git.add(".")
        git.commit("chore(config): accidental secret commit", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # 3. 3 Conflicting database migrations
        mig_dir = git.repo_path / "nexus_platform" / "app" / "migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "004a_rev.py").write_text('revision="004a"\ndown_revision="003"\n')
        (mig_dir / "004b_rev.py").write_text('revision="004b"\ndown_revision="003"\n')
        (mig_dir / "004c_rev.py").write_text('revision="004c"\ndown_revision="003"\n')
        git.add(".")
        git.commit("feat(db): 3 conflicting migrations merged", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # 4. Broken dependency in requirements.txt
        req_file = git.repo_path / "nexus_platform" / "requirements.txt"
        with open(req_file, "a") as f:
            f.write("broken-fake-malicious-pkg==99.99.99\n")
        git.add(".")
        git.commit("chore(deps): add broken package", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # 5. Broken CI workflow
        ci_dir = git.repo_path / ".github" / "workflows"
        ci_dir.mkdir(parents=True, exist_ok=True)
        (ci_dir / "ci.yml").write_text("BROKEN CI YAML SYNTAX: [unclosed\n")
        git.add(".")
        git.commit("ci: broken workflow", author_name="DevOps Team", author_email="devops@nexus.internal")

        # 6. Bad merge commit breaking orders
        git.checkout("bad-merge-branch", create=True)
        ord_file = git.repo_path / "nexus_platform" / "app" / "services" / "orders.py"
        ord_file.write_text(ord_file.read_text() + "\nSYNTAX ERROR BROKEN MERGE\n")
        git.add(".")
        git.commit("feat(orders): broken orders implementation", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")
        git.checkout("main")
        git.merge("bad-merge-branch", message="Merge branch 'bad-merge-branch'", no_ff=True)

        # 7. Corrupted release tag v2.5.0 pointing to the broken commit
        git.tag("v2.5.0", message="Corrupted release", ref="HEAD")

        # 8. Create a lost commit orphaned in reflog
        git.checkout("temp-ledger", create=True)
        (git.repo_path / "financial_ledger.py").write_text("# CRITICAL FINANCIAL LEDGER\ndef round_currency(val): return round(val, 2)\n")
        git.add(".")
        git.commit("fix(orders): patch critical financial ledger rounding", author_name="Staff Architect", author_email="architect@nexus.internal")
        # Delete branch leaving commit in reflog!
        git.checkout("main")
        git.run("branch", "-D", "temp-ledger")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        
        # 1. Check financial ledger rounding commit is recovered on main
        log = git.log("main", "--format=%s")
        if "patch critical financial ledger rounding" not in log:
            return False, "Lost financial ledger commit was not recovered onto 'main'!"

        # 2. Check secret is purged from git history
        sec_check = git.run("log", "-p", "-S", "AKIA_DISASTER_KEY_8877").stdout.strip()
        if "AKIA_DISASTER_KEY_8877" in sec_check:
            return False, "Leaked AWS key still exists in Git commit history!"

        # 3. Check requirements.txt does not contain broken dependency
        req_text = (git.repo_path / "nexus_platform" / "requirements.txt").read_text()
        if "broken-fake-malicious-pkg" in req_text:
            return False, "Broken dependency still present in requirements.txt."

        # 4. Check CI YAML is valid
        ci_text = (git.repo_path / ".github" / "workflows" / "ci.yml").read_text()
        if "BROKEN CI YAML" in ci_text:
            return False, "CI workflow still contains broken YAML syntax."

        # 5. Check migrations linear (no duplicate down_revisions)
        mig_dir = git.repo_path / "nexus_platform" / "app" / "migrations"
        down_revs = []
        for f in ["004a_rev.py", "004b_rev.py", "004c_rev.py"]:
            p = mig_dir / f
            if p.exists():
                for line in p.read_text().splitlines():
                    if "down_revision" in line:
                        down_revs.append(line.strip())
        if len(down_revs) > len(set(down_revs)):
            return False, "Database migrations still contain duplicate down_revisions!"

        # 6. Check tag v2.5.0
        tags = git.list_tags()
        if "v2.5.0" not in tags:
            return False, "Tag v2.5.0 does not exist."

        # 7. Check unit tests pass
        res = git.run("python3", "-m", "unittest", "discover", "-s", "nexus_platform/tests")
        if not res.success:
            return False, f"Unit test suite still failing: {res.stderr or res.stdout}"

        # 8. Check INCIDENT_REPORT.md exists
        report = git.repo_path / "INCIDENT_REPORT.md"
        if not report.exists():
            return False, "INCIDENT_REPORT.md does not exist at repo root."

        return True, "CONGRATULATIONS! You defeated THE FINAL BOSS and restored the repository to production stability!"

