"""Category A: Git Internals (Levels 01 - 05)."""

import os
from pathlib import Path
from typing import Tuple, Optional

from ..base import BaseChallenge, ChallengeCategory, InterviewQuestion, register_challenge
from ...core.git_client import GitClient
from ...core.repo_manager import repo_manager
from ...organization.developers import DEVELOPERS_BY_ID


# -----------------------------------------------------------------------------
# LEVEL 01: Git Object Database Investigation
# -----------------------------------------------------------------------------
@register_challenge
class Level01ObjectDatabase(BaseChallenge):
    level_id = "level_01"
    number = 1
    category = ChallengeCategory.A_INTERNALS
    title = "Git Object Database Investigation"
    difficulty = "Medium"
    estimated_time = "15 minutes"
    description = (
        "Nexus Platform security audit discovered an unreferenced, orphaned blob directly in "
        ".git/objects containing sensitive database credentials. "
        "Your task: Inspect the Git object database using git cat-file, identify the secret token "
        "stored inside the dangling blob, and write the recovered secret token into a file named "
        "'RECOVERED_SECRET.txt' at the root of the repository."
    )
    initial_state_desc = (
        "Repository initialized with initial commits. An unreferenced blob object exists in .git/objects."
    )
    expected_outcome = (
        "File 'RECOVERED_SECRET.txt' created in repository root containing exactly: 'NEXUS-CORP-SECRET-99812-TOKEN'"
    )
    hints = [
        "Use `git fsck --lost-found` or inspect `.git/objects` to find dangling blobs.",
        "Use `git cat-file -p <sha>` to view the contents of any Git object.",
        "Use `git cat-file -t <sha>` to inspect object type (blob, tree, commit, tag).",
    ]
    solution_guide = (
        "1. Run `git fsck --lost-found` to locate dangling blobs.\n"
        "2. Inspect the dangling blob: `git cat-file -p <hash>`.\n"
        "3. Write the secret token to RECOVERED_SECRET.txt: `echo 'NEXUS-CORP-SECRET-99812-TOKEN' > RECOVERED_SECRET.txt`.\n"
        "4. Run verification in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="How does Git store objects under .git/objects and what determines their hash?",
            key_points=[
                "Content-addressable storage using SHA-1 / SHA-256.",
                "Header format: '<type> <size>\\0<content>'.",
                "First 2 chars of the hex hash form the sub-directory; the remaining 38 chars form the filename.",
                "Objects are zlib-compressed.",
            ],
            in_depth_explanation=(
                "Git calculates the SHA hash over a header plus content: `sha1('blob ' + length + '\\0' + bytes)`. "
                "Because of this, identical content across different files or repositories produces the exact same object hash."
            ),
        ),
        InterviewQuestion(
            question="What are the four fundamental Git object types?",
            key_points=["blob (file data)", "tree (directory list)", "commit (metadata + root tree + parents)", "tag (annotated tag)"],
            in_depth_explanation="Blobs store content without file names or permissions; trees associate file names and modes with blob/tree hashes."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Initial Nexus Inventory Platform setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")
        
        # Inject an unreferenced dangling blob directly using git hash-object -w
        secret_content = "NEXUS-CORP-SECRET-99812-TOKEN\n"
        p = git.repo_path / ".temp_secret.txt"
        with open(p, "w", encoding="utf-8") as f:
            f.write(secret_content)
        
        # Write directly to object database
        res = git.run("hash-object", "-w", ".temp_secret.txt")
        p.unlink()

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        secret_file = git.repo_path / "RECOVERED_SECRET.txt"
        if not secret_file.exists():
            return False, "RECOVERED_SECRET.txt does not exist at repo root."
        content = secret_file.read_text(encoding="utf-8").strip()
        if content == "NEXUS-CORP-SECRET-99812-TOKEN":
            return True, "Successfully recovered orphaned secret token from Git object database!"
        return False, f"Content mismatch in RECOVERED_SECRET.txt: expected 'NEXUS-CORP-SECRET-99812-TOKEN', got '{content}'"


# -----------------------------------------------------------------------------
# LEVEL 02: Detached HEAD Recovery
# -----------------------------------------------------------------------------
@register_challenge
class Level02DetachedHeadRecovery(BaseChallenge):
    level_id = "level_02"
    number = 2
    category = ChallengeCategory.A_INTERNALS
    title = "Detached HEAD Recovery"
    difficulty = "Medium"
    estimated_time = "15 minutes"
    description = (
        "A junior engineer on the Backend team checked out an earlier commit by hash and added 2 critical "
        "commits fixing order inventory reservation, but then accidentally switched back to main without creating "
        "a branch! The commits are now orphaned in detached HEAD.\n"
        "Your task: Locate the detached commits and recover them cleanly onto a new branch named 'feature/recovered-work', "
        "ensuring HEAD points to 'feature/recovered-work' and working tree is clean."
    )
    initial_state_desc = "On branch main. 2 commits were made in detached HEAD and are unreferenced by any branch."
    expected_outcome = "Current branch is 'feature/recovered-work', containing both commits: 'fix(inventory): add lock' and 'test(inventory): add concurrency test'."
    hints = [
        "Use `git reflog` to find the SHA of the commits made during the detached HEAD state.",
        "Create a branch pointing to that commit: `git branch feature/recovered-work <sha>`.",
        "Switch to the branch: `git switch feature/recovered-work`.",
    ]
    solution_guide = (
        "1. Check reflog: `git reflog`\n"
        "2. Identify the commit hash for 'test(inventory): add concurrency test'.\n"
        "3. Switch and create branch: `git checkout -b feature/recovered-work <hash>`.\n"
        "4. Verify working tree is clean."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is detached HEAD state in Git?",
            key_points=[
                "HEAD points directly to a commit hash rather than a branch ref (refs/heads/<name>).",
                "New commits are created normally, updating HEAD to the new commit.",
                "Switching away without creating a branch leaves commits unreachable by any ref.",
            ],
            in_depth_explanation=(
                "Normally .git/HEAD contains 'ref: refs/heads/main'. In detached HEAD, .git/HEAD contains "
                "the 40-character commit SHA itself. Commits made here risk garbage collection after 30 days "
                "once reflog expires."
            ),
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("feat: initial platform code", author_name="Devon Mercer", author_email="devon.mercer@nexus.internal")
        first_sha = git.rev_parse("HEAD")

        # Checkout first_sha directly -> Detached HEAD
        git.checkout(first_sha)
        
        # Add commit 1 in detached HEAD
        inv_file = git.repo_path / "nexus_platform" / "app" / "services" / "inventory.py"
        with open(inv_file, "a") as f:
            f.write("\n# Concurrency lock added\n")
        git.add(".")
        git.commit("fix(inventory): add lock", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # Add commit 2 in detached HEAD
        test_file = git.repo_path / "nexus_platform" / "tests" / "test_concurrency.py"
        test_file.write_text("# Test concurrency\ndef test_lock(): pass\n")
        git.add(".")
        git.commit("test(inventory): add concurrency test", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # Now switch back to main leaving HEAD detached commits behind
        git.checkout("main")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        cur = git.current_branch()
        if cur != "feature/recovered-work":
            return False, f"Current branch is '{cur}', expected 'feature/recovered-work'."
        log = git.log("-n", "5", "--oneline")
        if "test(inventory): add concurrency test" not in log:
            return False, "Missing commit 'test(inventory): add concurrency test' on feature/recovered-work."
        if "fix(inventory): add lock" not in log:
            return False, "Missing commit 'fix(inventory): add lock' on feature/recovered-work."
        return True, "Successfully recovered detached HEAD commits onto feature/recovered-work!"


# -----------------------------------------------------------------------------
# LEVEL 03: Reflog Forensic Investigation
# -----------------------------------------------------------------------------
@register_challenge
class Level03ReflogForensics(BaseChallenge):
    level_id = "level_03"
    number = 3
    category = ChallengeCategory.A_INTERNALS
    title = "Reflog Forensic Investigation"
    difficulty = "Hard"
    estimated_time = "20 minutes"
    description = (
        "Disaster on Platform team: A developer intended to discard uncommitted changes but ran "
        "`git reset --hard HEAD~3` on main, and also accidentally ran `git branch -D feature/critical-fix`!\n"
        "Three vital commits were stripped from main, and the critical hotfix branch was deleted.\n"
        "Your task:\n"
        "1. Restore 'main' to its exact tip commit before the reset ('feat(orders): add bulk order processing').\n"
        "2. Re-create the deleted branch 'feature/critical-fix' pointing to its lost commit ('fix(auth): patch token expiration bug')."
    )
    initial_state_desc = "main is 3 commits behind where it was; feature/critical-fix branch is deleted."
    expected_outcome = "main tip is 'feat(orders): add bulk order processing'; feature/critical-fix exists pointing to 'fix(auth): patch token expiration bug'."
    hints = [
        "Use `git reflog show main` or `git reflog` to see all previous HEAD movements.",
        "Reset main back: `git reset --hard HEAD@{n}` or `git reset --hard <sha>`.",
        "Inspect reflog to find the commit where feature/critical-fix was before deletion, then `git branch feature/critical-fix <sha>`.",
    ]
    solution_guide = (
        "1. Run `git reflog`.\n"
        "2. Find the SHA for 'feat(orders): add bulk order processing' and run `git reset --hard <sha>` on main.\n"
        "3. Find the SHA for 'fix(auth): patch token expiration bug' and run `git branch feature/critical-fix <sha>`.\n"
        "4. Verify branches and commits."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the difference between git log and git reflog?",
            key_points=[
                "git log traverses the commit DAG (Directed Acyclic Graph) backwards from a ref.",
                "git reflog is a purely local chronological record of every time HEAD or local branch tips moved.",
                "Reflog is not pushed or shared with remotes; it defaults to a 90-day expiration.",
            ],
            in_depth_explanation=(
                "git log only sees commits that are reachable. When a branch is reset or deleted, commits become "
                "unreachable in the DAG and vanish from `git log`. But the local reflog preserves their commit hashes "
                "until git prune/gc runs."
            ),
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Initial platform setup", author_name="Maya Chen", author_email="maya.chen@nexus.internal")

        # 3 commits on main
        git.commit("feat(reporting): add valuation metrics", author_name="Maya Chen", author_email="maya.chen@nexus.internal", allow_empty=True)
        git.commit("feat(events): add audit stream indexing", author_name="Maya Chen", author_email="maya.chen@nexus.internal", allow_empty=True)
        git.commit("feat(orders): add bulk order processing", author_name="Maya Chen", author_email="maya.chen@nexus.internal", allow_empty=True)

        # Create feature/critical-fix branch
        git.checkout("feature/critical-fix", create=True)
        git.commit("fix(auth): patch token expiration bug", author_name="Aria Vance", author_email="aria.vance@nexus.internal", allow_empty=True)
        
        # Switch back to main
        git.checkout("main")
        # Accidentally delete feature/critical-fix
        git.run("branch", "-D", "feature/critical-fix")
        # Accidentally hard reset main 3 commits back
        git.reset_hard("HEAD~3")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        main_log = git.log("main", "-n", "1", "--oneline")
        if "feat(orders): add bulk order processing" not in main_log:
            return False, f"main tip is incorrect: {main_log}. Expected 'feat(orders): add bulk order processing'."
        
        branches = git.list_branches()
        if "feature/critical-fix" not in branches:
            return False, "Branch 'feature/critical-fix' has not been restored."
        
        fix_log = git.log("feature/critical-fix", "-n", "1", "--oneline")
        if "fix(auth): patch token expiration bug" not in fix_log:
            return False, f"feature/critical-fix tip is incorrect: {fix_log}"
        
        return True, "Successfully recovered main tip and restored feature/critical-fix via reflog!"


# -----------------------------------------------------------------------------
# LEVEL 04: Git Index Surgery
# -----------------------------------------------------------------------------
@register_challenge
class Level04IndexSurgery(BaseChallenge):
    level_id = "level_04"
    number = 4
    category = ChallengeCategory.A_INTERNALS
    title = "Git Index Surgery"
    difficulty = "Medium"
    estimated_time = "15 minutes"
    description = (
        "A developer carelessly ran `git add .` staging mixed, unrelated changes across 3 files: "
        "a critical bug fix in 'nexus_platform/app/services/orders.py', a messy experimental debug log "
        "in 'nexus_platform/app/main.py', and an unwanted local test file 'scratch_test.py'.\n"
        "Your task:\n"
        "1. Unstage the debug changes and unwanted files without losing work in working tree.\n"
        "2. Commit ONLY the bug fix in 'nexus_platform/app/services/orders.py' with commit message "
        "'fix(orders): validate stock before reserving'.\n"
        "3. Leave 'nexus_platform/app/main.py' unstaged in working directory and remove 'scratch_test.py'."
    )
    initial_state_desc = "Multiple unrelated changes staged in index."
    expected_outcome = "Only orders.py committed. main.py has unstaged changes. scratch_test.py removed."
    hints = [
        "Use `git restore --staged <file>` or `git reset HEAD <file>` to unstage without touching working tree.",
        "Commit only orders.py.",
        "Delete scratch_test.py.",
    ]
    solution_guide = (
        "1. `git restore --staged nexus_platform/app/main.py`\n"
        "2. `git restore --staged scratch_test.py`\n"
        "3. `rm scratch_test.py`\n"
        "4. `git commit -m 'fix(orders): validate stock before reserving'`\n"
        "5. Verify state."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the Git Index (staging area) and what file represents it?",
            key_points=[
                "Represented by binary file `.git/index`.",
                "Stores a list of path names, file modes, timestamps, and SHA-1/SHA-256 blob references.",
                "Acts as the preparation cache for the next tree object to be committed.",
            ],
            in_depth_explanation=(
                "When you run `git add`, Git writes blob objects into `.git/objects` and records their entries "
                "in `.git/index`. When you run `git commit`, Git writes tree objects representing the index and "
                "points a new commit object to the root tree."
            ),
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Initial setup", author_name="Devon Mercer", author_email="devon.mercer@nexus.internal")

        # 1. Modify orders.py (The legitimate fix)
        orders_file = git.repo_path / "nexus_platform" / "app" / "services" / "orders.py"
        with open(orders_file, "a") as f:
            f.write("\n# Verified: validate stock before reservation\n")

        # 2. Modify main.py (Messy debug)
        main_file = git.repo_path / "nexus_platform" / "app" / "main.py"
        with open(main_file, "a") as f:
            f.write("\n# DEBUG_LOG: print(request.headers)\n")

        # 3. Add scratch_test.py
        scratch_file = git.repo_path / "scratch_test.py"
        scratch_file.write_text("import sys; print('scratch')\n")

        # Stage everything
        git.add(".")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        last_commit = git.log("-n", "1", "--format=%s").strip()
        if last_commit != "fix(orders): validate stock before reserving":
            return False, f"Latest commit message is '{last_commit}', expected 'fix(orders): validate stock before reserving'."
        
        diff_commit = git.run("show", "--name-only", "--format=", "HEAD").stdout.strip().splitlines()
        clean_diff = [f.strip() for f in diff_commit if f.strip()]
        if clean_diff != ["nexus_platform/app/services/orders.py"]:
            return False, f"Latest commit modified unexpected files: {clean_diff}. Expected only orders.py."

        scratch_file = git.repo_path / "scratch_test.py"
        if scratch_file.exists():
            return False, "scratch_test.py still exists in repo root."

        status = git.status()
        if "nexus_platform/app/main.py" not in status:
            return False, "Expected unstaged changes in nexus_platform/app/main.py."

        return True, "Successfully performed index surgery and committed clean atomic change!"


# -----------------------------------------------------------------------------
# LEVEL 05: Advanced Commit Archaeology
# -----------------------------------------------------------------------------
@register_challenge
class Level05CommitArchaeology(BaseChallenge):
    level_id = "level_05"
    number = 5
    category = ChallengeCategory.A_INTERNALS
    title = "Advanced Commit Archaeology"
    difficulty = "Hard"
    estimated_time = "20 minutes"
    description = (
        "A critical regression was introduced into 'nexus_platform/app/services/auth.py' somewhere in a series of "
        "40 rapid commits authored by multiple engineers, breaking HMAC token verification security.\n"
        "Your task:\n"
        "1. Investigate the Git history using `git log -S`, `git blame`, or `git bisect`.\n"
        "2. Identify the exact commit SHA that introduced the bug.\n"
        "3. Write the 40-character commit SHA into 'CULPRIT_COMMIT.txt' at the repository root."
    )
    initial_state_desc = "40 commits present in history. auth.py has a security bug where HMAC verification returns True unconditionally."
    expected_outcome = "CULPRIT_COMMIT.txt contains the exact 40-character SHA that introduced the defect."
    hints = [
        "Inspect auth.py: look for where `hmac.compare_digest` was replaced or altered.",
        "Use `git log -S 'compare_digest' -p` to find the exact commit modifying that line.",
        "Alternatively use `git blame nexus_platform/app/services/auth.py`.",
    ]
    solution_guide = (
        "1. Inspect auth.py: `git log -p -S 'return True # BUG' nexus_platform/app/services/auth.py`\n"
        "2. Note the commit SHA.\n"
        "3. Save to file: `git log -1 --format=%H <commit> > CULPRIT_COMMIT.txt`\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the difference between git log -S (pickaxe) and git log -G?",
            key_points=[
                "git log -S <string> looks for differences that change the number of occurrences of the specified string.",
                "git log -G <regex> looks for differences whose patch text contains added/removed lines matching the regex.",
            ],
            in_depth_explanation=(
                "-S (the pickaxe) is ideal for finding when an exact symbol or function was introduced or completely removed. "
                "-G matches if any line matching the regex was added or modified."
            ),
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Initial platform setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        auth_path = git.repo_path / "nexus_platform" / "app" / "services" / "auth.py"
        culprit_index = 23

        for i in range(1, 41):
            if i == culprit_index:
                # Introduce the security bug
                text = auth_path.read_text()
                text = text.replace("return {\"username\": username, \"role\": role, \"timestamp\": timestamp}", "return {\"username\": username, \"role\": 'admin', \"timestamp\": timestamp} # BUGGED_AUTH")
                auth_path.write_text(text)
                git.add(str(auth_path))
                git.commit(
                    "refactor(auth): optimize token parsing speed",
                    author_name="Kavita Sharma",
                    author_email="kavita.sharma@nexus.internal",
                )
            else:
                dummy_file = git.repo_path / "nexus_platform" / "app" / f"metric_{i}.log"
                dummy_file.write_text(f"metric_{i}=true\n")
                git.add(str(dummy_file))
                git.commit(
                    f"chore(metrics): update telemetry metric counter {i}",
                    author_name="Mateo Silva",
                    author_email="mateo.silva@nexus.internal",
                )

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        culprit_file = git.repo_path / "CULPRIT_COMMIT.txt"
        if not culprit_file.exists():
            return False, "CULPRIT_COMMIT.txt does not exist in repo root."
        sha = culprit_file.read_text().strip()
        if len(sha) < 7:
            return False, f"Invalid SHA format: '{sha}'"

        # Check if the commit modified auth.py with the bug
        res = git.run("show", sha, "--name-only")
        if "nexus_platform/app/services/auth.py" not in res.stdout:
            return False, f"Commit {sha} did not modify auth.py."

        diff = git.run("show", sha).stdout
        if "BUGGED_AUTH" in diff:
            return True, f"Correctly identified regression commit {sha[:10]} using commit archaeology!"
        return False, f"Commit {sha} is not the commit that introduced the BUGGED_AUTH regression."

