"""Broken Repository Museum: Famous repository disaster exhibits."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..core.git_client import GitClient
from ..core.repo_manager import repo_manager


@dataclass
class MuseumExhibit:
    id: str
    name: str
    historical_context: str
    incident_severity: str
    educational_lesson: str


EXHIBITS: List[MuseumExhibit] = [
    MuseumExhibit(
        id="exhibit_01",
        name="The Detached Ghost",
        historical_context="A late-night hotfix was committed in detached HEAD state, then abandoned when switching back to main.",
        incident_severity="MEDIUM",
        educational_lesson="Understanding reflog mechanics and how Git retains unreachable objects before prune.",
    ),
    MuseumExhibit(
        id="exhibit_02",
        name="The Merge Octo-Monster",
        historical_context="4 developer teams merged their branches in an unverified multi-parent merge with broken dependencies.",
        incident_severity="HIGH",
        educational_lesson="Why linear histories or serialized merge queues prevent multi-parent merge paralysis.",
    ),
    MuseumExhibit(
        id="exhibit_03",
        name="The Leaked Production Secret",
        historical_context="Developer pushed production database credentials in config.json, then pushed 'rm config.json' thinking it was gone.",
        incident_severity="CRITICAL",
        educational_lesson="Git history is immutable until rewritten with filter-repo; secrets must always be immediately rotated at the provider.",
    ),
    MuseumExhibit(
        id="exhibit_04",
        name="The Stale Rebase Graveyard",
        historical_context="A 6-month-old feature branch was blindly rebased onto main, discarding upstream hotfixes.",
        incident_severity="HIGH",
        educational_lesson="Short-lived branch practices, rebase strategies, and conflict triage.",
    ),
    MuseumExhibit(
        id="exhibit_05",
        name="The Phantom Release Tag",
        historical_context="CI deployment triggered automatically from a tag accidentally placed on an unreviewed PR commit.",
        incident_severity="HIGH",
        educational_lesson="Tag verification policies, annotated tags, and deployment protection rules.",
    ),
]


class MuseumManager:
    """Installs museum exhibits into the playground for interactive forensic exploration."""

    @staticmethod
    def load_exhibit(exhibit_id: str) -> MuseumExhibit:
        exhibit = next((e for e in EXHIBITS if e.id == exhibit_id), None)
        if not exhibit:
            raise ValueError(f"Exhibit '{exhibit_id}' not found.")

        git = repo_manager.init_clean_repo()
        repo_manager.copy_template()
        git.add(".")
        git.commit("Museum Base Platform", author_name="Curator Bot", author_email="curator@nexus.internal")

        if exhibit_id == "exhibit_01":
            # Detached Ghost
            git.checkout("HEAD~0")
            (git.repo_path / "ghost.txt").write_text("Lost ghost commit\n")
            git.add(".")
            git.commit("feat(ghost): ghost in detached head", author_name="Unknown Engineer", author_email="ghost@nexus.internal")
            git.checkout("main")

        elif exhibit_id == "exhibit_02":
            # Multi-branch collision
            for i in range(1, 4):
                git.checkout("main")
                git.checkout(f"monster-branch-{i}", create=True)
                (git.repo_path / f"monster_{i}.py").write_text(f"# Monster {i}\n")
                git.add(".")
                git.commit(f"monster commit {i}", author_name="Dev Monster", author_email="dev@nexus.internal")
            git.checkout("main")

        elif exhibit_id == "exhibit_03":
            # Leaked Secret
            p = git.repo_path / "config_secret.env"
            p.write_text("AWS_SECRET_ACCESS_KEY=AKIA_MUSEUM_EXHIBIT_SECRET_999\n")
            git.add(".")
            git.commit("chore(config): commit secret file", author_name="Accidental Leaker", author_email="leaker@nexus.internal")
            git.run("rm", "config_secret.env")
            git.commit("chore(config): remove secret file oops", author_name="Panicked Leaker", author_email="leaker@nexus.internal")

        elif exhibit_id == "exhibit_04":
            # Stale branch
            git.checkout("stale-graveyard-feature", create=True)
            (git.repo_path / "ancient.txt").write_text("ancient feature\n")
            git.add(".")
            git.commit("feat(ancient): ancient commit", author_name="Former Engineer", author_email="legacy@nexus.internal")
            git.checkout("main")
            for i in range(15):
                (git.repo_path / f"main_advance_{i}.txt").write_text(f"Advance {i}\n")
                git.add(".")
                git.commit(f"chore: advance main {i}", author_name="Main Maintainer", author_email="maint@nexus.internal")

        elif exhibit_id == "exhibit_05":
            # Phantom tag
            (git.repo_path / "broken_release.txt").write_text("corrupted code\n")
            git.add(".")
            git.commit("wip: broken unstable code", author_name="Junior Dev", author_email="junior@nexus.internal")
            git.tag("v9.9.9-PHANTOM", message="Accidental Tag")

        return exhibit

