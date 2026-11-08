"""Simulation engine for realistic Nexus Engineering git activity."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import random

from .developers import Developer, DEVELOPERS, CommitBehavior
from .teams import TEAMS_BY_ID
from ..core.git_client import GitClient


@dataclass
class SimulatedPullRequest:
    id: int
    title: str
    branch_name: str
    author: Developer
    base_branch: str
    description: str
    files_changed: List[str]
    has_conflicts: bool = False
    is_stale: bool = False


class EngineeringSimulator:
    """Simulates realistic team branches, PRs, and commit patterns."""

    def __init__(self, git_client: GitClient, seed: int = 1337):
        self.git = git_client
        self.rng = random.Random(seed)

    def commit_as_developer(
        self,
        developer: Developer,
        message: str,
        files_to_modify: Optional[List[str]] = None,
        date: Optional[str] = None,
    ) -> None:
        """Create a commit authored by a specific fictional developer."""
        if files_to_modify:
            for rel_path in files_to_modify:
                full_path = self.git.repo_path / rel_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, "a", encoding="utf-8") as f:
                    f.write(f"\n# Change authored by {developer.name} ({developer.team_id})\n")
                self.git.add(rel_path)

        self.git.commit(
            message=message,
            author_name=developer.name,
            author_email=developer.email,
            date=date or "2026-03-10T12:00:00Z",
            allow_empty=not bool(files_to_modify),
        )

    def create_feature_branch(
        self,
        developer: Developer,
        branch_name: str,
        base_branch: str = "main",
    ) -> None:
        """Create and switch to a feature branch authored by developer."""
        self.git.checkout(base_branch)
        self.git.checkout(branch_name, create=True)

    def generate_team_activity(self, count: int = 10) -> List[SimulatedPullRequest]:
        """Generate simulated PR metadata for display."""
        prs = []
        for i in range(1, count + 1):
            dev = self.rng.choice(DEVELOPERS)
            team = TEAMS_BY_ID[dev.team_id]
            branch = f"feature/{dev.team_id}/{dev.name.lower().replace(' ', '-')}-patch-{i}"
            title = f"feat({dev.team_id}): optimize {team.name} component #{i}"
            desc = f"Authored by {dev.name} ({dev.role})\nResolves NEXUS-{1000 + i}"
            prs.append(
                SimulatedPullRequest(
                    id=i,
                    title=title,
                    branch_name=branch,
                    author=dev,
                    base_branch="main",
                    description=desc,
                    files_changed=dev.ownership[:2],
                    has_conflicts=(i % 3 == 0),
                    is_stale=(i % 4 == 0),
                )
            )
        return prs
