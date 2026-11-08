"""Git client: robust, safe subprocess wrapper for Git operations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import os
import subprocess


class GitError(Exception):
    """Raised when a Git command fails."""
    def __init__(self, message: str, returncode: int, stdout: str, stderr: str, cmd: List[str]):
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.cmd = cmd


@dataclass
class GitResult:
    returncode: int
    stdout: str
    stderr: str
    cmd: List[str]

    @property
    def success(self) -> bool:
        return self.returncode == 0


class GitClient:
    """Subprocess interface to Git, locked strictly to a target repository."""

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()

    def run(
        self,
        *args: str,
        env_vars: Optional[Dict[str, str]] = None,
        check: bool = False,
        cwd: Optional[Union[str, Path]] = None,
    ) -> GitResult:
        """Run a git command in the repository."""
        work_dir = Path(cwd).resolve() if cwd else self.repo_path
        cmd = ["git"] + list(args)

        # Build clean environment
        env = os.environ.copy()
        # Ensure deterministic timestamps if configured
        if env_vars:
            env.update(env_vars)

        proc = subprocess.run(
            cmd,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            env=env,
        )

        result = GitResult(
            returncode=proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            cmd=cmd,
        )

        if check and not result.success:
            raise GitError(
                f"Command failed: {' '.join(cmd)}\nStderr: {result.stderr}\nStdout: {result.stdout}",
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                cmd=cmd,
            )

        return result

    def init(self, default_branch: str = "main") -> GitResult:
        self.repo_path.mkdir(parents=True, exist_ok=True)
        return self.run("init", "-b", default_branch)

    def config(self, key: str, value: str) -> GitResult:
        return self.run("config", key, value)

    def status(self, porcelain: bool = True) -> str:
        cmd = ["status", "--porcelain"] if porcelain else ["status"]
        return self.run(*cmd).stdout

    def add(self, *paths: str) -> GitResult:
        return self.run("add", *paths)

    def commit(
        self,
        message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        date: Optional[str] = None,
        allow_empty: bool = False,
    ) -> GitResult:
        env = {}
        if author_name:
            env["GIT_AUTHOR_NAME"] = author_name
            env["GIT_COMMITTER_NAME"] = author_name
        if author_email:
            env["GIT_AUTHOR_EMAIL"] = author_email
            env["GIT_COMMITTER_EMAIL"] = author_email
        if date:
            env["GIT_AUTHOR_DATE"] = date
            env["GIT_COMMITTER_DATE"] = date

        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")

        return self.run(*args, env_vars=env)

    def branch(self, name: str, start_point: Optional[str] = None) -> GitResult:
        args = ["branch", name]
        if start_point:
            args.append(start_point)
        return self.run(*args)

    def list_branches(self, all_branches: bool = False) -> List[str]:
        args = ["branch"]
        if all_branches:
            args.append("-a")
        res = self.run(*args)
        if not res.stdout:
            return []
        branches = []
        for line in res.stdout.splitlines():
            line = line.strip().lstrip("* ")
            if "->" in line:  # Skip HEAD symref
                continue
            branches.append(line)
        return branches

    def checkout(self, branch_or_commit: str, create: bool = False) -> GitResult:
        args = ["checkout", "-b", branch_or_commit] if create else ["checkout", branch_or_commit]
        return self.run(*args)

    def switch(self, branch: str, create: bool = False) -> GitResult:
        args = ["switch", "-c", branch] if create else ["switch", branch]
        return self.run(*args)

    def current_branch(self) -> Optional[str]:
        res = self.run("branch", "--show-current")
        branch = res.stdout.strip()
        return branch if branch else None

    def rev_parse(self, ref: str = "HEAD") -> str:
        res = self.run("rev-parse", ref, check=True)
        return res.stdout.strip()

    def merge(self, branch: str, message: Optional[str] = None, no_ff: bool = False) -> GitResult:
        args = ["merge", branch]
        if message:
            args.extend(["-m", message])
        if no_ff:
            args.append("--no-ff")
        return self.run(*args)

    def tag(self, name: str, message: Optional[str] = None, ref: Optional[str] = None) -> GitResult:
        args = ["tag"]
        if message:
            args.extend(["-a", name, "-m", message])
        else:
            args.append(name)
        if ref:
            args.append(ref)
        return self.run(*args)

    def list_tags(self) -> List[str]:
        res = self.run("tag", "-l")
        return [t.strip() for t in res.stdout.splitlines() if t.strip()]

    def log(self, *args: str) -> str:
        cmd = ["log"] + list(args)
        return self.run(*cmd).stdout

    def reflog(self, max_count: int = 50) -> List[str]:
        res = self.run("reflog", f"-n{max_count}")
        return res.stdout.splitlines() if res.stdout else []

    def cat_file(self, flag: str, obj: str) -> GitResult:
        return self.run("cat-file", flag, obj)

    def reset_hard(self, ref: str = "HEAD") -> GitResult:
        return self.run("reset", "--hard", ref)

    def clean_force(self) -> GitResult:
        return self.run("clean", "-fdx")

    def worktree_add(self, path: Union[str, Path], branch: str) -> GitResult:
        return self.run("worktree", "add", str(path), branch)

    def worktree_remove(self, path: Union[str, Path]) -> GitResult:
        return self.run("worktree", "remove", "--force", str(path))

    def worktree_prune(self) -> GitResult:
        return self.run("worktree", "prune")

    def is_git_repo(self) -> bool:
        git_dir = self.repo_path / ".git"
        return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())

