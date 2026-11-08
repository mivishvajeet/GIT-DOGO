"""Base Challenge class and challenge registry for Git Dojo."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from ..core.git_client import GitClient
from ..core.repo_manager import repo_manager


class ChallengeCategory(str, Enum):
    A_INTERNALS = "Category A — Git Internals"
    B_BRANCHING = "Category B — Branching & History Surgery"
    C_DISTRIBUTED = "Category C — Distributed Team Simulation"
    D_RELEASE = "Category D — Release Engineering"
    E_INCIDENTS = "Category E — Production-Grade Git Incidents"


@dataclass
class InterviewQuestion:
    question: str
    key_points: List[str]
    in_depth_explanation: str


class BaseChallenge(ABC):
    """Abstract Base Class for all 30 Git Dojo levels."""

    level_id: str
    number: int
    category: ChallengeCategory
    title: str
    difficulty: str
    estimated_time: str
    description: str
    initial_state_desc: str
    expected_outcome: str
    hints: List[str] = field(default_factory=list)
    interview_questions: List[InterviewQuestion] = field(default_factory=list)
    solution_guide: str = ""

    def get_git(self, repo_path: Optional[Path] = None) -> GitClient:
        return GitClient(repo_path or repo_manager.repo_path)

    @abstractmethod
    def setup(self, repo_path: Optional[Path] = None) -> None:
        """Create the exact initial scenario state in the playground repository."""
        pass

    @abstractmethod
    def verify(self, repo_path: Optional[Path] = None) -> Tuple[bool, str]:
        """Verify if the user has successfully solved the challenge."""
        pass

    def reset(self, repo_path: Optional[Path] = None) -> None:
        """Reset the challenge by cleaning and re-running setup."""
        self.setup(repo_path)


# Global registry of challenges
CHALLENGES: Dict[str, BaseChallenge] = {}


def register_challenge(challenge_target: Any) -> Any:
    if isinstance(challenge_target, type) and issubclass(challenge_target, BaseChallenge):
        instance = challenge_target()
        CHALLENGES[instance.level_id] = instance
        return challenge_target
    elif isinstance(challenge_target, BaseChallenge):
        CHALLENGES[challenge_target.level_id] = challenge_target
        return challenge_target
    return challenge_target


def get_challenge(level_id: str) -> Optional[BaseChallenge]:
    return CHALLENGES.get(level_id)


def get_all_challenges() -> List[BaseChallenge]:
    return sorted(list(CHALLENGES.values()), key=lambda c: c.number)
