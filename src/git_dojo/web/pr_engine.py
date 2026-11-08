"""Pull Request & GitHub Workflow Engine for NexusHub."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import time

from ..organization.developers import DEVELOPERS, DEVELOPERS_BY_ID, Developer
from ..organization.teams import TEAMS_BY_ID
from ..core.git_client import GitClient
from ..core.repo_manager import repo_manager


@dataclass
class ReviewComment:
    id: str
    author: str
    avatar_initials: str
    role: str
    team: str
    timestamp: str
    file_path: Optional[str]
    line_number: Optional[int]
    comment: str
    is_blocking: bool = False


@dataclass
class PullRequest:
    id: int
    title: str
    branch: str
    base_branch: str
    author_id: str
    author_name: str
    author_email: str
    team_id: str
    description: str
    state: str  # "open", "merged", "closed", "draft"
    created_at: str
    files_changed: List[str]
    commits_count: int
    has_conflicts: bool = False
    conflicted_files: List[str] = field(default_factory=list)
    review_status: str = "review_required"  # "approved", "changes_requested", "review_required"
    ci_status: str = "success"  # "success", "failure", "pending"
    comments: List[ReviewComment] = field(default_factory=list)
    merge_strategy: Optional[str] = None  # "merge", "squash", "rebase"


class PullRequestManager:
    """Manages simulated GitHub PRs, code reviews, and merge conflicts."""

    def __init__(self):
        self.prs: Dict[int, PullRequest] = {}
        self._initialize_realistic_prs()

    def _initialize_realistic_prs(self) -> None:
        """Seed rich, realistic PRs spanning all 15 teams."""
        sample_prs = [
            {
                "id": 101,
                "title": "feat(inventory): add distributed redis stock allocation locking",
                "branch": "feature/inventory-redis-locks",
                "base_branch": "main",
                "author_id": "dev_002",
                "team_id": "backend",
                "description": "Implements distributed Redis locks on stock reservations to prevent double-allocation during flash sales.\n\nCloses NEXUS-1024.",
                "files_changed": ["nexus_platform/app/services/inventory.py", "nexus_platform/app/config.py"],
                "commits_count": 3,
                "has_conflicts": True,
                "conflicted_files": ["nexus_platform/app/services/inventory.py"],
                "review_status": "changes_requested",
                "ci_status": "failure",
                "comments": [
                    ReviewComment(
                        id="c1",
                        author="Elena Kowalski",
                        avatar_initials="EK",
                        role="Staff Software Engineer",
                        team="Architecture",
                        timestamp="2 hours ago",
                        file_path="nexus_platform/app/services/inventory.py",
                        line_number=45,
                        comment="Lock TTL must not exceed 5000ms. If the worker crashes, this lock will hang indefinitely.",
                        is_blocking=True,
                    ),
                    ReviewComment(
                        id="c2",
                        author="Mateo Silva",
                        avatar_initials="MS",
                        role="Senior SRE",
                        team="SRE",
                        timestamp="1 hour ago",
                        file_path=None,
                        line_number=None,
                        comment="CI failed on integration test `test_concurrency`. Please rebase on main and resolve conflicts.",
                        is_blocking=False,
                    )
                ]
            },
            {
                "id": 102,
                "title": "refactor(api): upgrade OrderResponse contract with pagination metadata",
                "branch": "feature/api-pagination-v2",
                "base_branch": "main",
                "author_id": "dev_011",
                "team_id": "api",
                "description": "Standardizes paginated REST responses across order and product listing endpoints.",
                "files_changed": ["contracts/api-schema.json", "nexus_platform/app/main.py"],
                "commits_count": 2,
                "has_conflicts": False,
                "conflicted_files": [],
                "review_status": "approved",
                "ci_status": "success",
                "comments": [
                    ReviewComment(
                        id="c3",
                        author="Kenji Takahashi",
                        avatar_initials="KT",
                        role="Tech Lead",
                        team="Frontend Engineering",
                        timestamp="3 hours ago",
                        file_path="contracts/api-schema.json",
                        line_number=18,
                        comment="Contract looks clean. Frontend dashboard is ready for these pagination fields.",
                        is_blocking=False,
                    )
                ]
            },
            {
                "id": 103,
                "title": "fix(auth): enforce constant-time HMAC signature verification",
                "branch": "security/patch-timing-attack",
                "base_branch": "main",
                "author_id": "dev_014",
                "team_id": "security",
                "description": "Mitigates potential timing side-channel attack during token validation by enforcing hmac.compare_digest.\n\nResolves SEC-991.",
                "files_changed": ["nexus_platform/app/services/auth.py"],
                "commits_count": 1,
                "has_conflicts": False,
                "conflicted_files": [],
                "review_status": "approved",
                "ci_status": "success",
                "comments": [
                    ReviewComment(
                        id="c4",
                        author="Siddharth Patel",
                        avatar_initials="SP",
                        role="Security Engineer",
                        team="Security Engineering",
                        timestamp="30 mins ago",
                        file_path=None,
                        line_number=None,
                        comment="Approved for emergency hotfix train.",
                        is_blocking=False,
                    )
                ]
            },
            {
                "id": 104,
                "title": "feat(db): add warehouse AGV telemetry schema migration",
                "branch": "feature/warehouse-telemetry-mig",
                "base_branch": "main",
                "author_id": "dev_020",
                "team_id": "database",
                "description": "Adds column `telemetry_ip` to warehouses table for AGV sensor streaming.",
                "files_changed": ["nexus_platform/app/migrations/004b_add_warehouse_telemetry.py"],
                "commits_count": 1,
                "has_conflicts": True,
                "conflicted_files": ["nexus_platform/app/migrations/runner.py"],
                "review_status": "review_required",
                "ci_status": "pending",
                "comments": [
                    ReviewComment(
                        id="c5",
                        author="Devon Mercer",
                        avatar_initials="DM",
                        role="Database Administrator",
                        team="Database Engineering",
                        timestamp="10 mins ago",
                        file_path="nexus_platform/app/migrations/004b_add_warehouse_telemetry.py",
                        line_number=2,
                        comment="Attention: PR #105 also created migration 004. You will collide on down_revision.",
                        is_blocking=True,
                    )
                ]
            }
        ]

        for p in sample_prs:
            dev = DEVELOPERS_BY_ID.get(p["author_id"], DEVELOPERS[0])
            self.prs[p["id"]] = PullRequest(
                id=p["id"],
                title=p["title"],
                branch=p["branch"],
                base_branch=p["base_branch"],
                author_id=dev.id,
                author_name=dev.name,
                author_email=dev.email,
                team_id=p["team_id"],
                description=p["description"],
                state="open",
                created_at="Today",
                files_changed=p["files_changed"],
                commits_count=p["commits_count"],
                has_conflicts=p["has_conflicts"],
                conflicted_files=p["conflicted_files"],
                review_status=p["review_status"],
                ci_status=p["ci_status"],
                comments=p["comments"],
            )

    def list_prs(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        prs = list(self.prs.values())
        if state:
            prs = [p for p in prs if p.state == state]
        return [asdict(p) for p in sorted(prs, key=lambda x: x.id, reverse=True)]

    def get_pr(self, pr_id: int) -> Optional[Dict[str, Any]]:
        pr = self.prs.get(pr_id)
        return asdict(pr) if pr else None

    def add_comment(
        self,
        pr_id: int,
        author: str,
        role: str,
        comment_text: str,
        action: Optional[str] = None,  # "comment", "approve", "request_changes"
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        pr = self.prs.get(pr_id)
        if not pr:
            return None

        cid = f"c_{len(pr.comments) + 1}_{int(time.time())}"
        initials = "".join([part[0].upper() for part in author.split()[:2]]) or "ME"

        new_comm = ReviewComment(
            id=cid,
            author=author,
            avatar_initials=initials,
            role=role,
            team="Platform Engineering",
            timestamp="Just now",
            file_path=file_path,
            line_number=line_number,
            comment=comment_text,
            is_blocking=(action == "request_changes"),
        )
        pr.comments.append(new_comm)

        if action == "approve":
            pr.review_status = "approved"
        elif action == "request_changes":
            pr.review_status = "changes_requested"

        return asdict(pr)

    def merge_pr(self, pr_id: int, strategy: str = "merge") -> Dict[str, Any]:
        """Simulate merging the PR."""
        pr = self.prs.get(pr_id)
        if not pr:
            return {"success": False, "error": f"PR #{pr_id} not found"}

        if pr.has_conflicts:
            return {
                "success": False,
                "error": f"Merge blocked: PR #{pr_id} has unresolved merge conflicts in {', '.join(pr.conflicted_files)}. Resolve conflicts via git before merging.",
                "conflicts": pr.conflicted_files,
            }

        if pr.review_status == "changes_requested":
            return {
                "success": False,
                "error": f"Merge blocked by Branch Protection: Changes requested by reviewers.",
            }

        if pr.ci_status == "failure":
            return {
                "success": False,
                "error": f"Merge blocked by Required Status Checks: CI pipeline failed.",
            }

        pr.state = "merged"
        pr.merge_strategy = strategy
        return {
            "success": True,
            "message": f"PR #{pr_id} successfully merged into '{pr.base_branch}' using {strategy} merge strategy!",
            "pr": asdict(pr),
        }


pr_manager = PullRequestManager()

