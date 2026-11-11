"""Category C: Distributed Team Simulation (Levels 16 - 20)."""

from pathlib import Path
from typing import Tuple, Optional
import json

from ..base import BaseChallenge, ChallengeCategory, InterviewQuestion, register_challenge
from ...core.git_client import GitClient
from ...core.repo_manager import repo_manager
from ...organization.developers import DEVELOPERS


# -----------------------------------------------------------------------------
# LEVEL 16: 10 Developers Editing the Same Modules Concurrently
# -----------------------------------------------------------------------------
@register_challenge
class Level16ConcurrentDevelopers(BaseChallenge):
    level_id = "level_16"
    number = 16
    category = ChallengeCategory.C_DISTRIBUTED
    title = "Concurrent Team Simulation: 10 Developers in One Module"
    difficulty = "Hardcore"
    estimated_time = "35 minutes"
    description = (
        "Nexus Platform high-concurrency surge: 10 developers across Backend, Data, and Platform teams "
        "have branched off main and committed independent enhancements to 'nexus_platform/app/services/inventory.py'.\n"
        "Their branches are named 'dev/branch-01' through 'dev/branch-10'.\n\n"
        "Your task: Integrate all 10 branches into 'main' cleanly. Resolve any merge conflicts, "
        "ensure no developer's code is deleted or overwritten, and run automated integration tests to confirm "
        "the inventory service remains fully functional and bug-free."
    )
    initial_state_desc = "10 independent developer branches ready to integrate into main."
    expected_outcome = "All 10 branches integrated into main. All 10 developer enhancements preserved. Tests pass."
    hints = [
        "Iterate over branches `dev/branch-01` to `dev/branch-10` and merge each into `main`.",
        "When conflicts arise in inventory.py, preserve both helper functions.",
        "Run `python3 -m unittest discover -s nexus_platform/tests` to verify."
    ]
    solution_guide = (
        "1. For i in {01..10}: `git merge dev/branch-$i`\n"
        "2. Resolve conflict markers in inventory.py keeping all functions intact.\n"
        "3. Complete merge commit.\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="How do large engineering organizations prevent merge thrashing when many developers touch common files?",
            key_points=[
                "Modular architecture (loose coupling, high cohesion) to reduce shared blast radius.",
                "Feature flags (Trunk-Based Development) allowing small frequent merges.",
                "Automated Merge Queues (e.g. GitHub Merge Queue / Bors) ensuring atomic CI validation before landing.",
            ],
            in_depth_explanation="Merge queues serialize the landing of approved PRs into temporary speculative branches, running full CI in parallel to prevent main breakage."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base platform setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Create 10 distinct developer branches
        for i in range(1, 11):
            branch_name = f"dev/branch-{i:02d}"
            git.checkout("main")
            git.checkout(branch_name, create=True)
            
            dev = DEVELOPERS[i]
            inv_file = git.repo_path / "nexus_platform" / "app" / "services" / "inventory.py"
            with open(inv_file, "a") as f:
                f.write(f"\ndef dev_enhancement_{i:02d}():\n    '''Authored by {dev.name} ({dev.team_id})'''\n    return 'feature_{i:02d}_active'\n")
            
            git.add(str(inv_file))
            git.commit(
                f"feat(inventory): add enhancement #{i:02d}",
                author_name=dev.name,
                author_email=dev.email,
            )

        git.checkout("main")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        cur = git.current_branch()
        if cur != "main":
            return False, f"Current branch is '{cur}', expected 'main'."

        inv_file = git.repo_path / "nexus_platform" / "app" / "services" / "inventory.py"
        content = inv_file.read_text()

        # Check for conflict markers
        if "<<<<<<<" in content or "=======" in content or ">>>>>>>" in content:
            return False, "Conflict markers detected in inventory.py!"

        # Check that all 10 enhancements are present
        missing = []
        for i in range(1, 11):
            func_name = f"def dev_enhancement_{i:02d}"
            if func_name not in content:
                missing.append(f"dev/branch-{i:02d}")

        if missing:
            return False, f"Missing enhancements from branches: {missing}"

        return True, "Successfully integrated all 10 concurrent developer branches without losing code!"


# -----------------------------------------------------------------------------
# LEVEL 17: Handle Multiple PRs Modifying Shared API Contracts
# -----------------------------------------------------------------------------
@register_challenge
class Level17SharedApiContracts(BaseChallenge):
    level_id = "level_17"
    number = 17
    category = ChallengeCategory.C_DISTRIBUTED
    title = "Concurrent PRs on Shared API Contracts"
    difficulty = "Hard"
    estimated_time = "30 minutes"
    description = (
        "Two high-impact PRs modify the core API contract schema 'contracts/api-schema.json':\n"
        "- Frontend Team on 'pr/frontend-pagination' added `page`, `page_size`, and `total_pages` fields.\n"
        "- Data Team on 'pr/data-analytics' added `analytics_trace_id` and `timestamp_epoch_ms`.\n\n"
        "Both teams submitted PRs modifying the same JSON schema block.\n"
        "Your task: Merge both PRs into 'main'. Resolve JSON syntax conflicts cleanly, ensuring valid JSON, "
        "preserving all 5 new contract fields, and ensuring schema validation succeeds."
    )
    initial_state_desc = "pr/frontend-pagination and pr/data-analytics ready with conflicting JSON changes."
    expected_outcome = "Both PRs merged into main. contracts/api-schema.json is valid JSON with all fields."
    hints = [
        "Merge the first PR: `git merge pr/frontend-pagination`.",
        "Merge the second PR: `git merge pr/data-analytics`.",
        "In contracts/api-schema.json, manually resolve the conflict ensuring JSON brackets and commas are valid.",
    ]
    solution_guide = (
        "1. `git merge pr/frontend-pagination`\n"
        "2. `git merge pr/data-analytics`\n"
        "3. Open contracts/api-schema.json, format as valid JSON containing both pagination and analytics fields.\n"
        "4. `git add contracts/api-schema.json && git commit`"
    )
    interview_questions = [
        InterviewQuestion(
            question="Why are structured formats like JSON, XML, and YAML notorious for Git merge conflicts?",
            key_points=[
                "Line-based diff algorithms (like Myers diff) lack syntax-tree awareness.",
                "Trailing commas and closing brackets often result in syntax errors during naive conflict resolution.",
                "Semantic diff and merge tools (AST-based merge) are required for automated lossless merging.",
            ],
            in_depth_explanation="A line-based merge might place commas incorrectly or duplicate curly braces, creating syntactically invalid documents even if conflict markers are removed."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        
        contracts_dir = git.repo_path / "contracts"
        contracts_dir.mkdir(parents=True, exist_ok=True)
        schema_file = contracts_dir / "api-schema.json"
        
        base_schema = {
            "version": "1.0",
            "definitions": {
                "OrderResponse": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "integer"},
                        "status": {"type": "string"},
                        "total_amount": {"type": "number"}
                    }
                }
            }
        }
        schema_file.write_text(json.dumps(base_schema, indent=2))
        git.add(".")
        git.commit("Base setup with API contract", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # PR 1: Frontend pagination
        git.checkout("pr/frontend-pagination", create=True)
        schema_1 = dict(base_schema)
        props1 = schema_1["definitions"]["OrderResponse"]["properties"]
        props1["page"] = {"type": "integer"}
        props1["page_size"] = {"type": "integer"}
        props1["total_pages"] = {"type": "integer"}
        schema_file.write_text(json.dumps(schema_1, indent=2))
        git.add(".")
        git.commit("feat(api): add pagination fields to OrderResponse schema", author_name="Kenji Takahashi", author_email="kenji.takahashi@nexus.internal")

        # PR 2: Data analytics
        git.checkout("main")
        git.checkout("pr/data-analytics", create=True)
        schema_2 = dict(base_schema)
        props2 = schema_2["definitions"]["OrderResponse"]["properties"]
        props2["analytics_trace_id"] = {"type": "string"}
        props2["timestamp_epoch_ms"] = {"type": "integer"}
        schema_file.write_text(json.dumps(schema_2, indent=2))
        git.add(".")
        git.commit("feat(analytics): add telemetry tracing fields to OrderResponse schema", author_name="Fatima Al-Mansoor", author_email="fatima.al-mansoor@nexus.internal")

        git.checkout("main")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        cur = git.current_branch()
        if cur != "main":
            return False, f"Current branch is '{cur}', expected 'main'."

        schema_file = git.repo_path / "contracts" / "api-schema.json"
        if not schema_file.exists():
            return False, "contracts/api-schema.json not found."

        try:
            data = json.loads(schema_file.read_text())
        except Exception as e:
            return False, f"contracts/api-schema.json is not valid JSON: {e}"

        props = data.get("definitions", {}).get("OrderResponse", {}).get("properties", {})
        required_fields = ["page", "page_size", "total_pages", "analytics_trace_id", "timestamp_epoch_ms"]
        missing = [f for f in required_fields if f not in props]
        if missing:
            return False, f"Missing contract fields in schema: {missing}"

        return True, "Successfully merged concurrent API contract PRs with valid JSON schema!"


# -----------------------------------------------------------------------------
# LEVEL 18: Conflicting Database Migrations
# -----------------------------------------------------------------------------
@register_challenge
class Level18ConflictingDatabaseMigrations(BaseChallenge):
    level_id = "level_18"
    number = 18
    category = ChallengeCategory.C_DISTRIBUTED
    title = "Conflicting Database Migrations (Alembic DAG Repair)"
    difficulty = "Hardcore"
    estimated_time = "35 minutes"
    description = (
        "Classic production headache: Two teams generated new database migrations in parallel:\n"
        "- Team A generated migration '004a_add_customer_loyalty.py' with down_revision = '003_add_order_notes'.\n"
        "- Team B generated migration '004b_add_warehouse_telemetry.py' ALSO with down_revision = '003_add_order_notes'.\n\n"
        "Both branches were merged, creating a multiple head branches conflict in the migration tree!\n"
        "Running migrations now fails with `Multiple head revisions are present in migration history`.\n\n"
        "Your task: Linearize or merge the migration revisions into a clean single head DAG, "
        "such that running the migration runner succeeds with zero errors and both migrations are applied."
    )
    initial_state_desc = "Two conflicting migrations with duplicate down_revisions."
    expected_outcome = "Migrations linear/merged. Migration runner executes cleanly."
    hints = [
        "Inspect `nexus_platform/app/migrations/`.",
        "Either update down_revision in one file to point to the other, or create a merge migration.",
    ]
    solution_guide = (
        "1. Open `004b_add_warehouse_telemetry.py`.\n"
        "2. Change its down_revision from '003_add_order_notes' to '004a_add_customer_loyalty'.\n"
        "3. Commit the change on main.\n"
        "4. Verify in `./dojo`."
    )
    interview_questions = [
        InterviewQuestion(
            question="Why does Alembic / Django detect multiple head revisions and refuse to run?",
            key_points=[
                "Database migrations form a Directed Acyclic Graph (DAG).",
                "If two branches create migrations from the same base revision, the DAG bifurcates into two heads.",
                "The engine refuses to guess execution order because database DDL dependencies must be deterministic.",
            ],
            in_depth_explanation="Alembic provides `alembic merge heads -m 'merge heads'` or developers can manually re-link `down_revision` to serialize the changes."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        mig_dir = git.repo_path / "nexus_platform" / "app" / "migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)

        # Migration 4a
        (mig_dir / "004a_add_customer_loyalty.py").write_text(
            'revision = "004a"\ndown_revision = "003"\n\ndef upgrade(db):\n    db.execute("ALTER TABLE users ADD COLUMN loyalty_points INT DEFAULT 0;")\n'
        )
        git.add(".")
        git.commit("feat(db): add customer loyalty migration", author_name="Aria Vance", author_email="aria.vance@nexus.internal")

        # Migration 4b (Conflicting down_revision!)
        (mig_dir / "004b_add_warehouse_telemetry.py").write_text(
            'revision = "004b"\ndown_revision = "003"\n\ndef upgrade(db):\n    db.execute("ALTER TABLE warehouses ADD COLUMN telemetry_ip TEXT DEFAULT \'\';")\n'
        )
        git.add(".")
        git.commit("feat(db): add warehouse telemetry migration", author_name="Marcus Sterling", author_email="marcus.sterling@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        mig_dir = git.repo_path / "nexus_platform" / "app" / "migrations"
        f_a = mig_dir / "004a_add_customer_loyalty.py"
        f_b = mig_dir / "004b_add_warehouse_telemetry.py"

        if not f_a.exists() or not f_b.exists():
            return False, "Migration files missing."

        text_a = f_a.read_text()
        text_b = f_b.read_text()

        down_a = [l for l in text_a.splitlines() if "down_revision" in l]
        down_b = [l for l in text_b.splitlines() if "down_revision" in l]

        if down_a == down_b:
            return False, f"Both migrations still point to duplicate down_revisions: {down_a}"

        return True, "Successfully repaired database migration DAG hierarchy!"


# -----------------------------------------------------------------------------
# LEVEL 19: Breaking Change Merged into Main
# -----------------------------------------------------------------------------
@register_challenge
class Level19BreakingChangeMerged(BaseChallenge):
    level_id = "level_19"
    number = 19
    category = ChallengeCategory.C_DISTRIBUTED
    title = "Mitigating Breaking Change Merged into Mainline"
    difficulty = "Hard"
    estimated_time = "25 minutes"
    description = (
        "An over-enthusiastic developer merged PR #88 ('refactor(api): change user response format') into 'main'.\n"
        "The change renamed the standard field `username` to `user_handle` across all response schemas, "
        "causing immediate failures in downstream order processing and customer-facing mobile apps.\n"
        "Two other critical bug fixes were pushed to main after this commit!\n\n"
        "Your task: Fix the regression on 'main' by introducing backward-compatibility (supporting BOTH "
        "`username` and `user_handle`) or reverting the breaking commit, ensuring downstream tests pass "
        "and subsequent commits remain intact."
    )
    initial_state_desc = "Breaking change merged into main followed by 2 other commits."
    expected_outcome = "API supports username. Downstream tests pass. History intact."
    hints = [
        "Run `python3 -m unittest discover -s nexus_platform/tests` to see the test failure.",
        "Either update the schema to alias `username` and `user_handle`, or `git revert <breaking_commit_sha>`.",
    ]
    solution_guide = (
        "1. Identify the breaking commit hash.\n"
        "2. Either run `git revert <breaking_commit>` or patch user service to return both username and user_handle.\n"
        "3. Commit and run tests."
    )
    interview_questions = [
        InterviewQuestion(
            question="What is the Expand and Contract pattern in API and database evolution?",
            key_points=[
                "Expand: Add the new field/capability alongside the old one without removing the old one.",
                "Migrate: Update clients/callers to consume the new field over time.",
                "Contract: Safely deprecate and remove the old field in a subsequent major release.",
            ],
            in_depth_explanation="Expand and contract eliminates breaking changes in distributed microservices, allowing independent deployment of services without simultaneous lockstep rollouts."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # 1. Breaking commit
        user_srv = git.repo_path / "nexus_platform" / "app" / "services" / "users.py"
        content = user_srv.read_text().replace('"username": username', '"user_handle": username')
        user_srv.write_text(content)
        git.add(".")
        git.commit("refactor(api): change user response format to user_handle", author_name="Lucas Sinclair", author_email="lucas.sinclair@nexus.internal")

        # 2. Subsequent commit 1
        (git.repo_path / "doc_patch.txt").write_text("doc update\n")
        git.add(".")
        git.commit("docs: update release notes", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # 3. Subsequent commit 2
        (git.repo_path / "nexus_platform" / "app" / "config.py").write_text(
            (git.repo_path / "nexus_platform" / "app" / "config.py").read_text() + "\n# Cache TTL = 300\n"
        )
        git.add(".")
        git.commit("chore(config): add cache TTL constant", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        # Run test suite
        tests_ok, test_out = self.run_platform_tests(repo_path)
        if not tests_ok:
            return False, f"Unit test suite still failing: {test_out}"
        
        # Verify subsequent commits are still present
        log = git.log("-n", "5", "--oneline")
        if "add cache TTL constant" not in log:
            return False, "Subsequent commits were lost!"

        return True, "Successfully mitigated breaking change and restored test suite integrity!"


# -----------------------------------------------------------------------------
# LEVEL 20: Stale PR After Major Architectural Changes
# -----------------------------------------------------------------------------
@register_challenge
class Level20StalePRRefactor(BaseChallenge):
    level_id = "level_20"
    number = 20
    category = ChallengeCategory.C_DISTRIBUTED
    title = "Rescue Stale PR After Monolith-to-Modular Architecture"
    difficulty = "Hardcore"
    estimated_time = "35 minutes"
    description = (
        "Branch 'feature/bulk-upload' has been waiting for review for 3 months.\n"
        "Meanwhile, the Architecture team moved all monolithic helper files into domain-specific packages "
        "under `nexus_platform/app/services/`.\n"
        "Attempting a direct merge causes dozens of conflicts and missing target files.\n\n"
        "Your task: Rebase or transplant 'feature/bulk-upload' onto the latest 'main' so that the bulk upload "
        "feature is located in `nexus_platform/app/services/bulk_upload.py`, integrates with the new "
        "modular services, and can be cleanly merged without conflicts."
    )
    initial_state_desc = "Stale feature branch based on old pre-modular file layout."
    expected_outcome = "feature/bulk-upload rebased cleanly onto main, using current modular directory structure."
    hints = [
        "Checkout `feature/bulk-upload`.",
        "Rebase onto main: `git rebase main`.",
        "Move the file to `nexus_platform/app/services/bulk_upload.py` and finish rebase.",
    ]
    solution_guide = (
        "1. `git checkout feature/bulk-upload`\n"
        "2. `git rebase main`\n"
        "3. Ensure the bulk upload code is placed in `nexus_platform/app/services/bulk_upload.py`.\n"
        "4. `git add . && git rebase --continue`."
    )
    interview_questions = [
        InterviewQuestion(
            question="How do you handle branches when repository files have undergone massive directory reorganizations?",
            key_points=[
                "`git rebase -X find-renames=<n>` helps Git track moved files during rebase.",
                "Perform architectural file restructuring in dedicated, isolated PRs with no logic changes.",
                "Encourage short-lived branches to minimize merge debt.",
            ],
            in_depth_explanation="When file moves are combined with large code changes in the same commit, Git's rename detection threshold may fail to recognize the file, triggering delete/create conflicts."
        )
    ]

    def setup(self, repo_path: Optional[Path] = None) -> None:
        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Base platform setup", author_name="Elena Kowalski", author_email="elena.kowalski@nexus.internal")

        # Stale feature branch created before directory restructuring
        git.checkout("feature/bulk-upload", create=True)
        old_file = git.repo_path / "nexus_platform" / "app" / "bulk_upload_old.py"
        old_file.write_text("def process_bulk_csv(content: str): return len(content.splitlines())\n")
        git.add(".")
        git.commit("feat(upload): add bulk csv parsing", author_name="Zoe Chen", author_email="zoe.chen@nexus.internal")

        # Now architectural restructuring on main
        git.checkout("main")
        for i in range(1, 4):
            (git.repo_path / "nexus_platform" / "app" / "services" / f"domain_service_{i}.py").write_text(f"# Service {i}\n")
            git.add(".")
            git.commit(f"refactor(arch): migrate domain subsystem {i}", author_name="Dante Castillo", author_email="dante.castillo@nexus.internal")

    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        git = self.get_git(repo_path)
        git.checkout("feature/bulk-upload")
        target_file = git.repo_path / "nexus_platform" / "app" / "services" / "bulk_upload.py"
        old_file = git.repo_path / "nexus_platform" / "app" / "bulk_upload_old.py"

        if old_file.exists():
            return False, "Old pre-refactor file bulk_upload_old.py still exists!"
        if not target_file.exists():
            return False, "Target file nexus_platform/app/services/bulk_upload.py does not exist!"

        content = target_file.read_text()
        if "process_bulk_csv" not in content:
            return False, "Function process_bulk_csv missing in target file."

        # Check commit history is rebased onto main
        main_tip = git.rev_parse("main")
        if not git.run("merge-base", "--is-ancestor", main_tip, "feature/bulk-upload").success:
            return False, "feature/bulk-upload is not rebased directly on top of main."

        return True, "Successfully rebased and refactored stale PR to match modern architecture!"

