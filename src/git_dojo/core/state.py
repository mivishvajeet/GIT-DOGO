"""State and progress tracker for Git Dojo."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import time

from .config import config


@dataclass
class LevelAttempt:
    timestamp: str
    success: bool
    recovery_time_seconds: float
    message: str


@dataclass
class LevelProgress:
    level_id: str
    completed: bool = False
    completed_at: Optional[str] = None
    attempts: int = 0
    best_recovery_time_seconds: Optional[float] = None
    history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DojoState:
    active_level: Optional[str] = None
    active_level_start_time: Optional[float] = None
    levels: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @property
    def total_completed(self) -> int:
        return sum(1 for lvl in self.levels.values() if lvl.get("completed"))

    @classmethod
    def load(cls, file_path: Optional[Path] = None) -> "DojoState":
        path = file_path or config.state_file
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(
                        active_level=data.get("active_level"),
                        active_level_start_time=data.get("active_level_start_time"),
                        levels=data.get("levels", {}),
                        total_completed=data.get("total_completed", 0),
                    )
            except Exception:
                pass
        return cls()

    def save(self, file_path: Optional[Path] = None) -> None:
        path = file_path or config.state_file
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "active_level": self.active_level,
            "active_level_start_time": self.active_level_start_time,
            "levels": self.levels,
            "total_completed": sum(1 for lvl in self.levels.values() if lvl.get("completed")),
            "updated_at": datetime.now().isoformat(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def start_level(self, level_id: str) -> None:
        self.active_level = level_id
        self.active_level_start_time = time.time()
        if level_id not in self.levels:
            self.levels[level_id] = {
                "level_id": level_id,
                "completed": False,
                "completed_at": None,
                "attempts": 0,
                "best_recovery_time_seconds": None,
                "history": [],
            }
        self.levels[level_id]["attempts"] = self.levels[level_id].get("attempts", 0) + 1
        self.save()

    def record_attempt(self, level_id: str, success: bool, message: str) -> None:
        now = datetime.now().isoformat()
        elapsed = 0.0
        if self.active_level_start_time:
            elapsed = round(time.time() - self.active_level_start_time, 2)

        if level_id not in self.levels:
            self.levels[level_id] = {
                "level_id": level_id,
                "completed": False,
                "completed_at": None,
                "attempts": 1,
                "best_recovery_time_seconds": None,
                "history": [],
            }

        lvl = self.levels[level_id]
        if success:
            lvl["completed"] = True
            lvl["completed_at"] = now
            best = lvl.get("best_recovery_time_seconds")
            if best is None or elapsed < best:
                lvl["best_recovery_time_seconds"] = elapsed

        lvl["history"].append({
            "timestamp": now,
            "success": success,
            "recovery_time_seconds": elapsed,
            "message": message,
        })
        self.save()

    def is_completed(self, level_id: str) -> bool:
        return bool(self.levels.get(level_id, {}).get("completed", False))


state_manager = DojoState.load()
