"""Category B: Branching and History Surgery (Levels 11 - 15)."""

from pathlib import Path
from typing import Tuple, Optional

from ..base import BaseChallenge, ChallengeCategory, InterviewQuestion, register_challenge
from ...core.git_client import GitClient
from ...core.repo_manager import repo_manager


# -----------------------------------------------------------------------------
# LEVEL 11: Git Rebase --onto
# -----------------------------------------------------------------------------
@register_challenge
class Level11RebaseOnto(BaseChallenge):
    level_id = "level_11"
    number = 11
    category = ChallengeCategory.B_BRANCHING
    title = "Surgical History Transplant with git rebase --onto"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "An engineer branched 'feature/experimental-analytics' from 'legacy-v1'.\n"
        "On that branch, they committed 2 experimental throwaway changes, followed by 2 high-priority production "
        "reporting fixes ('fix(reporting): calculate tax correctly' and 'fix(reporting): handle zero inventory').\n"
        "The legacy-v1 branch and the experimental commits will NEVER be merged into production.\n\n"
        "Your task: Surgically transplant ONLY the 2 production fixes directly onto 'main' on a new branch named "
        "'feature/reporting-fixes', without bringing along any of the experimental or legacy commits."
    )
    initial_state_desc = "2 production commits buried on top of experimental commits branched from legacy-v1."
    expected_outcome = "feature/reporting-fixes branched off main containing only the 2 reporting fixes."
    hints = [
        "Use `git rebase --onto main <experimental_commit_sha> feature/experimental-analytics`.",
        "Alternatively checkout main, create feature/reporting-fixes, and cherry-pick the 2 commits.",
    ]
    solution_guide = (
        "1. Identify the commit hash of the 2nd experimental commit: `<exp2_sha>`.\n"
        "2. Run `git checkout -b feature/reporting-fixes feature/experimental-analytics`.\n"
        "3. Run `git rebase --onto main <exp2_sha> feature/reporting-fixes`.\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="Explain the three parameters of `git rebase --onto <newbase> <upstream> <branch>`.",
            key_points=[
                "<newbase>: the commit/branch where the transplanted commits will land.",
                "<upstream>: the commit range boundary (exclusive); commits strictly after this are replayed.",
                "<branch>: the target branch whose commits are being moved (defaults to HEAD).",
            ],
            in_depth_explanation="`git rebase --onto A B C` means: take all commits in the range `B..C` and replay them on top of commit `A`."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base main setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Create legacy-v1 branch
        git.checkout("legacy-v1", create=True)
        (git.repo_path / "legacy.txt").write_text("legacy code\n")
        git.add(".")
        git.commit("chore(legacy): old v1 code base", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Create feature/experimental-analytics off legacy-v1
        git.checkout("feature/experimental-analytics", create=True)
        (git.repo_path / "exp1.txt").write_text("throwaway exp 1\n")
        git.add(".")
        git.commit("exp: risky prototype part 1", author_name="Mateo Silva", author_email="mateo.silva@nexus.internal")

        (git.repo_path / "exp2.txt").write_text("throwaway exp 2\n")
        git.add(".")
        git.commit("exp: risky prototype part 2", author_name="Mateo Silva", author_email="mateo.silva@nexus.internal")

        # 2 high priority production fixes
        p_rep = git.repo_path / "nexus_platform" / "app" / "services" / "reporting.py"
        with open(p_rep, "a") as f:
            f.write("\n# TAX_FIX: applied tax calculation\n")
        git.add(".")
        git.commit("fix(reporting): calculate tax correctly", author_name="Mateo Silva", author_email="mateo.silva@nexus.internal")

        with open(p_rep, "a") as f:
            f.write("\n# ZERO_INV_FIX: handle zero inventory safely\n")
        git.add(".")
        git.commit("fix(reporting): handle zero inventory", author_name="Mateo Silva", author_email="mateo.silva@nexus.internal")

        git.checkout("main")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        branches = git.list_branches()
        if "feature/reporting-fixes" not in branches:
            return False, "Branch 'feature/reporting-fixes' does not exist."

        # Check commit count between main and feature/reporting-fixes
        count = int(git.run("rev-list", "--count", "main..feature/reporting-fixes").stdout.strip())
        if count != 2:
            return False, f"Expected exactly 2 commits on feature/reporting-fixes above main, found {count}."

        commits = git.log("main..feature/reporting-fixes", "--format=%s").splitlines()
        expected = [
            "fix(reporting): handle zero inventory",
            "fix(reporting): calculate tax correctly",
        ]
        if commits != expected:
            return False, f"Unexpected commits on branch: {commits}"

        # Verify no experimental or legacy files exist on this branch
        git.checkout("feature/reporting-fixes")
        if (git.repo_path / "exp1.txt").exists() or (git.repo_path / "exp2.txt").exists() or (git.repo_path / "legacy.txt").exists():
            return False, "Experimental or legacy files were mistakenly included!"

        return True, "Successfully transplanted production fixes using git rebase --onto!"


# -----------------------------------------------------------------------------
# LEVEL 12: Revert a Merge Commit with Subsequent Dependent Commits
# -----------------------------------------------------------------------------
@register_challenge
class Level12RevertMergeCommit(BaseChallenge):
    level_id = "level_12"
    number = 12
    category = ChallengeCategory.B_BRANCHING
    title = "Revert a Faulty Merge Commit (git revert -m 1)"
    difficulty = "Hard"
    estimated_time = "20 minutes"
    description = (
        "Disaster on production: PR #42 ('feature/payment-v2') was merged into 'main'.\n"
        "Immediately after the merge, another engineer pushed a release version bump commit ('chore(release): v1.5.0').\n"
        "Production alerts are firing: payment-v2 contains a critical memory leak! "
        "Because subsequent commits exist, resetting main is strictly prohibited.\n\n"
        "Your task: Revert the faulty merge commit on 'main' using `git revert -m 1`, keeping the release commit intact."
    )
    initial_state_desc = "Faulty merge commit is in main history with a subsequent release commit."
    expected_outcome = "A revert commit exists undoing the merge changes. Release commit is preserved."
    hints = [
        "A merge commit has 2 parents. You must specify `-m 1` to designate parent 1 (mainline).",
        "Run `git log --oneline` to find the merge commit hash.",
        "Run `git revert -m 1 <merge_commit_sha>`.",
    ]
    solution_guide = (
        "1. Identify the SHA of `Merge branch 'feature/payment-v2'`.\n"
        "2. Run `git revert -m 1 <sha>`.\n"
        "3. Accept the default revert commit message.\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="Why does `git revert` on a merge commit require `-m 1` or `-m 2`?",
            key_points=[
                "A merge commit has two or more parents (parent 1 = mainline branch, parent 2 = merged branch).",
                "Git needs to know which parent represents the mainline to calculate the inverse diff against.",
                "-m 1 specifies parent 1 as the baseline.",
            ],
            in_depth_explanation=(
                "Reverting a merge undoes the data changes made by the branch, but does NOT rewrite history. "
                "Crucially, if the feature branch is re-merged in the future, Git will remember the commits as already merged! "
                "To re-merge later, one must first revert the revert commit."
            ),
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base main setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Feature payment-v2
        git.checkout("feature/payment-v2", create=True)
        pay_file = git.repo_path / "nexus_platform" / "app" / "services" / "payment_v2.py"
        pay_file.write_text("# FAULTY PAYMENT SERVICE: MEMORY LEAK\nimport os\n")
        git.add(".")
        git.commit("feat(payments): integrate payment v2 engine", author_name="Liam Chen", author_email="liam.chen@nexus.internal")

        # Merge into main
        git.checkout("main")
        git.merge("feature/payment-v2", message="Merge branch 'feature/payment-v2'", no_ff=True)

        # Subsequent release commit
        version_file = git.repo_path / "version.txt"
        version_file.write_text("v1.5.0\n")
        git.add(".")
        git.commit("chore(release): bump version to v1.5.0", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        # Check that payment_v2.py does not exist
        pay_file = git.repo_path / "nexus_platform" / "app" / "services" / "payment_v2.py"
        if pay_file.exists():
            return False, "payment_v2.py still exists! The merge commit was not reverted."

        # Check that version.txt exists and is intact
        v_file = git.repo_path / "version.txt"
        if not v_file.exists() or v_file.read_text().strip() != "v1.5.0":
            return False, "The subsequent release commit was destroyed!"

        # Check for revert commit in log
        head_msg = git.log("-n", "1", "--format=%s").strip()
        if not head_msg.startswith("Revert"):
            return False, f"Latest commit is '{head_msg}', expected a Revert commit."

        return True, "Successfully reverted merge commit while preserving subsequent release commits!"


# -----------------------------------------------------------------------------
# LEVEL 13: Resolve Accidental Duplicate Cherry-Pick
# -----------------------------------------------------------------------------
@register_challenge
class Level13DuplicateCherryPick(BaseChallenge):
    level_id = "level_13"
    number = 13
    category = ChallengeCategory.B_BRANCHING
    title = "Resolve Accidental Duplicate Cherry-Pick"
    difficulty = "Medium"
    estimated_time = "20 minutes"
    description = (
        "A developer attempted to apply a security patch ('fix(security): sanitize sql input') "
        "to 'feature/data-export'. Confused by git output, they ran `git cherry-pick` twice, causing "
        "a duplicated empty commit or repeated diff in git log.\n\n"
        "Your task: Inspect the branch history using `git log` and `git cherry-pick`, remove the redundant duplicate commit "
        "using interactive rebase (`git rebase -i`), leaving only ONE single instance of the security fix."
    )
    initial_state_desc = "feature/data-export has duplicate commits for the same security fix."
    expected_outcome = "Only one instance of 'fix(security): sanitize sql input' remains on the branch."
    hints = [
        "Inspect the branch: `git log --oneline` shows two identical commit titles.",
        "Run `git rebase -i HEAD~3` and drop one of the duplicate commits.",
    ]
    solution_guide = (
        "1. `git checkout feature/data-export`\n"
        "2. `git log -n 5 --oneline`\n"
        "3. `git rebase -i HEAD~3`\n"
        "4. In the editor, change 'pick' to 'drop' on the second duplicate commit.\n"
        "5. Save and finish rebase."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the difference between git cherry-pick and git merge?",
            key_points=[
                "git merge joins histories and creates a merge commit with multiple parents.",
                "git cherry-pick applies the diff of an individual commit to HEAD, creating a new commit with a new SHA.",
                "Cherry-picking can cause patch-id duplicates that create conflicts during future merges.",
            ],
            in_depth_explanation="`git patch-id` computes a hash of the diff. Git's rebase engine checks patch-ids to skip commits that already exist upstream."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        git.checkout("feature/data-export", create=True)
        (git.repo_path / "export.py").write_text("def export_data(): pass\n")
        git.add(".")
        git.commit("feat(export): initial export function", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # Duplicate commit 1
        sec_file = git.repo_path / "nexus_platform" / "app" / "security_patch.py"
        sec_file.write_text("# Sanitize inputs\ndef sanitize(q): return q.strip()\n")
        git.add(".")
        git.commit("fix(security): sanitize sql input", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # Duplicate commit 2 (accidental empty / repeated)
        git.commit("fix(security): sanitize sql input", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal", allow_empty=True)

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        log = git.log("feature/data-export", "--format=%s").splitlines()
        count = log.count("fix(security): sanitize sql input")
        if count != 1:
            return False, f"Found {count} occurrences of 'fix(security): sanitize sql input'. Expected exactly 1."
        return True, "Successfully eliminated duplicate cherry-pick commit!"


# -----------------------------------------------------------------------------
# LEVEL 14: Repair Diverged Branches Without Destroying Work
# -----------------------------------------------------------------------------
@register_challenge
class Level14RepairDivergedBranches(BaseChallenge):
    level_id = "level_14"
    number = 14
    category = ChallengeCategory.B_BRANCHING
    title = "Repair Diverged Branches Without Destroying Work"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "Two developers were working on shared branch 'feature/warehouse-v2'.\n"
        "Alice committed 'feat(warehouse): add barcode scanner support' and pushed.\n"
        "Bob (without pulling Alice's changes) committed 'feat(warehouse): add shelf coordinate system'.\n"
        "Bob's local branch has diverged by 1 commit ahead and 1 commit behind.\n\n"
        "Your task: Synchronize Bob's branch with Alice's work cleanly using `git rebase` or clean `git merge`, "
        "ensuring both features coexist, all tests pass, and zero work is lost or overwritten."
    )
    initial_state_desc = "Local branch and remote tracking branch have diverged with independent commits."
    expected_outcome = "Both commits present on feature/warehouse-v2. Clean working tree."
    hints = [
        "Run `git status` or inspect branches: `feature/warehouse-v2` and `alice/feature/warehouse-v2`.",
        "Rebase or merge: `git rebase alice/feature/warehouse-v2`.",
    ]
    solution_guide = (
        "1. `git checkout feature/warehouse-v2`\n"
        "2. `git rebase alice/feature/warehouse-v2`\n"
        "3. Verify both files exist."
    )
    interview_questions = [
        InterviewQuestion(
            question="Why does git push fail with '[rejected - non-fast-forward]' when branches diverge?",
            key_points=[
                "Fast-forward push only succeeds if remote ref is an ancestor of the local commit.",
                "If someone else pushed, remote contains commits not present locally.",
                "Forcing push would delete the remote commits from the branch tip.",
            ],
            in_depth_explanation="A fast-forward is a linear pointer advance. When history branches off, Git refuses to push without a merge or rebase to prevent silent data loss."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Base branch
        git.checkout("feature/warehouse-v2", create=True)
        base_sha = git.rev_parse("HEAD")

        # Alice's commit on branch alice/feature/warehouse-v2
        git.checkout("alice/feature/warehouse-v2", create=True)
        p1 = git.repo_path / "nexus_platform" / "app" / "services" / "barcode.py"
        p1.write_text("def scan_barcode(): return '12345'\n")
        git.add(".")
        git.commit("feat(warehouse): add barcode scanner support", author_name="Alice Vance", author_email="alice.vance@nexus.internal")

        # Bob's commit on feature/warehouse-v2
        git.checkout("feature/warehouse-v2")
        p2 = git.repo_path / "nexus_platform" / "app" / "services" / "shelf.py"
        p2.write_text("def get_shelf_coordinate(): return 'A-12'\n")
        git.add(".")
        git.commit("feat(warehouse): add shelf coordinate system", author_name="Bob Kowalski", author_email="bob.kowalski@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        git.checkout("feature/warehouse-v2")
        log = git.log("-n", "5", "--format=%s")
        if "add barcode scanner support" not in log:
            return False, "Missing Alice's commit: 'feat(warehouse): add barcode scanner support'."
        if "add shelf coordinate system" not in log:
            return False, "Missing Bob's commit: 'feat(warehouse): add shelf coordinate system'."

        p1 = git.repo_path / "nexus_platform" / "app" / "services" / "barcode.py"
        p2 = git.repo_path / "nexus_platform" / "app" / "services" / "shelf.py"
        if not p1.exists() or not p2.exists():
            return False, "Files from both features must exist in the working directory."

        return True, "Successfully repaired diverged branch without losing any developer work!"


# -----------------------------------------------------------------------------
# LEVEL 15: Recover From an Incorrectly Executed Force-Push
# -----------------------------------------------------------------------------
@register_challenge
class Level15RecoverForcePush(BaseChallenge):
    level_id = "level_15"
    number = 15
    category = ChallengeCategory.B_BRANCHING
    title = "Disaster Recovery: Accidental git push --force"
    difficulty = "Hardcore"
    estimated_time = "30 minutes"
    description = (
        "Catastrophe: A panicked developer had merge conflicts on 'feature/auth-sso' and ran "
        "`git push --force`, overwriting 3 days of work by Staff Engineer Elena!\n"
        "Elena's commits included OAuth2 PKCE verification and multi-factor authentication (MFA).\n"
        "The remote ref now only contains the developer's 1 stub commit.\n\n"
        "Your task: Perform forensic reflog recovery to find Elena's overwritten branch tip, "
        "restore 'feature/auth-sso' to its complete, uncorrupted state including all MFA and PKCE commits, "
        "and verify that `git log` reflects the restored history."
    )
    initial_state_desc = "feature/auth-sso tip was forcibly overwritten; prior 3 commits are unreferenced."
    expected_outcome = "feature/auth-sso restored to the complete commit containing MFA & OAuth2 PKCE."
    hints = [
        "Inspect the reflog: `git reflog show feature/auth-sso` or `git reflog`.",
        "Identify the commit before the force push (message: 'feat(auth): add MFA TOTP authentication').",
        "Reset the branch to that commit: `git reset --hard <sha>`.",
    ]
    solution_guide = (
        "1. `git checkout feature/auth-sso`\n"
        "2. `git reflog`\n"
        "3. Locate the SHA for 'feat(auth): add MFA TOTP authentication'.\n"
        "4. `git reset --hard <sha>`\n"
        "5. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="Why is `git push --force-with-lease` safer than `git push --force`?",
            key_points=[
                "`--force` blindly overwrites the remote ref regardless of its current state.",
                "`--force-with-lease` checks if the remote ref still matches your local remote-tracking ref (e.g. `origin/main`).",
                "If a teammate pushed commits to remote that you haven't fetched yet, `--force-with-lease` rejects the push.",
            ],
            in_depth_explanation="`--force-with-lease` acts like a Compare-And-Swap (CAS) atomic primitive in distributed systems, preventing accidental clobbering of un-fetched upstream work."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        git.checkout("feature/auth-sso", create=True)
        # Elena's work
        (git.repo_path / "oauth.py").write_text("# OAuth2 PKCE implementation\n")
        git.add(".")
        git.commit("feat(auth): implement OAuth2 PKCE verification", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        (git.repo_path / "mfa.py").write_text("# TOTP MFA implementation\n")
        git.add(".")
        git.commit("feat(auth): add MFA TOTP authentication", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Now simulate junior dev force-pushing a broken stub over the branch
        # Reset hard to base and commit stub
        git.reset_hard("main")
        (git.repo_path / "stub.txt").write_text("stub broken auth\n")
        git.add(".")
        git.commit("wip: messy auth stub", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        git.checkout("feature/auth-sso")
        log = git.log("-n", "5", "--format=%s")
        if "feat(auth): add MFA TOTP authentication" not in log:
            return False, "Branch tip does not contain Elena's commit 'feat(auth): add MFA TOTP authentication'."
        if "feat(auth): implement OAuth2 PKCE verification" not in log:
            return False, "Branch missing commit 'feat(auth): implement OAuth2 PKCE verification'."

        mfa_file = git.repo_path / "mfa.py"
        oauth_file = git.repo_path / "oauth.py"
        if not mfa_file.exists() or not oauth_file.exists():
            return False, "Recovered files mfa.py or oauth.py do not exist in the working directory."

        return True, "Successfully recovered from catastrophic force-push using reflog forensics!"
