"""Configuration and constants for Git Dojo."""

from dataclasses import dataclass
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DOJO_HOME = PROJECT_ROOT / ".git_dojo"
PLAYGROUND_ROOT = DOJO_HOME / "playground"
PLAYGROUND_REPO = PLAYGROUND_ROOT / "nexus-platform"
STATE_FILE = DOJO_HOME / "state.json"
NEXUS_TEMPLATE_DIR = PROJECT_ROOT / "nexus_platform"
DOCS_DIR = PROJECT_ROOT / "docs"
SOLUTIONS_DIR = DOCS_DIR / "SOLUTIONS"

# Deterministic random seed for reproducibility
DETERMINISTIC_SEED = 1337


@dataclass(frozen=True)
class DojoConfig:
    project_root: Path = PROJECT_ROOT
    dojo_home: Path = DOJO_HOME
    playground_root: Path = PLAYGROUND_ROOT
    playground_repo: Path = PLAYGROUND_REPO
    state_file: Path = STATE_FILE
    nexus_template: Path = NEXUS_TEMPLATE_DIR
    seed: int = DETERMINISTIC_SEED

    def ensure_directories(self) -> None:
        """Ensure necessary runtime directories exist."""
        self.dojo_home.mkdir(parents=True, exist_ok=True)
        self.playground_root.mkdir(parents=True, exist_ok=True)


config = DojoConfig()
