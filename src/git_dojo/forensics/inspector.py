"""Git Forensics Inspector: Read-only deep repository diagnostic analysis."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import subprocess
import os

from ..core.git_client import GitClient


@dataclass
class ForensicReport:
    repo_path: str
    is_valid_repo: bool
    current_branch: Optional[str] = None
    is_detached: bool = False
    head_commit: Optional[str] = None
    uncommitted_changes_count: int = 0
    untracked_files_count: int = 0
    has_merge_conflicts: bool = False
    conflicted_files: List[str] = field(default_factory=list)
    local_branches: List[str] = field(default_factory=list)
    stale_branches: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    recent_reflog: List[str] = field(default_factory=list)
    dangling_commits: List[str] = field(default_factory=list)
    large_files: List[Dict[str, Any]] = field(default_factory=list)
    suspicious_findings: List[str] = field(default_factory=list)
    contributor_activity: Dict[str, int] = field(default_factory=dict)
    health_score: int = 100
    health_status: str = "EXCELLENT"


class ForensicInspector:
    """Performs non-destructive deep forensics on any Git repository."""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path).resolve()
        self.git = GitClient(self.repo_path)

    def analyze(self) -> ForensicReport:
        if not self.git.is_git_repo():
            return ForensicReport(
                repo_path=str(self.repo_path),
                is_valid_repo=False,
                health_score=0,
                health_status="NOT_A_GIT_REPO",
            )

        report = ForensicReport(repo_path=str(self.repo_path), is_valid_repo=True)

        # 1. Branch & Detached HEAD Check
        cur_branch = self.git.current_branch()
        report.current_branch = cur_branch
        report.is_detached = cur_branch is None
        try:
            report.head_commit = self.git.rev_parse("HEAD")
        except Exception:
            report.head_commit = None

        # 2. Status & Working Tree
        status_lines = self.git.status(porcelain=True).splitlines()
        conflicted = []
        uncommitted = 0
        untracked = 0
        for line in status_lines:
            code = line[:2]
            filename = line[3:].strip()
            if code in ["UU", "AA", "UD", "DU", "DD", "AU", "UA"]:
                conflicted.append(filename)
            elif code.startswith("?"):
                untracked += 1
            else:
                uncommitted += 1

        report.has_merge_conflicts = len(conflicted) > 0
        report.conflicted_files = conflicted
        report.uncommitted_changes_count = uncommitted
        report.untracked_files_count = untracked

        # 3. Local Branches
        report.local_branches = self.git.list_branches()
        report.tags = self.git.list_tags()

        # 4. Reflog forensics
        report.recent_reflog = self.git.reflog(max_count=10)

        # 5. Dangling objects (non-destructive fsck)
        fsck_res = self.git.run("fsck", "--lost-found", "--unreachable")
        dangling = []
        for line in fsck_res.stdout.splitlines():
            if "dangling commit" in line or "unreachable commit" in line:
                dangling.append(line.split()[-1])
        report.dangling_commits = dangling[:10]

        # 6. Large files in working tree (> 1MB)
        large_files = []
        for root, _, files in os.walk(self.repo_path):
            if ".git" in root:
                continue
            for f in files:
                p = Path(root) / f
                try:
                    size = p.stat().st_size
                    if size > 1024 * 1024:  # > 1MB
                        rel = p.relative_to(self.repo_path)
                        large_files.append({"path": str(rel), "size_mb": round(size / (1024 * 1024), 2)})
                except Exception:
                    pass
        report.large_files = large_files

        # 7. Suspicious tokens / secrets check in working tree
        suspicious = []
        secret_patterns = [
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"(?i)api[_-]?key\s*=\s*['\"][0-9a-zA-Z\-_]{16,}['\"]"),
            re.compile(r"(?i)password\s*=\s*['\"][^'\"]{6,}['\"]"),
        ]
        for root, _, files in os.walk(self.repo_path):
            if ".git" in root:
                continue
            for f in files:
                p = Path(root) / f
                try:
                    if p.suffix in [".py", ".env", ".json", ".yaml", ".yml", ".txt", ".md"]:
                        content = p.read_text(encoding="utf-8", errors="ignore")
                        for pat in secret_patterns:
                            if pat.search(content):
                                suspicious.append(f"Potential secret in {p.relative_to(self.repo_path)}")
                                break
                except Exception:
                    pass
        report.suspicious_findings = suspicious

        # 8. Contributor Activity
        shortlog = self.git.run("shortlog", "-sn", "--no-merges", "HEAD").stdout.splitlines()
        contributors = {}
        for line in shortlog[:10]:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                try:
                    contributors[parts[1]] = int(parts[0])
                except ValueError:
                    pass
        report.contributor_activity = contributors

        # 9. Calculate Overall Health Score
        deductions = 0
        if report.is_detached:
            deductions += 15
        if report.has_merge_conflicts:
            deductions += 30
        if report.uncommitted_changes_count > 10:
            deductions += 10
        if len(report.suspicious_findings) > 0:
            deductions += 40
        if len(report.large_files) > 0:
            deductions += 10

        score = max(0, 100 - deductions)
        report.health_score = score
        if score >= 90:
            report.health_status = "EXCELLENT"
        elif score >= 70:
            report.health_status = "DEGRADED"
        elif score >= 50:
            report.health_status = "WARNING"
        else:
            report.health_status = "CRITICAL"

        return report
