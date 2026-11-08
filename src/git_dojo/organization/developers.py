"""100 Fictional Developer Identities for NEXUS ENGINEERING."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import random

from .teams import TEAMS, Team
from ..core.config import DETERMINISTIC_SEED


class CommitBehavior(str, Enum):
    CLEAN_ATOMIC = "clean_atomic"
    HUGE_MONOLITHIC = "huge_monolithic"
    FORGETS_PULL = "forgets_pull"
    FORCE_PUSH_PRONE = "force_push_prone"
    INTRODUCES_BUGS = "introduces_bugs"
    MODIFIES_SHARED = "modifies_shared"
    BLIND_MERGER = "blind_merger"
    BREAKING_API = "breaking_api"
    UNVETTED_DEPS = "unvetted_deps"


ROLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Staff Software Engineer",
    "Principal Engineer",
    "Tech Lead",
    "Engineering Manager",
    "Associate Software Engineer",
]

# Deterministic fictional names
FIRST_NAMES = [
    "Aria", "Liam", "Maya", "Elena", "Marcus", "Siddharth", "Zoe", "Kenji", "Fatima", "Mateo",
    "Chloe", "Devon", "Aaliyah", "Vikram", "Hanna", "Lucas", "Mei-Ling", "Tariq", "Svetlana", "Gabriel",
    "Kavita", "Rohan", "Ingrid", "Dante", "Nadia", "Carlos", "Yuki", "Samira", "Leila", "Chen",
    "Ananya", "Julian", "Amara", "Nikolai", "Soraya", "Felix", "Beatriz", "Haruki", "Camila", "Darius",
    "Priya", "Xavier", "Thalia", "Arjun", "Kira", "Ethan", "Zainab", "Leon", "Mira", "Rafael"
]

LAST_NAMES = [
    "Vance", "Kowalski", "Chen", "Sterling", "Patel", "Lindqvist", "O'Connor", "Takahashi", "Al-Mansoor", "Silva",
    "Novak", "Mercer", "Adeyemi", "Kapoor", "Mendoza", "Sinclair", "Zhang", "Dubois", "Petrov", "Santoro",
    "Sharma", "Hawthorne", "Bergstrom", "Castillo", "Fischer", "Kim", "Nakamura", "Morales", "Schneider", "Volkov",
    "Iyer", "Fontana", "Okafor", "Ivanov", "Hakimi", "Reyes", "Gomez", "Kozlov", "Hassan", "Moreau"
]


@dataclass(frozen=True)
class Developer:
    id: str
    name: str
    email: str
    team_id: str
    role: str
    behavior: CommitBehavior
    ownership: List[str]

    @property
    def git_author(self) -> str:
        return f"{self.name} <{self.email}>"


def _generate_100_developers(seed: int = DETERMINISTIC_SEED) -> List[Developer]:
    rng = random.Random(seed)
    developers: List[Developer] = []

    # Distribution of behaviors
    behaviors = [
        CommitBehavior.CLEAN_ATOMIC,
        CommitBehavior.CLEAN_ATOMIC,
        CommitBehavior.CLEAN_ATOMIC,
        CommitBehavior.HUGE_MONOLITHIC,
        CommitBehavior.FORGETS_PULL,
        CommitBehavior.FORCE_PUSH_PRONE,
        CommitBehavior.INTRODUCES_BUGS,
        CommitBehavior.MODIFIES_SHARED,
        CommitBehavior.BLIND_MERGER,
        CommitBehavior.BREAKING_API,
        CommitBehavior.UNVETTED_DEPS,
    ]

    used_names = set()
    dev_index = 1

    for team in TEAMS:
        # Distribute 6 to 8 devs per team to total 100
        team_size = 7 if team.id in ["backend", "platform", "api", "database", "devops", "security", "qa", "data", "release", "frontend"] else 6
        if len(developers) + team_size > 100:
            team_size = 100 - len(developers)

        for _ in range(team_size):
            while True:
                first = rng.choice(FIRST_NAMES)
                last = rng.choice(LAST_NAMES)
                full_name = f"{first} {last}"
                if full_name not in used_names:
                    used_names.add(full_name)
                    break

            clean_last = last.lower().replace("'", "")
            username = f"{first.lower()}.{clean_last}"
            email = f"{username}@nexus.internal"
            role = rng.choice(ROLES)
            behavior = rng.choice(behaviors)

            # Assign specific ownership based on team
            ownership = list(team.primary_ownership)
            dev_id = f"dev_{dev_index:03d}"
            developers.append(
                Developer(
                    id=dev_id,
                    name=full_name,
                    email=email,
                    team_id=team.id,
                    role=role,
                    behavior=behavior,
                    ownership=ownership,
                )
            )
            dev_index += 1

    # Fill remainder up to exactly 100 if any
    while len(developers) < 100:
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        if full_name in used_names:
            full_name = f"{first} {last} Jr."
        used_names.add(full_name)

        team = rng.choice(TEAMS)
        clean_last = last.lower().replace("'", "")
        username = f"dev{len(developers)+1}.{clean_last}"
        email = f"{username}@nexus.internal"
        developers.append(
            Developer(
                id=f"dev_{len(developers)+1:03d}",
                name=full_name,
                email=email,
                team_id=team.id,
                role=rng.choice(ROLES),
                behavior=rng.choice(behaviors),
                ownership=list(team.primary_ownership),
            )
        )

    return developers


DEVELOPERS: List[Developer] = _generate_100_developers()
DEVELOPERS_BY_ID: Dict[str, Developer] = {d.id: d for d in DEVELOPERS}
DEVELOPERS_BY_EMAIL: Dict[str, Developer] = {d.email: d for d in DEVELOPERS}


def get_developers_by_team(team_id: str) -> List[Developer]:
    return [d for d in DEVELOPERS if d.team_id == team_id]


def get_developer_by_behavior(behavior: CommitBehavior) -> List[Developer]:
    return [d for d in DEVELOPERS if d.behavior == behavior]
