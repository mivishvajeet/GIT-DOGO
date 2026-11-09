"""CLI entrypoint module with direct subcommand support."""

import sys
import os
import signal
import subprocess
from pathlib import Path
from .menu import DojoCli
from ..web.server import start_server
from ..challenges import get_challenge
from ..core.state import state_manager


def stop_server_on_port(port: int) -> bool:
    """Finds and terminates any server process listening on the given port."""
    try:
        res = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
        pids = [p.strip() for p in res.stdout.splitlines() if p.strip()]
        if not pids:
            return False
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        return True
    except Exception as e:
        print(f"Error stopping process on port {port}: {e}")
        return False


def main() -> None:
    args = sys.argv[1:]

    # 1. Stop command: ./dojo stop, ./dojo web stop, ./dojo web 8081 stop
    if any(arg in ["stop", "kill", "down"] for arg in args):
        ports_to_check = [8081, 8080, 8888]
        for arg in args:
            try:
                p = int(arg)
                ports_to_check.insert(0, p)
            except ValueError:
                pass
        
        stopped_any = False
        for port in ports_to_check:
            if stop_server_on_port(port):
                print(f"\033[92m[✓] Stopped server process listening on port {port}.\033[0m")
                stopped_any = True

        if not stopped_any:
            print("\033[93mNo active server found on ports 8081, 8080, or 8888.\033[0m")
        return

    # 2. Web Dashboard: ./dojo web [port]
    if args and args[0] in ["web", "--web", "dashboard"]:
        port = 8080
        if len(args) > 1:
            try:
                port = int(args[1])
            except ValueError:
                pass
        start_server(port=port)
        return

    # 3. Direct Launch: ./dojo start 06
    if args and args[0] in ["start", "launch", "level"] and len(args) > 1:
        lid = args[1]
        if not lid.startswith("level_"):
            try:
                num = int(lid)
                lid = f"level_{num:02d}"
            except ValueError:
                pass
        c = get_challenge(lid)
        if not c:
            print(f"Error: Scenario '{lid}' not found.")
            sys.exit(1)
        c.setup()
        state_manager.start_level(lid)
        print(f"\033[92m[✓] Level {c.number:02d} ({c.title}) launched in playground repository!\033[0m")
        print(f"Playground: .git_dojo/playground/nexus-platform")
        return

    # 4. Direct Verify: ./dojo verify
    if args and args[0] in ["verify", "test"]:
        active = state_manager.active_level
        if not active:
            print("No active scenario loaded. Run `./dojo start <number>` first.")
            sys.exit(1)
        c = get_challenge(active)
        if not c:
            print(f"Active scenario '{active}' not found.")
            sys.exit(1)
        success, msg = c.verify()
        state_manager.record_attempt(active, success, msg)
        if success:
            print(f"\033[92m[✓] VERIFICATION PASSED!\033[0m\n{msg}")
        else:
            print(f"\033[91m[✗] VERIFICATION FAILED\033[0m\n{msg}")
        return

    # 5. Interactive Menu
    try:
        app = DojoCli()
        app.run()
    except KeyboardInterrupt:
        print("\n\nOperation aborted by user. Exiting Git Dojo.")
        sys.exit(0)


if __name__ == "__main__":
    main()
