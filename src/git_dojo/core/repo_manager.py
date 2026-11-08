"""Repository Manager: handles safe, disposable sandboxes."""

import shutil
from pathlib import Path
from typing import Optional
from .config import config
from .git_client import GitClient


class RepoManager:
    """Safely manages isolated playground repositories for scenarios."""

    def __init__(self, target_path: Optional[Path] = None):
        self.repo_path = Path(target_path or config.playground_repo).resolve()
        # Security sanity check: ensure target is inside DOJO_HOME or explicitly designated
        if not str(self.repo_path).startswith(str(config.playground_root)):
            raise ValueError(
                f"Security violation: Target repo {self.repo_path} is outside playground root {config.playground_root}"
            )
        self.git = GitClient(self.repo_path)

    def exists(self) -> bool:
        return self.repo_path.exists() and self.git.is_git_repo()

    def wipe_playground(self) -> None:
        """Completely and safely wipe the playground repository."""
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)

    def init_clean_repo(self, default_branch: str = "main") -> GitClient:
        """Create a fresh empty git repository in playground."""
        self.wipe_playground()
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self.git.init(default_branch=default_branch)
        # Configure local git identity for automated actions
        self.git.config("user.name", "Nexus Platform Bot")
        self.git.config("user.email", "bot@nexus.internal")
        self.git.config("init.defaultBranch", default_branch)
        return self.git

    def copy_template(self, template_source: Optional[Path] = None) -> None:
        """Copy files from nexus_platform template into the playground repository."""
        src = template_source or config.nexus_template
        if not src.exists():
            raise FileNotFoundError(f"Template directory does not exist: {src}")

        for item in src.iterdir():
            if item.name.startswith(".git") and item.is_dir():
                continue
            dest = self.repo_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)


repo_manager = RepoManager()
