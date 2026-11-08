"""Challenges package: registers all 30 levels across Categories A to E."""

from .base import (
    BaseChallenge,
    ChallengeCategory,
    InterviewQuestion,
    CHALLENGES,
    register_challenge,
    get_challenge,
    get_all_challenges,
)

# Import categories to trigger registration
from .category_a_internals import levels_01_05
from .category_b_branching import levels_06_10, levels_11_15
from .category_c_distributed import levels_16_20
from .category_d_release import levels_21_25
from .category_e_incidents import levels_26_30

__all__ = [
    "BaseChallenge",
    "ChallengeCategory",
    "InterviewQuestion",
    "CHALLENGES",
    "register_challenge",
    "get_challenge",
    "get_all_challenges",
]
