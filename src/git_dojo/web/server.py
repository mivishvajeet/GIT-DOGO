"""HTTP Server & REST API for Nexus Ops Cockpit."""

import http.server
import json
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

from ..challenges import get_all_challenges, get_challenge
from ..core.config import config
from ..core.state import state_manager
from ..core.git_client import GitClient
from ..core.repo_manager import repo_manager
from ..forensics.inspector import ForensicInspector
from .pr_engine import pr_manager

STATIC_DIR = Path(__file__).resolve().parent / "static"


class CockpitApiHandler(http.server.SimpleHTTPRequestHandler):
    """Handles REST APIs and serves static frontend assets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            self._handle_api_get(path, urllib.parse.parse_qs(parsed.query))
        else:
            # Fallback to index.html for SPA routes or static files
            super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length > 0:
            try:
                raw_body = self.rfile.read(content_length).decode("utf-8")
                body = json.loads(raw_body)
            except Exception:
                pass

        if path.startswith("/api/"):
            self._handle_api_post(path, body)
        else:
            self._send_json({"error": "Method not allowed"}, status=405)

    def _send_json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _handle_api_get(self, path: str, query: Dict[str, list]) -> None:
        # 1. Scenarios List
        if path == "/api/scenarios":
            challenges = []
            for c in get_all_challenges():
                st = state_manager.levels.get(c.level_id, {})
                challenges.append({
                    "id": c.level_id,
                    "number": c.number,
                    "category": c.category.value,
                    "title": c.title,
                    "difficulty": c.difficulty,
                    "estimated_time": c.estimated_time,
                    "description": c.description,
                    "initial_state": c.initial_state_desc,
                    "expected_outcome": c.expected_outcome,
                    "hints": c.hints,
                    "completed": bool(st.get("completed")),
                    "attempts": st.get("attempts", 0),
                    "best_recovery_time": st.get("best_recovery_time_seconds"),
                    "interview_questions": [
                        {
                            "question": q.question,
                            "key_points": q.key_points,
                            "explanation": q.in_depth_explanation,
                        }
                        for q in c.interview_questions
                    ]
                })
            self._send_json({
                "active_level": state_manager.active_level,
                "total_completed": state_manager.total_completed,
                "total_levels": len(challenges),
                "scenarios": challenges,
            })
            return

        # 2. PR List
        if path == "/api/prs":
            state_filter = query.get("state", [None])[0]
            prs = pr_manager.list_prs(state_filter)
            self._send_json({"prs": prs})
            return

        # 3. Single PR Detail
        if path.startswith("/api/prs/"):
            try:
                pr_id = int(path.split("/")[-1])
                pr = pr_manager.get_pr(pr_id)
                if pr:
                    self._send_json({"pr": pr})
                else:
                    self._send_json({"error": "PR not found"}, status=404)
            except ValueError:
                self._send_json({"error": "Invalid PR ID"}, status=400)
            return

        # 4. Repo Status & Forensics
        if path == "/api/repo/status":
            inspector = ForensicInspector(config.playground_repo)
            rep = inspector.analyze()
            self._send_json({
                "repo_path": rep.repo_path,
                "is_valid_repo": rep.is_valid_repo,
                "current_branch": rep.current_branch,
                "is_detached": rep.is_detached,
                "head_commit": rep.head_commit,
                "uncommitted_count": rep.uncommitted_changes_count,
                "untracked_count": rep.untracked_files_count,
                "has_conflicts": rep.has_merge_conflicts,
                "conflicted_files": rep.conflicted_files,
                "local_branches": rep.local_branches,
                "tags": rep.tags,
                "health_score": rep.health_score,
                "health_status": rep.health_status,
                "suspicious_findings": rep.suspicious_findings,
                "dangling_commits": rep.dangling_commits,
            })
            return

        # 5. Commits Log
        if path == "/api/repo/commits":
            git = GitClient(config.playground_repo)
            if not git.is_git_repo():
                self._send_json({"commits": []})
                return
            log_res = git.run("log", "-n", "25", "--format=%H|%s|%an|%ae|%cr")
            commits = []
            for line in log_res.stdout.splitlines():
                parts = line.split("|")
                if len(parts) == 5:
                    commits.append({
                        "sha": parts[0],
                        "message": parts[1],
                        "author_name": parts[2],
                        "author_email": parts[3],
                        "time_ago": parts[4],
                    })
            self._send_json({"commits": commits})
            return

        self._send_json({"error": "Not Found"}, status=404)

    def _handle_api_post(self, path: str, body: Dict[str, Any]) -> None:
        # 1. Launch Scenario
        if path.startswith("/api/scenarios/") and path.endswith("/launch"):
            lid = path.split("/")[3]
            c = get_challenge(lid)
            if not c:
                self._send_json({"error": f"Scenario {lid} not found"}, status=404)
                return
            c.setup()
            state_manager.start_level(lid)
            self._send_json({"success": True, "message": f"Scenario {c.title} launched in playground!", "active_level": lid})
            return

        # 2. Verify Scenario
        if path.startswith("/api/scenarios/") and path.endswith("/verify"):
            lid = path.split("/")[3]
            c = get_challenge(lid)
            if not c:
                self._send_json({"error": f"Scenario {lid} not found"}, status=404)
                return
            success, msg = c.verify()
            state_manager.record_attempt(lid, success, msg)
            self._send_json({"success": success, "message": msg, "completed": state_manager.is_completed(lid)})
            return

        # 3. Reset Scenario
        if path.startswith("/api/scenarios/") and path.endswith("/reset"):
            lid = path.split("/")[3]
            c = get_challenge(lid)
            if not c:
                self._send_json({"error": f"Scenario {lid} not found"}, status=404)
                return
            c.reset()
            self._send_json({"success": True, "message": f"Scenario {c.title} reset to initial state."})
            return

        # 4. Add PR Review / Comment
        if path.startswith("/api/prs/") and path.endswith("/comments"):
            pr_id = int(path.split("/")[3])
            res = pr_manager.add_comment(
                pr_id=pr_id,
                author=body.get("author", "Staff Lead (You)"),
                role=body.get("role", "Staff Software Engineer"),
                comment_text=body.get("comment", ""),
                action=body.get("action", "comment"),
                file_path=body.get("file_path"),
                line_number=body.get("line_number"),
            )
            if res:
                self._send_json({"success": True, "pr": res})
            else:
                self._send_json({"error": "Failed to add comment"}, status=400)
            return

        # 5. Merge PR
        if path.startswith("/api/prs/") and path.endswith("/merge"):
            pr_id = int(path.split("/")[3])
            strat = body.get("strategy", "merge")
            res = pr_manager.merge_pr(pr_id, strategy=strat)
            self._send_json(res)
            return

        # 6. Repo Remote Sync (Push / Pull)
        if path == "/api/repo/sync":
            action = body.get("action", "pull")  # "pull" or "push"
            git = GitClient(config.playground_repo)
            cur_branch = git.current_branch() or "main"
            if action == "pull":
                res = git.run("pull", "origin", cur_branch)
                self._send_json({"success": res.success, "stdout": res.stdout, "stderr": res.stderr})
            elif action == "push":
                res = git.run("push", "origin", cur_branch)
                self._send_json({"success": res.success, "stdout": res.stdout, "stderr": res.stderr})
            else:
                self._send_json({"error": "Unknown sync action"}, status=400)
            return

        # 7. Incident Escalation Dispatch
        if path == "/api/escalate":
            sev = body.get("severity", "SEV-1")
            title = body.get("title", "Critical Production Outage")
            service = body.get("service", "Nexus Inventory Platform")
            impact = body.get("impact", "Checkout flow failing across 100% of user traffic")
            commander = body.get("commander", "Staff Engineer (You)")
            notes = body.get("notes", "Investigating merge conflicts & corrupted release tag.")

            broadcast_msg = (
                f"🚨 *[{sev} ESCALATION ALERT]* 🚨\n"
                f"*Incident*: {title}\n"
                f"*Impacted Service*: {service}\n"
                f"*Customer Impact*: {impact}\n"
                f"*Incident Commander*: {commander}\n"
                f"*Current Status*: Active War Room Open\n"
                f"*Operational Notes*: {notes}\n"
                f"--------------------------------------------------\n"
                f"Paging: @nexus-engineering/sre-oncall @nexus-engineering/release-managers\n"
                f"Bridge: https://meet.nexus.internal/warroom-incident"
            )

            self._send_json({
                "success": True,
                "severity": sev,
                "broadcast_message": broadcast_msg,
                "timestamp": "Just now",
            })
            return

        self._send_json({"error": "Not Found"}, status=404)


def start_server(port: int = 8080) -> None:
    """Starts the Nexus Ops Cockpit HTTP server."""
    server_address = ("127.0.0.1", port)
    httpd = http.server.ThreadingHTTPServer(server_address, CockpitApiHandler)
    print(f"\n\033[92m=======================================================================\033[0m")
    print(f"\033[1m\033[96m       NEXUS COCKPIT — ENTERPRISE REPOSITORY DASHBOARD ACTIVE\033[0m")
    print(f"\033[92m=======================================================================\033[0m")
    print(f"\n  URL: \033[1m\033[93mhttp://localhost:{port}\033[0m")
    print(f"  Playground: {config.playground_repo}")
    print(f"\n  Open http://localhost:{port} in your browser to start playing.")
    print(f"  Press Ctrl+C to stop the dashboard server.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Nexus Cockpit...")
        httpd.shutdown()
