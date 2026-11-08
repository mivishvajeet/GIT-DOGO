"""Category B: Branching and History Surgery (Levels 06 - 10)."""

from pathlib import Path
from typing import Tuple, Optional

from ..base import BaseChallenge, ChallengeCategory, InterviewQuestion, register_challenge
from ...core.git_client import GitClient
from ...core.repo_manager import repo_manager


# -----------------------------------------------------------------------------
# LEVEL 06: Multiple Simultaneous Merge Conflicts
# -----------------------------------------------------------------------------
@register_challenge
class Level06SimultaneousMergeConflicts(BaseChallenge):
    level_id = "level_06"
    number = 6
    category = ChallengeCategory.B_BRANCHING
    title = "Multiple Simultaneous Merge Conflicts"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "Two teams worked concurrently on major updates to Nexus Platform:\n"
        "- Backend team on 'feature/order-discount-engine' added discount calculations to order service, "
        "order schema, and config settings.\n"
        "- API team on 'feature/api-v2-routes' concurrently refactored config settings, order validation, "
        "and order API endpoints on 'main'.\n\n"
        "Your task: Merge 'feature/order-discount-engine' into 'main'. Resolve all conflicts in config.py, "
        "orders.py, and main.py so that BOTH features work harmoniously, all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) "
        "are removed, tests pass, and the merge is cleanly committed."
    )
    initial_state_desc = "On branch main. feature/order-discount-engine is ready to merge, creating 3 simultaneous file conflicts."
    expected_outcome = "feature/order-discount-engine is merged into main. Zero conflict markers. All syntax valid."
    hints = [
        "Run `git merge feature/order-discount-engine` to trigger the conflict.",
        "Inspect each conflicted file: `git status` shows 3 conflicted paths.",
        "Carefully merge the logic: keep both the v2 api routes and the discount engine settings.",
        "Add resolved files and finalize with `git commit`.",
    ]
    solution_guide = (
        "1. `git merge feature/order-discount-engine`\n"
        "2. In config.py: include both `API_V2_PREFIX` and `DISCOUNT_MAX_PERCENT`.\n"
        "3. In orders.py: include both the validation logic and the discount computation.\n"
        "4. In main.py: preserve both routes.\n"
        "5. `git add . && git commit -m 'Merge feature/order-discount-engine'`"
    )
    interview_questions = [
        InterviewQuestion(
            question="What is a 3-way merge in Git and how is the merge base identified?",
            key_points=[
                "Uses 3 snapshots: common ancestor (merge base), branch A tip (ours), and branch B tip (theirs).",
                "Git calculates the lowest common ancestor (LCA) in the DAG.",
                "If only one side changed relative to base, that change is cleanly applied. If both sides changed the same hunk differently, a conflict is raised.",
            ],
            in_depth_explanation="The merge base is determined by `git merge-base <branchA> <branchB>`, finding the lowest common ancestor node in the commit graph."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base platform release", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Create branch for discounts
        git.checkout("feature/order-discount-engine", create=True)
        config_path = git.repo_path / "nexus_platform" / "app" / "config.py"
        with open(config_path, "a") as f:
            f.write("\n    DISCOUNT_MAX_PERCENT: float = 30.0\n    ENABLE_DISCOUNTS: bool = True\n")
        
        orders_path = git.repo_path / "nexus_platform" / "app" / "services" / "orders.py"
        with open(orders_path, "a") as f:
            f.write("\ndef apply_order_discount(amount: float, pct: float) -> float:\n    return round(amount * (1.0 - (pct / 100.0)), 2)\n")
        
        git.add(".")
        git.commit("feat(discounts): add discount calculations and settings", author_name="Marcus Sterling", author_email="marcus.sterling@nexus.internal")

        # Switch back to main and create concurrent changes
        git.checkout("main")
        with open(config_path, "a") as f:
            f.write("\n    API_V2_PREFIX: str = '/api/v2'\n    RATE_LIMIT_PER_MINUTE: int = 120\n")
        
        with open(orders_path, "a") as f:
            f.write("\ndef validate_order_limits(amount: float) -> bool:\n    return amount <= 100000.0\n")

        git.add(".")
        git.commit("feat(api): add v2 routing prefix and order limits", author_name="Zoe Chen", author_email="zoe.chen@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        cur = git.current_branch()
        if cur != "main":
            return False, f"Current branch is '{cur}', expected 'main'."

        # Check if merge commit exists connecting feature/order-discount-engine
        parents = git.run("rev-parse", "HEAD^@").stdout.split()
        if len(parents) < 2:
            return False, "HEAD is not a merge commit. Expected at least 2 parent commits."

        # Verify no conflict markers exist anywhere
        for p in (git.repo_path / "nexus_platform").rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            if "<<<<<<<" in text or "=======" in text or ">>>>>>>" in text:
                return False, f"Conflict markers still found in {p.relative_to(git.repo_path)}"

        # Check that both features exist in files
        config_text = (git.repo_path / "nexus_platform" / "app" / "config.py").read_text()
        if "DISCOUNT_MAX_PERCENT" not in config_text or "API_V2_PREFIX" not in config_text:
            return False, "config.py does not contain both DISCOUNT_MAX_PERCENT and API_V2_PREFIX."

        orders_text = (git.repo_path / "nexus_platform" / "app" / "services" / "orders.py").read_text()
        if "apply_order_discount" not in orders_text or "validate_order_limits" not in orders_text:
            return False, "orders.py does not contain both apply_order_discount and validate_order_limits."

        return True, "Successfully merged concurrent features and cleanly resolved all file conflicts!"


# -----------------------------------------------------------------------------
# LEVEL 07: Three-Way Merge with Rename/Delete Conflicts
# -----------------------------------------------------------------------------
@register_challenge
class Level07RenameDeleteConflict(BaseChallenge):
    level_id = "level_07"
    number = 7
    category = ChallengeCategory.B_BRANCHING
    title = "Three-Way Merge with Rename/Delete Conflicts"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "Architectural conflict between two senior developers:\n"
        "- Developer A on 'feature/refactor-config' renamed 'nexus_platform/app/config.py' to "
        "'nexus_platform/app/settings.py' and added environment validator helper.\n"
        "- Developer B on 'main' edited 'nexus_platform/app/config.py' to add urgent security CORS headers.\n\n"
        "Your task: Merge 'feature/refactor-config' into 'main'. Resolve the rename/delete conflict by "
        "keeping the new file 'nexus_platform/app/settings.py', ensuring the CORS headers from main are preserved "
        "inside it, removing 'config.py', and committing the clean merge."
    )
    initial_state_desc = "Rename/edit conflict between settings.py and config.py."
    expected_outcome = "Merged cleanly. settings.py contains CORS headers and validator. config.py is deleted."
    hints = [
        "Run `git merge feature/refactor-config`.",
        "Git will report: CONFLICT (modify/delete): nexus_platform/app/config.py.",
        "Inspect the contents of config.py on main, migrate CORS headers into settings.py.",
        "Remove config.py: `git rm nexus_platform/app/config.py`.",
        "Add settings.py and complete commit.",
    ]
    solution_guide = (
        "1. `git merge feature/refactor-config`\n"
        "2. Copy `CORS_ALLOWED_ORIGINS` from config.py into settings.py.\n"
        "3. `git rm nexus_platform/app/config.py`\n"
        "4. `git add nexus_platform/app/settings.py`\n"
        "5. `git commit -m 'Merge feature/refactor-config resolving rename conflict'`"
    )
    interview_questions = [
        InterviewQuestion(
            question="How does Git detect renames during merges?",
            key_points=[
                "Git does not store rename metadata; it computes renames dynamically using similarity heuristics.",
                "`merge.renameLimit` and `-X rename-threshold=<n>` control detection.",
                "If one branch renamed a file and the other modified the original, Git generates a modify/delete or rename/modify conflict.",
            ],
            in_depth_explanation="Git hashes file contents and compares deleted files against newly added files. If similarity exceeds the threshold (default 50%), it treats it as a rename."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base platform setup", author_name="Kenji Takahashi", author_email="kenji.takahashi@nexus.internal")

        # Branch with rename
        git.checkout("feature/refactor-config", create=True)
        old_config = git.repo_path / "nexus_platform" / "app" / "config.py"
        new_settings = git.repo_path / "nexus_platform" / "app" / "settings.py"
        content = old_config.read_text() + "\ndef validate_settings():\n    return True\n"
        new_settings.write_text(content)
        git.run("rm", "nexus_platform/app/config.py")
        git.add("nexus_platform/app/settings.py")
        git.commit("refactor: migrate config.py to settings.py", author_name="Chloe Novak", author_email="chloe.novak@nexus.internal")

        # Main branch with edits to original config.py
        git.checkout("main")
        with open(old_config, "a") as f:
            f.write("\nCORS_ALLOWED_ORIGINS = ['https://nexus.internal', 'https://admin.nexus.internal']\n")
        git.add("nexus_platform/app/config.py")
        git.commit("feat(sec): add CORS allowed origins to config", author_name="Kenji Takahashi", author_email="kenji.takahashi@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        old_config = git.repo_path / "nexus_platform" / "app" / "config.py"
        new_settings = git.repo_path / "nexus_platform" / "app" / "settings.py"

        if old_config.exists():
            return False, "nexus_platform/app/config.py still exists! It should be removed in favor of settings.py."
        if not new_settings.exists():
            return False, "nexus_platform/app/settings.py does not exist."

        text = new_settings.read_text()
        if "CORS_ALLOWED_ORIGINS" not in text:
            return False, "CORS_ALLOWED_ORIGINS was not preserved in settings.py."
        if "validate_settings" not in text:
            return False, "validate_settings was lost in settings.py."

        parents = git.run("rev-parse", "HEAD^@").stdout.split()
        if len(parents) < 2:
            return False, "HEAD is not a merge commit."

        return True, "Successfully resolved rename/delete conflict and merged settings.py!"


# -----------------------------------------------------------------------------
# LEVEL 08: Stacked Pull Requests Across Five Dependent Branches
# -----------------------------------------------------------------------------
@register_challenge
class Level08StackedPRs(BaseChallenge):
    level_id = "level_08"
    number = 8
    category = ChallengeCategory.B_BRANCHING
    title = "Stacked Pull Requests Across 5 Dependent Branches"
    difficulty = "Hard"
    estimated_time = "30 minutes"
    description = (
        "Nexus Engineering uses stacked PRs for incremental code review:\n"
        "Branch chain: main -> pr1-base -> pr2-models -> pr3-api -> pr4-tests -> pr5-docs\n\n"
        "During review, the Tech Lead required an urgent change in pr1-base: updating the base error class.\n"
        "After updating pr1-base, all downstream branches (pr2, pr3, pr4, pr5) became out of sync and "
        "contain stale history!\n\n"
        "Your task: Rebase each stacked branch cleanly in order onto its immediate predecessor so that:\n"
        "1. pr2-models is based on pr1-base\n"
        "2. pr3-api is based on pr2-models\n"
        "3. pr4-tests is based on pr3-api\n"
        "4. pr5-docs is based on pr4-tests\n"
        "Each branch must contain its unique commits without duplicates, cleanly building on each other."
    )
    initial_state_desc = "Stacked branches pr1 to pr5 are out of sync after pr1-base received an amendment."
    expected_outcome = "All 5 branches sequentially rebased. No duplicate commits. History linear."
    hints = [
        "Use `git rebase --onto <new-base> <old-base> <branch>`.",
        "Alternatively: checkout pr2, `git rebase pr1-base`; checkout pr3, `git rebase pr2-models`, and so on.",
    ]
    solution_guide = (
        "1. `git checkout pr2-models && git rebase pr1-base`\n"
        "2. `git checkout pr3-api && git rebase pr2-models`\n"
        "3. `git checkout pr4-tests && git rebase pr3-api`\n"
        "4. `git checkout pr5-docs && git rebase pr4-tests`\n"
        "5. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What are stacked PRs and how does `git rebase --onto` manage them?",
            key_points=[
                "Stacked PRs break large features into small, reviewable sequential diffs.",
                "`git rebase --onto <new_base> <old_base> <branch>` extracts only the commits unique to <branch> (since <old_base>) and transplants them onto <new_base>.",
                "Avoids dragging duplicate or discarded upstream commits into the downstream PRs.",
            ],
            in_depth_explanation="Syntax: `git rebase --onto NEWBASE OLDBASE BRANCH`. It takes commits in OLDBASE..BRANCH and applies them one-by-one on top of NEWBASE."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # 1. pr1-base
        git.checkout("pr1-base", create=True)
        p1 = git.repo_path / "nexus_platform" / "app" / "base_error.py"
        p1.write_text("class NexusBaseError(Exception): pass\n")
        git.add(".")
        git.commit("feat(core): define base error class v1", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # 2. pr2-models
        git.checkout("pr2-models", create=True)
        p2 = git.repo_path / "nexus_platform" / "app" / "models" / "error_log.py"
        p2.parent.mkdir(parents=True, exist_ok=True)
        p2.write_text("# Error model\n")
        git.add(".")
        git.commit("feat(models): add error log model", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # 3. pr3-api
        git.checkout("pr3-api", create=True)
        p3 = git.repo_path / "nexus_platform" / "app" / "api" / "errors.py"
        p3.parent.mkdir(parents=True, exist_ok=True)
        p3.write_text("# Error API\n")
        git.add(".")
        git.commit("feat(api): add error reporting endpoint", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # 4. pr4-tests
        git.checkout("pr4-tests", create=True)
        p4 = git.repo_path / "nexus_platform" / "tests" / "test_errors.py"
        p4.write_text("# Test errors\n")
        git.add(".")
        git.commit("test(errors): add error unit tests", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # 5. pr5-docs
        git.checkout("pr5-docs", create=True)
        p5 = git.repo_path / "docs" / "ERRORS.md"
        p5.parent.mkdir(parents=True, exist_ok=True)
        p5.write_text("# Error Documentation\n")
        git.add(".")
        git.commit("docs(errors): add error handling manual", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # Now amend pr1-base after review feedback!
        git.checkout("pr1-base")
        p1.write_text("class NexusBaseError(Exception):\n    code: str = 'NEXUS_ERR'\n")
        git.add(".")
        git.commit("refactor(core): amend base error with status code", author_name="Aria Vance", author_email="aria.vance@nexus.internal")
        git.checkout("main")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        # Check that pr5-docs contains all 5 files
        git.checkout("pr5-docs")
        p1 = git.repo_path / "nexus_platform" / "app" / "base_error.py"
        p5 = git.repo_path / "docs" / "ERRORS.md"
        if not p1.exists() or "status code" not in git.log("pr5-docs", "--oneline"):
            return False, "pr5-docs does not contain amended pr1-base commits."
        if not p5.exists():
            return False, "pr5-docs missing documentation file."

        # Check that commit history is clean and contains the expected commits
        log = git.log("pr5-docs", "--oneline")
        for title in [
            "amend base error with status code",
            "add error log model",
            "add error reporting endpoint",
            "add error unit tests",
            "add error handling manual",
        ]:
            if title not in log:
                return False, f"Missing commit '{title}' in pr5-docs linear history."

        return True, "Successfully rebased stacked PR chain across all 5 dependent branches!"


# -----------------------------------------------------------------------------
# LEVEL 09: Rebase an Extremely Stale Branch with 30 Upstream Commits
# -----------------------------------------------------------------------------
@register_challenge
class Level09ExtremelyStaleRebase(BaseChallenge):
    level_id = "level_09"
    number = 9
    category = ChallengeCategory.B_BRANCHING
    title = "Rebase Extremely Stale Branch (30 Upstream Commits)"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "Branch 'feature/warehouse-automation' was branched off main 2 months ago. "
        "Since then, 30 commits have landed on 'main' modifying multiple packages.\n\n"
        "Your task: Rebase 'feature/warehouse-automation' cleanly onto 'main'. "
        "Ensure all warehouse automation features are preserved on top of the latest main, "
        "and resolve any conflict without losing upstream or feature changes."
    )
    initial_state_desc = "feature/warehouse-automation is 30 commits behind main."
    expected_outcome = "feature/warehouse-automation is rebased onto main with linear history."
    hints = [
        "Checkout the feature branch: `git checkout feature/warehouse-automation`.",
        "Run `git rebase main`.",
        "If conflicts occur, inspect `git status`, resolve, and `git rebase --continue`.",
    ]
    solution_guide = (
        "1. `git checkout feature/warehouse-automation`\n"
        "2. `git rebase main`\n"
        "3. If conflict in warehouse.py, preserve both zone definitions and capacity logic.\n"
        "4. `git rebase --continue` until finished."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the internal mechanism of `git rebase`?",
            key_points=[
                "Finds common ancestor of the current branch and upstream.",
                "Stores commits of current branch into temporary patch files (`.git/rebase-apply` or `.git/rebase-merge`).",
                "Resets the current branch pointer to upstream.",
                "Replays each stored commit sequentially one by one.",
            ],
            in_depth_explanation="Because rebase generates completely new commit objects with new parent SHAs and new timestamps, commit hashes are rewritten."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Initial setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Create branch off early main
        git.checkout("feature/warehouse-automation", create=True)
        wh = git.repo_path / "nexus_platform" / "app" / "services" / "warehouse_automation.py"
        wh.write_text("# Automated AGV dispatching\ndef dispatch_agv(item_id: int): return True\n")
        git.add(".")
        git.commit("feat(warehouse): add AGV dispatching service", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # Now simulate 30 commits landing on main
        git.checkout("main")
        for i in range(1, 31):
            p = git.repo_path / "nexus_platform" / "app" / f"upstream_update_{i}.txt"
            p.write_text(f"Upstream update {i}\n")
            git.add(str(p))
            git.commit(f"chore(platform): upstream system synchronization #{i}", author_name="Marcus Sterling", author_email="marcus.sterling@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        cur = git.current_branch()
        if cur != "feature/warehouse-automation":
            return False, f"Current branch is '{cur}', expected 'feature/warehouse-automation'."

        # Verify that HEAD commit is the AGV feature
        head_msg = git.log("-n", "1", "--format=%s").strip()
        if head_msg != "feat(warehouse): add AGV dispatching service":
            return False, f"Head commit message is '{head_msg}', expected 'feat(warehouse): add AGV dispatching service'."

        # Verify parent commit is the 30th commit of main
        main_tip = git.rev_parse("main")
        head_parent = git.rev_parse("HEAD~1")
        if head_parent != main_tip:
            return False, "feature/warehouse-automation is not cleanly based directly on top of main tip."

        return True, "Successfully rebased stale branch cleanly across 30 upstream commits!"


# -----------------------------------------------------------------------------
# LEVEL 10: Interactive Rebase Involving 40 Commits
# -----------------------------------------------------------------------------
@register_challenge
class Level10InteractiveRebase(BaseChallenge):
    level_id = "level_10"
    number = 10
    category = ChallengeCategory.B_BRANCHING
    title = "Interactive Rebase (Squash, Edit, Reorder, Split)"
    difficulty = "Hardcore"
    estimated_time = "35 minutes"
    description = (
        "A messy developer branch 'feature/event-pipeline' has accumulated 40 noisy, sloppy commits "
        "('wip', 'fix typo', 'oops forgot file', 'test again', 'fix fix fix').\n"
        "Company policy requires clean, atomic commits before PR approval.\n\n"
        "Your task: Clean up the branch history using interactive rebase so that:\n"
        "1. All 40 messy commits are consolidated into EXACTLY 3 clean, meaningful commits:\n"
        "   - Commit 1: 'feat(events): implement event bus architecture'\n"
        "   - Commit 2: 'feat(events): add event serialization and persistence'\n"
        "   - Commit 3: 'test(events): add comprehensive event pipeline tests'\n"
        "2. The working tree contents match the original feature branch functionality perfectly."
    )
    initial_state_desc = "feature/event-pipeline contains 40 noisy, fragmented commits."
    expected_outcome = "feature/event-pipeline contains exactly 3 clean commits on top of main."
    hints = [
        "Use `git rebase -i main` or soft reset: `git reset --soft main` then create the 3 atomic commits.",
        "Using `git reset --soft main` is a valid advanced alternative to consolidate large numbers of messy commits into atomic units.",
    ]
    solution_guide = (
        "Method A: `git checkout feature/event-pipeline && git rebase -i main` and squash.\n"
        "Method B: `git reset --soft main`, stage event bus files -> commit 1, stage serialization -> commit 2, stage tests -> commit 3."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the difference between squash and fixup in interactive rebase?",
            key_points=[
                "Both combine the commit into the previous commit in the list.",
                "`squash` prompts you to concatenate and edit the commit messages.",
                "`fixup` automatically discards the commit message of the squashed commit, keeping only the parent's message.",
            ],
            in_depth_explanation="`fixup -C <commit>` is an advanced flag that squashes into the target but replaces its message with this commit's message."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        git.checkout("feature/event-pipeline", create=True)
        # Create 40 noisy commits
        for i in range(1, 41):
            f = git.repo_path / "nexus_platform" / "app" / f"event_chunk_{i}.py"
            f.write_text(f"# Event pipeline component {i}\n")
            git.add(str(f))
            git.commit(f"wip chunk {i} fixup typo", author_name="Mateo Silva", author_email="mateo.silva@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        cur = git.current_branch()
        if cur != "feature/event-pipeline":
            return False, f"Current branch is '{cur}', expected 'feature/event-pipeline'."

        # Count commits since main
        res = git.run("rev-list", "--count", "main..HEAD").stdout.strip()
        try:
            count = int(res)
        except ValueError:
            return False, "Could not determine commit count."

        if count != 3:
            return False, f"Expected exactly 3 commits on feature/event-pipeline, but found {count}."

        commits = git.log("main..HEAD", "--format=%s").splitlines()
        expected = [
            "test(events): add comprehensive event pipeline tests",
            "feat(events): add event serialization and persistence",
            "feat(events): implement event bus architecture",
        ]
        if commits != expected:
            return False, f"Commit messages do not match expected standard.\nFound: {commits}\nExpected: {expected}"

        return True, "Successfully cleaned 40 messy commits into 3 pristine atomic commits!"
