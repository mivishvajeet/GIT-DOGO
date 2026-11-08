"""Category D: Release Engineering (Levels 21 - 25)."""

from pathlib import Path
from typing import Tuple, Optional

from ..base import BaseChallenge, ChallengeCategory, InterviewQuestion, register_challenge
from ...core.git_client import GitClient
from ...core.repo_manager import repo_manager


# -----------------------------------------------------------------------------
# LEVEL 21: Release Branch Management
# -----------------------------------------------------------------------------
@register_challenge
class Level21ReleaseBranchManagement(BaseChallenge):
    level_id = "level_21"
    number = 21
    category = ChallengeCategory.D_RELEASE
    title = "Release Branch Cut & Stabilization"
    difficulty = "Medium"
    estimated_time = "20 minutes"
    description = (
        "Nexus Platform is cutting release v1.4.0 from main:\n"
        "1. Create a release branch named 'release/v1.4.0' from 'main'.\n"
        "2. In the release branch, bump `version.txt` and `nexus_platform/app/config.py` to '1.4.0'.\n"
        "3. Update `CHANGELOG.md` with release notes for v1.4.0.\n"
        "4. Commit the release preparation commit with message 'chore(release): prepare v1.4.0'.\n"
        "5. Tag the commit with an annotated tag 'v1.4.0' and message 'Release v1.4.0'."
    )
    initial_state_desc = "On branch main at pre-release state (version 1.3.9)."
    expected_outcome = "Branch release/v1.4.0 created with version bumped, changelog updated, and annotated tag v1.4.0."
    hints = [
        "Create branch: `git checkout -b release/v1.4.0`.",
        "Edit version.txt and config.py, updating version string to 1.4.0.",
        "Create annotated tag: `git tag -a v1.4.0 -m 'Release v1.4.0'`.",
    ]
    solution_guide = (
        "1. `git checkout -b release/v1.4.0`\n"
        "2. Update version.txt to 1.4.0\n"
        "3. Commit: `git commit -am 'chore(release): prepare v1.4.0'`\n"
        "4. `git tag -a v1.4.0 -m 'Release v1.4.0'`\n"
        "5. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the difference between a lightweight tag and an annotated tag in Git?",
            key_points=[
                "A lightweight tag is just an uncompressed pointer (symref) to a commit SHA in `.git/refs/tags/`.",
                "An annotated tag creates a full Git object in `.git/objects` with its own author, date, message, and optional GPG signature.",
                "Production releases should always use annotated tags.",
            ],
            in_depth_explanation="Annotated tags (`git tag -a`) store who created the tag and when, whereas lightweight tags (`git tag <name>`) carry no metadata beyond the commit they point to."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        (git.repo_path / "version.txt").write_text("1.3.9\n")
        (git.repo_path / "CHANGELOG.md").write_text("# Nexus Platform Changelog\n\n## v1.3.9\n- Base version\n")
        git.add(".")
        git.commit("Base platform setup for release train", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        branches = git.list_branches()
        if "release/v1.4.0" not in branches:
            return False, "Branch 'release/v1.4.0' does not exist."

        tags = git.list_tags()
        if "v1.4.0" not in tags:
            return False, "Annotated tag 'v1.4.0' does not exist."

        # Verify tag is annotated
        tag_type = git.cat_file("-t", "v1.4.0").stdout.strip()
        if tag_type != "tag":
            return False, f"Tag 'v1.4.0' is lightweight (object type: {tag_type}). Expected an annotated tag object."

        git.checkout("release/v1.4.0")
        v_text = (git.repo_path / "version.txt").read_text().strip()
        if v_text != "1.4.0":
            return False, f"version.txt is '{v_text}', expected '1.4.0'."

        return True, "Successfully executed release branch cut, version bump, and annotated release tagging!"


# -----------------------------------------------------------------------------
# LEVEL 22: Emergency Production Hotfix
# -----------------------------------------------------------------------------
@register_challenge
class Level22EmergencyHotfix(BaseChallenge):
    level_id = "level_22"
    number = 22
    category = ChallengeCategory.D_RELEASE
    title = "Emergency Production Hotfix & Dual-Merge"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "Production Incident: Tag 'v1.4.0' is currently deployed in production. "
        "A critical zero-day vulnerability was discovered in inventory order allocation.\n"
        "Meanwhile, 'main' has moved forward with 5 experimental v1.5.0 features that CANNOT be released yet.\n\n"
        "Your task:\n"
        "1. Branch an emergency hotfix from the tag 'v1.4.0' named 'hotfix/v1.4.1'.\n"
        "2. Apply the fix: append `# SECURITY_HOTFIX_APPLIED` to 'nexus_platform/app/services/inventory.py'.\n"
        "3. Bump 'version.txt' to '1.4.1'.\n"
        "4. Commit with message 'fix(sec): patch critical inventory zero-day'.\n"
        "5. Tag the hotfix commit with annotated tag 'v1.4.1'.\n"
        "6. Dual-merge: Merge 'hotfix/v1.4.1' into 'main' so the fix is never lost in future releases."
    )
    initial_state_desc = "v1.4.0 is tagged. main has advanced with experimental commits."
    expected_outcome = "v1.4.1 tagged on hotfix commit branched from v1.4.0; hotfix merged into main."
    hints = [
        "Checkout tag: `git checkout -b hotfix/v1.4.1 v1.4.0`.",
        "Apply fix, bump version, commit, and tag: `git tag -a v1.4.1 -m 'Hotfix v1.4.1'`.",
        "Merge into main: `git checkout main && git merge hotfix/v1.4.1`.",
    ]
    solution_guide = (
        "1. `git checkout -b hotfix/v1.4.1 v1.4.0`\n"
        "2. Edit inventory.py and version.txt (1.4.1)\n"
        "3. `git commit -am 'fix(sec): patch critical inventory zero-day'`\n"
        "4. `git tag -a v1.4.1 -m 'Release v1.4.1'`\n"
        "5. `git checkout main && git merge hotfix/v1.4.1`\n"
        "6. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the Dual-Merge or Back-Merge pattern in release engineering?",
            key_points=[
                "Hotfixes branched from older release tags must be merged back into `main` (trunk).",
                "If omitted, the next major release will suffer a regression when the old bug resurfaces.",
                "Some teams use automated cherry-pick bots or dual-merge PR workflows.",
            ],
            in_depth_explanation="A frequent source of production incidents is fixing an issue on a maintenance branch while forgetting to backport/merge the fix into the development mainline."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        (git.repo_path / "version.txt").write_text("1.4.0\n")
        git.add(".")
        git.commit("Release v1.4.0 baseline", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")
        git.tag("v1.4.0", message="Production release 1.4.0")

        # 5 experimental commits land on main
        for i in range(1, 6):
            (git.repo_path / f"exp_v15_{i}.py").write_text(f"# Experimental v1.5 feature {i}\n")
            git.add(".")
            git.commit(f"feat(experimental): v1.5 prototype #{i}", author_name="Marcus Sterling", author_email="marcus.sterling@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        tags = git.list_tags()
        if "v1.4.1" not in tags:
            return False, "Annotated tag 'v1.4.1' does not exist."

        # Check that hotfix is an ancestor of main
        hotfix_sha = git.rev_parse("v1.4.1^{commit}")
        main_sha = git.rev_parse("main")
        if not git.run("merge-base", "--is-ancestor", hotfix_sha, main_sha).success:
            return False, "Hotfix commit is not merged into 'main'!"

        # Check that main contains the security hotfix
        inv_text = (git.repo_path / "nexus_platform" / "app" / "services" / "inventory.py").read_text()
        if "SECURITY_HOTFIX_APPLIED" not in inv_text:
            return False, "SECURITY_HOTFIX_APPLIED not found on main."

        return True, "Successfully executed emergency production hotfix and dual-merged into mainline!"


# -----------------------------------------------------------------------------
# LEVEL 23: Cherry-Pick Across Three Maintained Release Branches
# -----------------------------------------------------------------------------
@register_challenge
class Level23CherryPickAcrossReleases(BaseChallenge):
    level_id = "level_23"
    number = 23
    category = ChallengeCategory.D_RELEASE
    title = "Backporting: Cherry-Pick Across 3 Supported Release Branches"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "Nexus Platform supports 3 active LTS release branches in production:\n"
        "- `release/v1.2`\n"
        "- `release/v1.3`\n"
        "- `release/v1.4`\n\n"
        "A critical timing attack fix was authored on 'main' in commit 'fix(auth): prevent timing attack in token verify'.\n"
        "Your task: Cherry-pick this exact security fix cleanly onto ALL THREE release branches (`release/v1.2`, "
        "`release/v1.3`, `release/v1.4`), ensuring all 3 branches contain the patch."
    )
    initial_state_desc = "Security patch exists on main. 3 release branches are unpatched."
    expected_outcome = "All 3 release branches contain the cherry-picked security commit."
    hints = [
        "Find the SHA of the security commit: `git log -1 --grep='prevent timing attack' --format=%H`.",
        "For each release branch: checkout and run `git cherry-pick <sha>`.",
    ]
    solution_guide = (
        "1. Identify commit hash on main.\n"
        "2. `git checkout release/v1.2 && git cherry-pick <sha>`\n"
        "3. `git checkout release/v1.3 && git cherry-pick <sha>`\n"
        "4. `git checkout release/v1.4 && git cherry-pick <sha>`\n"
        "5. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is `git cherry-pick -x` and why is it recommended for backports?",
            key_points=[
                "`-x` appends a line to the commit message: `(cherry picked from commit <sha>)`.",
                "Establishes lineage and audit trail across maintenance branches.",
                "Enables automated tooling and security scanners to track patch propagation.",
            ],
            in_depth_explanation="Without `-x`, cherry-picked commits look completely unrelated in Git's object database, making it difficult to audit whether an LTS branch has received a CVE fix."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base platform setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Create 3 LTS branches
        for ver in ["v1.2", "v1.3", "v1.4"]:
            git.checkout(f"release/{ver}", create=True)
            (git.repo_path / "version.txt").write_text(f"{ver}.0\n")
            git.add(".")
            git.commit(f"chore(release): cut {ver}", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # On main, commit the critical security fix
        git.checkout("main")
        auth_file = git.repo_path / "nexus_platform" / "app" / "services" / "auth.py"
        with open(auth_file, "a") as f:
            f.write("\n# TIMING_ATTACK_FIX: constant time comparison enforced\n")
        git.add(str(auth_file))
        git.commit("fix(auth): prevent timing attack in token verify", author_name="Security Team", author_email="security@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        for ver in ["release/v1.2", "release/v1.3", "release/v1.4"]:
            log = git.log(ver, "--oneline")
            if "prevent timing attack in token verify" not in log:
                return False, f"Branch {ver} is missing the cherry-picked security fix."

        return True, "Successfully backported critical security fix across all 3 LTS release branches!"


# -----------------------------------------------------------------------------
# LEVEL 24: Recover from a Broken Release Tag
# -----------------------------------------------------------------------------
@register_challenge
class Level24RecoverBrokenReleaseTag(BaseChallenge):
    level_id = "level_24"
    number = 24
    category = ChallengeCategory.D_RELEASE
    title = "Recover from an Incorrectly Tagged Release"
    difficulty = "Medium"
    estimated_time = "15 minutes"
    description = (
        "An automated deployment webhook triggered erroneously because release engineer tagged "
        "an unready commit ('v2.0.0' pointing to a broken experimental WIP commit)!\n"
        "Production deployment failed.\n\n"
        "Your task:\n"
        "1. Identify the correct stable commit marked with message 'chore(release): prepare production v2.0.0'.\n"
        "2. Retag 'v2.0.0' with an annotated tag pointing to the correct stable commit with message "
        "'Release v2.0.0 Stable'.\n"
        "3. Ensure the previous erroneous tag is completely replaced."
    )
    initial_state_desc = "Tag v2.0.0 points to a broken WIP commit instead of the stable release commit."
    expected_outcome = "Annotated tag v2.0.0 points to the commit 'chore(release): prepare production v2.0.0'."
    hints = [
        "Delete the old tag: `git tag -d v2.0.0`.",
        "Find the SHA of 'chore(release): prepare production v2.0.0'.",
        "Create the new tag: `git tag -a v2.0.0 <sha> -m 'Release v2.0.0 Stable'`.",
    ]
    solution_guide = (
        "1. `git log --grep='prepare production v2.0.0' --oneline`\n"
        "2. `git tag -d v2.0.0`\n"
        "3. `git tag -a v2.0.0 <sha> -m 'Release v2.0.0 Stable'`\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="Why is deleting or moving a published Git tag considered dangerous?",
            key_points=[
                "Git clients cache tags permanently once fetched; `git pull` does not automatically update changed tags.",
                "Developers and build servers will have conflicting SHAs for the same tag name.",
                "If a tag must be changed, communication or creating a new patch tag (e.g. `v2.0.1`) is preferred.",
            ],
            in_depth_explanation="If forced retagging is unavoidable, clients must run `git fetch --tags --force` to synchronize local tag refs with the remote."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base platform setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Stable release commit
        (git.repo_path / "version.txt").write_text("2.0.0\n")
        git.add(".")
        git.commit("chore(release): prepare production v2.0.0", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")
        stable_sha = git.rev_parse("HEAD")

        # Broken WIP commit
        (git.repo_path / "broken_wip.py").write_text("SYNTAX ERROR BROKEN\n")
        git.add(".")
        git.commit("wip: broken experimental prototype", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")
        
        # Erroneously tag the broken commit!
        git.tag("v2.0.0", message="Release v2.0.0 Broken", ref="HEAD")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        tag_target = git.rev_parse("v2.0.0^{commit}")
        target_log = git.log(tag_target, "-n", "1", "--format=%s").strip()

        if target_log != "chore(release): prepare production v2.0.0":
            return False, f"Tag v2.0.0 points to '{target_log}', expected 'chore(release): prepare production v2.0.0'."

        tag_type = git.cat_file("-t", "v2.0.0").stdout.strip()
        if tag_type != "tag":
            return False, "Tag v2.0.0 is not an annotated tag object."

        return True, "Successfully corrected release tag to stable release commit!"


# -----------------------------------------------------------------------------
# LEVEL 25: Roll Back a Failed Release and Re-Release Safely
# -----------------------------------------------------------------------------
@register_challenge
class Level25RollbackFailedRelease(BaseChallenge):
    level_id = "level_25"
    number = 25
    category = ChallengeCategory.D_RELEASE
    title = "Roll Back Failed Release & Safe Re-Release"
    difficulty = "Hard"
    estimated_time = "30 minutes"
    description = (
        "Release 'v1.6.0' was deployed and crashed immediately due to a database deadlock.\n"
        "The SRE team triggered an automated rollback to 'v1.5.0'.\n\n"
        "Your task as Release Manager:\n"
        "1. On 'main', revert the faulty release merge commit ('Merge branch 'release/v1.6.0'') using `git revert -m 1`.\n"
        "2. Fix the deadlock issue in 'nexus_platform/app/services/orders.py' by appending `# DEADLOCK_RESOLVED`.\n"
        "3. Bump 'version.txt' to '1.6.1'.\n"
        "4. Commit the fix and tag the corrected release with annotated tag 'v1.6.1' ('Release v1.6.1 Stable')."
    )
    initial_state_desc = "v1.6.0 merge is active on main causing deadlocks."
    expected_outcome = "v1.6.0 reverted, deadlock fixed, version bumped to 1.6.1, and annotated tag v1.6.1 created."
    hints = [
        "Revert merge commit: `git revert -m 1 <merge_sha>`.",
        "Add `# DEADLOCK_RESOLVED` to orders.py.",
        "Bump version.txt to 1.6.1.",
        "Tag `v1.6.1`.",
    ]
    solution_guide = (
        "1. Revert merge: `git revert -m 1 HEAD`\n"
        "2. Edit orders.py and version.txt\n"
        "3. `git commit -am 'fix(orders): resolve deadlock and prepare v1.6.1'`\n"
        "4. `git tag -a v1.6.1 -m 'Release v1.6.1 Stable'`\n"
        "5. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the difference between rolling back code in Git vs rolling back deployments in Kubernetes/Cloud?",
            key_points=[
                "Git rollback is a code-level change (revert commit or forward-fix) that goes through CI/CD.",
                "Deployment rollback switches container traffic immediately to the previous image replica set.",
                "In high-velocity organizations, deployment rollback buys time for engineers to craft a clean Git forward-fix.",
            ],
            in_depth_explanation="Rolling forward (applying a fix as a new commit) is generally preferred over force-resetting mainline branches in production environments."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        (git.repo_path / "version.txt").write_text("1.5.0\n")
        git.add(".")
        git.commit("Release v1.5.0 baseline", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")
        git.tag("v1.5.0", message="Release v1.5.0")

        # Branch v1.6.0
        git.checkout("release/v1.6.0", create=True)
        (git.repo_path / "nexus_platform" / "app" / "services" / "orders.py").write_text(
            (git.repo_path / "nexus_platform" / "app" / "services" / "orders.py").read_text() + "\n# BUG: DEADLOCK IN TRANSACTION\n"
        )
        (git.repo_path / "version.txt").write_text("1.6.0\n")
        git.add(".")
        git.commit("feat(release): v1.6.0 features", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Merge to main
        git.checkout("main")
        git.merge("release/v1.6.0", message="Merge branch 'release/v1.6.0'", no_ff=True)
        git.tag("v1.6.0", message="Release v1.6.0")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        tags = git.list_tags()
        if "v1.6.1" not in tags:
            return False, "Annotated tag 'v1.6.1' does not exist."

        v_file = git.repo_path / "version.txt"
        if v_file.read_text().strip() != "1.6.1":
            return False, "version.txt does not reflect 1.6.1."

        orders_text = (git.repo_path / "nexus_platform" / "app" / "services" / "orders.py").read_text()
        if "DEADLOCK_RESOLVED" not in orders_text:
            return False, "Deadlock fix (# DEADLOCK_RESOLVED) missing from orders.py."

        return True, "Successfully rolled back faulty release and published clean v1.6.1!"

